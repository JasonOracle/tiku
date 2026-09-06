"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 评分引擎重构: 填空题多空强匹配/多选题漏选半对/简答题待批阅(pending_grading)/finalize_record 终算/时间窗口惰性收卷/题目锁定守卫]
"""
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.models.record import ExamRecord
from app.core.config import settings

OBJECTIVE_TYPES = ("single", "multiple", "judge")
ALL_TYPES = ("single", "multiple", "judge", "fill", "short")


def _norm(val) -> str:
    """判卷前归一化: 切除首尾空格并统一大写 (填空/客观题统一口径)"""
    return str(val if val is not None else "").strip().upper()


# =====================================================================
# 评分核心
# =====================================================================

def score_objective_item(q_type: str, u_ans: list, c_ans: list, eq_score: int) -> Tuple[bool, int, bool]:
    """客观题判卷 (单选/判断/多选/填空)
    :return: (是否全对, 得分, 是否部分得分[多选半对])
    """
    if q_type == "multiple":
        u_set = {_norm(x) for x in (u_ans or []) if _norm(x)}
        c_set = {_norm(x) for x in (c_ans or []) if _norm(x)}
        if c_set and u_set == c_set:
            return True, eq_score, False
        # 多选半对机制: 漏选 (真子集) 得一半分, 错选不得分
        if u_set and u_set < c_set:
            return False, int(eq_score / 2), True
        return False, 0, False

    if q_type == "fill":
        # c_ans 为二维数组 [["北京","北京市"],["是"]]; 兼容一维旧数据视为单空
        if not isinstance(c_ans, list) or not c_ans:
            return False, 0, False
        blanks = c_ans if isinstance(c_ans[0], list) else [[x] for x in c_ans]
        # 学生逐空作答 (顺序对应题干 ___); 空数不一致直接判错
        if len(u_ans or []) != len(blanks):
            return False, 0, False
        for i, accepted in enumerate(blanks):
            ua = _norm((u_ans or [])[i])
            if not ua or ua not in {_norm(a) for a in accepted}:
                return False, 0, False
        return True, eq_score, False

    # single / judge: 100% 强匹配
    u_set = {_norm(x) for x in (u_ans or []) if _norm(x)}
    c_set = {_norm(x) for x in (c_ans or []) if _norm(x)}
    is_correct = bool(c_set) and u_set == c_set
    return is_correct, (eq_score if is_correct else 0), False


def evaluate_submission(
    db: Session,
    exam: Exam,
    user_answers: Dict[str, List[str]],
    short_scores: Optional[Dict[str, int]] = None,
) -> dict:
    """全量评估一次作答
    :return: {items, total_score, passed, correct_count, wrong_count, partial_count, has_short, pending}
             pending=True 表示仍有简答题未定分 (不能发布成绩)
    """
    exam_questions = db.query(ExamQuestion).filter(
        ExamQuestion.exam_id == exam.id
    ).order_by(ExamQuestion.sort_order).all()

    items: List[dict] = []
    total_score = 0
    correct_count = wrong_count = partial_count = 0
    has_short = False
    pending = False
    given_short = {str(k): v for k, v in (short_scores or {}).items()}

    for eq in exam_questions:
        question = db.query(Question).filter(Question.id == eq.question_id).first()
        if not question:
            continue

        q_id_str = str(question.id)
        u_ans = user_answers.get(q_id_str) or []

        if question.type == "short":
            has_short = True
            if q_id_str in given_short and given_short[q_id_str] is not None:
                gained = max(0, min(int(given_short[q_id_str]), eq.score))
            else:
                gained = 0
                pending = True  # 简答题尚未定分, 整卷不可出分
            total_score += gained
            items.append({
                "question": question,
                "user_answer": u_ans,
                "correct_answer": question.answer or [],
                "is_correct": None,
                "is_pending": q_id_str not in given_short or given_short[q_id_str] is None,
                "is_partial": False,
                "gained": gained,
                "eq_score": eq.score,
            })
            continue

        is_correct, gained, is_partial = score_objective_item(
            question.type, u_ans, question.answer or [], eq.score
        )
        total_score += gained
        if is_correct:
            correct_count += 1
        elif is_partial:
            partial_count += 1
        else:
            wrong_count += 1
        items.append({
            "question": question,
            "user_answer": u_ans,
            "correct_answer": question.answer or [],
            "is_correct": is_correct,
            "is_pending": False,
            "is_partial": is_partial,
            "gained": gained,
            "eq_score": eq.score,
        })

    return {
        "items": items,
        "total_score": total_score,
        "passed": (total_score >= exam.pass_score) if not pending else False,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "partial_count": partial_count,
        "has_short": has_short,
        "pending": pending,
    }


# =====================================================================
# 提交与终算 (First-Submit-Wins 悲观锁)
# =====================================================================

def submit_exam_record_with_lock(
    db: Session,
    record_id: int,
    user_id: int,
    user_answers: Dict[str, List[str]],
    time_spent: int
):
    """悲观锁抢先提交。含简答题的试卷进入 pending_grading (等待 AI/人工批阅)。
    :return: (record, eval_result)
    """
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.user_id == user_id
    ).with_for_update().first()

    if not record:
        raise HTTPException(status_code=404, detail="答题记录不存在")

    if record.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该试卷答题记录已被提交或结算，请勿重复提交！"
        )

    # 空卷拦截：一题未答不允许交卷（防误入3秒产生0分幽灵记录）
    answered = sum(1 for v in (user_answers or {}).values() if v)
    if answered == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您尚未作答任何题目，无需交卷"
        )

    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="关联试卷不存在")

    result = evaluate_submission(db, exam, user_answers)

    record.user_answers = user_answers
    record.time_spent = time_spent
    record.submit_time = datetime.now()

    if result["has_short"]:
        # 主观题存在: 进入待批阅, 成绩由 finalize_record 统一发布
        record.status = "pending_grading"
        record.score = 0
        record.passed = False
    else:
        record.status = "submitted"
        record.score = result["total_score"]
        record.passed = result["passed"]

    db.commit()
    db.refresh(record)
    return record, result


def finalize_record(db: Session, record: ExamRecord, short_scores: Dict[str, int]) -> ExamRecord:
    """批阅终算: 合并客观题得分与简答题定分, 发布最终成绩 (submitted 为唯一出分终态)"""
    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="关联试卷不存在")

    result = evaluate_submission(db, exam, record.user_answers or {}, short_scores=short_scores)
    record.status = "submitted"
    record.score = result["total_score"]
    record.passed = result["passed"]
    record.short_scores = {str(k): int(v) for k, v in (short_scores or {}).items() if v is not None}
    record.submit_time = datetime.now()
    db.commit()
    db.refresh(record)
    return record


# =====================================================================
# 幽灵记录结算: 传统限时超时 + 时间窗口惰性收卷 (0 运维基建)
# =====================================================================

def cleanup_expired_records(db: Session, user_id: int):
    """检查并被动结算当前用户所有已超期的 in_progress 答题记录 (预留 2 分钟缓冲网络容错)"""
    now = datetime.now()
    in_progress_records = db.query(ExamRecord).filter(
        ExamRecord.user_id == user_id,
        ExamRecord.status == "in_progress"
    ).all()

    for record in in_progress_records:
        exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
        if not exam or not exam.is_timed:
            continue
        time_limit_minutes = exam.time_limit + 2  # 2分钟缓冲容错
        if now > (record.start_time + timedelta(minutes=time_limit_minutes)):
            result = evaluate_submission(db, exam, record.user_answers or {})
            if result["has_short"]:
                record.status = "pending_grading"
            else:
                record.status = "timeout"
                record.score = result["total_score"]
                record.passed = result["passed"]
            record.submit_time = now

    db.commit()


def close_expired_window_records(db: Session, user_id: Optional[int] = None, exam_id: Optional[int] = None) -> int:
    """时间硬边界惰性收卷: 当前时间已过试卷 end_time 的 in_progress 记录当场强制扭转为已交卷。
    - 无简答题: 直接评分置 submitted
    - 有简答题: 置 pending_grading 交由人工/AI 批阅
    由学生打开列表 / 老师打开阅卷大厅等查询路径顺手触发, 无需后台定时任务。
    :return: 本次收卷条数
    """
    now = datetime.now()
    query = db.query(ExamRecord).join(
        Exam, ExamRecord.exam_id == Exam.id
    ).filter(
        ExamRecord.status == "in_progress",
        Exam.end_time.isnot(None),
        Exam.end_time < now
    )
    if user_id is not None:
        query = query.filter(ExamRecord.user_id == user_id)
    if exam_id is not None:
        query = query.filter(ExamRecord.exam_id == exam_id)

    records = query.all()
    for record in records:
        exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
        if not exam:
            continue
        result = evaluate_submission(db, exam, record.user_answers or {})
        if result["has_short"]:
            record.status = "pending_grading"
        else:
            record.status = "submitted"
            record.score = result["total_score"]
            record.passed = result["passed"]
        record.submit_time = now
    if records:
        db.commit()
    return len(records)


# =====================================================================
# 考试时间窗口
# =====================================================================

def exam_window_status(exam: Exam, now: Optional[datetime] = None) -> Optional[str]:
    """试卷子状态: 未开始(upcoming) / 进行中(ongoing) / 已结束(ended); 无时间窗口返回 None"""
    if not exam.start_time and not exam.end_time:
        return None
    now = now or datetime.now()
    if exam.start_time and now < exam.start_time:
        return "upcoming"
    if exam.end_time and now > exam.end_time:
        return "ended"
    return "ongoing"


def ensure_exam_started(exam: Exam, now: Optional[datetime] = None):
    """开考前/考后拦截学生进入作答"""
    now = now or datetime.now()
    if exam.start_time and now < exam.start_time:
        raise HTTPException(status_code=400, detail="考试尚未开始，请耐心等待")
    if exam.end_time and now > exam.end_time:
        raise HTTPException(status_code=400, detail="考试已结束，无法再作答")


def validate_exam_window(time_limit: int, is_timed: bool, start_time: Optional[datetime], end_time: Optional[datetime]):
    """组卷时间锁强制校验: 考试时长必须 ≤ (end_time - start_time) 开放区间"""
    if start_time and end_time:
        if end_time <= start_time:
            raise HTTPException(status_code=400, detail="考试结束时间必须晚于开始时间")
        if is_timed and time_limit:
            window_minutes = int((end_time - start_time).total_seconds() // 60)
            if time_limit > window_minutes:
                raise HTTPException(
                    status_code=400,
                    detail=f"考试限时不能大于考试开放总区间时间（当前区间 {window_minutes} 分钟）"
                )


# =====================================================================
# 治理工具
# =====================================================================

def first_category_id(db: Session, target_type: str) -> Optional[int]:
    """取某用途分类第一项（sort_order,id 双排序，与B端列表一致）"""
    from app.models.category import ExamCategory
    cat = db.query(ExamCategory).filter(
        ExamCategory.target_type == target_type
    ).order_by(ExamCategory.sort_order.asc(), ExamCategory.id.asc()).first()
    return cat.id if cat else None


def recalc_exam_totals(db: Session, exam: Exam) -> Exam:
    """按现行关联重算试卷总分与及格线（删题联动/组卷变更共用）"""
    links = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).all()
    total = 0
    for eq in links:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            total += eq.score or 0
    pct = exam.pass_percent if exam.pass_percent is not None else 60
    exam.total_score = total
    exam.pass_score = math.ceil(total * pct / 100.0)
    return exam


def ensure_publishable(db: Session, exam: Exam):
    """上架校验：必须绑定有效分类，并写入分类名称快照"""
    from app.models.category import ExamCategory
    if not exam.category_id:
        raise HTTPException(status_code=400, detail="上架前请先选择试卷分类")
    cat = db.query(ExamCategory).filter(ExamCategory.id == exam.category_id).first()
    if not cat:
        raise HTTPException(status_code=400, detail="绑定的试卷分类不存在，请重新选择")
    exam.category_name = cat.name


def get_locked_exam_titles(db: Session, question_id: int) -> List[str]:
    """题目锁定防篡改: 返回引用该题目且处于 published/archived 状态的试卷名列表 (非空即全局只读)"""
    from app.models.exam import Exam, ExamQuestion
    links = db.query(ExamQuestion).filter(ExamQuestion.question_id == question_id).all()
    exam_ids = sorted({lk.exam_id for lk in links})
    titles = []
    for eid in exam_ids:
        ex = db.query(Exam).filter(Exam.id == eid, Exam.status.in_(["published", "archived"])).first()
        if ex:
            titles.append(ex.title)
    return titles


def validate_fill_question(title: str, answer) -> None:
    """填空题防崩溃强制校验: 题干 ___ 占位符数量 == answer 二维数组长度"""
    blank_count = title.count("___")
    if not isinstance(answer, list) or not answer:
        raise HTTPException(status_code=400, detail="填空题必须配置答案（二维数组，如 [[\"北京\",\"北京市\"]]）")
    normalized = answer if isinstance(answer[0], list) else [answer]
    if blank_count != len(normalized):
        raise HTTPException(
            status_code=400,
            detail=f"填空题校验失败：题干中 ___ 占位符数量({blank_count})必须与答案空数({len(normalized)})一致"
        )
    for blank in normalized:
        if not isinstance(blank, list) or not [a for a in blank if str(a).strip()]:
            raise HTTPException(status_code=400, detail="填空题每个空至少需要一个可接受答案")

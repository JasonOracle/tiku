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

def cleanup_expired_records(db: Session, user_id: int):
    """
    检查并被动结算当前用户所有已超期的 in_progress 答题记录 (预留 2 分钟缓冲网络容错)
    """
    now = datetime.now()
    in_progress_records = db.query(ExamRecord).filter(
        ExamRecord.user_id == user_id,
        ExamRecord.status == "in_progress"
    ).all()

    for record in in_progress_records:
        exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
        if not exam or not exam.is_timed:
            continue
        
        # 判断时间差 (单位：分钟)
        time_limit_minutes = exam.time_limit + 2  # 2分钟缓冲容错
        if now > (record.start_time + timedelta(minutes=time_limit_minutes)):
            record.status = "timeout"
            record.submit_time = now
    
    db.commit()

def calculate_exam_score(
    db: Session, 
    exam_id: int, 
    user_answers: Dict[str, List[str]]
) -> Tuple[int, bool, int, int, List[Dict]]:
    """
    核心评分引擎算法
    :return: (最终得分, 是否及格, 答对题数, 答错题数, 题目分析明细)
    """
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    # 查询试卷绑定的所有题目明细
    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.sort_order).all()
    
    total_user_score = 0
    correct_count = 0
    wrong_count = 0
    analysis_list = []

    for eq in exam_questions:
        question = db.query(Question).filter(Question.id == eq.question_id).first()
        if not question:
            continue

        q_id_str = str(question.id)
        u_ans = user_answers.get(q_id_str, [])
        c_ans = question.answer if question.answer else []

        # 排序后比较数组是否完全相等
        u_ans_sorted = sorted([str(x).strip() for x in u_ans])
        c_ans_sorted = sorted([str(x).strip() for x in c_ans])

        is_correct = (u_ans_sorted == c_ans_sorted)
        
        if is_correct:
            total_user_score += eq.score
            correct_count += 1
        else:
            wrong_count += 1

        analysis_list.append({
            "question_id": question.id,
            "question": question,
            "user_answer": u_ans,
            "correct_answer": c_ans,
            "is_correct": is_correct,
            "score": eq.score if is_correct else 0
        })

    is_passed = (total_user_score >= exam.pass_score)
    return total_user_score, is_passed, correct_count, wrong_count, analysis_list

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


def submit_exam_record_with_lock(
    db: Session, 
    record_id: int, 
    user_id: int, 
    user_answers: Dict[str, List[str]], 
    time_spent: int
) -> ExamRecord:
    """
    悲观锁抢先提交与结算逻辑 (First-Submit-Wins)
    """
    # 数据库行级悲观锁
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

    # 计算得分
    score, passed, _, _, _ = calculate_exam_score(db, record.exam_id, user_answers)

    record.status = "submitted"
    record.score = score
    record.passed = passed
    record.time_spent = time_spent
    record.submit_time = datetime.now()
    record.user_answers = user_answers

    db.commit()
    db.refresh(record)
    return record

"""
[变更日志]
修改时间：2026-09-06 18:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 C端答题流重构: 考试时间硬边界(未开始/已结束拦截+倒计时压缩)、续答、含简答题交卷转 pending_grading 并触发 AI 批阅、
         新增"我的测试"三态聚合接口、报告降级查看与防泄题解析锁]
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.models.record import ExamRecord, UserFavorite
from app.schemas.record import (
    ExamStartRequest, ExamStartResponse,
    ExamSubmitRequest, ExamReportResponse,
    QuestionAnalysisItem
)
from app.schemas.question import QuestionResponse
from app.schemas.common import ResponseModel, PageResponse
from app.services.exam_service import (
    cleanup_expired_records, close_expired_window_records,
    submit_exam_record_with_lock, evaluate_submission,
    exam_window_status, ensure_exam_started,
)
from app.services.ai_grading import run_ai_grading
from app.services import ai_service
from app.core.security import decode_token

router = APIRouter()


def _load_paper_questions(db: Session, exam: Exam, protect_answer: bool = True) -> List[QuestionResponse]:
    """装载试卷题目; protect_answer=True 时隐藏标准答案 (作答中防泄露)"""
    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.sort_order).all()
    questions = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            q_res = QuestionResponse.model_validate(q)
            if protect_answer:
                q_res.answer = []  # 保护标准答案
            questions.append(q_res)
    return questions


def _start_response(db: Session, record: ExamRecord, exam: Exam) -> ExamStartResponse:
    return ExamStartResponse(
        record_id=record.id,
        exam_id=exam.id,
        exam_title=exam.title,
        is_timed=exam.is_timed,
        time_limit=exam.time_limit,
        total_score=exam.total_score,
        pass_score=exam.pass_score,
        start_time=record.start_time,
        end_time=exam.end_time,
        server_now=datetime.now(),
        questions=_load_paper_questions(db, exam, protect_answer=True),
    )


def _short_comment_map(record: ExamRecord) -> dict:
    """提取 AI/教师给简答题写的评语 {question_id: comment}"""
    result = record.ai_grading_result or {}
    return {str(s.get("question_id")): str(s.get("comment", ""))
            for s in (result.get("suggestions") or [])}


def build_report_response(db: Session, record: ExamRecord, current_user: User) -> ExamReportResponse:
    """构建答题报告 (含待批阅降级 / 防泄题解析锁 / 多选半对与简答评语)"""
    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    now = datetime.now()

    is_pending = record.status == "pending_grading"
    final_scores = record.short_scores if record.status == "submitted" else None
    result = evaluate_submission(db, exam, record.user_answers or {}, short_scores=final_scores)

    # 防泄题解析锁: 1) 待批阅期间仅可查看自己原答案; 2) 已出分但考试 end_time 未到时锁标准答案
    analysis_locked = is_pending or bool(exam and exam.end_time and now <= exam.end_time)

    user_fav_qids = set(
        f.question_id for f in db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).all()
    )
    comment_map = _short_comment_map(record)

    questions_analysis = []
    for item in result["items"]:
        q = item["question"]
        q_res = QuestionResponse.model_validate(q)
        if analysis_locked:
            q_res.answer = []          # 隐藏标准答案
            q_res.explanation = ""     # 隐藏解析
        questions_analysis.append(QuestionAnalysisItem(
            question=q_res,
            user_answer=item["user_answer"],
            correct_answer=[] if analysis_locked else item["correct_answer"],
            is_correct=None if (is_pending or item["is_correct"] is None) else item["is_correct"],
            is_pending=item["is_pending"],
            is_partial=item["is_partial"],
            is_favorited=q.id in user_fav_qids,
            gained=0 if is_pending else item["gained"],
            eq_score=item["eq_score"],
            comment=comment_map.get(str(q.id), "") if record.status == "submitted" else "",
        ))

    return ExamReportResponse(
        record_id=record.id,
        exam_id=exam.id if exam else 0,
        exam_title=exam.title if exam else "",
        user_id=current_user.id,
        status=record.status,
        pending=is_pending,
        analysis_locked=analysis_locked,
        score=0 if is_pending else (record.score or 0),
        total_score=exam.total_score if exam else 0,
        pass_score=exam.pass_score if exam else 0,
        passed=bool(record.passed) if record.status == "submitted" else False,
        time_spent=record.time_spent or 0,
        total_questions=len(questions_analysis),
        correct_count=result["correct_count"],
        wrong_count=result["wrong_count"],
        partial_count=result["partial_count"],
        pending_count=sum(1 for it in result["items"] if it["is_pending"]),
        start_time=record.start_time,
        submit_time=record.submit_time,
        questions_analysis=questions_analysis,
    )


@router.post("/start", response_model=ResponseModel[ExamStartResponse])
def start_exam(
    data: ExamStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """开始/续答: 时间硬边界校验 (未开始/已结束拦截); 已有 in_progress 记录则续答不新建"""
    # 被动结算: 传统限时超时 + 时间窗口惰性收卷
    cleanup_expired_records(db, current_user.id)
    close_expired_window_records(db, user_id=current_user.id)

    exam = db.query(Exam).filter(Exam.id == data.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if exam.status != "published":
        raise HTTPException(status_code=404, detail="试卷不存在或已被下架")

    ensure_exam_started(exam)

    # 续答: 同卷已有进行中的记录直接返回 (避免重复开卷)
    record = db.query(ExamRecord).filter(
        ExamRecord.user_id == current_user.id,
        ExamRecord.exam_id == exam.id,
        ExamRecord.status == "in_progress"
    ).first()
    if not record:
        record = ExamRecord(
            user_id=current_user.id,
            exam_id=exam.id,
            status="in_progress",
            start_time=datetime.now()
        )
        db.add(record)
        db.commit()
        db.refresh(record)

    return ResponseModel(code=200, data=_start_response(db, record, exam))


@router.post("/submit", response_model=ResponseModel[ExamReportResponse])
def submit_exam(
    data: ExamSubmitRequest,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交答卷: 悲观锁抢提交; 含简答题转 pending_grading, 开启 AI 全托管/预批改时后台异步批阅"""
    # 允许 5 分钟宽限期 Token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_token(token, allow_grace_period=True)
        if not payload:
            raise HTTPException(status_code=401, detail="登录凭证已完全失效")

    record, result = submit_exam_record_with_lock(
        db=db,
        record_id=data.record_id,
        user_id=current_user.id,
        user_answers=data.user_answers,
        time_spent=data.time_spent
    )

    # 含简答题: 交卷瞬间立刻返回, AI 批阅(全托管或预批改)在后台协程执行 (主线程不阻塞)
    if record.status == "pending_grading" and ai_service.ai_available():
        background_tasks.add_task(run_ai_grading, record.id)

    return ResponseModel(code=200, data=build_report_response(db, record, current_user))


@router.get("/my-tests", response_model=ResponseModel[dict])
def my_tests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """C端"我的测试"三态聚合: 进行中 / 未开始 / 已考试 (按试卷聚合, 卡片状态只反映最新一次作答)"""
    cleanup_expired_records(db, current_user.id)
    closed = close_expired_window_records(db, user_id=current_user.id)

    now = datetime.now()
    exams = db.query(Exam).filter(Exam.status == "published").order_by(Exam.id.desc()).all()
    my_records = db.query(ExamRecord).filter(ExamRecord.user_id == current_user.id).order_by(ExamRecord.id.desc()).all()

    records_by_exam: dict = {}
    for r in my_records:
        records_by_exam.setdefault(r.exam_id, []).append(r)

    def _card(exam: Exam) -> dict:
        recs = records_by_exam.get(exam.id, [])
        latest = recs[0] if recs else None
        in_progress = next((r for r in recs if r.status == "in_progress"), None)
        window = exam_window_status(exam, now)
        # 解析解锁: 无 end_time 的卷考完即解锁; 有 end_time 的必须等考试彻底结束 (防泄题)
        analysis_unlocked = (not exam.end_time) or now > exam.end_time
        return {
            "exam_id": exam.id,
            "title": exam.title,
            "cover_url": exam.cover_url or "",
            "category_name": exam.category_name or "",
            "total_score": exam.total_score,
            "pass_score": exam.pass_score,
            "is_timed": exam.is_timed,
            "time_limit": exam.time_limit,
            "start_time": exam.start_time.isoformat(sep=" ", timespec="seconds") if exam.start_time else None,
            "end_time": exam.end_time.isoformat(sep=" ", timespec="seconds") if exam.end_time else None,
            "window_status": window,
            "is_random": exam.is_random,
            "question_count": db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).count(),
            "attempts": len([r for r in recs if r.status != "in_progress"]),
            "my_record_id": in_progress.id if in_progress else None,
            "latest_record_id": latest.id if latest else None,
            "latest_status": latest.status if latest else None,
            "latest_score": latest.score if latest else None,
            "latest_passed": latest.passed if latest else None,
            "latest_submit_time": latest.submit_time.isoformat(sep=" ", timespec="seconds") if latest and latest.submit_time else None,
            "analysis_unlocked": analysis_unlocked,
        }

    ongoing: List[dict] = []
    upcoming: List[dict] = []
    completed: List[dict] = []

    for exam in exams:
        window = exam_window_status(exam, now)
        recs = records_by_exam.get(exam.id, [])
        has_final = any(r.status in ("submitted", "timeout", "pending_grading") for r in recs)
        card = _card(exam)

        if window == "upcoming":
            upcoming.append(card)
        elif window == "ended":
            if has_final:
                completed.append(card)
            # 已结束且从未作答的试卷不展示 (错过即错过)
        else:  # ongoing 或无时间窗
            if any(r.status == "in_progress" for r in recs):
                ongoing.append(card)
            elif has_final:
                completed.append(card)  # 已考过 (窗口仍开时可重考)
            else:
                ongoing.append(card)

    return ResponseModel(code=200, data={
        "ongoing": ongoing,
        "upcoming": upcoming,
        "completed": completed,
        "lazy_closed": closed,
        "server_now": now.isoformat(sep=" ", timespec="seconds"),
    })


@router.get("/history", response_model=ResponseModel[PageResponse[ExamReportResponse]])
def get_exam_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取个人答题历史明细 (标准分页)"""
    query = db.query(ExamRecord).filter(ExamRecord.user_id == current_user.id, ExamRecord.status == "submitted")
    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    records = query.order_by(ExamRecord.id.desc()).offset((page - 1) * size).limit(size).all()

    items = []
    for r in records:
        items.append(build_report_response(db, r, current_user))

    return ResponseModel(
        code=200,
        data=PageResponse(
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            items=items
        )
    )


@router.get("/{record_id}", response_model=ResponseModel[ExamStartResponse])
def get_exam_record_detail(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取正在进行的答题记录详情及题目列表"""
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="答题记录不存在")

    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="关联试卷不存在")

    return ResponseModel(code=200, data=_start_response(db, record, exam))


@router.get("/{record_id}/report", response_model=ResponseModel[ExamReportResponse])
def get_exam_report(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取答题成绩分析报告 (含得分统计、错题解析、收藏状态; 待批阅时降级展示)"""
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="答题记录不存在")

    return ResponseModel(code=200, data=build_report_response(db, record, current_user))

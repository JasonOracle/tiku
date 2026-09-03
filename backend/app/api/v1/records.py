from fastapi import APIRouter, Depends, HTTPException, Query, Header
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
from app.services.exam_service import cleanup_expired_records, submit_exam_record_with_lock, calculate_exam_score
from app.core.security import decode_token

router = APIRouter()

@router.post("/start", response_model=ResponseModel[ExamStartResponse])
def start_exam(
    data: ExamStartRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """开始答题：生成唯一 record_id，并自动被动结算历史超期记录"""
    # 自动清算超期记录
    cleanup_expired_records(db, current_user.id)

    exam = db.query(Exam).filter(Exam.id == data.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if exam.status != "published":
        raise HTTPException(status_code=404, detail="试卷不存在或已被下架")

    record = ExamRecord(
        user_id=current_user.id,
        exam_id=exam.id,
        status="in_progress",
        start_time=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 获取题目
    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.sort_order).all()
    questions = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            # 隐藏答案后返回给前端做题（练习或考试）
            q_res = QuestionResponse.model_validate(q)
            q_res.answer = []  # 保护标准答案
            questions.append(q_res)

    return ResponseModel(
        code=200,
        data=ExamStartResponse(
            record_id=record.id,
            exam_id=exam.id,
            exam_title=exam.title,
            is_timed=exam.is_timed,
            time_limit=exam.time_limit,
            total_score=exam.total_score,
            pass_score=exam.pass_score,
            start_time=record.start_time,
            questions=questions
        )
    )

@router.post("/submit", response_model=ResponseModel[ExamReportResponse])
def submit_exam(
    data: ExamSubmitRequest, 
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """提交答卷：支持 5 分钟宽限期 Token 验证与悲观锁抢提交防护"""
    # 允许 5 分钟宽限期 Token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_token(token, allow_grace_period=True)
        if not payload:
            raise HTTPException(status_code=401, detail="登录凭证已完全失效")

    record = submit_exam_record_with_lock(
        db=db,
        record_id=data.record_id,
        user_id=current_user.id,
        user_answers=data.user_answers,
        time_spent=data.time_spent
    )

    # 获得报告
    return get_exam_report(record_id=record.id, db=db, current_user=current_user)

@router.get("/{record_id}/report", response_model=ResponseModel[ExamReportResponse])
def get_exam_report(
    record_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """获取答题成绩分析报告 (含得分统计、错题解析、收藏状态)"""
    record = db.query(ExamRecord).filter(
        ExamRecord.id == record_id,
        ExamRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="答题记录不存在")

    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    
    # 评分计算
    user_answers = record.user_answers or {}
    score, passed, correct_count, wrong_count, analysis_items = calculate_exam_score(db, record.exam_id, user_answers)

    # 用户收藏夹集合
    user_fav_qids = set(
        f.question_id for f in db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).all()
    )

    questions_analysis = []
    for item in analysis_items:
        q = item["question"]
        q_res = QuestionResponse.model_validate(q)
        is_fav = q.id in user_fav_qids
        
        questions_analysis.append(QuestionAnalysisItem(
            question=q_res,
            user_answer=item["user_answer"],
            correct_answer=item["correct_answer"],
            is_correct=item["is_correct"],
            is_favorited=is_fav
        ))

    return ResponseModel(
        code=200,
        data=ExamReportResponse(
            record_id=record.id,
            exam_id=exam.id if exam else 0,
            exam_title=exam.title if exam else "",
            user_id=current_user.id,
            status=record.status,
            score=record.score,
            passed=record.passed,
            time_spent=record.time_spent,
            total_questions=len(questions_analysis),
            correct_count=correct_count,
            wrong_count=wrong_count,
            start_time=record.start_time,
            submit_time=record.submit_time,
            questions_analysis=questions_analysis
        )
    )

@router.get("/users/me/stats", response_model=ResponseModel[dict])
def get_user_me_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 C 端当前登录用户的仪表盘作答统计 (作答场次、通过率、收藏总数)"""
    records = db.query(ExamRecord).filter(
        ExamRecord.user_id == current_user.id,
        ExamRecord.status == "submitted"
    ).all()

    total_exams_taken = len(records)
    passed_count = sum(1 for r in records if r.passed)
    pass_rate = round((passed_count / total_exams_taken) * 100, 1) if total_exams_taken > 0 else 0.0

    favorite_count = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).count()

    return ResponseModel(code=200, data={
        "total_exams_taken": total_exams_taken,
        "passed_count": passed_count,
        "pass_rate": pass_rate,
        "favorite_count": favorite_count,
        "history_count": total_exams_taken
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
        rep_res = get_exam_report(record_id=r.id, db=db, current_user=current_user)
        items.append(rep_res.data)

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



"""
[变更日志]
修改时间：2026-09-04 00:08:00
AI模型：Gemini 底层
修改内容：[1. C端试卷列表与详情强制拦截非 published 状态试卷，防未上架预览泄露]
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.schemas.exam import ExamResponse, ExamDetailResponse
from app.schemas.question import QuestionResponse
from app.schemas.common import ResponseModel, PageResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.exam_service import cleanup_expired_records

router = APIRouter()

@router.get("", response_model=ResponseModel[PageResponse[ExamResponse]])
def list_exams(
    category_id: Optional[int] = Query(None, description="分类ID"),
    is_recommended: Optional[bool] = Query(None, description="是否首页推荐"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db)
):
    """C端查询已上架试卷列表 (标准分页)"""
    query = db.query(Exam).filter(Exam.status == "published")
    if category_id is not None:
        query = query.filter(Exam.category_id == category_id)
    if is_recommended is not None:
        query = query.filter(Exam.is_recommended == is_recommended)

    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    exams = query.order_by(Exam.id.desc()).offset((page - 1) * size).limit(size).all()
    
    result_items = []
    for exam in exams:
        count = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).count()
        item = ExamResponse.model_validate(exam)
        item.question_count = count
        result_items.append(item)

    return ResponseModel(
        code=200,
        data=PageResponse(
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            items=result_items
        )
    )

@router.get("/{exam_id}", response_model=ResponseModel[ExamDetailResponse])
def get_exam_detail(
    exam_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """C端获取试卷详情 (限制仅 published 状态)"""
    if current_user:
        cleanup_expired_records(db, current_user.id)

    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.status == "published").first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在或已被下架")


    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.sort_order).all()
    
    questions = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            questions.append(QuestionResponse.model_validate(q))

    detail = ExamDetailResponse.model_validate(exam)
    detail.question_count = len(questions)
    detail.questions = questions

    return ResponseModel(code=200, data=detail)

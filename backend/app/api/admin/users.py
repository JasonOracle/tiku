from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin, User
from app.models.record import ExamRecord
from app.models.exam import Exam
from app.schemas.auth import UserResponse
from app.schemas.common import ResponseModel, PageResponse
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class AdminExamRecordResponse(BaseModel):
    record_id: int
    user_id: int
    username: str
    exam_id: int
    exam_title: str
    status: str
    score: int
    passed: bool
    time_spent: int
    start_time: datetime
    submit_time: Optional[datetime] = None

@router.get("", response_model=ResponseModel[PageResponse[UserResponse]])
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取注册 C端用户列表"""
    query = db.query(User)
    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    users = query.order_by(User.id.desc()).offset((page - 1) * size).limit(size).all()
    items = [UserResponse.model_validate(u) for u in users]

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

@router.get("/records", response_model=ResponseModel[PageResponse[AdminExamRecordResponse]])
def list_all_records(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取全站用户答题明细列表 (标准分页)"""
    query = db.query(ExamRecord)
    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    records = query.order_by(ExamRecord.id.desc()).offset((page - 1) * size).limit(size).all()
    
    items = []
    for r in records:
        u = db.query(User).filter(User.id == r.user_id).first()
        e = db.query(Exam).filter(Exam.id == r.exam_id).first()
        items.append(AdminExamRecordResponse(
            record_id=r.id,
            user_id=r.user_id,
            username=u.username if u else "已注销",
            exam_id=r.exam_id,
            exam_title=e.title if e else "已删除试卷",
            status=r.status,
            score=r.score,
            passed=r.passed,
            time_spent=r.time_spent,
            start_time=r.start_time,
            submit_time=r.submit_time
        ))

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

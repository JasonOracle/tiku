"""
[变更日志]
修改时间：2026-09-04 00:08:00
AI模型：Gemini 底层
修改内容：[1. C端分类查询仅返回 target_type='exam' 的试卷分类]
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.category import ExamCategory
from app.schemas.category import CategoryResponse
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("", response_model=ResponseModel[List[CategoryResponse]])
def get_categories(db: Session = Depends(get_db)):
    """获取 C 端试卷分类列表 (仅 target_type='exam')"""
    categories = db.query(ExamCategory).filter(ExamCategory.target_type == "exam").order_by(ExamCategory.sort_order.asc(), ExamCategory.id.asc()).all()
    return ResponseModel(code=200, data=categories)


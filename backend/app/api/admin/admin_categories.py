"""
[变更日志]
修改时间：2026-09-04 00:08:00
AI模型：Gemini 底层
修改内容：[1. 分类 CRUD 支持 target_type 过滤 (question 题目分类 / exam 试卷分类)]
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.category import ExamCategory
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("", response_model=ResponseModel[List[CategoryResponse]])
def list_admin_categories(
    target_type: Optional[str] = Query(None, description="分类用途: question (题目), exam (试卷)"),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取分类列表 (支持 target_type 隔离)"""
    query = db.query(ExamCategory)
    if target_type:
        query = query.filter(ExamCategory.target_type == target_type)
    categories = query.order_by(ExamCategory.sort_order.asc(), ExamCategory.id.asc()).all()
    return ResponseModel(code=200, data=categories)

@router.post("", response_model=ResponseModel[CategoryResponse], status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate, 
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端创建分类"""
    cat = ExamCategory(
        name=data.name, 
        target_type=data.target_type or "exam",
        icon=data.icon, 
        sort_order=data.sort_order
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return ResponseModel(code=201, message="分类创建成功", data=cat)


@router.put("/{category_id}", response_model=ResponseModel[CategoryResponse])
def update_category(
    category_id: int, 
    data: CategoryUpdate, 
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端修改分类"""
    cat = db.query(ExamCategory).filter(ExamCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(cat, k, v)

    db.commit()
    db.refresh(cat)
    return ResponseModel(code=200, message="分类修改成功", data=cat)

@router.delete("/{category_id}", response_model=ResponseModel[dict])
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端删除分类（被题目/试卷引用时拦截）"""
    from app.models.question import Question
    from app.models.exam import Exam
    cat = db.query(ExamCategory).filter(ExamCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")

    q_count = db.query(Question).filter(Question.category_id == category_id).count()
    e_count = db.query(Exam).filter(Exam.category_id == category_id).count()
    if q_count or e_count:
        parts = []
        if q_count:
            parts.append(f"{q_count}道题目")
        if e_count:
            parts.append(f"{e_count}张试卷")
        raise HTTPException(status_code=400, detail=f"该分类正被{''.join(parts)}使用，不可删除")

    db.delete(cat)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": category_id})

"""
[变更日志]
修改时间：2026-09-06 19:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增审计日志查询 API (仅超级管理员): 双域留痕全量检索]
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.audit import AuditLog
from app.schemas.common import ResponseModel, PageResponse

router = APIRouter()


@router.get("", response_model=ResponseModel[PageResponse[dict]])
def list_audit_logs(
    action_type: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    operator_type: Optional[str] = Query(None, description="admin 人类 / ai AI员工"),
    keyword: Optional[str] = Query(None, description="摘要关键字"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """审计日志列表 (仅超管可查; 新→旧排序)"""
    if admin.role != "super_admin":
        raise HTTPException(status_code=403, detail="仅超级管理员可查看审计日志")

    query = db.query(AuditLog)
    if action_type:
        query = query.filter(AuditLog.action_type == action_type)
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
    if operator_type:
        query = query.filter(AuditLog.operator_type == operator_type)
    if keyword:
        query = query.filter(AuditLog.summary.like(f"%{keyword}%"))

    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages
    logs = query.order_by(AuditLog.id.desc()).offset((page - 1) * size).limit(size).all()

    return ResponseModel(code=200, data=PageResponse(
        total=total, page=page, size=size, total_pages=total_pages, has_next=has_next,
        items=[{
            "id": a.id,
            "admin_id": a.admin_id,
            "operator_type": a.operator_type,
            "operator_name": a.operator_name,
            "action_type": a.action_type,
            "target_type": a.target_type,
            "target_id": a.target_id,
            "summary": a.summary,
            "before_data": a.before_data,
            "after_data": a.after_data,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else "",
        } for a in logs]))

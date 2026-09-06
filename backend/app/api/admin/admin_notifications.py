"""
[变更日志]
修改时间：2026-09-06 19:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增消息中心 API: 站内信列表/未读数红点/标记已读/全部已读]
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.notification import Notification
from app.schemas.common import ResponseModel, PageResponse

router = APIRouter()


@router.get("", response_model=ResponseModel[PageResponse[dict]])
def list_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """我的站内信列表 (倒序)"""
    query = db.query(Notification).filter(Notification.admin_id == admin.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)  # noqa: E712
    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages
    items = query.order_by(Notification.id.desc()).offset((page - 1) * size).limit(size).all()
    return ResponseModel(code=200, data=PageResponse(
        total=total, page=page, size=size, total_pages=total_pages, has_next=has_next,
        items=[{
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "notif_type": n.notif_type,
            "link": n.link or "",
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S") if n.created_at else "",
        } for n in items]))


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """未读数 (侧边栏红点轮询)"""
    count = db.query(Notification).filter(
        Notification.admin_id == admin.id, Notification.is_read == False  # noqa: E712
    ).count()
    return ResponseModel(code=200, data={"count": count})


class ReadRequest(BaseModel):
    ids: Optional[List[int]] = None  # 为空=全部已读


@router.post("/read")
def mark_read(
    data: ReadRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """标记已读 (ids 为空则全部已读)"""
    query = db.query(Notification).filter(
        Notification.admin_id == admin.id, Notification.is_read == False  # noqa: E712
    )
    if data.ids:
        query = query.filter(Notification.id.in_(data.ids))
    updated = query.update({Notification.is_read: True}, synchronize_session=False)
    db.commit()
    return ResponseModel(code=200, message=f"已读 {updated} 条", data={"updated": updated})

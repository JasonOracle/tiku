"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增审计留痕与站内信服务 (双域留痕: 人类/AI 写操作全量记录; 消息中心业务联动)]
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.models.notification import Notification


def write_audit(
    db: Session,
    action_type: str,
    target_type: str = "",
    target_id: Optional[int] = None,
    summary: str = "",
    before_data=None,
    after_data=None,
    admin=None,
    operator_type: str = "admin",
) -> None:
    """双域全量留痕: 任何写操作 (人类或 AI) 必须记录 操作人/动作/前后快照"""
    db.add(AuditLog(
        admin_id=admin.id if admin else None,
        operator_type=operator_type,
        operator_name=(admin.username if admin else ("" if operator_type != "ai" else "AI员工")),
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        summary=summary,
        before_data=before_data,
        after_data=after_data,
    ))


def push_notification(
    db: Session,
    admin_id: int,
    title: str,
    content: str = "",
    notif_type: str = "system",
    link: str = "",
) -> None:
    """向指定老师推送一条站内信"""
    db.add(Notification(
        admin_id=admin_id,
        title=title,
        content=content,
        notif_type=notif_type,
        link=link,
    ))

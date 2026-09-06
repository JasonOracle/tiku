"""
[变更日志]
修改时间：2026-09-06 17:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 Notification B端站内信模型 (消息中心)]
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from app.core.database import Base

class Notification(Base):
    """B端站内信 (AI 预批改完成 / 组卷草稿生成 / 批阅异常等业务联动通知)"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, nullable=False, index=True, comment="接收老师ID")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=True, default="", comment="通知正文")
    notif_type = Column(String(30), default="system", comment="通知类型 (grading, exam_draft, ai_error, system)")
    link = Column(String(255), nullable=True, default="", comment="B端跳转路径 (仅 /admin/ 开头)")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

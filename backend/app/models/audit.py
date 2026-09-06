"""
[变更日志]
修改时间：2026-09-06 17:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 AuditLog 双域留痕模型 (人类/AI 写操作全量审计)]
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    """审计日志模型: 任何写操作 (人类管理员或 AI 员工) 全量留痕"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, nullable=True, index=True, comment="操作人ID (AI 操作时可为空)")
    operator_type = Column(String(20), default="admin", comment="操作者类型 (admin 人类, ai AI员工, system 系统)")
    operator_name = Column(String(50), default="", comment="操作者名称快照")
    action_type = Column(String(50), nullable=False, comment="动作类型 (create/update/delete/publish/archive/grade/generate...)")
    target_type = Column(String(50), default="", comment="目标对象类型 (question/exam/record/admin/quota)")
    target_id = Column(Integer, nullable=True, comment="目标对象ID")
    summary = Column(String(255), default="", comment="动作摘要 (便于列表直读)")
    before_data = Column(JSON, nullable=True, comment="操作前数据快照")
    after_data = Column(JSON, nullable=True, comment="操作后数据")
    created_at = Column(DateTime, default=datetime.now, comment="操作时间")

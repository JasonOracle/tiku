"""
[变更日志]
修改时间：2026-09-06 17:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 AiUsageLog AI 算力流水模型 (额度内外有别: 主动创造扣老师额度, 被动阅卷记系统账单)]
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from app.core.database import Base

class AiUsageLog(Base):
    """AI 调用流水: 主动创造型 (出题/组卷/聊天) 扣减老师个人额度; 被动业务型 (交卷触发阅卷) admin_id 为空记系统账单"""
    __tablename__ = "ai_usage_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, nullable=True, index=True, comment="发起老师ID (null=系统业务兜底调用)")
    action = Column(String(30), nullable=False, comment="动作 (question_gen, exam_gen, chat, grading)")
    quota_delta = Column(Integer, default=0, comment="个人额度变动 (负数=扣减, 0=系统调用)")
    detail = Column(JSON, nullable=True, comment="调用明细 (模型/耗时/题目数等)")
    created_at = Column(DateTime, default=datetime.now, comment="调用时间")

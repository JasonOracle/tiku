"""
[变更日志]
修改时间：2026-09-04 00:08:00
AI模型：Gemini 底层
修改内容：[1. ExamCategory 模型增加 target_type 字段以区分题目分类与试卷分类]
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class ExamCategory(Base):
    """试卷与题目分类模型"""
    __tablename__ = "exam_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    target_type = Column(String(20), default="exam", nullable=False, comment="分类用途: question (题目分类), exam (试卷分类)")
    icon = Column(String(50), nullable=True, default="folder", comment="分类图标 key")
    sort_order = Column(Integer, default=0, comment="排序规则 (数字越小越靠前)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


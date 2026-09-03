"""
[变更日志]
修改时间：2026-09-03 23:36:00
AI模型：Gemini 底层
修改内容：[1. Question 模型添加 score 字段，默认分值 10 分]
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class Question(Base):
    """题目模型 (题海)"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(20), nullable=False, comment="题型 (single, multiple, judge)")
    title = Column(Text, nullable=False, comment="题目标题/题干")
    options = Column(JSON, nullable=True, comment="选项列表 JSON [{'key':'A', 'text':'xxx'}]")
    answer = Column(JSON, nullable=False, comment="正确答案 JSON ['A'] 或 ['A', 'B']")
    explanation = Column(Text, nullable=True, default="", comment="文字解析")
    difficulty = Column(String(20), default="medium", comment="难度 (easy, medium, hard)")
    score = Column(Integer, default=10, comment="题目默认分数")
    category_id = Column(Integer, ForeignKey("exam_categories.id", ondelete="SET NULL"), nullable=True, comment="所属分类ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


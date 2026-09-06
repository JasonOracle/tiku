"""
[变更日志]
修改时间：2026-09-06 17:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 主观题阅卷: ExamRecord 状态新增 pending_grading, 增加 ai_grading_result 与 short_scores]
"""
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from app.core.database import Base

class ExamRecord(Base):
    """用户答题记录模型
    状态机: in_progress -> submitted | timeout | pending_grading (含简答题待批阅) -> submitted
    ai_grading_result: {"suggestions": [{"question_id", "suggested_score", "comment"}], "error": str|null, "graded_at": str}
    short_scores: 简答题最终得分 {"<question_id>": score} (AI全托管或老师确认后写入)
    """
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="in_progress", comment="状态 (in_progress, submitted, timeout, pending_grading)")
    score = Column(Integer, default=0, comment="得分")
    passed = Column(Boolean, default=False, comment="是否及格")
    time_spent = Column(Integer, default=0, comment="用时时长 (秒)")
    start_time = Column(DateTime, default=datetime.now, comment="开始做题时间")
    submit_time = Column(DateTime, nullable=True, comment="提交/结算时间")
    user_answers = Column(JSON, nullable=True, comment="用户作答答案 JSON {question_id: ['A']}")
    ai_grading_result = Column(JSON, nullable=True, comment="AI 预批改详情与建议分数")
    short_scores = Column(JSON, nullable=True, comment="简答题最终得分 {question_id: score}")

class UserFavorite(Base):
    """用户收藏夹明细"""
    __tablename__ = "user_favorites"
    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='uix_user_question_favorite'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, comment="收藏时间")

from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from app.core.database import Base

class ExamRecord(Base):
    """用户答题记录模型"""
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="in_progress", comment="状态 (in_progress, submitted, timeout)")
    score = Column(Integer, default=0, comment="得分")
    passed = Column(Boolean, default=False, comment="是否及格")
    time_spent = Column(Integer, default=0, comment="用时时长 (秒)")
    start_time = Column(DateTime, default=datetime.now, comment="开始做题时间")
    submit_time = Column(DateTime, nullable=True, comment="提交/结算时间")
    user_answers = Column(JSON, nullable=True, comment="用户作答答案 JSON {question_id: ['A']}")

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

"""
[变更日志]
修改时间：2026-09-06 17:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 考试时间窗口与AI全托管: Exam 增加 start_time/end_time/is_ai_auto_grade/creator_id]
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class Exam(Base):
    """试卷模型"""
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="试卷标题")
    category_id = Column(Integer, ForeignKey("exam_categories.id", ondelete="SET NULL"), nullable=True, comment="分类ID")
    category_name = Column(String(100), nullable=True, default="", comment="上架时分类名称快照")
    cover_url = Column(String(255), nullable=True, default="", comment="试卷封面图片路径")
    is_timed = Column(Boolean, default=True, comment="是否限制作答时长")
    time_limit = Column(Integer, default=30, comment="限时时长 (分钟)")
    start_time = Column(DateTime, nullable=True, comment="考试开放开始时间 (空=不限制)")
    end_time = Column(DateTime, nullable=True, comment="考试开放结束时间 (空=不限制)")
    total_score = Column(Integer, default=100, comment="试卷总分")
    pass_score = Column(Integer, default=60, comment="及格分数")
    pass_percent = Column(Integer, default=60, comment="及格百分比 0-100")
    status = Column(String(20), default="draft", nullable=False, comment="状态: draft (待上架), published (已上架), archived (已下架)")
    is_recommended = Column(Boolean, default=False, comment="是否在首页推荐推荐")
    is_random = Column(Boolean, default=False, comment="是否随机题目顺序")
    is_ai_auto_grade = Column(Boolean, default=False, comment="AI全权阅卷开关 (含简答题时生效: 开启=AI批完直接发布成绩)")
    creator_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True, comment="创建老师ID (试卷隔离依据)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")



class ExamQuestion(Base):
    """试卷与题目关联明细表"""
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, default=10, comment="该题在此试卷中的分值")
    sort_order = Column(Integer, default=0, comment="题目在试卷中的顺序")

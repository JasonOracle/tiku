"""
[变更日志]
修改时间：2026-09-06 17:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 题型扩展: Question 增加 is_deleted 软删除 / source 来源标签 / grading_points 简答题踩分点, answer 兼容填空二维数组]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[个人数据感知: Question 增加 creator_id 出题人归属列 (AI 助管统计“我创建了几道题”依据)]
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.core.database import Base

class Question(Base):
    """题目模型 (题海)
    题型 type: single(单选) / multiple(多选) / judge(判断) / fill(填空) / short(简答)
    answer 结构:
      - single/multiple/judge: ['A'] 或 ['A','B']
      - fill: 二维数组 [["北京","北京市"],["是"]] (外层=空, 内层=可接受答案)
      - short: ["标准答案全文"]
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(20), nullable=False, comment="题型 (single, multiple, judge, fill, short)")
    title = Column(Text, nullable=False, comment="题目标题/题干 (填空题用 ___ 作空位占位符)")
    options = Column(JSON, nullable=True, comment="选项列表 JSON [{'key':'A', 'text':'xxx'}]")
    answer = Column(JSON, nullable=False, comment="正确答案 JSON (题型相关, 见类注释)")
    explanation = Column(Text, nullable=True, default="", comment="文字解析")
    grading_points = Column(JSON, nullable=True, comment="简答题踩分点 JSON ['要点1','要点2']")
    difficulty = Column(String(20), default="medium", comment="难度 (easy, medium, hard)")
    score = Column(Integer, default=10, comment="题目默认分数")
    source = Column(String(20), default="manual", comment="来源 (manual 人工, ai AI生成)")
    is_deleted = Column(Boolean, default=False, comment="软删除标记 (防牵连: 已引用试卷仍可拉取原题)")
    category_id = Column(Integer, ForeignKey("exam_categories.id", ondelete="SET NULL"), nullable=True, comment="所属分类ID")
    creator_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True, comment="创建出题人ID (个人统计依据, 历史数据可空)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

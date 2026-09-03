"""
[变更日志]
修改时间：2026-09-04 00:08:00
AI模型：Gemini 底层
修改内容：[1. Exam Schema 添加 status 上下架状态定义; 2. 新增 ExamStatsResponse 考情看板数据结构]
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any
from app.schemas.question import QuestionResponse

class ExamQuestionConfig(BaseModel):
    question_id: int = Field(..., description="题目ID")
    score: Optional[int] = Field(10, description="分值")
    sort_order: Optional[int] = Field(0, description="试卷内部排序")

class ExamCreate(BaseModel):
    title: str = Field(..., description="试卷标题")
    category_id: Optional[int] = Field(None, description="分类ID")
    cover_url: Optional[str] = Field("", description="封面图片路径")
    is_timed: bool = Field(True, description="是否限时")
    time_limit: int = Field(30, description="做题限制时长(分钟)")
    pass_percent: int = Field(60, description="及格百分比 0-100")
    status: Optional[str] = Field("draft", description="状态: draft (待上架), published (已上架)")
    is_recommended: bool = Field(False, description="首页推荐标识")
    question_ids: Optional[List[int]] = Field(default=[], description="包含的题目ID列表")
    questions: Optional[List[ExamQuestionConfig]] = Field(default=[], description="组卷关联题目与分值明细")

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    cover_url: Optional[str] = None
    is_timed: Optional[bool] = None
    time_limit: Optional[int] = None
    pass_percent: Optional[int] = None
    status: Optional[str] = None
    is_recommended: Optional[bool] = None
    question_ids: Optional[List[int]] = None
    questions: Optional[List[ExamQuestionConfig]] = None

class ExamQuestionDetail(BaseModel):
    id: int
    exam_id: int
    question_id: int
    score: int
    sort_order: int
    question: Optional[Any] = None

class ExamResponse(BaseModel):
    id: int
    title: str
    category_id: Optional[int] = None
    category_name: Optional[str] = ""
    cover_url: Optional[str] = ""
    is_timed: bool = True
    time_limit: int = 30
    total_score: int = 0
    pass_score: int = 0
    pass_percent: int = 60
    status: str = "draft"
    is_recommended: bool = False
    question_count: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class ExamUserRecordItem(BaseModel):
    record_id: int
    user_id: int
    username: str
    score: int
    is_passed: bool
    time_spent: int
    submit_time: str

class ExamStatsResponse(BaseModel):
    exam_id: int
    title: str
    total_participants: int
    avg_score: float
    pass_rate: float
    user_records: List[ExamUserRecordItem] = []


class ExamDetailResponse(ExamResponse):
    questions: List[QuestionResponse] = []


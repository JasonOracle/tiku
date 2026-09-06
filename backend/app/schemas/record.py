"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 Schema 扩展: 答题响应携带时间窗(end_time/server_now); 报告支持待批阅降级查看(pending)与防泄题解析锁(analysis_locked)与多选半对/简答评语]
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.schemas.question import QuestionResponse

class ExamStartRequest(BaseModel):
    exam_id: int = Field(..., description="试卷ID")

class ExamStartResponse(BaseModel):
    record_id: int = Field(..., description="答题记录ID")
    exam_id: int
    exam_title: str
    is_timed: bool
    time_limit: int
    total_score: int
    pass_score: int
    start_time: datetime
    end_time: Optional[datetime] = Field(None, description="考试开放截止时间 (倒计时硬边界)")
    server_now: datetime = Field(..., description="服务器当前时间 (前端据此计算剩余时长)")
    questions: List[QuestionResponse]

class ExamSubmitRequest(BaseModel):
    record_id: int = Field(..., description="答题记录ID")
    user_answers: Dict[str, List[str]] = Field(..., description="作答答案 JSON { 'question_id': ['A'] }")
    time_spent: int = Field(0, description="做题消耗时长 (秒)")

class QuestionAnalysisItem(BaseModel):
    question: QuestionResponse
    user_answer: List[str] = []
    correct_answer: List[Any] = []
    is_correct: Optional[bool] = Field(None, description="None=简答题待批阅")
    is_pending: bool = False
    is_partial: bool = Field(False, description="多选漏选半对")
    is_favorited: bool = False
    gained: int = Field(0, description="本题得分")
    eq_score: int = Field(0, description="本题满分 (组卷分值)")
    comment: str = Field("", description="AI/教师评语 (简答题)")

class ExamReportResponse(BaseModel):
    record_id: int
    exam_id: int
    exam_title: str
    user_id: int
    status: str
    pending: bool = Field(False, description="是否待批阅 (成绩未发布, 降级仅查看自己的作答)")
    analysis_locked: bool = Field(False, description="解析锁: 考试 end_time 未到时禁止查看标准答案 (防泄题)")
    score: int = Field(0, description="得分 (待批阅时为0)")
    total_score: int = 0
    pass_score: int = 0
    passed: bool = False
    time_spent: int = 0
    total_questions: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    partial_count: int = Field(0, description="多选半对题数")
    pending_count: int = Field(0, description="待批阅简答题数")
    start_time: Optional[datetime] = None
    submit_time: Optional[datetime] = None
    questions_analysis: List[QuestionAnalysisItem] = []

class FavoriteRequest(BaseModel):
    question_id: int = Field(..., description="题目ID")

class FavoriteResponse(BaseModel):
    id: int
    question_id: int
    created_at: datetime
    question: Optional[QuestionResponse] = None

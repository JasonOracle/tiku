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
    questions: List[QuestionResponse]

class ExamSubmitRequest(BaseModel):
    record_id: int = Field(..., description="答题记录ID")
    user_answers: Dict[str, List[str]] = Field(..., description="作答答案 JSON { 'question_id': ['A'] }")
    time_spent: int = Field(0, description="做题消耗时长 (秒)")

class QuestionAnalysisItem(BaseModel):
    question: QuestionResponse
    user_answer: List[str] = []
    correct_answer: List[str] = []
    is_correct: bool = False
    is_favorited: bool = False

class ExamReportResponse(BaseModel):
    record_id: int
    exam_id: int
    exam_title: str
    user_id: int
    status: str
    score: int
    passed: bool
    time_spent: int
    total_questions: int
    correct_count: int
    wrong_count: int
    start_time: datetime
    submit_time: Optional[datetime] = None
    questions_analysis: List[QuestionAnalysisItem] = []

class FavoriteRequest(BaseModel):
    question_id: int = Field(..., description="题目ID")

class FavoriteResponse(BaseModel):
    id: int
    question_id: int
    created_at: datetime
    question: Optional[QuestionResponse] = None

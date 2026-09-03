"""
[变更日志]
修改时间：2026-09-03 23:36:00
AI模型：Gemini 底层
修改内容：[1. Question Pydantic Schema 加入 score 字段定义]
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any, Dict

class OptionItem(BaseModel):
    key: str = Field(..., description="选项标识如 'A', 'B', 'C'")
    text: str = Field(..., description="选项具体文字描述")

class QuestionCreate(BaseModel):
    type: str = Field(..., description="题型: single(单选), multiple(多选), judge(判断)")
    title: str = Field(..., description="题目题干说明")
    options: Optional[List[OptionItem]] = Field(default=[], description="选项列表")
    answer: List[str] = Field(..., description="标准答案列表，例 ['A']")
    explanation: Optional[str] = Field("", description="文字详细解析")
    difficulty: Optional[str] = Field("medium", description="难度: easy, medium, hard")
    score: Optional[int] = Field(10, description="题目默认分值")
    category_id: Optional[int] = Field(None, description="所属分类ID")

class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    options: Optional[List[OptionItem]] = None
    answer: Optional[List[str]] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    score: Optional[int] = None
    category_id: Optional[int] = None

class QuestionResponse(BaseModel):
    id: int
    type: str
    title: str
    options: Optional[List[Dict[str, Any]]] = []
    answer: List[str]
    explanation: Optional[str] = ""
    difficulty: str = "medium"
    score: int = 10
    category_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


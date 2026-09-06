"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 Schema 扩展: 题型支持 fill/short, 新增 grading_points/source/locked 字段]
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any, Dict

class OptionItem(BaseModel):
    key: str = Field(..., description="选项标识如 'A', 'B', 'C'")
    text: str = Field(..., description="选项具体文字描述")

class QuestionCreate(BaseModel):
    type: str = Field(..., description="题型: single(单选), multiple(多选), judge(判断), fill(填空), short(简答)")
    title: str = Field(..., description="题目题干说明 (填空题用 ___ 作空位占位符)")
    options: Optional[List[OptionItem]] = Field(default=[], description="选项列表 (填空/简答为空)")
    answer: List[Any] = Field(..., description="标准答案: 客观题 ['A']; 填空题二维数组 [['北京','北京市'],['是']]; 简答题 ['答案全文']")
    grading_points: Optional[List[str]] = Field(default=[], description="简答题踩分点列表")
    explanation: Optional[str] = Field("", description="文字详细解析")
    difficulty: Optional[str] = Field("medium", description="难度: easy, medium, hard")
    score: Optional[int] = Field(10, description="题目默认分值")
    category_id: Optional[int] = Field(None, description="所属分类ID")
    source: Optional[str] = Field("manual", description="来源: manual 人工 / ai AI生成")

class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    options: Optional[List[OptionItem]] = None
    answer: Optional[List[Any]] = None
    grading_points: Optional[List[str]] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    score: Optional[int] = None
    category_id: Optional[int] = None

class QuestionResponse(BaseModel):
    id: int
    type: str
    title: str
    options: Optional[List[Dict[str, Any]]] = []
    answer: List[Any]
    grading_points: Optional[List[str]] = []
    explanation: Optional[str] = ""
    difficulty: str = "medium"
    score: int = 10
    source: str = "manual"
    is_deleted: bool = False
    locked: bool = False
    category_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

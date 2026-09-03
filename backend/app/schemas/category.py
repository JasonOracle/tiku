"""
[变更日志]
修改时间：2026-09-04 00:08:00
AI模型：Gemini 底层
修改内容：[1. Category Schema 加入 target_type 分类用途属性定义]
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100, description="分类名称")
    target_type: Optional[str] = Field("exam", description="分类用途: question (题目分类), exam (试卷分类)")
    icon: Optional[str] = Field("folder", description="分类图标标识")
    sort_order: Optional[int] = Field(0, description="排序")

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    target_type: Optional[str] = Field(None)
    icon: Optional[str] = Field(None)
    sort_order: Optional[int] = Field(None)

class CategoryResponse(BaseModel):
    id: int
    name: str
    target_type: Optional[str] = "question"
    icon: Optional[str] = "folder"
    sort_order: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


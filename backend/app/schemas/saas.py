"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[新建多租户契约 Schema：登录/成员/资源/任务/核验/知识库]
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class PhoneLoginRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class JoinedTenant(BaseModel):
    tenant_id: int
    tenant_name: str = ""
    role: str = "member"


class SysUserOut(BaseModel):
    id: int
    phone: str
    display_name: Optional[str] = ""
    is_super_admin: bool = False

    class Config:
        from_attributes = True


class LoginData(BaseModel):
    token: str
    user: SysUserOut
    default_tenant_id: Optional[int] = None
    joined_tenants: List[JoinedTenant] = []


class MemberCreate(BaseModel):
    phone: str = Field(..., description="成员手机号")
    name: Optional[str] = Field(None, description="展示名")
    role: Optional[str] = Field("member", description="owner/admin/member")


class ResourceCreate(BaseModel):
    type: str = "single_choice"
    content: str
    options: Optional[Any] = None
    correct_answer: Optional[Any] = None
    score: int = 10
    category_id: Optional[int] = None
    ai_rag_sources: Optional[Any] = None


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    cover_image: Optional[str] = ""
    category_id: Optional[int] = None
    is_timed: bool = False
    time_limit: Optional[int] = None
    start_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    verification_mode: str = "manual"
    resource_ids: List[int] = []


class SubmitAnswers(BaseModel):
    task_id: int
    time_spent: int = 0
    answers: List[Any] = []


class VerifyConfirm(BaseModel):
    accept_ai_suggestion: bool = True
    final_score: Optional[int] = None
    comments: Optional[str] = ""

"""
[变更日志]
修改时间：2026-09-06 19:10:00
AI模型：ZCode (GLM)
修改内容：[v1.3: RegisterRequest 扩展注册资料 (昵称必填/性别必选/手机号必填/职务邮箱选填), UserResponse 带全量资料]
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RegisterRequest(BaseModel):
    """注册请求: 必填/格式校验由接口层手动执行并返回 400 中文提示 (C端不解析 422)"""
    username: Optional[str] = Field(None, description="用户名 (3-50位)")
    password: Optional[str] = Field(None, description="密码 (6-100位)")
    nickname: Optional[str] = Field(None, description="昵称 (必填, 1-30位)")
    gender: Optional[str] = Field(None, description="性别 (male/female, 必选)")
    phone: Optional[str] = Field(None, description="手机号 (必填, 大陆11位, 全局唯一)")
    position: Optional[str] = Field(None, description="职务 (选填)")
    email: Optional[str] = Field(None, description="邮箱 (选填)")

class UserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    gender: Optional[str] = None
    position: Optional[str] = ""
    phone: Optional[str] = None
    email: Optional[str] = ""
    avatar: Optional[str] = ""
    status: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class AdminResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = ""
    position: Optional[str] = ""
    bio: Optional[str] = ""
    role: str
    status: bool = True
    ai_quota_limit: int = 0
    daily_ai_quota: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class AdminProfileUpdate(BaseModel):
    """B端管理员个人信息修改（白名单，不允许修改 role/username/quota 等敏感字段）"""
    name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    gender: Optional[str] = Field(None, description="性别 (male/female)")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    position: Optional[str] = Field(None, max_length=50, description="职务")
    bio: Optional[str] = Field(None, max_length=500, description="个人介绍")

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class TokenResponse(BaseModel):
    token: str = Field(..., description="JWT Bearer Token")
    user: Optional[UserResponse] = None
    admin: Optional[AdminResponse] = None

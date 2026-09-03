from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

class UserResponse(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = ""
    status: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class AdminResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class TokenResponse(BaseModel):
    token: str = Field(..., description="JWT Bearer Token")
    user: Optional[UserResponse] = None
    admin: Optional[AdminResponse] = None

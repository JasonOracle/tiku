"""
[变更日志]
修改时间：2026-09-06 19:10:00
AI模型：ZCode (GLM)
修改内容：[v1.3: 注册扩展昵称/性别/手机号/职务/邮箱资料, 手动校验全部返回 400 中文提示 (C端不解析 422)]
"""
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.schemas.common import ResponseModel

router = APIRouter()

PHONE_RE = re.compile(r"^1[3-9]\d{9}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@router.post("/register", response_model=ResponseModel[UserResponse], status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    """C端用户注册 (昵称必填/性别必选/手机号必填唯一/职务邮箱选填)"""
    username = (data.username or "").strip()
    password = data.password or ""
    nickname = (data.nickname or "").strip()
    gender = (data.gender or "").strip().lower()
    phone = (data.phone or "").strip()
    position = (data.position or "").strip()
    email = (data.email or "").strip()

    if not username or len(username) < 3 or len(username) > 50:
        raise HTTPException(status_code=400, detail="用户名需为 3-50 位字符")
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    if not nickname:
        raise HTTPException(status_code=400, detail="请填写昵称")
    if len(nickname) > 30:
        raise HTTPException(status_code=400, detail="昵称不能超过 30 个字符")
    if gender not in ("male", "female"):
        raise HTTPException(status_code=400, detail="请选择性别")
    if not phone or not PHONE_RE.match(phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确（需为大陆 11 位手机号）")
    if email and not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="该用户名已被占用")
    if db.query(User).filter(User.phone == phone).first():
        raise HTTPException(status_code=400, detail="该手机号已被注册")

    user = User(
        username=username,
        password_hash=get_password_hash(password),
        nickname=nickname,
        gender=gender,
        phone=phone,
        position=position,
        email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ResponseModel(code=201, message="注册成功", data=user)


@router.post("/login", response_model=ResponseModel[TokenResponse])
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    """C端用户登录"""
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    if not user.status:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_access_token(subject=user.id, user_type="user")
    return ResponseModel(
        code=200,
        message="登录成功",
        data=TokenResponse(token=token, user=user)
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.schemas.common import ResponseModel

router = APIRouter()

@router.post("/register", response_model=ResponseModel[UserResponse], status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    """C端用户注册"""
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="该用户名已被占用")

    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password)
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

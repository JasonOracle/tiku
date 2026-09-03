from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import Admin
from app.schemas.auth import RegisterRequest, LoginRequest, AdminResponse, TokenResponse
from app.schemas.common import ResponseModel

router = APIRouter()

@router.post("/login", response_model=ResponseModel[TokenResponse])
def login_admin(data: LoginRequest, db: Session = Depends(get_db)):
    """B端管理员登录"""
    admin = db.query(Admin).filter(Admin.username == data.username).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=400, detail="管理员账号或密码错误")

    token = create_access_token(subject=admin.id, user_type="admin")
    return ResponseModel(
        code=200,
        message="登录成功",
        data=TokenResponse(token=token, admin=admin)
    )

@router.post("/init", response_model=ResponseModel[AdminResponse], status_code=status.HTTP_201_CREATED)
def init_super_admin(data: RegisterRequest, db: Session = Depends(get_db)):
    """初始化超级管理员 (仅在无管理员时可调用)"""
    count = db.query(Admin).count()
    if count > 0:
        raise HTTPException(status_code=400, detail="系统已初始化管理员，禁止重复调用")

    admin = Admin(
        username=data.username,
        password_hash=get_password_hash(data.password),
        role="super_admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return ResponseModel(code=201, message="超级管理员初始化成功", data=admin)

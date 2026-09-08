from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.schemas.auth import RegisterRequest, LoginRequest, AdminResponse, AdminProfileUpdate, TokenResponse
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("/me", response_model=ResponseModel[AdminResponse])
def get_admin_profile(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端当前管理员信息 (含角色与今日 AI 额度余额, 前端 RBAC 菜单与额度展示依赖)"""
    from app.services.quota_service import refresh_daily_quota
    refresh_daily_quota(admin)
    db.commit()
    return ResponseModel(code=200, data=admin)


@router.post("/login", response_model=ResponseModel[TokenResponse])
def login_admin(data: LoginRequest, db: Session = Depends(get_db)):
    """B端管理员登录"""
    admin = db.query(Admin).filter(Admin.username == data.username).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=400, detail="管理员账号或密码错误")
    if not admin.status:
        raise HTTPException(status_code=403, detail="该账号已被禁用，请联系超级管理员")

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


@router.put("/profile", response_model=ResponseModel[AdminResponse])
def update_admin_profile(
    data: AdminProfileUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端管理员更新个人信息（白名单字段，不允许修改角色/额度等敏感项）"""
    # 只更新实际传入的非 None 字段
    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(admin, field, value)
    db.commit()
    db.refresh(admin)
    return ResponseModel(code=200, message="个人信息已更新", data=admin)

"""
[变更日志]
修改时间：2026-09-07 01:05:00
AI模型：Gemini 系列
修改内容：[重构三级权限架构 API: 允许超级管理员创建管理员/出题人，管理员创建出题人；增加 name(姓名)/phone(手机号) 字段]
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.core.security import get_password_hash
from app.models.user import Admin
from app.schemas.common import ResponseModel, PageResponse
from app.services.quota_service import refresh_daily_quota
from app.services.audit_service import write_audit

router = APIRouter()


def require_admin_or_super(admin: Admin) -> None:
    if admin.role not in ("super_admin", "admin"):
        raise HTTPException(status_code=403, detail="仅管理员或超级管理员可执行此操作")


class MemberCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    name: Optional[str] = Field(None, max_length=50, description="真实姓名/名字")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    password: str = Field(..., min_length=6, max_length=100)
    ai_quota_limit: int = Field(20, ge=0, le=10000, description="每日 AI 额度")
    role: str = Field("teacher", description="角色: admin 管理员 / teacher 出题人")

class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    role: Optional[str] = Field(None, description="角色: admin / teacher")
    ai_quota_limit: Optional[int] = Field(None, ge=0, le=10000)
    status: Optional[bool] = None

class QuotaRefill(BaseModel):
    amount: int = Field(..., ge=1, le=10000, description="即时补充的今日余额")


@router.get("", response_model=ResponseModel[PageResponse[dict]])
def list_members(
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """成员列表 (含角色/状态/姓名/手机号/额度配置/今日余额)"""
    require_admin_or_super(admin)
    query = db.query(Admin)
    if keyword:
        query = query.filter(
            (Admin.username.like(f"%{keyword}%")) | (Admin.name.like(f"%{keyword}%"))
        )
    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages
    members = query.order_by(Admin.id.asc()).offset((page - 1) * size).limit(size).all()

    from app.models.exam import Exam
    items = []
    for m in members:
        refresh_daily_quota(m)
        items.append({
            "id": m.id,
            "username": m.username,
            "name": m.name or "",
            "phone": m.phone or "",
            "role": m.role,
            "status": m.status,
            "ai_quota_limit": m.ai_quota_limit or 0,
            "daily_ai_quota": m.daily_ai_quota or 0,
            "quota_reset_date": str(m.quota_reset_date) if m.quota_reset_date else None,
            "exam_count": db.query(Exam).filter(Exam.creator_id == m.id).count(),
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
        })
    db.commit()
    return ResponseModel(code=200, data=PageResponse(
        total=total, page=page, size=size, total_pages=total_pages, has_next=has_next, items=items))


@router.post("", response_model=ResponseModel[dict], status_code=201)
def create_member(
    data: MemberCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """创建账号 (超管可创建管理员/出题人；管理员仅可创建出题人)"""
    require_admin_or_super(admin)
    if admin.role == "admin" and data.role != "teacher":
        raise HTTPException(status_code=403, detail="管理员仅可创建出题人账号")
    if data.role not in ("admin", "teacher"):
        raise HTTPException(status_code=400, detail="角色非法，可选 role: admin(管理员) 或 teacher(出题人)")

    if db.query(Admin).filter(Admin.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    member = Admin(
        username=data.username,
        name=data.name,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        role=data.role,
        status=True,
        ai_quota_limit=data.ai_quota_limit,
        daily_ai_quota=data.ai_quota_limit,
        quota_reset_date=datetime.now().date(),
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    write_audit(db, "create", "admin", member.id, summary=f"创建账号 {member.username}({data.role}) (每日AI额度 {data.ai_quota_limit})",
                after_data={"username": member.username, "role": data.role, "ai_quota_limit": data.ai_quota_limit}, admin=admin)
    db.commit()
    return ResponseModel(code=201, message="创建成功", data={"id": member.id, "username": member.username})


@router.put("/{member_id}", response_model=ResponseModel[dict])
def update_member(
    member_id: int,
    data: MemberUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """编辑成员: 改密/改名/改手机/改角色/调整每日额度/启用禁用"""
    require_admin_or_super(admin)
    member = db.query(Admin).filter(Admin.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="账号不存在")
    if admin.role == "admin" and member.role in ("super_admin", "admin") and member.id != admin.id:
        raise HTTPException(status_code=403, detail="普通管理员无法编辑其他管理员或超级管理员")

    if member.role == "super_admin" and member.id == admin.id and data.status is False:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    before = {"name": member.name, "phone": member.phone, "role": member.role, "ai_quota_limit": member.ai_quota_limit, "status": member.status}
    if data.name is not None:
        member.name = data.name
    if data.phone is not None:
        member.phone = data.phone
    if data.role is not None and admin.role == "super_admin":
        member.role = data.role
    if data.password:
        member.password_hash = get_password_hash(data.password)
    if data.ai_quota_limit is not None:
        member.ai_quota_limit = data.ai_quota_limit
        member.quota_reset_date = datetime.now().date()
        member.daily_ai_quota = data.ai_quota_limit
    if data.status is not None:
        member.status = data.status
    db.commit()

    write_audit(db, "update", "admin", member.id,
                summary=f"编辑账号 {member.username}",
                before_data=before,
                after_data={"name": member.name, "phone": member.phone, "role": member.role, "ai_quota_limit": member.ai_quota_limit, "status": member.status}, admin=admin)
    db.commit()
    return ResponseModel(code=200, message="更新成功", data={"id": member.id})


@router.post("/{member_id}/refill", response_model=ResponseModel[dict])
def refill_quota(
    member_id: int,
    data: QuotaRefill,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """即时补充账号今日 AI 余额"""
    require_admin_or_super(admin)
    member = db.query(Admin).filter(Admin.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="账号不存在")
    refresh_daily_quota(member)
    member.daily_ai_quota = (member.daily_ai_quota or 0) + data.amount
    db.commit()
    write_audit(db, "refill_quota", "admin", member.id,
                summary=f"为 {member.username} 补充今日 AI 额度 +{data.amount}",
                after_data={"daily_ai_quota": member.daily_ai_quota}, admin=admin)
    db.commit()
    return ResponseModel(code=200, message=f"已补充 {data.amount} 次", data={
        "id": member.id, "daily_ai_quota": member.daily_ai_quota})

"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[成员搜索 + PUT 编辑；手机号 UPSERT 录入不变]
"""
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.api.deps import require_admin
from app.api.saas.ops import write_audit
from app.models.saas import SysUser, SysTenantUser, SysUserProfile

router = APIRouter()
PHONE_RE = re.compile(r"^1[3-9]\d{9}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@router.post("")
def create_member(payload: dict, ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    phone = str(payload.get("phone") or "").strip()
    name = str(payload.get("name") or payload.get("display_name") or "").strip()
    role = str(payload.get("role") or "member").strip()
    if not PHONE_RE.match(phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    if role not in ("owner", "admin", "member"):
        role = "member"
    tenant_id = ctx["tenant_id"]
    user = db.query(SysUser).filter(SysUser.phone == phone).first()
    if not user:
        user = SysUser(phone=phone, username=phone, password_hash=get_password_hash("123456"),
                       display_name=name or phone)
        db.add(user)
        db.flush()
    rel = db.query(SysTenantUser).filter(
        SysTenantUser.tenant_id == tenant_id, SysTenantUser.user_id == user.id).first()
    if not rel:
        rel = SysTenantUser(tenant_id=tenant_id, user_id=user.id, role=role, status="active")
        db.add(rel)
    else:
        rel.role = role
        rel.status = "active"
    # 可选写入 profile 六字段
    nickname = str(payload.get("nickname") or "").strip() or None
    email = str(payload.get("email") or "").strip() or None
    occupation = str(payload.get("occupation") or "").strip() or None
    bio = str(payload.get("bio") or "").strip() or None
    age = payload.get("age")
    gender = str(payload.get("gender") or "").strip() or None
    if nickname or email or occupation or bio or age or gender:
        _ensure_profile(db, user.id, nickname, email, occupation, bio, age, gender)
    db.flush()
    write_audit(db, tenant_id, ctx["user"], "create", "member", user.id,
                f"录入成员 {phone}（{role}）")
    db.commit()
    return {"code": 201, "message": "成员添加成功", "data": {"user_id": user.id, "tenant_id": tenant_id}}


@router.get("")
def list_members(ctx: dict = Depends(require_admin), db: Session = Depends(get_db),
                 page: int = 1, size: int = 20, keyword: str = ""):
    tenant_id = ctx["tenant_id"]
    q = db.query(SysTenantUser, SysUser).join(SysUser, SysUser.id == SysTenantUser.user_id).filter(
        SysTenantUser.tenant_id == tenant_id, SysTenantUser.status == "active")
    if keyword.strip():
        kw = f"%{keyword.strip()}%"
        q = q.filter(
            (SysUser.phone.like(kw)) |
            (SysUser.display_name.like(kw)) |
            (SysUserProfile.nickname.like(kw)))
    total = q.count()
    rows = q.offset((page - 1) * size).limit(size).all()
    items = []
    for r, u in rows:
        profile = db.query(SysUserProfile).filter(SysUserProfile.user_id == u.id).first()
        items.append({
            "user_id": u.id,
            "phone": u.phone,
            "display_name": u.display_name,
            "nickname": profile.nickname if profile else None,
            "email": profile.email if profile else None,
            "role": r.role,
            "status": r.status
        })
    return {"code": 200, "data": {"total": total, "page": page, "size": size,
            "items": items}}


@router.put("/{user_id}")
def update_member(user_id: int, payload: dict, ctx: dict = Depends(require_admin),
                  db: Session = Depends(get_db)):
    tenant_id = ctx["tenant_id"]
    uid = int(user_id)
    rel = db.query(SysTenantUser).filter(
        SysTenantUser.tenant_id == tenant_id, SysTenantUser.user_id == uid).first()
    if not rel:
        raise HTTPException(status_code=404, detail="成员不存在或不属于本租户")
    user = db.query(SysUser).filter(SysUser.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 角色约束：不能把自己降权
    if str(uid) == str(ctx["user"].id) and rel.role in ("owner", "admin"):
        new_role = str(payload.get("role") or rel.role).strip()
        if new_role in ("member",) and rel.role in ("owner", "admin"):
            raise HTTPException(status_code=400, detail="不能将自己从管理员降为普通成员")
        if new_role != rel.role:
            rel.role = new_role
    elif "role" in payload:
        new_role = str(payload["role"] or "").strip()
        if new_role in ("owner", "admin", "member"):
            rel.role = new_role
    # 状态：不能禁用自己
    if "status" in payload:
        new_status = str(payload["status"] or "").strip()
        if new_status not in ("active", "disabled"):
            raise HTTPException(status_code=400, detail="status 必须为 active 或 disabled")
        if new_status == "disabled" and str(uid) == str(ctx["user"].id):
            raise HTTPException(status_code=400, detail="不能禁用自己")
        rel.status = new_status
    # 展示名
    if "display_name" in payload:
        user.display_name = str(payload["display_name"] or "").strip()[:50] or None
    # Profile 六字段
    nickname = payload.get("nickname")
    email = payload.get("email")
    occupation = payload.get("occupation")
    bio = payload.get("bio")
    age = payload.get("age")
    gender = payload.get("gender")
    has_profile_fields = nickname is not None or email is not None or occupation is not None \
                         or bio is not None or age is not None or gender is not None
    if has_profile_fields:
        if email is not None and email and not EMAIL_RE.match(str(email)):
            raise HTTPException(status_code=400, detail="邮箱格式不正确")
        if gender is not None and gender and str(gender) not in ("male", "female", "secret", ""):
            raise HTTPException(status_code=400, detail="性别必须为 male/female/secret")
        _ensure_profile(db, uid,
                        str(nickname).strip() if nickname else None,
                        str(email).strip() if email else None,
                        str(occupation).strip() if occupation else None,
                        str(bio).strip() if bio else None,
                        int(age) if age is not None else None,
                        str(gender).strip() if gender else None)
    db.flush()
    write_audit(db, tenant_id, ctx["user"], "update", "member", uid,
                f"编辑成员 {user.phone}（{rel.role} {rel.status}）")
    db.commit()
    db.refresh(user)
    profile = db.query(SysUserProfile).filter(SysUserProfile.user_id == uid).first()
    return {"code": 200, "message": "成员已更新", "data": {
        "user_id": uid, "phone": user.phone,
        "display_name": user.display_name, "nickname": profile.nickname if profile else None,
        "email": profile.email if profile else None,
        "role": rel.role, "status": rel.status}}


def _ensure_profile(db: Session, user_id: int,
                    nickname, email, occupation, bio, age, gender):
    p = db.query(SysUserProfile).filter(SysUserProfile.user_id == user_id).first()
    if not p:
        p = SysUserProfile(user_id=user_id)
        db.add(p)
        db.flush()
    if nickname is not None: p.nickname = nickname
    if email is not None: p.email = email
    if occupation is not None: p.occupation = occupation
    if bio is not None: p.bio = bio
    if age is not None: p.age = age
    if gender is not None: p.gender = gender


def _mask_key(key: str) -> str:
    if not key: return ""
    k = str(key)
    return "****" + k[-4:] if len(k) > 4 else "****"

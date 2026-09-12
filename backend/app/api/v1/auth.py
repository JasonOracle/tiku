"""
[变更日志]
修改时间：2026-09-12
AI模型：OpenCode / DeepSeek
修改内容：[权限隔离重构：B端登录（携带 X-Client: admin 标识）拦截纯学员身份——非 super_admin 且未在任一租户持有 owner/admin 角色时返回 403，落实「Member 仅限 C 端做题」严格二分法；C 端不传该标识，登录链路零改动]
修改时间：2026-09-10
AI模型：Muse Spark
修改内容：[GET /me 联表回显 profile 六字段，修复资料有写无读]
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_sys_user
from app.models.saas import SysUser, SysTenant, SysTenantUser, SysUserProfile, SysUserProfile

router = APIRouter()


@router.post("/register", status_code=410)
def register_closed():
    """开放注册已永久关闭：成员由企业管理员静默录入。"""
    raise HTTPException(status_code=410, detail="开放注册已关闭，请联系企业管理员录入手机号后登录")


@router.get("/me")
def get_me(user: SysUser = Depends(get_current_sys_user),
           db: Session = Depends(get_db),
           x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID")):
    """本人信息：含加入企业列表与当前企业角色。"""
    rels = db.query(SysTenantUser, SysTenant).join(
        SysTenant, SysTenant.id == SysTenantUser.tenant_id
    ).filter(SysTenantUser.user_id == user.id, SysTenantUser.status == "active").all()
    joined = [{"tenant_id": t.id, "tenant_name": t.name, "role": r.role} for r, t in rels]
    role = None
    if x_tenant_id:
        if user.is_super_admin:
            role = "super"
        else:
            rel = db.query(SysTenantUser).filter(
                SysTenantUser.user_id == user.id,
                SysTenantUser.tenant_id == int(x_tenant_id)).first()
            role = rel.role if rel else None
    prof = db.query(SysUserProfile).filter(SysUserProfile.user_id == user.id).first()
    profile = {
        "nickname": (prof.nickname if prof and prof.nickname else ""),
        "email": (prof.email if prof and prof.email else ""),
        "occupation": (prof.occupation if prof and prof.occupation else ""),
        "bio": (prof.bio if prof and prof.bio else ""),
        "age": (prof.age if prof and prof.age is not None else None),
        "gender": (prof.gender if prof and prof.gender else ""),
    }
    return {"code": 200, "data": {
        "id": user.id, "phone": user.phone,
        "display_name": user.display_name or "",
        "role": role, "is_super_admin": bool(user.is_super_admin),
        "joined_tenants": joined, **profile}}


@router.put("/profile")
def update_profile(payload: Dict[str, Any], user: SysUser = Depends(get_current_sys_user),
                   db: Session = Depends(get_db)):
    """修改本人资料：display_name/phone 写 sys_user，其余白名单写 sys_user_profile。"""
    name = str(payload.get("display_name") or payload.get("name") or "").strip()
    phone = str(payload.get("phone") or "").strip()
    if name:
        user.display_name = name[:50]
    if phone and phone != user.phone:
        import re as _re
        if not _re.match(r"^1[3-9]\d{9}$", phone):
            raise HTTPException(status_code=400, detail="手机号格式不正确")
        if db.query(SysUser).filter(SysUser.phone == phone).first():
            raise HTTPException(status_code=400, detail="该手机号已被占用")
        user.phone = phone
    prof = db.query(SysUserProfile).filter(SysUserProfile.user_id == user.id).first()
    if prof is None:
        prof = SysUserProfile(user_id=user.id)
        db.add(prof)
    if "nickname" in payload:
        prof.nickname = (str(payload.get("nickname") or "").strip() or None)
    if "email" in payload:
        email = str(payload.get("email") or "").strip()
        prof.email = (email[:100] if email else None)
    if "occupation" in payload:
        prof.occupation = (str(payload.get("occupation") or "").strip() or None)
    if "bio" in payload:
        prof.bio = (str(payload.get("bio") or "").strip() or None)
    if "age" in payload:
        raw_age = payload.get("age")
        if raw_age in (None, ""):
            prof.age = None
        else:
            try:
                prof.age = int(raw_age)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="年龄必须为整数")
    if "gender" in payload:
        gender = str(payload.get("gender") or "").strip()
        if gender and gender not in ("male", "female", "secret"):
            raise HTTPException(status_code=400, detail="性别仅支持 male/female/secret")
        prof.gender = (gender or None)
    db.commit()
    db.refresh(prof)
    return {"code": 200, "message": "个人资料已更新",
            "data": {"id": user.id, "phone": user.phone,
                      "display_name": user.display_name or "",
                      "nickname": prof.nickname or "",
                      "email": prof.email or "",
                      "occupation": prof.occupation or "",
                      "bio": prof.bio or "",
                      "age": prof.age,
                      "gender": prof.gender or ""}}


@router.post("/login")
def login(payload: Dict[str, Any], db: Session = Depends(get_db),
          x_client: Optional[str] = Header(default=None, alias="X-Client")):
    """全端统一手机号登录，返回默认租户与加入列表。

    权限隔离：当请求方声明为 B 端（X-Client: admin）时，纯学员身份（未在任一租户持有
    owner/admin 角色且非 super_admin）一律 403 拒绝，确保 member 只能从 C 端参加测评。
    C 端不携带该标识，登录链路行为完全不变。
    """
    phone = str(payload.get("phone") or "").strip()
    password = str(payload.get("password") or "")
    if not phone or not password:
        raise HTTPException(status_code=400, detail="请输入手机号与密码")
    user = db.query(SysUser).filter(SysUser.phone == phone).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="手机号或密码错误")
    if not user.status:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    rels = db.query(SysTenantUser, SysTenant).join(
        SysTenant, SysTenant.id == SysTenantUser.tenant_id
    ).filter(SysTenantUser.user_id == user.id, SysTenantUser.status == "active").all()
    joined = [{"tenant_id": t.id, "tenant_name": t.name, "role": r.role} for r, t in rels]
    # B 端登录拦截：仅对声明为 B 端的请求校验；任一租户持有 owner/admin 即视为管理人员放行
    if x_client == "admin" and not user.is_super_admin:
        roles = {j["role"] for j in joined}
        if not ({"owner", "admin"} & roles):
            raise HTTPException(
                status_code=403,
                detail="当前账号为学员身份，请前往学员端 (C端) 参加测评",
            )
    default_tenant = joined[0]["tenant_id"] if joined else None
    token = create_access_token(
        subject=user.id, user_type="sys",
        extra={"is_super_admin": bool(user.is_super_admin),
               "default_tenant_id": default_tenant},
    )
    return {"code": 200, "message": "登录成功", "data": {
        "token": token,
        "user": {"id": user.id, "phone": user.phone,
                 "display_name": user.display_name or "",
                 "is_super_admin": bool(user.is_super_admin)},
        "default_tenant_id": default_tenant,
        "joined_tenants": joined,
    }}

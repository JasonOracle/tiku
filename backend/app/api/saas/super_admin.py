"""
[变更日志]
修改时间：2026-09-10
AI模型：OpenCode / Gemini 底层
修改内容：[新增超管专属接口 GET /tenants/{tenant_id}/members：支持视察特定企业成员，租户严格隔离，所有者置顶]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[新建上帝视图：租户大盘管理，仅超管可访问；新增空库一次性引导]
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict
from app.core.database import get_db
from app.core.security import get_password_hash
from app.api.deps import require_super_admin
from app.models.saas import SysTenant, SysUser, SysTenantUser, SysUserProfile

router = APIRouter()


@router.post("/bootstrap", status_code=201)
def bootstrap_god(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """空库一次性引导：全库无用户时创建首个超级管理员（此后永久自锁）。"""
    if db.query(SysUser).count() > 0:
        raise HTTPException(status_code=403, detail="系统已初始化，引导通道已关闭")
    phone = str(payload.get("phone") or "").strip()
    password = str(payload.get("password") or "")
    import re as _re
    if not _re.match(r"^1[3-9]\d{9}$", phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    god = SysUser(phone=phone, username=phone, password_hash=get_password_hash(password),
                  display_name="超级管理员", is_super_admin=True)
    db.add(god)
    db.commit()
    return {"code": 201, "message": "超级管理员创建成功", "data": {"user_id": god.id}}


@router.get("/tenants")
def list_tenants(_: SysUser = Depends(require_super_admin), db: Session = Depends(get_db)):
    tenants = db.query(SysTenant).order_by(SysTenant.id.desc()).all()
    return {"code": 200, "data": {"items": [
        {"tenant_id": t.id, "tenant_name": t.name, "status": t.status,
         "short_name": t.short_name, "industry": t.industry, "scale": t.scale,
         "contact_name": t.contact_name, "contact_phone": t.contact_phone,
         "remark": t.remark} for t in tenants]}}


@router.post("/tenants")
def create_tenant(payload: dict, _: SysUser = Depends(require_super_admin), db: Session = Depends(get_db)):
    name = str(payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="企业名称必填")
    t = SysTenant(name=name, status="active")
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"code": 201, "message": "企业创建成功", "data": {"tenant_id": t.id}}


@router.post("/tenants/{tenant_id}/disable")
def disable_tenant(tenant_id: int, _: SysUser = Depends(require_super_admin), db: Session = Depends(get_db)):
    t = db.query(SysTenant).filter(SysTenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="企业不存在")
    t.status = "disabled"
    db.commit()
    return {"code": 200, "message": "企业已封禁"}


@router.put("/tenants/{tenant_id}")
def update_tenant(tenant_id: int, payload: dict, _: SysUser = Depends(require_super_admin),
                  db: Session = Depends(get_db)):
    t = db.query(SysTenant).filter(SysTenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="企业不存在")
    if "name" in payload:
        name = str(payload["name"] or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="企业名称不能为空")
        t.name = name
    if "short_name" in payload:
        t.short_name = str(payload["short_name"] or "").strip() or None
    if "industry" in payload:
        t.industry = str(payload["industry"] or "").strip() or None
    if "scale" in payload:
        if payload["scale"] not in ("初创", "中小", "中型", "大型", "集团", None):
            raise HTTPException(status_code=400, detail="scale 字段值非法")
        t.scale = payload["scale"] or None
    if "contact_name" in payload:
        t.contact_name = str(payload["contact_name"] or "").strip() or None
    if "contact_phone" in payload:
        t.contact_phone = str(payload["contact_phone"] or "").strip() or None
    if "remark" in payload:
        t.remark = str(payload["remark"] or "").strip()[:255] or None
    if "status" in payload:
        if payload["status"] not in ("active", "disabled"):
            raise HTTPException(status_code=400, detail="status 必须为 active 或 disabled")
        t.status = payload["status"]
    db.commit()
    db.refresh(t)
    return {"code": 200, "message": "企业已更新", "data": {
        "tenant_id": t.id, "tenant_name": t.name, "status": t.status,
        "short_name": t.short_name, "industry": t.industry, "scale": t.scale,
        "contact_name": t.contact_name, "contact_phone": t.contact_phone,
        "remark": t.remark}}


@router.get("/tenants/{tenant_id}/members")
def list_tenant_members(tenant_id: int, page: int = 1, size: int = 50, keyword: str = "",
                        _: SysUser = Depends(require_super_admin), db: Session = Depends(get_db)):
    """超管上帝视角：视察指定租户下的所有组织成员（带租户严格隔离，不污染全局上下文）。"""
    t = db.query(SysTenant).filter(SysTenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="企业不存在")
    q = db.query(SysTenantUser, SysUser).join(SysUser, SysUser.id == SysTenantUser.user_id).filter(
        SysTenantUser.tenant_id == tenant_id
    )
    if keyword.strip():
        kw = f"%{keyword.strip()}%"
        q = q.filter((SysUser.phone.like(kw)) | (SysUser.display_name.like(kw)))
    # 所有者优先展示
    q = q.order_by(
        (SysTenantUser.role == "owner").desc(),
        (SysTenantUser.role == "admin").desc(),
        SysTenantUser.id.desc()
    )
    total = q.count()
    rows = q.offset((page - 1) * size).limit(size).all()
    items = []
    for rel, u in rows:
        profile = db.query(SysUserProfile).filter(SysUserProfile.user_id == u.id).first()
        items.append({
            "user_id": u.id,
            "phone": u.phone,
            "display_name": u.display_name or u.username or "—",
            "nickname": profile.nickname if profile else None,
            "email": profile.email if profile else None,
            "role": rel.role,
            "status": rel.status,
            "created_at": rel.created_at.strftime("%Y-%m-%d %H:%M:%S") if rel.created_at else ""
        })
    return {"code": 200, "data": {
        "tenant_id": t.id,
        "tenant_name": t.name,
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }}


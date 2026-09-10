"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[上帝无租户头时返回明确 403 指引（请先选择视察企业）；非法租户头 400]
"""
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import decode_token
from app.models.saas import SysUser, SysTenantUser

security_bearer = HTTPBearer(auto_error=False)


def _payload(credentials: Optional[HTTPAuthorizationCredentials]) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录")
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "sys":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的凭证或登录已过期")
    return payload


def get_current_sys_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> SysUser:
    payload = _payload(credentials)
    u = db.query(SysUser).filter(SysUser.id == int(payload.get("sub"))).first()
    if not u or not u.status:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被禁用")
    return u


def get_current_tenant(
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> int:
    """租户上下文透传：除登录外所有业务接口必须携带 X-Tenant-ID。"""
    payload = _payload(credentials)
    if not x_tenant_id:
        if payload.get("is_super_admin") is True:
            raise HTTPException(status_code=403, detail="请先选择视察企业")
        raise HTTPException(status_code=400, detail="缺少 X-Tenant-ID")
    try:
        tid = int(x_tenant_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="非法租户标识")
    if payload.get("is_super_admin") is True:
        # 上帝视察模式：不查归属表，但必须显式携带租户头，复用同一套过滤逻辑
        return tid
    rel = db.query(SysTenantUser).filter(
        SysTenantUser.user_id == int(payload.get("sub")),
        SysTenantUser.tenant_id == tid,
        SysTenantUser.status == "active",
    ).first()
    if not rel:
        raise HTTPException(status_code=403, detail="无该企业访问权限")
    return tid


def require_tenant_role(*allowed: str):
    def _check(
        tenant_id: int = Depends(get_current_tenant),
        user: SysUser = Depends(get_current_sys_user),
        db: Session = Depends(get_db),
    ):
        if user.is_super_admin:
            return {"user": user, "tenant_id": tenant_id, "role": "super"}
        rel = db.query(SysTenantUser).filter(
            SysTenantUser.user_id == user.id,
            SysTenantUser.tenant_id == tenant_id,
            SysTenantUser.status == "active",
        ).first()
        if not rel or rel.role not in allowed:
            raise HTTPException(status_code=403, detail="角色权限不足")
        return {"user": user, "tenant_id": tenant_id, "role": rel.role}
    return _check


require_member = require_tenant_role("owner", "admin", "member")
require_admin = require_tenant_role("owner", "admin")


def require_super_admin(user: SysUser = Depends(get_current_sys_user)) -> SysUser:
    if not user.is_super_admin:
        raise HTTPException(status_code=403, detail="仅超级管理员可访问")
    return user

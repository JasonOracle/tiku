# -*- coding: utf-8 -*-
"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[彻底清洗：种子脚本改种多租户底座，企业101+上帝+管理员+成员]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models import SysTenant, SysUser, SysTenantUser  # noqa: F401
from app.core.security import get_password_hash

PASSWORD = "123456"


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(SysTenant).filter(SysTenant.id == 101).first():
            db.add(SysTenant(id=101, name="演示企业", status="active"))
        seeds = [
            (1, "10000000000", "god", "上帝管理员", True, None),
            (2, "13800138000", "demo_admin", "演示企业管理员", False, "admin"),
            (3, "13900139000", "demo_member", "演示成员", False, "member"),
        ]
        for uid, phone, username, name, super_, role in seeds:
            u = db.query(SysUser).filter(SysUser.id == uid).first()
            if not u:
                db.add(SysUser(id=uid, phone=phone, username=username,
                               password_hash=get_password_hash(PASSWORD),
                               display_name=name, is_super_admin=super_))
                db.flush()
            if role and not db.query(SysTenantUser).filter(
                    SysTenantUser.tenant_id == 101, SysTenantUser.user_id == uid).first():
                db.add(SysTenantUser(tenant_id=101, user_id=uid, role=role, status="active"))
        db.commit()
        print("seed ok: tenant=101 god=10000000000 admin=13800138000 member=13900139000 / 123456")
    finally:
        db.close()


if __name__ == "__main__":
    main()

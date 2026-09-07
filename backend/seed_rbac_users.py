# -*- coding: utf-8 -*-
"""
[变更日志]
修改时间: 2026-09-07
AI模型: Muse Spark
修改内容: [v1.2 Step1.2 新建: 多级 RBAC 6 账号种子脚本 (超管/管理员A/B/出题人A1A2B1B2), 统一密码 123456]
"""
"""v1.2 Step 1.2 数据种子: 创建 6 个层级测试账号 (幂等可重跑).

账号清单 (统一密码 123456):
  1. admin@tiku.io            超管 super_admin, 额度 99999999
  2. manager.zhang@tiku.io    管理员A admin (上级=超管), 额度 1000
     - creator.chen@tiku.io   出题人A1 creator (上级=管理员A), 额度 100
     - creator.lin@tiku.io    出题人A2 creator (上级=管理员A), 额度 100
  3. manager.liu@tiku.io      管理员B admin (上级=超管), 额度 1000
     - creator.wang@tiku.io   出题人B1 creator (上级=管理员B), 额度 100
     - creator.zhao@tiku.io   出题人B2 creator (上级=管理员B), 额度 100

用法:
  cd backend
  python seed_rbac_users.py
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models import Admin  # noqa: F401 (触发模型注册)
from app.core.security import get_password_hash

PASSWORD = "123456"

SEED_PLAN = [
    {"username": "admin@tiku.io", "role": "super_admin", "quota": 99999999, "parent": None},
    {"username": "manager.zhang@tiku.io", "role": "admin", "quota": 1000, "parent": "admin@tiku.io"},
    {"username": "creator.chen@tiku.io", "role": "creator", "quota": 100, "parent": "manager.zhang@tiku.io"},
    {"username": "creator.lin@tiku.io", "role": "creator", "quota": 100, "parent": "manager.zhang@tiku.io"},
    {"username": "manager.liu@tiku.io", "role": "admin", "quota": 1000, "parent": "admin@tiku.io"},
    {"username": "creator.wang@tiku.io", "role": "creator", "quota": 100, "parent": "manager.liu@tiku.io"},
    {"username": "creator.zhao@tiku.io", "role": "creator", "quota": 100, "parent": "manager.liu@tiku.io"},
]


def ensure_columns():
    """MySQL 实库幂等补列 (与 app.main.auto_patch_db_columns 同口径, 种子先跑也能用)."""
    from sqlalchemy import text
    ddls = [
        "ALTER TABLE admins ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'",
        "ALTER TABLE admins ADD COLUMN created_by_id INT NULL",
        "ALTER TABLE admins ADD COLUMN status BOOLEAN DEFAULT TRUE",
        "ALTER TABLE admins ADD COLUMN ai_quota_limit INT DEFAULT 0",
        "ALTER TABLE admins ADD COLUMN daily_ai_quota INT DEFAULT 0",
        "ALTER TABLE admins ADD COLUMN quota_reset_date DATE NULL",
    ]
    try:
        with engine.connect() as conn:
            for ddl in ddls:
                try:
                    conn.execute(text(ddl))
                    conn.commit()
                except Exception:
                    pass
    except Exception:
        pass


def seed():
    ensure_columns()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        id_by_name = {}
        for item in SEED_PLAN:
            admin = db.query(Admin).filter(Admin.username == item["username"]).first()
            parent_id = id_by_name.get(item["parent"])
            if parent_id is None and item["parent"]:
                parent = db.query(Admin).filter(Admin.username == item["parent"]).first()
                parent_id = parent.id if parent else None
            if admin is None:
                admin = Admin(
                    username=item["username"],
                    password_hash=get_password_hash(PASSWORD),
                    role=item["role"],
                    status=True,
                    created_by_id=parent_id,
                    ai_quota_limit=item["quota"],
                    daily_ai_quota=item["quota"],
                    quota_reset_date=datetime.now().date(),
                )
                db.add(admin)
                db.commit()
                db.refresh(admin)
                print(f"[seed] created {admin.username} role={admin.role} quota={item['quota']} parent={item['parent']}")
            else:
                admin.password_hash = get_password_hash(PASSWORD)
                admin.role = item["role"]
                admin.status = True
                admin.created_by_id = parent_id
                admin.ai_quota_limit = item["quota"]
                admin.daily_ai_quota = item["quota"]
                admin.quota_reset_date = datetime.now().date()
                db.commit()
                print(f"[seed] updated {admin.username} role={admin.role} quota={item['quota']} parent={item['parent']}")
            id_by_name[item["username"]] = admin.id
        print("[seed] done: 6 RBAC accounts ready (password 123456).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

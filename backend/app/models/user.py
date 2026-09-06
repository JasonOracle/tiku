# -*- coding: utf-8 -*-
"""
[变更日志]
修改时间: 2026-09-06 17:00:00
AI模型: ZCode (GLM)
修改内容: [v1.2 RBAC 与 AI 额度资产化: Admin 增加 status/ai_quota_limit/daily_ai_quota/quota_reset_date]
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date
from datetime import datetime
from app.core.database import Base

class User(Base):
    """C端注册用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    avatar = Column(String(255), nullable=True, default="", comment="头像URL")
    status = Column(Boolean, default=True, comment="账号状态 (True=正常, False=禁用)")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")

class Admin(Base):
    """B端管理员模型 (super_admin 超管 / admin 老师 / ai AI员工)"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="管理员账号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(String(20), default="admin", comment="角色 (super_admin, admin, ai)")
    status = Column(Boolean, default=True, comment="账号状态 (True=正常, False=禁用)")
    ai_quota_limit = Column(Integer, default=0, comment="每日 AI 额度配置值 (超管分配)")
    daily_ai_quota = Column(Integer, default=0, comment="今日 AI 额度余额 (主动生成型扣减)")
    quota_reset_date = Column(Date, nullable=True, comment="额度所属日期 (跨天自动重置)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

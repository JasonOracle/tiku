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
    """C端注册用户模型
    v1.3 注册资料: nickname/gender/position/phone(唯一)/email; 老数据可空, 展示口径"昵称优先回退用户名"
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), nullable=True, comment="昵称 (注册必填, 展示回退 username)")
    gender = Column(String(10), nullable=True, comment="性别 (male/female, 注册必选)")
    position = Column(String(50), nullable=True, default="", comment="职务 (选填)")
    phone = Column(String(20), nullable=True, unique=True, comment="手机号 (注册必填, 全局唯一)")
    email = Column(String(100), nullable=True, default="", comment="邮箱 (选填)")
    avatar = Column(String(255), nullable=True, default="", comment="头像URL")
    status = Column(Boolean, default=True, comment="账号状态 (True=正常, False=禁用)")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")

class Admin(Base):
    """B端管理员模型 (super_admin 超级管理员 / admin 管理员 / teacher 出题人 / ai AI员工)"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="管理员账号")
    name = Column(String(50), nullable=True, comment="真实姓名/名字")
    phone = Column(String(20), nullable=True, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(String(20), default="teacher", comment="角色 (super_admin, admin, teacher, ai)")
    status = Column(Boolean, default=True, comment="账号状态 (True=正常, False=禁用)")
    ai_quota_limit = Column(Integer, default=0, comment="每日 AI 额度配置值")
    daily_ai_quota = Column(Integer, default=0, comment="今日 AI 额度余额")
    quota_reset_date = Column(Date, nullable=True, comment="额度所属日期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

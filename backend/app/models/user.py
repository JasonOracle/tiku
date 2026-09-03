# -*- coding: utf-8 -*-
"""
[变更日志]
修改时间: 2026-09-03
AI模型: Gemini 底层
修改内容: [1. 修复 SQLAlchemy Column primary_order 属性拼写问题]
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
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
    """B端管理员模型"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="管理员账号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    role = Column(String(20), default="admin", comment="角色 (super_admin, admin)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

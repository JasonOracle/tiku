"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[彻底清洗：仅保留多租户 SaaS 模型，旧 users/admins/exams/questions 等已物理删除]
"""
from app.core.database import Base
from app.models.saas import (
    SysTenant, SysUser, SysUserProfile, SysTenantUser, ResourceCategory, ResourceItem,
    Task, TaskResource, TaskRecord, KbDocument, KbChunk, ResourceFavorite,
    Banner, BannerSetting, Notification, AuditLog, AiSession, AiMessage,
    AiTenantConfig,
)
__all__ = [
    "Base",
    "SysTenant",
    "SysUser",
    "SysUserProfile",
    "SysTenantUser",
    "ResourceCategory",
    "ResourceItem",
    "Task",
    "TaskResource",
    "TaskRecord",
    "KbDocument",
    "KbChunk",
    "ResourceFavorite",
    "Banner",
    "BannerSetting",
    "Notification",
    "AuditLog",
    "AiSession",
    "AiMessage",
    "AiTenantConfig",
]

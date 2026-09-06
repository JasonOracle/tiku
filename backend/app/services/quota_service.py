"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 AI 额度资产化服务: 跨天自动重置 / 余额校验拦截 / 主动创造扣个人额度, 被动业务记系统账单]
"""
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import Admin
from app.models.ai_usage import AiUsageLog


def refresh_daily_quota(admin: Admin) -> Admin:
    """跨天惰性重置: 首次在新的一天调用时, 将余额回满为配置的每日额度 (无需定时任务)"""
    today = date.today()
    if admin.quota_reset_date != today:
        admin.quota_reset_date = today
        admin.daily_ai_quota = admin.ai_quota_limit or 0
    return admin


def ensure_quota(db: Session, admin: Admin) -> int:
    """校验并惰性刷新今日额度余额, 返回当前余额; 不足则 400 拦截"""
    refresh_daily_quota(admin)
    db.commit()
    if (admin.daily_ai_quota or 0) <= 0:
        raise HTTPException(
            status_code=400,
            detail="今日 AI 额度已用尽，请联系超级管理员分配额度"
        )
    return admin.daily_ai_quota


def deduct_quota(db: Session, admin: Admin, action: str, detail: Optional[dict] = None) -> int:
    """扣减一次主动创造型 AI 额度并记录流水 (出题/组卷/聊天)"""
    refresh_daily_quota(admin)
    if (admin.daily_ai_quota or 0) <= 0:
        raise HTTPException(status_code=400, detail="今日 AI 额度已用尽，请联系超级管理员分配额度")
    admin.daily_ai_quota = (admin.daily_ai_quota or 0) - 1
    db.add(AiUsageLog(admin_id=admin.id, action=action, quota_delta=-1, detail=detail or {}))
    db.commit()
    return admin.daily_ai_quota


def log_system_usage(db: Session, action: str, detail: Optional[dict] = None):
    """被动业务型 AI 调用 (如学生交卷触发阅卷): 记录系统账单, 不扣任何老师个人额度"""
    db.add(AiUsageLog(admin_id=None, action=action, quota_delta=0, detail=detail or {}))
    db.commit()

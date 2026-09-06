"""
[变更日志]
修改时间：2026-09-06 19:20:00
AI模型：ZCode (GLM)
修改内容：[v1.3: 新增 GET /me 完整个人资料接口 (昵称/性别/职务/手机号/邮箱), 供个人中心展示]
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.record import ExamRecord, UserFavorite
from app.schemas.auth import UserResponse
from app.schemas.common import ResponseModel

router = APIRouter()

@router.get("/me", response_model=ResponseModel[UserResponse])
def get_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 C 端当前登录用户完整个人资料 (昵称优先展示, 无则回退用户名)"""
    return ResponseModel(code=200, data=current_user)

@router.get("/me/stats", response_model=ResponseModel[dict])
def get_user_me_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 C 端当前登录用户的仪表盘作答统计 (作答场次、通过率、收藏总数)"""
    records = db.query(ExamRecord).filter(
        ExamRecord.user_id == current_user.id,
        ExamRecord.status.in_(["submitted", "timeout"])
    ).all()

    total_exams_taken = len(records)
    passed_count = sum(1 for r in records if r.passed)
    pass_rate = round((passed_count / total_exams_taken) * 100, 1) if total_exams_taken > 0 else 0.0

    favorite_count = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).count()

    return ResponseModel(code=200, data={
        "total_exams_taken": total_exams_taken,
        "passed_count": passed_count,
        "pass_rate": pass_rate,
        "favorite_count": favorite_count,
        "history_count": total_exams_taken
    })

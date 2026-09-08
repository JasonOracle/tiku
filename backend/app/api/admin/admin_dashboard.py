"""
[变更日志]
修改时间：2026-09-08
AI模型：Muse Spark
修改内容：[v1.3 任务4: Dashboard 聚合接口 (KPI/7天趋势/类型环形/热门排行/最近动态/公告/额度), 出题人仅看本人数据]
修改时间：2026-09-08
AI模型：Muse Spark
修改内容：[环形图维度修正: 按试卷分类统计 (与试卷管理分类列一致), 替代题型构成划分]
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin, User
from app.models.exam import Exam
from app.models.record import ExamRecord
from app.models.notification import Notification
from app.models.ai_usage import AiUsageLog
from app.schemas.common import ResponseModel

router = APIRouter()


def _scoped_exam_ids(db: Session, admin: Admin) -> Optional[list]:
    """出题人仅看本人试卷, 超管/管理员全览 (与试卷列表隔离口径一致)"""
    if admin.role == "super_admin":
        return None
    if admin.role == "admin":
        return None
    rows = db.query(Exam.id).filter(Exam.creator_id == admin.id).all()
    return [r[0] for r in rows]


@router.get("/stats", response_model=ResponseModel[dict])
def dashboard_stats(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """首页 Dashboard 聚合: KPI/近7天趋势/试卷分类环形/热门排行/最近动态/系统公告/额度"""
    scope_ids = _scoped_exam_ids(db, admin)
    in_scope = (scope_ids is None)

    def exam_filter(q):
        if not in_scope:
            q = q.filter(Exam.id.in_(scope_ids or [-1]))
        return q

    # ---- KPI ----
    total_exams = exam_filter(db.query(func.count(Exam.id))).scalar() or 0
    rec_q = db.query(ExamRecord).filter(ExamRecord.status == "submitted")
    if not in_scope:
        rec_q = rec_q.filter(ExamRecord.exam_id.in_(scope_ids or [-1]))
    total_records = rec_q.count()
    pending = db.query(ExamRecord).filter(ExamRecord.status == "pending_grading")
    if not in_scope:
        pending = pending.filter(ExamRecord.exam_id.in_(scope_ids or [-1]))
    pending_count = pending.count()
    today = date.today()
    ai_used = db.query(func.count(AiUsageLog.id)).filter(
        AiUsageLog.quota_delta < 0,
        func.date(AiUsageLog.created_at) == today
    ).scalar() or 0

    # ---- 近7天趋势 (提交数 + 平均分) ----
    trend = []
    spark_records = []
    spark_exams = []
    spark_ai = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        q = db.query(ExamRecord).filter(
            ExamRecord.status == "submitted",
            func.date(ExamRecord.submit_time) == day
        )
        if not in_scope:
            q = q.filter(ExamRecord.exam_id.in_(scope_ids or [-1]))
        rows = q.all()
        avg = round(sum(r.score or 0 for r in rows) / len(rows), 1) if rows else 0
        trend.append({"day": day.strftime("%m/%d"), "count": len(rows), "avg": avg})
        spark_records.append(len(rows))
        eq = exam_filter(db.query(func.count(Exam.id))).filter(func.date(Exam.created_at) == day)
        spark_exams.append(eq.scalar() or 0)
        spark_ai.append(db.query(func.count(AiUsageLog.id)).filter(
            AiUsageLog.quota_delta < 0, func.date(AiUsageLog.created_at) == day).scalar() or 0)

    def _pct(cur: int, prev: int) -> str:
        if prev <= 0:
            return "—" if cur <= 0 else "100%"
        return f"{round((cur - prev) * 100.0 / prev, 1)}%"

    # ---- 周环比 (近7天 vs 前7天) ----
    week_ago = today - timedelta(days=7)
    two_ago = today - timedelta(days=14)

    def _range_count(model, dt_col, start, end, exam_scoped: bool = False):
        qq = db.query(func.count(model.id)).filter(dt_col >= start, dt_col < end)
        if exam_scoped and not in_scope:
            qq = qq.filter(ExamRecord.exam_id.in_(scope_ids or [-1]))
        if model is Exam and not in_scope:
            qq = qq.filter(Exam.creator_id == admin.id)
        return qq.scalar() or 0

    cur_rec = _range_count(ExamRecord, ExamRecord.submit_time, week_ago, today + timedelta(days=1), True)
    prev_rec = _range_count(ExamRecord, ExamRecord.submit_time, two_ago, week_ago, True)
    cur_ex = _range_count(Exam, Exam.created_at, week_ago, today + timedelta(days=1))
    prev_ex = _range_count(Exam, Exam.created_at, two_ago, week_ago)
    cur_ai = db.query(func.count(AiUsageLog.id)).filter(
        AiUsageLog.quota_delta < 0, AiUsageLog.created_at >= week_ago).scalar() or 0
    prev_ai = db.query(func.count(AiUsageLog.id)).filter(
        AiUsageLog.quota_delta < 0, AiUsageLog.created_at >= two_ago,
        AiUsageLog.created_at < week_ago).scalar() or 0

    # ---- 试卷分类环形 (按试卷分类统计, 与试卷管理分类列一致) ----
    from app.models.category import ExamCategory
    exams = exam_filter(db.query(Exam)).all()
    cat_names = {c.id: c.name for c in db.query(ExamCategory).all()}
    buckets: dict = {}
    for e in exams:
        name = e.category_name or cat_names.get(e.category_id or -1, "") or "未分类"
        buckets[name] = buckets.get(name, 0) + 1
    donut = [{"name": k, "value": v} for k, v in sorted(buckets.items(), key=lambda x: -x[1])]

    # ---- 热门排行 Top5 (按提交人次) ----
    hot_rows = db.query(
        ExamRecord.exam_id, func.count(ExamRecord.id).label("cnt")
    ).filter(ExamRecord.status == "submitted")
    if not in_scope:
        hot_rows = hot_rows.filter(ExamRecord.exam_id.in_(scope_ids or [-1]))
    hot_rows = hot_rows.group_by(ExamRecord.exam_id).order_by(func.count(ExamRecord.id).desc()).limit(5).all()
    hot = []
    for exam_id, cnt in hot_rows:
        e = db.query(Exam).filter(Exam.id == exam_id).first()
        if e:
            hot.append({"exam_id": exam_id, "title": e.title, "count": cnt})

    # ---- 最近动态 (最新5条已提交) ----
    recent_q = db.query(ExamRecord).filter(ExamRecord.status == "submitted")
    if not in_scope:
        recent_q = recent_q.filter(ExamRecord.exam_id.in_(scope_ids or [-1]))
    recent = []
    for r in recent_q.order_by(ExamRecord.submit_time.desc()).limit(5).all():
        e = db.query(Exam).filter(Exam.id == r.exam_id).first()
        u = db.query(User).filter(User.id == r.user_id).first()
        recent.append({
            "time": r.submit_time.strftime("%Y年%m月%d日 %H:%M") if r.submit_time else "",
            "name": e.title if e else f"试卷#{r.exam_id}",
            "username": (u.nickname or u.username) if u else f"用户#{r.user_id}",
            "score": r.score,
            "status": "已完成"
        })

    # ---- 系统公告 (本人最新4条通知) ----
    notes = db.query(Notification).filter(
        Notification.admin_id == admin.id
    ).order_by(Notification.created_at.desc()).limit(4).all()
    notices = [{
        "text": n.title,
        "date": n.created_at.strftime("%m-%d") if n.created_at else "",
    } for n in notes]

    # ---- 额度 ----
    quota_used = db.query(func.coalesce(func.sum(-AiUsageLog.quota_delta), 0)).filter(
        AiUsageLog.admin_id == admin.id,
        AiUsageLog.quota_delta < 0,
        func.date(AiUsageLog.created_at) == today
    ).scalar() or 0

    return ResponseModel(code=200, data={
        "kpi": {
            "exams": total_exams,
            "records": total_records,
            "ai_usage": ai_used,
            "pending": pending_count
        },
        "deltas": {
            "exams": _pct(cur_ex, prev_ex),
            "records": _pct(cur_rec, prev_rec),
            "ai_usage": _pct(cur_ai, prev_ai)
        },
        "sparks": {
            "exams": spark_exams,
            "records": spark_records,
            "ai": spark_ai
        },
        "trend": trend,
        "donut": donut,
        "hot": hot,
        "recent": recent,
        "notices": notices,
        "quota": {
            "used_today": int(quota_used),
            "remaining": admin.daily_ai_quota if admin.role != "super_admin" else 99999999,
            "limit": admin.ai_quota_limit if admin.role != "super_admin" else 99999999
        }
    })

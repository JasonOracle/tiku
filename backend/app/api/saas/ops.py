"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[新建运营底座：数据看板聚合/横幅/上传/通知/审计，全部租户隔离]
"""
import os
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
from app.core.database import get_db
from app.api.deps import require_admin, require_member
from app.models.saas import (
    SysUser, SysTenantUser, ResourceCategory, ResourceItem, Task, TaskResource,
    TaskRecord, Banner, BannerSetting, Notification, AuditLog,
)

admin_router = APIRouter()
member_router = APIRouter()


# ---------- 审计/通知写 helper（供业务路由调用） ----------

def write_audit(db: Session, tenant_id: int, actor: Optional[SysUser],
                action: str, target_type: str = "", target_id: Optional[int] = None,
                summary: str = ""):
    try:
        db.add(AuditLog(tenant_id=tenant_id, actor_id=actor.id if actor else None,
                        actor_name=(actor.display_name or actor.phone) if actor else "系统",
                        operator_type=("admin" if actor and not actor.is_super_admin else
                                       ("super" if actor else "system")),
                        action=action, target_type=target_type, target_id=target_id,
                        summary=summary[:255]))
        db.flush()
    except Exception:
        pass


def notify(db: Session, tenant_id: int, user_id: int, title: str, content: str = "",
           notif_type: str = "system", link: str = ""):
    try:
        db.add(Notification(tenant_id=tenant_id, user_id=user_id, title=title,
                            content=content, notif_type=notif_type, link=link))
        db.flush()
    except Exception:
        pass


def notify_admins(db: Session, tenant_id: int, title: str, content: str = "",
                  notif_type: str = "system", link: str = ""):
    rels = db.query(SysTenantUser).filter(
        SysTenantUser.tenant_id == tenant_id,
        SysTenantUser.role.in_(["owner", "admin"]),
        SysTenantUser.status == "active").all()
    for r in rels:
        notify(db, tenant_id, r.user_id, title, content, notif_type, link)


# ---------- 数据看板 ----------

@admin_router.get("/dashboard/stats")
def dashboard_stats(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    tid = ctx["tenant_id"]
    tasks = db.query(Task).filter(Task.tenant_id == tid).all()
    recs = db.query(TaskRecord).filter(TaskRecord.tenant_id == tid).all()
    members = db.query(SysTenantUser).filter(SysTenantUser.tenant_id == tid,
                                              SysTenantUser.status == "active").count()
    resources = db.query(ResourceItem).filter(ResourceItem.tenant_id == tid,
                                               ResourceItem.is_deleted == False).count()  # noqa
    today = datetime.now().date()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    per_day = {d.isoformat(): {"count": 0, "scores": []} for d in days}
    ai_total = 0
    ai_today = 0
    pending = 0
    for r in recs:
        if r.status == "pending_verification":
            pending += 1
        if isinstance(r.ai_result, dict) and r.ai_result:
            ai_total += 1
            ts = r.submit_time or r.created_at
            if ts and ts.date() == today:
                ai_today += 1
        ts = r.submit_time or r.created_at
        if ts:
            key = ts.date().isoformat()
            if key in per_day:
                per_day[key]["count"] += 1
                if r.score is not None:
                    per_day[key]["scores"].append(r.score)
    trend = [{"day": d.isoformat()[5:], "count": per_day[d.isoformat()]["count"],
              "avg": round(sum(per_day[d.isoformat()]["scores"]) / len(per_day[d.isoformat()]["scores"]))
              if per_day[d.isoformat()]["scores"] else 0} for d in days]
    sparks_tasks = [0] * 7  # 任务创建时间未建模，按周均摊展示
    if tasks:
        sparks_tasks[-1] = len(tasks)
    sparks = {"exams": sparks_tasks,
              "records": [per_day[d.isoformat()]["count"] for d in days],
              "ai": [ai_today if d == today else 0 for d in days]}
    by_cat: Dict[str, int] = defaultdict(int)
    cats = {c.id: c.name for c in db.query(ResourceCategory).filter(
        ResourceCategory.tenant_id == tid).all()}
    for t in tasks:
        by_cat[cats.get(t.category_id or -1, "未分类")] += 1
    donut = [{"name": k, "value": v} for k, v in sorted(by_cat.items(), key=lambda x: -x[1])] or \
        [{"name": "暂无任务", "value": 0}]
    counts: Dict[int, int] = defaultdict(int)
    for r in recs:
        counts[r.task_id] += 1
    titles = {t.id: t.title for t in tasks}
    hot = [{"exam_id": tid_, "task_id": tid_, "title": titles.get(tid_, f"任务#{tid_}"),
            "count": c} for tid_, c in sorted(counts.items(), key=lambda x: -x[1])[:5]]
    users = {u.id: (u.display_name or u.phone) for u in db.query(SysUser).filter(
        SysUser.id.in_([r.user_id for r in recs]) if recs else False).all()}
    recent = [{"time": (r.submit_time or r.created_at or datetime.now()).strftime("%m-%d %H:%M"),
               "name": users.get(r.user_id, f"成员#{r.user_id}"),
               "username": users.get(r.user_id, ""),
               "score": r.score or 0, "status": r.status} for r in sorted(
        recs, key=lambda x: x.id, reverse=True)[:8]]
    notices = []
    if pending:
        notices.append({"text": f"当前有 {pending} 份任务提交等待核验", "date": "今天"})
    if tasks:
        notices.append({"text": f"企业累计创建 {len(tasks)} 个任务、{resources} 条资源",
                        "date": "累计"})
    return {"code": 200, "data": {
        "kpi": {"exams": len(tasks), "records": len(recs), "ai_usage": ai_total,
                "pending": pending, "members": members, "resources": resources},
        "deltas": {"exams": "—", "records": "—", "ai_usage": "—"},
        "sparks": sparks, "trend": trend, "donut": donut, "hot": hot,
        "recent": recent, "notices": notices,
        "quota": {"used_today": ai_today, "remaining": ai_total, "limit": 0}}}


# ---------- 横幅 ----------

def _banner_out(b: Banner) -> Dict[str, Any]:
    return {"id": b.id, "image_url": b.image_url, "link_type": b.link_type,
            "link_value": b.link_value or "", "sort_order": b.sort_order or 0,
            "is_enabled": bool(b.is_enabled)}


@admin_router.get("/banners")
def list_banners(ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(Banner).filter(Banner.tenant_id == ctx["tenant_id"]).order_by(
        Banner.sort_order, Banner.id).all()
    return {"code": 200, "data": [_banner_out(b) for b in rows]}


@admin_router.post("/banners", status_code=201)
def create_banner(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                  db: Session = Depends(get_db)):
    if not str(payload.get("image_url") or "").strip():
        raise HTTPException(status_code=400, detail="请先上传图片")
    b = Banner(tenant_id=ctx["tenant_id"], image_url=payload["image_url"].strip(),
               link_type=payload.get("link_type") or "none",
               link_value=payload.get("link_value") or "",
               sort_order=int(payload.get("sort_order") or 0),
               is_enabled=bool(payload.get("is_enabled", True)))
    db.add(b)
    db.commit()
    db.refresh(b)
    write_audit(db, ctx["tenant_id"], ctx["user"], "create", "banner", b.id,
                f"新增横幅 #{b.id}")
    db.commit()
    return {"code": 201, "message": "已创建", "data": _banner_out(b)}


@admin_router.get("/banners/settings")
def get_banner_settings(ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    s = db.query(BannerSetting).filter(BannerSetting.tenant_id == ctx["tenant_id"]).first()
    return {"code": 200, "data": {"interval_seconds": s.interval_seconds if s else 4}}


@admin_router.put("/banners/settings")
def put_banner_settings(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                        db: Session = Depends(get_db)):
    v = int(payload.get("interval_seconds") or 4)
    v = max(2, min(v, 10))
    s = db.query(BannerSetting).filter(BannerSetting.tenant_id == ctx["tenant_id"]).first()
    if not s:
        s = BannerSetting(tenant_id=ctx["tenant_id"], interval_seconds=v)
        db.add(s)
    else:
        s.interval_seconds = v
    db.commit()
    return {"code": 200, "message": "已保存", "data": {"interval_seconds": v}}


@admin_router.put("/banners/{bid}")
def update_banner(bid: int, payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                  db: Session = Depends(get_db)):
    b = db.query(Banner).filter(Banner.id == bid, Banner.tenant_id == ctx["tenant_id"]).first()
    if not b:
        raise HTTPException(status_code=404, detail="横幅不存在")
    for k in ("image_url", "link_type", "link_value", "sort_order", "is_enabled"):
        if k in payload and payload[k] is not None:
            setattr(b, k, payload[k])
    db.commit()
    return {"code": 200, "message": "已保存", "data": _banner_out(b)}


@admin_router.delete("/banners/{bid}")
def delete_banner(bid: int, ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    b = db.query(Banner).filter(Banner.id == bid, Banner.tenant_id == ctx["tenant_id"]).first()
    if not b:
        raise HTTPException(status_code=404, detail="横幅不存在")
    db.delete(b)
    db.commit()
    return {"code": 200, "message": "已删除"}


@member_router.get("/banners")
def member_banners(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    rows = db.query(Banner).filter(Banner.tenant_id == ctx["tenant_id"],
                                   Banner.is_enabled == True).order_by(  # noqa
        Banner.sort_order, Banner.id).all()
    s = db.query(BannerSetting).filter(BannerSetting.tenant_id == ctx["tenant_id"]).first()
    return {"code": 200, "data": {"items": [_banner_out(b) for b in rows],
                                  "interval_seconds": s.interval_seconds if s else 4}}


# ---------- 上传 ----------

@admin_router.post("/upload", status_code=201)
def upload_file(file: UploadFile = File(...), ctx: dict = Depends(require_admin)):
    data = file.file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件超过 10MB 上限")
    ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "bin"
    if ext not in ("png", "jpg", "jpeg", "gif", "webp", "pdf", "txt", "md", "xlsx"):
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    name = f"{uuid.uuid4().hex}.{ext}"
    updir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
    os.makedirs(updir, exist_ok=True)
    with open(os.path.join(updir, name), "wb") as f:
        f.write(data)
    return {"code": 201, "message": "上传成功", "data": {"url": f"/uploads/{name}"}}


# ---------- 通知 ----------

@admin_router.get("/notifications")
def list_notifications(ctx: dict = Depends(require_member), db: Session = Depends(get_db),
                       unread_only: bool = False, page: int = 1, size: int = 15):
    q = db.query(Notification).filter(Notification.tenant_id == ctx["tenant_id"],
                                      Notification.user_id == ctx["user"].id)
    if unread_only:
        q = q.filter(Notification.is_read == False)  # noqa
    total = q.count()
    rows = q.order_by(Notification.id.desc()).offset((page - 1) * size).limit(size).all()
    return {"code": 200, "data": {"total": total, "page": page, "size": size, "items": [
        {"id": n.id, "title": n.title, "content": n.content or "",
         "notif_type": n.notif_type, "link": n.link or "", "is_read": bool(n.is_read),
         "created_at": n.created_at.strftime("%Y-%m-%d %H:%M") if n.created_at else ""}
        for n in rows]}}


@admin_router.get("/notifications/unread-count")
def unread_count(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.tenant_id == ctx["tenant_id"],
                                      Notification.user_id == ctx["user"].id,
                                      Notification.is_read == False).count()  # noqa
    return {"code": 200, "data": {"count": n}}


@admin_router.post("/notifications/read")
def mark_read(payload: Dict[str, Any], ctx: dict = Depends(require_member),
              db: Session = Depends(get_db)):
    ids = payload.get("ids")
    q = db.query(Notification).filter(Notification.tenant_id == ctx["tenant_id"],
                                      Notification.user_id == ctx["user"].id,
                                      Notification.is_read == False)  # noqa
    if ids:
        q = q.filter(Notification.id.in_([int(i) for i in ids]))
    q.update({"is_read": True})
    db.commit()
    return {"code": 200, "message": "已标记为已读"}


# ---------- 审计 ----------

@admin_router.get("/audit")
def list_audit(ctx: dict = Depends(require_admin), db: Session = Depends(get_db),
               operator_type: str = "", target_type: str = "", keyword: str = "",
               page: int = 1, size: int = 20):
    q = db.query(AuditLog).filter(AuditLog.tenant_id == ctx["tenant_id"])
    if operator_type:
        q = q.filter(AuditLog.operator_type == operator_type)
    if target_type:
        q = q.filter(AuditLog.target_type == target_type)
    if keyword:
        q = q.filter(AuditLog.summary.like(f"%{keyword}%"))
    total = q.count()
    rows = q.order_by(AuditLog.id.desc()).offset((page - 1) * size).limit(size).all()
    return {"code": 200, "data": {"total": total, "page": page, "size": size, "items": [
        {"id": a.id, "actor_name": a.actor_name, "operator_type": a.operator_type,
         "action": a.action, "target_type": a.target_type, "target_id": a.target_id,
         "summary": a.summary,
         "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S") if a.created_at else ""}
        for a in rows]}}

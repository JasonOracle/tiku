"""
[变更日志]
修改时间：2026-09-10
AI模型：OpenCode / Gemini 底层
修改内容：[admin_list_tasks 补充支持 keyword/category_id/status 检索过滤]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[彻底清洗扩展：资源/任务全量CRUD+详情/统计/复制/批量/导入，容忍旧表单字段并映射双写]
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.database import get_db
from app.api.deps import require_admin, require_member
from app.api.saas.ops import write_audit, notify, notify_admins
from app.models.saas import ResourceItem, Task, TaskResource, TaskRecord, SysTenant, SysTenantUser
from app.schemas.saas import SubmitAnswers, VerifyConfirm

router = APIRouter()


def _res_out(r: ResourceItem) -> Dict[str, Any]:
    """新旧双写行结构：content/title、correct_answer/answer 并存。"""
    ans = r.correct_answer or []
    return {"id": r.id, "type": r.type, "title": r.content, "content": r.content,
            "options": r.options or [], "answer": ans, "correct_answer": ans,
            "score": r.score or 10, "category_id": r.category_id, "difficulty": "medium",
            "locked": False, "explanation": "", "grading_points": [], "source": "manual",
            "source_ref": [], "ai_rag_sources": r.ai_rag_sources or [],
            "creator_id": r.creator_id,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""}


def _task_out(t: Task, with_count: bool = False, db: Session = None) -> Dict[str, Any]:
    d = {"id": t.id, "task_id": t.id, "title": t.title, "description": t.description or "",
         "cover_image": t.cover_image or "", "cover_url": t.cover_image or "",
         "category_id": t.category_id, "status": t.status, "is_timed": bool(t.is_timed),
         "time_limit": t.time_limit, "start_time": t.start_time.isoformat() if t.start_time else None,
         "deadline": t.deadline.isoformat() if t.deadline else None,
         "end_time": t.deadline.isoformat() if t.deadline else None,
         "verification_mode": t.verification_mode,
         "grading_mode": "ai_auto" if t.verification_mode == "ai_auto" else "manual",
         "ai_rag_sources": t.ai_rag_sources or [],
         "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else ""}
    if with_count and db is not None:
        d["question_count"] = db.query(TaskResource).filter(TaskResource.task_id == t.id).count()
    return d


# ---- 资源库 ----
@router.get("/resources")
def list_resources(ctx: dict = Depends(require_member), db: Session = Depends(get_db),
                   page: int = 1, size: int = 10, keyword: str = "", type: str = "",
                   category_id: Optional[int] = None):
    tid = ctx["tenant_id"]
    q = db.query(ResourceItem).filter(ResourceItem.tenant_id == tid, ResourceItem.is_deleted == False)  # noqa
    if keyword:
        q = q.filter(ResourceItem.content.like(f"%{keyword}%"))
    if type:
        q = q.filter(ResourceItem.type == type)
    if category_id:
        q = q.filter(ResourceItem.category_id == category_id)
    total = q.count()
    items = q.order_by(ResourceItem.id.desc()).offset((page - 1) * size).limit(size).all()
    return {"code": 200, "data": {"total": total, "page": page, "size": size,
            "total_pages": (total + size - 1) // size if size else 0,
            "items": [_res_out(r) for r in items]}}


@router.post("/resources", status_code=201)
def create_resource(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                    db: Session = Depends(get_db)):
    content = str(payload.get("content") or payload.get("title") or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="条目内容不能为空")
    r = ResourceItem(tenant_id=ctx["tenant_id"], type=str(payload.get("type") or "single_choice"),
                     content=content, options=payload.get("options") or [],
                     correct_answer=payload.get("correct_answer") or payload.get("answer") or [],
                     score=int(payload.get("score") or 10),
                     category_id=payload.get("category_id"),
                     creator_id=ctx["user"].id,
                     ai_rag_sources=payload.get("ai_rag_sources") or [])
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"code": 201, "message": "资源创建成功", "data": _res_out(r)}


@router.post("/resources/batch")
def batch_create(payload: List[Dict[str, Any]], ctx: dict = Depends(require_admin),
                 db: Session = Depends(get_db)):
    ids = []
    for it in payload[:100]:
        content = str(it.get("content") or it.get("title") or "").strip()
        if not content:
            continue
        r = ResourceItem(tenant_id=ctx["tenant_id"], type=str(it.get("type") or "single_choice"),
                         content=content, options=it.get("options") or [],
                         correct_answer=it.get("correct_answer") or it.get("answer") or [],
                         score=int(it.get("score") or 10), category_id=it.get("category_id"),
                         creator_id=ctx["user"].id, ai_rag_sources=it.get("ai_rag_sources") or [])
        db.add(r)
        db.flush()
        ids.append(r.id)
    db.commit()
    return {"code": 201, "message": f"入库成功，共 {len(ids)} 条", "data": {"ids": ids}}


@router.post("/resources/import")
def import_resources(file: UploadFile = File(...), category_id: Optional[int] = None,
                     ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """Excel 批量导入：首列为内容，次列为答案（逗号分隔多选），首行为表头时自动跳过。"""
    try:
        from openpyxl import load_workbook
        import io
        data = file.file.read()
        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel 解析失败：{e}")
    imported, skipped = 0, 0
    start = 0
    if rows and rows[0] and str(rows[0][0]).strip() in ("题干", "内容", "content", "题目", "标题"):
        start = 1
    for row in rows[start:]:
        if not row or not str(row[0] or "").strip():
            skipped += 1
            continue
        ans_raw = str(row[1] or "").strip() if len(row) > 1 else ""
        ans = [a.strip() for a in ans_raw.replace("，", ",").split(",") if a.strip()]
        db.add(ResourceItem(tenant_id=ctx["tenant_id"], type="single_choice",
                            content=str(row[0]).strip(), options=[],
                            correct_answer=ans, score=10, category_id=category_id,
                            creator_id=ctx["user"].id, ai_rag_sources=[]))
        imported += 1
    db.commit()
    return {"code": 200, "message": "导入完成",
            "data": {"imported_count": imported, "skipped_count": skipped}}


@router.post("/resources/{rid}/copy", status_code=201)
def copy_resource(rid: int, ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    src = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                         ResourceItem.tenant_id == ctx["tenant_id"]).first()
    if not src:
        raise HTTPException(status_code=404, detail="资源不存在")
    r = ResourceItem(tenant_id=src.tenant_id, type=src.type, content=src.content,
                     options=src.options, correct_answer=src.correct_answer, score=src.score,
                     category_id=src.category_id, creator_id=ctx["user"].id,
                     ai_rag_sources=src.ai_rag_sources or [])
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"code": 201, "message": "已复制为新条目", "data": _res_out(r)}


@router.put("/resources/{rid}")
def update_resource(rid: int, payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                    db: Session = Depends(get_db)):
    r = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                       ResourceItem.tenant_id == ctx["tenant_id"]).first()
    if not r:
        raise HTTPException(status_code=404, detail="资源不存在")
    if payload.get("content") or payload.get("title"):
        r.content = str(payload.get("content") or payload.get("title"))
    for k in ("type", "options", "score", "category_id", "ai_rag_sources"):
        if k in payload and payload[k] is not None:
            setattr(r, k, payload[k])
    if "correct_answer" in payload or "answer" in payload:
        r.correct_answer = payload.get("correct_answer") or payload.get("answer") or []
    db.commit()
    return {"code": 200, "message": "已修改", "data": _res_out(r)}


@router.delete("/resources/{rid}")
def delete_resource(rid: int, ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    r = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                       ResourceItem.tenant_id == ctx["tenant_id"]).first()
    if not r:
        raise HTTPException(status_code=404, detail="资源不存在")
    r.is_deleted = True  # 软删除防牵连
    db.commit()
    return {"code": 200, "message": "已删除"}


# ---- 任务 ----
def _verification_mode(payload: Dict[str, Any]) -> str:
    if payload.get("verification_mode") in ("manual", "ai_auto"):
        return payload["verification_mode"]
    gm = payload.get("grading_mode")
    if gm == "ai_auto" or payload.get("is_ai_auto_grade") is True:
        return "ai_auto"
    return "manual"


@router.post("/tasks", status_code=201)
def create_task(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                db: Session = Depends(get_db)):
    title = str(payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="任务标题不能为空")
    rids = list(payload.get("resource_ids") or payload.get("question_ids") or [])
    t = Task(tenant_id=ctx["tenant_id"], title=title,
             description=str(payload.get("description") or ""),
             cover_image=str(payload.get("cover_image") or payload.get("cover_url") or ""),
             category_id=payload.get("category_id"),
             is_timed=bool(payload.get("is_timed", False)),
             time_limit=payload.get("time_limit"),
             start_time=payload.get("start_time"),
             deadline=payload.get("deadline") or payload.get("end_time"),
             verification_mode=_verification_mode(payload),
             creator_id=ctx["user"].id,
             status=str(payload.get("status") or "draft"))
    db.add(t)
    db.flush()
    for i, rid in enumerate(rids):
        res = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                             ResourceItem.tenant_id == ctx["tenant_id"]).first()
        if not res:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"资源 {rid} 不存在或不属于当前企业")
        db.add(TaskResource(task_id=t.id, resource_id=rid, score=res.score or 10, sort_order=i))
    db.flush()
    write_audit(db, ctx["tenant_id"], ctx["user"], "create", "task", t.id,
                f"创建任务《{title}》")
    db.commit()
    return {"code": 201, "message": "任务创建成功", "data": {"task_id": t.id, "id": t.id}}


@router.get("/tasks")
def admin_list_tasks(ctx: dict = Depends(require_member), db: Session = Depends(get_db),
                     page: int = 1, size: int = 10, keyword: str = "",
                     category_id: Optional[int] = None, status: str = ""):
    tid = ctx["tenant_id"]
    q = db.query(Task).filter(Task.tenant_id == tid)
    if ctx.get("role") == "member":
        q = q.filter(Task.status == "published")
    elif status.strip():
        q = q.filter(Task.status == status.strip())
    if keyword.strip():
        q = q.filter(Task.title.like(f"%{keyword.strip()}%"))
    if category_id:
        q = q.filter(Task.category_id == category_id)
    q = q.order_by(Task.id.desc())
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    tids = [t.id for t in items]
    pend: Dict[int, int] = {}
    subs: Dict[int, int] = {}
    if tids:
        for r in db.query(TaskRecord).filter(TaskRecord.task_id.in_(tids),
                                              TaskRecord.tenant_id == tid).all():
            subs[r.task_id] = subs.get(r.task_id, 0) + 1
            if r.status == "pending_verification":
                pend[r.task_id] = pend.get(r.task_id, 0) + 1
    out = []
    for t in items:
        d = _task_out(t, True, db)
        d["pending_count"] = pend.get(t.id, 0)
        d["submit_count"] = subs.get(t.id, 0)
        out.append(d)
    return {"code": 200, "data": {"total": total, "page": page, "size": size,
            "total_pages": (total + size - 1) // size if size else 0,
            "items": out}}


@router.get("/tasks/{task_id}")
def task_detail(task_id: int, ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == ctx["tenant_id"]).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    links = db.query(TaskResource, ResourceItem).join(
        ResourceItem, ResourceItem.id == TaskResource.resource_id
    ).filter(TaskResource.task_id == t.id).order_by(TaskResource.sort_order).all()
    out = _task_out(t, True, db)
    qs = [{**_res_out(r), "eq_score": link.score} for link, r in links]
    if ctx.get("role") == "member":
        # 成员视角防泄漏：剥离正确答案（作答入口请走 /member/tasks/{id}/entry）
        for q in qs:
            q.pop("answer", None)
            q.pop("correct_answer", None)
    out["questions"] = qs
    return {"code": 200, "data": out}


@router.get("/tasks/{task_id}/stats")
def task_stats(task_id: int, ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == ctx["tenant_id"]).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    recs = db.query(TaskRecord).filter(TaskRecord.task_id == task_id,
                                        TaskRecord.tenant_id == ctx["tenant_id"]).all()
    return {"code": 200, "data": {
        "submit_count": len([r for r in recs if r.status in ("submitted", "verified", "pending_verification")]),
        "verify_pending": len([r for r in recs if r.status == "pending_verification"]),
        "verified": len([r for r in recs if r.status == "verified"]),
        "total": len(recs)}}


@router.put("/tasks/{task_id}")
def update_task(task_id: int, payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == ctx["tenant_id"]).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    if t.status == "archived":
        raise HTTPException(status_code=400, detail="任务已归档冻结，不可编辑")
    for k, col in (("title", "title"), ("description", "description"), ("category_id", "category_id"),
                   ("is_timed", "is_timed"), ("time_limit", "time_limit")):
        if k in payload and payload[k] is not None:
            setattr(t, col, payload[k])
    if "cover_image" in payload or "cover_url" in payload:
        t.cover_image = str(payload.get("cover_image") or payload.get("cover_url") or "")
    if "start_time" in payload:
        t.start_time = payload["start_time"]
    if "deadline" in payload or "end_time" in payload:
        t.deadline = payload.get("deadline") or payload.get("end_time")
    if any(k in payload for k in ("verification_mode", "grading_mode", "is_ai_auto_grade")):
        t.verification_mode = _verification_mode(payload)
    if "status" in payload and payload["status"] in ("draft", "published", "archived"):
        t.status = payload["status"]
    if "resource_ids" in payload or "question_ids" in payload:
        rids = list(payload.get("resource_ids") or payload.get("question_ids") or [])
        db.query(TaskResource).filter(TaskResource.task_id == t.id).delete()
        for i, rid in enumerate(rids):
            res = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                                 ResourceItem.tenant_id == ctx["tenant_id"]).first()
            if not res:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"资源 {rid} 不存在或不属于当前企业")
            db.add(TaskResource(task_id=t.id, resource_id=rid, score=res.score or 10, sort_order=i))
    db.commit()
    return {"code": 200, "message": "任务已修改", "data": {"task_id": t.id}}


@router.put("/tasks/{task_id}/status")
def task_status(task_id: int, status: str, ctx: dict = Depends(require_admin),
                db: Session = Depends(get_db)):
    if status not in ("draft", "published", "archived"):
        raise HTTPException(status_code=400, detail="状态非法")
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == ctx["tenant_id"]).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    t.status = status
    db.commit()
    return {"code": 200, "message": "状态已更新", "data": {"task_id": t.id, "status": status}}


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == ctx["tenant_id"]).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    n = db.query(TaskRecord).filter(TaskRecord.task_id == task_id).count()
    if n and t.status != "draft":
        raise HTTPException(status_code=400, detail="已有提交的任务仅可归档，不可删除")
    db.query(TaskResource).filter(TaskResource.task_id == task_id).delete()
    db.delete(t)
    db.commit()
    return {"code": 200, "message": "任务已删除"}


# ---- 本人信息（成员端/管理端共用） ----
@router.get("/me")
def my_info(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    u = ctx["user"]
    rels = db.query(SysTenantUser, SysTenant).join(
        SysTenant, SysTenant.id == SysTenantUser.tenant_id
    ).filter(SysTenantUser.user_id == u.id, SysTenantUser.status == "active").all()
    return {"code": 200, "data": {
        "id": u.id, "phone": u.phone, "display_name": u.display_name or "",
        "role": ctx.get("role"), "tenant_id": ctx.get("tenant_id"),
        "joined_tenants": [{"tenant_id": t.id, "tenant_name": t.name, "role": r.role}
                            for r, t in rels]}}


# ---- 成员待办 ----
@router.get("/member-tasks")
def member_tasks(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    tid = ctx["tenant_id"]
    tasks = db.query(Task).filter(Task.tenant_id == tid, Task.status == "published").order_by(Task.id.desc()).all()
    recs = {r.task_id: r for r in db.query(TaskRecord).filter(
        TaskRecord.tenant_id == tid, TaskRecord.user_id == ctx["user"].id).all()}
    return {"code": 200, "data": {"items": [
        {"task_id": t.id, "title": t.title, "status": (recs[t.id].status if t.id in recs else "pending"),
         "category_id": t.category_id,
         "deadline": t.deadline.isoformat() if t.deadline else None} for t in tasks]}}


# ---- 提交（悲观锁 + 服务端权威计时） ----
@router.post("/task-records/submit")
def submit_task(payload: SubmitAnswers, ctx: dict = Depends(require_member),
                db: Session = Depends(get_db)):
    tid = ctx["tenant_id"]
    uid = ctx["user"].id
    now = datetime.now()
    task = db.query(Task).filter(Task.id == payload.task_id, Task.tenant_id == tid).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status != "published":
        raise HTTPException(status_code=400, detail="任务未发布，不可提交")
    if task.deadline and now > task.deadline:
        raise HTTPException(status_code=400, detail="任务已截止，不可提交")
    rec = db.query(TaskRecord).filter(TaskRecord.task_id == task.id,
                                       TaskRecord.user_id == uid).with_for_update().first()
    if rec and rec.status in ("submitted", "verified", "pending_verification"):
        raise HTTPException(status_code=400, detail="不可重复提交")
    # 服务端结算用时：now - 开考时刻（入口行创建时间），客户端上报值仅参考取最小？
    # 防作弊：完全忽略客户端 time_spent；限时任务按上限截断
    started = (rec.created_at if rec and rec.created_at else now)
    server_spent = max(0, int((now - started).total_seconds()))
    if task.is_timed and task.time_limit:
        server_spent = min(server_spent, int(task.time_limit) * 60)
    need_verify = (task.verification_mode == "ai_auto")
    status = "pending_verification" if need_verify else "submitted"
    if not rec:
        rec = TaskRecord(tenant_id=tid, task_id=task.id, user_id=uid, status=status,
                         time_spent=server_spent, answers=payload.answers,
                         created_at=started, submit_time=now)
        db.add(rec)
    else:
        rec.status = status
        rec.time_spent = server_spent
        rec.answers = payload.answers
        rec.submit_time = now
    db.flush()
    write_audit(db, tid, ctx["user"], "submit", "task_record", rec.id or 0,
                f"提交任务 #{task.id}")
    if need_verify:
        notify_admins(db, tid, "新任务提交待核验", f"任务《{task.title}》收到一份新提交",
                      "verification", "/verification")
    db.commit()
    msg = "提交成功，等待管理员或AI核验" if need_verify else "提交成功"
    return {"code": 200, "message": msg, "data": {"status": status,
                                                 "time_spent": server_spent,
                                                 "server_now": now.isoformat()}}


# ---- 核验大厅 ----
@router.get("/verifications/pending")
def pending_list(ctx: dict = Depends(require_admin), db: Session = Depends(get_db),
                 task_id: Optional[int] = None, exam_id: Optional[int] = None):
    tid = ctx["tenant_id"]
    f_task = task_id or exam_id
    q = db.query(TaskRecord).filter(TaskRecord.tenant_id == tid,
                                    TaskRecord.status == "pending_verification")
    if f_task:
        q = q.filter(TaskRecord.task_id == f_task)
    rows = q.order_by(TaskRecord.id.desc()).all()
    return {"code": 200, "data": {"items": [
        {"record_id": r.id, "task_id": r.task_id, "user_id": r.user_id,
         "answers": r.answers, "ai_result": r.ai_result,
         "submit_time": r.submit_time.strftime("%Y-%m-%d %H:%M:%S") if r.submit_time else ""} for r in rows]}}


@router.get("/verifications/{record_id}")
def verify_detail(record_id: int, ctx: dict = Depends(require_admin),
                  db: Session = Depends(get_db)):
    rec = db.query(TaskRecord).filter(TaskRecord.id == record_id,
                                       TaskRecord.tenant_id == ctx["tenant_id"]).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    task = db.query(Task).filter(Task.id == rec.task_id).first()
    items = []
    for a in (rec.answers or []):
        rid = a.get("resource_id") if isinstance(a, dict) else None
        ans = a.get("answer") if isinstance(a, dict) else a
        content = ""
        if rid:
            r = db.query(ResourceItem).filter(ResourceItem.id == rid).first()
            if r:
                content = r.content
        items.append({"resource_id": rid, "content": content, "answer": ans})
    return {"code": 200, "data": {"record_id": rec.id, "task_id": rec.task_id,
            "task_title": task.title if task else "", "user_id": rec.user_id,
            "answers": rec.answers, "items": items, "ai_result": rec.ai_result,
            "score": rec.score, "status": rec.status, "comments": rec.comments or ""}}


@router.post("/verifications/{record_id}/confirm")
def verify_confirm(record_id: int, payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                   db: Session = Depends(get_db)):
    rec = db.query(TaskRecord).filter(TaskRecord.id == record_id,
                                       TaskRecord.tenant_id == ctx["tenant_id"]).with_for_update().first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    scores = payload.get("scores") or {}
    total = None
    if isinstance(scores, dict) and scores:
        try:
            total = sum(int(v) for v in scores.values())
        except Exception:
            total = None
    rec.status = "verified"
    rec.score = payload.get("final_score", total)
    rec.comments = str(payload.get("comments") or "")
    db.flush()
    write_audit(db, ctx["tenant_id"], ctx["user"], "verify", "task_record", rec.id,
                f"核验记录 #{rec.id}（{rec.score} 分）")
    notify(db, ctx["tenant_id"], rec.user_id, "任务已核验",
           f"你的任务提交已核验，得分 {rec.score} 分", "verification", "/my-tasks")
    db.commit()
    return {"code": 200, "message": "核验完成", "data": {"record_id": rec.id, "score": rec.score}}

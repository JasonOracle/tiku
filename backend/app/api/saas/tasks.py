"""
[变更日志]
修改时间：2026-09-11
AI模型：Codex 3
修改内容：[1. _res_out 改读持久化 r.explanation（替代硬编码空串），create/batch/update/copy 资源接口全链路读写 explanation；2. verify_detail 明细 items 补 explanation，供阅卷大厅批阅参考]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. submit_task 接口增加客观题自动评分引擎：单选/多选/判断精确比对 correct_answer 立即出分，填空题宽松文本比对，简答题跳过交核验；2. 总分写入 rec.score 并在返回数据中携带 score 字段]
[变更日志]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. submit_task 提交试卷接口返回数据中直接补齐 record_id，让前端提交后无需轮询二次查询即可精确跳转成绩报告页]
[变更日志]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. member_tasks 接口补充返回 record_id（若学员已有提交记录），便于 C 端列表与我的测试卡片精准携带答卷ID直达报告页]
[变更日志]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. 升级 member_tasks 接口：联合聚合计算输出真实题目数 question_count、总分 total_score、及格分 pass_score，并返回 category_name、is_timed、time_limit、start_time、score、submit_time 等元数据，彻底修复 C 端首页与我的测试列表题目/总分/及格分全为 0 的问题]
[变更日志]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[彻底修复 AI 批量入库后列表来源显示为人工录入的Bug：1. _res_out 动态读取持久化 r.source，并对历史数据通过 ai_rag_sources 智能推断来源；2. create_resource 与 batch_create 完整持久化 payload['source'] 到 resources 表]
[变更日志]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. 升级 create_task 与 update_task 接口：支持接收 questions=[{id, score}] 个性化题目分值设置，实现试卷内原地灵活改分与落库]
[变更日志]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. 强化 task_stats 统计接口：user_records 补充输出 status 字段，支持待批阅状态透传; 2. 统计 pass_rate 与 is_passed 时动态计算试卷及格线，支持区分已终审(verified)与待核验(pending_verification)成员成绩]
[变更日志]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. _task_out 及 admin_list_tasks 支持解析并输出 creator_name(创建人姓名/昵称)，解决试卷管理列表创建人显示为空白短横线问题]
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
from app.models.saas import ResourceItem, Task, TaskResource, TaskRecord, SysTenant, SysTenantUser, SysUser, SysUserProfile, ResourceCategory
from app.schemas.saas import SubmitAnswers, VerifyConfirm

router = APIRouter()


def _res_out(r: ResourceItem) -> Dict[str, Any]:
    """新旧双写行结构：content/title、correct_answer/answer 并存。"""
    ans = r.correct_answer or []
    # 优先使用持久化 source 字段，若空则检测是否有切片溯源智能兜底判断
    src = getattr(r, "source", None) or ("ai" if (r.ai_rag_sources and len(r.ai_rag_sources) > 0) else "manual")
    # explanation 持久化列直读，存量无解析数据输出空串兼容前端占位
    explanation = getattr(r, "explanation", None) or ""
    return {"id": r.id, "type": r.type, "title": r.content, "content": r.content,
            "options": r.options or [], "answer": ans, "correct_answer": ans,
            "score": r.score or 10, "category_id": r.category_id, "difficulty": "medium",
            "locked": False, "explanation": explanation, "grading_points": [], "source": src,
            "source_ref": [], "ai_rag_sources": r.ai_rag_sources or [],
            "creator_id": r.creator_id,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""}


def _task_out(t: Task, with_count: bool = False, db: Session = None, creator_name: str = None) -> Dict[str, Any]:
    d = {"id": t.id, "task_id": t.id, "title": t.title, "description": t.description or "",
         "cover_image": t.cover_image or "", "cover_url": t.cover_image or "",
         "category_id": t.category_id, "status": t.status, "is_timed": bool(t.is_timed),
         "time_limit": t.time_limit, "start_time": t.start_time.isoformat() if t.start_time else None,
         "deadline": t.deadline.isoformat() if t.deadline else None,
         "end_time": t.deadline.isoformat() if t.deadline else None,
         "verification_mode": t.verification_mode,
         "grading_mode": "ai_auto" if t.verification_mode == "ai_auto" else "manual",
         "ai_rag_sources": t.ai_rag_sources or [],
         "creator_id": t.creator_id,
         "creator_name": creator_name or "",
         "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else ""}
    if with_count and db is not None:
        d["question_count"] = db.query(TaskResource).filter(TaskResource.task_id == t.id).count()
    if not d["creator_name"] and t.creator_id and db is not None:
        u = db.query(SysUser).filter(SysUser.id == t.creator_id).first()
        if u:
            p = db.query(SysUserProfile).filter(SysUserProfile.user_id == u.id).first()
            d["creator_name"] = (p.nickname if p and p.nickname else (u.display_name or u.username)) or ""
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
    src = str(payload.get("source") or "manual")
    r = ResourceItem(tenant_id=ctx["tenant_id"], type=str(payload.get("type") or "single_choice"),
                     content=content, options=payload.get("options") or [],
                     correct_answer=payload.get("correct_answer") or payload.get("answer") or [],
                     explanation=(payload.get("explanation") or "").strip() or None,
                     score=int(payload.get("score") or 10),
                     category_id=payload.get("category_id"),
                     source=src,
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
        src = str(it.get("source") or "manual")
        r = ResourceItem(tenant_id=ctx["tenant_id"], type=str(it.get("type") or "single_choice"),
                         content=content, options=it.get("options") or [],
                         correct_answer=it.get("correct_answer") or it.get("answer") or [],
                         explanation=(it.get("explanation") or "").strip() or None,
                         score=int(it.get("score") or 10), category_id=it.get("category_id"),
                         source=src,
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
                     explanation=src.explanation,
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
    for k in ("type", "options", "score", "category_id", "ai_rag_sources", "explanation"):
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
    # 支持接收 [{id: 1, score: 20}] 对象列表，或纯 ID 列表 [1, 2]
    q_items = payload.get("questions")
    if q_items and isinstance(q_items, list) and len(q_items) > 0 and isinstance(q_items[0], dict):
        q_list = [{"id": item.get("id"), "score": item.get("score")} for item in q_items if item.get("id")]
    else:
        rids = list(payload.get("resource_ids") or payload.get("question_ids") or [])
        q_list = [{"id": rid, "score": None} for rid in rids]

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
    for i, q_info in enumerate(q_list):
        rid = q_info["id"]
        res = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                             ResourceItem.tenant_id == ctx["tenant_id"]).first()
        if not res:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"资源 {rid} 不存在或不属于当前企业")
        final_score = q_info["score"] if q_info["score"] is not None else (res.score or 10)
        db.add(TaskResource(task_id=t.id, resource_id=rid, score=final_score, sort_order=i))
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
    # 批量查询试卷创建人，杜绝 N+1 慢查询
    creator_ids = list({t.creator_id for t in items if t.creator_id})
    creator_map: Dict[int, str] = {}
    if creator_ids:
        users = db.query(SysUser).filter(SysUser.id.in_(creator_ids)).all()
        profiles = db.query(SysUserProfile).filter(SysUserProfile.user_id.in_(creator_ids)).all()
        prof_map = {p.user_id: p for p in profiles}
        for u in users:
            p = prof_map.get(u.id)
            creator_map[u.id] = (p.nickname if p and p.nickname else (u.display_name or u.username)) or ""

    out = []
    for t in items:
        c_name = creator_map.get(t.creator_id) if t.creator_id else ""
        d = _task_out(t, True, db, creator_name=c_name)
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


# /**
#  * [变更日志]
#  * 修改时间：2026-09-11
#  * AI模型：Gemini 3.6 Flash
#  * 修改内容：[1. 重构 /tasks/{task_id}/stats 接口，返回包含 total_participants, avg_score, pass_rate 及 user_records 列表的全量分析数据]
#  */
@router.get("/tasks/{task_id}/stats")
def task_stats(task_id: int, ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == ctx["tenant_id"]).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    recs = db.query(TaskRecord).filter(TaskRecord.task_id == task_id,
                                        TaskRecord.tenant_id == ctx["tenant_id"]).all()
    
    # 计算当前试卷总分与及格线（避免写死 60 分导致判定偏差）
    t_resources = db.query(TaskResource).filter(TaskResource.task_id == task_id).all()
    task_total_score = sum(tr.score or 10 for tr in t_resources) if t_resources else 100
    pass_percent = t.pass_percent if hasattr(t, "pass_percent") and t.pass_percent else 60
    pass_score = (task_total_score * pass_percent) / 100.0

    total_participants = len(recs)
    verify_pending_recs = [r for r in recs if r.status == "pending_verification"]
    verified_recs = [r for r in recs if r.status == "verified"]

    scores = [r.score for r in recs if r.score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    passed_count = len([s for s in scores if s >= pass_score])
    pass_rate = round((passed_count / len(scores)) * 100, 1) if scores else 0

    # 查关联用户信息
    user_ids = [r.user_id for r in recs]
    users = db.query(SysUser).filter(SysUser.id.in_(user_ids)).all() if user_ids else []
    profiles = db.query(SysUserProfile).filter(SysUserProfile.user_id.in_(user_ids)).all() if user_ids else []
    
    user_map = {u.id: u for u in users}
    profile_map = {p.user_id: p for p in profiles}

    user_records = []
    for r in recs:
        u = user_map.get(r.user_id)
        p = profile_map.get(r.user_id)
        cur_score = r.score or 0
        user_records.append({
            "record_id": r.id,
            "user_id": r.user_id,
            "username": u.username if u else f"用户#{r.user_id}",
            "nickname": p.nickname if p and p.nickname else (u.display_name if u else None),
            "score": cur_score,
            "status": r.status or "submitted",
            "is_passed": cur_score >= pass_score,
            "time_spent": r.time_spent or 0,
            "submit_time": r.submit_time.strftime("%Y-%m-%d %H:%M:%S") if r.submit_time else (r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "")
        })

    return {"code": 200, "data": {
        "total_participants": total_participants,
        "avg_score": avg_score,
        "pass_rate": pass_rate,
        "pass_score": pass_score,
        "task_total_score": task_total_score,
        "user_records": user_records,
        "submit_count": len([r for r in recs if r.status in ("submitted", "verified", "pending_verification")]),
        "verify_pending": len(verify_pending_recs),
        "verified": len(verified_recs),
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
    if "resource_ids" in payload or "question_ids" in payload or "questions" in payload:
        q_items = payload.get("questions")
        if q_items and isinstance(q_items, list) and len(q_items) > 0 and isinstance(q_items[0], dict):
            q_list = [{"id": item.get("id"), "score": item.get("score")} for item in q_items if item.get("id")]
        else:
            rids = list(payload.get("resource_ids") or payload.get("question_ids") or [])
            q_list = [{"id": rid, "score": None} for rid in rids]

        db.query(TaskResource).filter(TaskResource.task_id == t.id).delete()
        for i, q_info in enumerate(q_list):
            rid = q_info["id"]
            res = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                                 ResourceItem.tenant_id == ctx["tenant_id"]).first()
            if not res:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"资源 {rid} 不存在或不属于当前企业")
            final_score = q_info["score"] if q_info["score"] is not None else (res.score or 10)
            db.add(TaskResource(task_id=t.id, resource_id=rid, score=final_score, sort_order=i))
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
    
    # 批量预加载所有分类与题目关联，避免 N+1 慢查询
    cat_ids = list({t.category_id for t in tasks if t.category_id})
    cat_map: Dict[int, str] = {}
    if cat_ids:
        for c in db.query(ResourceCategory).filter(ResourceCategory.id.in_(cat_ids)).all():
            cat_map[c.id] = c.name

    task_ids = [t.id for t in tasks]
    tr_map: Dict[int, List[int]] = {}
    if task_ids:
        for tr in db.query(TaskResource).filter(TaskResource.task_id.in_(task_ids)).all():
            tr_map.setdefault(tr.task_id, []).append(tr.score if tr.score is not None else 10)

    items = []
    for t in tasks:
        scores = tr_map.get(t.id, [])
        q_count = len(scores)
        t_total = sum(scores) if scores else 100
        p_percent = getattr(t, "pass_percent", None) or 60
        p_score = int(round(t_total * p_percent / 100.0))
        r = recs.get(t.id)

        items.append({
            "task_id": t.id,
            "record_id": r.id if r else None,
            "title": t.title,
            "status": (r.status if r else "pending"),
            "category_id": t.category_id,
            "category_name": cat_map.get(t.category_id) or "",
            "question_count": q_count,
            "total_score": t_total,
            "pass_score": p_score,
            "is_timed": bool(t.is_timed),
            "time_limit": t.time_limit or 0,
            "start_time": t.start_time.isoformat() if t.start_time else None,
            "deadline": t.deadline.isoformat() if t.deadline else None,
            "score": r.score if r else None,
            "submit_time": r.submit_time.strftime("%Y-%m-%d %H:%M:%S") if (r and r.submit_time) else None
        })

    return {"code": 200, "data": {"items": items}}


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

    # ---- 自动评分：客观题（单选/多选/判断/填空）即时比对正确答案，简答题跳过交由核验 ----
    # 预加载本试卷所有题目的正确答案与分值
    links = db.query(TaskResource, ResourceItem).join(
        ResourceItem, ResourceItem.id == TaskResource.resource_id
    ).filter(TaskResource.task_id == task.id).all()
    # 构建 {resource_id: {correct_answer, type, score}} 映射
    answer_map: Dict[int, Dict[str, Any]] = {}
    for link, res in links:
        answer_map[res.id] = {
            "correct_answer": res.correct_answer or [],
            "type": res.type or "",
            "score": link.score if link.score is not None else (res.score or 10)
        }

    total_score = 0
    has_subjective = False  # 是否包含简答等主观题（需人工/AI核验）

    for ans_item in (payload.answers or []):
        if not isinstance(ans_item, dict):
            continue
        rid = ans_item.get("resource_id")
        user_ans = ans_item.get("answer")
        if rid is None or rid not in answer_map:
            continue
        meta = answer_map[rid]
        q_type = meta["type"]
        correct = meta["correct_answer"]
        q_score = meta["score"]

        # 简答题无法自动评分
        if q_type in ("short", "short_answer"):
            has_subjective = True
            continue

        # 客观题评分：用户作答与正确答案精确比对
        if q_type in ("single", "single_choice", "multiple", "multiple_choice", "judge", "true_false"):
            # 规范化为大写排序字符串列表
            def _norm_list(v):
                if isinstance(v, list):
                    return sorted([str(x).strip().upper() for x in v if str(x).strip()])
                if isinstance(v, str) and v.strip():
                    return [v.strip().upper()]
                return []

            user_norm = _norm_list(user_ans)
            correct_norm = _norm_list(correct)

            # 判断题特殊映射：correct_answer 可能存储为 ['正确'/'错误']，前端提交为 ['A'/'B']
            if q_type in ("judge", "true_false"):
                judge_map = {"正确": "A", "对": "A", "TRUE": "A", "YES": "A",
                             "错误": "B", "错": "B", "FALSE": "B", "NO": "B"}
                correct_norm = sorted([judge_map.get(c, c) for c in correct_norm])

            if user_norm == correct_norm:
                total_score += q_score

        # 填空题评分：逐空文本宽松比对（去空格、不区分大小写）
        elif q_type in ("fill", "fill_in"):
            def _norm_fill(v):
                if isinstance(v, list):
                    return [str(x).strip().lower() for x in v]
                if isinstance(v, str):
                    return [v.strip().lower()]
                return []
            u_list = _norm_fill(user_ans)
            c_list = _norm_fill(correct)
            # 填空按空数比对，全部正确才得分
            if u_list and c_list and len(u_list) == len(c_list):
                if all(u == c for u, c in zip(u_list, c_list)):
                    total_score += q_score

    rec.score = total_score

    db.flush()
    write_audit(db, tid, ctx["user"], "submit", "task_record", rec.id or 0,
                f"提交任务 #{task.id}")
    if need_verify:
        notify_admins(db, tid, "新任务提交待核验", f"任务《{task.title}》收到一份新提交",
                      "verification", "/verification")
    db.commit()
    msg = "提交成功，等待管理员或AI核验" if need_verify else "提交成功"
    return {"code": 200, "message": msg, "data": {"record_id": rec.id,
                                                 "status": status,
                                                 "score": total_score,
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

    # 查关联 Task, User, Profile
    t_ids = list(set(r.task_id for r in rows))
    u_ids = list(set(r.user_id for r in rows))

    tasks = db.query(Task).filter(Task.id.in_(t_ids)).all() if t_ids else []
    users = db.query(SysUser).filter(SysUser.id.in_(u_ids)).all() if u_ids else []
    profiles = db.query(SysUserProfile).filter(SysUserProfile.user_id.in_(u_ids)).all() if u_ids else []

    task_map = {t.id: t.title for t in tasks}
    user_map = {u.id: u for u in users}
    profile_map = {p.user_id: p for p in profiles}

    items = []
    for r in rows:
        u = user_map.get(r.user_id)
        p = profile_map.get(r.user_id)
        items.append({
            "record_id": r.id,
            "task_id": r.task_id,
            "task_title": task_map.get(r.task_id, f"试卷#{r.task_id}"),
            "user_id": r.user_id,
            "username": u.username if u else f"用户#{r.user_id}",
            "nickname": p.nickname if p and p.nickname else (u.display_name if u else None),
            "answers": r.answers,
            "ai_result": r.ai_result,
            "submit_time": r.submit_time.strftime("%Y-%m-%d %H:%M:%S") if r.submit_time else (r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "")
        })

    return {"code": 200, "data": {"items": items}}


@router.get("/verifications/{record_id}")
def verify_detail(record_id: int, ctx: dict = Depends(require_admin),
                  db: Session = Depends(get_db)):
    rec = db.query(TaskRecord).filter(TaskRecord.id == record_id,
                                       TaskRecord.tenant_id == ctx["tenant_id"]).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    task = db.query(Task).filter(Task.id == rec.task_id).first()
    user = db.query(SysUser).filter(SysUser.id == rec.user_id).first()
    profile = db.query(SysUserProfile).filter(SysUserProfile.user_id == rec.user_id).first()

    items = []
    for a in (rec.answers or []):
        rid = a.get("resource_id") if isinstance(a, dict) else None
        ans = a.get("answer") if isinstance(a, dict) else a
        content = ""
        q_type = "short"
        correct_ans = None
        q_score = 10
        explanation = ""
        if rid:
            r = db.query(ResourceItem).filter(ResourceItem.id == rid).first()
            if r:
                content = r.content
                q_type = r.type
                correct_ans = r.correct_answer
                q_score = r.score or 10
                explanation = getattr(r, "explanation", None) or ""
        items.append({
            "resource_id": rid,
            "content": content,
            "type": q_type,
            "correct_answer": correct_ans,
            "explanation": explanation,
            "score": q_score,
            "answer": ans
        })

    return {"code": 200, "data": {
        "record_id": rec.id,
        "task_id": rec.task_id,
        "task_title": task.title if task else "",
        "user_id": rec.user_id,
        "username": user.username if user else f"用户#{rec.user_id}",
        "nickname": profile.nickname if profile and profile.nickname else (user.display_name if user else None),
        "answers": rec.answers,
        "items": items,
        "ai_result": rec.ai_result,
        "score": rec.score,
        "status": rec.status,
        "comments": rec.comments or "",
        "submit_time": rec.submit_time.strftime("%Y-%m-%d %H:%M:%S") if rec.submit_time else (rec.created_at.strftime("%Y-%m-%d %H:%M:%S") if rec.created_at else "")
    }}


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

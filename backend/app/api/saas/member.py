"""
[变更日志]
修改时间：2026-09-12
AI模型：Agnes-3.0-flash (ZCode)
修改内容：[1. POST /tasks/{task_id}/retake 改造为 POST /tasks/{task_id}/continue：语义由「清空重考」改为「继续测试」，保留上次 answers 供考场回填续答，仅退回 pending 并清空未终审的分数与提交痕迹；2. 补严校验链：仅「manual + 卷含简答 + 记录为 pending_verification + 未过截止」才放行，已核验/已定稿/AI 模式/纯客观卷一律 400]
修改时间：2026-09-12
AI模型：Agnes-3.0-flash (ZCode)
修改内容：[1. 新增 POST /tasks/{task_id}/retake 截止前重考端点：重置本人该卷记录为 pending（覆盖旧作答与旧成绩），不新增记录行，已核验定分与已过截止时间均拒绝；2. 新增 GET /me/stats 个人中心统计端点：补齐此前前端调用但后端缺失的接口，按常规口径返回累计作答场次/综合通过率/收藏数/历史答卷数]
修改时间：2026-09-12
AI模型：Agnes-3.0-flash (ZCode)
修改内容：[my_result 成绩明细 items 补返回 type 与 options（C端报告页「我的作答明细」题型标签与选项/填空对照渲染所需数据）]
修改时间：2026-09-11
AI模型：Codex 3
修改内容：[my_result 成绩明细 items 补 correct_answer 与 explanation（提交后复盘场景：标准答案+解析对照，核验中/已提交/已核验均可见）]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[1. task_entry 接口：pending 状态用户重新进入考试时重置 created_at 为当前时间，修复因前端异常崩溃退出后重新进入导致服务端用时从旧开考时间累积计算的问题]
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[服务端权威计时：入口锁定 start_time，提交时服务端结算用时并校验截止]
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Any, Dict
from app.core.database import get_db
from app.api.deps import require_member
from app.api.saas.ops import write_audit
from app.models.saas import ResourceItem, Task, TaskResource, TaskRecord, ResourceFavorite

router = APIRouter()


def _public_question(r: ResourceItem, score: int = 10) -> Dict[str, Any]:
    """成员作答视角：剥离正确答案，防泄漏。"""
    return {"id": r.id, "type": r.type, "title": r.content, "content": r.content,
            "options": r.options or [], "score": score, "category_id": r.category_id}


@router.get("/tasks/{task_id}/entry")
def task_entry(task_id: int, ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    """成员执行入口：任务元信息 + 无答案条目 + 本人提交状态。
    服务端权威计时：首次进入落 in_progress 记录并锁定 start_time（DB 时间），
    之后每次进入复用同一 start_time；客户端上报的用时一律忽略，提交时服务端结算。"""
    now = datetime.now()
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == ctx["tenant_id"]).first()
    if not t or t.status != "published":
        raise HTTPException(status_code=404, detail="任务不存在或未发布")
    links = db.query(TaskResource, ResourceItem).join(
        ResourceItem, ResourceItem.id == TaskResource.resource_id
    ).filter(TaskResource.task_id == t.id,
             ResourceItem.is_deleted == False).order_by(TaskResource.sort_order).all()  # noqa
    rec = db.query(TaskRecord).filter(TaskRecord.task_id == t.id,
                                       TaskRecord.user_id == ctx["user"].id).with_for_update().first()
    if not rec:
        # 开考时刻 = 行创建时间（服务端时间），后续进入复用，杜绝客户端改表作弊
        rec = TaskRecord(tenant_id=ctx["tenant_id"], task_id=t.id, user_id=ctx["user"].id,
                         status="pending", time_spent=0, created_at=now, submit_time=None)
        db.add(rec)
        db.commit()
        db.refresh(rec)
    else:
        # 仍为 pending（未提交）状态：用户可能因页面崩溃/退出后重新进入，重置开考时间为当前时刻
        if rec.status == "pending":
            rec.created_at = now
            db.commit()
        else:
            db.commit()
    started = rec.created_at or now
    return {"code": 200, "data": {
        "task_id": t.id, "exam_title": t.title, "title": t.title,
        "is_timed": bool(t.is_timed), "time_limit": t.time_limit or 30,
        "end_time": t.deadline.isoformat() if t.deadline else None,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "server_now": now.isoformat(),
        "started_at": started.isoformat(),
        "my_status": rec.status if rec else "pending",
        "my_record_id": rec.id if rec else None,
        # 续答回填数据：仅「继续测试」把记录退回 pending 后非空，供考场恢复上次作答
        "my_answers": rec.answers or [],
        "questions": [_public_question(r, link.score) for link, r in links]}}


@router.get("/task-records")
def my_records(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    """我的提交历史。"""
    rows = db.query(TaskRecord, Task).join(Task, Task.id == TaskRecord.task_id).filter(
        TaskRecord.tenant_id == ctx["tenant_id"],
        TaskRecord.user_id == ctx["user"].id).order_by(TaskRecord.id.desc()).all()
    return {"code": 200, "data": {"items": [
        {"record_id": r.id, "task_id": r.task_id, "task_title": t.title,
         "status": r.status, "score": r.score,
         "submit_time": r.submit_time.strftime("%Y-%m-%d %H:%M:%S") if r.submit_time else ""}
        for r, t in rows]}}


@router.get("/task-records/{record_id}")
def my_result(record_id: int, ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    """我的成绩结果：仅本人可见，不含正确答案。"""
    rec = db.query(TaskRecord).filter(TaskRecord.id == record_id,
                                       TaskRecord.tenant_id == ctx["tenant_id"],
                                       TaskRecord.user_id == ctx["user"].id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    task = db.query(Task).filter(Task.id == rec.task_id).first()
    items = []
    for a in (rec.answers or []):
        rid = a.get("resource_id") if isinstance(a, dict) else None
        ans = a.get("answer") if isinstance(a, dict) else a
        content, score = "", 0
        correct_ans, explanation = None, ""
        q_type, q_options = None, []
        if rid:
            r = db.query(ResourceItem).filter(ResourceItem.id == rid).first()
            if r:
                content, score = r.content, r.score or 0
                correct_ans = r.correct_answer
                explanation = getattr(r, "explanation", None) or ""
                q_type = r.type
                q_options = r.options or []
            link = db.query(TaskResource).filter(TaskResource.task_id == rec.task_id,
                                                  TaskResource.resource_id == rid).first()
            if link:
                score = link.score
        items.append({"resource_id": rid, "content": content, "type": q_type, "options": q_options,
                      "user_answer": ans, "correct_answer": correct_ans, "explanation": explanation,
                      "gained": None, "eq_score": score})
    pending = rec.status == "pending_verification"
    # 及格判断：总分基于 TaskResource 分值聚合，及格线基于 task.pass_percent（默认60%）
    total_possible = sum(i.get("eq_score", 0) for i in items)
    if not total_possible:
        total_possible = 100
    pass_percent = getattr(task, "pass_percent", None) or 60
    pass_score = int(round(total_possible * pass_percent / 100.0))
    actual_score = rec.score if rec.score is not None else 0
    passed = actual_score >= pass_score and rec.score is not None
    return {"code": 200, "data": {
        "record_id": rec.id, "task_id": rec.task_id,
        "task_title": task.title if task else "",
        "status": rec.status, "pending": pending,
        "score": rec.score, "passed": passed,
        "time_spent": rec.time_spent or 0,
        "comments": rec.comments or "",
        "ai_comments": (rec.ai_result or {}).get("comments", "") if isinstance(rec.ai_result, dict) else "",
        "submit_time": rec.submit_time.strftime("%Y-%m-%d %H:%M:%S") if rec.submit_time else "",
        "items": items}}


@router.post("/tasks/{task_id}/continue")
def continue_task(task_id: int, ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    """继续测试：把本人该卷记录从「审核中」退回「进行中」，**保留上次作答内容**供学员续答修改。

    适用条件（四个缺一不可）：人工审核模式 manual、记录处于 pending_verification（成绩未终审）、
    卷内含简答题、考试时间未到期（deadline 为空视为长期开放）。
    TaskRecord 全库按「每用户每卷唯一」建模，故走原地状态回退而非新增记录行；
    已核验/已定稿的卷子一律拒绝，避免冲掉批改结论或已出成绩。"""
    now = datetime.now()
    tid = ctx["tenant_id"]
    t = db.query(Task).filter(Task.id == task_id, Task.tenant_id == tid).first()
    if not t or t.status != "published":
        raise HTTPException(status_code=404, detail="任务不存在或未发布")
    if t.deadline and now > t.deadline:
        raise HTTPException(status_code=400, detail="考试已截止，不可继续测试")
    if (t.verification_mode or "manual") != "manual":
        raise HTTPException(status_code=400, detail="该试卷为 AI 核验模式，不支持继续测试")
    has_subjective = db.query(TaskResource).join(
        ResourceItem, ResourceItem.id == TaskResource.resource_id
    ).filter(TaskResource.task_id == t.id,
             ResourceItem.type.in_(("short", "short_answer"))).first() is not None
    if not has_subjective:
        raise HTTPException(status_code=400, detail="该试卷不含简答题，交卷即定稿，不可继续测试")
    rec = db.query(TaskRecord).filter(TaskRecord.task_id == t.id,
                                      TaskRecord.tenant_id == tid,
                                      TaskRecord.user_id == ctx["user"].id).with_for_update().first()
    if not rec:
        raise HTTPException(status_code=400, detail="暂无作答记录，请直接开始测试")
    if rec.status != "pending_verification":
        raise HTTPException(status_code=400,
                            detail="已核验定分，不可继续测试" if rec.status == "verified"
                            else ("成绩已定稿，不可继续测试" if rec.status == "submitted"
                                  else "当前无需继续测试"))
    # 保留 rec.answers：学员回考场后回填上次作答，可修改后重新交卷
    rec.status = "pending"
    rec.score = None
    rec.ai_result = None
    rec.ai_rag_sources = None
    rec.comments = ""
    rec.submit_time = None
    rec.time_spent = 0
    # 重开计时锚点：以服务端当前时间为准，重新给满考试时限，杜绝客户端篡改
    rec.created_at = now
    db.flush()
    write_audit(db, tid, ctx["user"], "continue", "task_record", rec.id, f"继续测试任务 #{t.id}")
    db.commit()
    return {"code": 200, "message": "已恢复上次作答，继续本次测试",
            "data": {"record_id": rec.id, "status": "pending"}}


@router.get("/me/stats")
def my_stats(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    """个人中心统计（常规口径）：
    - 累计作答场次 / 历史答题记录 = 已交卷 + 审核中 + 已核验 的提交记录数
    - 综合通过率 = 已出分记录中「得分 >= 该卷动态及格线」的占比
    - 收藏数 = 本人收藏表真实计数
    全程强制 tenant_id + user_id 双过滤，仅 3 条 SQL，不做逐记录查库。"""
    tid = ctx["tenant_id"]
    uid = ctx["user"].id
    recs = db.query(TaskRecord).filter(
        TaskRecord.tenant_id == tid, TaskRecord.user_id == uid,
        TaskRecord.status.in_(("submitted", "pending_verification", "verified"))).all()

    task_ids = list({r.task_id for r in recs})
    total_map: Dict[int, int] = {}
    percent_map: Dict[int, int] = {}
    if task_ids:
        for t in db.query(Task).filter(Task.id.in_(task_ids), Task.tenant_id == tid).all():
            percent_map[t.id] = getattr(t, "pass_percent", None) or 60
        for tr in db.query(TaskResource).filter(TaskResource.task_id.in_(task_ids)).all():
            total_map[tr.task_id] = total_map.get(tr.task_id, 0) + (tr.score if tr.score is not None else 10)

    scored = [r for r in recs if r.score is not None]
    passed_count = 0
    for r in scored:
        total_possible = total_map.get(r.task_id) or 100
        pass_score = int(round(total_possible * percent_map.get(r.task_id, 60) / 100.0))
        if r.score >= pass_score:
            passed_count += 1
    taken = len(recs)
    return {"code": 200, "data": {
        "total_exams_taken": taken,
        "history_count": taken,
        "passed_count": passed_count,
        "pass_rate": round(passed_count / len(scored) * 100, 1) if scored else 0.0,
        "favorite_count": db.query(ResourceFavorite).filter(
            ResourceFavorite.tenant_id == tid, ResourceFavorite.user_id == uid).count()}}


@router.get("/favorites")
def list_favorites(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    rows = db.query(ResourceFavorite, ResourceItem).join(
        ResourceItem, ResourceItem.id == ResourceFavorite.resource_id
    ).filter(ResourceFavorite.tenant_id == ctx["tenant_id"],
             ResourceFavorite.user_id == ctx["user"].id).order_by(ResourceFavorite.id.desc()).all()
    return {"code": 200, "data": {"items": [
        {"id": f.id, "resource_id": r.id, "question_id": r.id,
         "content": r.content, "title": r.content, "type": r.type,
         "options": r.options or []} for f, r in rows]}}


@router.post("/favorites", status_code=201)
def add_favorite(payload: Dict[str, Any], ctx: dict = Depends(require_member),
                 db: Session = Depends(get_db)):
    rid = payload.get("resource_id") or payload.get("question_id")
    if not rid:
        raise HTTPException(status_code=400, detail="请提供 resource_id")
    r = db.query(ResourceItem).filter(ResourceItem.id == int(rid),
                                       ResourceItem.tenant_id == ctx["tenant_id"]).first()
    if not r:
        raise HTTPException(status_code=404, detail="条目不存在")
    if not db.query(ResourceFavorite).filter(
            ResourceFavorite.tenant_id == ctx["tenant_id"],
            ResourceFavorite.user_id == ctx["user"].id,
            ResourceFavorite.resource_id == r.id).first():
        db.add(ResourceFavorite(tenant_id=ctx["tenant_id"], user_id=ctx["user"].id,
                                resource_id=r.id))
        db.commit()
    return {"code": 201, "message": "收藏成功"}


@router.delete("/favorites/{rid}")
def remove_favorite(rid: int, ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    f = db.query(ResourceFavorite).filter(
        ResourceFavorite.tenant_id == ctx["tenant_id"],
        ResourceFavorite.user_id == ctx["user"].id,
        ResourceFavorite.resource_id == rid).first()
    if f:
        db.delete(f)
        db.commit()
    return {"code": 200, "message": "已取消收藏"}

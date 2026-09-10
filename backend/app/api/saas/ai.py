"""
[变更日志]
修改时间：2026-09-11
AI模型：OpenCode / Gemini 底层
修改内容：[打通组织人事与试卷资产全景问答: 1. _build_system_prompt 自动查询并权威注入所属企业成员总数、各成员姓名/角色/职业/性别/年龄画像全景; 2. 注入企业试卷总数、各出卷人统计及近期试卷明细; 3. 支持自然语言直接询问‘有几个人叫啥、个人资料、最近某老师出了什么试卷’并一键输出结构化明细]
修改时间：2026-09-10
AI模型：Gemini 系列
修改内容：[个人资料与长期记忆闭环: 1. _build_system_prompt 联合查询并权威注入当前用户的结构化档案(姓名/昵称/职业/年龄/简介等)，绝无遗漏; 2. 接入本地 Mem0 长期记忆召回(recall); 3. 流式对话完成(done)后异步触发 Mem0 长期偏好提炼(remember_async)，不阻塞 SSE 流]
修改时间：2026-09-10
AI模型：OpenCode / Gemini 底层
修改内容：[工具链全功能补齐: 1. 明确定义并补齐 delete_question (删除题目草稿/归档题目) 工具与 execute_tool 执行闭环; 2. 完善单题/多题/整卷生成与题目/试卷安全删除的完整工具链]
修改时间：2026-09-10
AI模型：OpenCode / Gemini 底层
修改内容：[智能组卷升级: 1. TOOL_DEFINITIONS 及 System Prompt 全面升级支持输出原创 questions 全量试题对象; 2. execute_tool_endpoint 正确落库真实试题 ResourceItem 与 TaskResource 关联合同; 3. 工具确认 action_required 携带完整题目并与知识库 RAG 切片强制绑定]
修改时间：2026-09-10
AI模型：OpenCode / Gemini 底层
修改内容：[工具别名兼容: execute_tool_endpoint 增加对前端 create_exam 和 batch_questions 别名的自动对齐映射，彻底解决‘未知工具: create_exam’报错]
修改时间：2026-09-10
AI模型：OpenCode / Gemini 底层
修改内容：[致命Bug修复: 解决 ai_service 产出 tool_calls 时未 yield done 导致后端漏发 action_required 工具确认事件的问题，确保出题/组卷卡片正常触发]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[租户网关覆盖+向量检索抽象接入，旧 LIKE 直查已迁移至 vector_store]
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.core.database import get_db
from app.api.deps import require_admin, require_member, require_super_admin
from app.api.saas.ops import write_audit
from app.models.saas import ResourceItem, Task, TaskResource, TaskRecord, KbDocument, KbChunk, SysUser, SysUserProfile
from app.services import memory_service
from app.models.saas import AiSession, AiMessage, AiTenantConfig, SysUser
from app.services.ai_service import chat_completion, extract_json, ai_available, AiServiceError
from app.services.ai_service import get_embedding, chat_completion_stream
from app.services.vector_store import rag_search

router = APIRouter()


def _tenant_provider(db: Session, tenant_id: int) -> Optional[Dict[str, str]]:
    """租户网关覆盖：未配置/关闭时返回 None（走服务端环境变量）。"""
    try:
        cfg = db.query(AiTenantConfig).filter(AiTenantConfig.tenant_id == tenant_id).first()
    except Exception:
        return None
    if not cfg or not cfg.enabled:
        return None
    if not (cfg.chat_api_key and cfg.chat_api_url):
        return None
    return {"name": f"Tenant#{tenant_id}", "api_url": cfg.chat_api_url,
            "api_key": cfg.chat_api_key, "model": cfg.chat_model or "default"}


def _ask(prompt: str, system: str, json_mode: bool = False,
         db: Session = None, tenant_id: int = 0) -> str:
    """网关返回 (content, tool_calls) 元组，此处只取正文；租户覆盖优先。"""
    provider = _tenant_provider(db, tenant_id) if db is not None else None
    content, _tools = chat_completion(prompt=prompt, system=system,
                                      json_mode=json_mode, provider=provider)
    return content or ""


def _rag_hits(db: Session, tenant_id: int, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """公有知识库检索（向量优先/LIKE 兜底，TiDB 分支由 vector_store 按开关路由）。
    返回强制溯源结构 [{document_id, file_name, chunk_content, similarity_score}]。"""
    vec = None
    try:
        vec = get_embedding(query, provider=_tenant_provider(db, tenant_id))
    except Exception:
        vec = None
    return rag_search(db, tenant_id, query, limit, query_vec=vec)


@router.post("/generate-resources")
def ai_generate_resources(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                          db: Session = Depends(get_db)):
    """AI 出题：基于公有知识库生成条目并落库，强制溯源。"""
    topic = str(payload.get("topic") or "").strip()
    count = int(payload.get("count") or 3)
    if not topic:
        raise HTTPException(status_code=400, detail="请提供 topic 主题")
    count = max(1, min(count, 10))
    tid = ctx["tenant_id"]
    sources = _rag_hits(db, tid, topic)
    context = "\n".join(s["chunk_content"] for s in sources) or "(暂无知识库命中，基于通用知识)"
    ids: List[int] = []
    if ai_available():
        try:
            raw = _ask(
                prompt=f"基于以下企业知识生成{count}道单选题(JSON数组，每项含content/options[{{\"key\",\"text\"}}]/correct_answer/ score)：\n知识：{context}\n主题：{topic}",
                system="你是企业培训出题助手，只输出JSON数组。",
                json_mode=True, db=db, tenant_id=tid,
            )
            items = extract_json(raw) or []
            for it in items[:count]:
                r = ResourceItem(tenant_id=tid, type="single_choice",
                                 content=str(it.get("content") or topic)[:2000],
                                 options=it.get("options") or [],
                                 correct_answer=it.get("correct_answer") or [],
                                 score=int(it.get("score") or 10),
                                 creator_id=ctx["user"].id, ai_rag_sources=sources)
                db.add(r)
                db.flush()
                ids.append(r.id)
            db.flush()
            write_audit(db, tid, ctx["user"], "generate", "resource", None,
                        f"AI 生成 {len(ids)} 条资源（{topic[:30]}）")
            db.commit()
            return {"code": 200, "message": "AI 出题成功", "data": {"resource_ids": ids, "ai_rag_sources": sources}}
        except (AiServiceError, Exception):
            db.rollback()
    # 降级：人工兜底（仍带溯源空壳，548 语义：需人工补录）
    for _ in range(count):
        r = ResourceItem(tenant_id=tid, type="single_choice", content=f"【待人工补录】{topic}",
                         options=[], correct_answer=[], score=10,
                         creator_id=ctx["user"].id, ai_rag_sources=sources)
        db.add(r)
        db.flush()
        ids.append(r.id)
    db.flush()
    write_audit(db, tid, ctx["user"], "generate", "resource", None,
                f"AI 降级兜底 {len(ids)} 条资源（{topic[:30]}）")
    db.commit()
    return {"code": 200, "message": "AI 不可用，已生成人工兜底草稿", "data": {"resource_ids": ids, "ai_rag_sources": sources}}


@router.post("/assemble-task", status_code=201)
def ai_assemble_task(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                     db: Session = Depends(get_db)):
    """AI 组卷：从资源库挑选条目组装任务，强制溯源。"""
    title = str(payload.get("title") or "").strip()
    resource_ids = list(payload.get("resource_ids") or [])
    if not title or not resource_ids:
        raise HTTPException(status_code=400, detail="请提供 title 与 resource_ids")
    tid = ctx["tenant_id"]
    sources = _rag_hits(db, tid, title)
    t = Task(tenant_id=tid, title=title, description=str(payload.get("description") or ""),
             verification_mode=str(payload.get("verification_mode") or "manual"),
             creator_id=ctx["user"].id, status="draft", ai_rag_sources=sources)
    db.add(t)
    db.flush()
    for i, rid in enumerate(resource_ids):
        res = db.query(ResourceItem).filter(ResourceItem.id == rid,
                                             ResourceItem.tenant_id == tid).first()
        if not res:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"资源 {rid} 不存在或不属于当前企业")
        db.add(TaskResource(task_id=t.id, resource_id=rid, score=res.score or 10, sort_order=i))
    db.flush()
    write_audit(db, tid, ctx["user"], "generate", "task", t.id,
                f"AI 组装任务《{title[:30]}》")
    db.commit()
    return {"code": 201, "message": "任务组装成功", "data": {"task_id": t.id, "ai_rag_sources": sources}}


@router.post("/verify/{record_id}")
def ai_verify_record(record_id: int, ctx: dict = Depends(require_admin),
                     db: Session = Depends(get_db)):
    """AI 核验：对成员提交打分建议并落库，强制溯源；失败留人工池。"""
    tid = ctx["tenant_id"]
    rec = db.query(TaskRecord).filter(TaskRecord.id == record_id,
                                       TaskRecord.tenant_id == tid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    task = db.query(Task).filter(Task.id == rec.task_id).first()
    sources = _rag_hits(db, tid, task.title if task else "")
    if ai_available():
        try:
            raw = _ask(
                prompt=f"任务《{task.title if task else ''}》作答{rec.answers}，请给出0-100分与评语(JSON {{\"score\": int, \"comments\": str}})。参考知识：{chr(10).join(s['chunk_content'] for s in sources)}",
                system="你是企业任务核验员，只输出JSON。",
                json_mode=True, db=db, tenant_id=tid,
            )
            verdict = extract_json(raw) or {}
            rec.ai_result = {"suggested_score": verdict.get("score"), "comments": verdict.get("comments", "")}
            rec.ai_rag_sources = sources
            rec.status = "pending_verification"
            db.commit()
            return {"code": 200, "data": {"record_id": rec.id, "ai_result": rec.ai_result,
                                          "ai_rag_sources": sources}}
        except (AiServiceError, Exception):
            pass
    rec.ai_result = {"error": "AI 不可用，转人工核验"}
    rec.ai_rag_sources = sources
    rec.status = "pending_verification"
    db.commit()
    return {"code": 200, "message": "AI 不可用，已转人工核验池",
            "data": {"record_id": rec.id, "ai_rag_sources": sources}}


@router.post("/questions/generate")
def ai_questions_generate_compat(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                                 db: Session = Depends(get_db)):
    """兼容旧出题表单：{material, types, count, difficulty, doc_ids, category_id}。
    返回可预览条目（不落库，由 /resources/batch 入库），强制溯源。"""
    material = str(payload.get("material") or "")[:2000]
    if not material:
        raise HTTPException(status_code=400, detail="请填写出题材料或需求描述")
    count = int(payload.get("count") or 5)
    count = max(1, min(count, 20))
    tid = ctx["tenant_id"]
    sources = _rag_hits(db, tid, material)
    context = "\n".join(s["chunk_content"] for s in sources) or "(暂无知识库命中)"
    questions: List[Dict[str, Any]] = []
    if ai_available():
        try:
            raw = _ask(
                prompt=f"基于以下材料出{count}道题(JSON数组，每项含type(single/multiple/judge/fill/short)/title/options[{{\"key\",\"text\"}}]/answer/score)：\n材料：{material}\n知识：{context}",
                system="你是企业培训出题助手，只输出JSON数组。",
                json_mode=True, db=db, tenant_id=tid,
            )
            for it in (extract_json(raw) or [])[:count]:
                questions.append({"type": it.get("type") or "single",
                                  "title": str(it.get("title") or it.get("content") or material[:30]),
                                  "options": it.get("options") or [],
                                  "answer": it.get("answer") or it.get("correct_answer") or [],
                                  "score": int(it.get("score") or 10),
                                  "ai_rag_sources": sources})
        except (AiServiceError, Exception):
            questions = []
    if not questions:
        for i in range(count):
            questions.append({"type": "single", "title": f"【待人工补录】{material[:40]}（{i + 1}）",
                              "options": [], "answer": [], "score": 10,
                              "ai_rag_sources": sources})
    return {"code": 200, "message": "AI 已生成，请预览勾选后入库",
            "data": {"questions": questions, "ai_rag_sources": sources}}


@router.post("/exams/generate")
def ai_exams_generate_compat(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                             db: Session = Depends(get_db)):
    """兼容旧组卷表单：{title, description, specs, difficulty, category_id, ...}。
    直接生成草稿任务并落库，强制溯源。"""
    description = str(payload.get("description") or "")
    title = str(payload.get("title") or "") or (description[:30] or "AI 智能组卷")
    specs = payload.get("specs") or [{"q_type": "single", "count": 5}]
    total = sum(int(s.get("count") or 0) for s in specs) or 5
    tid = ctx["tenant_id"]
    sources = _rag_hits(db, tid, description or title)
    context = "\n".join(s["chunk_content"] for s in sources) or "(暂无知识库命中)"
    made: List[Dict[str, Any]] = []
    if ai_available():
        try:
            raw = _ask(
                prompt=f"主题{title}需求{description}，生成{total}道单选题(JSON数组，每项含title/options/correct_answer)：\n知识：{context}",
                system="你是企业培训出题助手，只输出JSON数组。",
                json_mode=True, db=db, tenant_id=tid,
            )
            for it in (extract_json(raw) or [])[:total]:
                made.append({"title": str(it.get("title") or title),
                             "options": it.get("options") or [],
                             "answer": it.get("correct_answer") or []})
        except (AiServiceError, Exception):
            made = []
    if not made:
        made = [{"title": f"【待人工补录】{title}（{i + 1}）", "options": [], "answer": []}
                for i in range(total)]
    t = Task(tenant_id=tid, title=title, description=description,
             category_id=payload.get("category_id"),
             is_timed=bool(payload.get("is_timed", False)),
             time_limit=payload.get("time_limit"),
             verification_mode="manual", creator_id=ctx["user"].id,
             status="draft", ai_rag_sources=sources)
    db.add(t)
    db.flush()
    rids = []
    for i, q in enumerate(made):
        r = ResourceItem(tenant_id=tid, type="single_choice", content=q["title"],
                         options=q.get("options") or [], correct_answer=q.get("answer") or [],
                         score=10, category_id=payload.get("category_id"),
                         creator_id=ctx["user"].id, ai_rag_sources=sources)
        db.add(r)
        db.flush()
        rids.append(r.id)
        db.add(TaskResource(task_id=t.id, resource_id=r.id, score=10, sort_order=i))
    db.flush()
    write_audit(db, tid, ctx["user"], "generate", "task", t.id,
                f"AI 一键组卷《{title[:30]}》（{len(rids)} 条）")
    db.commit()
    return {"code": 200, "message": f"已生成草稿，共 {len(rids)} 题",
            "data": {"exam_id": t.id, "task_id": t.id, "question_count": len(rids),
                     "new_questions": len(rids),
                     "questions": [{"id": rid, **q} for rid, q in zip(rids, made)],
                     "ai_rag_sources": sources}}


@router.post("/chat")
def ai_chat(payload: Dict[str, Any], ctx: dict = Depends(require_member),
            db: Session = Depends(get_db)):
    """Copilot 交互：基于公有知识库回答，强制附带溯源；落会话持久化。"""
    message = str(payload.get("message") or "")[:500]
    if not message:
        raise HTTPException(status_code=400, detail="请输入问题")
    tid = ctx["tenant_id"]
    uid = ctx["user"].id
    sources = _rag_hits(db, tid, message)
    if ai_available():
        try:
            context = "\n".join(s["chunk_content"] for s in sources)
            content = _ask(
                prompt=f"参考知识：{context}\n问题：{message}",
                system="你是企业知识助手，基于给定知识回答。",
                db=db, tenant_id=tid,
            )
            sid = _persist_turn(db, tid, uid, payload.get("session_id"),
                                message, content, sources, title_hint=message[:20])
            return {"code": 200, "data": {"content": content, "ai_rag_sources": sources,
                                          "session_id": sid}}
        except (AiServiceError, Exception):
            pass
    sid = _persist_turn(db, tid, uid, payload.get("session_id"), message,
                        "AI 暂不可用，以下为知识库原文切片：", sources,
                        title_hint=message[:20])
    return {"code": 200, "message": "AI 不可用，返回检索切片由人工解读",
            "data": {"content": "AI 暂不可用，以下为知识库原文切片：",
                     "ai_rag_sources": sources, "session_id": sid}}


def _persist_turn(db: Session, tenant_id: int, user_id: int, session_id: Any,
                  message: str, content: str, sources: List[Dict[str, Any]],
                  title_hint: str = "新对话") -> Optional[int]:
    """会话落库（失败静默，不阻塞对话主流程）。"""
    try:
        sid = int(session_id) if session_id else None
        s = None
        if sid:
            s = db.query(AiSession).filter(AiSession.id == sid,
                                            AiSession.tenant_id == tenant_id,
                                            AiSession.user_id == user_id).first()
        if not s:
            s = AiSession(tenant_id=tenant_id, user_id=user_id,
                          title=(title_hint or "新对话")[:40])
            db.add(s)
            db.flush()
        db.add(AiMessage(tenant_id=tenant_id, session_id=s.id, role="user", content=message))
        db.add(AiMessage(tenant_id=tenant_id, session_id=s.id, role="assistant",
                         content=content, rag_sources=sources))
        db.commit()
        return s.id
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        return None


@router.get("/sessions")
def list_sessions(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    rows = db.query(AiSession).filter(AiSession.tenant_id == ctx["tenant_id"],
                                      AiSession.user_id == ctx["user"].id).order_by(
        AiSession.id.desc()).all()
    return {"code": 200, "data": {"items": [{"id": s.id, "title": s.title} for s in rows]}}


@router.post("/sessions", status_code=201)
def create_session(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    s = AiSession(tenant_id=ctx["tenant_id"], user_id=ctx["user"].id, title="新对话")
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"code": 201, "data": {"id": s.id, "title": s.title}}


@router.put("/sessions/{sid}")
def rename_session(sid: int, payload: Dict[str, Any], ctx: dict = Depends(require_member),
                   db: Session = Depends(get_db)):
    s = db.query(AiSession).filter(AiSession.id == sid, AiSession.tenant_id == ctx["tenant_id"],
                                   AiSession.user_id == ctx["user"].id).first()
    if not s:
        raise HTTPException(status_code=404, detail="会话不存在")
    title = str(payload.get("title") or "").strip()
    if title:
        s.title = title[:40]
        db.commit()
    return {"code": 200, "data": {"id": s.id, "title": s.title}}


@router.delete("/sessions/{sid}")
def delete_session(sid: int, ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    s = db.query(AiSession).filter(AiSession.id == sid, AiSession.tenant_id == ctx["tenant_id"],
                                   AiSession.user_id == ctx["user"].id).first()
    if not s:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.query(AiMessage).filter(AiMessage.session_id == sid).delete()
    db.delete(s)
    db.commit()
    return {"code": 200, "message": "已删除"}


@router.get("/sessions/{sid}/messages")
def session_messages(sid: int, ctx: dict = Depends(require_member), db: Session = Depends(get_db),
                     limit: int = 50, before_id: Optional[int] = None):
    s = db.query(AiSession).filter(AiSession.id == sid, AiSession.tenant_id == ctx["tenant_id"],
                                   AiSession.user_id == ctx["user"].id).first()
    if not s:
        raise HTTPException(status_code=404, detail="会话不存在")
    q = db.query(AiMessage).filter(AiMessage.session_id == sid)
    if before_id:
        q = q.filter(AiMessage.id < before_id)
    rows = q.order_by(AiMessage.id.desc()).limit(max(1, min(limit, 100))).all()
    rows = list(reversed(rows))
    items = [{"id": m.id, "role": m.role, "content": m.content,
              "ai_rag_sources": m.rag_sources or []} for m in rows]
    return {"code": 200, "data": {"items": items,
                                  "has_more": len(rows) == min(max(1, min(limit, 100)), 100),
                                  "next_cursor": rows[0].id if rows else None}}


def _mask_key(key: str) -> str:
    if not key:
        return ""
    k = str(key)
    return "****" + k[-4:] if len(k) > 4 else "****"


@router.get("/config")
def get_tenant_config(ctx: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """租户 AI 网关配置（密钥脱敏；未配置则继承服务端环境）。"""
    from app.services.ai_service import get_ai_config
    cfg = db.query(AiTenantConfig).filter(AiTenantConfig.tenant_id == ctx["tenant_id"]).first()
    env = get_ai_config()
    return {"code": 200, "data": {
        "enabled": cfg.enabled if cfg else True,
        "chat_api_url": (cfg.chat_api_url if cfg and cfg.chat_api_url else env.get("api_url")) or "",
        "chat_api_key_masked": _mask_key(cfg.chat_api_key) if cfg and cfg.chat_api_key else "",
        "chat_model": (cfg.chat_model if cfg and cfg.chat_model else env.get("model")) or "",
        "embed_model": (cfg.embed_model if cfg and cfg.embed_model else ""),
        "customized": bool(cfg and (cfg.chat_api_key or cfg.chat_api_url)),
        "env_model": env.get("model") or "",
        "source": "tenant" if cfg and (cfg.chat_api_key or cfg.chat_api_url) else "env"}}


@router.put("/config")
def put_tenant_config(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                      db: Session = Depends(get_db)):
    """保存租户网关覆盖：空密钥表示沿用旧值；传 clear_key=true 清除覆盖回退环境。"""
    cfg = db.query(AiTenantConfig).filter(AiTenantConfig.tenant_id == ctx["tenant_id"]).first()
    if not cfg:
        cfg = AiTenantConfig(tenant_id=ctx["tenant_id"], enabled=True)
        db.add(cfg)
        db.flush()
    if "enabled" in payload:
        cfg.enabled = bool(payload["enabled"])
    if payload.get("clear_key"):
        cfg.chat_api_key = ""
    elif str(payload.get("chat_api_key") or "").strip() and "****" not in str(payload["chat_api_key"]):
        cfg.chat_api_key = str(payload["chat_api_key"]).strip()
    if payload.get("chat_api_url") is not None:
        cfg.chat_api_url = str(payload.get("chat_api_url") or "").strip()
    if payload.get("chat_model") is not None:
        cfg.chat_model = str(payload.get("chat_model") or "").strip()
    if payload.get("embed_model") is not None:
        cfg.embed_model = str(payload.get("embed_model") or "").strip()
    from app.api.saas.ops import write_audit
    db.flush()
    write_audit(db, ctx["tenant_id"], ctx["user"], "update", "ai_config", cfg.id,
                "更新租户 AI 网关配置")
    db.commit()
    return {"code": 200, "message": "配置已保存", "data": {"customized": True}}


@router.post("/config/test")
def test_tenant_config(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                       db: Session = Depends(get_db)):
    """连通性测试：用租户覆盖（或提交的临时值，不落库）真实请求一句。"""
    import time as _time
    override = None
    key = str(payload.get("chat_api_key") or "")
    url = str(payload.get("chat_api_url") or "")
    model = str(payload.get("chat_model") or "")
    if key and "****" not in key and url:
        override = {"name": "test", "api_url": url, "api_key": key, "model": model or "default"}
    else:
        override = _tenant_provider(db, ctx["tenant_id"])
    t0 = _time.time()
    try:
        content, _ = chat_completion(prompt="请只回复：连通正常", system="你是连通性探针。",
                                     provider=override)
        return {"code": 200, "data": {"ok": True, "latency_ms": int((_time.time() - t0) * 1000),
                                      "reply": (content or "")[:200],
                                      "source": "tenant" if override else "env"}}
    except AiServiceError as e:
        raise HTTPException(status_code=502, detail=f"网关连通失败：{e}")


@router.post("/models/list")
def list_remote_models(payload: Dict[str, Any], _: SysUser = Depends(require_super_admin)):
    """无状态中继：拉取远端模型列表并测延迟，仅用于展示，不落库。"""
    import time as _time
    import httpx
    base_url = str(payload.get("base_url") or "").rstrip("/")
    api_key = str(payload.get("api_key") or "")
    if not base_url:
        raise HTTPException(status_code=400, detail="base_url 必填")
    headers: Dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    t0 = _time.time()
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{base_url}/models", headers=headers)
            r.raise_for_status()
            data = r.json()
            models = [m["id"] for m in (data.get("data") or [])]
            latency = int((_time.time() - t0) * 1000)
            return {"code": 200, "data": {"models": models, "latency_ms": latency}}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"远端返回 HTTP {e.response.status_code}: {e.response.text[:200]}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"网络错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"拉取异常: {e}")



# ============================================================================
# SSE 流式对话 + 工具执行
# ============================================================================

import asyncio

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_exam_draft",
            "description": "AI 智能组卷：根据用户需求原创生成整套试卷草稿，必须包含全量原创试题列表（含题型/题干/选项/答案/解析/分值），供用户在前端卡片中全面预览、调整参数与一键保存。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "试卷标题"},
                    "description": {"type": "string", "description": "试卷描述/出卷背景说明"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"], "description": "试卷难度"},
                    "category_id": {"type": "integer", "description": "试卷分类ID"},
                    "is_timed": {"type": "boolean", "description": "是否限时"},
                    "time_limit": {"type": "integer", "description": "考试限时（分钟）"},
                    "grading_mode": {"type": "string", "enum": ["manual", "ai_auto"], "description": "主观题阅卷模式"},
                    "questions": {
                        "type": "array",
                        "description": "整套试卷包含的原创试题全量列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["single", "multiple", "judge", "fill", "short"], "description": "题型: single单选/multiple多选/judge判断/fill填空/short简答"},
                                "title": {"type": "string", "description": "完整题干内容"},
                                "options": {
                                    "type": "array",
                                    "description": "选项列表（单选/多选题必填，判断/填空/简答题传空数组）",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "key": {"type": "string", "description": "选项标识，如 A, B, C, D"},
                                            "text": {"type": "string", "description": "选项文本"}
                                        },
                                        "required": ["key", "text"]
                                    }
                                },
                                "answer": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "正确答案数组（单选如['A']，多选如['A','B']，判断如['正确']或['错误']，简答/填空传参考关键词或答案）"
                                },
                                "score": {"type": "integer", "description": "本题分值，默认10分"},
                                "explanation": {"type": "string", "description": "题目解析与答案依据"}
                            },
                            "required": ["type", "title", "answer"]
                        }
                    }
                },
                "required": ["title", "questions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_question_draft",
            "description": "AI 批量出题：基于材料生成若干题目草稿，供预览和入库。",
            "parameters": {
                "type": "object",
                "properties": {
                    "material": {"type": "string", "description": "出题材料或需求描述"},
                    "types": {"type": "array", "items": {"type": "string"}},
                    "count": {"type": "integer", "default": 5},
                    "difficulty": {"type": "string"},
                    "category_id": {"type": "integer"}
                },
                "required": ["material"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_exam",
            "description": "删除指定试卷（仅允许删除本人创建的未上架草稿或已下架试卷）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "exam_id": {"type": "integer", "description": "试卷 ID"},
                    "keyword": {"type": "string", "description": "按关键词匹配最近一份试卷"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_question",
            "description": "删除指定题目（根据题目ID或题干关键词进行安全软删除）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_id": {"type": "integer", "description": "题目 ID"},
                    "keyword": {"type": "string", "description": "按题干关键词匹配最近一条题目"}
                }
            }
        }
    }
]


def _get_pending_snapshot(db: Session, tid: int, limit: int = 10) -> str:
    """返回待阅试卷快照文本，用于 AI 上下文注入。"""
    try:
        from app.models.saas import TaskRecord, Task
        pend = db.query(TaskRecord.task_id).filter(
            TaskRecord.tenant_id == tid, TaskRecord.status == "pending_verification"
        ).distinct().all()
        if not pend:
            return ""
        task_ids = [p[0] for p in pend[:limit]]
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
        lines = []
        for t in tasks:
            cnt = db.query(TaskRecord).filter(
                TaskRecord.task_id == t.id, TaskRecord.status == "pending_verification"
            ).count()
            if cnt > 0:
                lines.append(f"- 待批 《{t.title[:40]}》(id={t.id}) {cnt} 份")
        return "\n".join(lines) if lines else ""
    except Exception:
        return ""


def _get_tenant_organization_snapshot(db: Session, tid: int) -> str:
    """查询所属企业的全部组织成员姓名、角色、职业、性别、年龄等画像明细。"""
    try:
        from app.models.saas import SysTenantUser, SysUser, SysUserProfile, SysTenant
        t = db.query(SysTenant).filter(SysTenant.id == tid).first()
        t_name = t.name if t else f"企业#{tid}"
        rows = db.query(SysTenantUser, SysUser).join(
            SysUser, SysUser.id == SysTenantUser.user_id
        ).filter(
            SysTenantUser.tenant_id == tid, SysTenantUser.status == "active"
        ).order_by(
            (SysTenantUser.role == "owner").desc(),
            (SysTenantUser.role == "admin").desc(),
            SysTenantUser.id.asc()
        ).all()
        if not rows:
            return f"- 当前企业【{t_name}】暂无其他成员记录"
        
        lines = [f"企业名称: 【{t_name}】 (当前团队在职成员共 {len(rows)} 人):"]
        role_map = {"owner": "所有者", "admin": "管理员", "member": "普通成员/教师"}
        gender_map = {"male": "男", "female": "女", "secret": "保密"}
        
        for idx, (rel, u) in enumerate(rows, 1):
            profile = db.query(SysUserProfile).filter(SysUserProfile.user_id == u.id).first()
            p_items = []
            if profile:
                if profile.occupation: p_items.append(f"职业: {profile.occupation}")
                if profile.gender and profile.gender in gender_map: p_items.append(f"性别: {gender_map[profile.gender]}")
                if profile.age: p_items.append(f"年龄: {profile.age}岁")
                if profile.bio: p_items.append(f"简介: {profile.bio[:30]}")
            extra_str = f" ({', '.join(p_items)})" if p_items else ""
            lines.append(f"  {idx}. {u.display_name or u.phone} [角色: {role_map.get(rel.role, '成员')}, 手机号: {u.phone}]{extra_str}")
        return "\n".join(lines)
    except Exception:
        return ""


def _get_tenant_tasks_snapshot(db: Session, tid: int) -> str:
    """查询所属企业试卷资产全景：试卷总数、各老师/创建人出题出卷量、最近一份/近期试卷明细。"""
    try:
        from app.models.saas import Task, SysUser, TaskResource
        tasks = db.query(Task).filter(Task.tenant_id == tid).order_by(Task.id.desc()).all()
        if not tasks:
            return "- 当前企业团队尚未创建任何试卷"
        
        total_count = len(tasks)
        # 各创建人出卷量统计
        creator_stats = {}
        creator_names = {}
        for t in tasks:
            cid = t.creator_id
            creator_stats[cid] = creator_stats.get(cid, 0) + 1
            if cid not in creator_names and cid:
                u = db.query(SysUser).filter(SysUser.id == cid).first()
                creator_names[cid] = u.display_name or u.phone if u else f"用户#{cid}"
        
        stat_lines = []
        for cid, cnt in creator_stats.items():
            name = creator_names.get(cid, "系统/未知")
            stat_lines.append(f"{name}: 出卷 {cnt} 份")
        
        lines = [
            f"企业试卷总数: 共 {total_count} 套试卷",
            f"各老师出卷统计: {', '.join(stat_lines)}",
            "近期创建/出卷明细（按时间倒序，最新在前）:"
        ]
        
        # 取最近 5 份试卷详细信息
        status_map = {"draft": "草稿/未上架", "published": "已发布/已上架", "archived": "已归档"}
        for idx, t in enumerate(tasks[:5], 1):
            c_name = creator_names.get(t.creator_id, "未知出题人")
            created_str = t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "近期"
            q_cnt = db.query(TaskResource).filter(TaskResource.task_id == t.id).count()
            lines.append(
                f"  {idx}. 《{t.title}》 [出卷人: {c_name}] (状态: {status_map.get(t.status, t.status)}, 包含题目: {q_cnt}道, 阅卷方式: {t.verification_mode}, 创建时间: {created_str})"
            )
        return "\n".join(lines)
    except Exception:
        return ""


def _build_system_prompt(ctx: dict, db: Session, query: str = "") -> str:
    """构建权威系统提示词（含角色/企业组织成员全景/企业试卷资产全景/结构化用户画像/Mem0长期记忆/待阅上下文/工具规范）。"""
    role_text = "超级管理员" if ctx["role"] == "super" else ("管理员" if ctx["role"] == "admin" else "出题人")
    pending = _get_pending_snapshot(db, ctx["tenant_id"])
    org_snapshot = _get_tenant_organization_snapshot(db, ctx["tenant_id"])
    tasks_snapshot = _get_tenant_tasks_snapshot(db, ctx["tenant_id"])
    tid = ctx["tenant_id"]
    user = ctx["user"]

    # 1. 结构化用户画像查询（MySQL 权威事实：即时更新，零延迟）
    profile = db.query(SysUserProfile).filter(SysUserProfile.user_id == user.id).first()
    gender_map = {"male": "男", "female": "女", "secret": "保密"}
    gender_text = gender_map.get(profile.gender, "") if profile and profile.gender else ""

    profile_lines = [
        f"- 账号/手机号: {user.phone or user.username or '未知'}",
        f"- 姓名: {user.display_name or '未设置'}",
        f"- 昵称: {profile.nickname or '未设置'}" if profile and profile.nickname else "",
        f"- 职务/职业: {profile.occupation or '未设置'}" if profile and profile.occupation else "",
        f"- 性别: {gender_text}" if gender_text else "",
        f"- 年龄: {profile.age}岁" if profile and profile.age is not None else "",
        f"- 个人简介与专长: {profile.bio}" if profile and profile.bio else ""
    ]
    valid_profile = "\n".join([line for line in profile_lines if line])

    # 2. 本地 Mem0 长期偏好与历史记忆召回 (跨会话语义检索)
    mem0_context = ""
    if query:
        try:
            mem0_context = memory_service.recall(tid, user.id, query, limit=3)
        except Exception:
            mem0_context = ""

    parts = [
        f"你是企业培训 AI 智能助管，当前系统角色={role_text}，租户企业ID={ctx['tenant_id']}。",
        "【当前交互对象档案（结构化权威信息，请在交谈中自然称呼并知悉其背景）】:",
        valid_profile or "- 暂无详细档案",
        "",
        "【企业团队成员花名册与详细资料（只读权威事实，当用户询问有几个人、都叫啥、资料信息时，必须如实、清晰罗列）】:",
        org_snapshot,
        "",
        "【企业试卷与出题资产全景（只读权威事实，当用户询问一共出了多少试卷、最近一份试卷是什么、某某老师出的试卷明细时，必须基于此事实权威清晰作答）】:",
        tasks_snapshot,
        "",
        mem0_context if mem0_context else "",
        f"当前待阅试卷：{pending or '暂无'}",
        "",
        "你可以调用以下工具完成业务操作：",
        "1. create_exam_draft: 智能组卷。当用户提出出卷、组卷、整套试题测评需求（如‘出一套关于...的试卷’、‘组一套10道题试卷’）时，必须调用本工具！在 questions 列表中输出全量原创试题。",
        "2. create_question_draft: 批量或单道出题。当用户提出‘出1道单选题’、‘出一道题’、‘根据材料批量出题’等非整卷需求时调用。",
        "3. delete_exam: 删除试卷。当用户明确要求删除指定试卷或草稿时调用。",
        "4. delete_question: 删除题目。当用户明确要求删除某道题目或根据关键词清理题库题目时调用。",
        "请准确识别用户意图，保持亲切、专业、直接。若用户询问团队成员、出卷统计或试卷明细，直接调取上述事实以清晰结构化列表作答；当涉及组卷、出题、删除操作时，优先发起工具调用以便系统在前端渲染出交互确认卡片。"
    ]
    return "\n".join([p for p in parts if p is not None])


async def _stream_chat(
    payload: Dict[str, Any],
    ctx: dict,
    db: Session
):
    """SSE 流式对话生成器。"""
    import json
    from app.services.ai_service import chat_completion_stream
    from app.models.saas import AiSession, AiMessage
    
    message = str(payload.get("display_text") or payload.get("message") or "").strip()
    session_id = payload.get("session_id")
    tid = ctx["tenant_id"]
    uid = ctx["user"].id
    
    if not message:
        yield f"data: {{\"type\":\"error\",\"message\":\"消息不能为空\"}}\n\n"
        return
    
    # 确保会话存在
    sid: Optional[int] = None
    if session_id:
        try:
            sid = int(session_id)
        except (TypeError, ValueError):
            sid = None
    
    s = None
    if sid:
        s = db.query(AiSession).filter(
            AiSession.id == sid, AiSession.tenant_id == tid, AiSession.user_id == uid
        ).first()
    if not s:
        s = AiSession(tenant_id=tid, user_id=uid, title=message[:40])
        db.add(s)
        db.flush()
        sid = s.id
        db.commit()
    
    # 持久化用户消息
    db.add(AiMessage(tenant_id=tid, session_id=sid, role="user", content=message))
    db.flush()
    user_msg_id = None
    latest_um = db.query(AiMessage.id).filter(
        AiMessage.session_id == sid, AiMessage.role == "user"
    ).order_by(AiMessage.id.desc()).first()
    user_msg_id = latest_um.id if latest_um else None
    
    # 获取历史消息（最近6条）
    history_msgs = db.query(AiMessage).filter(
        AiMessage.session_id == sid
    ).order_by(AiMessage.id.desc()).limit(12).all()
    history = [{"role": m.role, "content": m.content} for m in reversed(history_msgs)]
    
    system_prompt = _build_system_prompt(ctx, db, query=message)
    provider = _tenant_provider(db, tid)
    
    try:
        assistant_msg = AiMessage(tenant_id=tid, session_id=sid, role="assistant", content="")
        db.add(assistant_msg)
        db.flush()
        assistant_msg_id = assistant_msg.id
        
        tool_calls_buf: Dict[int, dict] = {}
        full_content = ""
        
        for ev in chat_completion_stream(
            prompt=message,
            system=system_prompt,
            temperature=0.5,
            timeout=180.0,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            history=history
        ):
            etype = ev.get("type")
            if etype == "delta":
                text = ev.get("text", "")
                if text:
                    full_content += text
                    yield f"data: {{\"type\":\"delta\",\"text\":{json.dumps(text, ensure_ascii=False)}}}\n\n"
            elif etype == "tool_calls":
                for tc in ev.get("tool_calls", []):
                    func = tc.get("function") or {}
                    tool_name = func.get("name", "")
                    raw_args = func.get("arguments", "{}")
                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                    except Exception:
                        args = {}
                    tool_call_id = tc.get("id") or f"call_{assistant_msg_id}"
                    tool_calls_buf[len(tool_calls_buf)] = {
                        "id": tool_call_id,
                        "name": tool_name,
                        "arguments": args
                    }
            elif etype == "done":
                # 持久化 assistant 消息
                assistant_msg.content = full_content
                db.commit()
                yield f"data: {{\"type\":\"done\",\"assistant_message_id\":{assistant_msg_id},\"user_message_id\":{user_msg_id}}}\n\n"

                # 异步提炼并沉淀用户交互偏好到本地 Mem0（非阻塞，后台线程）
                if full_content and not full_content.startswith("AI 服务响应超时"):
                    memory_service.remember_async(tid, uid, message, full_content)
                # 触发工具调用确认
                for frag in tool_calls_buf.values():
                    tool_name = frag.get("name", "")
                    args = frag.get("arguments") or {}
                    # 针对组卷和出题工具自动关联知识库检索溯源
                    if tool_name in ("create_exam_draft", "create_question_draft"):
                        # 针对整卷或材料真实检索
                        overall_query = str(args.get("title") or args.get("material") or "")
                        try:
                            overall_sources = _rag_hits(db, tid, overall_query, limit=3) if overall_query else []
                        except Exception:
                            overall_sources = []

                        # 针对每道题进行独立精细化匹配判定，避免无脑全量挂载
                        if isinstance(args.get("questions"), list):
                            for q in args["questions"]:
                                if not isinstance(q, dict):
                                    continue
                                # 若大模型自己声明了来源，保留；否则基于题干真实检索
                                if not q.get("ai_rag_sources"):
                                    q_title = str(q.get("title") or "").strip()
                                    matched_sources = []
                                    if q_title:
                                        try:
                                            matched_sources = _rag_hits(db, tid, q_title, limit=1)
                                        except Exception:
                                            matched_sources = []
                                    # 仅当真实命中相关切片时才挂载，未命中则严格不挂
                                    if matched_sources:
                                        q["ai_rag_sources"] = matched_sources

                        if overall_sources:
                            args["ai_rag_sources"] = overall_sources
                    yield f"data: {{\"type\":\"action_required\"," \
                          f"\"tool_name\":\"{tool_name}\"," \
                          f"\"tool_call_id\":\"{frag['id']}\"," \
                          f"\"assistant_message_id\":{assistant_msg_id}," \
                          f"\"arguments\":{json.dumps(args, ensure_ascii=False)}," \
                          f"\"risk_level\":\"medium\"," \
                          f"\"message\":\"请确认是否执行 {tool_name}\"}}\n\n"
                tool_calls_buf.clear()
            elif etype == "error":
                err_msg = ev.get("message", "AI 服务异常")
                yield f"data: {{\"type\":\"error\",\"message\":\"{err_msg}\"}}\n\n"
                break
    except Exception as e:
        yield f"data: {{\"type\":\"error\",\"message\":\"{str(e)}\"}}\n\n"
    finally:
        try:
            db.rollback()
        except Exception:
            pass


@router.post("/chat/stream")
async def chat_stream_endpoint(
    payload: Dict[str, Any],
    ctx: dict = Depends(require_member),
    db: Session = Depends(get_db)
):
    """SSE 流式对话接口。"""
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        _stream_chat(payload, ctx, db),
        media_type="text/event-stream"
    )


@router.post("/chat/execute_tool")
def execute_tool_endpoint(
    payload: Dict[str, Any],
    ctx: dict = Depends(require_member),
    db: Session = Depends(get_db)
):
    """执行 AI 工具调用（create_exam_draft / create_question_draft / delete_exam）。"""
    import time as _time
    from app.models.saas import Task, ResourceItem, TaskResource
    
    tool_name = str(payload.get("tool_name") or "").strip()
    # 兼容前端传入的规范别名映射
    alias_map = {
        "create_exam": "create_exam_draft",
        "batch_questions": "create_question_draft"
    }
    tool_name = alias_map.get(tool_name, tool_name)
    arguments = payload.get("arguments") or {}
    tool_call_id = str(payload.get("tool_call_id") or "")
    message_id = payload.get("message_id")
    tid = ctx["tenant_id"]
    uid = ctx["user"].id
    
    # 校验消息归属并标记已执行
    if message_id:
        try:
            mid = int(message_id)
        except (TypeError, ValueError):
            mid = None
        if mid:
            am = db.query(AiMessage).filter(
                AiMessage.id == mid, AiMessage.tenant_id == tid, AiMessage.role == "assistant"
            ).first()
            if not am:
                raise HTTPException(status_code=404, detail="消息不存在")
            card = am.action_card_data or {}
            card["status"] = "executed"
            am.action_card_data = card
            db.flush()
    
    t0 = _time.time()
    result = {"status": "ok"}
    
    if tool_name == "create_exam_draft":
        title = str(arguments.get("title") or "AI 智能组卷").strip()
        description = str(arguments.get("description") or "")
        category_id = arguments.get("category_id")
        is_timed = bool(arguments.get("is_timed", False))
        time_limit = int(arguments.get("time_limit") or 0)
        grading_mode = str(arguments.get("grading_mode") or "manual")
        start_time = None
        deadline = None
        if arguments.get("start_time"):
            try:
                from datetime import datetime as _dt
                start_time = _dt.fromisoformat(str(arguments["start_time"]).replace("Z", ""))
            except Exception:
                start_time = None
        if arguments.get("deadline"):
            try:
                from datetime import datetime as _dt
                deadline = _dt.fromisoformat(str(arguments["deadline"]).replace("Z", ""))
            except Exception:
                deadline = None

        sources = arguments.get("ai_rag_sources") or _rag_hits(db, tid, title)
        t = Task(
            tenant_id=tid, title=title, description=description,
            category_id=category_id,
            is_timed=is_timed, time_limit=time_limit,
            start_time=start_time, deadline=deadline,
            verification_mode="ai_auto" if grading_mode == "ai_auto" else "manual",
            creator_id=uid, status="draft", ai_rag_sources=sources
        )
        db.add(t)
        db.flush()

        raw_questions = arguments.get("questions")
        qids: List[int] = []

        if isinstance(raw_questions, list) and len(raw_questions) > 0:
            for idx, q in enumerate(raw_questions):
                if not isinstance(q, dict):
                    continue
                q_type = str(q.get("type") or "single")
                q_content = str(q.get("title") or q.get("content") or f"试题 {idx + 1}")
                q_opts = q.get("options") or []
                q_ans = q.get("answer") or q.get("correct_answer") or []
                q_score = int(q.get("score") or 10)
                q_sources = q.get("ai_rag_sources") or sources

                r = ResourceItem(
                    tenant_id=tid,
                    type=q_type,
                    content=q_content,
                    options=q_opts,
                    correct_answer=q_ans,
                    score=q_score,
                    category_id=category_id,
                    creator_id=uid,
                    ai_rag_sources=q_sources
                )
                db.add(r)
                db.flush()
                qids.append(r.id)
                db.add(TaskResource(task_id=t.id, resource_id=r.id, score=q_score, sort_order=len(qids)))
        else:
            # 降级兜底兼容 specs 计数
            specs = arguments.get("specs") or [{"q_type": "single", "count": 5}]
            for i, spec in enumerate(specs):
                qtype = str(spec.get("q_type") or "single")
                count = int(spec.get("count") or 3)
                for j in range(count):
                    r = ResourceItem(
                        tenant_id=tid, type=qtype,
                        content=f"【AI 生成草稿】{title}（{qtype}题 第{j+1}题）",
                        options=[], correct_answer=[], score=10,
                        category_id=category_id,
                        creator_id=uid, ai_rag_sources=sources
                    )
                    db.add(r)
                    db.flush()
                    qids.append(r.id)
                    db.add(TaskResource(task_id=t.id, resource_id=r.id, score=10, sort_order=len(qids)))

        db.flush()
        write_audit(db, tid, ctx["user"], "generate", "task", t.id, f"AI 组卷《{title[:30]}》共 {len(qids)} 题")
        db.commit()
        result = {"exam_id": t.id, "question_count": len(qids), "title": title}
        
    elif tool_name == "create_question_draft":
        material = str(arguments.get("material") or "").strip()
        types = arguments.get("types") or ["single"]
        count = max(1, min(int(arguments.get("count") or 5), 20))
        difficulty = str(arguments.get("difficulty") or "medium")
        category_id = arguments.get("category_id")
        
        sources = _rag_hits(db, tid, material)
        questions: List[Dict[str, Any]] = []
        if ai_available():
            try:
                raw = _ask(
                    prompt=f"基于以下材料出{count}道题(JSON数组，每项含type(single/multiple/judge/fill/short)/title/options[key,text]/answer/score)：\n材料：{material}\n类型：{types}",
                    system="你是企业培训出题助手，只输出JSON数组。",
                    json_mode=True, db=db, tenant_id=tid,
                )
                questions = extract_json(raw) or []
            except Exception:
                questions = []
        if not questions:
            for i in range(count):
                questions.append({"type": "single", "title": f"【待人工补录】{material[:40]}（{i + 1}）",
                                  "options": [], "answer": [], "score": 10,
                                  "ai_rag_sources": sources})
        
        qids = []
        for it in questions[:count]:
            r = ResourceItem(
                tenant_id=tid, type=str(it.get("type") or "single"),
                content=str(it.get("title") or material[:50]),
                options=it.get("options") or [],
                correct_answer=it.get("answer") or it.get("correct_answer") or [],
                score=int(it.get("score") or 10),
                category_id=category_id, creator_id=uid, ai_rag_sources=sources
            )
            db.add(r)
            db.flush()
            qids.append(r.id)
        db.commit()
        write_audit(db, tid, ctx["user"], "generate", "resource", None, f"AI 批量出题 {len(qids)} 条")
        result = {"question_ids": qids, "count": len(qids)}
        
    elif tool_name == "delete_exam":
        exam_id = arguments.get("exam_id")
        keyword = str(arguments.get("keyword") or "").strip()
        q = db.query(Task).filter(Task.tenant_id == tid, Task.creator_id == uid,
                                  Task.status.in_(["draft", "archived"]))
        if exam_id:
            try:
                q = q.filter(Task.id == int(exam_id))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="exam_id 无效")
        elif keyword:
            q = q.filter(Task.title.contains(keyword))
        target = q.order_by(Task.id.desc()).first()
        if not target:
            raise HTTPException(status_code=404, detail="未找到符合条件的试卷")
        pending = db.query(TaskRecord).filter(
            TaskRecord.task_id == target.id, TaskRecord.status != "verified"
        ).count()
        if pending > 0:
            raise HTTPException(status_code=400, detail=f"该试卷有 {pending} 份未完成答卷，无法删除")
        db.delete(target)
        db.commit()
        write_audit(db, tid, ctx["user"], "delete", "task", target.id, f"删除试卷《{target.title[:30]}》")
        result = {"deleted_id": target.id, "title": target.title}
    elif tool_name == "delete_question":
        question_id = arguments.get("question_id")
        keyword = str(arguments.get("keyword") or "").strip()
        q = db.query(ResourceItem).filter(ResourceItem.tenant_id == tid, ResourceItem.is_deleted == False)
        if question_id:
            try:
                q = q.filter(ResourceItem.id == int(question_id))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="question_id 无效")
        elif keyword:
            q = q.filter(ResourceItem.content.contains(keyword))
        target = q.order_by(ResourceItem.id.desc()).first()
        if not target:
            raise HTTPException(status_code=404, detail="未找到符合条件的题目")
        target.is_deleted = True
        db.commit()
        write_audit(db, tid, ctx["user"], "delete", "resource", target.id, f"删除题目 #{target.id}")
        result = {"deleted_question_id": target.id, "content": target.content[:40]}
    else:
        raise HTTPException(status_code=400, detail=f"未知工具: {tool_name}")
    
    latency_ms = int((_time.time() - t0) * 1000)
    return {"code": 200, "message": "工具执行成功", "data": {**result, "latency_ms": latency_ms}}

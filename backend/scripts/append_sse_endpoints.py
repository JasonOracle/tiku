# -*- coding: utf-8 -*-
"""Append SSE stream and execute_tool endpoints to ai.py"""

NEW_CODE = r'''


# ============================================================================
# SSE 流式对话 + 工具执行
# ============================================================================

import asyncio

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_exam_draft",
            "description": "AI 智能组卷：根据用户需求生成试卷草稿（含题型/题数/难度配置），返回可确认的试卷结构。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "试卷标题"},
                    "description": {"type": "string", "description": "试卷描述/需求说明"},
                    "specs": {
                        "type": "array",
                        "items": {"type": "object", "properties": {
                            "q_type": {"type": "string", "enum": ["single", "multiple", "judge", "fill", "short"]},
                            "count": {"type": "integer"}
                        }}
                    },
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                    "category_id": {"type": "integer"},
                    "is_timed": {"type": "boolean"},
                    "time_limit": {"type": "integer"},
                    "grading_mode": {"type": "string", "enum": ["manual", "ai_auto"]}
                },
                "required": ["title", "specs"]
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


def _build_system_prompt(ctx: dict, db: Session) -> str:
    """构建系统提示词（含角色/上下文）。"""
    role_text = "超级管理员" if ctx["role"] == "super" else ("管理员" if ctx["role"] == "admin" else "出题人")
    pending = _get_pending_snapshot(db, ctx["tenant_id"])
    parts = [
        f"你是企业培训 AI 智能助管，角色={role_text}，租户={ctx['tenant_id']}。",
        f"当前待阅试卷：{pending or '暂无'}",
        "你可以调用以下工具完成任务：",
        "- create_exam_draft: 智能组卷",
        "- create_question_draft: 批量出题",
        "- delete_exam: 删除试卷",
        "请根据用户意图选择合适的工具或直接回答。"
    ]
    return "\n".join(parts)


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
    
    system_prompt = _build_system_prompt(ctx, db)
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
            history=history,
            provider=provider
        ):
            etype = ev.get("type")
            if etype == "delta":
                text = ev.get("text", "")
                if text:
                    full_content += text
                    yield f"data: {{\"type\":\"delta\",\"text\":{json.dumps(text, ensure_ascii=False)}}}\n\n"
            elif etype == "tool_calls":
                for tc in ev.get("tool_calls", []):
                    idx = tc.get("index", 0)
                    frag = tool_calls_buf.setdefault(idx, {"id": "", "name": "", "arguments": ""})
                    if tc.get("id"):
                        frag["id"] = tc["id"]
                    func = tc.get("function") or {}
                    if func.get("name"):
                        frag["name"] = func["name"]
                    if func.get("arguments"):
                        frag["arguments"] += func["arguments"]
            elif etype == "done":
                # 持久化 assistant 消息
                assistant_msg.content = full_content
                db.commit()
                yield f"data: {{\"type\":\"done\",\"assistant_message_id\":{assistant_msg_id},\"user_message_id\":{user_msg_id}}}\n\n"
                # 触发工具调用确认
                for frag in tool_calls_buf.values():
                    tool_name = frag.get("name", "")
                    try:
                        args = json.loads(frag.get("arguments") or "{}")
                    except Exception:
                        args = {}
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
    
    tool_name = str(payload.get("tool_name") or "")
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
        specs = arguments.get("specs") or [{"q_type": "single", "count": 5}]
        difficulty = str(arguments.get("difficulty") or "medium")
        category_id = arguments.get("category_id")
        is_timed = bool(arguments.get("is_timed", False))
        time_limit = int(arguments.get("time_limit") or 0)
        grading_mode = str(arguments.get("grading_mode") or "manual")
        
        sources = _rag_hits(db, tid, title)
        t = Task(
            tenant_id=tid, title=title, description=description,
            category_id=category_id,
            is_timed=is_timed, time_limit=time_limit,
            verification_mode="ai_auto" if grading_mode == "ai_auto" else "manual",
            creator_id=uid, status="draft", ai_rag_sources=sources
        )
        db.add(t)
        db.flush()
        
        qids: List[int] = []
        for i, spec in enumerate(specs):
            qtype = str(spec.get("q_type") or "single")
            count = int(spec.get("count") or 3)
            for j in range(count):
                r = ResourceItem(
                    tenant_id=tid, type=qtype,
                    content=f"【AI 生成草稿】{title}（{qtype}题 第{j+1}题）",
                    options=[], correct_answer=[], score=10,
                    creator_id=uid, ai_rag_sources=sources
                )
                db.add(r)
                db.flush()
                qids.append(r.id)
                db.add(TaskResource(task_id=t.id, resource_id=r.id, score=10, sort_order=len(qids)))
        db.flush()
        write_audit(db, tid, ctx["user"], "generate", "task", t.id, f"AI 组卷《{title[:30]}》")
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
    else:
        raise HTTPException(status_code=400, detail=f"未知工具: {tool_name}")
    
    latency_ms = int((_time.time() - t0) * 1000)
    return {"code": 200, "message": "工具执行成功", "data": {**result, "latency_ms": latency_ms}}
'''

filepath = r"D:\project\tiku\tiku\backend\app\api\saas\ai.py"
with open(filepath, "a", encoding="utf-8") as f:
    f.write(NEW_CODE)
print("Done appending SSE stream code to ai.py")

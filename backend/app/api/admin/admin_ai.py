"""
[变更日志]
修改时间：2026-09-06 22:30:00
AI模型：ZCode (GLM)
修改内容：[v1.5 修复用户反馈: AI出题材料指定数量被默认5覆盖(材料数量优先) / 单次生成上限10道(超出截断+提示) /
         v1.2 新增 AI 员工 API: ✨AI出题(预览+二次确认入库)/✨AI智能组卷/AI Copilot/额度资产化/双域审计]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[v1.2 Step2: AI 组卷 grading_mode 与 is_ai_auto_grade 双写]
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.models.category import ExamCategory
from app.schemas.question import QuestionCreate, QuestionResponse
from app.schemas.common import ResponseModel
from app.services import ai_service
from app.services.ai_service import AiServiceError
from app.services.quota_service import deduct_quota
from app.services.exam_service import first_category_id, recalc_exam_totals
from app.services.audit_service import write_audit, push_notification
from app.services.ai_tools_registry import get_allowed_tools, REGISTRY
from app.models.ai_chat import AiChatSession, AiChatMessage
import json
import re

router = APIRouter()

# v1.5: 单次 AI 出题硬上限 (防止一次生成太多等待过久, 更多请分批生成; 前端红字提示同步此数)
AI_GEN_MAX_COUNT = 10


# ---------------- 请求体 ----------------

class QuestionGenRequest(BaseModel):
    """AI 出题请求: material 必填; 高级选项(题型/数量/难度)可选, 但任一填写则三项都必须填写 (冲突时以高级选项为准)"""
    material: str = Field(..., min_length=5, description="材料文本或自然语言描述")
    types: Optional[List[str]] = Field(None, description="题型组合, 如 ['single','judge']; 空则 AI 按 material 自主决定")
    count: Optional[int] = Field(None, ge=1, le=AI_GEN_MAX_COUNT, description=f"出题数量 1~{AI_GEN_MAX_COUNT}; 空则 AI 按材料指定数量(不超上限), 材料未指定默认 5")
    difficulty: Optional[str] = Field(None, description="难度 easy/medium/hard; 空则默认 medium")
    category_id: Optional[int] = Field(None, description="归入分类")
    # 兼容旧字段 (v1.2 单题型), 内部并入 types
    q_type: Optional[str] = Field(None, description="已废弃, 兼容旧前端: 单题型")

class ExamSpecItem(BaseModel):
    q_type: str = Field(..., description="题型")
    count: int = Field(..., ge=1, le=20, description="数量")
    score: Optional[int] = Field(None, description="每题分值 (默认取题库题目分值或10)")

class ExamGenRequest(BaseModel):
    title: Optional[str] = Field(None, description="试卷标题 (AI 可补全)")
    description: str = Field(..., min_length=5, description="组卷自然语言需求")
    specs: List[ExamSpecItem] = Field(..., description="题型构成要求")
    difficulty: Optional[str] = Field("medium", description="难度: easy, medium, hard")
    category_id: Optional[int] = Field(None, description="试卷分类")
    is_timed: bool = Field(True)
    time_limit: int = Field(30)
    pass_percent: int = Field(60)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="老师提问 (可含前端状态快照)")
    history: Optional[List[dict]] = Field(default=[], description="轻量历史 [{role, content}]")
    session_id: Optional[int] = Field(None, description="云端会话ID (stream 落库用, 未传自动新建)")
    display_text: Optional[str] = Field(None, description="用户原文 (落库与展示用, 不含隐藏快照)")

class ExecuteToolRequest(BaseModel):
    tool_name: str
    arguments: dict
    tool_call_id: str
    message_id: Optional[int] = Field(None, description="卡片所属消息ID (执行成功后持久化 executed 状态)")

class ChatFeedbackRequest(BaseModel):
    message_content: str
    rating: str = Field(..., description="'up' or 'down'")

class ChatFeedbackRequest(BaseModel):
    message_content: str
    rating: str = Field(..., description="'up' or 'down'")


# ---------------- 状态 ----------------

@router.get("/status")
def ai_status(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """AI 能力状态: 是否配置 Key / 模型名 / 本人今日剩余额度"""
    from app.services.quota_service import refresh_daily_quota
    refresh_daily_quota(admin)
    db.commit()
    cfg = ai_service.get_ai_config()
    
    # 针对 super_admin 返回无限制
    q_remaining = 99999999 if admin.role == "super_admin" else (admin.daily_ai_quota or 0)
    q_limit = 99999999 if admin.role == "super_admin" else (admin.ai_quota_limit or 0)
    
    return ResponseModel(code=200, data={
        "available": ai_service.ai_available(),
        "model": cfg["model"],
        "quota_remaining": q_remaining,
        "quota_limit": q_limit,
    })


# ---------------- 云端会话与消息流水 (跨端漫游 + 游标分页) ----------------

class SessionRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120, description="新标题")


def _get_owned_session(db: Session, admin: Admin, session_id: int) -> AiChatSession:
    s = db.query(AiChatSession).filter(
        AiChatSession.id == session_id, AiChatSession.admin_id == admin.id).first()
    if not s:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    return s


def _serialize_session(s: AiChatSession) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "",
        "updated_at": s.updated_at.strftime("%Y-%m-%d %H:%M:%S") if s.updated_at else "",
    }


def _serialize_message(m: AiChatMessage) -> dict:
    return {
        "id": m.id,
        "session_id": m.session_id,
        "role": m.role,
        "content": m.content,
        "quote": m.quote,
        "action_card_data": m.action_card_data,
        "action_list_data": m.action_list_data,
        "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
    }


def _format_tool_result_fallback(t_name: str, result_data) -> str:
    """空回复兜底：模型归纳轮返回空包时，按工具结果拼装人工可读回复，绝不落空库"""
    try:
        data = result_data or {}
        if t_name == "get_my_exams":
            exams = data.get("my_exams") or []
            if not exams:
                return "你名下暂无创建的试卷（共 0 套）。可在试卷管理中新建组卷。"
            lines = [f"《{e.get('title')}》(状态: {e.get('status')})" for e in exams[:10]]
            suffix = f"等共 {len(exams)} 套" if len(exams) > 10 else f"共 {len(exams)} 套"
            return f"你名下{suffix}试卷：\n" + "\n".join(f"- {l}" for l in lines)
        if t_name == "get_database_stats":
            cur = data.get("current_user") or {}
            glo = data.get("global_stats") or {}
            return (f"业务统计：全站题目 {glo.get('total_questions', 0)} 道、试卷 {glo.get('total_exams', 0)} 套、"
                    f"分类 {glo.get('total_categories', 0)} 个；你（{cur.get('username', '')}）创建题目 "
                    f"{cur.get('created_questions_count', 0)} 道、试卷 {cur.get('created_exams_count', 0)} 套。")
        if t_name == "get_user_stats":
            parts = [f"{k}: {v}" for k, v in data.items() if k != "role_distribution"]
            return "用户统计：" + ("、".join(parts) if parts else "暂无数据")
        s = json.dumps(data, ensure_ascii=False)
        return "已获取业务数据：" + (s[:500] + "…" if len(s) > 500 else (s or "暂无数据"))
    except Exception:
        return "已获取业务数据，请继续追问细化。"


def _parse_action_blocks(text: str):
    """从 Assistant 全文提取 action_card / action_list 代码块 (落库用, 解析失败则 None)"""
    card = lst = None
    if text:
        mc = re.search(r"```action_card\s*([\s\S]*?)```", text)
        if mc:
            try:
                card = json.loads(mc.group(1))
                if isinstance(card, dict):
                    card = {**card, "status": "pending"}
                else:
                    card = None
            except Exception:
                card = None
        ml = re.search(r"```action_list\s*([\s\S]*?)```", text)
        if ml:
            try:
                lst = json.loads(ml.group(1))
                if not isinstance(lst, list):
                    lst = None
            except Exception:
                lst = None
    return card, lst


@router.get("/sessions", response_model=ResponseModel[dict])
def list_chat_sessions(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """云端会话列表 (按最近活跃倒序, 仅本人)"""
    sessions = db.query(AiChatSession).filter(
        AiChatSession.admin_id == admin.id).order_by(AiChatSession.updated_at.desc()).all()
    return ResponseModel(code=200, data={"items": [_serialize_session(s) for s in sessions]})


@router.post("/sessions", response_model=ResponseModel[dict])
def create_chat_session(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """新建云端会话 (默认标题“新对话”)"""
    s = AiChatSession(admin_id=admin.id, title="新对话")
    db.add(s)
    db.commit()
    db.refresh(s)
    return ResponseModel(code=201, message="会话已创建", data=_serialize_session(s))


@router.delete("/sessions/{session_id}", response_model=ResponseModel[dict])
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """删除会话及旗下全部消息 (校验归属权, 显式双删以兼容无 FK 强约束库)"""
    s = _get_owned_session(db, admin, session_id)
    db.query(AiChatMessage).filter(AiChatMessage.session_id == s.id).delete()
    db.delete(s)
    db.commit()
    return ResponseModel(code=200, message="会话已删除", data={"id": session_id})


@router.put("/sessions/{session_id}", response_model=ResponseModel[dict])
def rename_chat_session(
    session_id: int,
    data: SessionRenameRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """重命名会话标题"""
    s = _get_owned_session(db, admin, session_id)
    s.title = data.title.strip()
    db.commit()
    return ResponseModel(code=200, message="已重命名", data=_serialize_session(s))


@router.get("/sessions/{session_id}/messages", response_model=ResponseModel[dict])
def list_chat_messages(
    session_id: int,
    before_id: Optional[int] = Query(None, description="游标: 仅返回 id 更小的更早消息"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """游标分页拉取消息 (DESC 取 limit+1 判 has_more, 内存反转为时间正序)"""
    _get_owned_session(db, admin, session_id)
    q = db.query(AiChatMessage).filter(AiChatMessage.session_id == session_id)
    if before_id is not None:
        q = q.filter(AiChatMessage.id < before_id)
    rows = q.order_by(AiChatMessage.id.desc()).limit(limit + 1).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    items = [_serialize_message(m) for m in reversed(rows)]
    return ResponseModel(code=200, data={
        "items": items,
        "has_more": has_more,
        "next_cursor": items[0]["id"] if items else None,
    })


# ---------------- ✨ AI 出题 ----------------

QUESTION_JSON_SPEC = """{"questions": [{"type": "single|multiple|judge|fill|short",
 "title": "题干, 填空题用___作空位占位符",
 "options": [{"key": "A", "text": "选项内容"}],
 "answer": 客观题如["A"], 填空题为二维数组如[["北京","北京市"]], 简答题为["参考答案全文"],
 "grading_points": ["简答题踩分点1", "踩分点2"],
 "explanation": "解析", "difficulty": "easy|medium|hard", "score": 10}]}"""


def _normalize_options(options) -> list:
    from app.api.admin.questions import normalize_options
    return normalize_options(options)


def _normalize_generated_question(q: dict, default_type: str, default_difficulty: str) -> dict:
    """规范化 AI 生成的题目结构 (大模型常把 answer/options 返回成字符串或错位结构, 统一纠正)"""
    q_type = q.get("type", default_type)
    title = str(q.get("title", ""))
    answer = q.get("answer")
    if q_type == "fill":
        if not isinstance(answer, list) or not answer:
            answer = [["参考答案"]]
        else:
            answer = [b if isinstance(b, list) else [str(b)] for b in answer]
        # 自动强对齐: 确保题干中的 ___ 占位符数量与 answer 二维数组空数一致
        blank_count = title.count("___")
        if blank_count == 0:
            # 题干中若 AI 忘记写 ___ 占位符，自动补充在题干末尾
            needed_blanks = len(answer)
            title = title.rstrip() + " " + " ".join(["___"] * needed_blanks)
            blank_count = title.count("___")
        
        # 如果 blank_count != len(answer)，以题干占位符数量为准裁剪或补齐答案
        if blank_count > len(answer):
            diff = blank_count - len(answer)
            for _ in range(diff):
                answer.append(["参考答案"])
        elif blank_count < len(answer):
            answer = answer[:blank_count]

    elif q_type == "short":
        if isinstance(answer, str):
            answer = [answer]
        answer = [str(a) for a in (answer or [])]
    else:
        if isinstance(answer, str):
            answer = [a.strip().upper() for a in answer.replace(",", "").replace("；", "").replace(";", "") if a.strip()]
        answer = [str(a) for a in (answer or [])]
    gp = q.get("grading_points")
    if isinstance(gp, str):
        grading_points = [gp]
    elif isinstance(gp, list):
        grading_points = [str(x) for x in gp]
    elif gp is not None and not isinstance(gp, (list, dict)):
        grading_points = [str(gp)]
    else:
        grading_points = []

    return {
        "type": q_type,
        "title": title,
        "options": _normalize_options(q.get("options")),
        "answer": answer,
        "grading_points": grading_points,
        "explanation": str(q.get("explanation", "")),
        "difficulty": q.get("difficulty", default_difficulty),
        "score": 10,
    }

@router.post("/questions/generate")
def ai_generate_questions(
    data: QuestionGenRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """✨AI出题: 生成结构化题目 JSON 供前端预览, 老师二次确认后才调用批量入库 (本接口不写题库)。
    高级选项规则: 题型组合/数量/难度 三项要么全空 (AI 按 material 自主: 材料指定数量优先, 未指定默认5题),
    要么全部填写; 与 material 文字描述冲突时, 以高级选项为准 (数量以高级选项硬性为准)。
    v1.5: 单次生成硬上限 AI_GEN_MAX_COUNT 道, 材料要求超出时按上限截断并在 message 中说明。"""
    if not ai_service.ai_available():
        raise HTTPException(status_code=400, detail="AI 服务未配置（缺少 SENSENOVA_API_KEY）")

    # ---- 归一化高级选项 (兼容旧 q_type 字段) ----
    types = list(data.types) if data.types else ([data.q_type] if data.q_type else None)
    count = data.count
    difficulty = (data.difficulty or "").strip().lower() or None
    for t in (types or []):
        if t not in ("single", "multiple", "judge", "fill", "short"):
            raise HTTPException(status_code=400, detail=f"不支持的题型: {t}")

    # 高级选项(types, count, difficulty) 要么全空, 要么全填 (兼容单题型旧参数)
    filled_count = sum(1 for x in [types, count, difficulty] if x is not None)
    if filled_count > 0 and filled_count < 3:
        raise HTTPException(status_code=400, detail="高级选项(题型组合、题目数量、难度)请完整填写，或全部留空由 AI 自主决定")

    # 当指定了数量 N 且选了多个题型，若 N < len(types)，以数量为准，截取前 N 个题型
    if types and count and count < len(types):
        types = types[:count]

    if not count:
        count = 5
    if not difficulty:
        difficulty = "medium"
        count = count or 5
        difficulty = difficulty or "medium"

    deduct_quota(db, admin, "question_gen", {"count": count, "types": types})

    # ---- Prompt: 高级选项是硬性指令 (与 material 文字冲突时以指令为准) ----
    type_names = {"single": "单选题", "multiple": "多选题", "judge": "判断题", "fill": "填空题", "short": "简答题"}
    if types:
        if len(types) == 1:
            type_line = f"所有题目必须为【{type_names[types[0]]}】, 不得混入其他题型。"
        else:
            type_line = ("题目必须按以下题型构成输出(合计恰好 "
                         + f"{count} 题): " + "、".join(f"{type_names[t]}若干" for t in types)
                         + f"。总题数必须正好 {count} 题。")
        constraint = (
            f"【硬性要求(优先级最高, 与材料文字描述冲突时以此为准)】:\n"
            f"1. 必须输出恰好 {count} 道题, 不多不少。\n"
            f"2. {type_line}\n"
            f"3. 难度统一为 {difficulty}。\n"
            f"材料仅作为出题主题素材, 材料中提到的题目数量/题型要求一律忽略。"
        )
    else:
        # v1.5 修复: 材料里明确写的"生成N道"必须优先于默认值 (此前被写死的"输出 5 道"覆盖, 用户说10道只出5道)
        constraint = (
            "根据材料自主决定最合适的题型与题目分布。"
            "若材料中明确指定了题目数量（如「生成10道」「出20题」），必须严格按材料指定的数量输出；"
            f"材料未指定数量时默认输出 {count} 道题。"
            f"无论材料要求多少, 单次生成总题数不得超过 {AI_GEN_MAX_COUNT} 道, 超出时按 {AI_GEN_MAX_COUNT} 道输出。"
            f"难度默认 {difficulty}。"
        )

    system = "你是专业的题库出题专家。根据老师给定的材料或描述出题。只输出 JSON, 格式: " + QUESTION_JSON_SPEC
    prompt = (
        f"{constraint}\n\n"
        f"出题要求: 每题 score=10, 带解析。填空题题干中 ___ 的数量必须与 answer 二维数组长度一致; "
        f"简答题必须给出参考答案和踩分点。\n\n材料/需求:\n{data.material}"
    )
    try:
        raw, _ = ai_service.chat_completion(prompt, system=system, json_mode=True)
        parsed = ai_service.extract_json(raw)
        questions = parsed.get("questions") if isinstance(parsed, dict) else parsed
        if not isinstance(questions, list) or not questions:
            raise AiServiceError("未返回题目列表")
    except (AiServiceError, ValueError) as e:
        raise HTTPException(status_code=502, detail=f"AI 出题失败: {e}")

    # 结构规范化 (不给 AI 越权字段; 纠正 answer/options 结构)
    safe_items = []
    for q in questions:
        if not isinstance(q, dict) or not q.get("title"):
            continue
        default_type = types[0] if (types and len(types) == 1) else "single"
        item = _normalize_generated_question(q, default_type, difficulty or "medium")
        if types and item["type"] not in types:
            continue  # AI 越出题型构成, 丢弃
        item["category_id"] = data.category_id
        item["source"] = "ai"
        safe_items.append(item)
    if not safe_items:
        raise HTTPException(status_code=502, detail="AI 未生成有效题目，请调整描述后重试")
    # v1.5: 全局硬上限截断 (材料要求超过上限时按上限出); 高级选项数量仍硬性为准
    cap_note = ""
    if len(safe_items) > AI_GEN_MAX_COUNT:
        safe_items = safe_items[:AI_GEN_MAX_COUNT]
        cap_note = f"（单次最多生成 {AI_GEN_MAX_COUNT} 道，已按上限截断，如需更多请分批生成）"
    if types and count and len(safe_items) > count:
        safe_items = safe_items[:count]
    note = "" if not types or len(safe_items) >= count else f"（AI 实际返回 {len(safe_items)}/{count} 题，数量不足可再生成一批）"
    return ResponseModel(code=200, message="生成成功，请预览确认后入库" + cap_note + note, data={"questions": safe_items})


# ---------------- ✨ AI 智能组卷 ----------------

@router.post("/exams/generate")
def ai_generate_exam(
    data: ExamGenRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """✨AI智能一键组卷: 优先从共享题库检索, 不足自动生成新题; 试卷强制 Draft 待人工审核上架"""
    if not ai_service.ai_available():
        raise HTTPException(status_code=400, detail="AI 服务未配置（缺少 SENSENOVA_API_KEY）")
    total_expected = sum(s.count for s in data.specs)
    deduct_quota(db, admin, "exam_gen", {"title": data.title, "specs": [s.model_dump() for s in data.specs]})

    # 题库摘要 (供 AI 检索复用; 截断防 prompt 过长超时)
    bank = db.query(Question).filter(Question.is_deleted == False).order_by(Question.id.desc()).limit(120).all()  # noqa: E712
    bank_digest = [{"id": q.id, "type": q.type, "title": (q.title or "")[:30]} for q in bank]

    system = (
        "你是智能组卷助理。你会收到: 老师需求、题型构成要求、当前共享题库摘要。"
        "请优先复用题库中的题目 (引用 id); 数量不足或无合适题目时生成新题 (short 题需 grading_points, "
        "fill 题题干用___且数量与 answer 二维数组长度一致)。"
        '只输出 JSON: {"title": "试卷标题", "items": [{"question_id": 题库id} 或 {"new_question": {'
        '"type","title","options","answer","grading_points","explanation","difficulty"}}]}'
    )
    difficulty = data.difficulty or "medium"
    prompt = (
        f"老师需求: {data.description}\n"
        f"题型构成: {[(s.q_type, s.count) for s in data.specs]}\n"
        f"题目难度: {difficulty}\n"
        f"题库摘要(共{len(bank_digest)}题): {bank_digest}\n"
        f"请严格按题型构成数量输出 items (合计 {total_expected} 项)。"
    )
    try:
        raw, _ = ai_service.chat_completion(prompt, system=system, json_mode=True, temperature=0.2)
        parsed = ai_service.extract_json(raw)
        items = parsed.get("items") if isinstance(parsed, dict) else None
        if not isinstance(items, list) or not items:
            raise AiServiceError("未返回组卷明细")
    except (AiServiceError, ValueError) as e:
        raise HTTPException(status_code=502, detail=f"AI 组卷失败: {e}")

    # ---- 落库: 新题 source=ai; 试卷强制 Draft ----
    question_ids: List[int] = []
    created_new = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("question_id"):
            q = db.query(Question).filter(Question.id == int(item["question_id"]), Question.is_deleted == False).first()  # noqa: E712
            if q:
                question_ids.append(q.id)
        elif isinstance(item.get("new_question"), dict):
            nq = _normalize_generated_question(item["new_question"], "single", difficulty)
            try:
                from app.api.admin.questions import _validate_question_payload
                _validate_question_payload(nq["type"], nq["title"], nq["answer"])
            except HTTPException:
                continue  # 生成的新题不合法直接丢弃, 宁缺毋滥
            q = Question(
                type=nq["type"],
                title=nq["title"],
                options=nq["options"],
                answer=nq["answer"],
                grading_points=nq["grading_points"],
                explanation=nq["explanation"],
                difficulty=nq["difficulty"],
                score=10,
                source="ai",
                category_id=first_category_id(db, "question"),
                creator_id=admin.id,
            )
            db.add(q)
            db.flush()
            question_ids.append(q.id)
            created_new += 1

    if not question_ids:
        raise HTTPException(status_code=502, detail="AI 组卷未命中任何有效题目，请调整需求重试")

    # ---- 确定性兜底: AI 漏项时按题型构成从共享题库补齐 ----
    wanted: dict = {}
    for s in data.specs:
        wanted[s.q_type] = wanted.get(s.q_type, 0) + s.count
    got: dict = {}
    for qid in question_ids:
        q = db.query(Question).filter(Question.id == qid).first()
        if q:
            got[q.type] = got.get(q.type, 0) + 1
    missing_total = 0
    for q_type, need in wanted.items():
        lack = need - got.get(q_type, 0)
        for _ in range(max(0, lack)):
            bank_q = (
                db.query(Question)
                .filter(Question.type == q_type, Question.is_deleted == False, Question.id.notin_(question_ids))  # noqa: E712
                .first()
            )
            if bank_q:
                question_ids.append(bank_q.id)
                got[q_type] = got.get(q_type, 0) + 1
            else:
                missing_total += 1

    title = data.title or (parsed.get("title") if isinstance(parsed, dict) else None) or "AI 智能组卷"
    _has_short = any(s.q_type == "short" for s in data.specs)
    exam = Exam(
        title=title[:200],
        category_id=data.category_id,
        is_timed=data.is_timed,
        time_limit=data.time_limit,
        start_time=data.start_time,
        end_time=data.end_time,
        pass_percent=data.pass_percent,
        status="draft",  # 强制草稿, 必须人工检查后手动上架
        is_ai_auto_grade=_has_short,
        grading_mode=("ai_auto" if _has_short else "manual"),
        creator_id=admin.id,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    for idx, qid in enumerate(question_ids):
        q = db.query(Question).filter(Question.id == qid).first()
        db.add(ExamQuestion(exam_id=exam.id, question_id=qid,
                            score=(q.score if q else 10), sort_order=idx + 1))
    recalc_exam_totals(db, exam)
    db.commit()

    write_audit(db, "generate", "exam", exam.id,
                summary=f"AI 智能组卷《{exam.title}》(草稿, 复用{len(question_ids)-created_new}题/新生成{created_new}题)",
                after_data={"question_ids": question_ids, "status": "draft"}, admin=admin, operator_type="ai")
    push_notification(db, admin.id, "AI 组卷草稿已生成",
                      f"《{exam.title}》已生成草稿（共 {len(question_ids)} 题, 其中 AI 新生成 {created_new} 题），请检查后手动上架。",
                      notif_type="exam_draft", link="/admin/exams")
    db.commit()

    detail_q = db.query(Question).filter(Question.id.in_(question_ids)).all()
    shortage_note = f"，题库不足缺 {missing_total} 题" if missing_total else ""
    return ResponseModel(code=200, message=f"AI 组卷完成：草稿《{exam.title}》共 {len(question_ids)} 题（新生成 {created_new}{shortage_note}），请审核后上架",
                         data={"exam_id": exam.id, "title": exam.title, "question_count": len(question_ids),
                               "new_questions": created_new,
                               "questions": [QuestionResponse.model_validate(q) for q in detail_q]})


# ---------------- AI Copilot (前端状态注入, 后端透传 + SSE 流式) ----------------

def _build_chat_system(admin: Admin):
    """Copilot System Prompt 单一来源 (/chat 与 /chat/stream 共用, 含 Action 协议与精简约束)."""
    role_map = {"super_admin": "超级管理员", "admin": "管理员", "teacher": "出题人", "creator": "出题人", "ai": "AI员工"}
    role_name = role_map.get(admin.role, "未知角色")
    allowed_tools = get_allowed_tools(admin.role)

    system_prompt = f"你是智题库平台的 AI 智能助管, 熟悉题库/组卷/阅卷业务。\n"
    system_prompt += f"当前跟你对话的用户是【{admin.username}】，其在系统中的角色为【{role_name}】。\n"
    system_prompt += "作为系统 AI 助理，你不仅能陪聊，你还可以并且必须使用提供的工具去操作或查询数据库。\n"
    system_prompt += "如果用户询问你能做什么，或者让你帮他操作，你需要查阅你当前的 tools 列表并告知用户你可以做哪些事。不要编造你没有的工具能力。\n"
    system_prompt += "如果用户让你执行越权操作，请礼貌地拒绝并说明这是因为其角色权限不足。\n"
    # v1.2 Step5 Action Card 协议 (与前端 AiAssistantView.vue 联动, 不得破坏已有 Function Calling 链路)
    system_prompt += (
        "【人机协同 Action Card 协议】涉及敏感写操作 (如向出题人划拨 AI 额度、批量入库) 时, "
        "必须在回答末尾附带一个 ```action_card JSON 代码块, 格式: "
        '{"actionType": "TRANSFER_QUOTA", "title": "划拨 AI 额度", "riskLevel": "medium", '
        '"details": [{"label": "目标出题人", "value": "用户名"}, {"label": "划拨数量", "value": "50次"}], '
        '"payload": {"target_username": "对方登录用户名", "amount": 50}}。'
        "用户在前端卡片点击确认后才会真正执行, 你不得直接落库。\n"
    )
    system_prompt += (
        "【交互式操作路由 action_list 协议】当用户询问待办 (如待批阅试卷) 时, 在回答末尾附带一个 "
        "```action_list JSON 代码块, 格式为数组: "
        '[{"title": "试卷名", "badge": "3 份待批改", '
        '"action": {"type": "in_app", "label": "去批改", "target": "open_grading_drawer", "params": {"exam_id": 试卷ID}}}]。'
        "只列出该用户自己名下的试卷 (出题人仅可见自己创建的)。出题人无权触发人员/额度/全局看板动作, 不要为其生成这类卡片。\n"
    )
    system_prompt += (
        "【脱敏与降级】全程自称「AI 智能助管」(或「AI 智算引擎」), 严禁透露底层模型供应商商业名称; "
        "遇到超出题库知识库范畴的问题, 诚实告知超出范畴并给出 3 个业务内推荐提问, 杜绝幻觉编造。\n"
    )
    system_prompt += (
        "【精简约束】回答务必专业精炼、直奔主题, 普通问答长度严格控制在 150-200 字以内, 严禁冗长铺垫。\n"
    )
    system_prompt += (
        "【意图防误触】当用户提出咨询、使用方法类问题 (如“怎么做…”、“如何…”、“介绍…”) 时, "
        "只给操作指引说明, 严禁直接触发 create_question_draft 等创建类工具; "
        "只有用户明确要求“创建/出题/新增/生成题目”时才调用创建类工具。\n"
    )
    system_prompt += (
        "【意图精准分流】\n"
        "1. 当用户要求创建或出一道特定题目时，调用 create_question_draft；\n"
        "2. 当用户要求生成一份试卷/测试卷/多题组卷时，必须调用 create_exam_draft，"
        "并在 questions 参数中一次性原创生成指定题型与数量的完整题目列表，严禁用 create_question_draft 只创建一道题！\n"
    )
    return system_prompt, allowed_tools, role_name


@router.post("/chat")
def ai_chat(
    data: ChatRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """AI 网关: 角色权限继承, 支持 Function Calling"""
    if not ai_service.ai_available():
        raise HTTPException(status_code=400, detail="AI 服务未配置（缺少 SENSENOVA_API_KEY）")
    deduct_quota(db, admin, "chat", {"length": len(data.message)})

    system_prompt, allowed_tools, role_name = _build_chat_system(admin)

    try:
        content, tool_calls = ai_service.chat_completion(
            prompt=data.message[:6000],
            system=system_prompt,
            history=data.history,
            temperature=0.5,
            tools=allowed_tools if allowed_tools else None
        )
        
        if tool_calls:
            # 简化处理，目前只处理第一个工具调用
            tc = tool_calls[0]
            tc_id = tc.get("id")
            func_obj = tc.get("function", {})
            t_name = func_obj.get("name")
            try:
                t_args = json.loads(func_obj.get("arguments", "{}"))
            except:
                t_args = {}
            
            tool_reg = REGISTRY.get(t_name)
            if not tool_reg:
                return ResponseModel(code=200, data={"reply": f"系统错误：未找到工具 {t_name}", "quota_remaining": admin.daily_ai_quota})
            
            risk_level = tool_reg["definition"].risk_level
            if admin.role not in tool_reg["definition"].allowed_roles:
                return ResponseModel(code=200, data={"reply": f"权限拦截：你的角色({role_name})无权使用 {t_name}", "quota_remaining": admin.daily_ai_quota})

            if risk_level == "low":
                # 低风险，直接由网关在后台替 AI 执行，并将结果喂回给大模型进行归纳
                handler = tool_reg["handler"]
                result_data = handler(db, admin, t_args)
                
                # 第二轮对话
                second_history = data.history + [{"role": "user", "content": data.message}]
                second_history.append({
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [tc]
                })
                second_history.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "name": t_name,
                    "content": json.dumps(result_data, ensure_ascii=False)
                })
                
                final_content, _ = ai_service.chat_completion(
                    prompt="",
                    system=system_prompt,
                    history=second_history,
                    temperature=0.5,
                    tools=allowed_tools if allowed_tools else None
                )
                q_remaining = 99999999 if admin.role == "super_admin" else admin.daily_ai_quota
                return ResponseModel(code=200, data={"reply": final_content, "quota_remaining": q_remaining})
            else:
                # 高风险，要求前端显示二次确认卡片
                q_remaining = 99999999 if admin.role == "super_admin" else admin.daily_ai_quota
                return ResponseModel(code=200, data={
                    "type": "action_required",
                    "tool_name": t_name,
                    "arguments": t_args,
                    "tool_call_id": tc_id,
                    "risk_level": tool_reg['definition'].risk_level,
                    "message": f"即将执行{ {'high': '高', 'medium': '中'}.get(tool_reg['definition'].risk_level, '低') }风险操作: {tool_reg['definition'].description}",
                    "quota_remaining": q_remaining
                })

        q_remaining = 99999999 if admin.role == "super_admin" else admin.daily_ai_quota
        return ResponseModel(code=200, data={"reply": content, "quota_remaining": q_remaining})

    except AiServiceError as e:
        raise HTTPException(status_code=502, detail=f"AI 助手暂时不可用: {e}")

@router.post("/chat/stream")
def ai_chat_stream(
    data: ChatRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """SSE 流式对话 (打字机逐字输出) + 流水落库闭环: 事件协议
    - {"type": "delta", "text": "..."} 增量文本
    - {"type": "action_required", ...} 中高风险工具二次确认 (同 /chat 字段)
    - {"type": "done", "quota_remaining": N, "user_message_id": ID, "assistant_message_id": ID} 结束
    - {"type": "error", "message": "..."} 失败
    额度扣减与工具执行语义与 /chat 完全一致；User 提问发起即落库，
    Assistant 全文在生成器结束时随请求会话原子落库 (依赖清理在流结束后才执行，
    与工具执行共用同一会话，天生可测，无测试污染生产库风险)。
    """
    if not ai_service.ai_available():
        raise HTTPException(status_code=400, detail="AI 服务未配置")
    deduct_quota(db, admin, "chat", {"length": len(data.message), "stream": True})

    system_prompt, allowed_tools, role_name = _build_chat_system(admin)
    tools_arg = allowed_tools if allowed_tools else None
    history = data.history or []
    message = data.message[:6000]
    display = (data.display_text or "").strip() or message
    quote = (display[:30] + "…") if len(display) > 30 else display

    # 会话归属解析 (未传自动新建) + User 提问即时落库
    if data.session_id is not None:
        session = _get_owned_session(db, admin, data.session_id)
    else:
        session = AiChatSession(admin_id=admin.id, title="新对话")
        db.add(session)
        db.commit()
        db.refresh(session)
    session_id = session.id
    user_msg = AiChatMessage(session_id=session_id, role="user", content=display)
    db.add(user_msg)
    session.updated_at = datetime.now()
    if session.title == "新对话" and display:
        session.title = display[:15]
    db.commit()
    db.refresh(user_msg)
    user_message_id = user_msg.id
    flow = {"done_persisted": False}

    def _persist_assistant(content: str, card, lst) -> Optional[int]:
        """随请求会话原子落库 Assistant 全文 + 卡片数据 (流结束前依赖不关闭，可测无污染)"""
        try:
            s = db.query(AiChatSession).filter(AiChatSession.id == session_id).first()
            if not s:
                return None
            m = AiChatMessage(
                session_id=session_id, role="assistant",
                content=content or "", quote=quote,
                action_card_data=card, action_list_data=lst,
            )
            db.add(m)
            s.updated_at = datetime.now()
            db.commit()
            db.refresh(m)
            flow["done_persisted"] = True
            return m.id
        except Exception:
            db.rollback()
            return None

    def event_stream():
        def sse(payload: dict) -> str:
            return "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"

        def quota_now() -> int:
            return 99999999 if admin.role == "super_admin" else (admin.daily_ai_quota or 0)

        def run_turn(prompt_text: str, hist: list):
            """流式跑一轮: 转发 delta, 返回 {"failed", "tool_calls", "text"}（返回值驱动，无闭包累加器）。"""
            full_text = ""
            pending_tool_calls: Optional[list] = None
            try:
                for ev in ai_service.chat_completion_stream(
                    prompt=prompt_text, system=system_prompt, history=hist,
                    temperature=0.5, tools=tools_arg,
                ):
                    et = ev.get("type")
                    if et == "delta":
                        piece = ev.get("text", "")
                        full_text += piece
                        yield sse({"type": "delta", "text": piece})
                    elif et == "tool_calls":
                        pending_tool_calls = ev.get("tool_calls")
                    elif et == "error":
                        print(f"[ai_chat_stream] provider error: {ev.get('message')}")
                        yield sse({"type": "error", "message": "AI 助手暂时不可用，请稍后重试"})
                        return {"failed": True, "tool_calls": None, "text": full_text}
            except Exception as e:
                import traceback as _tb
                _tb.print_exc()
                yield sse({"type": "error", "message": "AI 助手暂时不可用，请稍后重试"})
                return {"failed": True, "tool_calls": None, "text": full_text}
            return {"failed": False, "tool_calls": pending_tool_calls, "text": full_text}

        def done_ids(assistant_id: Optional[int]) -> dict:
            return {
                "type": "done", "quota_remaining": quota_now(),
                "user_message_id": user_message_id, "assistant_message_id": assistant_id,
                "session_id": session_id,
            }

        full_first = ""
        full_second = ""
        try:
            res1 = yield from run_turn(message, history)
            full_first = res1["text"]
            if res1["failed"]:
                return
            tool_calls = res1["tool_calls"]
            if tool_calls:
                tc = tool_calls[0]
                tc_id = tc.get("id")
                func_obj = tc.get("function", {})
                t_name = func_obj.get("name")
                try:
                    t_args = json.loads(func_obj.get("arguments", "{}"))
                except Exception:
                    t_args = {}
                tool_reg = REGISTRY.get(t_name)
                if not tool_reg:
                    err_text = f"系统错误：未找到工具 {t_name}"
                    yield sse({"type": "delta", "text": err_text})
                    aid = _persist_assistant(err_text, None, None)
                    yield sse(done_ids(aid))
                    return
                risk_level = tool_reg["definition"].risk_level
                if admin.role not in tool_reg["definition"].allowed_roles:
                    deny_text = f"权限拦截：你的角色({role_name})无权使用 {t_name}"
                    yield sse({"type": "delta", "text": deny_text})
                    aid = _persist_assistant(deny_text, None, None)
                    yield sse(done_ids(aid))
                    return
                if risk_level == "low":
                    result_data = tool_reg["handler"](db, admin, t_args)
                    second_history = history + [{"role": "user", "content": message}]
                    second_history.append({"role": "assistant", "content": "", "tool_calls": [tc]})
                    second_history.append({
                        "role": "tool", "tool_call_id": tc_id, "name": t_name,
                        "content": json.dumps(result_data, ensure_ascii=False),
                    })
                    res2 = yield from run_turn("", second_history)
                    full_second = res2["text"]
                    if res2["failed"]:
                        return
                    # 极少数第二轮又调工具: 直接转文本兜底, 不再递归
                    final_text = res2["text"]
                    if res2["tool_calls"]:
                        fallback = "已获取业务数据，请继续追问细化。"
                        yield sse({"type": "delta", "text": fallback})
                        final_text += fallback
                    # 空包兜底：归纳轮返回空时按工具结果拼装，绝不落空
                    if not final_text.strip():
                        final_text = _format_tool_result_fallback(t_name, result_data)
                        yield sse({"type": "delta", "text": final_text})
                    card2, list2 = _parse_action_blocks(final_text)
                    aid = _persist_assistant(final_text, card2, list2)
                    yield sse(done_ids(aid))
                else:
                    action_msg = f"即将执行{ {'high': '高', 'medium': '中'}.get(tool_reg['definition'].risk_level, '低') }风险操作: {tool_reg['definition'].description}"
                    tool_card = {
                        "kind": "tool",
                        "tool_name": t_name,
                        "arguments": t_args,
                        "tool_call_id": tc_id,
                        "risk_level": tool_reg["definition"].risk_level,
                        "message": action_msg,
                        "status": "pending",
                    }
                    aid = _persist_assistant(action_msg, tool_card, None)
                    yield sse({
                        "type": "action_required",
                        "tool_name": t_name,
                        "arguments": t_args,
                        "tool_call_id": tc_id,
                        "risk_level": tool_reg["definition"].risk_level,
                        "message": action_msg,
                        "quota_remaining": quota_now(),
                        "assistant_message_id": aid,
                    })
                    yield sse(done_ids(aid))
            else:
                card, lst = _parse_action_blocks(full_first)
                if not full_first.strip() and not card and not lst:
                    full_first = "AI 本次未返回有效内容，请换个问法或稍后重试。"
                    yield sse({"type": "delta", "text": full_first})
                aid = _persist_assistant(full_first, card, lst)
                yield sse(done_ids(aid))
        except Exception:
            import traceback as _tb
            _tb.print_exc()
            yield sse({"type": "error", "message": "AI 助手暂时不可用，请稍后重试"})
        finally:
            # 首尾兜底：流被掐断（关页/断网/异常）且正常落库未发生时，把已吐出的半截文本落库，杜绝有问无答
            try:
                if not flow["done_persisted"]:
                    partial = (full_first + full_second).strip()
                    if partial:
                        card, lst = _parse_action_blocks(partial)
                        _persist_assistant(partial, card, lst)
            except Exception:
                pass

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@router.post("/chat/execute_tool")
def ai_chat_execute_tool(
    data: ExecuteToolRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """网关拦截后，人工审批通过的高风险 Tool 执行接口"""
    tool_reg = REGISTRY.get(data.tool_name)
    if not tool_reg:
        raise HTTPException(status_code=400, detail="非法工具")
    
    if admin.role not in tool_reg["definition"].allowed_roles:
        raise HTTPException(status_code=403, detail="越权调用拦截")
        
    handler = tool_reg["handler"]
    result = handler(db, admin, data.arguments)

    # 卡片状态持久化: 执行成功即标 executed, 防刷新/漫游回退导致重复执行
    if data.message_id is not None:
        card_msg = db.query(AiChatMessage).filter(AiChatMessage.id == data.message_id).first()
        if card_msg is not None:
            sess = db.query(AiChatSession).filter(
                AiChatSession.id == card_msg.session_id, AiChatSession.admin_id == admin.id).first()
            if sess is not None and isinstance(card_msg.action_card_data, dict):
                updated = dict(card_msg.action_card_data)
                updated["status"] = "executed"
                card_msg.action_card_data = updated
                db.commit()

    # 写入双重审计日志
    write_audit(db, "execute_tool", "ai_gateway", admin.id,
                summary=f"AI Agent 执行工具: {data.tool_name}",
                after_data={"arguments": data.arguments, "result": result}, admin=admin, operator_type="ai")
    db.commit()
    
    return ResponseModel(code=200, message="操作已执行", data=result)


@router.post("/chat/feedback")
def ai_chat_feedback(
    data: ChatFeedbackRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """大模型回答反馈 (MVP: 纯记录 AuditLog)"""
    # The current write_audit signature: write_audit(db, action, module, user_id, summary, after_data=None, before_data=None, admin=None, operator_type="user")
    write_audit(db, "chat_feedback", "ai_gateway", admin.id,
                summary=f"用户对大模型的回复进行了评价。评价: {'👍 赞' if data.rating == 'up' else '👎 踩'}",
                after_data={
                    "rating": data.rating,
                    "message_snippet": data.message_content[:500]
                }, admin=admin)
    db.commit()
    return ResponseModel(code=200, message="反馈已记录，感谢您的评价！")

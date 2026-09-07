"""
[变更日志]
修改时间：2026-09-06 22:30:00
AI模型：ZCode (GLM)
修改内容：[v1.5 修复用户反馈: AI出题材料指定数量被默认5覆盖(材料数量优先) / 单次生成上限10道(超出截断+提示) /
         v1.2 新增 AI 员工 API: ✨AI出题(预览+二次确认入库)/✨AI智能组卷/AI Copilot/额度资产化/双域审计]
"""
from fastapi import APIRouter, Depends, HTTPException
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
import json

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
    message: str = Field(..., min_length=1, description="老师提问")
    history: Optional[List[dict]] = Field(default=[], description="轻量历史 [{role, content}]")

class ExecuteToolRequest(BaseModel):
    tool_name: str
    arguments: dict
    tool_call_id: str

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
        raw = ai_service.chat_completion(prompt, system=system, json_mode=True)
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
        raw = ai_service.chat_completion(prompt, system=system, json_mode=True, temperature=0.2)
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
    exam = Exam(
        title=title[:200],
        category_id=data.category_id,
        is_timed=data.is_timed,
        time_limit=data.time_limit,
        start_time=data.start_time,
        end_time=data.end_time,
        pass_percent=data.pass_percent,
        status="draft",  # 强制草稿, 必须人工检查后手动上架
        is_ai_auto_grade=any(s.q_type == "short" for s in data.specs),
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


# ---------------- AI Copilot (前端状态注入, 后端纯透传) ----------------

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

    role_map = {"super_admin": "超级管理员", "admin": "管理员", "teacher": "出题人"}
    role_name = role_map.get(admin.role, "未知角色")
    allowed_tools = get_allowed_tools(admin.role)
    
    system_prompt = f"你是智题库平台的 AI 助手, 熟悉题库/组卷/阅卷业务。\n"
    system_prompt += f"当前跟你对话的用户是【{admin.username}】，其在系统中的角色为【{role_name}】。\n"
    system_prompt += "作为系统 AI 助理，你不仅能陪聊，你还可以并且必须使用提供的工具去操作或查询数据库。\n"
    system_prompt += "如果用户询问你能做什么，或者让你帮他操作，你需要查阅你当前的 tools 列表并告知用户你可以做哪些事。不要编造你没有的工具能力。\n"
    system_prompt += "如果用户让你执行越权操作，请礼貌地拒绝并说明这是因为其角色权限不足。\n"

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
                    "message": f"即将执行{ '高' if tool_reg['definition'].risk_level == 'high' else '低' }风险操作: {tool_reg['definition'].description}",
                    "quota_remaining": q_remaining
                })

        q_remaining = 99999999 if admin.role == "super_admin" else admin.daily_ai_quota
        return ResponseModel(code=200, data={"reply": content, "quota_remaining": q_remaining})

    except AiServiceError as e:
        raise HTTPException(status_code=502, detail=f"AI 助手暂时不可用: {e}")

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

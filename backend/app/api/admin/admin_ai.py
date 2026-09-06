"""
[变更日志]
修改时间：2026-09-06 19:20:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 AI 员工 API: ✨AI出题(预览+二次确认入库)/✨AI智能组卷(优先检索题库,不足生成新题,强制Draft)/
         AI Copilot 透传对话(前端状态注入)/额度资产化扣减(主动创造型)/双域审计留痕]
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

router = APIRouter()


# ---------------- 请求体 ----------------

class QuestionGenRequest(BaseModel):
    material: str = Field(..., min_length=5, description="材料文本或自然语言描述")
    count: int = Field(3, ge=1, le=20, description="生成数量")
    q_type: str = Field("single", description="题型 single/multiple/judge/fill/short")
    difficulty: str = Field("medium", description="难度 easy/medium/hard")
    category_id: Optional[int] = Field(None, description="归入分类")

class ExamSpecItem(BaseModel):
    q_type: str = Field(..., description="题型")
    count: int = Field(..., ge=1, le=20, description="数量")
    score: Optional[int] = Field(None, description="每题分值 (默认取题库题目分值或10)")

class ExamGenRequest(BaseModel):
    title: Optional[str] = Field(None, description="试卷标题 (AI 可补全)")
    description: str = Field(..., min_length=5, description="组卷自然语言需求")
    specs: List[ExamSpecItem] = Field(..., description="题型构成要求")
    category_id: Optional[int] = Field(None, description="试卷分类")
    is_timed: bool = Field(True)
    time_limit: int = Field(30)
    pass_percent: int = Field(60)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="老师提问 (前端已注入状态快照前导)")
    history: Optional[List[dict]] = Field(default=[], description="轻量历史 [{role, content}]")


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
    return ResponseModel(code=200, data={
        "available": ai_service.ai_available(),
        "model": cfg["model"],
        "quota_remaining": admin.daily_ai_quota or 0,
        "quota_limit": admin.ai_quota_limit or 0,
    })


# ---------------- ✨ AI 出题 ----------------

QUESTION_JSON_SPEC = """{"questions": [{"type": "single|multiple|judge|fill|short",
 "title": "题干, 填空题用___作空位占位符",
 "options": [{"key": "A", "text": "选项内容"}],
 "answer": 客观题如["A"], 填空题为二维数组如[["北京","北京市"]], 简答题为["参考答案全文"],
 "grading_points": ["简答题踩分点1", "踩分点2"],
 "explanation": "解析", "difficulty": "easy|medium|hard", "score": 10}]}"""

@router.post("/questions/generate")
def ai_generate_questions(
    data: QuestionGenRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """✨AI出题: 生成结构化题目 JSON 供前端预览, 老师二次确认后才调用批量入库 (本接口不写题库)"""
    if not ai_service.ai_available():
        raise HTTPException(status_code=400, detail="AI 服务未配置（缺少 SENSENOVA_API_KEY）")
    deduct_quota(db, admin, "question_gen", {"count": data.count, "q_type": data.q_type})

    system = (
        "你是专业的题库出题专家。根据老师给定的材料或描述出题。只输出 JSON, 格式: " + QUESTION_JSON_SPEC
    )
    prompt = (
        f"请出 {data.count} 道{data.q_type}题, 难度 {data.difficulty}。"
        f"每题 score=10, 带解析。填空题题干中 ___ 的数量必须与 answer 二维数组长度一致; "
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

    # 结构规范化 (不给 AI 越权字段)
    safe_items = []
    for q in questions[:data.count]:
        if not isinstance(q, dict) or not q.get("title"):
            continue
        safe_items.append({
            "type": q.get("type", data.q_type),
            "title": str(q.get("title", "")),
            "options": q.get("options") or [],
            "answer": q.get("answer") or [],
            "grading_points": q.get("grading_points") or [],
            "explanation": str(q.get("explanation", "")),
            "difficulty": q.get("difficulty", data.difficulty),
            "score": 10,
            "category_id": data.category_id,
            "source": "ai",
        })
    if not safe_items:
        raise HTTPException(status_code=502, detail="AI 未生成有效题目，请调整描述后重试")
    return ResponseModel(code=200, message="生成成功，请预览确认后入库", data={"questions": safe_items})


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

    # 题库摘要 (供 AI 检索复用)
    bank = db.query(Question).filter(Question.is_deleted == False).all()  # noqa: E712
    bank_digest = [{"id": q.id, "type": q.type, "title": (q.title or "")[:60], "difficulty": q.difficulty}
                   for q in bank]

    system = (
        "你是智能组卷助理。你会收到: 老师需求、题型构成要求、当前共享题库摘要。"
        "请优先复用题库中的题目 (引用 id); 数量不足或无合适题目时生成新题 (short 题需 grading_points, "
        "fill 题题干用___且数量与 answer 二维数组长度一致)。"
        '只输出 JSON: {"title": "试卷标题", "items": [{"question_id": 题库id} 或 {"new_question": {'
        '"type","title","options","answer","grading_points","explanation","difficulty"}}]}'
    )
    prompt = (
        f"老师需求: {data.description}\n"
        f"题型构成: {[(s.q_type, s.count) for s in data.specs]}\n"
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
            nq = item["new_question"]
            try:
                from app.api.admin.questions import _validate_question_payload
                _validate_question_payload(nq.get("type", "single"), str(nq.get("title", "")), nq.get("answer") or [])
            except HTTPException:
                continue  # 生成的新题不合法直接丢弃, 宁缺毋滥
            q = Question(
                type=nq.get("type", "single"),
                title=str(nq.get("title", "")),
                options=nq.get("options") or [],
                answer=nq.get("answer") or [],
                grading_points=nq.get("grading_points") or [],
                explanation=str(nq.get("explanation", "")),
                difficulty=nq.get("difficulty", "medium"),
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
    return ResponseModel(code=200, message=f"AI 组卷完成：草稿《{exam.title}》共 {len(question_ids)} 题（新生成 {created_new}），请审核后上架",
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
    """AI 助手: 前端把 Pinia 状态快照硬拼在 message 前导, 后端纯透传大模型 (无 RAG/无查表), 扣个人额度"""
    if not ai_service.ai_available():
        raise HTTPException(status_code=400, detail="AI 服务未配置（缺少 SENSENOVA_API_KEY）")
    deduct_quota(db, admin, "chat", {"length": len(data.message)})

    try:
        reply = ai_service.chat_completion(
            data.message[:6000],
            system="你是智题库平台的 AI 助手, 熟悉题库/组卷/阅卷业务。回答简洁专业, 使用中文。",
            temperature=0.5,
        )
    except AiServiceError as e:
        raise HTTPException(status_code=502, detail=f"AI 助手暂时不可用: {e}")

    return ResponseModel(code=200, data={"reply": reply, "quota_remaining": admin.daily_ai_quota})

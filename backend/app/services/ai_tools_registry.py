"""
[变更日志]
修改时间：2026-09-09
AI模型：Gemini 系列
修改内容：[优化 delete_exam 工具: 允许未有人作答(graded=0)的已下架/已归档试卷物理删除，仅拦截正在上架中(published)或已有真实学员作答记录的试卷，彻底打通用户下架后删除试卷的闭环]
修改时间：2026-09-09
AI模型：Gemini 系列
修改内容：[新增 delete_exam 工具及 delete_exam_handler: 严格校验本人权限、未上架草稿(draft)、零人次作答(0记录)，支持通过 ID 或关键词匹配删除试卷并记录审计日志]
修改时间：2026-09-08
AI模型：Gemini 系列
修改内容：[export_my_latest_exam 工具返回数据补充 created_at 格式化创建时间字段，便于仿豆包质感文档卡片展示创建时间]
修改时间：2026-09-08
AI模型：Gemini 系列
修改内容：[澄清 get_my_exams 工具中的 pass_score_percent 字段含义为「及格标准线」，避免大模型将其与学员实际作答「通过率」概念混淆产生误导]
修改时间：2026-09-06 17:35:00
AI模型：Gemini 3.1 Pro
修改内容：[创建 AI 代理网关使用的工具注册表]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[风险三档 low/medium/high: create_question_draft 降为 medium 蓝色轻确认; allowed_roles 补齐 creator(保留 teacher 别名); user_stats creator 合并计数]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[新增 create_exam_draft 组卷工具: questions 一次性原创入库 + 试卷元数据缺省保护 + ExamQuestion 关联]
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.models.user import Admin
from app.models.question import Question
from app.models.exam import Exam, ExamQuestion

class AiToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict
    risk_level: str = "low"  # low(自动执行) / medium(蓝色轻确认卡) / high(红色高危确认卡)
    allowed_roles: List[str] = ["super_admin", "admin", "teacher", "creator"]

def get_database_stats_handler(db: Session, admin: Admin, args: dict) -> dict:
    """获取题库大盘及当前用户个人创建数据统计"""
    from app.models.category import ExamCategory
    total_questions = db.query(Question).filter(Question.is_deleted == False).count()  # noqa: E712
    total_exams = db.query(Exam).count()
    total_categories = db.query(ExamCategory).count()

    # 当前用户个人维度统计
    my_questions = db.query(Question).filter(
        Question.creator_id == admin.id,
        Question.is_deleted == False  # noqa: E712
    ).count()
    my_exams = db.query(Exam).filter(Exam.creator_id == admin.id).count()

    return {
        "current_user": {
            "username": admin.username,
            "role": admin.role,
            "created_questions_count": my_questions,
            "created_exams_count": my_exams
        },
        "global_stats": {
            "total_questions": total_questions,
            "total_exams": total_exams,
            "total_categories": total_categories
        }
    }

def get_user_stats_handler(db: Session, admin: Admin, args: dict) -> dict:
    """获取用户统计数据 (C端用户与管理员)"""
    from app.models.user import User
    from sqlalchemy import func
    
    # 统计C端用户
    total_users = db.query(User).count()
    
    # 统计B端人员角色
    counts = db.query(Admin.role, func.count(Admin.id)).group_by(Admin.role).all()
    stats = {row[0]: row[1] for row in counts}
    
    return {
        "super_admin": stats.get("super_admin", 0),
        "admin": stats.get("admin", 0),
        "creator": stats.get("creator", 0) + stats.get("teacher", 0),
        "c_end_users": total_users,
        "role_distribution": stats
    }


def get_my_exams_handler(db: Session, admin: Admin, args: dict) -> dict:
    """获取我的试卷列表"""
    q = db.query(Exam).filter(Exam.creator_id == admin.id)
    limit = args.get("limit", 10)
    exams = q.order_by(Exam.id.desc()).limit(limit).all()
    return {
        "my_exams": [
            {
                "id": e.id,
                "title": e.title,
                "status": "已发布" if e.status == "published" else ("待上架草稿" if e.status == "draft" else "已下架"),
                "pass_score_line": f"{e.pass_percent or 60}% (试卷及格分数线设定, 非作答通过率)",
                "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S")
            } for e in exams
        ]
    }

def soft_delete_question_handler(db: Session, admin: Admin, args: dict) -> dict:
    """软删除公共题库某道题"""
    q_id = args.get("question_id")
    q = db.query(Question).filter(Question.id == q_id).first()
    if not q:
        return {"error": f"题目 ID {q_id} 不存在"}
    
    # 真正的执行逻辑 (在网关二次确认后调用)
    q.is_deleted = True
    db.commit()
    return {"success": True, "message": f"题目 ID {q_id} 已成功软删除"}

def _normalize_tool_options(raw_options) -> list:
    """工具参数选项归一化 -> [{key, text}]: 兼容 {key,text} / {content,is_correct} / "A. 文本" 三种形状"""
    import re as _re
    opts = []
    for i, o in enumerate(raw_options or []):
        if isinstance(o, dict):
            key = str(o.get("key") or "").strip().upper()
            text = str(o.get("text", o.get("content", "")))
            if not key:
                m = _re.match(r"^\s*([A-F])[\.\、\s]", text)
                key = m.group(1) if m else chr(65 + i)
            opts.append({"key": key, "text": _re.sub(r"^\s*[A-F][\.\、\s]+", "", text).strip() or text})
        else:
            s = str(o)
            m = _re.match(r"^\s*([A-F])[\.\、\s]+(.*)$", s)
            if m:
                opts.append({"key": m.group(1), "text": m.group(2).strip()})
            else:
                opts.append({"key": chr(65 + i), "text": s})
    return opts


def _normalize_tool_answer(q_type: str, raw_answer, norm_options: list) -> list:
    """工具参数答案归一化: 选项题映射为选项 key (文本命中也转 key), 填空/简答保持原文"""
    ans = raw_answer if isinstance(raw_answer, list) else ([raw_answer] if raw_answer else [])
    ans = [str(a).strip() for a in ans if str(a).strip()]
    if q_type in ("single", "multiple", "judge") and norm_options:
        key_by_upper = {o["key"].upper(): o["key"] for o in norm_options}
        text_to_key = {o["text"].strip().upper(): o["key"] for o in norm_options}
        mapped = []
        for a in ans:
            u = a.upper()
            if u in key_by_upper:
                mapped.append(key_by_upper[u])
            elif a.strip().upper() in text_to_key:
                mapped.append(text_to_key[a.strip().upper()])
            else:
                mapped.append(a)
        return mapped
    return ans


def create_question_draft_handler(db: Session, admin: Admin, args: dict) -> dict:
    """创建题目草稿 (AI 工具链路, 入库前已过蓝色确认卡)"""
    from app.models.category import ExamCategory
    from app.services.exam_service import first_category_id, validate_fill_question

    q_type = args.get("type", "single")
    if q_type not in ("single", "multiple", "judge", "fill", "short"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"不支持的题型: {q_type}")
    title = str(args.get("title") or "").strip()
    if not title:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="题干不能为空")
    norm_options = _normalize_tool_options(args.get("options"))
    answer = _normalize_tool_answer(q_type, args.get("answer"), norm_options)
    if not answer:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="必须给出正确答案")
    if q_type == "fill":
        validate_fill_question(title, answer)
    difficulty = args.get("difficulty", "medium")
    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "medium"
    try:
        score = int(args.get("score", 10))
    except (TypeError, ValueError):
        score = 10

    q = Question(
        category_id=first_category_id(db, "question"),
        type=q_type,
        title=title,
        options=norm_options,
        answer=answer,
        explanation=str(args.get("explanation", "")),
        difficulty=difficulty,
        score=score,
        source="ai",
        creator_id=admin.id,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"success": True, "message": f"题目草稿已创建，ID: {q.id}", "question_id": q.id}


def _parse_tool_datetime(val):
    """工具参数时间解析: datetime 或 'YYYY-MM-DDTHH:mm:ss' 字符串, 非法返回 None"""
    from datetime import datetime as _dt
    if val is None:
        return None
    if isinstance(val, _dt):
        return val
    s = str(val).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return _dt.strptime(s, fmt)
        except ValueError:
            continue
    try:
        return _dt.fromisoformat(s)
    except ValueError:
        return None


def create_exam_draft_handler(db: Session, admin: Admin, args: dict) -> dict:
    """整卷组卷草稿 (AI 工具链路): questions 一次性原创入库 + 试卷元数据缺省保护"""
    from datetime import datetime, timedelta
    from fastapi import HTTPException
    from app.models.exam import Exam, ExamQuestion
    from app.services.exam_service import (
        first_category_id, validate_fill_question, validate_exam_window, recalc_exam_totals,
    )

    title = str(args.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="试卷标题不能为空")
    raw_questions = args.get("questions")
    if not isinstance(raw_questions, list) or not raw_questions:
        raise HTTPException(status_code=400, detail="题目列表不能为空，questions 必须一次性给出完整题目")

    # ---- 试卷元数据缺省安全保护 ----
    exam_cat_id = args.get("category_id") or first_category_id(db, "exam")
    start_time = _parse_tool_datetime(args.get("start_time")) or datetime.now()
    end_time = _parse_tool_datetime(args.get("end_time")) or (start_time + timedelta(days=7))
    is_timed = args.get("is_timed", True)
    if not isinstance(is_timed, bool):
        is_timed = True
    try:
        time_limit = int(args.get("time_limit", 30))
    except (TypeError, ValueError):
        time_limit = 30
    grading_mode = args.get("grading_mode", "manual")
    if grading_mode not in ("manual", "ai_pre", "ai_auto"):
        grading_mode = "manual"
    validate_exam_window(time_limit=time_limit, is_timed=is_timed, start_time=start_time, end_time=end_time)

    # ---- questions 逐项归一化校验 ----
    q_cat_id = first_category_id(db, "question")
    normed = []
    for q in raw_questions:
        if not isinstance(q, dict):
            raise HTTPException(status_code=400, detail="题目必须是对象结构")
        q_type = q.get("type", "single")
        if q_type not in ("single", "multiple", "judge", "fill", "short"):
            raise HTTPException(status_code=400, detail=f"不支持的题型: {q_type}")
        q_title = str(q.get("title") or "").strip()
        if not q_title:
            raise HTTPException(status_code=400, detail="题目题干不能为空")
        opts = _normalize_tool_options(q.get("options"))
        ans = _normalize_tool_answer(q_type, q.get("answer"), opts)
        if not ans:
            raise HTTPException(status_code=400, detail=f"题目缺少正确答案: {q_title[:20]}")
        if q_type == "fill":
            validate_fill_question(q_title, ans)
        difficulty = q.get("difficulty", "medium")
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"
        try:
            score = int(q.get("score", 10))
        except (TypeError, ValueError):
            score = 10
        normed.append({
            "type": q_type, "title": q_title, "options": opts, "answer": ans,
            "explanation": str(q.get("explanation", "")), "difficulty": difficulty, "score": score,
        })

    exam = Exam(
        title=title[:200],
        category_id=exam_cat_id,
        is_timed=is_timed,
        time_limit=time_limit,
        start_time=start_time,
        end_time=end_time,
        pass_percent=60,
        status="draft",
        total_score=0,
        pass_score=0,
        is_ai_auto_grade=(grading_mode == "ai_auto"),
        grading_mode=grading_mode,
        creator_id=admin.id,
    )
    db.add(exam)
    db.flush()
    for idx, nq in enumerate(normed):
        qq = Question(
            category_id=q_cat_id,
            type=nq["type"],
            title=nq["title"],
            options=nq["options"],
            answer=nq["answer"],
            explanation=nq["explanation"],
            difficulty=nq["difficulty"],
            score=nq["score"],
            source="ai",
            creator_id=admin.id,
        )
        db.add(qq)
        db.flush()
        db.add(ExamQuestion(exam_id=exam.id, question_id=qq.id, score=nq["score"], sort_order=idx + 1))
    recalc_exam_totals(db, exam)
    db.commit()
    db.refresh(exam)
    return {"success": True, "exam_id": exam.id,
            "message": f"试卷《{title}》草稿已成功创建，共包含 {len(normed)} 道题目，已存入试卷管理。"}

def list_all_exams_handler(db: Session, admin: Admin, args: dict) -> dict:
    """全站试卷列表及出题人归属 (仅超管, 只读)"""
    from app.models.category import ExamCategory
    try:
        limit = int(args.get("limit", 20))
    except (TypeError, ValueError):
        limit = 20
    limit = max(1, min(limit, 50))
    total = db.query(Exam).count()
    exams = db.query(Exam).order_by(Exam.id.desc()).limit(limit).all()
    items = []
    by_category: dict = {}
    for e in exams:
        creator_name = ""
        if e.creator_id:
            creator = db.query(Admin).filter(Admin.id == e.creator_id).first()
            creator_name = creator.username if creator else "未知(账号已删除)"
        category_name = e.category_name or ""
        if not category_name and e.category_id:
            cat = db.query(ExamCategory).filter(ExamCategory.id == e.category_id).first()
            category_name = cat.name if cat else ""
        category_name = category_name or "未分类"
        by_category[category_name] = by_category.get(category_name, 0) + 1
        q_count = db.query(ExamQuestion).filter(ExamQuestion.exam_id == e.id).count()
        items.append({
            "id": e.id,
            "title": e.title,
            "status": e.status,
            "category": category_name,
            "creator": creator_name or "未知(历史数据)",
            "question_count": q_count,
            "total_score": e.total_score,
        })
    return {"total": total, "by_category": by_category, "exams": items}


def export_my_latest_exam_handler(db: Session, admin: Admin, args: dict) -> dict:
    """获取用户最近创建的一份试卷并生成导出下载信息"""
    keyword = str(args.get("keyword") or "").strip()
    q = db.query(Exam).filter(Exam.creator_id == admin.id)
    if keyword:
        q = q.filter(Exam.title.contains(keyword))
    exam = q.order_by(Exam.id.desc()).first()
    if not exam:
        return {"found": False, "message": "未找到您名下的试卷，请先创建试卷。"}
    q_count = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).count()
    download_url = f"/api/v1/admin/exams/{exam.id}/export"
    created_time_str = exam.created_at.strftime("%m-%d %H:%M") if exam.created_at else ""
    return {
        "found": True,
        "exam_id": exam.id,
        "title": exam.title,
        "total_score": exam.total_score or 100,
        "pass_percent": exam.pass_percent or 60,
        "question_count": q_count,
        "download_url": download_url,
        "created_at": created_time_str,
        "message": f"已找到您最近创建的试卷《{exam.title}》（共 {q_count} 题，总分 {exam.total_score or 100} 分），可直接下载格式化试卷文件。"
    }


def get_my_questions_pass_rate_handler(db: Session, admin: Admin, args: dict) -> dict:
    """统计当前管理员在指定时间窗口内出过的试卷/试题的作答通过率"""
    from datetime import datetime, timedelta
    from app.models.record import ExamRecord
    days = int(args.get("days", 7))
    days = max(1, min(days, 90))
    since_date = datetime.now() - timedelta(days=days)

    # 查找该老师创建的试卷
    my_exams = db.query(Exam).filter(
        Exam.creator_id == admin.id,
        Exam.created_at >= since_date
    ).all()
    exam_ids = [e.id for e in my_exams]

    if not exam_ids:
        # 如果最近N天没有出新试卷，统计其所有已出试卷在最近N天内的答卷情况
        all_my_exams = db.query(Exam).filter(Exam.creator_id == admin.id).all()
        exam_ids = [e.id for e in all_my_exams]

    if not exam_ids:
        return {
            "period_days": days,
            "total_exams": 0,
            "total_records": 0,
            "pass_count": 0,
            "pass_rate": "0.0%",
            "message": f"最近 {days} 天内未检索到您创建的试卷或答卷记录。"
        }

    # 查询这些试卷在指定时间段内的答卷记录
    records = db.query(ExamRecord).filter(
        ExamRecord.exam_id.in_(exam_ids),
        ExamRecord.status == "submitted",
        ExamRecord.submit_time >= since_date
    ).all()

    total_records = len(records)
    pass_count = sum(1 for r in records if r.passed)
    pass_rate = (pass_count / total_records * 100) if total_records > 0 else 0.0

    return {
        "period_days": days,
        "exams_count": len(exam_ids),
        "total_records": total_records,
        "pass_count": pass_count,
        "pass_rate": f"{pass_rate:.1f}%",
        "average_score": round(sum(r.score or 0 for r in records) / total_records, 1) if total_records > 0 else 0,
        "message": f"统计结果：最近 {days} 天内，您名下的 {len(exam_ids)} 套试卷共有 {total_records} 人次提交作答，其中及格 {pass_count} 人次，整体通过率为 {pass_rate:.1f}%。"
    }


def delete_exam_handler(db: Session, admin: Admin, args: dict) -> dict:
    """删除单份试卷（执行前需人工确认卡，严格遵循：本人名下、未上架草稿 draft、零人次作答）"""
    from fastapi import HTTPException
    from app.models.record import ExamRecord
    from app.services.audit_service import write_audit

    exam_id = args.get("exam_id")
    keyword = str(args.get("keyword") or "").strip()

    exam = None
    if exam_id:
        try:
            eid = int(exam_id)
            exam = db.query(Exam).filter(Exam.id == eid).first()
        except (ValueError, TypeError):
            exam = None
    elif keyword:
        # 关键词优先匹配自己名下的试卷
        exam = db.query(Exam).filter(
            Exam.creator_id == admin.id,
            Exam.title.contains(keyword)
        ).order_by(Exam.id.desc()).first()
    else:
        # 未指定 ID 也未指定关键词，默认匹配自己名下最近创建的一份试卷
        exam = db.query(Exam).filter(Exam.creator_id == admin.id).order_by(Exam.id.desc()).first()

    if not exam:
        raise HTTPException(status_code=404, detail="未检索到符合条件的试卷，请核对试卷名称或ID")

    # 1. 权限校验：必须是本人出的试卷（超管除外）
    if exam.creator_id != admin.id and admin.role != "super_admin":
        raise HTTPException(status_code=403, detail="您无权删除他人创建的试卷，仅支持删除您名下的试卷")

    # 2. 上架状态校验：若正在发布中，提示先下架
    if exam.status == "published":
        raise HTTPException(status_code=400, detail=f"试卷《{exam.title}》处于已上架状态，不可直接删除；请先在试卷管理列表中将其下架，然后再点删除。")

    # 3. 答卷作答记录校验：有人做过绝不能物理删除
    graded = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam.id,
        ExamRecord.status.in_(["submitted", "timeout", "pending_grading"])
    ).count()
    if graded > 0:
        raise HTTPException(status_code=400, detail=f"试卷《{exam.title}》已有 {graded} 人次学员作答，为保护学员考试数据不可删除，仅可保持下架归档。")

    # 4. 清理无意义的未提交幽灵记录后执行物理删除
    db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam.id,
        ExamRecord.status == "in_progress"
    ).delete()
    
    # 清理试卷试题关联
    db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).delete()

    title = exam.title
    deleted_id = exam.id
    db.delete(exam)
    db.commit()

    write_audit(db, "delete", "exam", deleted_id, summary=f"AI助管删除试卷《{title}》",
                before_data={"title": title, "exam_id": deleted_id}, admin=admin)
    db.commit()

    return {
        "success": True,
        "deleted_exam_id": deleted_id,
        "title": title,
        "message": f"试卷《{title}》（ID: {deleted_id}）已成功删除。"
    }

# ================= 工具注册表 =================

REGISTRY: Dict[str, dict] = {
    "get_database_stats": {
        "definition": AiToolDefinition(
            name="get_database_stats",
            description="查询系统全局题库/试卷/分类数量，同时返回当前用户个人创建的题目数与试卷数。当用户询问宏观统计、“我创建了几道题”、“我的业务统计”时调用此工具。",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin", "admin", "teacher", "creator"]
        ),
        "handler": get_database_stats_handler
    },
    "get_my_exams": {
        "definition": AiToolDefinition(
            name="get_my_exams",
            description="获取当前登录用户（我自己）创建的试卷列表（包含试卷标题、发布状态、及格标准分数线 pass_score_line 等信息，注意：pass_score_line 是试卷配置的及格线如60%，绝对不是学员做题的通过率！未有人作答时没有通过率）。当用户询问自己出过/创建过哪些试卷时调用。",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "需要返回的试卷数量上限，默认10"
                    }
                },
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin", "admin", "teacher", "creator"]
        ),
        "handler": get_my_exams_handler
    },
    "soft_delete_question": {
        "definition": AiToolDefinition(
            name="soft_delete_question",
            description="软删除公共题库中的某道题目。当用户明确要求删除某个具体 ID 的题目时调用。",
            parameters={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "integer",
                        "description": "要删除的题目 ID"
                    }
                },
                "required": ["question_id"]
            },
            risk_level="high",
            allowed_roles=["super_admin", "admin"]
        ),
        "handler": soft_delete_question_handler
    },
    "create_question_draft": {
        "definition": AiToolDefinition(
            name="create_question_draft",
            description="创建一道新的题目。当用户要求新增或创建特定题目时调用。",
            parameters={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["single", "multiple", "judge", "fill", "short"]},
                    "title": {"type": "string", "description": "题干内容"},
                    "options": {"type": "array", "items": {"type": "object"}},
                    "answer": {"type": "array", "items": {"type": "string"}},
                    "explanation": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                    "score": {"type": "integer"}
                },
                "required": ["type", "title", "answer"]
            },
            risk_level="medium",
            allowed_roles=["super_admin", "admin", "teacher", "creator"]
        ),
        "handler": create_question_draft_handler
    },
    "create_exam_draft": {
        "definition": AiToolDefinition(
            name="create_exam_draft",
            description="当用户明确要求生成整份试卷/测试卷/模拟卷/综合测验，或要求包含多种题型构成的试卷时调用此工具。必须在 questions 参数中一次性原创生成指定题型与数量的完整题目列表。",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "试卷标题，如'消防安全知识测试卷'"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"], "description": "试卷难度"},
                    "questions": {
                        "type": "array",
                        "description": "按用户要求生成的全量题目列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["single", "multiple", "judge", "fill", "short"]},
                                "title": {"type": "string", "description": "题干"},
                                "options": {
                                    "type": "array",
                                    "items": {"type": "object", "properties": {"key": {"type": "string"}, "text": {"type": "string"}}}
                                },
                                "answer": {"type": "array", "items": {"type": "string"}},
                                "explanation": {"type": "string"},
                                "score": {"type": "integer"}
                            },
                            "required": ["type", "title", "answer"]
                        }
                    }
                },
                "required": ["title", "questions"]
            },
            risk_level="medium",
            allowed_roles=["super_admin", "admin", "teacher", "creator"]
        ),
        "handler": create_exam_draft_handler
    },
    "get_user_stats": {
        "definition": AiToolDefinition(
            name="get_user_stats",
            description="查询系统用户大盘数据，包括C端用户、管理员、出题人的数量分布。当用户询问用户统计时调用。",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin"]
        ),
        "handler": get_user_stats_handler
    },
    "list_all_exams": {
        "definition": AiToolDefinition(
            name="list_all_exams",
            description="仅超管可用：查询全站所有试卷及其分类、出题人归属（标题/分类/状态/出题人/题数/总分，附 by_category 按分类汇总）。当超级管理员询问全站有哪些试卷、都是什么类型/分类、都是谁出的、各卷归属时调用此工具，分类统计直接读 by_category。",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "返回数量上限，默认20，最大50"}
                },
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin"]
        ),
        "handler": list_all_exams_handler
    },
    "export_my_latest_exam": {
        "definition": AiToolDefinition(
            name="export_my_latest_exam",
            description="查询并导出当前老师名下最近创建的一份试卷（支持按关键词筛选标题）。当用户要求“给我导出最近我出的一份试卷”、“下载最近出的试卷”、“导出某某试卷”时必须调用此工具。",
            parameters={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "试卷标题关键词，未指定则留空直接取最近一份"}
                },
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin", "admin", "teacher", "creator"]
        ),
        "handler": export_my_latest_exam_handler
    },
    "get_my_questions_pass_rate": {
        "definition": AiToolDefinition(
            name="get_my_questions_pass_rate",
            description="统计当前老师在指定天数内出过的试卷/试题的作答及格率与通过率。当用户询问“统计最近我一周出过的试题通过率”、“我出的题通过率怎么样”、“统计最近答卷情况”时调用此工具。",
            parameters={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "统计过去多少天内，默认 7 天"}
                },
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin", "admin", "teacher", "creator"]
        ),
        "handler": get_my_questions_pass_rate_handler
    },
    "delete_exam": {
        "definition": AiToolDefinition(
            name="delete_exam",
            description="删除当前老师自己创建的名下某份试卷。满足业务安全约束：试卷必须是本人创建、处于未上架或已下架状态(非已上架published)、且没有任何学员作答记录(0人次作答)。当用户表达“我想删除这份试卷”、“帮我删除某某试卷”、“删除刚建的试卷”等单张试卷删除意图时调用此工具。",
            parameters={
                "type": "object",
                "properties": {
                    "exam_id": {
                        "type": "integer",
                        "description": "要删除的试卷ID（可选，与 keyword 二选一）"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "试卷标题关键词，用于模糊匹配名下试卷（可选，若未指定ID与关键词则默认取名下最近一份试卷）"
                    }
                },
                "required": []
            },
            risk_level="medium",
            allowed_roles=["super_admin", "admin", "teacher", "creator"]
        ),
        "handler": delete_exam_handler
    },
}


def get_allowed_tools(role: str) -> List[dict]:
    """根据角色获取其被允许使用的工具定义列表 (符合 OpenAI Tools Schema)"""
    tools = []
    for tool_name, tool_data in REGISTRY.items():
        definition: AiToolDefinition = tool_data["definition"]
        if role in definition.allowed_roles:
            tools.append({
                "type": "function",
                "function": {
                    "name": definition.name,
                    "description": definition.description,
                    "parameters": definition.parameters
                }
            })
    return tools

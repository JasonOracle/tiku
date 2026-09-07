"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 AI 阅卷调度器: 原子化 Prompt 单次请求批阅整卷简答题, 动态满分(exam_questions.score), 全托管/预批改双模式, 失败回退人工大厅]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[v1.2 Step2: 全托管判定改走 exam_grading_mode(grading_mode 为准, 兼容历史开关)]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[致命修复: chat_completion 返回元组需解包 (AI 阅卷生产 500 根因)]
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.exam import Exam, ExamQuestion, exam_grading_mode
from app.models.question import Question
from app.models.record import ExamRecord
from app.models.user import Admin
from app.services import ai_service
from app.services.ai_service import AiServiceError
from app.services.exam_service import finalize_record
from app.services.quota_service import log_system_usage
from app.services.audit_service import write_audit, push_notification

GRADING_SYSTEM_PROMPT = (
    "你是一名严格、公正的主观题阅卷老师。你会收到试卷的多道简答题, "
    "每题包含: 题干、标准答案、踩分点、该题满分、学生作答原文。"
    "请逐题按点给分: 踩中要点或语义等价即给对应分, 部分踩中给部分分, 完全不符给 0 分。"
    "最终只输出一个 JSON 对象, 格式: "
    '{"results": [{"question_id": 整数, "score": 整数(0~该题满分), "comment": "简短中文评语"}]}。'
    "不得输出 JSON 以外的任何文字。"
)


def build_grading_prompt(short_items: list) -> str:
    """将整卷所有简答题合并拼装为一个大 JSON Prompt (原子化: 单次请求, 同成功同失败)"""
    payload = []
    for it in short_items:
        payload.append({
            "question_id": it["question_id"],
            "title": it["title"],
            "reference_answer": it["reference_answer"],
            "grading_points": it["grading_points"],
            "full_score": it["full_score"],
            "student_answer": it["student_answer"],
        })
    import json
    return (
        "以下是学生答卷中的全部简答题, 请逐题批阅并按格式输出 JSON:\n"
        + json.dumps(payload, ensure_ascii=False, indent=1)
    )


def collect_short_items(db: Session, record: ExamRecord) -> list:
    """提取该答卷全部简答题批阅要素 (动态满分: 取组卷时的 exam_questions.score)"""
    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == record.exam_id).all()
    items = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id, Question.type == "short").first()
        if not q:
            continue
        items.append({
            "question_id": q.id,
            "title": q.title,
            "reference_answer": "; ".join(q.answer or []) if isinstance(q.answer, list) else str(q.answer or ""),
            "grading_points": q.grading_points or [],
            "full_score": eq.score or q.score or 10,
            "student_answer": "\n".join((record.user_answers or {}).get(str(q.id), [])) or "(未作答)",
        })
    return items


def run_ai_grading(record_id: int, db: Optional[Session] = None) -> Optional[ExamRecord]:
    """AI 批阅入口 (BackgroundTasks 后台执行)。
    - 成功 + grading_mode == 'ai_auto': 直接终算发布成绩
    - 成功 + 'ai_pre': 仅写建议分数, 留给老师复核
    - 任何失败: 写入 error 信息, 记录留在 pending_grading 交人工大厅兜底
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        return _run(db, record_id)
    finally:
        if own_session:
            db.close()


def _run(db: Session, record_id: int) -> Optional[ExamRecord]:
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record or record.status != "pending_grading":
        return None

    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    if not exam:
        return None

    short_items = collect_short_items(db, record)
    if not short_items:
        # 无简答题却处于待批阅 (如历史数据), 直接终算兜底
        finalize_record(db, record, short_scores={})
        return record

    try:
        raw, _ = ai_service.chat_completion(
            build_grading_prompt(short_items),
            system=GRADING_SYSTEM_PROMPT,
            json_mode=True,
        )
        parsed = ai_service.extract_json(raw)
        results = parsed.get("results") if isinstance(parsed, dict) else parsed
        if not isinstance(results, list):
            raise AiServiceError("JSON 结构不符 (缺少 results 数组)")

        suggestions = []
        short_scores = {}
        full_map = {it["question_id"]: it["full_score"] for it in short_items}
        for r in results:
            qid = int(r.get("question_id"))
            if qid not in full_map:
                continue
            score = max(0, min(int(r.get("score", 0)), full_map[qid]))
            comment = str(r.get("comment", ""))[:200]
            suggestions.append({"question_id": qid, "suggested_score": score, "comment": comment})
            short_scores[str(qid)] = score

        # 缺漏的简答题按 0 分补齐, 保证原子完整性
        for it in short_items:
            if str(it["question_id"]) not in short_scores:
                short_scores[str(it["question_id"])] = 0
                suggestions.append({"question_id": it["question_id"], "suggested_score": 0, "comment": "AI未返回该题评分，默认0分，请人工复核"})

        record.ai_grading_result = {"suggestions": suggestions, "error": None, "graded_at": datetime.now().isoformat(sep=" ", timespec="seconds")}
        log_system_usage(db, "grading", {"record_id": record.id, "exam_id": exam.id, "short_count": len(short_items)})

        if exam_grading_mode(exam) == "ai_auto":
            finalize_record(db, record, short_scores=short_scores)
            write_audit(db, "grade", "record", record.id,
                        summary=f"AI 全托管批阅并发布成绩: 记录#{record.id} 得分{record.score}",
                        after_data={"short_scores": short_scores, "operator": "ai"}, operator_type="ai")
            if exam.creator_id:
                push_notification(db, exam.creator_id, "AI 全托管批阅完成",
                                  f"《{exam.title}》答卷 #{record.id} 已由 AI 批阅完毕并自动发布成绩（{record.score} 分）。",
                                  notif_type="grading", link="/admin/grading")
            db.commit()
        else:
            db.commit()
            if exam.creator_id:
                push_notification(db, exam.creator_id, "AI 预批改完成，待复核",
                                  f"《{exam.title}》答卷 #{record.id} 的 {len(short_items)} 道简答题已由 AI 预批改，请前往阅卷大厅复核。",
                                  notif_type="grading", link="/admin/grading")
        return record

    except (AiServiceError, ValueError, TypeError) as e:
        db.rollback()
        record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
        if record and record.status == "pending_grading":
            record.ai_grading_result = {
                "suggestions": [], "error": str(e)[:500],
                "graded_at": datetime.now().isoformat(sep=" ", timespec="seconds"),
            }
            log_system_usage(db, "grading", {"record_id": record.id, "exam_id": record.exam_id, "failed": True})
            db.commit()
            exam2 = db.query(Exam).filter(Exam.id == record.exam_id).first()
            if exam2 and exam2.creator_id:
                push_notification(db, exam2.creator_id, "AI 批阅异常，请人工接管",
                                  f"《{exam2.title}》答卷 #{record.id} AI 批阅失败：{str(e)[:120]}。可在阅卷大厅人工批改或重新触发 AI。",
                                  notif_type="ai_error", link="/admin/grading")
        return record

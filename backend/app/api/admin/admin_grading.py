"""
[变更日志]
修改时间：2026-09-06 19:00:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增阅卷大厅 API: 待批阅列表(红点联动)/批阅详情(踩分点+学生原文+AI建议)/人工确认发布/
         一键采信全部AI评分/重新触发AI。RBAC: 老师仅批改自己创建的试卷]
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin, User
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.models.record import ExamRecord
from app.schemas.common import ResponseModel, PageResponse
from app.services.exam_service import (
    evaluate_submission, finalize_record, close_expired_window_records,
)
from app.services.ai_grading import run_ai_grading, collect_short_items
from app.services import ai_service
from app.services.audit_service import write_audit

router = APIRouter()


class GradeConfirmRequest(BaseModel):
    accept_ai: bool = Field(False, description="一键采信全部 AI 评分")
    scores: Dict[str, int] = Field(default={}, description="简答题定分 {question_id: score} (accept_ai=false 时必填)")


def _owned_exam(db: Session, admin: Admin, exam: Exam) -> None:
    if admin.role != "super_admin" and exam.creator_id not in (admin.id, None):
        raise HTTPException(status_code=403, detail="无权批改他人创建的试卷")


@router.get("/records", response_model=ResponseModel[PageResponse[dict]])
def list_pending_records(
    exam_id: Optional[int] = Query(None),
    only_error: bool = Query(False, description="仅看 AI 批阅异常的答卷"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """阅卷大厅列表: pending_grading 答卷 (进入时顺手惰性收卷已超 end_time 的僵尸卷)"""
    close_expired_window_records(db, exam_id=exam_id)

    query = db.query(ExamRecord).filter(ExamRecord.status == "pending_grading")
    exam_ids_owned = None
    if admin.role != "super_admin":
        owned = [e.id for e in db.query(Exam).filter(
            (Exam.creator_id == admin.id) | (Exam.creator_id.is_(None))).all()]
        exam_ids_owned = owned or [-1]
        query = query.filter(ExamRecord.exam_id.in_(exam_ids_owned))
    if exam_id:
        query = query.filter(ExamRecord.exam_id == exam_id)

    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages
    records = query.order_by(ExamRecord.submit_time.asc()).offset((page - 1) * size).limit(size).all()

    items = []
    for r in records:
        exam = db.query(Exam).filter(Exam.id == r.exam_id).first()
        if not exam:
            continue
        if exam_id is None and admin.role != "super_admin" and exam.creator_id not in (admin.id, None):
            continue
        u = db.query(User).filter(User.id == r.user_id).first()
        ai_result = r.ai_grading_result or {}
        suggestions = ai_result.get("suggestions") or []
        eval_ = evaluate_submission(db, exam, r.user_answers or {})
        items.append({
            "record_id": r.id,
            "exam_id": exam.id,
            "exam_title": exam.title,
            "username": u.username if u else f"用户#{r.user_id}",
            "submit_time": r.submit_time.strftime("%Y-%m-%d %H:%M:%S") if r.submit_time else "",
            "short_count": sum(1 for it in eval_["items"] if it["question"].type == "short"),
            "objective_score": eval_["total_score"],
            "has_ai_suggestion": bool(suggestions),
            "ai_error": ai_result.get("error"),
            "is_ai_auto": exam.is_ai_auto_grade,
        })

    if only_error:
        items = [it for it in items if it["ai_error"]]
        total = len(items)
        total_pages = 1 if total else 0
        has_next = False

    return ResponseModel(code=200, data=PageResponse(
        total=total, page=page, size=size, total_pages=total_pages, has_next=has_next, items=items
    ))


@router.get("/records/{record_id}", response_model=ResponseModel[dict])
def get_grading_detail(
    record_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """批阅详情: 全卷题目 + 简答题(踩分点/标准答案/学生原文/AI建议分/评语)"""
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="答卷不存在")
    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="关联试卷不存在")
    _owned_exam(db, admin, exam)

    u = db.query(User).filter(User.id == record.user_id).first()
    ai_result = record.ai_grading_result or {}
    suggestion_map = {str(s.get("question_id")): s for s in (ai_result.get("suggestions") or [])}
    final_scores = record.short_scores or {}

    eval_ = evaluate_submission(db, exam, record.user_answers or {}, short_scores=final_scores if record.status == "submitted" else None)

    questions = []
    for it in eval_["items"]:
        q = it["question"]
        entry: Dict[str, Any] = {
            "question_id": q.id,
            "type": q.type,
            "title": q.title,
            "eq_score": it["eq_score"],
            "user_answer": it["user_answer"],
            "gained": it["gained"] if record.status == "submitted" else None,
            "is_correct": it["is_correct"] if record.status == "submitted" else None,
            "is_partial": it["is_partial"],
        }
        if q.type == "short":
            sug = suggestion_map.get(str(q.id), {})
            entry.update({
                "reference_answer": "; ".join(q.answer or []) if isinstance(q.answer, list) else str(q.answer or ""),
                "grading_points": q.grading_points or [],
                "ai_suggested_score": sug.get("suggested_score"),
                "ai_comment": sug.get("comment", ""),
                "final_score": (final_scores or {}).get(str(q.id)),
            })
        questions.append(entry)

    return ResponseModel(code=200, data={
        "record_id": record.id,
        "status": record.status,
        "exam_id": exam.id,
        "exam_title": exam.title,
        "username": u.username if u else f"用户#{record.user_id}",
        "total_score": exam.total_score,
        "pass_score": exam.pass_score,
        "objective_score": eval_["total_score"],
        "ai_error": ai_result.get("error"),
        "questions": questions,
    })


@router.post("/records/{record_id}/confirm", response_model=ResponseModel[dict])
def confirm_grading(
    record_id: int,
    data: GradeConfirmRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """老师定分确认 → 终算并发布成绩 (可一键采信全部 AI 评分)"""
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="答卷不存在")
    if record.status != "pending_grading":
        raise HTTPException(status_code=400, detail="该答卷不在待批阅状态")
    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="关联试卷不存在")
    _owned_exam(db, admin, exam)

    short_items = collect_short_items(db, record)
    full_map = {it["question_id"]: it["full_score"] for it in short_items}

    if data.accept_ai:
        suggestion_map = {str(s.get("question_id")): s.get("suggested_score", 0)
                          for s in ((record.ai_grading_result or {}).get("suggestions") or [])}
        if not suggestion_map:
            raise HTTPException(status_code=400, detail="暂无 AI 预批改结果，请手动评分或先触发 AI 批改")
        scores = suggestion_map
    else:
        scores = {str(k): v for k, v in (data.scores or {}).items()}
        missing = [str(qid) for qid in full_map if str(qid) not in scores]
        if missing:
            raise HTTPException(status_code=400, detail=f"还有 {len(missing)} 道简答题未定分，请完成评分后再发布")

    for qid, sc in scores.items():
        qid_int = int(qid)
        if qid_int in full_map:
            scores[qid] = max(0, min(int(sc), full_map[qid_int]))

    finalize_record(db, record, short_scores=scores)
    write_audit(db, "grade", "record", record.id,
                summary=f"批阅发布: 《{exam.title}》答卷#{record.id} 最终得分 {record.score}",
                after_data={"short_scores": scores, "accept_ai": data.accept_ai}, admin=admin)
    db.commit()
    return ResponseModel(code=200, message=f"成绩已发布：{record.score} 分", data={
        "record_id": record.id, "score": record.score, "passed": record.passed,
    })


@router.post("/records/{record_id}/retry-ai", response_model=ResponseModel[dict])
def retry_ai_grading(
    record_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """重新触发 AI 批改 (AI 宕机兜底: 老师可在异常红点处手动重试)"""
    record = db.query(ExamRecord).filter(ExamRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="答卷不存在")
    if record.status != "pending_grading":
        raise HTTPException(status_code=400, detail="该答卷不在待批阅状态")
    exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="关联试卷不存在")
    _owned_exam(db, admin, exam)

    if not ai_service.ai_available():
        raise HTTPException(status_code=400, detail="AI 服务未配置（缺少 SENSENOVA_API_KEY），请人工批改")

    record.ai_grading_result = None
    db.commit()
    background_tasks.add_task(run_ai_grading, record.id)
    return ResponseModel(code=200, message="已重新触发 AI 批改，请稍后刷新查看", data={"record_id": record.id})

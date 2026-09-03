"""
[变更日志]
修改时间：2026-09-03 23:36:00
AI模型：Gemini 底层
修改内容：[1. 试卷根据绑定的题目 score 自动计算 total_score; 2. 结合 pass_percent 自动计算向上取整的及格分 pass_score; 3. 支持绑定 question_ids]
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
import math
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.exam import Exam, ExamQuestion
from app.models.question import Question
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse, ExamDetailResponse
from app.schemas.question import QuestionResponse
from app.schemas.common import ResponseModel, PageResponse

router = APIRouter()

@router.get("", response_model=ResponseModel[PageResponse[ExamResponse]])
def list_admin_exams(
    category_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端试卷列表查询"""
    query = db.query(Exam)
    if category_id:
        query = query.filter(Exam.category_id == category_id)
    if keyword:
        query = query.filter(Exam.title.like(f"%{keyword}%"))

    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    exams = query.order_by(Exam.id.desc()).offset((page - 1) * size).limit(size).all()
    
    result_items = []
    for exam in exams:
        count = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).count()
        item = ExamResponse.model_validate(exam)
        item.question_count = count
        result_items.append(item)

    return ResponseModel(
        code=200,
        data=PageResponse(
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            items=result_items
        )
    )

@router.post("", response_model=ResponseModel[ExamDetailResponse], status_code=status.HTTP_201_CREATED)
def create_exam(
    data: ExamCreate, 
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端创建试卷与进行关联组卷"""
    exam = Exam(
        title=data.title,
        category_id=data.category_id,
        cover_url=data.cover_url,
        is_timed=data.is_timed,
        time_limit=data.time_limit,
        pass_percent=data.pass_percent,
        status=data.status or "draft",
        total_score=0,
        pass_score=0,
        is_recommended=data.is_recommended
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    # 确定关联题目的ID列表
    target_q_ids = []
    if data.question_ids:
        target_q_ids = data.question_ids
    elif data.questions:
        target_q_ids = [q.question_id for q in data.questions]

    calculated_total_score = 0
    if target_q_ids:
        for idx, q_id in enumerate(target_q_ids):
            q_obj = db.query(Question).filter(Question.id == q_id).first()
            score_val = q_obj.score if q_obj else 10
            calculated_total_score += score_val
            eq = ExamQuestion(
                exam_id=exam.id,
                question_id=q_id,
                score=score_val,
                sort_order=idx + 1
            )
            db.add(eq)

    # 更新自动计算出的总分与及格分
    pass_percent = data.pass_percent if data.pass_percent is not None else 60
    calculated_pass_score = math.ceil(calculated_total_score * pass_percent / 100.0)

    exam.total_score = calculated_total_score
    exam.pass_score = calculated_pass_score
    # 直接上架创建：校验分类并写入快照
    if (exam.status or "draft") == "published":
        from app.services.exam_service import ensure_publishable
        ensure_publishable(db, exam)
    db.commit()
    db.refresh(exam)

    # 查询详情返回
    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.sort_order).all()
    questions = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            questions.append(QuestionResponse.model_validate(q))

    detail = ExamDetailResponse.model_validate(exam)
    detail.question_count = len(questions)
    detail.questions = questions

    return ResponseModel(code=201, message="创建试卷成功", data=detail)

@router.put("/{exam_id}/status", response_model=ResponseModel[dict])
def update_exam_status(
    exam_id: int,
    status_val: str = Query(..., alias="status", description="新状态: draft, published, archived"),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端切换试卷上下架状态（归档为终态，上架需分类并写快照）"""
    from app.services.exam_service import ensure_publishable
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    if status_val not in ["draft", "published", "archived"]:
        raise HTTPException(status_code=400, detail="无效的状态参数")

    if exam.status == "archived":
        raise HTTPException(status_code=400, detail="该试卷已归档冻结，不可变更状态")
    if status_val == "published":
        ensure_publishable(db, exam)

    exam.status = status_val
    db.commit()
    return ResponseModel(code=200, message=f"试卷状态已更新为 {status_val}", data={"id": exam_id, "status": status_val})


@router.get("/{exam_id}", response_model=ResponseModel[ExamDetailResponse])
def get_admin_exam_detail(
    exam_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取试卷详情（含草稿/已下架，不受 published 隔离限制）"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.sort_order).all()
    questions = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            questions.append(QuestionResponse.model_validate(q))

    detail = ExamDetailResponse.model_validate(exam)
    detail.question_count = len(questions)
    detail.questions = questions
    return ResponseModel(code=200, data=detail)


@router.put("/{exam_id}", response_model=ResponseModel[ExamDetailResponse])
def update_exam(
    exam_id: int,
    data: ExamUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端修改编辑试卷配置与重新组卷"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    update_dict = data.model_dump(exclude_unset=True)
    # 归档终态：冻结一切编辑
    if exam.status == "archived":
        raise HTTPException(status_code=400, detail="该试卷已归档冻结，不可编辑")
    # 已上架锁定：前置拦截，避免先删关联再报错导致脏 session
    wants_question_change = ("question_ids" in update_dict) or ("questions" in update_dict)
    if exam.status == "published" and wants_question_change:
        raise HTTPException(status_code=400, detail="该试卷已上线发布，锁定题目修改以保障历史成绩一致性！如需更改请先下架试卷")

    questions_config = update_dict.pop("questions", None)
    question_ids = update_dict.pop("question_ids", None)

    for k, v in update_dict.items():
        setattr(exam, k, v)

    target_q_ids = None
    if question_ids is not None:
        target_q_ids = question_ids
    elif questions_config is not None:
        target_q_ids = [q.get("question_id") if isinstance(q, dict) else q.question_id for q in questions_config]

    # 如果有提交题目关联更新
    if target_q_ids is not None:
        db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).delete()
        calculated_total_score = 0
        for idx, q_id in enumerate(target_q_ids):
            q_obj = db.query(Question).filter(Question.id == q_id).first()
            score_val = q_obj.score if q_obj else 10
            calculated_total_score += score_val

            eq = ExamQuestion(
                exam_id=exam.id,
                question_id=q_id,
                score=score_val,
                sort_order=idx + 1
            )
            db.add(eq)

        pass_percent = exam.pass_percent if exam.pass_percent is not None else 60
        exam.total_score = calculated_total_score
        exam.pass_score = math.ceil(calculated_total_score * pass_percent / 100.0)
    else:
        # 如果仅修改了 pass_percent 但没有动题目
        pass_percent = exam.pass_percent if exam.pass_percent is not None else 60
        exam.pass_score = math.ceil(exam.total_score * pass_percent / 100.0)

    # 终态为上架：校验分类并刷新快照；草稿悬空分类则置空待重选
    if (exam.status or "draft") == "published":
        from app.services.exam_service import ensure_publishable
        ensure_publishable(db, exam)
    elif exam.category_id:
        from app.models.category import ExamCategory
        if not db.query(ExamCategory).filter(ExamCategory.id == exam.category_id).first():
            exam.category_id = None

    db.commit()
    db.refresh(exam)

    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.sort_order).all()
    questions = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            questions.append(QuestionResponse.model_validate(q))

    detail = ExamDetailResponse.model_validate(exam)
    detail.question_count = len(questions)
    detail.questions = questions

    return ResponseModel(code=200, message="更新成功", data=detail)


@router.get("/{exam_id}/stats", response_model=ResponseModel[dict])
def get_exam_stats(
    exam_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取已上架试卷的考情数据看板 (参与人数、平均分、通过率、个人作答明细)"""
    from app.models.record import ExamRecord
    from app.models.user import User

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    records = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id,
        ExamRecord.status == "submitted"
    ).order_by(ExamRecord.submit_time.desc()).all()

    total_participants = len(records)
    avg_score = round(sum(r.score or 0 for r in records) / total_participants, 1) if total_participants > 0 else 0.0
    passed_count = sum(1 for r in records if r.passed)
    pass_rate = round((passed_count / total_participants) * 100, 1) if total_participants > 0 else 0.0

    user_records = []
    for r in records:
        u = db.query(User).filter(User.id == r.user_id).first()
        user_records.append({
            "record_id": r.id,
            "user_id": r.user_id,
            "username": u.username if u else f"用户#{r.user_id}",
            "score": r.score,
            "is_passed": r.passed,
            "time_spent": r.time_spent,
            "submit_time": r.submit_time.strftime("%Y-%m-%d %H:%M:%S") if r.submit_time else ""
        })

    return ResponseModel(code=200, data={
        "exam_id": exam.id,
        "title": exam.title,
        "total_participants": total_participants,
        "avg_score": avg_score,
        "pass_rate": pass_rate,
        "user_records": user_records
    })


@router.delete("/{exam_id}", response_model=ResponseModel[dict])
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端删除试卷（仅draft零作答可删；其余一律下架归档）"""
    from app.models.record import ExamRecord
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    if exam.status == "archived":
        raise HTTPException(status_code=400, detail="该试卷已归档冻结，不可删除")
    if exam.status == "published":
        raise HTTPException(status_code=400, detail="该试卷已上架，请先下架后再删除")
    graded = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id,
        ExamRecord.status.in_(["submitted", "timeout"])
    ).count()
    if graded:
        raise HTTPException(status_code=400, detail=f"该试卷已有{graded}人次作答，为保护成绩只能下架归档，不可删除")
    # 清理无意义的未提交幽灵记录后删除
    db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id, ExamRecord.status == "in_progress"
    ).delete()
    db.delete(exam)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": exam_id})


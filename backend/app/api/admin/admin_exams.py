"""
[变更日志]
修改时间：2026-09-09
AI模型：Gemini 系列
修改内容：[优化试卷删除与状态流转: 1. 允许未有人作答(graded=0)的已归档/下架试卷物理删除，消除下架后无法删除的逻辑死锁; 2. 允许零作答的已归档试卷重新切回草稿(draft)或再次上架(published)]
修改时间：2026-09-08
AI模型：Gemini 系列
修改内容：[彻底修复 Word 试卷导出中文出现方框口口乱码与选项序号缺失 Bug: 1. 全局绑定中文字体 '微软雅黑' / '宋体' 并写入 OpenXML w:eastAsia 东亚字符集映射，彻底消除 Office/WPS 回退至未包含中文字形字体所致的豆腐块乱码; 2. 对选项 key 缺失或为空的题目按索引自动兜底补偿 'A'、'B'、'C'、'D']
修改时间：2026-09-08
AI模型：Gemini 系列
修改内容：[实施方案A: 全面升级试卷导出为标准 Word 文档 (.docx) 格式；支持正规试卷排版（大标题/考生须知/装订线/大题分组/题干与选项网格/参考答案与详解附录），彻底替代粗糙的 .txt 文本]
修改时间：2026-09-08
AI模型：Gemini 系列
修改内容：[修复试卷导出中文标题引发的 HTTP Header UnicodeEncodeError (latin-1) 导致的 500 Internal Server Error，依据 RFC 5987 采用 filename* = UTF-8'' 编码标准文件名]
修改时间：2026-09-06 18:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 试卷管理: RBAC 试卷按创建者隔离(超管全览)/组卷时间锁强制校验/is_ai_auto_grade 全托管开关/
         列表双维状态(主状态+时间窗子状态)+待批阅红点(pending_count)/写操作审计留痕]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[v1.2 Step2: grading_mode 与 is_ai_auto_grade 双写兼容; 出题人(creator/teacher)查询隔离显式化]
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from typing import Optional, List
import math
from urllib.parse import quote
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.exam import Exam, ExamQuestion, GRADING_MODES, sync_grading_fields
from app.models.question import Question
from app.models.record import ExamRecord
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse, ExamDetailResponse
from app.schemas.question import QuestionResponse
from app.schemas.common import ResponseModel, PageResponse
from app.services.exam_service import (
    ensure_publishable, validate_exam_window, exam_window_status,
    close_expired_window_records,
)
from app.services.audit_service import write_audit

router = APIRouter()


def is_super(admin: Admin) -> bool:
    return admin.role == "super_admin"


def _get_owned_exam(db: Session, admin: Admin, exam_id: int) -> Exam:
    """RBAC 数据隔离: 老师只能操作自己创建的试卷, 超管可操作全部"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if not is_super(admin) and exam.creator_id not in (admin.id, None):
        raise HTTPException(status_code=403, detail="无权操作他人创建的试卷")
    return exam


def _decorate(db: Session, exam: Exam, item: ExamResponse) -> ExamResponse:
    item.question_count = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).count()
    item.pending_count = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam.id, ExamRecord.status == "pending_grading"
    ).count()
    item.window_status = exam_window_status(exam)
    if exam.creator_id:
        creator = db.query(Admin).filter(Admin.id == exam.creator_id).first()
        item.creator_name = creator.username if creator else ""
    return item


def _exam_questions_payload(db: Session, exam: Exam) -> List[QuestionResponse]:
    exam_questions = db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.sort_order).all()
    questions = []
    for eq in exam_questions:
        q = db.query(Question).filter(Question.id == eq.question_id).first()
        if q:
            questions.append(QuestionResponse.model_validate(q))
    return questions


def _build_detail(db: Session, exam: Exam) -> ExamDetailResponse:
    detail = ExamDetailResponse.model_validate(exam)
    questions = _exam_questions_payload(db, exam)
    detail.question_count = len(questions)
    detail.pending_count = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam.id, ExamRecord.status == "pending_grading"
    ).count()
    detail.window_status = exam_window_status(exam)
    if exam.creator_id:
        creator = db.query(Admin).filter(Admin.id == exam.creator_id).first()
        detail.creator_name = creator.username if creator else ""
    detail.questions = questions
    return detail


@router.get("", response_model=ResponseModel[PageResponse[ExamResponse]])
def list_admin_exams(
    category_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端试卷列表查询 (出题人 creator/teacher 仅见自己创建的试卷, 超管全览; 附带待批阅红点与时间窗子状态)"""
    query = db.query(Exam)
    # v1.2 Step2 出题人查询隔离: role == 'creator' (兼容历史 'teacher' 别名) 强制追加 creator_id 过滤
    if admin.role in ("creator", "teacher"):
        query = query.filter(Exam.creator_id == admin.id)
    elif not is_super(admin):
        query = query.filter((Exam.creator_id == admin.id) | (Exam.creator_id.is_(None)))
    if category_id:
        query = query.filter(Exam.category_id == category_id)
    if keyword:
        query = query.filter(Exam.title.like(f"%{keyword}%"))
    if status_filter:
        query = query.filter(Exam.status == status_filter)

    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    exams = query.order_by(Exam.id.desc()).offset((page - 1) * size).limit(size).all()

    result_items = []
    for exam in exams:
        item = ExamResponse.model_validate(exam)
        result_items.append(_decorate(db, exam, item))

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
    """B端创建试卷与进行关联组卷 (时间锁校验 + 记录创建者)"""
    # v1.2 Step2 时间悖论硬校验: 考试限时不能大于开放总区间时间
    if data.start_time and data.end_time and data.time_limit:
        delta_minutes = (data.end_time - data.start_time).total_seconds() / 60
        if data.time_limit > delta_minutes:
            raise HTTPException(status_code=400, detail="考试限时不能大于开放总区间时间")
    validate_exam_window(time_limit=data.time_limit, is_timed=data.is_timed,
                         start_time=data.start_time, end_time=data.end_time)

    # v1.2 Step2 阅卷模式归一化: grading_mode 显式值优先;
    # 未传 grading_mode 时沿用历史开关语义 (True=ai_auto, False/缺省=ai_pre), 仅显式 manual 关闭 AI
    _mode = data.grading_mode
    if _mode is not None and _mode not in GRADING_MODES:
        raise HTTPException(status_code=400, detail="grading_mode 非法, 可选 manual / ai_pre / ai_auto")
    if _mode is None:
        _mode = "ai_auto" if data.is_ai_auto_grade else "ai_pre"

    exam = Exam(
        title=data.title,
        category_id=data.category_id,
        cover_url=data.cover_url,
        is_timed=data.is_timed,
        time_limit=data.time_limit,
        start_time=data.start_time,
        end_time=data.end_time,
        pass_percent=data.pass_percent,
        status=data.status or "draft",
        total_score=0,
        pass_score=0,
        is_recommended=data.is_recommended,
        is_random=data.is_random,
        is_ai_auto_grade=(_mode == "ai_auto"),
        grading_mode=_mode,
        creator_id=admin.id,
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
    for idx, q_id in enumerate(target_q_ids):
        q_obj = db.query(Question).filter(Question.id == q_id).first()
        score_val = q_obj.score if q_obj else 10
        calculated_total_score += score_val
        db.add(ExamQuestion(
            exam_id=exam.id,
            question_id=q_id,
            score=score_val,
            sort_order=idx + 1
        ))

    pass_percent = data.pass_percent if data.pass_percent is not None else 60
    exam.total_score = calculated_total_score
    exam.pass_score = math.ceil(calculated_total_score * pass_percent / 100.0)
    # 直接上架创建：校验分类并写入快照
    if (exam.status or "draft") == "published":
        ensure_publishable(db, exam)
    db.commit()
    db.refresh(exam)

    write_audit(db, "create", "exam", exam.id, summary=f"创建试卷《{exam.title}》",
                after_data={"title": exam.title, "status": exam.status, "question_count": len(target_q_ids)}, admin=admin)
    db.commit()

    return ResponseModel(code=201, message="创建试卷成功", data=_build_detail(db, exam))

@router.put("/{exam_id}/status", response_model=ResponseModel[dict])
def update_exam_status(
    exam_id: int,
    status_val: str = Query(..., alias="status", description="新状态: draft, published, archived"),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端切换试卷上下架状态（零作答允许在草稿/上架/归档间流转；已有作答的归档为终态）"""
    exam = _get_owned_exam(db, admin, exam_id)

    if status_val not in ["draft", "published", "archived"]:
        raise HTTPException(status_code=400, detail="无效的状态参数")

    if exam.status == "archived":
        graded = db.query(ExamRecord).filter(
            ExamRecord.exam_id == exam_id,
            ExamRecord.status.in_(["submitted", "timeout", "pending_grading"])
        ).count()
        if graded > 0:
            raise HTTPException(status_code=400, detail="该试卷已有学员作答并归档，不可再变更状态")
    if status_val == "published":
        ensure_publishable(db, exam)

    before = exam.status
    exam.status = status_val
    db.commit()
    write_audit(db, "update_status", "exam", exam.id,
                summary=f"试卷《{exam.title}》状态 {before} → {status_val}",
                before_data={"status": before}, after_data={"status": status_val}, admin=admin)
    db.commit()
    return ResponseModel(code=200, message=f"试卷状态已更新为 {status_val}", data={"id": exam_id, "status": status_val})


@router.get("/{exam_id}", response_model=ResponseModel[ExamDetailResponse])
def get_admin_exam_detail(
    exam_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取试卷详情（含草稿/已下架，不受 published 隔离限制）"""
    exam = _get_owned_exam(db, admin, exam_id)
    return ResponseModel(code=200, data=_build_detail(db, exam))


@router.put("/{exam_id}", response_model=ResponseModel[ExamDetailResponse])
def update_exam(
    exam_id: int,
    data: ExamUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端修改编辑试卷配置与重新组卷"""
    exam = _get_owned_exam(db, admin, exam_id)

    update_dict = data.model_dump(exclude_unset=True)
    # 归档终态：冻结一切编辑
    if exam.status == "archived":
        raise HTTPException(status_code=400, detail="该试卷已归档冻结，不可编辑")
    # 已上架锁定：前置拦截，避免先删关联再报错导致脏 session
    wants_question_change = ("question_ids" in update_dict) or ("questions" in update_dict)
    if exam.status == "published" and wants_question_change:
        raise HTTPException(status_code=400, detail="该试卷已上线发布，锁定题目修改以保障历史成绩一致性！如需更改请先下架试卷")

    # 时间锁校验 (以更新后的整体窗口为准)
    new_time_limit = update_dict.get("time_limit", exam.time_limit)
    new_is_timed = update_dict.get("is_timed", exam.is_timed)
    new_start = update_dict.get("start_time", exam.start_time)
    new_end = update_dict.get("end_time", exam.end_time)
    # v1.2 Step2 时间悖论硬校验
    if new_start and new_end and new_time_limit:
        _delta = (new_end - new_start).total_seconds() / 60
        if new_time_limit > _delta:
            raise HTTPException(status_code=400, detail="考试限时不能大于开放总区间时间")
    validate_exam_window(time_limit=new_time_limit, is_timed=new_is_timed, start_time=new_start, end_time=new_end)

    # v1.2 Step2 阅卷模式双写: grading_mode 优先, 否则由 is_ai_auto_grade 推导
    if "grading_mode" in update_dict or "is_ai_auto_grade" in update_dict:
        _g = update_dict.pop("grading_mode", None)
        _a = update_dict.pop("is_ai_auto_grade", None)
        if _g is not None and _g not in GRADING_MODES:
            raise HTTPException(status_code=400, detail="grading_mode 非法, 可选 manual / ai_pre / ai_auto")
        _resolved = _g if _g is not None else ("ai_auto" if _a else "ai_pre") if _a is not None else None
        if _resolved is not None:
            sync_grading_fields(exam, _resolved)

    before_snapshot = {"title": exam.title, "status": exam.status, "is_ai_auto_grade": exam.is_ai_auto_grade}

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

            db.add(ExamQuestion(
                exam_id=exam.id,
                question_id=q_id,
                score=score_val,
                sort_order=idx + 1
            ))

        pass_percent = exam.pass_percent if exam.pass_percent is not None else 60
        exam.total_score = calculated_total_score
        exam.pass_score = math.ceil(calculated_total_score * pass_percent / 100.0)
    else:
        # 如果仅修改了 pass_percent 但没有动题目
        pass_percent = exam.pass_percent if exam.pass_percent is not None else 60
        exam.pass_score = math.ceil(exam.total_score * pass_percent / 100.0)

    # 终态为上架：校验分类并刷新快照；草稿悬空分类则置空待重选
    if (exam.status or "draft") == "published":
        ensure_publishable(db, exam)
    elif exam.category_id:
        from app.models.category import ExamCategory
        if not db.query(ExamCategory).filter(ExamCategory.id == exam.category_id).first():
            exam.category_id = None

    db.commit()
    db.refresh(exam)

    write_audit(db, "update", "exam", exam.id, summary=f"编辑试卷《{exam.title}》",
                before_data=before_snapshot, after_data={"title": exam.title, "status": exam.status}, admin=admin)
    db.commit()

    return ResponseModel(code=200, message="更新成功", data=_build_detail(db, exam))


@router.get("/{exam_id}/stats", response_model=ResponseModel[dict])
def get_exam_stats(
    exam_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取已上架试卷的考情数据看板 (参与人数、平均分、通过率、个人作答明细、待批阅数)"""
    from app.models.user import User

    exam = _get_owned_exam(db, admin, exam_id)

    # 惰性收卷: 老师查看考情时顺手结算已过 end_time 的僵尸卷
    close_expired_window_records(db, exam_id=exam.id)

    records = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id,
        ExamRecord.status == "submitted"
    ).order_by(ExamRecord.submit_time.desc()).all()

    pending_count = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id, ExamRecord.status == "pending_grading"
    ).count()

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
            "nickname": (u.nickname if u else None),
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
        "pending_count": pending_count,
        "user_records": user_records
    })


@router.delete("/{exam_id}", response_model=ResponseModel[dict])
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端删除试卷（仅未上架且零作答可删；若已上架需先下架；有作答成绩则一律不可物理删除）"""
    exam = _get_owned_exam(db, admin, exam_id)

    if exam.status == "published":
        raise HTTPException(status_code=400, detail="该试卷正在上架发布中，请先下架后再删除")

    graded = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id,
        ExamRecord.status.in_(["submitted", "timeout", "pending_grading"])
    ).count()
    if graded:
        raise HTTPException(status_code=400, detail=f"该试卷已有 {graded} 人次作答，为保护学员成绩只能下架归档，不可删除")

    # 清理无意义的未提交幽灵记录后删除
    db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id, ExamRecord.status == "in_progress"
    ).delete()
    # 清理试卷试题关联
    db.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).delete()

    title = exam.title
    db.delete(exam)
    db.commit()
    write_audit(db, "delete", "exam", exam_id, summary=f"删除试卷《{title}》",
                before_data={"title": title, "status": exam.status}, admin=admin)
    db.commit()
    return ResponseModel(code=200, message=f"试卷《{title}》已彻底物理删除", data={"id": exam_id})


# ---- 试卷导出 (方案 A: 标准 Word .docx 正规试卷排版) ----
from fastapi.responses import Response
import io

# 中文题型映射与大题序号映射
_TYPE_LABEL = {
    "single": "单项选择题", "multiple": "多项选择题", "judge": "判断题",
    "fill": "填空题", "short": "简答题",
}
_BIG_NUMS = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]


@router.get("/{exam_id}/export")
def export_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """导出试卷为标准 Word 文档 (docx)，支持纸质打印与本地编辑"""
    exam = _get_owned_exam(db, admin, exam_id)
    questions = _exam_questions_payload(db, exam)

    total_score = sum(q.score or 10 for q in questions)
    clean_title = (exam.title or f"试卷_{exam_id}").strip()

    try:
        from docx import Document as DocxDocument
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.oxml.ns import qn

        doc = DocxDocument()

        # 全局默认字体绑定为通用中文字体 (微软雅黑 / 保证东亚字符集正常解析)
        def _apply_chinese_font(run, font_name="微软雅黑"):
            run.font.name = font_name
            rPr = run._element.get_or_add_rPr()
            rFonts = rPr.get_or_add_rFonts()
            rFonts.set(qn("w:eastAsia"), font_name)
            rFonts.set(qn("w:ascii"), font_name)
            rFonts.set(qn("w:hAnsi"), font_name)

        # 页面边距设为标准窄边距或适中边距 (左右各 2cm, 上下各 2cm)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.9)
            section.right_margin = Inches(0.9)

        # 1. 试卷大标题 (居中, 20pt, 粗体)
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_p.paragraph_format.space_before = Pt(0)
        title_p.paragraph_format.space_after = Pt(6)
        title_run = title_p.add_run(clean_title)
        title_run.font.size = Pt(20)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        _apply_chinese_font(title_run, "微软雅黑")

        # 2. 副信息条 (满分/题量/及格线/考试分类)
        meta_p = doc.add_paragraph()
        meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta_p.paragraph_format.space_after = Pt(14)
        cat_info = f"  |  分类: {exam.category_name}" if exam.category_name else ""
        meta_run = meta_p.add_run(
            f"（满分：{total_score} 分    题量：{len(questions)} 题    合格线：{exam.pass_percent or 60}%{cat_info}）"
        )
        meta_run.font.size = Pt(10.5)
        meta_run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        _apply_chinese_font(meta_run, "微软雅黑")

        # 3. 考生信息填报栏 (姓名/考号/成绩/监考)
        table = doc.add_table(rows=1, cols=4)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True
        row_cells = table.rows[0].cells
        cols_text = ["姓名：________", "考号：________", "得分：________", "批阅：________"]
        for i, text in enumerate(cols_text):
            p = row_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.size = Pt(10.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
            _apply_chinese_font(r, "微软雅黑")

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

        # 4. 按题型分组
        grouped: dict[str, list] = {}
        for q in questions:
            grouped.setdefault(q.type, []).append(q)

        seq = 0
        big_idx = 0
        answers_list: list[dict] = []

        for qtype, qs in grouped.items():
            type_label = _TYPE_LABEL.get(qtype, qtype)
            type_total = sum(q.score or 10 for q in qs)
            big_num = _BIG_NUMS[big_idx] if big_idx < len(_BIG_NUMS) else str(big_idx + 1)
            big_idx += 1

            # 大题题目标题 (如: 一、单项选择题（共 10 题，共 100 分）)
            sec_p = doc.add_paragraph()
            sec_p.paragraph_format.space_before = Pt(14)
            sec_p.paragraph_format.space_after = Pt(6)
            sec_run = sec_p.add_run(f"{big_num}、{type_label}（共 {len(qs)} 题，满分 {type_total} 分）")
            sec_run.font.size = Pt(12)
            sec_run.font.bold = True
            sec_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            _apply_chinese_font(sec_run, "微软雅黑")

            # 各小题渲染
            for q in qs:
                seq += 1
                q_p = doc.add_paragraph()
                q_p.paragraph_format.space_before = Pt(4)
                q_p.paragraph_format.space_after = Pt(3)
                q_run = q_p.add_run(f"{seq}. 【{q.score or 10}分】{q.title}")
                q_run.font.size = Pt(11)
                _apply_chinese_font(q_run, "微软雅黑")

                # 选择题选项排列 (若 key 缺失则根据索引自动补 A, B, C, D)
                if q.options and isinstance(q.options, list):
                    for oi, opt in enumerate(q.options):
                        fallback_key = chr(65 + oi) if oi < 26 else str(oi + 1)
                        key = (opt.get("key", "") if isinstance(opt, dict) else "").strip() or fallback_key
                        text = (opt.get("text", "") if isinstance(opt, dict) else str(opt)).strip()
                        opt_p = doc.add_paragraph()
                        opt_p.paragraph_format.left_indent = Inches(0.25)
                        opt_p.paragraph_format.space_before = Pt(1)
                        opt_p.paragraph_format.space_after = Pt(2)
                        opt_run = opt_p.add_run(f"{key}. {text}")
                        opt_run.font.size = Pt(10.5)
                        opt_run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
                        _apply_chinese_font(opt_run, "微软雅黑")

                # 收集参考答案用于附录
                ans_str = ""
                if isinstance(q.answer, list):
                    ans_str = "、".join(str(a) for a in q.answer)
                elif q.answer is not None:
                    ans_str = str(q.answer)
                answers_list.append({
                    "seq": seq,
                    "title": q.title,
                    "answer": ans_str,
                    "explanation": q.explanation or ""
                })

        # 5. 试卷附录：参考答案与详细解析 (独立起段)
        doc.add_page_break()
        ans_title_p = doc.add_paragraph()
        ans_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ans_title_p.paragraph_format.space_before = Pt(12)
        ans_title_p.paragraph_format.space_after = Pt(12)
        ans_title_run = ans_title_p.add_run(f"《{clean_title}》参考答案与名师解析")
        ans_title_run.font.size = Pt(16)
        ans_title_run.font.bold = True
        ans_title_run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        _apply_chinese_font(ans_title_run, "微软雅黑")

        for a in answers_list:
            ap = doc.add_paragraph()
            ap.paragraph_format.space_before = Pt(6)
            ap.paragraph_format.space_after = Pt(2)
            
            ar1 = ap.add_run(f"第 {a['seq']} 题参考答案：")
            ar1.font.bold = True
            ar1.font.size = Pt(10.5)
            _apply_chinese_font(ar1, "微软雅黑")
            
            ar2 = ap.add_run(f"{a['answer'] or '（略）'}\n")
            ar2.font.bold = True
            ar2.font.size = Pt(10.5)
            ar2.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
            _apply_chinese_font(ar2, "微软雅黑")

            if a["explanation"]:
                exp_p = doc.add_paragraph()
                exp_p.paragraph_format.left_indent = Inches(0.2)
                exp_p.paragraph_format.space_before = Pt(0)
                exp_p.paragraph_format.space_after = Pt(4)
                er1 = exp_p.add_run("【解析】")
                er1.font.size = Pt(10)
                er1.font.bold = True
                er1.font.color.rgb = RGBColor(0x05, 0x96, 0x69)
                _apply_chinese_font(er1, "微软雅黑")
                er2 = exp_p.add_run(a["explanation"])
                er2.font.size = Pt(10)
                er2.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
                _apply_chinese_font(er2, "微软雅黑")

        # 保存到内存字节流
        stream = io.BytesIO()
        doc.save(stream)
        stream.seek(0)
        docx_bytes = stream.getvalue()

        encoded_filename = quote(f"{clean_title}.docx")
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"exam_{exam_id}.docx\"; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        # 如环境异常则无缝降级为纯文本，保障 100% 可用性
        clean_title = (exam.title or f"exam_{exam_id}").strip()
        encoded_filename = quote(f"{clean_title}.txt")
        fallback_text = f"【试卷名称】{clean_title}\n总分: {total_score} 分\n" + "\n".join(f"{i+1}. {q.title}" for i, q in enumerate(questions))
        return Response(
            content=fallback_text.encode("utf-8"),
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=\"exam_{exam_id}.txt\"; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )

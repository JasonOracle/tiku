"""
[变更日志]
修改时间：2026-09-06 18:40:00
AI模型：ZCode (GLM)
修改内容：[v1.2 题海管理: 填空/简答题型 + 填空防崩溃校验 + 题目锁定防篡改(上架/归档卷引用即只读) +
         防牵连软删除(is_deleted) + 复制新题 + AI 批量入库 + Excel 导入支持 fill/short + 审计留痕]
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Optional, List
import openpyxl
import io
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.schemas.common import ResponseModel, PageResponse
from app.services.exam_service import (
    first_category_id, get_locked_exam_titles, validate_fill_question,
)
from app.services.audit_service import write_audit

router = APIRouter()

SUPPORTED_TYPES = ("single", "multiple", "judge", "fill", "short")


def normalize_options(options) -> list:
    """规范化选项结构: 字符串数组 ["A. 甲","乙"] → [{"key":"A","text":"甲"},...] (AI 生成/历史数据双兼容)"""
    import re as _re
    if not isinstance(options, list):
        return []
    normalized = []
    for opt in options:
        if isinstance(opt, dict):
            if opt.get("key") is not None or opt.get("text") is not None:
                normalized.append({"key": str(opt.get("key", "")), "text": str(opt.get("text", ""))})
            continue
        text = str(opt).strip()
        if not text:
            continue
        m = _re.match(r"^([A-Fa-f])\s*[.、:：\)）]\s*(.+)$", text)
        if m:
            normalized.append({"key": m.group(1).upper(), "text": m.group(2).strip()})
        else:
            key = "ABCDEF"[len(normalized)] if len(normalized) < 6 else "X"
            normalized.append({"key": key, "text": text})
    return normalized


def _decorate_locked(db: Session, q: Question, res: QuestionResponse) -> QuestionResponse:
    res.locked = bool(get_locked_exam_titles(db, q.id))
    return res


def _validate_question_payload(q_type: str, title: str, answer) -> None:
    """入库前题型级校验 (防崩溃)。multiple 连写答案 ["ABC"] 自动拆分为 ["A","B","C"] (原地修正)"""
    if q_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的题型: {q_type}")
    if q_type == "fill":
        validate_fill_question(title, answer)
    elif q_type == "short":
        if not answer or not str(answer[0]).strip():
            raise HTTPException(status_code=400, detail="简答题必须配置标准答案")
    elif q_type == "single":
        if not answer or len(answer) != 1:
            raise HTTPException(status_code=400, detail="单选题答案只能有一个")
    elif q_type == "judge":
        if not answer or len(answer) != 1:
            raise HTTPException(status_code=400, detail="判断题答案只能有一个")
    elif q_type == "multiple":
        # 兼容连写: ["ABC"] / ["A","BC"] → 拆成单字母集合再校验
        expanded: list = []
        for a in (answer or []):
            token = str(a).strip().upper()
            for ch in token:
                if ch in "ABCDEF":
                    expanded.append(ch)
        if len(expanded) < 2:
            raise HTTPException(status_code=400, detail="多选题答案至少两个")
        answer[:] = expanded


@router.get("", response_model=ResponseModel[PageResponse[QuestionResponse]])
def list_questions(
    type: Optional[str] = Query(None, description="题型过滤"),
    category_id: Optional[int] = Query(None, description="分类过滤"),
    keyword: Optional[str] = Query(None, description="标题关键字"),
    include_deleted: bool = Query(False, description="是否包含已软删除题目"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取题目列表 (默认过滤软删除; 附带锁定状态与来源标签)"""
    query = db.query(Question)
    if not include_deleted:
        query = query.filter(Question.is_deleted == False)  # noqa: E712
    if type:
        query = query.filter(Question.type == type)
    if category_id:
        query = query.filter(Question.category_id == category_id)
    if keyword:
        query = query.filter(Question.title.like(f"%{keyword}%"))

    total = query.count()
    total_pages = (total + size - 1) // size if total > 0 else 0
    has_next = page < total_pages

    questions = query.order_by(Question.id.desc()).offset((page - 1) * size).limit(size).all()
    items = [_decorate_locked(db, q, QuestionResponse.model_validate(q)) for q in questions]

    return ResponseModel(
        code=200,
        data=PageResponse(
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            items=items
        )
    )

@router.post("", response_model=ResponseModel[QuestionResponse], status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端创建题目（无分类时默认第一项；填空/简答带结构校验）"""
    _validate_question_payload(data.type, data.title, data.answer)
    from app.services.exam_service import first_category_id as _fc
    category_id = data.category_id
    if not category_id:
        category_id = _fc(db, "question")
    question = Question(
        type=data.type,
        title=data.title,
        options=normalize_options(data.options),
        answer=data.answer,
        grading_points=data.grading_points or [],
        explanation=data.explanation,
        difficulty=data.difficulty or "medium",
        score=data.score if data.score is not None else 10,
        source=data.source if data.source in ("manual", "ai") else "manual",
        category_id=category_id
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    write_audit(db, "create", "question", question.id, summary=f"新增题目 #{question.id} [{data.type}]",
                after_data={"title": question.title[:100], "type": question.type, "source": question.source}, admin=admin)
    db.commit()
    return ResponseModel(code=201, message="创建题目成功", data=question)


@router.post("/batch", response_model=ResponseModel[dict], status_code=status.HTTP_201_CREATED)
def batch_create_questions(
    data: List[QuestionCreate],
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端批量入库题目 (AI 出题二次确认后的落地入口; 逐题校验, 全部合法才入库)"""
    if not data:
        raise HTTPException(status_code=400, detail="题目列表为空")
    if len(data) > 50:
        raise HTTPException(status_code=400, detail="单次最多入库 50 道题")

    created_ids = []
    for item in data:
        if item.type == "fill" and isinstance(item.answer, list):
            blank_count = item.title.count("___")
            normalized = [b if isinstance(b, list) else [str(b)] for b in item.answer]
            if blank_count == 0:
                item.title = item.title.rstrip() + " " + " ".join(["___"] * len(normalized))
                blank_count = item.title.count("___")
            if blank_count > len(normalized):
                for _ in range(blank_count - len(normalized)):
                    normalized.append(["参考答案"])
            elif blank_count < len(normalized):
                normalized = normalized[:blank_count]
            item.answer = normalized

        _validate_question_payload(item.type, item.title, item.answer)
        category_id = item.category_id or first_category_id(db, "question")
        q = Question(
            type=item.type,
            title=item.title,
            options=normalize_options(item.options),
            answer=item.answer,
            grading_points=item.grading_points or [],
            explanation=item.explanation or "",
            difficulty=item.difficulty or "medium",
            score=item.score if item.score is not None else 10,
            source=item.source if item.source in ("manual", "ai") else "manual",
            category_id=category_id
        )
        db.add(q)
        db.flush()
        created_ids.append(q.id)

    write_audit(db, "create", "question", None,
                summary=f"批量入库 {len(created_ids)} 道题目 (来源: {'AI生成' if data[0].source == 'ai' else '人工'})",
                after_data={"question_ids": created_ids}, admin=admin)
    db.commit()
    return ResponseModel(code=201, message=f"成功入库 {len(created_ids)} 道题目", data={"question_ids": created_ids})


@router.post("/{question_id}/copy", response_model=ResponseModel[QuestionResponse], status_code=status.HTTP_201_CREATED)
def copy_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """复制新题 (锁定题目的唯一修改路径: 复制后修改副本)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    clone = Question(
        type=question.type,
        title=(question.title or "") + "（副本）",
        options=question.options,
        answer=question.answer,
        grading_points=question.grading_points,
        explanation=question.explanation,
        difficulty=question.difficulty,
        score=question.score,
        source="manual",
        is_deleted=False,
        category_id=question.category_id,
    )
    db.add(clone)
    db.commit()
    db.refresh(clone)
    write_audit(db, "copy", "question", clone.id, summary=f"复制题目 #{question_id} → #{clone.id}",
                after_data={"source_id": question_id}, admin=admin)
    db.commit()
    return ResponseModel(code=201, message="复制成功，请修改副本内容", data=clone)


@router.put("/{question_id}", response_model=ResponseModel[QuestionResponse])
def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端编辑修改题目 (被上架/归档卷引用的题目全局只读, 只能复制新题)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    if question.is_deleted:
        raise HTTPException(status_code=400, detail="该题目已删除，不可编辑")

    locked_titles = get_locked_exam_titles(db, question_id)
    if locked_titles:
        shown = "、".join([f"《{t}》" for t in locked_titles[:3]])
        more = f"等{len(locked_titles)}张试卷" if len(locked_titles) > 3 else ""
        raise HTTPException(status_code=400, detail=f"该题目已被{shown}{more}引用并锁定为只读，如需修改请复制产生新题")

    update_dict = data.model_dump(exclude_unset=True)
    if "options" in update_dict and update_dict["options"] is not None:
        update_dict["options"] = normalize_options(update_dict["options"])

    new_type = update_dict.get("type", question.type)
    new_title = update_dict.get("title", question.title)
    new_answer = update_dict.get("answer", question.answer)
    if "answer" in update_dict or "title" in update_dict or "type" in update_dict:
        _validate_question_payload(new_type, new_title, new_answer)

    before_snapshot = {"title": question.title[:100], "type": question.type, "score": question.score}
    for k, v in update_dict.items():
        setattr(question, k, v)

    db.commit()
    db.refresh(question)
    write_audit(db, "update", "question", question.id, summary=f"编辑题目 #{question.id}",
                before_data=before_snapshot, after_data={"title": question.title[:100], "type": question.type}, admin=admin)
    db.commit()
    res = QuestionResponse.model_validate(question)
    return ResponseModel(code=200, message="更新成功", data=_decorate_locked(db, question, res))


@router.delete("/{question_id}", response_model=ResponseModel[dict])
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端删除题目 → 防牵连软删除: 打 is_deleted 标记从题库隐藏, 已引用试卷仍可正常拉取原题 (绝不物理删除)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    if question.is_deleted:
        raise HTTPException(status_code=400, detail="该题目已处于删除状态")

    question.is_deleted = True
    db.commit()
    write_audit(db, "delete", "question", question_id, summary=f"软删除题目 #{question_id}",
                before_data={"title": question.title[:100], "type": question.type}, admin=admin)
    db.commit()
    return ResponseModel(code=200, message="已删除（已引用该题的试卷不受影响）", data={"id": question_id})


@router.post("/import", response_model=ResponseModel[dict])
async def import_questions_excel(
    file: UploadFile = File(...),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端 Excel 导入题目 (按表头匹配列, 行级“分类”列; v1.2 支持 fill/short:
    填空答案格式 "答案1,答案2|答案3" (逗号=一空多答, 竖线=分空); 简答答案列为标准答案全文, 可选“踩分点”列分号分隔)"""
    from app.models.category import ExamCategory
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持 Excel (.xlsx, .xls) 文件上传")

    contents = await file.read()
    workbook = openpyxl.load_workbook(filename=io.BytesIO(contents))
    sheet = workbook[workbook.sheetnames[0]]

    imported_count = 0
    skipped_count = 0
    diff_map = {"简单": "easy", "中等": "medium", "困难": "hard"}

    def _cell(row, idx):
        return row[idx] if row and idx < len(row) else None

    header = None
    col_idx: dict = {}
    for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        if row_idx == 1:
            header = [(str(c).strip() if c is not None else "") for c in (row or [])]
            for name in ("题型", "题干", "答案", "解析", "难度", "分值", "分类", "踩分点"):
                if name in header:
                    col_idx[name] = header.index(name)
            continue  # 跳过表头

        if not row or not row[0] or not row[1]:
            continue

        q_type = str(row[0]).strip().lower()
        if q_type not in SUPPORTED_TYPES:
            skipped_count += 1
            continue

        title = str(row[1]).strip()

        # 选项组装 (fill/short 无选项)
        options = []
        if q_type in ("single", "multiple", "judge"):
            for i, key in enumerate(["A", "B", "C", "D"]):
                col = 2 + i
                if len(row) > col and row[col]:
                    options.append({"key": key, "text": str(row[col]).strip()})

        explanation = str(row[7]).strip() if len(row) > 7 and row[7] else ""
        raw_diff = str(row[8]).strip() if len(row) > 8 and row[8] else "medium"
        difficulty = diff_map.get(raw_diff, raw_diff.lower())
        score = 10
        if len(row) > 9 and row[9]:
            try:
                score = int(row[9])
            except ValueError:
                score = 10

        # ---- 答案解析 (题型相关) ----
        raw_ans = str(row[6]).strip() if len(row) > 6 and row[6] else ""
        answer: list = []
        grading_points: list = []
        if q_type in ("single", "multiple", "judge"):
            answer = [a.strip().upper() for a in raw_ans.replace(",", "").replace(";", "") if a.strip()]
        elif q_type == "fill":
            # "北京,北京市|是" → [["北京","北京市"],["是"]]
            answer = [[a.strip() for a in seg.split(",") if a.strip()] for seg in raw_ans.split("|") if seg.strip()]
        elif q_type == "short":
            answer = [raw_ans]
            if "踩分点" in col_idx:
                raw_points = str(_cell(row, col_idx["踩分点"]) or "").strip()
                grading_points = [p.strip() for p in raw_points.replace("；", ";").split(";") if p.strip()]

        # ---- 题型级校验: 不合法跳过计数, 不中断整批 ----
        try:
            _validate_question_payload(q_type, title, answer)
        except HTTPException:
            skipped_count += 1
            continue

        # 行级分类：全局参数优先兼容；否则按“分类”列名匹配，不存在自动新建，空则取第一项
        row_cat_id = category_id
        if not row_cat_id:
            raw_cat = str(_cell(row, col_idx["分类"])).strip() if "分类" in col_idx and _cell(row, col_idx["分类"]) else ""
            if raw_cat:
                hit = db.query(ExamCategory).filter(
                    ExamCategory.name == raw_cat, ExamCategory.target_type == "question"
                ).first()
                if not hit:
                    hit = ExamCategory(name=raw_cat, target_type="question", icon="folder", sort_order=0)
                    db.add(hit)
                    db.flush()
                row_cat_id = hit.id
            else:
                row_cat_id = first_category_id(db, "question")

        db.add(Question(
            type=q_type,
            title=title,
            options=options,
            answer=answer,
            grading_points=grading_points,
            explanation=explanation,
            difficulty=difficulty,
            score=score,
            category_id=row_cat_id
        ))
        imported_count += 1

    db.commit()
    write_audit(db, "import", "question", None, summary=f"Excel 导入 {imported_count} 道题目 (跳过 {skipped_count})",
                after_data={"imported_count": imported_count, "skipped_count": skipped_count}, admin=admin)
    db.commit()
    return ResponseModel(code=200, message="批量导入成功", data={"imported_count": imported_count, "skipped_count": skipped_count})

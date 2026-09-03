"""
[变更日志]
修改时间：2026-09-03 23:36:00
AI模型：Gemini 底层
修改内容：[1. 题目 CRUD 完美绑定 score 默认分值与 category_id; 2. Excel 导入支持中文难度与分数字段解析]
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

router = APIRouter()

@router.get("", response_model=ResponseModel[PageResponse[QuestionResponse]])
def list_questions(
    type: Optional[str] = Query(None, description="题型过滤"),
    category_id: Optional[int] = Query(None, description="分类过滤"),
    keyword: Optional[str] = Query(None, description="标题关键字"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端获取题目列表 (标准分页 + 条件筛选)"""
    query = db.query(Question)
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
    items = [QuestionResponse.model_validate(q) for q in questions]

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
    """B端创建题目（无分类时默认第一项）"""
    from app.services.exam_service import first_category_id
    category_id = data.category_id
    if not category_id:
        category_id = first_category_id(db, "question")
    question = Question(
        type=data.type,
        title=data.title,
        options=[opt.model_dump() for opt in data.options] if data.options else [],
        answer=data.answer,
        explanation=data.explanation,
        difficulty=data.difficulty or "medium",
        score=data.score if data.score is not None else 10,
        category_id=category_id
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return ResponseModel(code=201, message="创建题目成功", data=question)

@router.put("/{question_id}", response_model=ResponseModel[QuestionResponse])
def update_question(
    question_id: int, 
    data: QuestionUpdate, 
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端编辑修改题目"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    update_dict = data.model_dump(exclude_unset=True)
    if "options" in update_dict and update_dict["options"] is not None:
        update_dict["options"] = [opt.model_dump() if hasattr(opt, 'model_dump') else opt for opt in update_dict["options"]]

    for k, v in update_dict.items():
        setattr(question, k, v)

    db.commit()
    db.refresh(question)
    return ResponseModel(code=200, message="更新成功", data=question)

@router.delete("/{question_id}", response_model=ResponseModel[dict])
def delete_question(
    question_id: int, 
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端删除题目（被上架/归档卷引用时拦截；仅草稿引用则联动移除并重算）"""
    from app.models.exam import Exam, ExamQuestion
    from app.services.exam_service import recalc_exam_totals
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    links = db.query(ExamQuestion).filter(ExamQuestion.question_id == question_id).all()
    exam_ids = sorted({lk.exam_id for lk in links})
    locked_titles = []
    for eid in exam_ids:
        ex = db.query(Exam).filter(Exam.id == eid).first()
        if ex and ex.status in ("published", "archived"):
            locked_titles.append(ex.title)
    if locked_titles:
        shown = "、".join([f"《{t}》" for t in locked_titles[:3]])
        more = f"等{len(locked_titles)}张试卷" if len(locked_titles) > 3 else ""
        raise HTTPException(status_code=400, detail=f"该题目正被{shown}{more}引用，不可删除")

    # 仅草稿卷引用：联动移除并重算总分及格线
    for eid in exam_ids:
        db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == eid, ExamQuestion.question_id == question_id
        ).delete()
        ex = db.query(Exam).filter(Exam.id == eid).first()
        if ex:
            recalc_exam_totals(db, ex)

    db.delete(question)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": question_id})

@router.post("/import", response_model=ResponseModel[dict])
async def import_questions_excel(
    file: UploadFile = File(...),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """B端 Excel 导入题目 (按表头匹配列，含行级“分类”列；short/fill 预留题型跳过计数)"""
    from app.models.category import ExamCategory
    from app.services.exam_service import first_category_id
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持 Excel (.xlsx, .xls) 文件上传")

    contents = await file.read()
    workbook = openpyxl.load_workbook(filename=io.BytesIO(contents))
    sheet = workbook[workbook.sheetnames[0]]

    imported_count = 0
    skipped_count = 0
    diff_map = {"简单": "easy", "中等": "medium", "困难": "hard"}
    supported_types = {"single", "multiple", "judge"}

    def _cell(row, idx):
        return row[idx] if row and idx < len(row) else None

    header = None
    cat_col_idx = None
    for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        if row_idx == 1:
            header = [(str(c).strip() if c is not None else "") for c in (row or [])]
            if "分类" in header:
                cat_col_idx = header.index("分类")
            continue  # 跳过表头

        if not row or not row[0] or not row[1]:
            continue

        q_type = str(row[0]).strip().lower()  # single, multiple, judge
        if q_type not in supported_types:
            skipped_count += 1  # short/fill 等预留题型暂跳过
            continue

        title = str(row[1]).strip()
        
        # 选项组装
        options = []
        if len(row) > 2 and row[2]: options.append({"key": "A", "text": str(row[2]).strip()})
        if len(row) > 3 and row[3]: options.append({"key": "B", "text": str(row[3]).strip()})
        if len(row) > 4 and row[4]: options.append({"key": "C", "text": str(row[4]).strip()})
        if len(row) > 5 and row[5]: options.append({"key": "D", "text": str(row[5]).strip()})

        # 答案解析
        raw_ans = str(row[6]).strip() if len(row) > 6 and row[6] else "A"
        answer_list = [a.strip().upper() for a in raw_ans.replace(",", "").replace(";", "")]

        explanation = str(row[7]).strip() if len(row) > 7 and row[7] else ""
        
        raw_diff = str(row[8]).strip() if len(row) > 8 and row[8] else "medium"
        difficulty = diff_map.get(raw_diff, raw_diff.lower())

        score = 10
        if len(row) > 9 and row[9]:
            try:
                score = int(row[9])
            except ValueError:
                score = 10

        # 行级分类：全局参数优先兼容；否则按“分类”列名匹配，不存在自动新建，空则取第一项
        row_cat_id = category_id
        if not row_cat_id:
            raw_cat = str(_cell(row, cat_col_idx)).strip() if cat_col_idx is not None and _cell(row, cat_col_idx) else ""
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

        q = Question(
            type=q_type,
            title=title,
            options=options,
            answer=answer_list,
            explanation=explanation,
            difficulty=difficulty,
            score=score,
            category_id=row_cat_id
        )
        db.add(q)
        imported_count += 1

    db.commit()
    return ResponseModel(code=200, message="批量导入成功", data={"imported_count": imported_count, "skipped_count": skipped_count})


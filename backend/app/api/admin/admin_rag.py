"""
[变更日志]
修改时间：2026-09-08
AI模型：Muse Spark
修改内容：[v1.3 任务3: RAG 私有文档库 API (上传切片/进度/列表/检索/删除/批量取块), 超管全览他人仅看自传]
"""
import json
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.rag import DocLibrary, DocChunk
from app.schemas.common import ResponseModel
from app.services import embedding_service

router = APIRouter()

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXTS = {".txt", ".md", ".pdf", ".docx"}


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="检索问题")
    limit: int = Field(6, ge=1, le=20, description="返回切片数")
    doc_ids: Optional[List[int]] = Field(None, description="限定文档范围, 空则全库")


def _owned_doc(db: Session, admin: Admin, doc_id: int) -> DocLibrary:
    d = db.query(DocLibrary).filter(DocLibrary.id == doc_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="文档不存在")
    if admin.role != "super_admin" and d.admin_id != admin.id:
        raise HTTPException(status_code=403, detail="无权访问他人文档")
    return d


def _serialize_doc(d: DocLibrary) -> dict:
    return {
        "id": d.id,
        "filename": d.filename,
        "status": d.status,
        "total_chunks": d.total_chunks,
        "done_chunks": d.done_chunks,
        "error": d.error or "",
        "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else "",
    }


def _serialize_chunk(c: DocChunk, filename: str = "", score: Optional[float] = None) -> dict:
    item = {
        "id": c.id,
        "doc_id": c.doc_id,
        "chunk_index": c.chunk_index,
        "text": c.text,
        "filename": filename,
    }
    if score is not None:
        item["score"] = round(score, 4)
    return item


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """滑窗切片 (按字符, 保留段落边界优先已在提取阶段归一化)"""
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    step = max(1, size - overlap)
    for i in range(0, len(text), step):
        part = text[i:i + size].strip()
        if part:
            chunks.append(part)
        if i + size >= len(text):
            break
    return chunks


def extract_text(filename: str, raw: bytes) -> str:
    ext = os.path.splitext(filename or "")[1].lower()
    if ext in (".txt", ".md"):
        return raw.decode("utf-8", errors="ignore")
    if ext == ".pdf":
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(raw))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if ext == ".docx":
        from docx import Document
        import io
        doc = Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)
    raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext or '未知'} (支持 txt/md/pdf/docx)")


def _embed_doc(doc_id: int) -> None:
    """后台向量化缺失切片并推进度 (独立会话, 失败标 failed)"""
    db = SessionLocal()
    try:
        doc = db.query(DocLibrary).filter(DocLibrary.id == doc_id).first()
        if not doc:
            return
        doc.status = "embedding"
        db.commit()
        chunks = db.query(DocChunk).filter(
            DocChunk.doc_id == doc_id, DocChunk.embedding.is_(None)).order_by(DocChunk.chunk_index).all()
        texts = [c.text for c in chunks]
        if texts:
            vecs = embedding_service.embed_texts(texts)
            for c, v in zip(chunks, vecs):
                c.embedding = json.dumps(v, ensure_ascii=False)
                doc.done_chunks = (doc.done_chunks or 0) + 1
                db.commit()
        doc.status = "done"
        db.commit()
    except Exception as e:
        try:
            doc = db.query(DocLibrary).filter(DocLibrary.id == doc_id).first()
            if doc:
                doc.status = "failed"
                doc.error = str(e)[:500]
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def retrieve_chunks(db: Session, query: str, doc_ids: Optional[List[int]] = None, limit: int = 6) -> List[dict]:
    """检索 top-k 切片 (本地 cosine; 云端替换为 TiDB Vector 查询即可)"""
    q = db.query(DocChunk).filter(DocChunk.embedding.isnot(None))
    if doc_ids:
        q = q.filter(DocChunk.doc_id.in_(doc_ids))
    rows = q.order_by(DocChunk.id.desc()).limit(2000).all()
    if not rows:
        return []
    qvec = embedding_service.embed_texts([query])
    if not qvec:
        return []
    cands = []
    for c in rows:
        try:
            vec = json.loads(c.embedding)
        except Exception:
            continue
        cands.append((c.id, vec))
    if not cands:
        return []
    top = embedding_service.top_k(qvec[0], cands, k=limit)
    by_id = {c.id: c for c in rows}
    names = {d.id: d.filename for d in db.query(DocLibrary).filter(
        DocLibrary.id.in_([by_id[i].doc_id for i, _ in top])).all()}
    return [_serialize_chunk(by_id[i], names.get(by_id[i].doc_id, ""), s) for i, s in top]


@router.post("/documents", response_model=ResponseModel[dict], status_code=201)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """上传私有文档并切片 (大文档后台向量化, 轮询状态看进度)"""
    filename = file.filename or "未命名"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"仅支持 {sorted(ALLOWED_EXTS)} 格式")
    raw = file.file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail="文件超过 10MB 上限")
    text = extract_text(filename, raw).strip()
    if not text:
        raise HTTPException(status_code=400, detail="文档内容为空，无法切片")
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads", "rag")
    os.makedirs(upload_dir, exist_ok=True)
    doc = DocLibrary(admin_id=admin.id, filename=filename, status="chunking")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    with open(os.path.join(upload_dir, f"{doc.id}_{filename}"), "wb") as f:
        f.write(raw)
    parts = split_text(text)
    chunk_rows = []
    for idx, part in enumerate(parts):
        c = DocChunk(doc_id=doc.id, chunk_index=idx, text=part)
        db.add(c)
        chunk_rows.append(c)
    doc.total_chunks = len(parts)
    doc.done_chunks = 0
    db.commit()
    if len(chunk_rows) <= 20:
        # 小文档同步向量化 (请求会话内完成, 可测无污染)
        try:
            vecs = embedding_service.embed_texts([c.text for c in chunk_rows])
            for c, v in zip(chunk_rows, vecs):
                c.embedding = json.dumps(v, ensure_ascii=False)
                doc.done_chunks = (doc.done_chunks or 0) + 1
            doc.status = "done"
            db.commit()
        except Exception as e:
            doc.status = "failed"
            doc.error = str(e)[:500]
            db.commit()
    else:
        background_tasks.add_task(_embed_doc, doc.id)
    db.refresh(doc)
    return ResponseModel(code=201, message=f"已上传并开始切片，共 {len(parts)} 块", data=_serialize_doc(doc))


@router.get("/documents", response_model=ResponseModel[dict])
def list_documents(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """文档列表 (超管全览, 他人仅看自传)"""
    q = db.query(DocLibrary)
    if admin.role != "super_admin":
        q = q.filter(DocLibrary.admin_id == admin.id)
    docs = q.order_by(DocLibrary.id.desc()).all()
    return ResponseModel(code=200, data={"items": [_serialize_doc(d) for d in docs]})


@router.get("/documents/{doc_id}", response_model=ResponseModel[dict])
def document_status(
    doc_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """文档切片进度"""
    return ResponseModel(code=200, data=_serialize_doc(_owned_doc(db, admin, doc_id)))


@router.delete("/documents/{doc_id}", response_model=ResponseModel[dict])
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """删除文档及切片 (归属校验, 显式双删)"""
    d = _owned_doc(db, admin, doc_id)
    db.query(DocChunk).filter(DocChunk.doc_id == d.id).delete()
    db.delete(d)
    db.commit()
    return ResponseModel(code=200, message="文档已删除", data={"id": doc_id})


@router.post("/search", response_model=ResponseModel[dict])
def search_chunks(
    data: RagSearchRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """检索切片 (出题人仅限自传文档, 超管全库)"""
    doc_ids = data.doc_ids
    if admin.role != "super_admin":
        own = [r[0] for r in db.query(DocLibrary.id).filter(DocLibrary.admin_id == admin.id).all()]
        doc_ids = [i for i in (doc_ids or own) if i in own]
        if not doc_ids:
            return ResponseModel(code=200, data={"items": []})
    items = retrieve_chunks(db, data.query, doc_ids=doc_ids, limit=data.limit)
    return ResponseModel(code=200, data={"items": items})


@router.get("/chunks", response_model=ResponseModel[dict])
def get_chunks(
    ids: str = Query(..., description="逗号分隔的 chunk id"),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """批量取块 (溯源抽屉用, 越权块自动过滤)"""
    try:
        wanted = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    except Exception:
        wanted = []
    if not wanted:
        return ResponseModel(code=200, data={"items": []})
    rows = db.query(DocChunk).filter(DocChunk.id.in_(wanted[:50])).all()
    allowed_docs = None
    if admin.role != "super_admin":
        allowed_docs = {r[0] for r in db.query(DocLibrary.id).filter(DocLibrary.admin_id == admin.id).all()}
    names = {d.id: d.filename for d in db.query(DocLibrary).filter(
        DocLibrary.id.in_([c.doc_id for c in rows])).all()}
    items = [_serialize_chunk(c, names.get(c.doc_id, ""))
             for c in rows if allowed_docs is None or c.doc_id in allowed_docs]
    items.sort(key=lambda x: wanted.index(x["id"]))
    return ResponseModel(code=200, data={"items": items})

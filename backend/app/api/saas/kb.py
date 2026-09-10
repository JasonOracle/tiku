"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[公私分权上传+列表；删除旧对话桩（统一走 AI 通道溯源对话）；上传写审计]
"""
import json
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_member
from app.api.saas.ops import write_audit
from app.models.saas import KbDocument, KbChunk, AiTenantConfig
from app.services.ai_service import get_embedding

router = APIRouter()


@router.post("/documents")
def upload_doc(file: UploadFile = File(...), scope: str = Form("private"),
               ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    tid = ctx["tenant_id"]
    role = ctx["role"]
    # 权限边界：成员强制 private
    if role == "member":
        scope = "private"
    if scope not in ("public", "private"):
        raise HTTPException(status_code=400, detail="scope 仅支持 public/private")
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "kb")
    os.makedirs(upload_dir, exist_ok=True)
    data = file.file.read()[:5 * 1024 * 1024]
    text = ""
    try:
        text = data.decode("utf-8", errors="ignore")[:20000]
    except Exception:
        text = ""
    doc = KbDocument(tenant_id=tid, scope=scope, creator_id=ctx["user"].id,
                     file_name=file.filename or "未命名", file_path="")
    db.add(doc)
    db.flush()
    # 简易切片：按500字一切；向量尽力而为（失败留空，检索回退 LIKE）
    chunks = [text[i:i + 500] for i in range(0, len(text), 500)][:20] or ["(空文档)"]
    prov = None
    try:
        cfg = db.query(AiTenantConfig).filter(AiTenantConfig.tenant_id == tid).first()
        if cfg and cfg.enabled and cfg.chat_api_key and cfg.chat_api_url:
            prov = {"name": f"Tenant#{tid}", "api_url": cfg.chat_api_url,
                    "api_key": cfg.chat_api_key, "model": cfg.chat_model or "default"}
    except Exception:
        prov = None
    for c in chunks:
        vec = None
        try:
            vec = get_embedding(c, provider=prov)
        except Exception:
            vec = None
        db.add(KbChunk(tenant_id=tid, document_id=doc.id, content=c,
                       embedding=json.dumps(vec) if vec else "[]"))
    db.flush()
    write_audit(db, tid, ctx["user"], "upload", "kb_document", doc.id,
                f"上传知识文档《{doc.file_name}》（{scope}）")
    db.commit()
    return {"code": 201, "message": "上传成功", "data": {"document_id": doc.id, "chunks": len(chunks)}}


@router.get("/documents")
def list_docs(ctx: dict = Depends(require_member), db: Session = Depends(get_db)):
    tid = ctx["tenant_id"]
    uid = ctx["user"].id
    role = ctx["role"]
    q = db.query(KbDocument).filter(KbDocument.tenant_id == tid)
    if role == "member":
        # 成员可见 public + 自己的 private
        docs = q.all()
        docs = [d for d in docs if d.scope == "public" or d.creator_id == uid]
    else:
        # 管理员可见 public + 自己 private（看不见成员 private）
        docs = [d for d in q.all() if d.scope == "public" or d.creator_id == uid]
    return {"code": 200, "data": {"items": [
        {"id": d.id, "file_name": d.file_name, "scope": d.scope} for d in docs]}}

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import os
import uuid
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.schemas.common import ResponseModel

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("", response_model=ResponseModel[dict])
async def upload_file(
    file: UploadFile = File(...),
    admin: Admin = Depends(get_current_admin)
):
    """B端图片/文件上传"""
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".xlsx"]
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="不支持的文件格式")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    url = f"/uploads/{filename}"
    return ResponseModel(code=200, message="上传成功", data={"url": url, "filename": filename})

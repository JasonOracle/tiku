"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[新建分类管理：资源/任务两用分类，租户隔离]
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict
from app.core.database import get_db
from app.api.deps import require_admin, require_member
from app.models.saas import ResourceCategory

router = APIRouter()


@router.get("")
def list_categories(ctx: dict = Depends(require_member), db: Session = Depends(get_db),
                    target_type: str = ""):
    q = db.query(ResourceCategory).filter(ResourceCategory.tenant_id == ctx["tenant_id"])
    if target_type:
        q = q.filter(ResourceCategory.target_type == target_type)
    items = q.order_by(ResourceCategory.sort_order, ResourceCategory.id).all()
    return {"code": 200, "data": {"items": [
        {"id": c.id, "name": c.name, "target_type": c.target_type} for c in items]}}


@router.post("", status_code=201)
def create_category(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                    db: Session = Depends(get_db)):
    name = str(payload.get("name") or "").strip()
    target = str(payload.get("target_type") or "resource")
    if not name:
        raise HTTPException(status_code=400, detail="分类名称必填")
    if target not in ("resource", "task"):
        target = "resource"
    c = ResourceCategory(tenant_id=ctx["tenant_id"], name=name, target_type=target)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"code": 201, "message": "分类创建成功", "data": {"id": c.id}}


@router.put("/{category_id}")
def update_category(category_id: int, payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                    db: Session = Depends(get_db)):
    c = db.query(ResourceCategory).filter(ResourceCategory.id == category_id,
                                           ResourceCategory.tenant_id == ctx["tenant_id"]).first()
    if not c:
        raise HTTPException(status_code=404, detail="分类不存在")
    name = str(payload.get("name") or "").strip()
    if name:
        c.name = name
    db.commit()
    return {"code": 200, "message": "修改成功"}


@router.delete("/{category_id}")
def delete_category(category_id: int, ctx: dict = Depends(require_admin),
                    db: Session = Depends(get_db)):
    c = db.query(ResourceCategory).filter(ResourceCategory.id == category_id,
                                           ResourceCategory.tenant_id == ctx["tenant_id"]).first()
    if not c:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(c)
    db.commit()
    return {"code": 200, "message": "已删除"}

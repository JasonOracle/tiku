"""
[变更日志]
修改时间：2026-09-12
AI模型：OpenCode / DeepSeek
修改内容：[权限隔离加固：list_categories 依赖由 require_member 收紧为 require_admin，分类配置仅管理员可读（经核实 C 端未调用分类接口）]
修改时间：2026-09-10
AI模型：Gemini 系列
修改内容：[1. list_categories 返回 sort_order 字段; 2. create_category 默认赋值当前最小 sort_order - 1 确保新增分类必定自动排在最上面; 3. 新增 PUT /reorder 批量拖拽排序更新接口]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[新建分类管理：资源/任务两用分类，租户隔离]
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, Dict, List
from app.core.database import get_db
from app.api.deps import require_admin
from app.models.saas import ResourceCategory

router = APIRouter()


@router.get("")
def list_categories(ctx: dict = Depends(require_admin), db: Session = Depends(get_db),
                    target_type: str = ""):
    q = db.query(ResourceCategory).filter(ResourceCategory.tenant_id == ctx["tenant_id"])
    if target_type:
        q = q.filter(ResourceCategory.target_type == target_type)
    items = q.order_by(ResourceCategory.sort_order.asc(), ResourceCategory.id.desc()).all()
    return {"code": 200, "data": {"items": [
        {"id": c.id, "name": c.name, "target_type": c.target_type, "sort_order": c.sort_order} for c in items]}}


@router.post("", status_code=201)
def create_category(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                    db: Session = Depends(get_db)):
    name = str(payload.get("name") or "").strip()
    target = str(payload.get("target_type") or "resource")
    if not name:
        raise HTTPException(status_code=400, detail="分类名称必填")
    if target not in ("resource", "task"):
        target = "resource"

    tid = ctx["tenant_id"]
    # 保证新增默认排在最上面：计算当前租户该类型下的最小 sort_order - 1
    min_sort = db.query(func.min(ResourceCategory.sort_order)).filter(
        ResourceCategory.tenant_id == tid,
        ResourceCategory.target_type == target
    ).scalar()
    first_sort = (min_sort - 1) if min_sort is not None else 1

    c = ResourceCategory(tenant_id=tid, name=name, target_type=target, sort_order=first_sort)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"code": 201, "message": "分类创建成功", "data": {"id": c.id, "sort_order": c.sort_order}}


@router.put("/reorder")
def reorder_categories(payload: Dict[str, Any], ctx: dict = Depends(require_admin),
                       db: Session = Depends(get_db)):
    """批量更新分类排序权重（支持前端直接上下拖拽调序）"""
    ids: List[int] = payload.get("category_ids") or []
    if not ids:
        return {"code": 200, "message": "排序已更新"}

    tid = ctx["tenant_id"]
    # 按照前端传递的顺序从 1 开始赋值 sort_order
    for index, cid in enumerate(ids):
        db.query(ResourceCategory).filter(
            ResourceCategory.id == cid,
            ResourceCategory.tenant_id == tid
        ).update({"sort_order": index + 1})
    db.commit()
    return {"code": 200, "message": "排序已保存"}


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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_admin
from app.models.user import Admin
from app.models.banner import Banner, BannerSetting
from app.schemas.banner import BannerCreate, BannerUpdate, BannerResponse, BannerSettingUpdate
from app.schemas.common import ResponseModel
from typing import List

router = APIRouter()

MAX_ENABLED = 3


def _check_link(data_link_type, data_link_value):
    lt = data_link_type or "none"
    if lt not in ("none", "external", "internal"):
        raise HTTPException(status_code=400, detail="无效的链接类型")
    if lt in ("external", "internal") and not (data_link_value or "").strip():
        raise HTTPException(status_code=400, detail="该链接类型必须填写链接地址")
    if lt == "internal" and not (data_link_value or "").strip().startswith("/"):
        raise HTTPException(status_code=400, detail="内部路径必须以 / 开头（如 /quiz?exam_id=1）")


def _check_enabled_limit(db: Session, exclude_id=None):
    n = db.query(Banner).filter(Banner.is_enabled == True)  # noqa: E712
    if exclude_id:
        n = n.filter(Banner.id != exclude_id)
    if n.count() >= MAX_ENABLED:
        raise HTTPException(status_code=400, detail=f"最多启用{MAX_ENABLED}张 Banner，请先停用其他")


@router.get("", response_model=ResponseModel[List[BannerResponse]])
def list_banners(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    items = db.query(Banner).order_by(Banner.sort_order.asc(), Banner.id.asc()).all()
    return ResponseModel(code=200, data=items)


@router.post("", response_model=ResponseModel[BannerResponse], status_code=201)
def create_banner(data: BannerCreate, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    _check_link(data.link_type, data.link_value)
    if data.is_enabled:
        _check_enabled_limit(db)
    b = Banner(
        image_url=data.image_url,
        link_type=data.link_type or "none",
        link_value=data.link_value or "",
        sort_order=data.sort_order or 0,
        is_enabled=data.is_enabled,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return ResponseModel(code=201, message="创建成功", data=b)


@router.get("/settings", response_model=ResponseModel[dict])
def get_settings(db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    s = db.query(BannerSetting).filter(BannerSetting.id == 1).first()
    return ResponseModel(code=200, data={"interval_seconds": s.interval_seconds if s else 4})


@router.put("/settings", response_model=ResponseModel[dict])
def update_settings(data: BannerSettingUpdate, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    s = db.query(BannerSetting).filter(BannerSetting.id == 1).first()
    if not s:
        s = BannerSetting(id=1, interval_seconds=data.interval_seconds)
        db.add(s)
    else:
        s.interval_seconds = data.interval_seconds
    db.commit()
    return ResponseModel(code=200, message="已保存", data={"interval_seconds": data.interval_seconds})


@router.put("/{banner_id}", response_model=ResponseModel[BannerResponse])
def update_banner(banner_id: int, data: BannerUpdate, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    b = db.query(Banner).filter(Banner.id == banner_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Banner 不存在")
    d = data.model_dump(exclude_unset=True)
    lt = d.get("link_type", b.link_type)
    lv = d.get("link_value", b.link_value)
    _check_link(lt, lv)
    if d.get("is_enabled") is True and not b.is_enabled:
        _check_enabled_limit(db, exclude_id=banner_id)
    for k, v in d.items():
        setattr(b, k, v)
    db.commit()
    db.refresh(b)
    return ResponseModel(code=200, message="更新成功", data=b)


@router.delete("/{banner_id}", response_model=ResponseModel[dict])
def delete_banner(banner_id: int, db: Session = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    b = db.query(Banner).filter(Banner.id == banner_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Banner 不存在")
    db.delete(b)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": banner_id})

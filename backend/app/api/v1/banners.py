from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.banner import Banner, BannerSetting
from app.schemas.banner import BannerListData
from app.schemas.common import ResponseModel

router = APIRouter()


@router.get("", response_model=ResponseModel[BannerListData])
def list_banners(db: Session = Depends(get_db)):
    """C端 Banner 列表（仅启用，按排序）"""
    items = db.query(Banner).filter(Banner.is_enabled == True).order_by(  # noqa: E712
        Banner.sort_order.asc(), Banner.id.asc()).all()
    s = db.query(BannerSetting).filter(BannerSetting.id == 1).first()
    return ResponseModel(code=200, data=BannerListData(
        interval_seconds=s.interval_seconds if s else 4,
        items=items,
    ))

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class BannerCreate(BaseModel):
    image_url: str = Field(..., description="图片路径")
    link_type: str = Field("none", description="链接类型: none, external, internal")
    link_value: Optional[str] = Field("", description="外链URL或站内路径")
    sort_order: Optional[int] = Field(0, description="排序")
    is_enabled: bool = Field(True, description="是否启用")


class BannerUpdate(BaseModel):
    image_url: Optional[str] = None
    link_type: Optional[str] = None
    link_value: Optional[str] = None
    sort_order: Optional[int] = None
    is_enabled: Optional[bool] = None


class BannerResponse(BaseModel):
    id: int
    image_url: str
    link_type: str = "none"
    link_value: Optional[str] = ""
    sort_order: int = 0
    is_enabled: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class BannerSettingUpdate(BaseModel):
    interval_seconds: int = Field(..., ge=2, le=10, description="轮播间隔秒 2-10")


class BannerListData(BaseModel):
    interval_seconds: int = 4
    items: List[BannerResponse] = []

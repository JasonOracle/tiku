from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class Banner(Base):
    """首页 Banner 模型（最多启用 3 张）"""
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_url = Column(String(255), nullable=False, comment="图片路径")
    link_type = Column(String(20), default="none", nullable=False, comment="链接类型: none, external, internal")
    link_value = Column(String(500), nullable=True, default="", comment="外链URL或站内路径")
    sort_order = Column(Integer, default=0, comment="排序（越小越靠前）")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class BannerSetting(Base):
    """Banner 全局设置单行表（id=1）"""
    __tablename__ = "banner_settings"

    id = Column(Integer, primary_key=True, autoincrement=False)
    interval_seconds = Column(Integer, default=4, comment="轮播间隔秒（2-10）")

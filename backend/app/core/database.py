from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from app.core.config import settings

# 创建 SQLAlchemy 数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类
Base = declarative_base()

def get_db() -> Generator:
    """
    FastAPI 依赖注入：获取数据库会话并在请求结束后自动关闭清理
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

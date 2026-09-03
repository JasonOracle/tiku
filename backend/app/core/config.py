import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "智题库 (TiKu) API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT 认证配置
    SECRET_KEY: str = "tiku_super_secret_jwt_key_2026_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    GRACE_PERIOD_MINUTES: int = 5  # 交卷宽限期 (分钟)
    
    # 数据库连接 (默认连接本地 Docker 启动的 MySQL 8.0)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:rootpassword@127.0.0.1:3306/tiku_db?charset=utf8mb4"
    )

    class Config:
        case_sensitive = True

settings = Settings()

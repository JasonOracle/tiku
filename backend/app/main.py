"""
[变更日志]
修改时间：2026-09-04 00:15:00
AI模型：Gemini 底层
修改内容：[1. main.py 增加数据库补列防护，确保 target_type, status, pass_percent 等物理列始终存在]
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.models import *  # 导入所有模型以触发自动建表

# 初始化数据库表结构
Base.metadata.create_all(bind=engine)

def auto_patch_db_columns():
    """安全补全已有表中可能缺失的新物理列"""
    try:
        with engine.connect() as conn:
            # 补全 exam_categories.target_type
            try:
                conn.execute(text("ALTER TABLE exam_categories ADD COLUMN target_type VARCHAR(20) NOT NULL DEFAULT 'exam'"))
                conn.commit()
            except Exception:
                pass

            # 补全 exams.pass_percent 与 status
            try:
                conn.execute(text("ALTER TABLE exams ADD COLUMN pass_percent INT DEFAULT 60"))
                conn.commit()
            except Exception:
                pass

            try:
                conn.execute(text("ALTER TABLE exams ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'draft'"))
                conn.commit()
            except Exception:
                pass

            # 补全 exams.category_name 快照列
            try:
                conn.execute(text("ALTER TABLE exams ADD COLUMN category_name VARCHAR(100) DEFAULT ''"))
                conn.commit()
            except Exception:
                pass

            # 补全 questions.score
            try:
                conn.execute(text("ALTER TABLE questions ADD COLUMN score INT DEFAULT 10"))
                conn.commit()
            except Exception:
                pass
    except Exception as e:
        pass

auto_patch_db_columns()

# C端路由
from app.api.v1.auth import router as v1_auth_router
from app.api.v1.categories import router as v1_categories_router
from app.api.v1.banners import router as v1_banners_router
from app.api.v1.exams import router as v1_exams_router
from app.api.v1.records import router as v1_records_router
from app.api.v1.favorites import router as v1_favorites_router

# B端路由
from app.api.admin.banners import router as admin_banners_router
from app.api.admin.admin_auth import router as admin_auth_router
from app.api.admin.questions import router as admin_questions_router
from app.api.admin.admin_exams import router as admin_exams_router
from app.api.admin.admin_categories import router as admin_categories_router
from app.api.admin.users import router as admin_users_router
from app.api.admin.upload import router as admin_upload_router



app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS 跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 C端 API 路由 (/api/v1/*)
app.include_router(v1_auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["C端认证"])
app.include_router(v1_categories_router, prefix=f"{settings.API_V1_STR}/categories", tags=["C端分类"])
app.include_router(v1_banners_router, prefix=f"{settings.API_V1_STR}/banners", tags=["C端Banner"])
app.include_router(v1_exams_router, prefix=f"{settings.API_V1_STR}/exams", tags=["C端试卷"])
app.include_router(v1_records_router, prefix=f"{settings.API_V1_STR}/records", tags=["C端答题与报告"])
app.include_router(v1_favorites_router, prefix=f"{settings.API_V1_STR}/favorites", tags=["C端收藏"])

# 挂载 B端 API 路由 (/api/v1/admin/*)
app.include_router(admin_auth_router, prefix=f"{settings.API_V1_STR}/admin/auth", tags=["B端认证"])
app.include_router(admin_banners_router, prefix=f"{settings.API_V1_STR}/admin/banners", tags=["B端Banner"])
app.include_router(admin_questions_router, prefix=f"{settings.API_V1_STR}/admin/questions", tags=["B端题海管理"])
app.include_router(admin_exams_router, prefix=f"{settings.API_V1_STR}/admin/exams", tags=["B端试卷管理"])
app.include_router(admin_categories_router, prefix=f"{settings.API_V1_STR}/admin/categories", tags=["B端分类管理"])
app.include_router(admin_users_router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["B端用户与明细"])
app.include_router(admin_upload_router, prefix=f"{settings.API_V1_STR}/admin/upload", tags=["B端文件上传"])

# 挂载静态文件目录
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/health", tags=["健康检查"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

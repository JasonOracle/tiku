"""
[变更日志]
修改时间：2026-09-06 19:00:00
AI模型：ZCode (GLM)
修改内容：[v1.3: auto_patch 新增 users 注册资料列 (nickname/gender/position/phone 唯一/email)]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[v1.2 Step1: auto_patch 新增 admins.created_by_id / admins.role 兜底 / exams.grading_mode 幂等补列]
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
    """安全补全已有表中可能缺失的新物理列 (幂等: 列已存在时静默跳过)"""
    patches = [
        # ---- v1.1 历史补列 ----
        "ALTER TABLE exam_categories ADD COLUMN target_type VARCHAR(20) NOT NULL DEFAULT 'exam'",
        "ALTER TABLE exams ADD COLUMN pass_percent INT DEFAULT 60",
        "ALTER TABLE exams ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'draft'",
        "ALTER TABLE exams ADD COLUMN category_name VARCHAR(100) DEFAULT ''",
        "ALTER TABLE exams ADD COLUMN is_random BOOLEAN DEFAULT FALSE",
        "ALTER TABLE questions ADD COLUMN score INT DEFAULT 10",
        # ---- v1.2 RBAC / 题库治理 ----
        "ALTER TABLE admins ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'admin'",
        "ALTER TABLE admins ADD COLUMN created_by_id INT NULL",
        "ALTER TABLE admins ADD COLUMN status BOOLEAN DEFAULT TRUE",
        "ALTER TABLE admins ADD COLUMN ai_quota_limit INT DEFAULT 0",
        "ALTER TABLE admins ADD COLUMN daily_ai_quota INT DEFAULT 0",
        "ALTER TABLE admins ADD COLUMN quota_reset_date DATE NULL",
        "ALTER TABLE questions ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE",
        "ALTER TABLE questions ADD COLUMN creator_id INT NULL",
        "ALTER TABLE questions ADD COLUMN source VARCHAR(20) DEFAULT 'manual'",
        "ALTER TABLE questions ADD COLUMN grading_points JSON NULL",
        # ---- v1.2 考试时间窗 / AI 全托管 / 试卷隔离 ----
        "ALTER TABLE exams ADD COLUMN start_time DATETIME NULL",
        "ALTER TABLE exams ADD COLUMN end_time DATETIME NULL",
        "ALTER TABLE exams ADD COLUMN is_ai_auto_grade BOOLEAN DEFAULT FALSE",
        "ALTER TABLE exams ADD COLUMN grading_mode VARCHAR(20) NOT NULL DEFAULT 'manual'",
        "ALTER TABLE exams ADD COLUMN creator_id INT NULL",
        # ---- v1.2 主观题阅卷 ----
        "ALTER TABLE exam_records ADD COLUMN ai_grading_result JSON NULL",
        "ALTER TABLE exam_records ADD COLUMN short_scores JSON NULL",
        # ---- v1.3 C端注册资料 ----
        "ALTER TABLE users ADD COLUMN nickname VARCHAR(50) NULL",
        "ALTER TABLE users ADD COLUMN gender VARCHAR(10) NULL",
        "ALTER TABLE users ADD COLUMN position VARCHAR(50) DEFAULT ''",
        "ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL",
        "ALTER TABLE users ADD COLUMN email VARCHAR(100) DEFAULT ''",
        "ALTER TABLE users ADD UNIQUE INDEX uix_users_phone (phone)",
    ]
    try:
        with engine.connect() as conn:
            for ddl in patches:
                try:
                    conn.execute(text(ddl))
                    conn.commit()
                except Exception:
                    pass  # 列已存在或 SQLite 等环境差异，静默跳过
    except Exception:
        pass

auto_patch_db_columns()

# C端路由
from app.api.v1.auth import router as v1_auth_router
from app.api.v1.categories import router as v1_categories_router
from app.api.v1.banners import router as v1_banners_router
from app.api.v1.exams import router as v1_exams_router
from app.api.v1.records import router as v1_records_router
from app.api.v1.favorites import router as v1_favorites_router
from app.api.v1.users import router as v1_users_router

# B端路由
from app.api.admin.banners import router as admin_banners_router
from app.api.admin.admin_auth import router as admin_auth_router
from app.api.admin.questions import router as admin_questions_router
from app.api.admin.admin_exams import router as admin_exams_router
from app.api.admin.admin_categories import router as admin_categories_router
from app.api.admin.users import router as admin_users_router
from app.api.admin.upload import router as admin_upload_router
from app.api.admin.admin_grading import router as admin_grading_router
from app.api.admin.admin_ai import router as admin_ai_router
from app.api.admin.admin_members import router as admin_members_router
from app.api.admin.admin_notifications import router as admin_notifications_router
from app.api.admin.admin_audit import router as admin_audit_router



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
app.include_router(v1_users_router, prefix=f"{settings.API_V1_STR}/users", tags=["C端用户"])

# 挂载 B端 API 路由 (/api/v1/admin/*)
app.include_router(admin_auth_router, prefix=f"{settings.API_V1_STR}/admin/auth", tags=["B端认证"])
app.include_router(admin_banners_router, prefix=f"{settings.API_V1_STR}/admin/banners", tags=["B端Banner"])
app.include_router(admin_questions_router, prefix=f"{settings.API_V1_STR}/admin/questions", tags=["B端题海管理"])
app.include_router(admin_exams_router, prefix=f"{settings.API_V1_STR}/admin/exams", tags=["B端试卷管理"])
app.include_router(admin_categories_router, prefix=f"{settings.API_V1_STR}/admin/categories", tags=["B端分类管理"])
app.include_router(admin_users_router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["B端用户与明细"])
app.include_router(admin_upload_router, prefix=f"{settings.API_V1_STR}/admin/upload", tags=["B端文件上传"])
app.include_router(admin_grading_router, prefix=f"{settings.API_V1_STR}/admin/grading", tags=["B端阅卷大厅"])
app.include_router(admin_ai_router, prefix=f"{settings.API_V1_STR}/admin/ai", tags=["B端AI员工"])
app.include_router(admin_members_router, prefix=f"{settings.API_V1_STR}/admin/members", tags=["B端成员与额度管理"])
app.include_router(admin_notifications_router, prefix=f"{settings.API_V1_STR}/admin/notifications", tags=["B端消息中心"])
app.include_router(admin_audit_router, prefix=f"{settings.API_V1_STR}/admin/audit", tags=["B端审计日志"])

# 挂载静态文件目录
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/health", tags=["健康检查"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

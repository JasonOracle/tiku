"""
[变更日志]
修改时间：2026-09-11
AI模型：Codex 3
修改内容：[lifespan 启动流程接入 db_migrate.ensure_schema()，幂等补齐存量库缺失列（当前为 resources.explanation），create_all 之后执行]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[彻底清洗：移除旧路由挂载与旧表补列，仅保留多租户 SaaS 路由]
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from contextlib import asynccontextmanager
from app.services.db_migrate import ensure_schema
from app.core.config import settings
from app.core.database import engine, Base
from app.models import *  # noqa: F401,F403 触发建表


def init_db_safely():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[Warning] DB init failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_safely()
    # 幂等增量迁移：存量库补列（新库 create_all 已建好时自动跳过）
    try:
        ensure_schema()
    except Exception as e:
        print(f"[Warning] schema migration failed: {e}")
    yield

# 统一登录
from app.api.v1.auth import router as v1_auth_router

# 多租户 SaaS 路由
from app.api.saas.members import router as saas_members_router
from app.api.saas.tasks import router as saas_tasks_router
from app.api.saas.member import router as saas_member_router
from app.api.saas.kb import router as saas_kb_router
from app.api.saas.super_admin import router as saas_super_router
from app.api.saas.ai import router as saas_ai_router
from app.api.saas.categories import router as saas_categories_router
from app.api.saas.ops import admin_router as saas_ops_admin_router
from app.api.saas.ops import member_router as saas_ops_member_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "智题库 (TiKu) API 服务已就绪",
        "docs": "/docs",
        "version": settings.VERSION
    }

# 配置 CORS 跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["统一登录"])

# 成员与组织
app.include_router(saas_members_router, prefix=f"{settings.API_V1_STR}/admin/members", tags=["成员管理"])
# 分类
app.include_router(saas_categories_router, prefix=f"{settings.API_V1_STR}/admin/categories", tags=["分类管理"])
app.include_router(saas_categories_router, prefix=f"{settings.API_V1_STR}/member/categories", tags=["成员分类"])
# 资源与任务（含成员待办/提交/核验）
app.include_router(saas_tasks_router, prefix=f"{settings.API_V1_STR}/admin", tags=["资源与任务"])
app.include_router(saas_tasks_router, prefix=f"{settings.API_V1_STR}/member", tags=["成员任务"])
# 成员闭环（作答入口/我的提交/成绩/收藏）
app.include_router(saas_member_router, prefix=f"{settings.API_V1_STR}/member", tags=["成员闭环"])
# 知识库
app.include_router(saas_kb_router, prefix=f"{settings.API_V1_STR}/admin/kb", tags=["知识库"])
app.include_router(saas_kb_router, prefix=f"{settings.API_V1_STR}/member/kb", tags=["成员知识库"])
# AI 通道（出题/组卷/核验/对话，强制溯源）
app.include_router(saas_ai_router, prefix=f"{settings.API_V1_STR}/admin/ai", tags=["AI协同"])
app.include_router(saas_ai_router, prefix=f"{settings.API_V1_STR}/member/ai", tags=["成员AI协同"])
# 运营底座（看板/横幅/上传/通知/审计）
app.include_router(saas_ops_admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["运营管理"])
app.include_router(saas_ops_member_router, prefix=f"{settings.API_V1_STR}/member", tags=["成员运营"])
# 上帝视图
app.include_router(saas_super_router, prefix=f"{settings.API_V1_STR}/super-admin", tags=["上帝视图"])

# 挂载静态文件目录
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/health", tags=["健康检查"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

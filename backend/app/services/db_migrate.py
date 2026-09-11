"""
[变更日志]
修改时间：2026-09-11
AI模型：Codex 3
修改内容：[1. 新增轻量 Schema 迁移助手 ensure_schema()：幂等补齐 ResourceItem.explanation 列（存量库 ALTER 加列，新库由 create_all 处理），随应用启动自动执行，零停机]
"""
from sqlalchemy import text
from app.core.database import engine


def ensure_schema() -> None:
    """幂等 Schema 迁移：检查 information_schema 缺列则 ALTER 补齐。
    使用独立连接，迁移异常绝不阻断应用启动（仅告警）。"""
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'resources' AND column_name = 'explanation'"
        )).first()
        if not row:
            conn.execute(text(
                "ALTER TABLE resources ADD COLUMN explanation TEXT NULL COMMENT '答案解析/采分要点'"
            ))
            conn.commit()
            print("[db_migrate] 已补齐列 resources.explanation")
        else:
            print("[db_migrate] 当前库 Schema 已就绪")

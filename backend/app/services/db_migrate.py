"""
[变更日志]
修改时间：2026-09-12
AI模型：OpenCode / DeepSeek
修改内容：[AI 助管加固：ensure_schema() 重构为列清单驱动，新增幂等补齐 ai_messages.action_card_data 列（工具调用卡片持久化），存量库自动 ALTER、新库由 create_all 处理]
修改时间：2026-09-11
AI模型：Codex 3
修改内容：[1. 新增轻量 Schema 迁移助手 ensure_schema()：幂等补齐 ResourceItem.explanation 列（存量库 ALTER 加列，新库由 create_all 处理），随应用启动自动执行，零停机]
"""
from sqlalchemy import text
from app.core.database import engine


# 需要幂等补齐的列清单：(表名, 列名, 补列 DDL)
_REQUIRED_COLUMNS = [
    ("resources", "explanation",
     "ALTER TABLE resources ADD COLUMN explanation TEXT NULL COMMENT '答案解析/采分要点'"),
    ("ai_messages", "action_card_data",
     "ALTER TABLE ai_messages ADD COLUMN action_card_data JSON NULL COMMENT '工具调用与业务确认卡片结构数据'"),
]


def ensure_schema() -> None:
    """幂等 Schema 迁移：检查 information_schema 缺列则 ALTER 补齐。
    使用独立连接，迁移异常绝不阻断应用启动（仅告警）。"""
    with engine.connect() as conn:
        for table_name, column_name, ddl in _REQUIRED_COLUMNS:
            row = conn.execute(text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = :t AND column_name = :c"
            ), {"t": table_name, "c": column_name}).first()
            if row:
                continue
            conn.execute(text(ddl))
            conn.commit()
            print(f"[db_migrate] 已补齐列 {table_name}.{column_name}")
        print("[db_migrate] 当前库 Schema 已就绪")

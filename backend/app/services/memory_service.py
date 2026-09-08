"""
[变更日志]
修改时间：2026-09-08
AI模型：Muse Spark
修改内容：[v1.3 任务2: Mem0 长期记忆服务 (User_ID 画像提取/检索注入, 本地 fastembed+qdrant, 失败静默降级)]
"""
import os
from typing import List

_client = None
_disabled_reason = ""


def is_enabled() -> bool:
    """总开关 (测试/应急: MEM0_ENABLED=0 关闭)"""
    return os.getenv("MEM0_ENABLED", "1") == "1"


def user_key(admin_id: int) -> str:
    return f"admin:{admin_id}"


def get_client():
    """懒加载单例；LLM 复用系统 AI 网关首选通道，embeddings 走本地 fastembed"""
    global _client, _disabled_reason
    if _client is not None:
        return _client
    if not is_enabled():
        _disabled_reason = "disabled by MEM0_ENABLED"
        return None
    try:
        from mem0 import Memory
        from app.services import ai_service

        cfg = ai_service.get_ai_config()
        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mem0")
        os.makedirs(data_dir, exist_ok=True)
        model = os.getenv("MEM0_MODEL") or cfg.get("model") or "dots3-note-prev"
        _client = Memory.from_config({
            "version": "v1.1",
            "embedder": {
                "provider": "fastembed",
                "config": {"model": os.getenv("MEM0_EMBED_MODEL", "BAAI/bge-small-zh-v1.5")},
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {"collection_name": "tiku_memories", "path": os.path.join(data_dir, "qdrant")},
            },
            "llm": {
                "provider": "openai",
                "config": {
                    "model": model,
                    "api_key": cfg.get("api_key") or "sk-local",
                    "openai_base_url": (cfg.get("api_url") or "").rsplit("/chat/completions", 1)[0]
                    or "https://note3-prev-api.askdiandian.com/v1",
                },
            },
            "history_db_path": os.path.join(data_dir, "history.db"),
        })
        return _client
    except Exception as e:
        _disabled_reason = str(e)[:200]
        return None


def remember(admin_id: int, user_text: str, assistant_text: str) -> None:
    """后台静默提取偏好记忆，失败不抛"""
    try:
        client = get_client()
        if client is None:
            return
        client.add(
            [{"role": "user", "content": user_text}, {"role": "assistant", "content": assistant_text}],
            user_id=user_key(admin_id),
        )
    except Exception:
        pass


def recall(admin_id: int, query: str, limit: int = 3) -> str:
    """检索长期记忆并拼装为 Prompt 片段，失败返回空串"""
    try:
        client = get_client()
        if client is None:
            return ""
        hits = client.search(query, user_id=user_key(admin_id), limit=limit) or []
        lines = []
        for h in hits:
            text = h.get("memory") if isinstance(h, dict) else str(h)
            if text:
                lines.append(f"- {text}")
        if not lines:
            return ""
        return "【长期记忆·该用户的教学偏好】\n" + "\n".join(lines) + "\n请在回答/出题中自然体现以上偏好。"
    except Exception:
        return ""

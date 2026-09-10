"""
[变更日志]
修改时间：2026-09-10
AI模型：Gemini 系列
修改内容：[落地本地 Mem0 长期记忆服务: 1. 采用本地轻量嵌入式 Qdrant + fastembed(BAAI/bge-small-zh-v1.5 512维) + Dots 模型闭环运行，零外部生产依赖; 2. 严格多租户隔离(tenant:X:user:Y); 3. 异步非阻塞写入; 4. 支持用户删除时彻底销毁记忆(delete_all)]
"""
import os
import threading
from typing import List, Optional
from app.services import ai_service

_client = None
_init_lock = threading.Lock()


def is_enabled() -> bool:
    """长期记忆总开关 (可通过 MEM0_ENABLED=0 关闭)"""
    return os.getenv("MEM0_ENABLED", "1") == "1"


def get_user_key(tenant_id: int, user_id: int) -> str:
    """多租户隔离用户唯一标识"""
    return f"tenant:{tenant_id}:user:{user_id}"


def get_client():
    """获取本地持久化 Mem0 单例客户端"""
    global _client
    if _client is not None:
        return _client
    if not is_enabled():
        return None

    with _init_lock:
        if _client is not None:
            return _client
        try:
            from mem0 import Memory

            # 存储在已映射持久化的 /app/app/data/mem0 目录下
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mem0")
            os.makedirs(data_dir, exist_ok=True)

            cfg = ai_service.get_ai_config()
            model = os.getenv("MEM0_MODEL") or cfg.get("model") or "dots3-note-prev"
            api_key = cfg.get("api_key") or "ak_KC3HqpqQsgU5yWr4pfGzDrYhMTWiI"
            api_url = cfg.get("api_url") or "https://note3-prev-api.askdiandian.com/v1"
            base_url = api_url.rsplit("/chat/completions", 1)[0]

            _client = Memory.from_config({
                "version": "v1.1",
                "embedder": {
                    "provider": "fastembed",
                    "config": {
                        "model": os.getenv("MEM0_EMBED_MODEL", "BAAI/bge-small-zh-v1.5")
                    }
                },
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "path": os.path.join(data_dir, "qdrant"),
                        "embedding_model_dims": 512
                    }
                },
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": model,
                        "api_key": api_key,
                        "openai_base_url": base_url
                    }
                },
                "history_db_path": os.path.join(data_dir, "history.db")
            })
            return _client
        except Exception as e:
            print(f"[Mem0 Init Error]: {e}")
            return None


def recall(tenant_id: int, user_id: int, query: str, limit: int = 3) -> str:
    """
    语义召回长期记忆，并拼装为 Prompt 片段。
    完全在本地执行，失败时静默返回空串，绝不影响主对话流程。
    """
    if not is_enabled() or not query.strip():
        return ""
    try:
        client = get_client()
        if client is None:
            return ""
        user_key = get_user_key(tenant_id, user_id)
        # mem0 v2 必须使用 filters={"user_id": ...}
        hits_data = client.search(query.strip(), filters={"user_id": user_key}, limit=limit)
        results = hits_data.get("results") if isinstance(hits_data, dict) else hits_data
        if not results or not isinstance(results, list):
            return ""

        lines: List[str] = []
        for item in results:
            if isinstance(item, dict):
                mem_text = item.get("memory") or item.get("text") or ""
                if mem_text and mem_text.strip():
                    lines.append(f"- {mem_text.strip()}")
            elif isinstance(item, str) and item.strip():
                lines.append(f"- {item.strip()}")

        if not lines:
            return ""
        return "【该用户的历史交流偏好与习惯记忆（跨会话）】:\n" + "\n".join(lines)
    except Exception as e:
        print(f"[Mem0 Recall Error]: {e}")
        return ""


def remember_async(tenant_id: int, user_id: int, user_text: str, assistant_text: str) -> None:
    """
    在独立后台线程中异步提炼长期记忆并持久化，不阻塞任何主线程与 SSE 流。
    纯参数传递，不持有任何 SQLAlchemy 数据库连接，彻底杜绝连接泄露。
    """
    if not is_enabled():
        return

    # 过滤掉系统内部控制消息、空消息或极短指令
    u_text = (user_text or "").strip()
    a_text = (assistant_text or "").strip()
    if not u_text or not a_text or len(u_text) < 2 or u_text.startswith("[系统消息]"):
        return

    def _worker(tid: int, uid: int, u: str, a: str):
        try:
            client = get_client()
            if client is None:
                return
            user_key = get_user_key(tid, uid)
            client.add(
                [
                    {"role": "user", "content": u},
                    {"role": "assistant", "content": a[:500]}
                ],
                user_id=user_key
            )
        except Exception as e:
            print(f"[Mem0 Remember Error]: {e}")

    t = threading.Thread(target=_worker, args=(tenant_id, user_id, u_text, a_text), daemon=True)
    t.start()


def delete_all_user_memories(tenant_id: int, user_id: int) -> None:
    """当用户被彻底删除/销毁时，级联清理其在本地 Mem0 中的全部向量记忆"""
    try:
        client = get_client()
        if client is None:
            return
        user_key = get_user_key(tenant_id, user_id)
        client.delete_all(filters={"user_id": user_key})
    except Exception as e:
        print(f"[Mem0 DeleteAll Error]: {e}")

"""
[变更日志]
修改时间：2026-09-08
AI模型：Muse Spark
修改内容：[v1.3 任务3: 本地向量服务 (fastembed 懒加载单例, cosine 检索, 可 monkeypatch 测试)]
"""
import math
from typing import List

_model = None
_model_name = ""


def _get_model():
    global _model, _model_name
    if _model is None:
        from fastembed import TextEmbedding
        import os
        name = os.getenv("RAG_EMBED_MODEL", "BAAI/bge-small-zh-v1.5")
        _model = TextEmbedding(model_name=name)
        _model_name = name
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """批量向量化 (空输入返回空列表)"""
    texts = [t for t in (texts or []) if t and t.strip()]
    if not texts:
        return []
    model = _get_model()
    return [list(map(float, v)) for v in model.embed(texts)]


def cosine(a: List[float], b: List[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0 or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def top_k(query_vec: List[float], candidates: List[tuple], k: int = 6) -> List[tuple]:
    """candidates: [(id, vec), ...] -> 按相似度取 top-k [(id, score)]"""
    scored = [(cid, cosine(query_vec, vec)) for cid, vec in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:max(1, k)]

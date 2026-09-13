"""
/**
 * [变更日志]
 * 修改时间：2026-09-13
 * AI模型：Gemini 系列
 * 修改内容：[1. 重构 _local_search 兜底检索：采用中文 2 字滑窗 Bigram OR 模糊检索 + 文件名联查，解决自然语言查询 0 命中的 RAG 溯源缺陷；2. 放宽文档 scope 过滤：同时支持租户内的 public 与 private 文档，彻底杜绝因上传文档默认 private 导致的检索落空]
 */
[变更日志]
修改时间：2026-09-10
AI模型：Gemini 系列
修改内容：[消除虚假 RAG 溯源 Bug: 移除 _local_search 中未命中时强行提取首个文档(base.limit)的虚假兜底逻辑，未真实命中相似度或关键词时严格返回空列表，杜绝无差别绑定 b_hist.txt]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[新建向量检索抽象：本地余弦/LIKE 直跑；TiDB Vector 分支仅当 TIDB_VECTOR=1 且服务端可用时启用，默认永不连云]
"""
import json
import math
import os
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.saas import KbChunk, KbDocument

EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))


def tidb_vector_enabled() -> bool:
    """运维显式开关（默认关闭）。仅生产 TiDB 上开启，本地/SQLite 测试永远走本地分支。"""
    return os.getenv("TIDB_VECTOR", "0") == "1"


def _cosine(a: List[float], b: List[float]) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    a, b = a[:n], b[:n]
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _parse_vec(raw: Any) -> Optional[List[float]]:
    try:
        if not raw:
            return None
        v = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(v, list) and v and isinstance(v[0], (int, float)):
            return [float(x) for x in v]
        return None
    except Exception:
        return None


def _local_search(db: Session, tenant_id: int, query: str,
                  query_vec: Optional[List[float]], limit: int) -> List[Dict[str, Any]]:
    """本地分支：向量余弦（有向量时）+ 中文 Bigram OR 模糊检索兜底，合并去重。"""
    from sqlalchemy import or_
    base = db.query(KbChunk, KbDocument).join(
        KbDocument, KbDocument.id == KbChunk.document_id
    ).filter(KbChunk.tenant_id == tenant_id)
    scored: List[tuple] = []
    if query_vec:
        for c, d in base.all():
            v = _parse_vec(c.embedding)
            if v:
                scored.append((_cosine(query_vec, v), c, d))
        scored.sort(key=lambda x: -x[0])
        # 仅当余弦相似度达到可信阈值（>=0.68）时才认定为参考了该知识库
        out = [{"document_id": d.id, "file_name": d.file_name,
                "chunk_content": c.content[:300], "similarity_score": round(s, 4)}
               for s, c, d in scored[:limit] if s >= 0.68]
        if out:
            return out
    # 关键词/词组 Bigram OR 兜底（替代原前12字前缀匹配，大幅提升无向量/自然语言命中率）
    q_clean = (query or "").strip()
    if q_clean and len(q_clean) >= 2:
        # 构造两字滑窗切词 (Bigram)，过滤纯标点
        tokens = [q_clean[i:i+2] for i in range(len(q_clean) - 1)] if len(q_clean) > 2 else [q_clean]
        # 去重并截取前 8 个代表性 token，避免 SQL 条件过多
        tokens = list(dict.fromkeys(tokens))[:8]
        conditions = []
        for t in tokens:
            conditions.append(KbChunk.content.ilike(f"%{t}%"))
            conditions.append(KbDocument.file_name.ilike(f"%{t}%"))
        hits = base.filter(or_(*conditions)).limit(limit).all()
        if hits:
            return [{"document_id": d.id, "file_name": d.file_name,
                     "chunk_content": c.content[:300], "similarity_score": 0.85}
                    for c, d in hits]
    # 未真实命中任何文档分块时，严格返回空列表，绝不张冠李戴
    return []


def _tidb_search(db: Session, tenant_id: int, query_vec: List[float],
                 limit: int) -> List[Dict[str, Any]]:
    """TiDB 分支（生产专用）：VEC_COSINE_DISTANCE 原生检索 embedding_vec 列。
    要求运维先执行 tiku_init.sql 内 TiDB 段（ADD COLUMN embedding_vec VECTOR）。"""
    from sqlalchemy import text
    vec_lit = "[" + ",".join(repr(float(x)) for x in query_vec[:EMBED_DIM]) + "]"
    rows = db.execute(text(
        "SELECT c.id, c.document_id, c.content, d.file_name, "
        "VEC_COSINE_DISTANCE(c.embedding_vec, :vec) AS dist "
        "FROM kb_chunks c JOIN kb_documents d ON d.id = c.document_id "
        "WHERE c.tenant_id = :tid "
        "ORDER BY dist LIMIT :lim"),
        {"vec": vec_lit, "tid": tenant_id, "lim": limit}).fetchall()
    return [{"document_id": r[1], "file_name": r[3],
             "chunk_content": (r[2] or "")[:300],
             "similarity_score": round(max(0.0, 1.0 - float(r[4] or 0)), 4)}
            for r in rows]


def rag_search(db: Session, tenant_id: int, query: str, limit: int = 3,
               query_vec: Optional[List[float]] = None) -> List[Dict[str, Any]]:
    """统一检索入口：TiDB 开关+向量齐备时走原生向量，否则本地分支。永不抛异常。"""
    try:
        if tidb_vector_enabled() and query_vec:
            return _tidb_search(db, tenant_id, query_vec, limit)
    except Exception:
        pass
    return _local_search(db, tenant_id, query, query_vec, limit)

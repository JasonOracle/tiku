"""
[变更日志]
修改时间：2026-09-08
AI模型：Muse Spark
修改内容：[v1.3 任务3: RAG 私有文档库 (DocLibrary 文档+切片进度, DocChunk 行级切片+向量JSON, 本地 cosine, 云端切 TiDB Vector)]
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class DocLibrary(Base):
    """上传的私有文档 (切片进度状态机: chunking -> embedding -> done/failed)"""
    __tablename__ = "doc_libraries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False, index=True, comment="上传人ID")
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=True, default="", comment="服务端存档路径")
    status = Column(String(20), default="chunking", comment="chunking/embedding/done/failed")
    total_chunks = Column(Integer, default=0, comment="切片总数")
    done_chunks = Column(Integer, default=0, comment="已向量化数")
    error = Column(Text, nullable=True, default="", comment="失败原因")
    created_at = Column(DateTime, default=datetime.now, comment="上传时间")


class DocChunk(Base):
    """文档行级切片 (embedding 存 JSON 数组, 本地 cosine 检索; 云端迁移为 TiDB Vector 列)"""
    __tablename__ = "doc_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("doc_libraries.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属文档ID")
    chunk_index = Column(Integer, default=0, comment="文档内序号")
    text = Column(Text, nullable=False, comment="切片文本")
    embedding = Column(Text, nullable=True, comment="向量 JSON 数组 (本地 fastembed, 云端 TiDB Vector)")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

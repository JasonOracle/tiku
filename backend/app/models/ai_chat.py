"""
[变更日志]
修改时间：2026-09-07
AI模型：OpenCode / Cursor / 协同架构师
修改内容：[新增 AI 智能助管持久化会话表与行级单调游标消息流水表]
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class AiChatSession(Base):
    """AI 助管会话 (一管理员多会话, 按 updated_at 倒序即最近活跃)"""
    __tablename__ = "ai_chat_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属管理员ID")
    title = Column(String(120), nullable=False, default="新对话", comment="会话标题")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True, comment="最近活跃时间")


class AiChatMessage(Base):
    """AI 助管行级消息流水 (id 天然单调自增游标, 供向上翻页)"""
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # 天然单调自增游标
    session_id = Column(Integer, ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属会话ID")
    role = Column(String(20), nullable=False, comment="角色: user | assistant | system")
    content = Column(Text, nullable=False, comment="消息正文")
    quote = Column(Text, nullable=True, comment="引用文本")
    action_card_data = Column(JSON, nullable=True, comment="动作卡片数据及状态机")
    action_list_data = Column(JSON, nullable=True, comment="操作路由待办卡数据")
    created_at = Column(DateTime, default=datetime.now, index=True, comment="发送时间")

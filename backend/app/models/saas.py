"""
[变更日志]
修改时间：2026-09-12
AI模型：OpenCode / DeepSeek
修改内容：[AI 助管加固：AiMessage 新增 action_card_data(JSON) 列，持久化工具调用交互卡片结构（工具名/参数/风险等级/执行状态），修复刷新或二次进入会话后出题/组卷确认卡片丢失的缺陷]
修改时间：2026-09-11
AI模型：Codex 3
修改内容：[ResourceItem 新增 explanation 列：持久化题目答案解析/采分要点，支撑 B 端出题表单、AI 出题/组卷与 C 端成绩报告解析闭环]
修改时间：2026-09-11
AI模型：Gemini 系列
修改内容：[在 ResourceItem 模型中新增 source 字段 (ai/manual/import)，准确持久化与区分 AI 出题、人工录入与 Excel 导入数据来源]
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[新建多租户 SaaS 底座模型：租户/用户/关联+资源/任务/记录/知识库，全部强制 tenant_id 隔离，兼容旧 exams/questions 表]
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, UniqueConstraint
from datetime import datetime
from app.core.database import Base


class SysTenant(Base):
    """租户/组织载体"""
    __tablename__ = "sys_tenant"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="企业/组织名称")
    short_name = Column(String(50), nullable=True, comment="企业简称")
    industry = Column(String(50), nullable=True, comment="所属行业")
    scale = Column(String(20), nullable=True, comment="规模：初创/中小/中型/大型/集团")
    contact_name = Column(String(50), nullable=True, comment="联系人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    remark = Column(String(255), nullable=True, comment="备注")
    status = Column(String(20), default="active", comment="active/disabled")
    created_at = Column(DateTime, default=datetime.now)


class SysUser(Base):
    """用户登录凭证表：仅凭证+上帝标识，绝不带租户业务字段"""
    __tablename__ = "sys_user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号全局唯一")
    username = Column(String(50), nullable=True, comment="兼容旧账号")
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(50), nullable=True, default="", comment="成员展示名")
    is_super_admin = Column(Boolean, default=False, comment="上帝视角标识")
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class SysTenantUser(Base):
    """枢纽关联表：用户在特定租户下的身份"""
    __tablename__ = "sys_tenant_user"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uix_tenant_user"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), default="member", comment="owner/admin/member")
    status = Column(String(20), default="active", comment="active/disabled")
    created_at = Column(DateTime, default=datetime.now)


class SysUserProfile(Base):
    """用户扩展资料表（一对一挂 sys_user，凭证仍只在 sys_user）"""
    __tablename__ = "sys_user_profile"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id", ondelete="CASCADE"),
                     nullable=False, unique=True, index=True, comment="一对一：sys_user.id")
    nickname = Column(String(50), nullable=True, comment="昵称")
    email = Column(String(100), nullable=True, comment="邮箱")
    occupation = Column(String(100), nullable=True, comment="职业")
    bio = Column(Text, nullable=True, comment="个人简介")
    age = Column(Integer, nullable=True, comment="年龄")
    gender = Column(String(10), nullable=True, comment="male/female/secret")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ResourceCategory(Base):
    """资源/任务分类（租户隔离）"""
    __tablename__ = "resource_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    target_type = Column(String(20), default="resource", comment="resource/task")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class ResourceItem(Base):
    """条目/资源（原题目通用化），全部挂载 tenant_id"""
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("resource_categories.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(20), nullable=False, default="single_choice", comment="single_choice/multiple/fill/short等")
    content = Column(Text, nullable=False, comment="条目题干/事务描述")
    options = Column(JSON, nullable=True)
    correct_answer = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True, comment="答案解析/采分要点（AI生成或人工录入，C端报告与阅卷参考）")
    score = Column(Integer, default=10)
    creator_id = Column(Integer, ForeignKey("sys_user.id", ondelete="SET NULL"), nullable=True)
    is_deleted = Column(Boolean, default=False)
    source = Column(String(20), default="manual", comment="来源：ai/manual/import")
    ai_rag_sources = Column(JSON, nullable=True, comment="切片级溯源 [{document_id,file_name,chunk_content,similarity_score}]")
    created_at = Column(DateTime, default=datetime.now)


class Task(Base):
    """任务/测评（原试卷通用化）"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True, default="")
    cover_image = Column(String(500), nullable=True, default="")
    category_id = Column(Integer, ForeignKey("resource_categories.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="draft", comment="draft/published/archived")
    is_timed = Column(Boolean, default=False)
    time_limit = Column(Integer, nullable=True, comment="分钟")
    start_time = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True, comment="结束时间=api契约deadline")
    verification_mode = Column(String(20), default="manual", comment="manual/ai_auto")
    creator_id = Column(Integer, ForeignKey("sys_user.id", ondelete="SET NULL"), nullable=True)
    ai_rag_sources = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class TaskResource(Base):
    """任务-条目关联"""
    __tablename__ = "task_resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, default=10)
    sort_order = Column(Integer, default=0)


class TaskRecord(Base):
    """成员任务提交记录（悲观锁防重交）"""
    __tablename__ = "task_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), default="pending", comment="pending/submitted/pending_verification/verified")
    score = Column(Integer, nullable=True)
    time_spent = Column(Integer, default=0)
    answers = Column(JSON, nullable=True)
    ai_result = Column(JSON, nullable=True)
    ai_rag_sources = Column(JSON, nullable=True)
    comments = Column(String(500), nullable=True, default="")
    created_at = Column(DateTime, default=datetime.now)
    submit_time = Column(DateTime, nullable=True)


class KbDocument(Base):
    """知识库文档元数据（公私分权）"""
    __tablename__ = "kb_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    scope = Column(String(20), default="private", comment="public/private")
    creator_id = Column(Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True, default="")
    status = Column(String(20), default="done")
    created_at = Column(DateTime, default=datetime.now)


class KbChunk(Base):
    """文档切片向量（本地TEXT存JSON，云端切TiDB Vector）"""
    __tablename__ = "kb_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("kb_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True, comment="向量JSON，云端为VECTOR列")
    created_at = Column(DateTime, default=datetime.now)


class ResourceFavorite(Base):
    """成员条目收藏（租户隔离）"""
    __tablename__ = "resource_favorites"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", "resource_id",
                                       name="uix_fav_tenant_user_resource"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)


class Banner(Base):
    """首页横幅（租户隔离）"""
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    link_type = Column(String(20), default="none")
    link_value = Column(String(500), nullable=True, default="")
    sort_order = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class BannerSetting(Base):
    """横幅轮播配置（每租户一行）"""
    __tablename__ = "banner_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"),
                       nullable=False, unique=True, index=True)
    interval_seconds = Column(Integer, default=4)


class Notification(Base):
    """站内通知（租户隔离到人）"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True, default="")
    notif_type = Column(String(30), nullable=True, default="system")
    link = Column(String(255), nullable=True, default="")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class AiSession(Base):
    """AI 对话会话（租户隔离到人）"""
    __tablename__ = "ai_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), default="新对话")
    created_at = Column(DateTime, default=datetime.now)


class AiMessage(Base):
    """AI 对话消息（含 RAG 溯源持久化）"""
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    rag_sources = Column(JSON, nullable=True)
    action_card_data = Column(JSON, nullable=True)  # 工具调用与业务确认卡片结构（持久化卡片状态）
    created_at = Column(DateTime, default=datetime.now)


class AiTenantConfig(Base):
    """租户级 AI 网关覆盖（为空则继承服务端环境变量；keys 落库，读取时脱敏）"""
    __tablename__ = "ai_tenant_config"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"),
                       nullable=False, unique=True, index=True)
    enabled = Column(Boolean, default=True, comment="租户 AI 总开关")
    chat_api_url = Column(String(500), nullable=True, default="")
    chat_api_key = Column(String(500), nullable=True, default="")
    chat_model = Column(String(100), nullable=True, default="")
    embed_model = Column(String(100), nullable=True, default="")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AuditLog(Base):
    """审计留痕（租户隔离）"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("sys_tenant.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("sys_user.id", ondelete="SET NULL"), nullable=True)
    actor_name = Column(String(50), nullable=True, default="")
    operator_type = Column(String(20), default="member")
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=True, default="")
    target_id = Column(Integer, nullable=True)
    summary = Column(String(255), nullable=True, default="")
    created_at = Column(DateTime, default=datetime.now)

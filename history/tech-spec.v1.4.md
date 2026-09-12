# 智题库 (TiKu) v1.4+ 技术规格说明书 (Technical Specification)

## 1. 架构总览与标准项目结构
系统基于前后端分离的多租户 SaaS 架构，技术栈与核心代码组织如下：

```
tiku/
├── toc/                     # C端成员答题中心 (Web/H5) - Vue3 + Vite + Pinia
├── tob/                     # B端SaaS管理中台 - Vue3 + Element Plus + Ant Design X 风格
├── backend/                 # 核心 API 后端 - FastAPI (Python 3.12)
│   ├── app/
│   │   ├── api/             # 路由层 (统一挂载至 /api/v1/saas/*)
│   │   │   ├── saas/        # 纯 SaaS 模块 (members, tasks, kb, ai, ops, etc.)
│   │   │   └── deps.py      # 多租户依赖注入与鉴权
│   │   ├── core/            # JWT 认证、中间件与数据库连接
│   │   ├── models/          # 纯 SaaS 数据库实体 (SysTenant, SysUser, Task, ResourceItem, etc.)
│   │   └── services/        # 核心服务层
│   │       ├── ai_service.py      # LLM 统一网关与流式调度
│   │       ├── memory_service.py  # 本地 Mem0 长期记忆单例引擎
│   │       └── vector_store.py    # 向量检索与余弦相似度引擎
│   ├── data/
│   │   └── mem0/            # 本地持久化嵌入式 Qdrant 向量库与模型权重
│   └── tests/               # 自动化回归测试基线
├── api-contract.md          # 接口契约规范
├── product.md               # 业务需求与产品规范
└── progress.md              # 研发进展与版本里程碑
```

> 🎯 **当前黄金标杆文件指引 (Active Gold Standard References)**
> 系统已于架构清洗中全面废弃了旧版 `admin_members.py` 与 `UsersView.vue`，后续开发与维护请严格参照以下最新文件：
> - **后端标杆**：`backend/app/api/saas/members.py`（多租户沙箱过滤、画像扩展、静默建号与 Mem0 记忆联动）
> - **前端标杆**：`tob/src/views/members/MembersView.vue`（Element Plus 表格外显、画像字段响应式编辑与标准 API 调用）
> - **AI 知识库标杆**：`tob/src/views/kb/KbView.vue`（明亮科技风设计、指标度量合一、独立免污染抽屉式验证通道）

---

## 2. 核心多租户物理隔离底座 (Multi-Tenant Isolation)

### 2.1 数据模型沙箱设计
所有核心业务表强制包含 `tenant_id` 外键与索引，杜绝跨租户越权：
- **`sys_tenant`**：租户主体表（`id`, `name`, `status`）。
- **`sys_user`**：用户全局主账号（`id`, `phone`, `password_hash`, `is_super_admin`）。此表严格独立于具体业务租户。
- **`sys_user_profile`**：用户通用画像（`user_id`, `nickname`, `gender`, `age`, `occupation`, `bio`），用于全平台画像复用与 AI 助手感知。
- **`sys_tenant_user`**：租户与成员绑定关系表（`tenant_id`, `user_id`, `role: 'owner'|'admin'|'member'`, `status`）。
- **业务资产表**（`tasks`, `resources`, `kb_documents`, `kb_chunks`, `task_records`）：全部强制包含 `tenant_id`。
- **答案解析字段**：
- **`resources` 表含 explanation（TEXT，选填），持久化题目答案解析/采分要点。B 端题目管理人工录入、AI 出题/AI 组卷自动产出；C 端 GET /member/task-records/{id} 成绩报告与 B 端阅卷大厅抽屉均回显，作为批阅参考与复盘依据。存量库经 ackend/app/services/db_migrate.ensure_schema() 幂等补列（应用启动时自动执行）。

### 2.2 上下文穿透与安全网关
- **客户端类型守卫 (X-Client)**：B 端后台登录时通过统一请求拦截器注入 X-Client: admin；服务端对携带该标识的纯 member 账号强制返回 403，物理斩断考前泄题路径。
- **Header 守卫**：除登录接口外，所有业务请求必须在 Header 中携带 `X-Tenant-ID: <tenant_id>`。
- **依赖注入校验 (`require_admin` / `require_member`)**：后端拦截器查询 `sys_tenant_user` 校验当前登录用户在目标租户中是否处于 `active` 状态。非法越权一律拦截返回 `403 Forbidden`。
- **超级管理员视察模式**：超级管理员（`is_super_admin=True`）不设全局放行后门，视察具体企业时由前端请求主动携带该企业的 `X-Tenant-ID`，后端复用标准化业务逻辑，确保隔离机制代码简洁闭环。

---

## 3. 本地 Mem0 长期记忆体系 (Embedded Mem0 Architecture)

为了规避生产环境外部网络不稳定及第三方托管向量库的成本，系统实现了纯本地离线运行的长期记忆服务：

### 3.1 核心组件与配置 (`backend/app/services/memory_service.py`)
- **向量数据库引擎**：本地嵌入式 **Qdrant**，数据持久化落盘于 `backend/app/data/mem0/qdrant`。
- **嵌入式向量模型 (Embedder)**：采用 `fastembed` 加载本地轻量级 `BAAI/bge-small-zh-v1.5`（512 维向量），推理零延迟且无需外部 API。
- **大语言模型 (LLM)**：通过系统已配置的 AI 网关（如 `dots3-note-prev`）提炼交互记忆。

### 3.2 运行机制
1. **记忆多租户隔离**：写入与检索使用复合键：
   ```python
   filters = {"user_id": f"tenant:{tenant_id}:user:{user_id}"}
   ```
2. **异步非阻塞提炼 (`remember_async`)**：在 AI 助手流式输出完毕（`done` 事件）后，启动后台守护线程进行对话分析并提炼用户偏好，彻底不阻塞前台 SSE 响应流。
3. **精准语义召回 (`recall`)**：在构建系统 Prompt 时，根据当前提问动态召回最相关的 Top-3 记忆切片。
4. **生命周期级联清理 (`delete_all`)**：当租户移除某成员时，物理销毁其在本地 Qdrant 中的全部向量数据。

---

## 4. AI 助管与双类工具调度链 (AI Assistant & Dual-Toolchain)

AI 助管通过统一网关 `backend/app/api/saas/ai.py` 调度，核心贯彻"只读全景感知 + 写操作安全确认"：

### 4.1 只读聚合工具 / 感知器 (Read-only Aggregation Tools)
此类工具由后端执行器在构建推理上下文时**自动触发并返回结构化数据**，零副作用，不向用户弹确认窗：
- **`_get_tenant_organization_snapshot(db, tid)`**：
  - 自动联查 `sys_tenant_user`, `sys_user`, `sys_user_profile`，实时格式化输出在职员工花名册、角色、职业、性别、年龄与简介。
- **`_get_tenant_tasks_snapshot(db, tid)`**：
  - 自动聚合企业试卷总数、各老师/出题人的出卷统计（`{name}: 出卷 {count} 份`）、最近 5 套试卷创建明细，以及**实时考情分析数据**（包含累计作答人数、全站平均得分、综合及格通过率）。

### 4.2 阅卷大厅与可视化抽屉批改架构 (Verification Hall & Grading Drawer)
- **待核验队列 API (`/api/v1/admin/verifications/pending`)**：
  - 高效联查 `Task`, `SysUser`, `SysUserProfile`，返回包含试卷全名、考生真实姓名、手机号及历史作答明细的组合 Payload。
- **可视化阅卷抽屉 (`VerificationView.vue`)**：
  - 提供 700px 高颜值抽屉，**默认精简过滤仅展示待批改的简答题（Short Answer）**，降低主考官认知负担。
  - **AI 智能 Prompt 优化**：AI 阅卷提示词格式化题目与作答为"第X题"，禁止输出 `resource_id` 抽象编号。提供一键采纳 AI 建议分数与评语按钮。

### 4.3 写操作工具 (Write Tools)
此类工具用于变更数据库资产，必须经过前端可视化卡片二次确认：
- **`create_exam_draft`**：智能组卷草稿。模型输出包含全量题目列表（题型/题干/选项/答案/分值）的结构化 JSON。
- **create_question_draft**：批量或单题出题草稿。模型输出含题型/题干/选项/标准答案/**答案解析 (explanation)**/分值的结构化 JSON，与 create_exam_draft 同构。
- **`delete_exam`** 与 **`delete_question`**：安全软删除工具。
- **执行闭环**：前端卡片确认后，请求 `POST /api/v1/saas/ai/chat/execute_tool`，系统完成事务落库并更新消息状态为 `executed`。

---

## 5. AI 知识库 (KB) 独立召回与切片架构

旧版实验性 RAG 全面升级为生产级独立模块 `backend/app/api/saas/kb.py`：

1. **多格式文本清洗抽取器**：
   - 原生支持 `.docx`, `.pdf`, `.xlsx`, `.txt` 文件的结构化提取，消除乱码与无意义标记，提升切片质量。
2. **切片可观测性**：
   - 记录切片分块序号（Chunk Index），列表实时展示切片进度与就绪状态。
3. **独立免污染验证通道 (`/api/v1/admin/kb/query`)**：
   - 提供专属的 RAG 调试接口，输入测试问题后，后台调用本地向量引擎计算余弦相似度（Cosine Similarity），返回命中文档、切片片段与真实相似度分值（0~100%）。
   - **完全不写入 `ai_sessions` 与 `ai_messages` 会话表**，避免对 AI 助管日常聊天上下文造成任何数据污染。

---

## 6. C 端考试闭环与防作弊机制
- **状态流转**：试卷由管理员在 B 端「试卷管理」发布后，状态变为 `published`（已上架），C 端成员通过 `GET /api/v1/member/member-tasks` 自动拉取可见。
- **开考防作弊与防崩溃锁定**：
  - 成员点击进入考试，服务端在 `TaskRecord` 插入或锁定 `pending` 记录，以服务端时间为基准锚定 `started_at`。
  - **异常恢复容错**：若成员在未交卷（`pending`）状态下因浏览器崩溃或误触退出而重新进入考场，服务端会自动重置 `started_at` 为最新进入时间，防止用时被错误累加。
  - 禁止客户端篡改作答计时；提交时在服务端计算真实作答耗时，超出时限自动截断。
- **客观题秒级判分与高并发保护**：
  - 提交接口使用悲观锁（`with_for_update`），保证一次作答绝不重复覆写。
  - 提交瞬间，触发服务端**客观题自动评分引擎**：单选、多选、判断精确比对 `correct_answer`（支持 TRUE/FALSE 到 A/B 映射），填空题执行无视大小写与空格的宽松匹配，即刻核算总分并落地。
- **交卷状态决策规则（含主观题即进核验池）**：
  - `answer_map`（本卷 `{resource_id: {correct_answer, type, score}}`）在状态决策**之前**构建，据此率先判定本卷是否含简答/主观题；
  - `need_verify = (verification_mode == "ai_auto") or has_subjective`：**只要卷内含简答题，无论 manual 还是 ai_auto，交卷后一律转 `pending_verification` 进入人工/AI 核验池**，C 端卡片显示「审核中」；
  - 仅 `manual` 且全客观题的卷子直接定稿 `submitted`（已交卷，客观题分数即为最终分）。
  - 历史坑位：早期 `need_verify` 只看 `verification_mode`，导致人工审核卷的简答题交卷即被错误定稿为「已交卷」，永远进不了核验队列。
- **首页可见性收敛与「继续测试」**：
  - 首页只呈现 `status = pending`（未作答/进行中）的已上架试卷；`submitted` / `pending_verification` / `verified` 一律隐藏，成绩统一去「我的测试」查看；分类胶囊基于过滤后的可见试卷重算，避免出现点分类后空白。
  - `GET /api/v1/member/member-tasks` 由后端统一下发 `can_continue`，**四条件缺一不可**：`verification_mode === 'manual'` 且 记录状态为 `pending_verification`（未出成绩）且 卷内含简答题（`short` / `short_answer`）且 未过 `deadline`（为空视为长期开放）。纯客观卷、已定稿 `submitted`、已核验 `verified`、AI 全托管 `ai_auto` 卷一律 `false`。前端只做渲染，不自行推断时间或模式。
  - 卡片渲染互斥二分：`can_continue` 为真时**只显示「继续测试」**（不显示分数、不显示查看成绩，因为成绩未终审）；为假时显示分数 + 「查看」。
  - 继续测试走 `POST /api/v1/member/tasks/{task_id}/continue`：**原地把记录退回 `pending` 并保留 `answers`**（供考场按入口返回的 `my_answers` 回填续答），清空未终审的成绩与提交痕迹，`created_at` 重置为重开计时锚点（重新给满时限）；不新增记录行 —— 全库按「每用户每卷唯一」建模（`{task_id: record}` 映射与 `.first()` 查询），新增行会导致列表与统计错乱。
  - 历史坑位：`can_continue` 最初只判「状态 ∈ (submitted, pending_verification) 且未过截止」，导致已出成绩的纯客观卷也出现「继续测试」，与分数、查看成绩三者并存自相矛盾；现由四条件收窄根治。
- **个人中心统计口径**：`GET /api/v1/member/me/stats` 返回累计作答场次 / 历史答卷数 / 通过数 / 综合通过率 / 收藏数。场次与历史答卷 = 已交卷 + 审核中 + 已核验记录数；通过率分母为**已出分记录**，及格线 = `sum(TaskResource.score) × (task.pass_percent or 60)%`，与列表 `pass_score`、报告页 `passed` 判定同源。

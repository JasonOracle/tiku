# 智题库 (TiKu) v1.4 技术说明书 (Technical Specification)

## 1. 架构总览与项目结构

本项目基于前后端分离的现代化架构，针对 v1.4 SaaS 化重构，技术栈与代码组织如下：

```
tiku/
├── toc/                     # 成员端 (原C端，Web H5) - Vue3 + Vite
├── tob/                     # 管理端 (原B端，SaaS后台) - Vue3 + Element Plus
├── backend/                 # 核心 API 服务 - FastAPI (Python 3.12)
│   ├── app/
│   │   ├── api/             # 路由分组
│   │   ├── core/            # 鉴权(JWT)与中间件
│   │   ├── models/          # 数据库实体 (强制包含 tenant_id)
│   │   └── services/        # 业务逻辑与 AI 调度
│   └── tests/               # 自动化集成测试 (Pytest)
├── api-contract.md          # 接口定义契约
└── product.md               # 产品需求规格说明书
```

---

## 2. 核心架构机制：多租户物理隔离 (Multi-Tenant Isolation)

在 v1.4 中，系统从单体向通用 SaaS 演进，**多租户隔离是系统的最高技术红线**。

### 2.1 数据库 Schema 改造 (核心表设计)
所有业务表强制挂载 `tenant_id`，实现数据沙箱隔离。

- **`sys_tenant`** (租户/组织表)
  - `id` (PK), `name`, `status`, `created_at`
- **`sys_user`** (用户登录凭证表)
  - `id` (PK), `phone` (唯一), `password`, `is_super_admin` (布尔标识，决定是否允许访问上帝视图)。
  - **红线**：此表严禁存放任何与租户相关的业务字段。
- **`sys_tenant_user`** (组织与成员关联表)
  - `tenant_id` (FK), `user_id` (FK), `role` (枚举：`owner`, `admin`, `member`)。
- **业务资产表** (包括 `tasks`, `items`, `kb_documents` 等)
  - 全部增加 `tenant_id` (FK)。

### 2.2 租户上下文透传与路由守卫
- **鉴权流**：用户登录后，JWT Payload 中除了携带 `user_id`，还必须返回用户默认或选定的 `tenant_id`。
- **API 通信**：前端发出任何业务请求，必须在 HTTP Header 中携带 `X-Tenant-ID`。
- **中间件拦截**：FastAPI 后端提供依赖注入 `get_current_tenant`。在执行任何业务逻辑前，系统先拦截查询：`SELECT 1 FROM sys_tenant_user WHERE user_id=? AND tenant_id=? AND status='active'`。若不通过，直接抛出 `403 Forbidden`。

### 2.3 超级管理员 (上帝视角) 的隐患防御
- **问题**：`is_super_admin` 不属于任何特定租户。如果代码中直接写 `if user.is_super_admin: return query.all()`，将破坏所有业务代码的隔离优雅性。
- **解决方案**：
  1. 上帝默认只能访问专用的超管路由前缀 `/api/v1/super-admin/*`（如管理全网租户）。
  2. 若上帝需要视察某个具体的组织，需在前端点击“模拟进入”，此时前端 Header 会携带该组织的 `X-Tenant-ID`。后端业务代码**无需任何特殊处理**，依旧按照普通的 `tenant_id` 过滤逻辑运行，实现完美隔离。

---

## 3. RAG 知识库与切片级溯源 (AI Traceability)

### 3.1 TiDB Vector 原生检索
废弃沉重的第三方向量数据库（如 Milvus），拥抱 **TiDB Cloud Serverless** 的原生 Vector 数据类型。

- **`kb_documents`** (文档元数据表)
  - `id`, `tenant_id`, `scope` (`public` / `private`), `creator_id`
- **`kb_chunks`** (文档切片向量表)
  - `id`, `document_id`, `content` (切片文本), `embedding` (VECTOR 维度视大模型而定)。

### 3.2 溯源信息持久化结构
当 AI 基于知识库生成结果时，无论生成的是“条目(Item)”还是“总结建议”，相关业务表必须增加 `ai_rag_sources` JSON 字段进行溯源保存。

格式规范：
```json
[
  {
    "document_id": 1024,
    "file_name": "2026年企业合规手册.pdf",
    "chunk_content": "员工在报销时必须提供对应的发票复印件...",
    "similarity_score": 0.89
  }
]
```
前端 UI 读取该字段后，需在生成结果旁渲染 `[引用溯源]` 交互徽章。

---

## 4. 业务流转底座设计

### 4.1 静默建号与自动绑定流
当管理员在 B 端通过手机号录入新成员时，调用接口 `POST /api/v1/admin/members`：
1. **DB 事务开始**。
2. 检索 `sys_user` 是否有该手机号。
3. 若无，新建记录并赋予 Hash 后的默认密码。
4. 获取该用户的 `user_id`。
5. 在 `sys_tenant_user` 中建立 `tenant_id` (从上下文获取) 与 `user_id` 的关联，`role` 设为 `member`。
6. **DB 事务提交**。

### 4.2 高并发写保护 (悲观锁)
在关键业务（如成员提交任务）时，必须保留原有架构的 `FOR UPDATE` 行级锁，防止网络重传导致的数据覆写：
```python
record = db.query(TaskRecord).filter(...).with_for_update().first()
if record.status != "in_progress":
    raise HTTPException(400, "不可重复提交")
```

### 4.3 异步 AI 核验 (BackgroundTasks)
对于需要主观判断的业务（原简答题批改），不阻塞 HTTP 请求主线程：
1. 更新数据库状态为 `pending_verification`。
2. 返回客户端 `200 OK`。
3. 利用 `fastapi.BackgroundTasks` 异步调度大模型，带上任务数据的 JSON Prompt 请求 AI。
4. AI 响应后，更新记录状态及意见；若超时或异常，则记录错误并保留在待人工核验池中。

# 智题库 (TiKu) v1.4 接口契约测试文档 (API Contract Specification)

> **版本规范**：本文档基于 v1.4 多租户通用 SaaS 架构编写。彻底废弃原有的“考试、题目、老师”等专属词汇。所有接口和数据结构均采用“任务(Task)、资源(Resource)、成员(Member)”等通用化定义。

---

## 1. 契约规范与通用约定

### 1.1 前缀与鉴权 (多租户隔离)
- **C端成员接口前缀**：`/api/v1/member`
- **B端管理接口前缀**：`/api/v1/admin`
- **上帝视图接口前缀**：`/api/v1/super-admin`
- **鉴权 Header**：`Authorization: Bearer <jwt_token>`
- **租户上下文 Header (核心)**：`X-Tenant-ID: <tenant_id>`
  - 除登录接口及超级管理员的特定接口外，**所有业务接口必须携带该 Header**。后端中间件会拦截校验当前 Token 所属用户是否拥有该 `tenant_id` 的合法权限。

### 1.2 抢提交机制 (Race-Condition Policy)
- **抢先提交原则 (First-Submit-Wins)**：
  - 任务提交 API 执行数据库原子更新与悲观锁（`FOR UPDATE`）。若任务记录状态已变为 `submitted`，后续重试或网络延迟带来的重复请求统一返回 `400 Bad Request`，确保数据绝不覆写。

### 1.3 统一响应格式与分页
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 45,
    "page": 1,
    "size": 10,
    "total_pages": 5,
    "items": []
  }
}
```

---

## 2. 核心鉴权与入驻流 (Auth & Onboarding)

### 2.1 用户登录 (全端统一)
#### POST `/api/v1/auth/login`
- **说明**：废除自由注册。系统仅允许手机号登录（首次建号由企业管理员完成，默认为手机号+默认密码）。
- **Request Body**:
  ```json
  { "phone": "13800138000", "password": "password123" }
  ```
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": { 
      "token": "eyJhbGciOi...", 
      "user": { "id": 1, "phone": "13800138000" },
      "default_tenant_id": 101,
      "joined_tenants": [
        { "tenant_id": 101, "tenant_name": "A科技有限公司", "role": "member" }
      ]
    }
  }
  ```

### 2.2 管理员录入成员 (静默建号)
#### POST `/api/v1/admin/members`
- **说明**：管理员在后台为组织添加成员。若手机号未在平台注册，系统执行 UPSERT 静默建号，并强制将其绑定至当前上下文的 `tenant_id` 中。
- **Request Body**:
  ```json
  { "phone": "13912345678", "name": "张三", "role": "member" }
  ```
- **Response 201**: `{ "code": 201, "message": "成员添加成功" }`

---

## 3. 业务资产模块 (Assets: Tasks & Resources)

> **注意**：所有以下接口的请求必须在 Header 中携带 `X-Tenant-ID`。

### 3.1 资源库管理 (原题库)
#### GET `/api/v1/admin/resources` — 资源库分页列表
- **Query Params**: `page`, `size`, `type`, `keyword`
#### POST `/api/v1/admin/resources` — 创建资源条目
- **Request Body**:
  ```json
  {
    "type": "single_choice",
    "content": "关于公司2026年报销标准，以下哪项是正确的？",
    "options": [
      { "key": "A", "text": "高铁二等座全额报销" },
      { "key": "B", "text": "无需发票即可报销" }
    ],
    "correct_answer": ["A"],
    "score": 10,
    "ai_rag_sources": [] 
  }
  ```

### 3.2 任务管理 (原试卷)
#### POST `/api/v1/admin/tasks` — 下发新任务 (组卷)
- **Request Body**:
  ```json
  {
    "title": "2026 Q3 财务合规性测评任务",
    "description": "请所有销售部成员在周五前完成。",
    "cover_image": "/uploads/task_cover.jpg",
    "is_timed": true,
    "time_limit": 15,
    "verification_mode": "ai_auto",
    "resource_ids": [101, 102, 103]
  }
  ```
#### GET `/api/v1/member/tasks` — 成员获取个人的待办/已办任务
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": {
      "items": [
        {
          "task_id": 8801,
          "title": "2026 Q3 财务合规性测评任务",
          "status": "pending",
          "deadline": "2026-09-15T23:59:59Z"
        }
      ]
    }
  }
  ```

---

## 4. 任务执行与核验闭环 (Execution & Verification)

### 4.1 执行任务与防并发提交
#### POST `/api/v1/member/task-records/submit`
- **说明**：成员提交任务结果。采用 `FOR UPDATE` 悲观锁。
- **Request Body**:
  ```json
  {
    "task_id": 8801,
    "time_spent": 252,
    "answers": [
      { "resource_id": 1001, "answer": "A" },
      { "resource_id": 1002, "answer": "这是我的简答/主观回复" }
    ]
  }
  ```
- **Response 200 (需 AI 核验或人工核验时)**:
  ```json
  { "code": 200, "message": "提交成功，等待管理员或AI核验", "data": { "status": "pending_verification" } }
  ```

### 4.2 任务核验大厅 (原阅卷大厅)
#### GET `/api/v1/admin/verifications/pending`
- **获取当前组织下所有待核验的任务提交记录**。

#### POST `/api/v1/admin/verifications/{record_id}/confirm`
- **说明**：管理员对成员的提交结果进行最终确认打分。
- **Request Body**:
  ```json
  {
    "accept_ai_suggestion": true,
    "final_score": 85,
    "comments": "合规意识不错"
  }
  ```

---

## 5. RAG 知识库与 AI 协同 (Public/Private KB)

### 5.1 上传知识库文档
#### POST `/api/v1/admin/kb/documents`
- **说明**：上传文件并进行切片 (Chunking) 和向量化 (Embedding)。
- **Request Body** (FormData): `file`, `scope` (`public` / `private`)
- **权限边界**：普通成员调用此接口，`scope` 强制被后台锁定为 `private`。管理员可选 `public`（企业全员只读共享）。

### 5.2 AI 执行动作 (自带溯源)
#### POST `/api/v1/admin/ai/chat` (Copilot 交互)
- **Response (SSE Stream 或 JSON)**：
  当 AI 返回建议或生成的资源时，强契约要求附带溯源切片：
  ```json
  {
    "content": "根据公司制度，报销确实需要发票复印件。",
    "ai_rag_sources": [
      {
        "document_name": "财务报销红头文件.pdf",
        "chunk_content": "第六条：任何无发票的报销申请将被直接驳回...",
        "similarity": 0.92
      }
    ]
  }
  ```

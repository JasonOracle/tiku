# 智题库 (TiKu) v1.4+ 接口契约规范 (API Contract Specification)

> **版本规范**：本文档基于当前生产环境的纯 SaaS 架构与直观业务语义编写。统一规范多租户隔离 Header、AI 工具链与知识库独立调试端点。

---

## 1. 契约规范与通用约定

### 1.1 前缀与鉴权规范
- **B端管理接口**：`/api/v1/saas/*`（兼容别名 `/api/v1/admin/*`）
- **C端成员接口**：`/api/v1/member/*`
- **超管上帝接口**：`/api/v1/super-admin/*`
- **必须携带 Header**：
  - `Authorization: Bearer <jwt_token>`
  - `X-Tenant-ID: <tenant_id>`（登录接口除外，所有业务接口强制校验）

### 1.2 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 45,
    "page": 1,
    "size": 10,
    "items": []
  }
}
```

---

## 2. 成员画像与组织架构 (Members)

### 2.1 添加企业成员（静默建号）
- **POST** `/api/v1/saas/members` (兼容 `/api/v1/admin/members`)
- **Request Body**:
  ```json
  {
    "phone": "13912345678",
    "name": "张三",
    "role": "member",
    "gender": "male",
    "age": 28,
    "occupation": "语文骨干教师",
    "bio": "从事中考语文一线教学8年"
  }
  ```
- **Response 200**: `{ "code": 200, "message": "成员添加成功" }`

### 2.2 更新成员画像与信息
- **PUT** `/api/v1/saas/members/{user_id}`
- **Request Body**:
  ```json
  {
    "name": "张老师",
    "role": "member",
    "gender": "male",
    "age": 29,
    "occupation": "高级语文教师",
    "bio": "重点班教研组长"
  }
  ```
- **Response 200**: `{ "code": 200, "message": "成员更新成功" }`

---

## 3. AI 知识库 (Knowledge Base)

### 3.1 获取知识库度量统计（指标大盘卡片）
- **GET** `/api/v1/admin/kb/metrics`
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": {
      "total_documents": 12,
      "total_chunks": 348,
      "storage_mb": 14.5,
      "ready_percentage": 100.0
    }
  }
  ```

### 3.2 独立 RAG 检索召回验证（不落会话数据库）
- **POST** `/api/v1/admin/kb/query`
- **Request Body**:
  ```json
  {
    "query": "请问本次考试的安全防作弊规范是什么？",
    "top_k": 3
  }
  ```
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": {
      "query": "请问本次考试的安全防作弊规范是什么？",
      "answer": "根据知识库规定，考试期间禁止切屏超过3次...",
      "sources": [
        {
          "document_id": 101,
          "filename": "2026考务规范.docx",
          "chunk_index": 2,
          "content": "切屏超过3次将自动强制交卷...",
          "similarity_score": 0.885
        }
      ]
    }
  }
  ```

---

## 4. AI 助管与工具交互链路 (AI Assistant)

### 4.1 AI 流式对话与感知 Prompt
- **POST** `/api/v1/saas/ai/chat/stream`
- **说明**：开启 SSE 长连接，后端自动调用 `_get_tenant_organization_snapshot` 与 `_get_tenant_tasks_snapshot`，结合 Mem0 长期偏好记忆拼装权威 Prompt，并支持下发 `delta`、`tool_calls` 和 `done` 事件。

### 4.2 执行写操作工具 (Tool Execution)
- **POST** `/api/v1/saas/ai/chat/execute_tool`
- **Request Body**:
  ```json
  {
    "tool_name": "create_exam_draft",
    "arguments": {
      "title": "2026 高一语文第一次月考试卷",
      "time_limit": 60,
      "grading_mode": "ai_auto",
      "questions": [
        {
          "type": "single_choice",
          "content": "下列字词注音完全正确的一项是？",
          "options": [{"key": "A", "text": "细腻(nì)"}],
          "answer": "A",
          "score": 5
        }
      ]
    },
    "tool_call_id": "call_12345",
    "message_id": 88
  }
  ```
- **Response 200**:
  ```json
  {
    "status": "ok",
    "result": { "exam_id": 56, "title": "2026 高一语文第一次月考试卷" },
    "tool_call_id": "call_12345"
  }
  ```

---

## 5. 试卷与题目核心资产 (Tasks & Resources)

### 5.1 试卷状态变更与上架
- **PUT** `/api/v1/saas/tasks/{task_id}/status`
- **Request Body**:
  ```json
  { "status": "published" } // 可选：draft, published, archived
  ```
- **说明**：变更试卷为 `published`（已上架）后，C 端成员在答题中心立即外显可见。

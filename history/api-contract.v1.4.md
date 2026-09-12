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
## 6. C 端任务提交流转 (Task Submission)

### 6.1 提交答卷与客观题自动评分
- **POST** `/api/v1/member/task-records/submit`
- **说明**：提交成员作答数据。服务端执行防重交悲观锁，并立即启动客观题秒级判分。
- **Request Body**:
  ```json
  {
    "task_id": 30,
    "time_spent": 1450,
    "answers": [
      { "resource_id": 168, "answer": ["A"] },
      { "resource_id": 171, "answer": ["洛神赋图"] }
    ]
  }
  ```
- **Response 200**:
  ```json
  {
    "code": 200,
    "message": "提交成功",
    "data": {
      "record_id": 122,
      "status": "submitted",
      "score": 80,
      "time_spent": 1450,
      "server_now": "2026-09-11T16:50:00.000000"
    }
  }
  ```
- **核心契约**：接口会直接在 `data` 中返回 `record_id` 与核算后的 `score`，前端可利用此 `record_id` 实现无缝零延迟跳转成绩报告页。
- **状态流转契约（含主观题即进核验池）**：`verification_mode = ai_auto`（AI 全托管）**或试卷含简答/主观题**时，交卷后 `status = pending_verification`（进入人工/AI 核验池，C 端卡片显示「审核中」）；仅当 `manual` 且全为客观题时才直接 `submitted`（已交卷，客观题分数已定稿）。简答题不计入自动判分。

---

## 7. 答案解析全链路 (Explaination Field Contract)

> **字段规范**：`resources.explanation`（TEXT，选填）持久化题目答案解析/采分要点。由 B 端题目管理人工录入、AI 出题/AI 组卷自动产出；C 端成绩报告与 B 端阅卷大厅均回显。存量库经 `backend/app/services/db_migrate.ensure_schema()` 幂等补列（应用启动时自动执行）。

### 7.1 资源条目新增/更新（含解析）
- **POST** `/api/v1/admin/resources` / **PUT** `/api/v1/admin/resources/{rid}` / **POST** `/api/v1/admin/resources/batch`
- **Request Body** 支持可选字段 `explanation`（string，选填；留空后端落库为 `null`）。
- **Response** `_res_out` 行结构新增 `explanation`（string，无解析时为空串 `""`）。

### 7.2 AI 出题 / AI 组卷（自动产出解析）
- **POST** `/api/v1/admin/ai/questions/generate`、**POST** `/api/v1/admin/ai/exams/generate`
- **说明**：模型 Prompt 现强制要求每题输出 `explanation`（50-150 字解析/采分要点），响应 `data.questions[]` 透传 `explanation`；组卷落库时写入 `ResourceItem.explanation`。

### 7.3 聊天工具链出题（含解析）
- **POST** `/api/v1/admin/ai/chat/execute_tool`（`create_exam_draft` / `create_question_draft`）
- 工具 schema `questions[].explanation` 为必输出属性；执行落库写入解析字段。

### 7.4 C 端成绩报告回显解析
- **GET** `/api/v1/member/task-records/{record_id}`
- 响应 `data.items[]` 每项包含：
  - `type`（题目类型，如 single/multiple/fill/short/judge 等）；
  - `options`（选项列表，对象数组或字符串数组，供客观题选项高亮比对）；
  - `correct_answer`（标准答案）与 `explanation`（解析）。
- C 端报告页逐题对照展示，核验中/已提交/已核验三态均可见。

### 7.5 阅卷大厅明细回显解析
- **GET** `/api/v1/admin/verifications/{record_id}`
- 响应 `data.items[]` 每项新增 `explanation`，供批阅人定分参考。
- **核心契约**：接口会直接在 `data` 中返回 `record_id` 与核算后的 `score`，前端可利用此 `record_id` 实现无缝零延迟跳转成绩报告页。

---

## 8. C 端试卷可见性、重考与个人统计契约

### 8.1 成员试卷列表（新增 can_continue / verification_mode）

- **GET** `/api/v1/member/member-tasks`
- **说明**：返回本企业全部 `published` 试卷（含本人作答状态），由前端决定可见性。首页仅展示 `status = pending`（未作答/进行中）的试卷；`submitted` / `pending_verification` / `verified` 一律从首页隐藏，统一在「我的测试」查看。
- **Response `data.items[]` 新增字段**：
  | 字段 | 类型 | 说明 |
  | :--- | :--- | :--- |
  | `can_continue` | boolean | 「继续测试」资格，**四条件缺一不可**：`verification_mode === 'manual'` 且 记录状态为 `pending_verification`（未出成绩）且 **卷内含简答题**（`short` / `short_answer`）且 未过 `deadline`（`deadline` 为空视为长期开放）。纯客观卷、`submitted` 已定稿、`verified` 已核验、`ai_auto` 卷一律 `false` |
  | `verification_mode` | string | `manual` / `ai_auto` |

### 8.2 继续测试（保留作答续答）

- **POST** `/api/v1/member/tasks/{task_id}/continue`
- **说明**：把本人该卷的 `TaskRecord` 从 `pending_verification` **原地退回** `pending`，**保留 `answers`（上次作答）**供学员回考场续答修改；同时清空未终审的 `score` / `ai_result` / `ai_rag_sources` / `comments` / `submit_time` / `time_spent`，并将 `created_at` 重置为服务端当前时间（**重新给满考试时限**）。**不新增记录行**（全库按「每用户每卷唯一」建模）。
- **Response 200**：
  ```json
  { "code": 200, "message": "已恢复上次作答，继续本次测试",
    "data": { "record_id": 122, "status": "pending" } }
  ```
- **400 守卫**：任务未发布（404）；考试已截止；AI 核验模式不支持；试卷不含简答题；暂无作答记录；记录非 `pending_verification`（已核验 / 已定稿 / 无需继续）。
- **审计**：写 `continue` 动作留痕。
- **配套读取**：`GET /api/v1/member/tasks/{task_id}/entry` 响应新增 `my_answers`（上次作答原文数组，结构与提交时的 `answers` 一致），供考场回填续答；首次作答时为 `[]`。

### 8.3 个人中心统计（常规口径）

- **GET** `/api/v1/member/me/stats`
- **Response 200**：
  ```json
  { "code": 200, "data": {
      "total_exams_taken": 3,   // 累计作答场次 = 已交卷 + 审核中 + 已核验
      "history_count": 3,       // 历史答题记录 = 提交记录数
      "passed_count": 2,        // 已出分记录中达到动态及格线的数量
      "pass_rate": 66.7,        // 百分比，保留 1 位小数，无已出分记录为 0
      "favorite_count": 5 } }   // 本人收藏题数
  ```
- **口径契约**：动态及格线 = `sum(TaskResource.score) × (task.pass_percent or 60)%`，与 `member_tasks` 列表的 `pass_score`、C 端报告页 `passed` 判定完全同源。全程强制 `tenant_id` + `user_id` 双过滤。
- **历史坑位**：前端早期误调 `/api/v1/users/me/stats`（后端不存在该路由），404 被静默吞掉导致四项统计恒为 0，现已收敛到本接口。

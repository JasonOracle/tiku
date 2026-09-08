# 智题库 (TiKu) 接口契约测试文档 (API Contract Specification)

## 1. 契约规范与通用约定

### 1.1 前缀与鉴权
- **C端接口前缀**：`/api/v1`
- **B端管理接口前缀**：`/api/v1/admin`
- **鉴权 Header**：`Authorization: Bearer <jwt_token>`
  - C端 Token 本地存储 Key：`tiku_toc_token`
  - B端 Token 本地存储 Key：`tiku_tob_token`
- **Token 有效期与安全机制**：
  - JWT Token 有效期统一设为 **7 天 (7 * 24h)**。
  - 交卷接口支持 5 分钟过期宽限期验证，确保考试中途不会因为 Token 超时导致作答数据丢失。

### 1.2 多账号并发与抢提交机制 (Race-Condition Policy)
- **多端同时登录**：采用无状态 JWT，允许同一账号多设备/浏览器并发作答，不互相强制下线。
- **抢先提交原则 (First-Submit-Wins)**：
  - 每次开始考试生成唯一 `record_id`。
  - 提交答卷 API 执行数据库原子更新与悲观锁：若记录状态已变为 `submitted` 或 `timeout`，后续提交统一返回 `400 Bad Request`，拒收后续重复提交，确保成绩以最早提交者为准。

### 1.3 统一响应格式与标准分页结构
- **普通响应结构**：
  ```json
  { "code": 200, "message": "success", "data": {} }
  ```
- **标准分页响应结构 (Pagination)**：
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "total": 45,
      "page": 1,
      "size": 10,
      "total_pages": 5,
      "has_next": true,
      "items": []
    }
  }
  ```

---

## 2. C 端 API 契约 Specification

### 2.1 认证模块 (Auth)
#### POST `/api/v1/auth/register` — 用户注册
- **Request Body**:
  ```json
  { "username": "student01", "password": "password123" }
  ```
- **Response 201**:
  ```json
  { "code": 201, "message": "注册成功", "data": { "id": 1, "username": "student01" } }
  ```

#### POST `/api/v1/auth/login` — 用户登录
- **Request Body**:
  ```json
  { "username": "student01", "password": "password123" }
  ```
- **Response 200**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": { "token": "eyJhbGciOi...", "user": { "id": 1, "username": "student01" } }
  }
  ```

---

### 2.2 分类与试卷模块 (Categories & Exams)
#### GET `/api/v1/categories` — 试卷分类列表
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": [
      { "id": 1, "name": "消防安全", "icon": "fire", "sort_order": 1 }
    ]
  }
  ```

#### GET `/api/v1/exams` — 试卷列表 (标准分页)
- **Query Params**: `category_id` (int, optional), `is_recommended` (bool, optional), `page` (int, default=1), `size` (int, default=10)
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": {
      "total": 45,
      "page": 1,
      "size": 10,
      "total_pages": 5,
      "has_next": true,
      "items": [
        {
          "id": 101,
          "title": "全国消防日科普知识测评 (2026版)",
          "cover_image": "/uploads/exam_cover_1.jpg",
          "category_name": "消防安全",
          "is_timed": true,
          "time_limit": 15,
          "question_count": 20,
          "total_score": 100,
          "is_random": true
        }
      ]
    }
  }
  ```

#### GET `/api/v1/exams/{id}` — 试卷详情
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": {
      "id": 101,
      "title": "全国消防日科普知识测评 (2026版)",
      "description": "包含 20 道权威消防安全题目",
      "cover_image": "/uploads/exam_cover_1.jpg",
      "is_timed": true,
      "time_limit": 15,
      "is_random": true,
      "total_score": 100,
      "questions": [
        {
          "id": 1001,
          "type": "single",
          "title": "根据《中华人民共和国消防法》，我国消防工作的方针是？",
          "options": [
            { "key": "A", "text": "安全第一，预防为主" },
            { "key": "B", "text": "预防为主，防消结合" }
          ],
          "score": 5
        }
      ]
    }
  }
  ```

---

### 2.3 答题流程与提交评分 (Quiz & Submit)

#### POST `/api/v1/records/start` — 开始考试 (含被动超时清理)
- **Request Body**: `{ "exam_id": 101 }`
- **说明**：请求时后端会自动校验该用户该试卷未完成的记录。若存在已被超期的 `in_progress` 记录，将其自动触发结算置为 `timeout` 状态，避免幽灵记录积压。
- **状态隔离**：仅 `status='published'` 可开考，draft/archived 直接 `404`（“试卷不存在或已被下架”）。
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": { "record_id": 8801, "start_time": "2026-09-03T17:15:00Z" }
  }
  ```

#### POST `/api/v1/records/submit` — 提交答卷 (抢先提交机制，实际落地接口)
- **说明**：以 `record_id + user_answers + time_spent` 为 Body；零作答直接 `400`（防误入产生 0 分幽灵记录）；`in_progress` 才能结算，否则 `400`（悲观锁 First-Submit-Wins）。
- **Response 400 (空卷)**：`{ "detail": "您尚未作答任何题目，无需交卷" }`

#### PUT `/api/v1/records/{record_id}/submit` — 提交答卷 (抢先提交机制，历史契约名，实际以后者为准)
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "time_spent": 252,
    "answers": [
      { "question_id": 1001, "answer": "B", "time_spent": 12 },
      { "question_id": 1002, "answer": ["A", "B"], "time_spent": 25 }
    ]
  }
  ```
- **Response 200 (首次成功提交)**:
  ```json
  {
    "code": 200,
    "message": "交卷成功",
    "data": {
      "record_id": 8801,
      "total_score": 85,
      "correct_count": 17,
      "total_count": 20,
      "time_spent": 252
    }
  }
  ```
- **Response 400 (已被并发账号抢先提交处理)**:
  ```json
  {
    "code": 400,
    "message": "该试卷答题记录已被提交结算或已超时，请勿重复提交！"
  }
  ```

#### GET `/api/v1/records/{record_id}/analysis` — 考试分析报告
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": {
      "record_id": 8801,
      "exam_title": "全国消防日科普知识测评 (2026版)",
      "total_score": 85,
      "pass_score": 60,
      "is_passed": true,
      "time_spent": 252,
      "avg_time_per_question": 12.6,
      "details": [
        {
          "question_id": 1001,
          "title": "我国消防工作的方针是？",
          "user_answer": "A",
          "correct_answer": "B",
          "is_correct": false,
          "explanation": "《消防法》第二条规定，消防工作贯彻“预防为主，防消结合”的方针。"
        }
      ]
    }
  }
  ```

---

### 2.4 个人中心与历史记录 (Profile & Records)
#### GET `/api/v1/users/me/stats` — 获取个人作答统计
- **Headers**: `Authorization: Bearer <token>`
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": {
      "total_exams_taken": 12,
      "passed_count": 10,
      "pass_rate": 83.3,
      "favorite_count": 8,
      "history_count": 12
    }
  }
  ```

#### GET `/api/v1/records/history` — 获取个人历史答题记录列表
- **Headers**: `Authorization: Bearer <token>`
- **Response 200**:
  ```json
  {
    "code": 200,
    "data": [
      {
        "record_id": 8801,
        "exam_title": "全国消防日科普知识测评",
        "score": 85,
        "pass_score": 60,
        "is_passed": true,
        "time_spent": 252,
        "created_at": "2026-09-03T17:15:00Z"
      }
    ]
  }
  ```

---

## 3. B 端 API 契约 Specification (Admin)

### 3.1 试卷与题目分类管理 (Categories)
- `GET /api/v1/admin/categories` — 查询分类列表（Query: `target_type`: 'question' | 'exam'；排序 `sort_order,id` 双字段，前端“第一项”与后端默认值以此为准）
- `POST /api/v1/admin/categories` — 创建分类（Body: `name`, `icon`, `sort_order`, `target_type`）
- `DELETE /api/v1/admin/categories/{id}` — 删除分类；被题目/试卷引用时 `400`（“该分类正被N道题目/M张试卷使用，不可删除”）

### 3.2 题海管理 (Question Pool)
- `GET /api/v1/admin/questions` — 题海标准分页列表（Query: `page`, `size`, `type`, `category_id`, `keyword`）
- **注意**：前端新建/导入前必须校验分类列表非空，否则阻断；题目列表中提供批量复选删除（支持多 ID 一并提交）。

### 3.3 试卷管理与考情看板 (Exam Management & Stats)
- `PUT /api/v1/admin/exams/{id}/status` — 试卷上下架状态切换（Body: `{ "status": "published" | "draft" }`）
- `GET /api/v1/admin/exams/{id}/stats` — 已上架试卷考情看板统计与用户作答列表
  - **Response 200**:
    ```json
    {
      "code": 200,
      "data": {
        "exam_id": 101,
        "title": "消防安全测评",
        "total_participants": 42,
        "avg_score": 78.5,
        "pass_rate": 85.7,
        "user_records": [
          { "username": "student01", "score": 90, "is_passed": true, "submit_time": "2026-09-03 20:10:00" }
        ]
      }
    }
    ```

- `POST /api/v1/admin/questions` — 新建题目（`category_id` 为空时服务端默认第一条题目分类）
  - **Request Body**:
    ```json
    {
      "category_id": 1,
      "type": "single",
      "title": "消防安全常识题",
      "options": [{ "key": "A", "text": "选项1" }, { "key": "B", "text": "选项2" }],
      "answer": ["A"],
      "explanation": "解析内容",
      "difficulty": "medium",
      "score": 10
    }
    ```
- `PUT /api/v1/admin/questions/{id}` — 编辑题目（已上架卷引用题目的内容编辑暂不锁定，已知历史口径漂移风险，见 progress §7.5）
- `DELETE /api/v1/admin/questions/{id}` — 删除题目；被 published/archived 卷引用时 `400`（报卷名）；仅被 draft 卷引用时联动移除并重算总分及格线
- `POST /api/v1/admin/questions/import` — Excel 批量导入题目（按表头匹配列：题型, 题干, 选项A-D, 答案, 解析, 难度, 分数, **分类**；分类按名匹配、不存则新建、空则取第一项；`short/fill` 预留题型跳过计数）
  - **Response 200**: `{ "code": 200, "data": { "imported_count": N, "skipped_count": M } }`
  - 模板：`sample_questions.xlsx`（仓库根目录；数据表第一顺位 + “导入说明”工作表）

### 3.3 试卷管理 (Exam Management)
- `GET /api/v1/admin/exams` — 试卷标准分页列表
- `POST /api/v1/admin/exams` — 创建试卷
  - **Request Body**:
    ```json
    {
      "category_id": 1,
      "title": "2026 消防安全与自救知识全能测评",
      "description": "描述说明",
      "cover_image": "/uploads/exam_cover_1.jpg",
      "is_timed": true,
      "time_limit": 15,
      "pass_percent": 60,
      "is_random": true,
      "is_recommended": true,
      "question_ids": [101, 102, 103]
    }
    ```
- `GET /api/v1/admin/exams/{id}` — B端试卷详情（含草稿/归档，不受 published 隔离；响应带 `category_name` 快照）
- `PUT /api/v1/admin/exams/{id}` — 编辑试卷与题目关联（archived 终态冻结一切编辑，400；published 锁题目变更；终态 published 自动刷新分类快照）
- `PUT /api/v1/admin/exams/{id}/status?status=` — 状态机：`draft→published`（需有效分类并写快照，否则400）、`published→archived`（归档冻结）、`archived→*` 一律 400
- `DELETE /api/v1/admin/exams/{id}` — 仅 draft 零作答可删；有 submitted/timeout 作答、published、archived 一律 `400`（draft 删时顺带清理 in_progress 幽灵记录）
- `ExamResponse` 新增 `category_name`（上架快照，分类改名/删除后展示不变）及 `is_random`（bool, 是否开启 C 端随机题目排列）
- `Exam.cover_url` 约定 `preset:1..5`（内置 SVG 封面，兼容旧 `/uploads/` 路径）
- `ExamReportResponse` 新增 `total_score/pass_score`（圆环按真实总分渲染）

### 3.4 首页 Banner（新增模块）
- `GET /api/v1/admin/banners`、`POST /api/v1/admin/banners`、`PUT/DELETE /api/v1/admin/banners/{id}` — 字段 `image_url/link_type(none|external|internal)/link_value/sort_order/is_enabled`；启用超 3 张 400
- `PUT /api/v1/admin/banners/settings` — 全局轮播秒数（2–10，默认 4）
- `GET /api/v1/banners`（C端）— `{ interval_seconds, items[启用有序] }`

---

## 4. v1.2 新增与变更 API 契约 (V1.2 Updates)

### 4.1 B 端 AI 协同与出题组卷模块
#### POST `/api/v1/admin/ai/chat` — AI Copilot 对话
- **Request Body**:
  ```json
  {
    "prompt": "[System: 待批阅10份, 余量15] 帮我总结下任务",
    "history": []
  }
  ```
- **Response 200**: 流式或完整文本返回。**后端注意**：需扣减该 Admin 的 `daily_ai_quota`，不足则返回 `403`。

#### POST `/api/v1/admin/ai/generate-questions` — AI 智能出题
- **Request Body**: `{ "topic": "消防安全", "count": 5, "type": "single" }`
- **Response 200**: 返回生成的题目 JSON 列表，供前端弹窗二次确认。此接口需扣减个人 Token。

### 4.2 阅卷大厅与主观题流转
#### GET `/api/v1/admin/records/pending` — 阅卷大厅列表
- **Response 200**: 获取 `status == 'pending_grading'` 的所有答卷记录。

#### PUT `/api/v1/admin/records/{record_id}/grade` — 人工/AI 最终复核批改
- **Request Body**:
  ```json
  {
    "final_score": 85,
    "teacher_comments": "回答得很棒",
    "question_scores": [{ "question_id": 1005, "score": 15 }]
  }
  ```
- **Response 200**: 将记录状态流转为 `submitted`（或 `passed`/`failed`），成绩正式对外发布。

### 4.3 基础数据结构与管理接口变更
- **Exams 表单扩展**：`POST / PUT /api/v1/admin/exams` 需增加 `start_time`, `end_time` 和 `grading_mode` (枚举：`'manual'`, `'ai_pre'`, `'ai_auto'`) 参数。
  - 时间校验逻辑（`time_limit <= end_time - start_time`）在前端和后端均需强制拦截。
  - 试卷权限隔离：出题人 (`creator`) 仅能查询和编辑 `creator_id == current_user.id` 的私有试卷。
- **Records 交卷逻辑扩展**：
  - 交卷接口如遇主观简答题：
    - 若 `grading_mode == 'ai_auto'`：后台大模型自动判分并计算总分，记录直接转为 `submitted` 并对外公布。
    - 若 `grading_mode == 'ai_pre'` 或 `'manual'`：返回 `status: "pending_grading"`，进入阅卷大厅待复核发布。
- **POST `/api/v1/admin/users/transfer-quota` — 管理员向下级划拨 AI 额度**：
  - **Request Body**: `{ "target_email": "creator.chen@tiku.io", "amount": 50 }`
  - **权限校验**：
    - 超管可向任何人划拨额度。
    - 管理员仅能向自己创建的/归属的下级出题人 (`creator`) 划拨额度；**向同级管理员或超管划拨直接返回 `403 Forbidden`**。
    - 出题人无权调用此接口。
- **POST `/api/v1/admin/users` — 创建管理成员**：
  - **Request Body**: `{ "username": "creator.chen@tiku.io", "nickname": "陈思源", "role": "creator", "password": "..." }`
  - **溯源绑定**：系统自动记录 `created_by_id = current_admin.id`，实现全链溯源。


---

## 5. v1.2 接口契约实现定案 (2026-09-06 落地，以此为准)

> 本节为 v1.2 最终实现口径。若与上文 §4 草案路径不一致，**一律以本节为准**（progress.md 同步记录）。所有响应均走统一 `ResponseModel{code, message, data}` 包装；写操作全部落 `audit_logs` 双域留痕。

### 5.1 阅卷大厅 (Grading Hall)
- **GET** `/api/v1/admin/grading/records?exam_id=&page=&size=` — 待批阅列表（进入时惰性收卷已过 end_time 的僵尸卷）。条目含 `objective_score / short_count / has_ai_suggestion / ai_error / is_ai_auto`。
- **GET** `/api/v1/admin/grading/records/{record_id}` — 批阅详情：全卷题目 + 简答题的 `reference_answer / grading_points / ai_suggested_score / ai_comment / final_score`。
- **POST** `/api/v1/admin/grading/records/{record_id}/confirm` — 定分发布。Body `{ "accept_ai": true }`（一键采信）或 `{ "accept_ai": false, "scores": {"<question_id>": score} }`（人工定分，需覆盖全部简答题）。终算后 `status → submitted`，`short_scores` 落库。
- **POST** `/api/v1/admin/grading/records/{record_id}/retry-ai` — AI 失败兜底重试（重置 ai_grading_result 并重新调度 BackgroundTasks）。
- **RBAC**：老师仅能批改自己创建（creator_id）的试卷，超管全览，越权 403。

### 5.2 AI 员工 (AI Employee)
- **GET** `/api/v1/admin/ai/status` — `{available, model, quota_remaining, quota_limit}`。
- **POST** `/api/v1/admin/ai/questions/generate` — Body `{material, count(1-20), q_type, difficulty, category_id?}`。返回**不入库**的预览题目列表（`source: "ai"`）；扣 1 次个人额度。
- **POST** `/api/v1/admin/questions/batch` — AI 出题二次确认入库（≤50 题，逐题校验）。
- **POST** `/api/v1/admin/ai/exams/generate` — Body `{title?, description, specs:[{q_type,count}], category_id?, time_limit, pass_percent, start_time?, end_time?}`。优先检索共享题库，不足自动生成新题（source=ai）；**试卷强制 draft** + 站内信通知；扣额度。
- **POST** `/api/v1/admin/ai/chat` — Copilot 透传；前端负责把状态快照拼进 message 前导；扣额度。

### 5.3 成员与额度 (Super Admin only)
- **GET/POST** `/api/v1/admin/members`，**PUT** `/api/v1/admin/members/{id}`（password/ai_quota_limit/status），**POST** `/api/v1/admin/members/{id}/refill` `{amount}`。
- 额度规则：`daily_ai_quota`(今日余额) 跨天首次使用惰性回满为 `ai_quota_limit`；调整配置即重置今日余额；被动 AI 阅卷记系统账单不扣个人额度。

### 5.4 消息中心 / 审计
- **GET** `/api/v1/admin/notifications?unread_only=`、**GET** `.../unread-count`（侧边栏 30s 轮询红点）、**POST** `.../read` `{ids: [..]|null}`（null=全部已读）。通知类型：`grading / exam_draft / ai_error / system`。
- **GET** `/api/v1/admin/audit?action_type=&target_type=&operator_type=&keyword=` — 审计日志（仅超管）。
- **GET** `/api/v1/admin/auth/me` — 当前管理员信息（RBAC 菜单与额度展示依赖）。

### 5.5 C 端答题流 v1.2 变更
- **POST** `/api/v1/records/start` — 新增时间窗拦截（未开始/已结束 400）；同卷 `in_progress` 记录自动**续答**；响应新增 `end_time / server_now`（前端倒计时 = min(限时-已耗时, 距 end_time)，用 server_now 校正时钟偏差）。
- **POST** `/api/v1/records/submit` — 含简答题时返回 `status: "pending_grading"`（`pending=true, score=0`），后台异步 AI 批阅；客观题照旧即时出分。
- **GET** `/api/v1/records/my-tests` — "我的测试"三桶聚合 `{ongoing, upcoming, completed, server_now}`；卡片按试卷聚合 `attempts / latest_status / latest_score / my_record_id / analysis_unlocked`。
- **GET** `/api/v1/records/{id}/report` — 新增 `pending / analysis_locked / partial_count / pending_count`；题目明细新增 `is_pending / is_partial / gained / eq_score / comment`。**解析锁**：pending 或 now≤end_time 时抹除标准答案/解析/评语（防泄题）。

### 5.6 题海 v1.2 变更
- 题型扩展 `fill / short`：fill 的 `answer` 为二维数组 `[["北京","北京市"],["京"]]`，保存强校验 `title.count("___") == len(answer)`；short 的 `answer=["标准答案全文"]` + `grading_points=["踩分点"]`。
- **PUT** 编辑被 published/archived 卷引用的题目 → 400（全局只读）；**POST** `/{id}/copy` 复制新题；**DELETE** 改为软删除 `is_deleted=1`（已引用试卷不受影响）。
- Excel 导入支持 fill（`a,b|c` 格式）与 short（可选"踩分点"列）。


---

## 6. v1.3 注册资料契约 (2026-09-06 落地)

### 6.1 注册 `POST /api/v1/auth/register`
- **Request Body**:
  ```json
  {
    "username": "3-50位", "password": "至少6位",
    "nickname": "昵称(必填,1-30位)", "gender": "male|female(必选)",
    "phone": "大陆11位(必填,全局唯一)", "position": "职务(选填)", "email": "选填"
  }
  ```
- **校验口径**: 必填/格式/唯一性全部返回 `400 + 中文 detail`（"请填写昵称"/"请选择性别"/"手机号格式不正确（需为大陆 11 位手机号）"/"该手机号已被注册"/"该用户名已被占用"/"邮箱格式不正确"）。**禁止改回 Pydantic 422**（C端拦截器不解析 422）。
- **Response 201**: `UserResponse{ id, username, nickname, gender, position, phone, email, avatar, status, created_at }`。

### 6.2 个人资料 `GET /api/v1/users/me`
- 返回当前登录用户完整 `UserResponse`（个人中心展示与昵称刷新依赖）。

### 6.3 昵称展示口径 (nickname display policy)
- 全端统一：**昵称优先，无则回退用户名**（老用户 nickname=NULL）。
- B端已接入：用户列表(users)、全站答题明细(users/records，响应新增 nickname 字段)、阅卷大厅列表与详情、考情看板 user_records。
- C端已接入：登录响应 user、/users/me、个人中心 (昵称大字 + @用户名 + 性别/职务标签)。
- users 表唯一索引: `uix_users_phone(phone)`；五列均经 main.py auto_patch 幂等补列。

---

## 7. v1.3 智能体与模型枢纽契约 (2026-09-08 落地)

### 7.1 看板聚合 `GET /api/v1/admin/dashboard/stats`
- **权限**：B端登录；出题人仅看本人试卷口径（与试卷列表隔离一致），超管/管理员全览。
- **Response 200**: `{ kpi{exams, records, ai_usage, pending}, deltas{exams, records, ai_usage}, sparks{exams, records, ai}, trend[{day, count, avg}]×7, donut[{name, value}]（客观/主观/组合/实操/其他，按题型构成划分）, hot[{exam_id, title, count}]Top5, recent[{time, name, username, score, status}]×5, notices[{text, date}]×4（本人通知）, quota{used_today, remaining, limit} }`。

### 7.2 RAG 私有库
- `POST /api/v1/admin/rag/documents` (201, multipart, 10MB, txt/md/pdf/docx)：小文档同步向量化，大文档后台进行。
- `GET /api/v1/admin/rag/documents`（超管全览，他人仅自传）、`GET /api/v1/admin/rag/documents/{id}`（进度）、`DELETE /api/v1/admin/rag/documents/{id}`（归属校验）。
- `POST /api/v1/admin/rag/search` `{query, limit≤20, doc_ids?}`（出题人自动限定自传文档）。
- `GET /api/v1/admin/rag/chunks?ids=`（溯源抽屉批量取块，越权块过滤）。
- AI 出题新增 `doc_ids?` 参数：命中切片拼入 prompt，预览题目带 `source_ref[{doc_id, chunk_id}]`；`QuestionCreate/QuestionResponse` 新增 `source_ref`（批量入库透传）。

### 7.3 Mem0 长期记忆 (静默，无独立端点)
- `User_ID` 口径：`admin:{id}`；聊天/组卷入口后台提取偏好，新建对话与出题组卷 Prompt 自动注入。
- 开关：`MEM0_ENABLED=0` 关闭；失败静默降级不阻断主流程；本地 Develop 用 fastembed + qdrant 本地路径。

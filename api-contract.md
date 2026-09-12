# 智题库 (TiKu) v1.5 API 接口契约规范 (API Contract)

> **版本标识**：v1.5 (全链路实库验证版)  
> **更新时间**：2026-09-12  
> **基准协议**：RESTful + SSE 实时流式 + JWT 鉴权 + `X-Tenant-Id` 多租户隔离头

---

## 一、全局通用约定

### 1.1 基础前缀与网关
- **API 统一根路径**：`/api/v1/`
- **公共鉴权**：`/api/v1/auth/`
- **SaaS 机构业务 (B端)**：`/api/v1/saas/`
- **C 端学员专区 (真实实库挂载)**：`/api/v1/member/`

### 1.2 鉴权与租户请求头
除登录接口外，所有受保护接口必须在 HTTP Header 中携带：
```http
Authorization: Bearer <jwt_token>
X-Tenant-Id: <tenant_id>
```

---

## 二、身份鉴权模块 (`/api/v1/auth`)

### 2.1 学员/成员登录
- **端点**：`POST /api/v1/auth/login`
- **请求体**：
```json
{
  "phone": "13900000006",
  "password": "123456"
}
```
- **响应体 (200 OK)**：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOi...",
    "user": {
      "id": 10,
      "username": "13900000006",
      "nickname": "陈伟",
      "phone": "13900000006",
      "role": "member"
    },
    "default_tenant_id": 2,
    "joined_tenants": [
      {
        "tenant_id": 2,
        "tenant_name": "皓石集团",
        "role": "member"
      }
    ]
  }
}
```

---

## 三、C 端移动端实库接口 (`/api/v1/member/...`)

### 3.1 获取可考测评列表 (带本人作答状态)
- **端点**：`GET /api/v1/member/member-tasks`
- **权限**：`require_member`
- **说明**：自动过滤出当前租户所有已发布的试卷，并聚合携带本人的作答进度、成绩与状态。
- **响应体**：
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "task_id": 1,
        "title": "2026年企业信息安全与合规考核",
        "category_id": 2,
        "total_score": 100,
        "pass_score": 60,
        "status": "published",
        "time_limit": 60,
        "deadline": "2026-12-31 23:59:59",
        "my_status": "submitted",
        "my_record_id": 88,
        "my_score": 90,
        "can_continue": false,
        "verification_mode": "manual"
      }
    ]
  }
}
```

---

### 3.2 考生入考取题（防泄题脱敏）
- **端点**：`GET /api/v1/member/tasks/{task_id}/entry`
- **机制**：服务端权威记录开考时刻 `created_at`，杜绝改本地时间作弊；响应中**严格剥离正确答案与解析**。
- **响应体**：
```json
{
  "code": 200,
  "data": {
    "task_id": 1,
    "exam_title": "2026年企业信息安全与合规考核",
    "title": "2026年企业信息安全与合规考核",
    "is_timed": true,
    "time_limit": 60,
    "deadline": "2026-12-31T23:59:59",
    "server_now": "2026-09-12T17:00:00.000000",
    "started_at": "2026-09-12T16:55:00.000000",
    "my_status": "pending",
    "my_record_id": 88,
    "my_answers": [],
    "questions": [
      {
        "id": 101,
        "type": "single_choice",
        "title": "离开工位时应如何处理电脑？",
        "content": "离开工位时应如何处理电脑？",
        "options": ["Win+L 锁屏", "保持屏幕常亮", "直接拔电源"],
        "score": 10,
        "category_id": 2
      }
    ]
  }
}
```

---

### 3.3 考生提交试卷 (交卷)
- **端点**：`POST /api/v1/saas/task-records/submit`
- **说明**：交卷端点挂载在 tasks 模块上。单选/多选/判断必须提交**选项Key**（如 "A" 或 ["A", "C"]），判断题必须提交 "A" 或 "B"，严禁传中文选项文本。
- **请求体**：
```json
{
  "task_id": 1,
  "time_spent": 120,
  "answers": [
    {
      "resource_id": 101,
      "answer": "A"
    },
    {
      "resource_id": 102,
      "answer": ["A", "C"]
    }
  ]
}
```
- **响应体**：
```json
{
  "code": 200,
  "message": "试卷已成功提交",
  "data": {
    "record_id": 88,
    "status": "pending_verification",
    "score": 0,
    "time_spent": 120
  }
}
```

---

### 3.4 考生答题记录列表 (我的测试)
- **端点**：`GET /api/v1/member/task-records`
- **说明**：获取当前学员在该租户下的所有历史作答记录。
- **响应体**：
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "record_id": 88,
        "task_id": 1,
        "task_title": "2026年企业信息安全与合规考核",
        "status": "pending_verification",
        "score": null,
        "submit_time": "2026-09-12 17:05:22"
      }
    ]
  }
}
```

---

### 3.5 单次成绩结果与答题复盘
- **端点**：`GET /api/v1/member/task-records/{record_id}`
- **说明**：查看单次作答的成绩单与每道题的作答对照。
- **响应体**：
```json
{
  "code": 200,
  "data": {
    "record_id": 88,
    "task_id": 1,
    "task_title": "2026年企业信息安全与合规考核",
    "status": "verified",
    "pending": false,
    "score": 90,
    "passed": true,
    "time_spent": 540,
    "comments": "完成得非常好，合规意识强",
    "ai_comments": "客观题全部正确",
    "submit_time": "2026-09-12 17:05:22",
    "items": [
      {
        "resource_id": 101,
        "content": "离开工位时应如何处理电脑？",
        "type": "single_choice",
        "options": ["Win+L 锁屏", "保持屏幕常亮", "直接拔电源"],
        "user_answer": "Win+L 锁屏",
        "correct_answer": "Win+L 锁屏",
        "explanation": "企业安全规范要求必须立即锁屏",
        "eq_score": 10
      }
    ]
  }
}
```

---

### 3.6 个人中心统计面板
- **端点**：`GET /api/v1/member/me/stats`
- **说明**：个人中心顶部资产统计。
- **响应体**：
```json
{
  "code": 200,
  "data": {
    "total_exams_taken": 12,
    "history_count": 12,
    "passed_count": 11,
    "pass_rate": 91.7,
    "favorite_count": 5
  }
}
```

---

### 3.7 重点题目收藏管理
- **获取收藏列表**：`GET /api/v1/member/favorites`
- **添加题目收藏**：`POST /api/v1/member/favorites`（请求体：`{"resource_id": 101}`）
- **取消题目收藏**：`DELETE /api/v1/member/favorites/{resource_id}`

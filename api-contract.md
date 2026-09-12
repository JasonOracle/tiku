# 智题库 (TiKu) v1.5 API 接口契约规范 (API Contract)

> **版本标识**：v1.5 (SaaS 多租户与双端对齐规范)  
> **更新时间**：2026-09-12  
> **基准协议**：RESTful + SSE 实时流式 + JWT 鉴权 + `X-Tenant-Id` 多租户隔离头

---

## 一、全局通用约定

### 1.1 基础前缀
- **API 统一根路径**：`/api/v1/`
- **公共鉴权**：`/api/v1/auth/`
- **SaaS 机构业务**：`/api/v1/saas/`
- **C 端考生专区**：`/api/v1/saas/member/`

### 1.2 鉴权与租户请求头
所有受保护接口必须在 HTTP Header 中携带：
```http
Authorization: Bearer <jwt_token>
X-Tenant-Id: <tenant_id>
```

---

## 二、身份鉴权模块 (`/api/v1/auth`)

### 2.1 账号密码登录
- **端点**：`POST /api/v1/auth/login`
- **请求体**：
```json
{
  "username": "13900000006",
  "password": "123456"
}
```
- **响应体 (200 OK)**：
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 10,
    "username": "13900000006",
    "name": "陈伟",
    "role": "member",
    "tenant_id": 2
  }
}
```

---

## 三、C 端移动端核心接口 (`/api/v1/saas/member`)

### 3.1 获取可考测评列表
- **端点**：`GET /api/v1/saas/tasks?status=published`
- **说明**：获取当前租户下所有已发布的测评试卷列表。
- **响应格式**：试卷数组（包含 id, title, total_score, pass_score, time_limit, deadline 等）。

---

### 3.2 考生进入考试（拉取试卷题目）
- **端点**：`GET /api/v1/saas/member/tasks/{task_id}/entry`
- **说明**：
  - 服务端权威锁定开考时刻 `created_at`，防止客户端改时钟作弊；
  - **防泄题机制**：响应中严格剥离正确答案（`correct_answer` 与 `explanation` 字段置空）。
- **响应体**：
```json
{
  "task": {
    "id": 1,
    "title": "2026年企业信息安全与合规考核",
    "time_limit": 60,
    "total_score": 100
  },
  "questions": [
    {
      "id": 101,
      "type": "single_choice",
      "content": "关于工作电脑锁屏，下列做法正确的是？",
      "options": ["离开工位立即 Win+L 锁屏", "中午吃饭无需锁屏", "下班直接拔电源"],
      "score": 10
    }
  ],
  "record": {
    "status": "pending",
    "time_spent": 0
  }
}
```

---

### 3.3 考生提交试卷
- **端点**：`POST /api/v1/saas/member/tasks/{task_id}/submit`
- **请求体**：
```json
{
  "answers": {
    "101": "离开工位立即 Win+L 锁屏",
    "102": ["A", "C"]
  }
}
```
- **响应体**：
```json
{
  "record_id": 88,
  "status": "pending_verification",
  "total_score": 0,
  "time_spent": 842,
  "message": "试卷已成功提交"
}
```

---

### 3.4 动态成绩与复盘报告
- **端点**：`GET /api/v1/saas/member/tasks/{task_id}/my_result`
- **响应行为**：
  - **客观题已批阅**：返回总分、及格判定，`items` 中包含我的作答与标准答案对照。
  - **含主观题核验中**：返回状态 `pending_verification`，**答案与解析字段打码或隐藏**，防止考后对答案泄题。

---

### 3.5 个人中心统计面板
- **端点**：`GET /api/v1/saas/member/me/stats`
- **说明**：个人中心顶部资产统计。
- **响应体**：
```json
{
  "completed_exams": 12,
  "pass_rate": 91.6,
  "favorite_count": 5,
  "avg_score": 86.5
}
```

---

### 3.6 重点题目收藏/取消收藏
- **端点**：`POST /api/v1/saas/member/resources/{resource_id}/favorite`
- **响应体**：`{"favorited": true, "message": "已加入收藏夹"}`

---

## 四、B 端核心管理接口概要

| 模块 | 端点 | 方法 | 说明 |
| :--- | :--- | :--- | :--- |
| **仪表盘** | `/api/v1/saas/dashboard/stats` | `GET` | 机构试卷/题目/考生汇总看板 |
| **题库管理** | `/api/v1/saas/resources` | `GET/POST` | 题目增删改查与批量导入 |
| **试卷管理** | `/api/v1/saas/tasks` | `GET/POST` | 试卷创建、组卷与发布 |
| **AI 助手** | `/api/v1/saas/ai/chat` | `POST (SSE)` | 对话式智能出题与工具调用流 |
| **AI 知识库** | `/api/v1/saas/kb/documents` | `GET/POST` | 教学文档上传与切片管理 |
| **阅卷管理** | `/api/v1/saas/verification/records` | `GET/POST` | 主观题流水线评分核验 |
| **成员管理** | `/api/v1/saas/members` | `GET/POST` | 学员名单导入与角色配置 |

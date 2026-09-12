# 智题库 (TiKu) v1.5 系统架构与技术白皮书 (Tech Spec)

> **版本标识**：v1.5 (跨端重构基线)  
> **更新时间**：2026-09-12  
> **设计美学**：极客蓝 (Geek Blue) 沉浸式极简 / 纯正 SVG 图标规范

---

## 一、系统全景架构

```
┌─────────────────────────────────────────────────────────────┐
│                      智题库 TiKu 总体技术拓扑                │
├──────────────────────────────┬──────────────────────────────┤
│      B 端管理后台 (PC)       │     C 端考生端 (H5/小程序)    │
│  - 框架: Vue 3.5 + Vite 8    │  - 框架: uni-app + Vue 3.5   │
│  - 语言: TypeScript 5.8      │  - 语言: TypeScript 5.8      │
│  - UI: Element Plus          │  - UI: Wot Design Uni        │
│  - 目录: /tob                │  - 目录: /toc-new            │
├──────────────────────────────┴──────────────────────────────┤
│                   Nginx 反向代理层 (Port 80)                │
│    /admin/ → tob 产物 │ / → toc-new 产物 │ /api/v1/ → 后端  │
├─────────────────────────────────────────────────────────────┤
│               FastAPI SaaS 核心后端 (Python 3.12)           │
│   - 架构: 多租户逻辑隔离 + JWT 鉴权 + 自动化审计切片        │
│   - AI: 深度结合 LLM 与私有知识库切片 (Mem0 / Qdrant)        │
│   - 数据库: MySQL 8.0 (InnoDB) 增量迁移驱动                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、C 端极客架构规范 (toc-new)

### 2.1 技术栈选型与目录设计
- **运行时环境**：`uni-app` (Vite + TypeScript 模板)
- **核心组件库**：`wot-design-uni`（适配 uni-app 的现代化极简移动组件库）
- **状态管理**：`pinia` + `pinia-plugin-persistedstate`
- **样式方案**：Sass/SCSS，定义极客蓝全局主题变量

**工程目录树**：
```
/toc-new
├── src/
│   ├── api/                 # 统一 API 模块（auth.ts, exam.ts, user.ts）
│   ├── components/          # 通用业务组件（沉浸 Header、SVG 容器等）
│   ├── static/              # 静态资源与纯正 SVG 图标集
│   ├── stores/              # Pinia 状态树（user.ts, examSession.ts）
│   ├── utils/
│   │   └── request.ts       # 统一请求拦截、Token 注入与错误 Toast
│   ├── pages/
│   │   ├── index/index.vue  # 首页（大卡片流、考试直达）
│   │   ├── records/index.vue# 我的测试（历史回顾、成绩报告）
│   │   ├── profile/index.vue# 个人中心（通顶卡片、收藏、退出）
│   │   ├── exam/index.vue   # 沉浸作答流（单题聚焦、左右滑动手势）
│   │   ├── report/index.vue # 动态成绩报告（防泄题审查态）
│   │   └── login/index.vue  # 极简登录页（极客蓝通顶微渐变）
│   ├── App.vue
│   ├── main.ts
│   ├── manifest.json
│   └── pages.json           # 路由表、自定义 NavigationBar 与 Tabbar 配置
├── package.json
└── vite.config.ts
```

### 2.2 视觉与主题体系 (Geek Blue)
- 主色调：`--geek-blue: #1D63FF;`
- 背景底色：`--bg-light: #F6F8FC;`
- 卡片背景：`--bg-card: #FFFFFF;`
- 主文字色：`--text-main: #1C2331;`
- 次级文字色：`--text-secondary: #748094;`
- 渐变色：`linear-gradient(135deg, #1D63FF 0%, #0045D8 100%);`

### 2.3 网络请求层规范 (`utils/request.ts`)
1. **多租户与 Token 自动透传**：
   - 请求头自动追加：`Authorization: Bearer <token>`
   - 自动透传租户标识：`X-Tenant-Id: <tenant_id>`
2. **错误自愈与拦截**：
   - 401 状态：清空本地凭证，无感知跳回 `/pages/login/index`
   - 403 越权或租户异常：给予明确 Wot Design Toast 告警

---

## 三、答题流状态机与安全规范

### 3.1 单题聚焦作答状态机
- 题目列表载入后，以当前索引 `currentIndex` 驱动 UI 视口。
- 选项点击实时更新 `examSession.answers[question_id]`。
- **离开屏幕检测**：利用 `document.addEventListener('visibilitychange')` 监控考生离开界面频次，达到限额触发警告或强制交卷。

### 3.2 成绩与防泄题逻辑
- **客观题试卷**：交卷后直接触发自动算分，报告页展示环形得分与题卡对错对比。
- **混合题型/主观题试卷**：
  - 后端标记交卷状态为 `pending_review`；
  - 前端阻断标准答案渲染，仅展示“正在等待人工/AI批阅核验后公布成绩”；
  - 彻底规避传统考试系统中考完立刻对答案导致的泄题风险。

---

## 四、数据持久化与增量迁移策略 (Migration)

遵循**选项 A 增量迁移**准则，保护既有业务数据资产：
1. **核心实体**：
   - `tenants`（多租户空间）
   - `users`（学员与管理员）
   - `resources`（多题型题库资源）
   - `tasks`（试卷与考试载体）
   - `task_records`（答题记录与主观题批阅快照）
   - `favorites`（学员重点题目收藏表）
2. **幂等迁移保障**：
   - `backend/app/services/db_migrate.py` 的 `ensure_schema()` 负责动态检视 MySQL 列结构，增量补齐必要字段，杜绝数据被清空。

---

## 五、质量保障与验证基线

1. **静态检查与构建测试**：
   - C 端工程在 `toc-new/` 必须跑通 `pnpm build:h5`；
   - B 端工程在 `tob/` 必须跑通 `pnpm run build`。
2. **自动化后端回归**：
   - 执行 `pytest` 跑通核心接口回归套件。

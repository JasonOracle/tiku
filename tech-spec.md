# 智题库 (TiKu) v1.5 系统架构与技术白皮书 (Tech Spec)

> **版本标识**：v1.5 (C端 Apple 钛金微光重塑版·实库校准)  
> **更新时间**：2026-09-13  
> **设计美学**：Apple 钛金微光风 (Light-Titanium Glassmorphism) / 原生内联题型 / 纯正 SVG 规范

---

## 一、系统全景拓扑与端口分配

```
┌─────────────────────────────────────────────────────────────┐
│                      智题库 TiKu 总体技术拓扑                │
├──────────────────────────────┬──────────────────────────────┤
│      B 端管理后台 (PC)       │     C 端考生端 (H5/小程序)    │
│  - 框架: Vue 3.5 + Vite 8    │  - 框架: uni-app + Vue 3.5   │
│  - 语言: TypeScript 5.8      │  - 语言: TypeScript 4.9.5    │
│  - UI: Element Plus          │  - 风格: Apple 钛金微光风    │
│  - 目录: /tob (Dev 端口 5173)│  - 目录: /toc-new (Dev 5174) │
├──────────────────────────────┴──────────────────────────────┤
│                   Nginx 反向代理层 (Port 80)                │
│  /admin/ → tob 产物 │ / → toc-new H5 产物 │ /api/v1/ → 后端 │
├─────────────────────────────────────────────────────────────┤
│             FastAPI SaaS 核心后端 (Python 3.12, 端口 8000)   │
│   - 架构: 多租户逻辑隔离 + JWT 鉴权 + 自动化审计切片        │
│   - AI: 深度结合 LLM 与私有知识库切片 (Mem0 / Qdrant)        │
│   - 数据库: MySQL 8.0 (InnoDB) 增量迁移驱动                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 开发与运行环境端口分配
- **FastAPI 后端**：`http://127.0.0.1:8000`
- **B 端管理后台 (tob)**：`http://localhost:5173`（base: `/admin/`）
- **C 端极客移动端 (toc-new)**：`http://localhost:5174`（base: `/`）
- **Nginx 统一网关**：`http://localhost` (Port 80)

---

## 二、C 端架构规范 (toc-new)

### 2.1 技术栈选型与目录设计
- **运行时环境**：`uni-app` (Vite + TypeScript 模板，由 `pnpm` 驱动)
- **渲染策略**：卡帕西务实范式，题目与选项原生展开内联渲染（零多层嵌套黑盒依赖，规避高度塌陷与白屏）
- **状态管理**：`pinia` + `pinia-plugin-persistedstate`
- **样式方案**：Sass/SCSS，由全局 `src/styles/tokens-apple.scss` 接管 Apple 钛金微光设计令牌

**工程目录树**：
```
/toc-new
├── src/
│   ├── api/                 # 统一 API 模块（auth.ts, exam.ts, user.ts）
│   ├── components/          # 通用业务组件（CustomHeader, PageState, GlobalToast）
│   ├── styles/              # 设计令牌规范（tokens-apple.scss）
│   ├── static/              # 静态资源与纯正 SVG 图标集
│   ├── stores/              # Pinia 状态树（user.ts, toast.ts）
│   ├── utils/
│   │   ├── format.ts        # 日期、时长、数字归一化工具
│   │   └── request.ts       # 统一请求拦截、Token 与 Tenant-Id 注入、401 拦截
│   ├── pages/
│   │   ├── index/index.vue  # Tab 1: 首页大厅（多色温漫反射卡片、动态胶囊 Banner）
│   │   ├── records/index.vue# Tab 2: 我的测试（果冻吸顶滑块、脉冲进行中绿点）
│   │   ├── profile/index.vue# Tab 3: 个人中心（钛金玻璃卡片、错题收藏、退出）
│   │   ├── exam/index.vue   # 子页面: 沉浸考场（高对比度纯白文本域、双大胶囊、60vh抽屉）
│   │   ├── report/index.vue # 子页面: 成绩报告（标准白底毛玻璃 Navbar、双模态防泄题看板）
│   │   ├── favorites/index.vue # 子页面: 我的收藏（错题卡片流、一键温故知新）
│   │   └── login/index.vue  # 子页面: 极简登录页（暮光光晕、隐式租户绑定）
│   ├── App.vue
│   ├── main.ts
│   ├── manifest.json
│   └── pages.json           # 路由表、自定义 NavigationBar 与 Tabbar 配置
├── package.json
└── vite.config.ts
```

### 2.2 Apple 钛金微光设计令牌 (`tokens-apple.scss`)
- 钛金冷白底盘：`$bg: #fbfbfd; $surface: #ffffff;`
- 墨色梯队：`$ink: #1d1d1f; $ink-2: #3a3a3c; $muted: #86868b;`
- 暮光微渐变主色：`$accent: #1852e0; $gradient: linear-gradient(135deg, #1852e0 0%, #0a3299 100%);`
- 漫反射多层微弥散阴影：`$shadow-card: 0 1px 2px rgba(20, 30, 60, 0.04), 0 8px 28px rgba(20, 30, 60, 0.08);`
- 琉璃毛玻璃材质：`$glass-blur: blur(24px) saturate(180%);`
- 高清晰输入规范：`border: 2rpx solid #cbd5e1; background: #ffffff; color: #0f172a;`


### 2.3 `pages.json` 规范定义
```json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": { "navigationStyle": "custom" }
    },
    {
      "path": "pages/records/index",
      "style": { "navigationStyle": "custom" }
    },
    {
      "path": "pages/profile/index",
      "style": { "navigationStyle": "custom" }
    },
    {
      "path": "pages/login/index",
      "style": { "navigationStyle": "custom" }
    },
    {
      "path": "pages/exam/index",
      "style": { "navigationStyle": "custom" }
    },
    {
      "path": "pages/report/index",
      "style": { "navigationStyle": "custom" }
    }
  ],
  "tabBar": {
    "color": "#94A3B8",
    "selectedColor": "#1D63FF",
    "borderStyle": "white",
    "backgroundColor": "#FFFFFF",
    "list": [
      { "pagePath": "pages/index/index", "text": "首页" },
      { "pagePath": "pages/records/index", "text": "我的测试" },
      { "pagePath": "pages/profile/index", "text": "个人中心" }
    ]
  }
}
```

---

## 三、答题流数据契约与状态机

### 3.1 答案收集数据契约
交卷接口 `POST /api/v1/saas/task-records/submit` 接收的 `answers` 格式必须严格对齐后端 `SubmitAnswers` 规范：
```typescript
interface UserAnswerItem {
  resource_id: number;
  answer: string | string[]; // 单选/判断/简答为 string，多选为 string[]
}
```
严禁序列化为字典对象 `{101: "A"}`，必须提交为对象数组 `[{"resource_id": 101, "answer": "A"}]`。

### 3.2 成绩与防泄题逻辑
- **客观题试卷**：交卷后直接触发自动算分，报告页展示环形得分与题卡对错对比。
- **混合题型/主观题试卷**：
  - 后端标记交卷状态为 `pending_verification`；
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

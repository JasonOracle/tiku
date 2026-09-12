# 智题库 (TiKu) 动态事实与研发进度总览 (Progress)

> **当前全局版本**：v1.5 (C端跨端极客重构)  
> **最新状态冻结时间**：2026-09-12 16:55:00  
> **执行标准**：严格执行 `agent.md`「最高行为准则」与「跨版本大更迭最高协议」

---

## 一、版本里程碑与状态总线

```
[v1.0 MVP] ──> [v1.2 AI-Native] ──> [v1.3 RAG/状态机] ──> [v1.4 SaaS多租户与Agent] ──> [v1.5 Geek App]
                                                                │
                                                                ▼
                                                   【已打 Tag: v1.4-final】
                                                   【旧核心文档已物理归档至 history/】
                                                   【已完成全套文档死角排查与接口实库对齐】
```

- ✅ **v1.4 结项成果归档**：
  - B 端管理后台（PC 端）全面稳态，多租户权限校验（`require_admin`）全面加固；
  - AI 智能助手交互卡片全面汉化、参数卡片重构，消息与卡片状态完整落库持久化（`action_card_data`）；
  - 自动化截屏与 v1.4 展示文档系统上线（`docs/v1.4_showcase.md`，双击批处理一键刷新）；
  - 代码库已打标：`git tag -a v1.4-final -m "End of version 1.4"` 并推送到云端。

- 🚀 **v1.5 深度审视与冲突查漏补缺（已完成）**：
  - **端口冲突消除**：明确后端 `8000`、B端 `5173`、C端 `5174`，避免 Vite 端口碰撞；
  - **关键接口实库对齐**：排查并修正了交卷端点（`POST /api/v1/saas/task-records/submit`）、记录查询（`GET /api/v1/saas/member/task-records`）与入参 `answers: [{resource_id, answer}]` 契约，规避了潜在的 404 与 422 风险；
  - **路由规范固化**：在 `tech-spec.md` 中白纸黑字固化 `pages.json` 规范定义；
  - **docs 与 history 职责分工**：明确 `docs/` 为对外全景展示中心（供 README 与外部浏览，绝不挪走），`history/` 为开发底稿归档区。

---

## 二、v1.5 实施路线与四阶段节奏

### 阶段 1：工程基建与网络底座 (Phase 1: Infrastructure) —— 【即将启动】
- [ ] 1.1 初始化 `toc-new` 脚手架（基于 `uni-app` Vue3 + TS + Vite 模板）
- [ ] 1.2 使用 `pnpm` 安装核心依赖：`wot-design-uni`、`pinia`、`pinia-plugin-persistedstate`、`sass`
- [ ] 1.3 搭建网络层：`src/utils/request.ts`（统一拦截器、自动注入 `Authorization` 与 `X-Tenant-Id`、401 自动跳回登录）
- [ ] 1.4 配置极客蓝 SCSS 主题变量与纯正 SVG 图标集

### 阶段 2：应用骨架与三大 Tab 体系 (Phase 2: App Skeleton & Tabs)
- [ ] 2.1 极简登录页 `pages/login/index.vue`（手机号+密码，极客蓝通顶微渐变，租户自动静默绑定）
- [ ] 2.2 底部三 Tabbar 配置（`pages.json`）：
  - 🏠 首页 `pages/index/index.vue`
  - 📝 我的测试 `pages/records/index.vue`
  - 🧑 个人中心 `pages/profile/index.vue`
- [ ] 2.3 自定义沉浸式通顶 Header 组件

### 阶段 3：沉浸式单题作答流 (Phase 3: Immersive Exam Flow)
- [ ] 3.1 考场初始化与开考页 `pages/exam/index.vue`
- [ ] 3.2 单题聚焦视野与左右滑动 (Swiper) 交互
- [ ] 3.3 半屏 60% 高度答题卡抽屉与题号快速定位
- [ ] 3.4 离开屏幕检测防作弊与倒计时联动

### 阶段 4：动态报告与个人资产中心 (Phase 4: Dynamic Report & Profile)
- [ ] 4.1 动态结果报告页 `pages/report/index.vue`（纯客观题环形得分 vs 主观题安全防泄题审核态）
- [ ] 4.2 个人中心 `pages/profile/index.vue`（资产卡片、历史统计、重点题目收藏）
- [ ] 4.3 Nginx 配置联调：将移动端根路径 `/` 无缝平滑切换至 `toc-new` 产物

---

## 三、接手检查清单 (Handover Checklist)

后续任何 Agent 接手开发时，按以下步骤入场：
1. **核对代码与 Tag**：确认当前在 `dev` 分支，最新 tag 为 `v1.4-final`。
2. **确认服务健康**：
   - 后端容器：`docker ps` 确保 `tiku_backend` 为 `healthy`。
   - B端管理后台：`http://localhost/admin` 正常运行。
3. **开发展开点**：从【阶段 1：工程基建与网络底座】开始在根目录下使用 `pnpm` 创建并初始化 `toc-new` 移动端工程。

---
*时间戳签名：2026-09-12 16:55:00 (Antigravity Engineering Closure)*

/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 勾选阶段一 1.1～1.3 完成项并补齐交付物与验收证据; 2. 新增「接口契约与后端实际路由不符」待办（不擅自修改核心文档）; 3. 刷新状态冻结时间]
 */

# 智题库 (TiKu) 动态事实与研发进度总览 (Progress)

> **当前全局版本**：v1.5 (C端跨端极客重构)  
> **最新状态冻结时间**：2026-09-12 17:39:01  
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

### 阶段 1：工程基建与网络底座 (Phase 1: Infrastructure) —— 【✅ 已完成交付】
- [x] 1.1 初始化 `toc-new` 脚手架（基于 `uni-app` Vue3 + TS + Vite 模板）
- [x] 1.2 使用 `pnpm` 安装核心依赖：`wot-design-uni`、`pinia 3.0.4`、`pinia-plugin-persistedstate 4.7.1`、`sass`（修正 pnpm 软链传递依赖解析）
- [x] 1.3 搭建网络层：`src/utils/request.ts`（统一拦截器、自动注入 `Authorization` 与 `X-Tenant-Id`、401 自动跳回登录，GlobalToast 全局轻提示桥接）
- [ ] 1.4 配置极客蓝 SCSS 主题变量与纯正 SVG 图标集（移至阶段二配合 UI 落地）

**阶段 1 交付物清单（`toc-new/`）**：
- 脚手架：官方模板 `dcloudio/uni-preset-vue#vite-ts`；依赖 `wot-design-uni 1.14.0`、`pinia 3.0.4`、`pinia-plugin-persistedstate 4.7.1`、`sass`（dev）。
- 配置：`vite.config.ts`（端口 5174 + `/api/v1`、`/uploads` 代理至 `127.0.0.1:8000`）；`pages.json`（wot easycom 自动引入、`navigationStyle: custom`、本阶段不配 tabBar）；`tsconfig.json`（修正第三方库源码类型误报）。
- 状态层：`src/stores/index.ts`（Pinia 实例 + uni 存储适配的持久化插件）、`src/stores/user.ts`（token / userInfo / tenantId / joinedTenants）、`src/stores/toast.ts`（轻提示中转 + 全局调用入口）。
- 反馈层：`src/components/GlobalToast.vue` + `GlobalToast.md`（Pinia 桥接 wd-toast，解决纯 TS 文件无法调用 `useToast()` 的问题；未挂载时自动降级 `uni.showToast`）。
- 网络层：`src/utils/request.ts`（泛型 `request<T>`、注入 `Authorization` 与 `X-Tenant-Id`、401 清态并回登录页且防死循环、业务码失败走全局轻提示）。
- 接口层：`src/api/auth.ts`（登录）、`src/api/exam.ts`（测评列表 / 入考取题 / 交卷 / 成绩详情），出入参全量精确 TS 类型。
- 页面：`src/pages/login/index.vue` 最小占位页（保证 401 跳转物理可达并挂载 `GlobalToast`）。
- 验收证据（终端物理输出）：
  1. `pnpm type-check`（`vue-tsc --noEmit`）零报错；
  2. `pnpm build:h5` 输出 `DONE Build complete.`，产物落于 `dist/build/h5`（含 `pages-login-index.*.js` 与 wot-design-uni 图标字体）；
  3. `pnpm dev:h5` 在 `http://localhost:5174` 返回 HTTP 200；
  4. 真实浏览器（Chromium，390×844 移动端视口）渲染实测：`#/pages/login/index` 路由命中，页面文本正确输出「智题库」与占位说明，`uni-app` 根节点正常挂载，控制台除模板默认缺失的 `/favicon.ico`（404，非功能性）外无任何致命报错。

**⚠️ 已知偏差与待办（不擅自改动核心文档）**：
1. **`api-contract.md` 与后端实际路由不符**：文档中的 `/api/v1/saas/*` 前缀在 `backend/app/main.py` 中根本不存在（`saas` 仅为 Python 模块目录名），实际 C 端统一挂在 `/api/v1/member/*`。本次已按**真实后端**落地路由，`api-contract.md` 的路由表与登录契约（真实入参为 `phone`，响应为 `{code,message,data:{token,user,default_tenant_id,joined_tenants}}`，无 `access_token`）需要后续专项修订。
2. **`build:h5` 不做类型检查**：官方模板的 `uni build` 默认跳过 TS 检查，故已额外固化 `pnpm type-check` 作为第二道验收命令。
3. **pnpm 软链解析**：uni 工具链开启了 `preserveSymlinks`，导致 pinia 的传递依赖解析失败，已在 `vite.config.ts` 用 post 优先级插件纠正为 `false`。
4. **`answers` 取值语义未裁决**：`"A"`（选项字母）与选项原文两种表述均被后端评分逻辑兼容，类型层用 `string | string[]` 保留双形态，待作答流实现时确认。

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
3. **开发展开点**：阶段 1 已收口，直接从【阶段 2：应用骨架与三大 Tab 体系】开始。
   - C 端工程位于 `toc-new/`，启动命令 `cd toc-new && pnpm dev:h5`（端口 5174）；
   - 新增页面时务必在页面模板内挂载 `<GlobalToast />`，否则轻提示会降级为原生 toast；
   - 所有 C 端接口调用一律以 `/api/v1/member/*` 为准（真实后端路由），不要使用 `api-contract.md` 里的 `/api/v1/saas/*`。

---
*时间戳签名：2026-09-12 17:55:00 (Antigravity Engineering Closure)*

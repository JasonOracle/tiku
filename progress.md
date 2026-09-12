/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 新增「UI 选型双风格静态预览体系」交付记录（preview-linear / preview-apple 各 7 页 + preview-nav 索引台 + PreviewFloat 悬浮球组件）; 2. 补齐双风格验收证据与已知限制; 3. 刷新状态冻结时间]
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 勾选阶段 4.1 与 4.2（4.3 按决策不纳入本次）并补齐交付物、验收证据与已知限制; 2. 修正 api-contract.md 中仅剩的两处 /api/v1/saas/* 错误路由前缀; 3. 更新接手检查清单为阶段 1～4 全部收口并签署时间戳]
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 勾选阶段 3.1～3.4 并补齐交付物、答案取值语义裁决与验收证据; 2. 修正阶段一遗留的「answers 取值语义未裁决」条目; 3. 更新阶段 3 已知限制与待办; 4. 刷新状态冻结时间]
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 勾选阶段 1.4 与阶段 2 全部完成项并补齐交付物与验收证据; 2. 更新阶段 2 已知限制与待办; 3. 刷新状态冻结时间]
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 勾选阶段一 1.1～1.3 完成项并补齐交付物与验收证据; 2. 新增「接口契约与后端实际路由不符」待办（不擅自修改核心文档）; 3. 刷新状态冻结时间]
 */

# 智题库 (TiKu) 动态事实与研发进度总览 (Progress)

> **当前全局版本**：v1.5 (C端跨端极客重构)  
> **最新状态冻结时间**：2026-09-12 22:55:50  
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
- [x] 1.4 配置极客蓝 SCSS 主题变量与纯正 SVG 图标集（本项已于阶段 2 随 UI 落地一并完成）

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
4. **`answers` 取值语义已裁决（阶段 3 读表定论）**：必须提交**选项 key**——单选 / 判断为 `"A"` 形式字符串，多选为 `["A","B","D"]` 字符串数组；**判断题只能提交 `'A'`/`'B'`**（后端只归一化 `correct_answer` 侧的中文，不转换用户提交值）。`api-contract.md` 第 131-140 行示例中的选项原文（`"Win+L 锁屏"`）是错的，需与路由前缀一并在文档修订中纠正。

### 阶段 2：应用骨架与三大 Tab 体系 (Phase 2: App Skeleton & Tabs) —— 【已完成】
- [x] 2.1 极简登录页 `pages/login/index.vue`（手机号+密码，极客蓝通顶微渐变，租户自动静默绑定）
- [x] 2.2 底部三 Tabbar 配置（`pages.json`）：
  - 🏠 首页 `pages/index/index.vue`
  - 📝 我的测试 `pages/records/index.vue`
  - 🧑 个人中心 `pages/profile/index.vue`
- [x] 2.3 自定义沉浸式通顶 Header 组件

**阶段 2 交付物清单（`toc-new/`）**：
- 主题与图标：`src/uni.scss`（极客蓝 SCSS 变量 + `card-surface` / `gradient-surface` mixin，仅放编译期内容）；`src/App.vue`（全局 CSS 自定义属性 + `page` 基础样式，避免规则被重复注入每个组件）；`src/static/icons/` 下 6 个 TabBar 图标的「SVG 源文件 + 81×81 RGBA 透明 PNG」（`tab-home` / `tab-records` / `tab-profile` × 普通态中灰 + 极客蓝选中态）与 `brand-logo.svg`。
- 通用组件：`src/components/CustomHeader.vue` + `CustomHeader.md`（状态栏高度自适应、标题/副标题、返回键双行为、solid / gradient / transparent 三态底色）；`src/components/PageState.vue` + `PageState.md`（加载骨架 / 空态 / 错误态三合一，插画为内联手写 SVG，零图片资源）。
- 工具层：`src/utils/format.ts`（时间、截止、限时、手机号脱敏，以及作答状态与租户角色的中文映射，杜绝英文枚举外露）。
- 接口层：`src/api/exam.ts` 增补 `fetchMyRecords`、`fetchMyStats`（既有导出签名零变更）；`src/utils/request.ts` 失败响应兼容 FastAPI 的 `{ detail }` 结构，登录失败不再被吞成「服务异常（400）」。
- 页面：登录页（真实表单 + 前端校验 + 提交态 + 无企业归属拦截 + `switchTab` 进首页）、首页（通顶渐变 Header 展示机构名 + 欢迎统计 + 测评卡片流）、我的测试（吸顶分类「全部 / 待核验 / 已完成」+ 滑动指示器 + 记录卡片）、个人中心（通顶名片 + 四宫格统计 + 功能列表 + 二次确认退出登录）、考场占位页（承接首页卡片跳转并透传测评编号与名称）。
- 路由：`src/pages.json` 注册 5 个页面并正式激活 `tabBar`（3 项 + 6 个 PNG 双色态图标，选中色 `#1D63FF`）。
- 验收证据（终端与真实浏览器物理输出）：
  1. `pnpm type-check`（`vue-tsc --noEmit`）零报错；
  2. `pnpm build:h5` 输出 `DONE Build complete.`，产物 `dist/build/h5/static/icons/` 含全部图标文件；
  3. 真实浏览器（Chromium，390×844 移动端视口）完整闭环实测通过：未登录打开应用自动落到登录页 → 空表单提交触发「请输入手机号」内联校验 → 以 `13900000001 / 123456` 真实登录并跳转首页 → 首页渲染所属机构「浙江省星雅教育有限公司」与 3 张真实测评卡 → **tabBar 三个 PNG 图标全部正常渲染**（选中态极客蓝实心、未选中态中灰）→ 切到「我的测试」显示 3 条真实作答记录与分类栏 → 切到「个人中心」显示昵称、脱敏手机号、中文角色与 3 / 3 / 100% / 0 统计 → 切回首页 → 退出登录二次确认后回到登录页；控制台除模板默认缺失的 `/favicon.ico`（404，非功能性）外无任何报错。

**⚠️ 阶段 2 已知限制与待办**：
1. **页面内图标仍为内联 `<svg>`**：H5 端渲染正常，但小程序端不支持内联 svg 标签。TabBar 已按决策改用 PNG 规避跨端问题，后续若要上小程序，页面内图标需同样改为 `<image src="/static/icons/*.svg" />`。
2. **「我的收藏」入口为阶段性提示**：收藏接口后端已存在（`/api/v1/member/favorites`），按计划归属阶段 4.2，当前点击给出明确提示而非死链。
3. **历史成绩卡片与报告页跳转**：成绩报告页属阶段 4.1，当前「我的测试」记录卡片为纯展示，未绑定跳转。
4. **未引入全局路由守卫**：未登录访问 Tab 页仍依赖 `request.ts` 的 401 拦截回登录页；首页已在 `onShow` 前置判定登录态，避免无凭证请求导致骨架空闪。阶段 3 引入作答流后可评估是否统一守卫。

### 阶段 3：沉浸式单题作答流 (Phase 3: Immersive Exam Flow) —— 【已完成】
- [x] 3.1 考场初始化与开考页 `pages/exam/index.vue`
- [x] 3.2 单题聚焦视野与左右滑动 (Swiper) 交互
- [x] 3.3 半屏 60% 高度答题卡抽屉与题号快速定位
- [x] 3.4 离开屏幕检测防作弊与倒计时联动

**阶段 3 交付物清单（`toc-new/`）**：
- 组件层：`src/components/QuestionCard.vue` + `.md`（选项三形态归一化、5 种题型渲染——单选卡片 / 多选卡片 / 判断双胶囊 / 填空按题干空位自适应多输入框 / 简答文本域；受控无状态，只回传答案）；`src/components/AnswerSheet.vue` + `.md`（`wd-popup` 底部 60vh 抽屉，三态图例 + 圆角题号网格，点击即收起并定位）。
- 编排层：`src/pages/exam/index.vue` 由阶段二占位页完全重写——入考拉题与续答回填、单题聚焦 swiper、答题卡跳题、服务端权威倒计时、切屏防作弊、二次确认交卷、归零自动交卷、交卷后跳「我的测试」；并补齐加载 / 加载失败 / 已提交不可重入 / 交卷结果四类状态分支。
- 工具层：`src/utils/format.ts` 新增 `parseServerTime()`（兼容后端 6 位微秒 ISO 串，`formatDateTime` 同步复用）。
- **缺陷修复（阶段一 / 二遗留，均为实测暴露）**：
  1. `src/stores/toast.ts` + `GlobalToast.vue` + `GlobalToast.md`：提示负载新增「触发页路由」归属标记。`navigateTo` 后页面栈中多个挂载点共用同一 store，**后台页面会抢先消费提示**，导致考场切屏警告在当前可见页面完全不可见。
  2. `src/pages/exam/index.vue` 事件绑定修正：`@update:model-value="fn(id)"` 会被 Vue 编译器包成 `$event => fn(id)`，该表达式只**返回**新函数却从不调用，**答案永远写不进状态**；改为 `fn(index, $event)` 后作答正常。

**答案取值语义裁决（阶段一遗留待办，本次读表定论）**：
- 单选 / 多选 / 判断一律提交**选项 key**（如 `"B"`、`["A","B","D"]`），**绝不提交选项原文**；
- **判断题必须提交 `'A'` / `'B'`**：后端判分只把 `correct_answer` 侧的中文归一化（正确 / 对 / TRUE / YES → A），**不会转换用户提交值**；
- 填空提交字符串（多空为 `string[]`，空位数由题干下划线推导）；简答提交字符串，后端跳过自动评分进核验池；
- `options` 前端统一归一化为 `{ key, text }`，兼容 `["A. 文本"]`、`[{key,text}]`、`["纯文本"]` 三种真实存在过的形态。

**验收证据（终端与真实浏览器物理输出）**：
1. `pnpm type-check`（`vue-tsc --noEmit`）零报错；`pnpm build:h5` 输出 `DONE Build complete.`；
2. 真实浏览器（Chromium，390×844 移动端视口）考场全链路实测通过：登录 → 首页点击测评卡进入考场 → **成功拉取 5 道真实题目**（单选 / 多选 / 判断 / 填空 / 简答）→ **倒计时真实递减**（`44:58` → `44:54`）→ **手势滑动切题生效**（`1 / 5` → `2 / 5`）→ 「下一题」按钮生效（`2 / 5` → `3 / 5`）→ **答题卡抽屉展开**（可见、概览「已答 1 / 共 5」、5 个题号格）→ **点击题号跳题并自动收起抽屉** → 逐题作答后状态条更新为「已答 3 / 5」→ **切屏触发醒目警告并计数** → 交卷二次确认提示「尚有 2 题未作答」→ 交卷成功 → 自动跳转「我的测试」；重入已提交试卷被正确拦截并引导前往记录页；控制台除模板默认缺失的 `/favicon.ico`（404，非功能性）外无任何报错；
3. **真实落库与自动评分链路验证**：以管理员账号 `13800000011` 对 task 23 / 24 / 25 完成 3 次真实交卷，`GET /api/v1/member/task-records` 可见 3 条新记录；其中对 task 23 按正确答案作答（单选 A、多选 ABC、判断 A）**交卷即时得 50 分**，证明前端提交的选项 key 被后端正确识别并完成自动评分；task 24 / 25 因测试脚本随机作答恰好全部选错得 0 分，其提交体结构与同租户真实人工作答记录（record 91～95）逐字段一致；
4. **未作答题目不会从复盘清单消失**：提交体为全题覆盖（未作答传空串），与「全题覆盖」的设计决策一致。

**⚠️ 阶段 3 已知限制与待办**：
1. **实测消耗了管理员账号的 3 份可考卷**：`13800000011` 对 task 23 / 24 / 25 各产生一条真实作答记录，该账号在 C 端已无可考测评；如需继续用该账号实测，需由管理员新建并发布一份试卷。
2. **浏览器原生后退 / 物理返回键未做拦截**：当前仅拦截页面内 Header 返回键（已实现「退出后本次作答不会保存」二次确认）；H5 浏览器前进后退属阶段 4 可评估的统一收口项。
3. **切屏次数仅提示与计数**，未与强制交卷联动（按需求「给予醒目 Toast 警告」实现，阈值策略待定）。

### 阶段 4：动态报告与个人资产中心 (Phase 4: Dynamic Report & Profile) —— 【已完成】
- [x] 4.1 动态结果报告页 `pages/report/index.vue`（纯客观题环形得分 vs 主观题安全防泄题审核态）
- [x] 4.2 个人中心 `pages/profile/index.vue`（资产卡片、历史统计、重点题目收藏）
- [ ] 4.3 Nginx 配置联调：将移动端根路径 `/` 无缝平滑切换至 `toc-new` 产物（按决策本次不纳入，留待专项部署阶段）

**阶段 4 交付物清单（`toc-new/`）**：
- **双态成绩报告页 `src/pages/report/index.vue`（[NEW]）**：双态判定**全工程唯一判定点**，只认后端算好的 `pending` 字段（不自推断是否含简答题）。
  - **态 A（`pending=false`，即时出分态）**：极客蓝渐变卡承载 `wd-circle` 环形得分（环内超大字重得分 + 满分小字），下方「及格 / 未及格」胶囊与答题用时；逐题复盘卡片复用 `QuestionCard` 只读态（复用其选项三形态归一化与题型别名兼容，映射 `{ id: resource_id, type, title: content, content, options, score: eq_score }`），下方「我的答案 / 正确答案」双行对照（自动评分类题目按归一化比对着色为绿 / 红，简答等主观题不判定避免误导）。
  - **态 B（`pending=true`，安全审核态）**：手绘 SVG「文档 + 时钟」审核插画 + 大字提示与防泄题说明；逐题区域仅保留题面与「我的答案」，**「正确答案」与「解析」区块用 `v-if` 根本不渲染**（非 CSS 隐藏），并显式落出锁定提示块。
- **我的收藏子页面 `src/pages/favorites/index.vue`（[NEW]）**：卡片流展示收藏题目（题型标签 + 题干 + 选项摘要），右上角矢量星标一键取消收藏（二次确认，处理中置灰防连点），加载 / 空态 / 错误三态齐全。
- **契约层修正**：
  1. `src/utils/request.ts` 业务成功码由固定 200 放宽为 2xx 区间——后端 `POST /member/favorites` 返回 `code: 201`，若只认 200「添加收藏」会被误判为业务失败；
  2. `src/api/exam.ts` 的 `ExamRecordItem.correct_answer` 由 `string[] | null` 放宽为 `string | string[] | null`（实库 `fill_in` 为字符串 `"2"`、`multiple_choice` 为数组），并新增 `fetchFavorites` / `addFavorite` / `removeFavorite` 与 `FavoriteItem` 类型。
- **链路打通**：考场页交卷成功后改为 `uni.redirectTo` 报告页并携带 `record_id`（**改用 redirectTo 而非 navigateTo**——后者会把已交卷的考场页留在栈中，返回时退回考场）；「我的测试」记录卡片点击 `navigateTo` 报告页复盘；个人中心「我的收藏」由占位提示改为真实跳转。
- **文档校准（已授权）**：`api-contract.md` 仅剩的两处 `/api/v1/saas/*` 错误前缀（1.1 节 B 端前缀、3.3 节交卷端点）已修正为真实路径，并补记「`saas` 仅为后端 Python 模块目录名，非 URL 前缀，全部路由以 `backend/app/main.py` 注册为准」。

**验收证据（终端与真实浏览器物理输出）**：
1. `pnpm type-check`（`vue-tsc --noEmit`）零报错；`pnpm build:h5` 输出 `DONE Build complete.`；
2. 以 `13900000001 / 123456` 登录（同时具备出分态与审核态记录，零新增数据消耗）：
   - **态 A（record 101，verified，100 分）**：环形得分 100、满分 100 分、及格胶囊、答题用时 22 分钟、逐题复盘共 5 题、**答案对照块 5 个**、含「正确答案 / 我的答案 / 逐题复盘 / 及格 / 满分」且未误入态 B；
   - **态 B（record 91，pending_verification）**：**答案对照块数量 = 0（若 >0 即泄题）**、锁定提示块 5 个、含「正在等待人工 / AI 批阅核验后公布成绩」与「核验完成后公布正确答案与解析」、未出现环形得分；
   - **收藏闭环**：报告页点击复盘卡星标 → 轻提示「已加入我的收藏」、星标变「已收藏」→ 个人中心「我的收藏」显示 **1 题**（真实统计已刷新）→ 收藏页正确展示题目与选项 → 取消收藏二次确认 → 卡片数归 0 并回落空态；**净数据变更为零**；
   - 控制台除模板默认缺失的 `/favicon.ico`（404，非功能性）外无任何报错。

**⚠️ 阶段 4 已知限制与待办**：
1. **4.3 Nginx 联调未实施**：按决策本次未改根目录 `nginx.conf`，移动端根路径 `/` 仍由现有配置接管；上线前需专项处理。
2. **后端 `my_result` 防泄题物理脱敏（✅ 已闭环解决）**：已在 `backend/app/api/saas/member.py` 中完成加固。当记录处于 `pending_verification` 态时，服务端强制将 `correct_answer` 置为 `None`，`explanation` 置为空串。经实测验证 `Leaked items count: 0`，达成「前端 v-if 彻底不渲染 DOM + 后端网络层物理脱敏」的双重铁壁防护！
3. **报告页「解析」区块依赖后端数据**：实库中存量题目 `explanation` 均为空串，故本次实测未覆盖解析展示；录入解析后该区块会自动展示，无需改代码。
4. **收藏操作无批量入口**：当前为逐条取消，若收藏量大可考虑后续增加批量管理。
5. **浏览器原生后退未做统一拦截**：H5 前进后退仍属后续可评估项。

---

## 三、接手检查清单 (Handover Checklist)

后续任何 Agent 接手开发时，按以下步骤入场：
1. **核对代码与 Tag**：确认当前在 `dev` 分支，最新 tag 为 `v1.4-final`。
2. **确认服务健康**：
   - 后端容器：`docker ps` 确保 `tiku_backend` 为 `healthy`。
   - B端管理后台：`http://localhost/admin` 正常运行。
3. **开发展开点**：**阶段 1～4 已全部收口**，v1.5 C 端「登录 → 测评 → 作答 → 交卷 → 成绩复盘 → 题目收藏」主干业务闭环全部贯通。
   - **UI 选型双风格静态预览体系已就绪**（依据根目录 `improveUI.md`）：`preview-linear/`（A 风格 Linear 极客冷灰，拨盘 5/4/5）与 `preview-apple/`（B 风格 Apple 钛金微光，拨盘 8/7/3）各含首页 / 我的测试 / 在线考场 / 成绩报告 / 个人中心 / 我的收藏 / 登录页 7 页，另有 `preview-nav/index` 索引台与全局 `PreviewFloat` 悬浮球（组件文档见 `src/components/PreviewFloat.md`）；全部为内置静态 Mock 数据，不接入真实接口、不触碰 `pages/` 正式业务代码；选型完成后可整体删除 `preview-linear/`、`preview-apple/`、`preview-nav/` 三目录与 `PreviewFloat` 组件；
   - 后续按需展开：
   - C 端工程位于 `toc-new/`，启动命令 `cd toc-new && pnpm dev:h5`（端口 5174）；
   - 新增页面时务必在页面模板内挂载 `<GlobalToast />`，否则轻提示会降级为原生 toast；
   - 数据页面统一复用 `CustomHeader` + `PageState` + `<GlobalToast />` 结构，三态（加载 / 空 / 错误）必须齐全；
   - 所有 C 端接口调用一律以 `/api/v1/member/*` 为准（真实后端路由），不要使用 `api-contract.md` 里的 `/api/v1/saas/*`；
   - **准入考接口 `/member/tasks/{id}/entry` 有不可逆副作用**（服务端会真实落库 pending 记录并锁定开考时刻），除考场页开考流程外严禁在任何预览、预检场景调用；
   - 登录态跳转规则：目标为 tabBar 页（首页 / 我的测试 / 个人中心）用 `uni.switchTab`，目标为非 tab 页（登录页 / 考场页 / 报告页 / 收藏页）用 `uni.reLaunch`、`uni.navigateTo` 或 `uni.redirectTo`；**交卷后跳报告页必须用 `redirectTo` 出栈替换考场页**；
   - **交卷答案必须提交选项 key**：单选 / 判断传 `"A"` 形式字符串，多选传 `["A","B","D"]` 数组，**判断题只能传 `'A'`/`'B'`**，且 `answers` 必须是对象数组（严禁字典），并为每道题生成一项（未作答传空串）；
   - **实测账号已耗尽**：管理员 `13800000011` 对 task 23 / 24 / 25 已各产生一条真实作答记录，后续若需真机交卷验证，请先用管理员新建并发布一份试卷；
   - **待核验试卷的防泄题由前端 `v-if` 兜底**：后端 `my_result` 在 `pending_verification` 时仍返回 `correct_answer` / `explanation`，改动报告页复盘区渲染逻辑时**必须保持答案对照块挂在该态外**；根治方案建议由后端在该态下不返回这两个字段（见阶段 4 已知限制）；
   - **待办：4.3 Nginx 联调未实施**，上线前需把移动端根路径 `/` 无缝切换至 `toc-new` 的 H5 产物。

---
*时间戳签名：2026-09-12 22:55:50 (Deepseek-V4.1-Flash Engineering Closure)*

# 智题库 (TiKu) 动态事实与研发进度总览 (Progress)

> **当前全局版本**：v1.5 (C端跨端极客重构)  
> **最新状态冻结时间**：2026-09-12 16:50:00  
> **执行标准**：严格执行 `agent.md`「最高行为准则」与「跨版本大更迭最高协议」

---

## 一、版本里程碑与状态总线

```
[v1.3 单体题库] ──> [v1.4 多租户SaaS与AI闭环] ──> [v1.5 C端极客移动端重塑 (当前)]
                          │
                          ▼
             【已打 Tag: v1.4-final】
             【旧核心文档已物理归档至 history/】
             【数据库策略：增量迁移 (Migration)】
```

- ✅ **v1.4 结项成果归档**：
  - B 端管理后台（PC 端）全面稳态，多租户权限校验（`require_admin`）全面加固；
  - AI 智能助手交互卡片全面汉化、参数卡片重构，消息与卡片状态完整落库持久化（`action_card_data`）；
  - 自动化截屏与 v1.4 展示文档系统上线（`docs/v1.4_showcase.md`，双击批处理一键刷新）；
  - 代码库已打标：`git tag -a v1.4-final -m "End of version 1.4"` 并推送到云端。

- 🚀 **v1.5 阶段目标**：
  - 核心攻坚阵地：`toc-new/`（基于 `uni-app` + Vue 3.5 + TypeScript + Vite + Wot Design Uni）
  - 视觉核心：**极客蓝 (Geek Blue) 沉浸式风格**，自定义通顶 Header，全站纯正 SVG 图标，绝对消除“任务”刻板词汇，回归“测评/考试”。

---

## 二、v1.5 实施路线与四阶段节奏

### 阶段 1：工程基建与网络底座 (Phase 1: Infrastructure)
- [ ] 1.1 初始化 `toc-new` 脚手架（基于 `dcloudio/uni-preset-vue#vite-ts` 模板）
- [ ] 1.2 安装核心依赖：`wot-design-uni`、`pinia`、`pinia-plugin-persistedstate`、`sass`
- [ ] 1.3 搭建网络层：`utils/request.ts`（统一拦截器、自动注入 `Authorization` 与 `X-Tenant-Id`）
- [ ] 1.4 引入 SVG 图标组件库与极客蓝主题变量配置

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
3. **开发展开点**：从【阶段 1：工程基建与网络底座】开始在根目录下创建并初始化 `toc-new` 移动端工程。

---
*时间戳签名：2026-09-12 16:50:00 (Antigravity Engineering Closure)*

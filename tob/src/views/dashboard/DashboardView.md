# DashboardView SaaS 首页仪表盘

## 💡 核心思想

v1.3 按 `首页设计图.png` 1:1 还原：浅蓝 Banner（Agnes 生图插画）+ 4 KPI 卡（迷你折线）+ 成绩趋势双线面积图 + 试卷分类环形图 + 最近动态/AI 额度/热门排行/系统公告四小卡。

数据流：组件挂载后并行发起两个请求——

1. `GET /api/v1/admin/dashboard/stats` → 灌入 `stats`，由各 `computed` 拆解给 KPI、折线、环形、排行、公告、额度使用；
2. `GET /api/v1/admin/categories?target_type=task` → 灌入 `categoryOptions`，仅用于环形卡右上角「类型」下拉的选项。

**关键设计（防坑点）**：

- **下拉选项来自分类接口，不是 donut 聚合结果**：`donut` 只包含「当前已有试卷的分类」，而分类管理里可能定义了暂无量数据的分类。下拉必须展示**全量试卷分类**，否则会出现「只有全部类型」的假空现象。
- **下拉是数据驱动的**：`target_type=task` 对应「试卷分类」，新增/删减分类时前端无需改动。
- **下拉与环形图联动**：`donutFilter` 为 `all` 时展示全部分类占比；选中某个分类时 `donutData` 只保留该分类（按分类名匹配），环形图变为单色 100%，图例也只显示一行；若该分类暂无试卷则环形图为空。中央「总计」始终是**全部试卷总和**。
- **图表实例集中管理**：所有 ECharts 实例塞进 `charts` 数组，`onUnmounted` 统一 `dispose()`，避免内存泄漏；`donutChart` 单独持有引用，供下拉切换时用 `setOption(option, true)`（notMerge）重绘。

## 数据口径

- `GET /api/v1/admin/dashboard/stats`（管理员鉴权，出题人自动作用域隔离）：
  - `donut`：`Array<{ name: string; value: number }>`，按资源分类聚合的试卷数量；无数据时后端兜底 `[{ name: '暂无试卷', value: 0 }]`。
  - 其余字段：`kpi / deltas / sparks / trend / hot / recent / notices / quota`。
- `GET /api/v1/admin/categories?target_type=task`（成员即可读）：`data.items` 为该租户全部试卷分类，本页仅取 `name` 作为下拉项。

## 素材

- `public/images/dashboard-banner.png`（Agnes 2.5 Flash 生图，21:9）
- `public/images/ai-edu.png`（侧边栏"AI 赋能教育"小插画）
- `public/images/admin-avatar.png`（备用管理员头像）

## 💻 使用示例

```vue
<!-- router/index.ts -->
{ path: 'dashboard', name: 'Dashboard', component: () => import('../views/dashboard/DashboardView.vue') }
```

组件无需接收任何 props，挂载即自动拉取统计与分类接口并渲染看板。

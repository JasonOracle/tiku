# DashboardView SaaS 首页仪表盘

## 设计初衷

v1.3 按 `首页设计图.png` 1:1 还原：浅蓝 Banner（Agnes 生图插画）+ 4 KPI 卡（迷你折线）+ 成绩趋势双线面积图 + 试卷类型环形图 + 最近动态/AI 额度/热门排行/系统公告四小卡。

## 数据口径

当前为**静态假数据**展示（与设计图数字一致），图表基于 ECharts。后续接真实统计接口时，替换 `<script>` 中的假数据常量即可，图表配置无需改动。

## 素材

- `public/images/dashboard-banner.png`（Agnes 2.5 Flash 生图，21:9）
- `public/images/ai-edu.png`（侧边栏"AI 赋能教育"小插画）
- `public/images/admin-avatar.png`（备用管理员头像）

## 调用示例

```vue
<!-- router/index.ts -->
{ path: 'dashboard', name: 'Dashboard', component: () => import('../views/dashboard/DashboardView.vue') }
```

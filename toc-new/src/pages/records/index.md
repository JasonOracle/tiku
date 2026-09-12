# 我的测试页 (Records)

## 💡 核心思想

本页面作为考生答题足迹的核心归档与复盘枢纽，**100% 像素级对齐风格 B（Apple 钛金微光风）预览标准**：

1. **毛玻璃吸顶分段切换器 (`rc-seg`)**：
   - 采用原生 Apple 平滑滑块（`rc-seg__thumb`），根据选中项进行 `translateX(0 / 100% / 200%)` 物理平滑移动。
   - 严格覆盖三大业务维度：`进行中`、`未开始`、`已参加`。
2. **Apple 钛金质感考务卡片 (`rc-card`)**：
   - **进行中**：展示作答进度条（Apple 蓝渐变进度条 `rc-progress__fill`）与动态呼吸闪烁绿点（`dot-live`），右侧提供 Apple 渐变胶囊按钮“继续答题”。
   - **未开始**：灰质感预约题卡（`rc-card--muted`），配备拟物灰色安全小锁（`rc-lock`）与“未到开考时间”禁用态按钮。
   - **已参加**：展示大号得分（64rpx 特大粗体 `rc-score__num`），自动按成绩分档展示绿色高光（`rc-score--ok`）、橙色审核中（`rc-score--warn`）以及红色待努力（`rc-score--danger`），右侧为毛玻璃幽灵按钮“查看报告”。
3. **真实后端数据闭环**：
   - 真实对接 `GET /api/v1/member/member-tasks`，依据服务端的 `status` 与 `start_time` 智能归类入库，点击直接导航至 `/pages/report/index?record_id=...`。

---

## 💻 使用示例

```vue
<!-- 作为 uni-app 主 tabBar 第二项使用 -->
<template>
  <RecordsPage />
</template>
```

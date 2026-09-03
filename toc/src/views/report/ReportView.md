# ReportView 考试分析报告组件文档

## 💡 核心思想
展示考试或练习完成后的可视化数据报告。包含 SVG 环形得分进度圈、合格判定、答对/答错题目数量卡片，以及每道题目的标准答案与用户作答对比解析。

## 💻 使用示例
```vue
<template>
  <ReportView />
</template>

<script setup lang="ts">
import ReportView from './views/report/ReportView.vue';
</script>
```

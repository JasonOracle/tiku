# HistoryView 历史答题记录视图组件文档

## 💡 核心思想
展示 C 端用户所有的历史考试作答记录。列表项清晰展示：试卷名称、得分、及格与否 Badge、答题用时与提交时间。点击任一历史记录卡片直接跳转至当次答题分析报告 `/report?record_id=xxx`！

## 💻 使用示例
```vue
<template>
  <HistoryView />
</template>

<script setup lang="ts">
import HistoryView from './HistoryView.vue';
</script>
```

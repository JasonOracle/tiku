# QuestionsView 题海管理视图组件文档

## 💡 核心思想
实现 B 端全站题海库的统一 CRUD 管理。支持按分类、题型、难度和关键字筛选，具备中文难度映射（简单/中等/困难），以及设置题目默认分值（Score）。提供标准的 Excel 模板批量导入功能。

## 💻 使用示例
```vue
<template>
  <QuestionsView />
</template>

<script setup lang="ts">
import QuestionsView from './QuestionsView.vue';
</script>
```

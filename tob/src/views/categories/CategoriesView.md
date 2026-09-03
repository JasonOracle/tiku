# CategoriesView 双分类管理视图组件文档

## 💡 核心思想
实现 B 端分类管理的双重隔离。
1. **题目分类 Tab**：维护题目归属学科/领域（如金融类、消防安全、编程基础）。
2. **试卷分类 Tab**：维护试卷考试场景（如模拟、真题、练习、趣闻问答、测试）。

## 💻 使用示例
```vue
<template>
  <CategoriesView />
</template>

<script setup lang="ts">
import CategoriesView from './CategoriesView.vue';
</script>
```

# ProfileView 个人中心视图组件文档

## 💡 核心思想
C 端移动端个人中心组件。包含标准 Aero 渐变 SVG 默认头像、作答统计仪表盘（累计作答场次、综合通过率）以及双导航 Cell 选项：
1. **我的题目收藏夹** Cell ➔ 显示题数，跳转 `/favorite`。
2. **历史答题记录** Cell ➔ 显示试卷份数，跳转 `/history`。

## 💻 使用示例
```vue
<template>
  <ProfileView />
</template>

<script setup lang="ts">
import ProfileView from './ProfileView.vue';
</script>
```

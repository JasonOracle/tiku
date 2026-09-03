# UsersView 用户与全站答题明细组件文档

## 💡 核心思想
包含两页标签面板 (Tabs)：
1. 注册用户列表：查看 C 端用户列表及账号状态。
2. 全站答题记录明细：实时掌握全站学生的作答成绩、得分率与作答用时。

## 💻 使用示例
```vue
<template>
  <UsersView />
</template>

<script setup lang="ts">
import UsersView from './views/users/UsersView.vue';
</script>
```

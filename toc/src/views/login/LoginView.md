# LoginView C端移动端登录与注册组件文档

## 💡 核心思想
移动端轻量级登录/注册二合一折叠表单。支持快速切换注册模式与登录模式，成功后自动将 JWT 写入 `tiku_toc_token`。

## 💻 使用示例
```vue
<template>
  <LoginView />
</template>

<script setup lang="ts">
import LoginView from './views/login/LoginView.vue';
</script>
```

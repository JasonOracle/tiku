# LoginView 登录页面组件文档

## 💡 核心思想
提供 B 端 SaaS 管理后台的管理员登录与首次初始化入口。采用了选定的 **Aero Glass 浅蓝毛玻璃拟态视觉样式** (`#0284C7` 天空蓝与 `#38BDF8` 渐变背景)，利用纯 CSS `backdrop-filter: blur(16px)` 实现高质感卡片折射效果。避免 Emoji，使用 Element Plus 的原生 Icon。

## 💻 使用示例
```vue
<template>
  <LoginView />
</template>

<script setup lang="ts">
import LoginView from './views/login/LoginView.vue';
</script>
```

# TabBar 公共浮动导航栏

## 💡 核心思想
C 端首页与个人中心通用的底部悬浮导航栏。
- **视觉设计**：参考 `zbzn` 高级玻璃晶体规范，采用 65% 透明度渐变背景（`linear-gradient(180deg, rgba(245,245,245,0.65) ...)`）、模糊滤镜 `backdrop-filter: blur(8px)`、内高光阴影 `inset 1px 1px 0 rgba(255,255,255,0.9)` 以及胶囊大圆角 (`border-radius: 60px`)。
- **选中动效**：激活项呈现淡暗底色 (`background: rgba(26,26,26,0.06)`) 与高亮图标投影。

## 💻 使用示例
```vue
<template>
  <div class="page">
    <!-- 页面正文内容 -->
    <TabBar active="home" />
  </div>
</template>

<script setup lang="ts">
import TabBar from '@/components/TabBar.vue';
</script>
```

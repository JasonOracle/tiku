# NavBar 统一导航栏组件

## 💡 核心思想

全局统一的移动端顶部导航栏，解决之前各页面返回按钮样式不一致、跳转目标混乱的问题，并支持沉浸式透明渐变效果。

- **左侧**：标准化返回箭头 SVG 图标（22×22，stroke-width 2.4），点击执行 `router.back()`，无历史时回退首页 `/`。
- **中间**：标题文字居中（视觉居中，用 `margin-right: -36px` 补偿左侧按钮宽度）。
- **右侧**：`<slot name="right" />` 预留插槽，供答题页收藏按钮等扩展使用。
- **沉浸模式**：传入 `immersive` 属性后，未滚动时背景保持全透明；当页面向下滚动超过 `scrollThreshold`（默认 30px）时，平滑过渡为毛玻璃白底。

### 防坑要点
- 使用 `router.back()` 而非 `router.push('/')`，确保返回到来源页而非首页。
- `window.history.length > 1` 兜底：首次直接打开子页面时回退到首页。
- 监听 `window` 的 `scroll` 事件时配置了 `{ passive: true }`，避免卡顿。组件销毁时强制注销监听器。

## 💻 使用示例

### 1. 普通固顶导航栏

```vue
<template>
  <NavBar title="我的收藏夹" />
  <!-- 页面内容 -->
</template>

<script setup lang="ts">
import NavBar from '@/components/NavBar.vue';
</script>
```

### 2. 沉浸式透明滚动渐变导航栏

```vue
<template>
  <div class="page-container">
    <!-- 未滚动时透明，向下滚动 30px 后自动变为白色毛玻璃背景 -->
    <NavBar title="答题报告" immersive />
    
    <div class="content">
      <!-- 页面长内容 -->
    </div>
  </div>
</template>
```

### 3. 带右侧插槽

```vue
<NavBar title="在线测评">
  <template #right>
    <button @click="toggleFav">⭐</button>
  </template>
</NavBar>
```


# AppModal 通用弹窗组件文档

## 💡 核心思想
替代浏览器原生 `alert` 与 `window.confirm`，提供与移动端 SPA 风格高度一致的高颜值的毛玻璃通用弹窗。
1. **视觉规范**：采用暗色毛玻璃渐变蒙层 + 白底/微卡片悬浮框，带有平滑淡入缩放动画 (`modal-pop`)。
2. **多模式支持**：
   - `confirm` 模式：显示取消与确认双按钮，支持自定义按钮文本与样式。
   - `alert` 模式：仅显示单确认按钮。
3. **安全闭环**：结合 Vue 3 响应式 Promise 包装或事件触发，确保用户确认/取消状态精准回调。

## 💻 使用示例
```vue
<template>
  <AppModal
    v-model="showModal"
    title="提示"
    content="确定要退出当前答题吗？"
    type="confirm"
    confirm-text="确定"
    cancel-text="取消"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AppModal from '@/components/AppModal.vue';

const showModal = ref(false);

const handleConfirm = () => {
  console.log('用户点击了确定');
};

const handleCancel = () => {
  console.log('用户点击了取消');
};
</script>
```

# MessageBubble 消息气泡组件文档

## 💡 核心思想
该组件专为 AI 对话系统设计，遵循 Ant Design X 的 Bubble 交互规范：
1. **多态渲染流**：支持 `user`（用户发言，右侧偏置）与 `assistant`（AI助管发言，左侧带精致徽标与渐变头像）两种形态；
2. **打字机光标与状态解耦**：在 `isStreaming` 期间于内容末尾挂载 CSS 闪烁打字机光标；思考阶段展示原生跳动圆点骨架，收到流式首字后平滑展开为 Markdown 正文；
3. **安全与微交互**：内置 `marked` 鲁棒转义，支持悬浮展示复制全文、有用/无用反馈与私有知识库来源（RAG）点击溯源。

## 💻 使用示例
```vue
<template>
  <MessageBubble
    role="assistant"
    content="你好！我是企业培训 AI 智能助管。"
    username="Admin"
    :is-thinking="false"
    :is-streaming="false"
    @show-source="handleShowSource"
    @feedback="handleFeedback"
  />
</template>

<script setup lang="ts">
import MessageBubble from './components/MessageBubble.vue';

const handleShowSource = (source: any) => {
  console.log('查看溯源', source);
};

const handleFeedback = (rating: 'up' | 'down') => {
  console.log('评价', rating);
};
</script>
```

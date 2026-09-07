# AiAssistantView 独立的类 DeepSeek AI 助理 Tab 组件文档

## 💡 核心思想
独立全屏 Tab 页 AI 工作台组件：
1. **类 DeepSeek / ChatGPT 界面范式**：
   - **左侧会话历史侧边栏**：支持新建对话、会话列表自由切换与删除。
   - **中央消息区与欢迎卡片**：无历史消息时呈现快捷 Prompt 卡片（如一键智能组卷、快速生成题目、上帝视角查询）。
   - **底部控制台**：带智能换行、键盘快捷提交与发送状态控制。
2. **前端状态快照注入 (State Preamble)**：自动隐藏注入当前用户的系统角色、额度与业务上下文。

## 💻 使用示例
```vue
<template>
  <AiAssistantView />
</template>

<script setup lang="ts">
import AiAssistantView from './views/ai/AiAssistantView.vue';
</script>
```

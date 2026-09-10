# SessionSidebar 组件自说明文档

## 💡 核心思想

`SessionSidebar` 承担 AI 智能助理工作台左侧的历史对话检索、快速会话切换、新建会话以及会话生命周期管理（重命名与删除）。

1. **扁平化状态设计与轻量交互**：
   - 会话条目采用沉浸式 hover 高亮微动效（背景色平滑从浅灰到高亮淡蓝），激活会话采用主色语义区分。
   - 更多操作按钮（上下三点 SVG 图标 `MoreFilled`）在鼠标悬浮（hover）或下拉菜单展开时显现，平时隐去，降低视觉噪点。
2. **防误触危险动作保障**：
   - 下拉菜单将“删除”标红（危险操作），并配以分割线。
   - 点击“重命名”唤起原生风格的对话框，支持回车确认与焦点自动聚集。
   - 点击“删除”唤起标准的危险二次确认弹窗（黄色感叹号图标 + 警告文案 + 危险红确认按钮），严格杜绝误删对话记录。
3. **数据流同源与局部更新**：
   - 重命名成功后，通过 `remamed` 事件局部修改内存中 session 对象的 `title`，无需引起全量网络重拉或页面闪烁；删除后通知父组件联动清除或切换至剩余会话。

---

## 💻 使用示例

```vue
<template>
  <SessionSidebar
    :sessions="sessionList"
    :active-id="currentSessionId"
    @new="handleCreateSession"
    @select="handleSelectSession"
    @delete="handleDeleteSession"
    @renamed="handleRenamedSession"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SessionSidebar, { type CloudSession } from './components/SessionSidebar.vue';

const currentSessionId = ref<number | null>(1);
const sessionList = ref<CloudSession[]>([
  { id: 1, title: '多类交通工具与钢铁侠战甲平面展示' },
  { id: 2, title: '新对话' }
]);

const handleCreateSession = () => {
  // 创建新会话逻辑
};

const handleSelectSession = (id: number) => {
  currentSessionId.value = id;
};

const handleDeleteSession = (id: number) => {
  sessionList.value = sessionList.value.filter(s => s.id !== id);
};

const handleRenamedSession = (id: number, newTitle: string) => {
  const target = sessionList.value.find(s => s.id === id);
  if (target) target.title = newTitle;
};
</script>
```

# AiAssistantView AI 智能助管工作台组件文档

## 💡 核心思想
独立全屏 Tab 页 AI 工作台组件：
1. **现代交互范式**：
   - **左侧会话历史侧边栏**：支持新建对话、会话列表自由切换与删除。
   - **中央消息区与欢迎卡片**：无历史消息时呈现快捷 Prompt 卡片（如一键智能组卷、快速生成题目、上帝视角查询）。
   - **底部控制台**：带智能换行、键盘快捷提交与发送状态控制。
2. **前端状态快照注入 (State Preamble)**：自动隐藏注入当前用户的系统角色、额度与待阅试卷业务上下文（出题人仅注入其私有试卷）。
3. **全站脱敏**：界面统一使用「AI 智能助管」/「AI 智算引擎」，不露出底层模型供应商商业名称。
4. **企业级会话持久化与跨端漫游**：会话与消息全量落库（`ai_chat_sessions` / `ai_chat_messages`），
   彻底告别 localStorage；换浏览器、换电脑登录历史无缝同步。
5. **仿微信向上游标分页**：触顶（<60px）按 `before_id` 拉更早 20 条，视口高度数学补偿零跳屏；
   打字流仅底部附近吸底，上滑阅读时视口静止。

## 🃏 Action Card / Action List 协议

- **待确认卡片（三档风险）**：`high` 红卡（删除等高危）、`medium` 蓝色轻确认卡（新建题目等安全新增，
  仍需人工核对入库防幻觉污染）、`low` 自动执行无卡片。确认后调用真实业务接口转绿色 `已执行`。
- **新建题目结构化预览**：`create_question_draft` 不再展示生硬 JSON，而是排版呈现题干、选项明细
  （标出正确答案）、答案与解析。
- **操作路由卡片**：解析 ````action_list```` 数组，渲染任务列表（试卷名 + 待批数量 + `[去批改]`）。
  点击原地唤出 `GradingDrawer` 批阅抽屉。前端 `ACTION_WHITELIST` 白名单拦截越权动作，
  出题人仅允许 `open_grading_drawer`。

## 💻 使用示例
```vue
<template>
  <AiAssistantView />
</template>

<script setup lang="ts">
import AiAssistantView from './views/ai/AiAssistantView.vue';
</script>
```

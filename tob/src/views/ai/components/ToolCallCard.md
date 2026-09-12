# ToolCallCard 组件自说明文档

## 💡 核心思想

ToolCallCard 是 AI 助理工作台核心的交互式业务操作确认卡片。遵循 Karpathy 务实设计原则与极简闭环逻辑：
1. **防误触与风控闭环**：当大模型判定需要调用核心后端业务工具（如智能组卷 `create_exam_draft`、批量出题 `create_question_draft`、物理删除试卷 `delete_exam`、删除题目 `delete_question`）时，系统绝不隐式自动执行破坏性写操作，而是通过本组件向管理员呈现完整的题目预览、选项高亮、分值与 RAG 知识库溯源凭证。
2. **原地表单微调与智能判断**：管理员在确认建卷或批量出题前，可以直接在卡片内选择试卷/题库分类（调用 `/api/v1/admin/categories` 时分别支持 `task` 与 `resource` 目标类型）、配置考试时间窗口、考试时长限制。对于批量出题（`create_question_draft`），组件区分出题参数指令卡（出题材料、题型集合、出题数量、难度等级）与已生成题干草稿列表展示，确保出题信息如实对应，避免数据错配。**AI 阅卷模式选项具备动态识别能力**：仅当题目中包含主观简答题（`short` / `essay` / `subjective` / `qa`）时才渲染该配置项，且默认值强制绑定为 `ai_auto`（AI 自动托管）；纯客观题试卷则无需呈现多余选项。点击确认后，表单参数将与大模型生成的原创题目列表无缝合并，统一打入后端 `/api/v1/admin/ai/chat/execute_tool` 接口完成原子化入库。

## 💻 使用示例

```vue
<template>
  <ToolCallCard
    :message="toolMessage"
    :categories="examCategories"
    @confirm="handleConfirmTool"
    @cancel="handleCancelTool"
    @show-source="handleOpenTraceDrawer"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ToolCallCard, { type ToolCallMessage } from './components/ToolCallCard.vue';

const toolMessage = ref<ToolCallMessage>({
  role: 'assistant',
  toolName: 'create_exam_draft',
  toolCallId: 'call_1024',
  riskLevel: 'medium',
  arguments: {
    title: '甲午中日战争专题测评',
    difficulty: 'medium',
    questions: [
      {
        type: 'single',
        title: '甲午中日战争爆发于哪一年？',
        options: [
          { key: 'A', text: '1894年' },
          { key: 'B', text: '1895年' },
          { key: 'C', text: '1898年' },
          { key: 'D', text: '1900年' }
        ],
        answer: ['A'],
        score: 10,
        ai_rag_sources: [{ document_name: '中国近代史重点考纲.pdf' }]
      }
    ]
  }
});

const examCategories = ref([{ id: 1, name: '历史学科' }]);

const handleConfirmTool = (msg: ToolCallMessage) => {
  console.log('确认执行并提交后端参数：', msg.arguments);
};

const handleCancelTool = (msg: ToolCallMessage) => {
  console.log('用户取消操作');
};

const handleOpenTraceDrawer = (source: any) => {
  console.log('打开溯源抽屉：', source);
};
</script>
```

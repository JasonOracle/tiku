# QuestionPreview 题目透亮预览组件文档

## 💡 核心思想

本组件作为普通组卷与 AI 组卷审阅共用的「题目选项与正确答案透亮预览」基石组件。
1. **视觉一致性**：客观题（单选/多选）选项默认呈浅灰色胶囊徽章，正确答案自动切换为绿色高亮浅背景（`#f0fdf4`），并在首部强化 `✔ [选项标号]` 标识。
2. **多源数据容错**：由于历史题目与大模型生成的选项结构多样（可能返回 `key`、`label`、`value` 甚至未给标号），组件内部通过 `getOptKey(opt, index)` 进行智能兜底识别，并在标号缺失时自动按序号推导 `A, B, C, D...`，杜绝出现空中括号 `[ ]` 的显示缺陷。
3. **判断题自动裁决**：判断题依据答案与选项文本自动生成「✔ 正确」绿色徽章或「✖ 错误」红色徽章。
4. **填空/简答主观题紧凑化**：填空题自动拼装横向标准答案，简答题折叠展示采分要点（`grading_points`）。

## 💻 使用示例

```vue
<template>
  <QuestionPreview :question="currentQuestion" />
</template>

<script setup lang="ts">
import QuestionPreview from './components/QuestionPreview.vue';

const currentQuestion = {
  type: 'single',
  title: '金融心理学中描述损失厌恶在投资中的表现？',
  options: [
    { key: 'A', text: '投资者更愿意承担更高风险' },
    { key: 'B', text: '投资者对同样金额损失的痛苦明显大于同样金额收益的快乐' }
  ],
  answer: ['B']
};
</script>
```

# ResourcePreview 组件自说明文档

## 💡 核心思想

本组件是试卷编排与 AI 组卷审阅环节的**试题所见即所得核心预览组件**，负责渲染单选、多选、判断、填空、简答等各类试题的：
1. **选项列表**：自动规范化后端或大模型返回的多元格式（对象数组、带字母前缀字符串数组、纯文本数组），单选/多选自动匹配高亮正确答案。
2. **正确答案高亮**：无论数据格式是数组还是单值，自动归一化匹配，正确选项赋予浅绿底色、加粗字样并前置打勾符号。
3. **极简标准答案**：填空与简答题清晰呈现标准答案全文，为人工核验或 AI 判卷提供直接参考，彻底摒弃多余冗杂的「踩分点」与「文字解析」。
4. **防御性安全边界**：严防未声明变量导致的运行时崩溃与白屏。

---

## 💻 使用示例

在试卷审阅或题目列表中嵌入：

```vue
<template>
  <ResourcePreview :resource="questionItem" />
</template>

<script setup lang="ts">
import ResourcePreview from './components/ResourcePreview.vue';

const questionItem = {
  type: 'single',
  title: '计算机网络中，HTTP 协议默认端口是？',
  options: [
    { key: 'A', text: '80' },
    { key: 'B', text: '443' },
    { key: 'C', text: '8080' },
    { key: 'D', text: '22' }
  ],
  answer: ['A'],
  score: 5
};
</script>
```

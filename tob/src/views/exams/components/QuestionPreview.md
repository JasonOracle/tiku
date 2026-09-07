# QuestionPreview 题目透亮预览

## 设计初衷

普通组卷与 AI 组卷审阅共用同一套「选项与正确答案绿色高亮」排版（tech-spec Step 1.5），
避免两处各自实现导致样式漂移。

## 渲染规则

- 单选/多选：普通选项浅灰小标签；正确答案 `background #f0fdf4 + border #86efac + color #166534 + font-weight 600`，前置 `✔ [key]`。
- 判断题：挂 `✔ 正确`（绿）或 `✖ 错误`（红）Badge（按正确选项文本是否含错/误/否/False 判定），选项同样高亮。
- 填空/简答：紧凑展示标准答案 / 参考答案 + 采分点。

## 调用示例

```vue
<script setup lang="ts">
import QuestionPreview from './components/QuestionPreview.vue';
</script>

<template>
  <QuestionPreview :question="row" />
</template>
```

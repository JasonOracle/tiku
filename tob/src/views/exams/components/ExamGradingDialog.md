# ExamGradingDialog 试卷行级阅卷大厅全屏弹窗

## 设计初衷

v1.7 试卷管理行内直达批阅：点击某试卷的「阅卷大厅」按钮，全屏弹窗列出该卷全部待批阅答卷，
逐份批阅定分/一键采信/重试 AI，无需跳转独立大厅页面。批阅抽屉（`GradingDrawer`）保留给 AI 助管卡片联动调用。

## 调用示例

```vue
<script setup lang="ts">
import ExamGradingDialog from './components/ExamGradingDialog.vue';

const gradingDlgVisible = ref(false);
const gradingExam = ref<any>(null);
</script>

<template>
  <el-button @click="gradingExam = row; gradingDlgVisible = true">阅卷大厅</el-button>
  <ExamGradingDialog
    :visible="gradingDlgVisible"
    :exam-id="gradingExam?.id ?? null"
    :exam-title="gradingExam?.title ?? ''"
    @update:visible="gradingDlgVisible = $event"
    @graded="loadExams"
  />
</template>
```

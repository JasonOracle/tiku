# GradingDrawer 主观题批阅抽屉

## 设计初衷

v1.1 的独立「阅卷大厅」一级菜单 too heavy：老师批卷需要在列表页与大厅页之间来回跳转。
v1.2 贯彻轻量化设计：废除大菜单依赖，试卷管理行内 `[N 份待批阅]` 橙色微章点击后**原地滑出**本抽屉，
零跳转完成「看作答 → 对答案 → 参考 AI 初评 → 打分 → 发布 → 下一份」的闭环。

## 调用示例

```vue
<script setup lang="ts">
import GradingDrawer from './components/GradingDrawer.vue';

const gradingVisible = ref(false);
const gradingExam = ref<any>(null);

const handleOpenGrading = (row: any) => {
  gradingExam.value = row;
  gradingVisible.value = true;
};
</script>

<template>
  <!-- 试卷标题列行内待办微章 -->
  <el-tag
    v-if="row.pending_count > 0"
    type="warning"
    effect="dark"
    class="cursor-pointer"
    @click="handleOpenGrading(row)"
  >
    {{ row.pending_count }} 份待批阅
  </el-tag>

  <!-- 行内批阅抽屉 -->
  <GradingDrawer
    :visible="gradingVisible"
    :exam-id="gradingExam?.id ?? null"
    :exam-title="gradingExam?.title ?? ''"
    @update:visible="gradingVisible = $event"
    @graded="loadExams"
  />
</template>
```

## 行为契约

- 打开时按 `GET /api/v1/admin/grading/records?exam_id=X` 拉取该卷全部待批阅答卷，顶部展示 `第 1 / N 份` 进度。
- 每份答卷展示：考生简答题原文作答、题目标准答案、采分点；有 `ai_grading_result` 时展示浅蓝
  `AI 初评建议分` 框；打分输入框（Slider + 数字输入）预填 AI 建议分，可手动微调。
- 底部主按钮 `[✔ 确认发布成绩]` 调 `POST /records/{id}/confirm`（手动分），发布后自动切下一份；
  徽章数量由父页面 `graded` 事件触发 `loadExams()` 刷新，减至 0 后抽屉自动关闭。
- `POST /records/{id}/retry-ai` 兜底 AI 异常；`一键采信 AI` 调 `accept_ai=true`。
- 权限：非本人试卷后端返回 `403`，抽屉内由全局拦截器提示。

# TraceDrawer RAG 高亮溯源抽屉

## 设计初衷

v1.3 任务 3：基于私有资料生成的题目自带 `[引用溯源]` 标签，点击在右侧唤出抽屉，
展示原文档切片出处，并按答案命中词精准高亮（`<mark>` 黄底）。

## 数据来源

题目 `source_ref: [{doc_id, chunk_id}]`（AI 出题 `doc_ids` 入库时写入），
经 `GET /api/v1/admin/rag/chunks?ids=` 批量取块，越权块由后端过滤。

## 调用示例

```vue
<script setup lang="ts">
import TraceDrawer from './components/TraceDrawer.vue';

const traceVisible = ref(false);
const traceQuestion = ref<any>(null);
</script>

<template>
  <el-button v-if="(row.source_ref || []).length" type="success" text size="small"
             @click="traceQuestion = row; traceVisible = true">
    引用溯源
  </el-button>
  <TraceDrawer :visible="traceVisible" :question="traceQuestion" @update:visible="traceVisible = $event" />
</template>
```

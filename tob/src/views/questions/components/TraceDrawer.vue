<!--
  * [变更日志]
  * 修改时间：2026-09-08
  * AI模型：Muse Spark
  * 修改内容：[v1.3 任务3: RAG 高亮溯源抽屉 (按 source_ref 取块 + 答案命中高亮)]
  -->
<template>
  <el-drawer
    :model-value="visible"
    title="引用溯源"
    size="520px"
    destroy-on-close
    @close="handleClose"
  >
    <div v-loading="loading">
      <div v-if="question" class="trace-q">题目：{{ question.title }}</div>
      <div v-for="c in chunks" :key="c.id" class="trace-card">
        <div class="trace-head">
          <el-tag size="small" type="info">{{ c.filename || `文档#${c.doc_id}` }}</el-tag>
          <span class="trace-idx">切片 #{{ c.chunk_index }}</span>
        </div>
        <div class="trace-text" v-html="highlight(c.text)"></div>
      </div>
      <el-empty v-if="!loading && !chunks.length" description="暂无溯源出处" />
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import request from '../../../utils/request';

const props = defineProps<{
  visible: boolean;
  question: any;
}>();

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void;
}>();

const loading = ref(false);
const chunks = ref<any[]>([]);

const escapeHtml = (s: string): string =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// 高亮答案命中词 (正确选项文本 / 填空可接受答案 / 简答关键词)
const keywords = (): string[] => {
  const q = props.question || {};
  const out: string[] = [];
  const push = (s: any) => {
    const t = String(s || '').trim();
    if (t.length >= 2) out.push(t);
  };
  if (q.type === 'short') {
    (q.grading_points || []).forEach(push);
    const ans = Array.isArray(q.answer) ? q.answer[0] : q.answer;
    String(ans || '').split(/[，。；、]/).forEach(push);
  } else if (q.type === 'fill') {
    (q.answer || []).forEach((b: any) => (Array.isArray(b) ? b : [b]).forEach(push));
  } else {
    const ansSet = new Set((q.answer || []).map((x: any) => String(x)));
    (q.options || []).forEach((o: any) => {
      if (ansSet.has(String(o.key))) push(o.text);
    });
  }
  return [...new Set(out)].sort((a, b) => b.length - a.length).slice(0, 8);
};

const highlight = (text: string): string => {
  let html = escapeHtml(text || '');
  for (const kw of keywords()) {
    const esc = kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    html = html.replace(new RegExp(esc, 'g'), (m) => `<mark>${m}</mark>`);
  }
  return html;
};

const loadChunks = async (): Promise<void> => {
  const refs = props.question?.source_ref || [];
  if (!refs.length) {
    chunks.value = [];
    return;
  }
  loading.value = true;
  try {
    // source_ref 可能是 [{doc_id, chunk_id}] 或增量数字 ID 数组，统一取 chunk_id
    const ids = refs.map((r: any) => (typeof r === 'object' ? r.chunk_id ?? r.id : r)).filter((v: any) => v != null);
    if (!ids.length) {
      chunks.value = [];
      return;
    }
    const res: any = await request.get('/api/v1/admin/rag/chunks', { params: { ids: ids.join(',') } });
    chunks.value = res.items || [];
  } finally {
    loading.value = false;
  }
};

const handleClose = (): void => {
  emit('update:visible', false);
};

watch(() => props.visible, (v: boolean) => {
  if (v) loadChunks();
});
</script>

<style scoped>
.trace-q {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12px;
  line-height: 1.6;
}

.trace-card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 12px;
  background: #f8fafc;
}

.trace-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.trace-idx {
  font-size: 12px;
  color: #94a3b8;
}

.trace-text {
  font-size: 13px;
  color: #334155;
  line-height: 1.8;
  white-space: pre-wrap;
}

.trace-text :deep(mark) {
  background: #fef08a;
  color: #854d0e;
  border-radius: 3px;
  padding: 0 2px;
}
</style>

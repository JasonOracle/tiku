<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗重写：直接渲染条目 ai_rag_sources 溯源，旧 source_ref/chunks 接口已删除]
-->
<template>
  <el-drawer
    :model-value="visible"
    title="参考溯源"
    size="520px"
    destroy-on-close
    @close="handleClose"
  >
    <div>
      <div v-if="resource" class="trace-q">条目：{{ resource.title || resource.content }}</div>
      <div v-for="(s, i) in sources" :key="i" class="trace-card">
        <div class="trace-head">
          <el-tag size="small" type="info">{{ s.file_name || `文档#${s.document_id}` }}</el-tag>
          <span class="trace-idx">相似度 {{ s.similarity_score }}</span>
        </div>
        <div class="trace-text" v-html="highlight(s.chunk_content)"></div>
      </div>
      <el-empty v-if="!sources.length" description="暂无溯源引用" />
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  visible: boolean;
  resource: any;
}>();

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void;
}>();

const sources = computed(() => props.resource?.ai_rag_sources || []);

const escapeHtml = (s: string): string =>
  String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const keywords = (): string[] => {
  const q = props.resource || {};
  const out: string[] = [];
  const push = (s: any) => {
    const t = String(s || '').trim();
    if (t.length >= 2) out.push(t);
  };
  const ans = q.answer || q.correct_answer || [];
  if (Array.isArray(ans)) ans.forEach((a: any) => (Array.isArray(a) ? a.forEach(push) : push(a)));
  else push(ans);
  (q.options || []).forEach((o: any) => push(o.text));
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

const handleClose = (): void => {
  emit('update:visible', false);
};
</script>

<style scoped>
.trace-q {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12px;
}
.trace-card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 10px;
  background: #f8fafc;
}
.trace-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.trace-idx {
  font-size: 12px;
  color: #0284c7;
  font-weight: 600;
}
.trace-text {
  font-size: 13px;
  color: #334155;
  line-height: 1.7;
  white-space: pre-wrap;
}
</style>

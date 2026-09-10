<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[新建消息气泡组件 - Markdown 渲染 + 复制/反馈按钮]
-->
<template>
  <div class="message-bubble" :class="role">
    <div v-if="role === 'user'" class="user-avatar">
      {{ username.substring(0, 1).toUpperCase() }}
    </div>
    <div v-else class="ai-avatar">
      <el-icon><MagicStick /></el-icon>
    </div>
    <div class="content-cell">
      <div class="sender-name">{{ role === 'user' ? username : 'AI 智能助管' }}</div>
      <div v-if="quote" class="quote-bar">| 回复 全Ai系统: {{ quote }}</div>
      <div
        v-if="content && content.trim()"
        class="bubble-content markdown-body"
        v-html="renderedContent"
      />
      <div v-if="role === 'assistant' && !isThinking" class="message-actions">
        <el-tooltip content="复制内容" placement="top">
          <span class="action-icon" @click="copyContent">
            <el-icon><DocumentCopy /></el-icon>
          </span>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-tooltip content="有用" placement="top">
          <span class="action-icon" @click="submitFeedback('up')" style="font-size: 14px;">
            <svg viewBox="0 0 24 24" width="1em" height="1em" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
          </span>
        </el-tooltip>
        <el-tooltip content="无用" placement="top">
          <span class="action-icon" @click="submitFeedback('down')" style="font-size: 14px;">
            <svg viewBox="0 0 24 24" width="1em" height="1em" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path></svg>
          </span>
        </el-tooltip>
      </div>
      <div v-if="isThinking" class="thinking-spinner">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        <span style="margin-left: 8px; color: #64748b; font-size: 13px;">正在思考中...</span>
      </div>
      <div v-if="ragSources && ragSources.length" class="sources">
        <el-tag
          v-for="(s, i) in ragSources"
          :key="i"
          size="small"
          type="info"
          effect="plain"
          class="src-tag"
          @click="$emit('show-source', s)"
        >
          📚 {{ s.document_name || s.file_name || `文档#${s.document_id}` }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ElMessage } from 'element-plus';
import { MagicStick, DocumentCopy } from '@element-plus/icons-vue';
import { marked } from 'marked';

interface RagSource {
  document_id?: number;
  file_name?: string;
  document_name?: string;
  chunk_content?: string;
  similarity?: number;
  similarity_score?: number;
}

const props = defineProps<{
  role: 'user' | 'assistant';
  content: string;
  username: string;
  quote?: string;
  isThinking?: boolean;
  ragSources?: RagSource[];
}>();

const emit = defineEmits<{
  (e: 'show-source', source: RagSource): void;
  (e: 'feedback', rating: 'up' | 'down'): void;
}>();

const renderedContent = computed(() => {
  if (!props.content) return '';
  return marked.parse(props.content) as string;
});

const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(props.content);
    ElMessage.success('已复制到剪贴板');
  } catch {
    ElMessage.error('复制失败');
  }
};

const submitFeedback = (rating: 'up' | 'down') => {
  emit('feedback', rating);
};
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-bubble.user {
  flex-direction: row-reverse;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #0284c7;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.content-cell {
  flex: 1;
  min-width: 0;
}

.sender-name {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 4px;
}

.bubble-content {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  color: #1e293b;
  font-size: 14px;
  max-width: 85%;
  border: 1px solid #e2e8f0;
}

.message-bubble.user .bubble-content {
  background: #e0f2fe;
  border-color: #bae6fd;
  color: #0369a1;
}

.quote-bar {
  font-size: 12px;
  color: #64748b;
  border-left: 3px solid #bae6fd;
  padding-left: 8px;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.action-icon {
  cursor: pointer;
  color: #94a3b8;
  transition: color 0.15s;
  display: flex;
  align-items: center;
}

.action-icon:hover {
  color: #0284c7;
}

.thinking-spinner {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  max-width: 85%;
}

.thinking-spinner .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #0284c7;
  animation: bounce 1.4s infinite ease-in-out both;
}

.thinking-spinner .dot:nth-child(1) { animation-delay: -0.32s; }
.thinking-spinner .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.sources {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.src-tag {
  cursor: pointer;
}

/* Markdown styles */
.markdown-body :deep(p) {
  margin: 0 0 8px;
  line-height: 1.6;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: Consolas, Monaco, monospace;
}

.markdown-body :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}

.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) {
  margin: 12px 0 8px;
  font-weight: 700;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.markdown-body :deep(th), .markdown-body :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #f8fafc;
  font-weight: 600;
}
</style>

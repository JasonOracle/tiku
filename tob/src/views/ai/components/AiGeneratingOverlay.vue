<!--
  * AI 生成等待蒙层（复用组件）：覆盖出题/组卷确认卡，允许用户取消。
  * 用法：<AiGeneratingOverlay :visible="fetching" :title="..." :detail="..." :elapsed="secs" :error="err" @cancel="..." @retry="..." />
-->
<template>
  <div v-if="visible" class="ai-gen-overlay">
    <div class="ai-gen-box">
      <template v-if="!error">
        <el-icon class="ai-gen-spin"><Loading /></el-icon>
        <div class="ai-gen-title">{{ title }}</div>
        <div class="ai-gen-detail">{{ detail }}<span v-if="typeof elapsed === 'number'"> · 已等待{{ elapsed }}s</span></div>
        <div class="ai-gen-actions">
          <el-button v-if="cancelable" size="small" plain @click="$emit('cancel')">取消生成</el-button>
        </div>
        <div v-if="cancelable" class="ai-gen-tip">取消后保留卡片，可随时重试</div>
      </template>
      <template v-else>
        <div class="ai-gen-title ai-gen-err">{{ error }}</div>
        <div class="ai-gen-actions">
          <el-button size="small" type="primary" plain @click="$emit('retry')">重新生成</el-button>
          <el-button v-if="cancelable" size="small" plain @click="$emit('cancel')">取消</el-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue';

const props = withDefaults(
  defineProps<{
    visible: boolean;
    title?: string;
    detail?: string;
    elapsed?: number;
    error?: string;
    cancelable?: boolean;
  }>(),
  { cancelable: true }
);

defineEmits<{
  (e: 'cancel'): void;
  (e: 'retry'): void;
}>();
</script>

<style scoped>
.ai-gen-overlay {
  position: absolute;
  inset: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(248, 250, 252, 0.82);
  backdrop-filter: blur(2px);
  border-radius: 8px;
  padding: 16px;
}
.ai-gen-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  max-width: 320px;
}
.ai-gen-spin {
  font-size: 28px;
  color: #0284c7;
  animation: ai-gen-rotate 1.2s linear infinite;
}
@keyframes ai-gen-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.ai-gen-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}
.ai-gen-detail {
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}
.ai-gen-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.ai-gen-tip {
  font-size: 11px;
  color: #94a3b8;
}
.ai-gen-err {
  color: #b91c1c;
  font-weight: 600;
}
</style>

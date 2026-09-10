<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[重构 ActionCard - 对标 Ant Design X Actions 确认卡，彻底消灭 JSON 裸露]
-->
<template>
  <div class="antx-action-card" :class="`risk-${cardData.riskLevel || 'medium'}`">
    <div class="card-header">
      <div class="title-group">
        <el-icon class="status-icon"><WarningFilled /></el-icon>
        <span class="card-title">{{ cardData.title }}</span>
      </div>
      <el-tag :type="riskTagType" size="small" effect="plain" class="risk-badge">
        {{ riskLabel }}
      </el-tag>
    </div>

    <div class="card-summary" v-if="cardData.summary">
      {{ cardData.summary }}
    </div>

    <div class="card-fields" v-if="cardData.displayFields && cardData.displayFields.length">
      <div v-for="(field, idx) in cardData.displayFields" :key="idx" class="field-item">
        <span class="field-label">{{ field.label }}：</span>
        <span class="field-value">{{ field.value }}</span>
      </div>
    </div>

    <el-collapse v-if="cardData.rawParams && Object.keys(cardData.rawParams).length > 0" class="param-collapse">
      <el-collapse-item title="查看执行技术参数">
        <pre class="raw-code">{{ JSON.stringify(cardData.rawParams, null, 2) }}</pre>
      </el-collapse-item>
    </el-collapse>

    <div class="card-actions">
      <el-button
        type="primary"
        size="default"
        :loading="cardData.status === 'executing'"
        :disabled="cardData.status !== 'pending'"
        @click="$emit('confirm', cardData)"
      >
        {{ cardData.status === 'confirmed' ? '已执行' : '确认执行' }}
      </el-button>
      <el-button
        size="default"
        :disabled="cardData.status !== 'pending'"
        @click="$emit('cancel', cardData)"
      >
        取消
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { WarningFilled } from '@element-plus/icons-vue';
import type { ActionCardPayload } from '../types';

const props = defineProps<{
  cardData: ActionCardPayload;
}>();

defineEmits<{
  (e: 'confirm', card: ActionCardPayload): void;
  (e: 'cancel', card: ActionCardPayload): void;
}>();

const riskTagType = computed(() => {
  if (props.cardData.riskLevel === 'high') return 'danger';
  if (props.cardData.riskLevel === 'low') return 'info';
  return 'warning';
});

const riskLabel = computed(() => {
  if (props.cardData.riskLevel === 'high') return '高风险操作';
  if (props.cardData.riskLevel === 'low') return '低风险';
  return '业务确认';
});
</script>

<style scoped>
.antx-action-card {
  margin-top: 10px;
  max-width: 540px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.antx-action-card.risk-high {
  border-left: 4px solid #f56c6c;
}

.antx-action-card.risk-medium {
  border-left: 4px solid #e6a23c;
}

.antx-action-card.risk-low {
  border-left: 4px solid #409eff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
}

.status-icon {
  color: #e6a23c;
}

.risk-badge {
  font-size: 11px;
}

.card-summary {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.5;
}

.card-fields {
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
}

.field-item {
  display: flex;
  font-size: 13px;
  line-height: 22px;
}

.field-label {
  color: #64748b;
  min-width: 80px;
  flex-shrink: 0;
}

.field-value {
  color: #0f172a;
  font-weight: 500;
  word-break: break-all;
}

.param-collapse {
  margin-bottom: 12px;
  border: none;
}

.raw-code {
  font-size: 12px;
  background: #0f172a;
  color: #e2e8f0;
  padding: 8px 12px;
  border-radius: 6px;
  max-height: 150px;
  overflow-y: auto;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>

<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[新建动作确认卡组件 - action_card 协议渲染]
-->
<template>
  <div class="action-card" :class="[riskClass, { 'action-card--resolved': card.resolved === 'done' || card.resolved === 'cancelled' }]">
    <div class="action-card__header">
      <span class="action-card__icon">
        <el-icon><MagicStick /></el-icon>
      </span>
      <span class="action-card__title">确认: {{ card.title }}</span>
      <span class="action-card__badge" :class="card.resolved === 'done' ? 'badge--done' : card.resolved === 'cancelled' ? 'badge--cancelled' : 'badge--pending'">
        {{ card.resolved === 'done' ? '已执行' : card.resolved === 'cancelled' ? '已取消' : '待确认' }}
      </span>
    </div>
    <div class="action-card__body">
      <div class="action-card__desc">
        风险等级: <strong :style="{ color: riskColor }">{{ riskLabel }}</strong>
      </div>
      <div v-for="(d, di) in card.details" :key="di" class="action-card__detail">
        {{ d.label }}: <strong>{{ d.value }}</strong>
      </div>
      <div v-if="card.resolved === 'cancelled'" class="action-card__cancelled">
        已取消该操作
      </div>
    </div>
    <div v-if="card.resolved !== 'done' && card.resolved !== 'cancelled'" class="action-card__footer">
      <button class="btn-confirm" @click="$emit('confirm', card)">确认执行</button>
      <button class="btn-cancel" @click="$emit('cancel', card)">取消</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { MagicStick } from '@element-plus/icons-vue';

export interface ActionDetail {
  label: string;
  value: string;
}

export interface ActionCard {
  actionType: string;
  title: string;
  riskLevel?: string;
  details?: ActionDetail[];
  payload?: any;
  resolved?: 'pending' | 'done' | 'cancelled';
}

const props = defineProps<{
  card: ActionCard;
}>();

const emit = defineEmits<{
  (e: 'confirm', card: ActionCard): void;
  (e: 'cancel', card: ActionCard): void;
}>();

const riskLabel = computed(() => {
  const level = props.card.riskLevel;
  if (level === 'high') return '高';
  if (level === 'medium') return '中';
  if (level === 'low') return '低';
  return '未知';
});

const riskClass = computed(() => {
  const level = props.card.riskLevel;
  if (level === 'high') return 'high-risk';
  if (level === 'medium') return 'med-risk';
  return 'low-risk';
});

const riskColor = computed(() => {
  const level = props.card.riskLevel;
  if (level === 'high') return '#ef4444';
  if (level === 'medium') return '#0284c7';
  return '#64748b';
});
</script>

<style scoped>
.action-card {
  margin-top: 12px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #fee2e2;
  width: 100%;
  max-width: 400px;
}

.action-card.med-risk {
  border-color: #cffafe;
}

.action-card.low-risk {
  border-color: #e2e8f0;
}

.action-card.action-card--resolved {
  border-color: #d1fae5;
}

.action-card__header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #fecaca 0%, #fff1f2 100%);
  border-bottom: 1px solid #fee2e2;
}

.action-card.med-risk .action-card__header {
  background: linear-gradient(135deg, #a5f3fc 0%, #ecfeff 100%);
  border-bottom-color: #cffafe;
}

.action-card.low-risk .action-card__header {
  background: linear-gradient(135deg, #e2e8f0 0%, #f1f5f9 100%);
  border-bottom-color: #e2e8f0;
}

.action-card.action-card--resolved .action-card__header {
  background: linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%);
  border-bottom-color: #d1fae5;
}

.action-card__icon {
  font-size: 16px;
}

.action-card__title {
  font-weight: 700;
  color: #1e293b;
  font-size: 14px;
  flex: 1;
}

.action-card__badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  background: #f87171;
  color: #fff;
}

.badge--done {
  background: #10b981;
}

.badge--cancelled {
  background: #94a3b8;
}

.action-card__body {
  padding: 16px;
}

.action-card__desc {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  margin-bottom: 12px;
}

.action-card__detail {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  margin-bottom: 8px;
}

.action-card__cancelled {
  font-size: 13px;
  color: #64748b;
}

.action-card__footer {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid #f1f5f9;
}

.btn-confirm {
  width: 100%;
  padding: 10px;
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm:hover {
  background: #dc2626;
}

.btn-confirm-medium {
  width: 100%;
  padding: 10px;
  background: #0284c7;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm-medium:hover {
  background: #0369a1;
}

.btn-cancel {
  width: 100%;
  padding: 10px;
  background: #fff;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}
</style>

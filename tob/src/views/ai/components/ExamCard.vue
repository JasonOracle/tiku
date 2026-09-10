<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[试卷导出卡片组件 - exam_card 协议渲染]
-->
<template>
  <div class="exam-card" :class="{ 'exam-card--active': active }">
    <div class="exam-card__header">
      <div class="exam-card__icon">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        </svg>
      </div>
      <div class="exam-card__info">
        <div class="exam-card__title">{{ cardData.title }}</div>
        <div class="exam-card__meta">
          <span>{{ cardData.questionCount || 0 }} 题</span>
          <span class="exam-card__dot">·</span>
          <span>{{ cardData.totalScore || 0 }} 分</span>
          <span v-if="cardData.createdAt" class="exam-card__dot">·</span>
          <span v-if="cardData.createdAt">{{ cardData.createdAt }}</span>
          <span class="exam-card__format">Word</span>
        </div>
      </div>
    </div>
    <div class="exam-card__actions">
      <button class="exam-card__btn" @click="$emit('download', cardData)" title="下载试卷 (Word 文档)">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
        </svg>
        下载
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExamCardData } from '../types';

defineProps<{
  cardData: ExamCardData;
  active?: boolean;
}>();

defineEmits<{
  (e: 'download', card: ExamCardData): void;
}>();
</script>

<style scoped>
.exam-card {
  position: relative;
  width: 100%;
  max-width: 440px;
  min-height: 80px;
  background: #ffffff;
  background-image:
    linear-gradient(to right, rgba(226, 232, 240, 0.45) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(226, 232, 240, 0.45) 1px, transparent 1px);
  background-size: 16px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 14px 60px 14px 16px;
  margin-top: 10px;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.02);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.exam-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04);
}

.exam-card--active {
  border-color: #0284c7;
  box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.15), 0 8px 20px rgba(2, 132, 199, 0.1);
}

.exam-card__header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.exam-card__icon {
  position: relative;
  z-index: 2;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2563eb;
  flex-shrink: 0;
}

.exam-card__info {
  position: relative;
  z-index: 2;
  padding-right: 8px;
  flex: 1;
  min-width: 0;
}

.exam-card__title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.4;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.exam-card__meta {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.exam-card__dot {
  color: #cbd5e1;
}

.exam-card__format {
  background: #eff6ff;
  color: #2563eb;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid #dbeafe;
}

.exam-card__actions {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 4px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 3px 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.exam-card__btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 6px;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s ease;
}

.exam-card__btn:hover {
  background: #f1f5f9;
  color: #2563eb;
}
</style>

<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[新建操作列表卡组件 - action_list 协议渲染]
-->
<template>
  <div class="action-list-card">
    <div v-for="(item, li) in list" :key="li" class="action-list-row">
      <div class="action-list-main">
        <span class="action-list-title">{{ item.title }}</span>
        <el-tag v-if="item.badge" size="small" type="warning" effect="dark">{{ item.badge }}</el-tag>
      </div>
      <el-button
        v-if="item.action"
        size="small"
        type="primary"
        plain
        @click="$emit('action', item.action)"
      >
        {{ item.action.label }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface ActionListItem {
  title: string;
  badge?: string;
  action?: {
    type: string;
    label: string;
    target: string;
    params?: any;
  };
}

defineProps<{
  list: ActionListItem[];
}>();

defineEmits<{
  (e: 'action', action: { type: string; label: string; target: string; params?: any }): void;
}>();
</script>

<style scoped>
.action-list-card {
  margin-top: 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  max-width: 440px;
}

.action-list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  border-bottom: 1px solid #f1f5f9;
}

.action-list-row:last-child {
  border-bottom: none;
}

.action-list-main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.action-list-title {
  font-weight: 600;
  color: #0f172a;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

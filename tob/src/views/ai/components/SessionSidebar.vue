<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Agnes-2.5-Flash
 * 修改内容：[新建会话侧边栏组件]
-->
<template>
  <div class="session-sidebar">
    <div class="new-chat-btn" @click="$emit('new')">
      <el-icon><Plus /></el-icon>
      <span>新建对话</span>
    </div>

    <div class="session-list">
      <div
        v-for="s in sessions"
        :key="s.id"
        class="session-item"
        :class="{ active: s.id === activeId }"
        @click="$emit('select', s.id)"
      >
        <el-icon class="item-icon"><ChatDotRound /></el-icon>
        <span class="session-title" @dblclick.stop="startRename(s)">{{ s.title || '新对话' }}</span>
        <el-icon
          v-if="hoveredId === s.id"
          class="del-icon"
          @click.stop="handleDelete(s.id)"
        ><Delete /></el-icon>
      </div>
    </div>

    <div v-if="renamingId" class="rename-input-wrap">
      <el-input
        v-model="renameValue"
        size="small"
        @keyup.enter="finishRename"
        @keyup.escape="cancelRename"
        blur
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, ChatDotRound, Delete } from '@element-plus/icons-vue';
import request from '../../../utils/request';

export interface CloudSession {
  id: number;
  title: string;
}

const props = defineProps<{
  sessions: CloudSession[];
  activeId: number | null;
}>();

const emit = defineEmits<{
  (e: 'new'): void;
  (e: 'select', id: number): void;
  (e: 'delete', id: number): void;
}>();

const hoveredId = ref<number | null>(null);
const renamingId = ref<number | null>(null);
const renameValue = ref('');

const startRename = (s: CloudSession) => {
  renamingId.value = s.id;
  renameValue.value = s.title;
};

const finishRename = async () => {
  if (!renamingId.value || !renameValue.value.trim()) return;
  try {
    await request.put(`/api/v1/admin/ai/sessions/${renamingId.value}`, {
      title: renameValue.value.trim().slice(0, 120)
    });
    emit('select', renamingId.value!);
  } catch (e) {
    /* 静默 */
  } finally {
    renamingId.value = null;
  }
};

const cancelRename = () => {
  renamingId.value = null;
  renameValue.value = '';
};

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('删除该会话？', '提示', { type: 'warning' });
  } catch {
    return;
  }
  try {
    await request.delete(`/api/v1/admin/ai/sessions/${id}`);
    emit('delete', id);
    ElMessage.success('已删除');
  } catch (e) {
    /* 拦截器已提示 */
  }
};
</script>

<style scoped>
.session-sidebar {
  width: 240px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  border: none;
  width: 100%;
}

.new-chat-btn:hover {
  opacity: 0.9;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 16px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #475569;
  cursor: pointer;
  margin-bottom: 4px;
  font-size: 13px;
  transition: all 0.15s;
}

.session-item:hover {
  background: #e2e8f0;
}

.session-item.active {
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 600;
}

.item-icon {
  flex-shrink: 0;
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.del-icon {
  display: none;
  color: #94a3b8;
  flex-shrink: 0;
}

.session-item:hover .del-icon {
  display: block;
}

.del-icon:hover {
  color: #ef4444;
}

.rename-input-wrap {
  margin-top: 8px;
}
</style>

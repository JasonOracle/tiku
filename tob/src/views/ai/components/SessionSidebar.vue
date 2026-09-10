<!--
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：Gemini 系列
 * 修改内容：[1. 精简重构侧边栏交互与视觉动效：添加会话悬浮态样式、平滑过渡背景；2. 新增豆包同款更多操作(MoreFilled上下三点图标)，悬浮/展开时显式展示；3. 下拉菜单支持重命名与危险红色删除选项；4. 原生样式还原“编辑对话名称”弹窗与“确定删除对话”危险确认弹窗]
-->
<template>
  <div class="session-sidebar">
    <!-- 新建对话按钮 -->
    <button class="new-chat-btn" type="button" @click="$emit('new')">
      <el-icon class="btn-icon"><Plus /></el-icon>
      <span>新建对话</span>
    </button>

    <!-- 会话列表 -->
    <div class="session-list">
      <div
        v-for="s in sessions"
        :key="s.id"
        class="session-item"
        :class="{ active: s.id === activeId, 'menu-open': activeMenuSessionId === s.id }"
        @click="$emit('select', s.id)"
      >
        <el-icon class="item-icon"><ChatDotRound /></el-icon>
        <span class="session-title" :title="s.title || '新对话'">{{ s.title || '新对话' }}</span>

        <!-- 右侧更多操作（上下三点） -->
        <div class="more-action" @click.stop>
          <el-dropdown
            trigger="click"
            placement="bottom-end"
            :teleported="true"
            @visible-change="(visible: boolean) => handleDropdownVisible(visible, s.id)"
            @command="(cmd: string) => handleMenuCommand(cmd, s)"
          >
            <span class="more-trigger-btn" title="更多操作">
              <el-icon><MoreFilled /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu class="session-dropdown-menu">
                <el-dropdown-item command="rename" class="menu-item-rename">
                  <el-icon><EditPen /></el-icon>
                  <span>重命名</span>
                </el-dropdown-item>
                <el-dropdown-item command="delete" class="menu-item-delete" divided>
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 编辑对话名称弹窗 (严格还原设计图3) -->
    <el-dialog
      v-model="renameDialogVisible"
      title="编辑对话名称"
      width="440px"
      :append-to-body="true"
      :show-close="true"
      custom-class="custom-rename-dialog"
      :before-close="handleRenameClose"
    >
      <div class="rename-dialog-body">
        <el-input
          ref="renameInputRef"
          v-model="renameInputValue"
          placeholder="请输入对话名称"
          maxlength="100"
          clearable
          @keyup.enter="confirmRename"
        />
      </div>
      <template #footer>
        <div class="dialog-actions">
          <button class="btn-cancel" type="button" @click="handleRenameClose">取消</button>
          <button class="btn-primary" type="button" :disabled="!renameInputValue.trim() || renameLoading" @click="confirmRename">
            确定
          </button>
        </div>
      </template>
    </el-dialog>

    <!-- 删除对话确认弹窗 (严格还原设计图4危险弹窗) -->
    <el-dialog
      v-model="deleteDialogVisible"
      width="440px"
      :append-to-body="true"
      :show-close="false"
      custom-class="custom-delete-dialog"
    >
      <div class="delete-dialog-body">
        <div class="warning-icon-wrap">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="delete-content">
          <h4 class="delete-title">确定删除对话？</h4>
          <p class="delete-desc">删除后，聊天记录将不可恢复。</p>
        </div>
      </div>
      <template #footer>
        <div class="dialog-actions">
          <button class="btn-cancel" type="button" :disabled="deleteLoading" @click="deleteDialogVisible = false">
            取消
          </button>
          <button class="btn-danger" type="button" :disabled="deleteLoading" @click="confirmDelete">
            删除
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus, ChatDotRound, MoreFilled, EditPen, Delete, WarningFilled } from '@element-plus/icons-vue';
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
  (e: 'renamed', id: number, newTitle: string): void;
}>();

// 下拉菜单显隐状态记录（用于保持悬浮更多图标显示）
const activeMenuSessionId = ref<number | null>(null);

// 重命名状态
const renameDialogVisible = ref(false);
const renameLoading = ref(false);
const renameInputValue = ref('');
const targetSession = ref<CloudSession | null>(null);
const renameInputRef = ref<any>(null);

// 删除弹窗状态
const deleteDialogVisible = ref(false);
const deleteLoading = ref(false);
const deleteTargetSessionId = ref<number | null>(null);

const handleDropdownVisible = (visible: boolean, sessionId: number) => {
  activeMenuSessionId.value = visible ? sessionId : null;
};

const handleMenuCommand = (cmd: string, session: CloudSession) => {
  if (cmd === 'rename') {
    targetSession.value = session;
    renameInputValue.value = session.title || '';
    renameDialogVisible.value = true;
    nextTick(() => {
      renameInputRef.value?.focus?.();
    });
  } else if (cmd === 'delete') {
    deleteTargetSessionId.value = session.id;
    deleteDialogVisible.value = true;
  }
};

const handleRenameClose = () => {
  renameDialogVisible.value = false;
  targetSession.value = null;
  renameInputValue.value = '';
};

const confirmRename = async () => {
  const newTitle = renameInputValue.value.trim();
  if (!targetSession.value || !newTitle || renameLoading.value) return;

  renameLoading.value = true;
  try {
    await request.put(`/api/v1/admin/ai/sessions/${targetSession.value.id}`, {
      title: newTitle.slice(0, 120)
    });
    // 本地响应式同步并通知父组件
    targetSession.value.title = newTitle;
    emit('renamed', targetSession.value.id, newTitle);
    ElMessage.success('重命名成功');
    handleRenameClose();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '重命名失败，请重试');
  } finally {
    renameLoading.value = false;
  }
};

const confirmDelete = async () => {
  if (!deleteTargetSessionId.value || deleteLoading.value) return;
  const sid = deleteTargetSessionId.value;
  deleteLoading.value = true;
  try {
    await request.delete(`/api/v1/admin/ai/sessions/${sid}`);
    deleteDialogVisible.value = false;
    deleteTargetSessionId.value = null;
    emit('delete', sid);
    ElMessage.success('对话已删除');
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败，请重试');
  } finally {
    deleteLoading.value = false;
  }
};
</script>

<style scoped>
.session-sidebar {
  width: 260px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 16px;
  box-sizing: border-box;
  user-select: none;
}

/* 新建对话按钮 */
.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #0284c7;
  color: #ffffff;
  padding: 11px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  width: 100%;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.2);
}

.new-chat-btn:hover {
  background: #0369a1;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
  transform: translateY(-1px);
}

.new-chat-btn:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 16px;
}

/* 列表区域 */
.session-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 16px;
  padding-right: 2px;
}

/* 单条会话 */
.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  color: #334155;
  cursor: pointer;
  margin-bottom: 6px;
  font-size: 13px;
  transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
  position: relative;
}

/* 鼠标悬浮效果 */
.session-item:hover {
  background: #edf2f7;
  color: #0f172a;
}

/* 选中激活状态 */
.session-item.active {
  background: #e0f2fe;
  color: #0284c7;
  font-weight: 600;
}

.session-item.active:hover {
  background: #d8eefe;
}

.item-icon {
  flex-shrink: 0;
  font-size: 16px;
  color: #64748b;
  transition: color 0.18s ease;
}

.session-item.active .item-icon {
  color: #0284c7;
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

/* 右侧更多操作（上下三点） */
.more-action {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.more-trigger-btn {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: #94a3b8;
  opacity: 0;
  transition: opacity 0.18s ease, color 0.18s ease, background-color 0.18s ease;
  cursor: pointer;
}

/* 悬浮会话或下拉打开时展示三点图标 */
.session-item:hover .more-trigger-btn,
.session-item.menu-open .more-trigger-btn {
  opacity: 1;
}

.more-trigger-btn:hover {
  color: #334155;
  background-color: rgba(0, 0, 0, 0.06);
}

.session-item.active .more-trigger-btn:hover {
  background-color: rgba(2, 132, 199, 0.12);
  color: #0284c7;
}

/* 弹窗通用操作按钮 */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 8px 20px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #ffffff;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.btn-primary {
  padding: 8px 24px;
  font-size: 14px;
  border: none;
  border-radius: 8px;
  background: #1677ff;
  color: #ffffff;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #4096ff;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  padding: 8px 24px;
  font-size: 14px;
  border: none;
  border-radius: 8px;
  background: #ff4d4f;
  color: #ffffff;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background: #ff7875;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 删除弹窗主体 */
.delete-dialog-body {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 8px 0 12px;
}

.warning-icon-wrap {
  flex-shrink: 0;
  font-size: 24px;
  color: #faad14;
  line-height: 1;
  margin-top: 2px;
}

.delete-content {
  flex: 1;
}

.delete-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.delete-desc {
  margin: 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.5;
}

/* 重命名弹窗主体 */
.rename-dialog-body {
  padding: 8px 0 16px;
}
</style>

<style>
/* 下拉菜单全局覆盖（因为 teleported 到 body） */
.session-dropdown-menu .menu-item-delete {
  color: #ff4d4f !important;
}

.session-dropdown-menu .menu-item-delete:hover {
  background-color: #fff1f0 !important;
  color: #ff4d4f !important;
}

.session-dropdown-menu .menu-item-delete .el-icon {
  color: #ff4d4f !important;
}
</style>

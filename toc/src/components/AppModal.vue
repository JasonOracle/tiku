<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[1. 新建高级拟物毛玻璃 AppModal.vue 通用弹窗组件，替代浏览器原生的 window.confirm 和 alert]
-->
<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="modelValue" class="app-modal-mask" @click="handleMaskClick">
        <div class="app-modal-container" @click.stop>
          <!-- 顶部 Icon 标识 -->
          <div class="modal-icon-wrapper" :class="type">
            <svg v-if="type === 'warning'" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <svg v-else-if="type === 'success'" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <svg v-else width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>

          <!-- 标题与内容正文 -->
          <h3 class="modal-title">{{ title }}</h3>
          <p class="modal-message" v-if="message">{{ message }}</p>

          <!-- 按钮操作区 -->
          <div class="modal-actions">
            <button v-if="showCancel" class="btn-cancel" @click="handleCancel">
              {{ cancelText }}
            </button>
            <button class="btn-confirm" :class="type" @click="handleConfirm">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: boolean;
    title?: string;
    message?: string;
    type?: 'warning' | 'info' | 'success' | 'danger';
    showCancel?: boolean;
    confirmText?: string;
    cancelText?: string;
    closeOnMask?: boolean;
  }>(),
  {
    title: '提示',
    message: '',
    type: 'info',
    showCancel: true,
    confirmText: '确定',
    cancelText: '取消',
    closeOnMask: true
  }
);

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);

const handleConfirm = () => {
  emit('update:modelValue', false);
  emit('confirm');
};

const handleCancel = () => {
  emit('update:modelValue', false);
  emit('cancel');
};

const handleMaskClick = () => {
  if (props.closeOnMask) {
    handleCancel();
  }
};
</script>

<style scoped>
.app-modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.app-modal-container {
  width: 100%;
  max-width: 320px;
  background: #ffffff;
  border-radius: 24px;
  padding: 24px 20px 20px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  text-align: center;
  border: 1px solid rgba(226, 232, 240, 0.8);
  animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalPop {
  0% { transform: scale(0.85); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.modal-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 20px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-icon-wrapper.warning {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #d97706;
}

.modal-icon-wrapper.success {
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  color: #16a34a;
}

.modal-icon-wrapper.info {
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
  color: #0284c7;
}

.modal-icon-wrapper.danger {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #dc2626;
}

.modal-title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 800;
  color: #0f172a;
}

.modal-message {
  margin: 0 0 20px;
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 10px;
}

.btn-cancel {
  flex: 1;
  height: 44px;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm {
  flex: 1;
  height: 44px;
  border-radius: 14px;
  border: none;
  color: white;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-confirm.info {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}

.btn-confirm.success {
  background: linear-gradient(135deg, #16a34a, #15803d);
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
}

.btn-confirm.danger {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>

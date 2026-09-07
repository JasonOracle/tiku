<!--
  * [变更日志]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.7 新建: 头像个人信息弹窗 (账号/角色/额度展示 + 退出登录)]
  -->
<template>
  <el-dialog v-model="visible" title="个人信息" width="420px" destroy-on-close>
    <div class="profile-box">
      <el-avatar :size="64" class="profile-avatar">
        {{ (userStore.username || 'A').substring(0, 1).toUpperCase() }}
      </el-avatar>
      <div class="profile-name">{{ userStore.username }}</div>
      <el-tag
        size="small"
        :type="userStore.isSuper() ? 'danger' : (userStore.role === 'admin' ? 'warning' : 'primary')"
        effect="plain"
      >
        {{ roleText }}
      </el-tag>
      <el-descriptions :column="1" border size="small" style="margin-top: 16px; width: 100%">
        <el-descriptions-item label="登录账号">{{ userStore.username }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ roleText }}</el-descriptions-item>
        <el-descriptions-item label="今日 AI 剩余额度">{{ userStore.quotaRemaining }} 次</el-descriptions-item>
        <el-descriptions-item label="每日 AI 额度上限">
          {{ userStore.isSuper() ? '无限制' : `${userStore.quotaLimit} 次` }}
        </el-descriptions-item>
      </el-descriptions>
    </div>
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../../../store/user';

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>();
const userStore = useUserStore();
const router = useRouter();

const visible = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v)
});

const roleText = computed(() =>
  userStore.isSuper() ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '出题人')
);

const handleLogout = () => {
  userStore.logout();
  visible.value = false;
  router.push('/login');
};
</script>

<style scoped>
.profile-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
}

.profile-avatar {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
}

.profile-name {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 12px 0 8px;
}
</style>

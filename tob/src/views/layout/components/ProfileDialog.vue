<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 3.6 Flash
 * 修改内容：[1. 将【姓名】设为必填字段并增加保存时的前置校验；2. 修复个人资料弹窗模板结构]
-->
<template>
  <el-dialog v-model="visible" title="个人资料与信息" width="520px" destroy-on-close @open="handleOpen">
    <div class="profile-box">
      <el-avatar :size="64" class="profile-avatar">
        {{ (form.name || userStore.username || userStore.phone || 'A').substring(0, 1).toUpperCase() }}
      </el-avatar>
      <div class="profile-name">{{ form.name || userStore.username || userStore.phone }}</div>
      <div class="role-quota-tags">
        <el-tag
          size="small"
          :type="userStore.isSuper() ? 'danger' : (userStore.role === 'admin' ? 'warning' : 'primary')"
          effect="plain"
        >
          {{ roleText }}
        </el-tag>
      </div>

      <el-tabs v-model="activeTab" style="width: 100%; margin-top: 16px;">
        <!-- 基本资料编辑 -->
        <el-tab-pane label="基本资料" name="edit">
          <el-form :model="form" label-width="80px" size="default" style="margin-top: 12px;">
            <el-form-item label="登录账号">
              <el-input :value="userStore.username || userStore.phone" disabled />
            </el-form-item>
            <el-form-item label="姓名" required>
              <el-input v-model="form.name" placeholder="请输入姓名（必填）" maxlength="30" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" placeholder="请输入昵称" maxlength="50" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" maxlength="100" />
            </el-form-item>
            <el-form-item label="职业">
              <el-input v-model="form.occupation" placeholder="请输入职业" maxlength="100" />
            </el-form-item>
            <el-form-item label="年龄">
              <el-input-number v-model="form.age" :min="0" :max="150" :precision="0" style="width: 100%" placeholder="请输入年龄" />
            </el-form-item>
            <el-form-item label="性别">
              <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%" clearable>
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
                <el-option label="保密" value="secret" />
              </el-select>
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="form.bio" type="textarea" :rows="3" placeholder="请输入个人简介" maxlength="500" show-word-limit />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 系统与权限概况 -->
        <el-tab-pane label="权限" name="info">
          <el-descriptions :column="1" border size="small" style="margin-top: 12px; width: 100%">
            <el-descriptions-item label="登录账号">{{ userStore.username }}</el-descriptions-item>
            <el-descriptions-item label="系统角色">{{ roleText }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
        <div style="flex: 1"></div>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveProfile">保存修改</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../../../store/user';
import request from '../../../utils/request';

const props = defineProps<{ modelValue: boolean }>();
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>();
const userStore = useUserStore();
const router = useRouter();

const activeTab = ref('edit');
const saving = ref(false);

const form = reactive({
  name: '',
  phone: '',
  nickname: '',
  email: '',
  occupation: '',
  bio: '',
  age: null as number | null,
  gender: ''
});

const visible = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v)
});

const roleText = computed(() =>
  userStore.isSuper() ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '成员')
);

// 打开弹窗时拉取最新详情
const handleOpen = async () => {
  try {
    const res: any = await request.get('/api/v1/auth/me');
    if (res) {
      form.name = res.display_name || '';
      form.phone = res.phone || '';
      form.nickname = res.nickname || '';
      form.email = res.email || '';
      form.occupation = res.occupation || '';
      form.bio = res.bio || '';
      form.age = (res.age ?? null) as number | null;
      form.gender = res.gender || '';
    }
  } catch (e) {
    /* 保持原样 */
  }
};

const handleSaveProfile = async () => {
  if (!form.name || !form.name.trim()) {
    ElMessage.warning('用户姓名不能为空，请输入姓名');
    return;
  }

  saving.value = true;
  try {
    await request.put('/api/v1/auth/profile', {
      display_name: form.name.trim(),
      phone: form.phone,
      nickname: form.nickname,
      email: form.email,
      occupation: form.occupation,
      bio: form.bio,
      age: form.age,
      gender: form.gender
    });
    // 立即刷新本地全局 Pinia 用户状态，确保 AI 助理和页面立即同步
    await userStore.loadProfile();
    ElMessage.success('个人资料已更新');
    visible.value = false;
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败');
  } finally {
    saving.value = false;
  }
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.profile-box {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-avatar {
  background: #0284c7;
  color: white;
  font-weight: bold;
  font-size: 24px;
}

.profile-name {
  margin-top: 8px;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.role-quota-tags {
  margin-top: 6px;
  display: flex;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  align-items: center;
  width: 100%;
}
</style>

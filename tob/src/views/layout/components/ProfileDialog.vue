<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：资料精简为展示名+手机号，旧性别/邮箱/职位/额度体系已删除]
-->
<template>
  <el-dialog v-model="visible" title="个人资料与信息" width="520px" destroy-on-close @open="handleOpen">
    <div class="profile-box">
      <el-avatar :size="64" class="profile-avatar">
        {{ (userStore.username || userStore.phone || 'A').substring(0, 1).toUpperCase() }}
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
            <el-form-item label="姓名">
              <el-input v-model="form.name" placeholder="请输入姓名" maxlength="30" />
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
  saving.value = true;
  try {
    await request.put('/api/v1/auth/profile', {
      display_name: form.name,
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
    ElMessage.success('个人资料已成功保存');
    visible.value = false;
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败，请稍后重试');
  } finally {
    saving.value = false;
  }
};

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
  padding: 4px 0;
}

.profile-avatar {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
}

.profile-name {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 10px 0 4px;
}

.role-quota-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.dialog-footer {
  display: flex;
  align-items: center;
  width: 100%;
}
</style>

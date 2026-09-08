<!--
  * [变更日志]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[v1.3: 升级个人信息弹窗，支持编辑基础资料(姓名/手机/邮箱/性别/职位/个人介绍)，无缝调用 PUT /api/v1/admin/auth/profile]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.7 新建: 头像个人信息弹窗 (账号/角色/额度展示 + 退出登录)]
  -->
<template>
  <el-dialog v-model="visible" title="个人资料与信息" width="520px" destroy-on-close @open="handleOpen">
    <div class="profile-box">
      <el-avatar :size="64" class="profile-avatar">
        {{ (userStore.username || 'A').substring(0, 1).toUpperCase() }}
      </el-avatar>
      <div class="profile-name">{{ form.name || userStore.username }}</div>
      <div class="role-quota-tags">
        <el-tag
          size="small"
          :type="userStore.isSuper() ? 'danger' : (userStore.role === 'admin' ? 'warning' : 'primary')"
          effect="plain"
        >
          {{ roleText }}
        </el-tag>
        <el-tag size="small" type="info" effect="plain" style="margin-left: 8px;">
          今日 AI 额度: {{ userStore.quotaRemaining }} 次
        </el-tag>
      </div>

      <el-tabs v-model="activeTab" style="width: 100%; margin-top: 16px;">
        <!-- 基本资料编辑 -->
        <el-tab-pane label="基本资料" name="edit">
          <el-form :model="form" label-width="80px" size="default" style="margin-top: 12px;">
            <el-form-item label="登录账号">
              <el-input :value="userStore.username" disabled />
            </el-form-item>
            <el-form-item label="真实姓名">
              <el-input v-model="form.name" placeholder="请输入姓名" maxlength="30" />
            </el-form-item>
            <el-form-item label="性别">
              <el-radio-group v-model="form.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
                <el-radio label="保密">保密</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="20" />
            </el-form-item>
            <el-form-item label="电子邮箱">
              <el-input v-model="form.email" placeholder="请输入常用邮箱" maxlength="100" />
            </el-form-item>
            <el-form-item label="担任职位">
              <el-input v-model="form.position" placeholder="例如：资深教研员 / 命题专家" maxlength="50" />
            </el-form-item>
            <el-form-item label="个人介绍">
              <el-input
                v-model="form.bio"
                type="textarea"
                :rows="3"
                placeholder="填写个人业务专长或教研方向..."
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 系统与权限概况 -->
        <el-tab-pane label="权限与额度" name="info">
          <el-descriptions :column="1" border size="small" style="margin-top: 12px; width: 100%">
            <el-descriptions-item label="登录账号">{{ userStore.username }}</el-descriptions-item>
            <el-descriptions-item label="系统角色">{{ roleText }}</el-descriptions-item>
            <el-descriptions-item label="今日 AI 剩余额度">{{ userStore.quotaRemaining }} 次</el-descriptions-item>
            <el-descriptions-item label="每日 AI 额度上限">
              {{ userStore.isSuper() ? '无限制 (超级管理员)' : `${userStore.quotaLimit} 次` }}
            </el-descriptions-item>
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
  gender: '保密',
  email: '',
  position: '',
  bio: ''
});

const visible = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v)
});

const roleText = computed(() =>
  userStore.isSuper() ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '出题人')
);

// 打开弹窗时拉取最新详情
const handleOpen = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/auth/me');
    if (res) {
      form.name = res.name || '';
      form.phone = res.phone || '';
      form.gender = res.gender || '保密';
      form.email = res.email || '';
      form.position = res.position || '';
      form.bio = res.bio || '';
    }
  } catch (e) {
    /* 保持原样 */
  }
};

const handleSaveProfile = async () => {
  saving.value = true;
  try {
    await request.put('/api/v1/admin/auth/profile', {
      name: form.name,
      phone: form.phone,
      gender: form.gender,
      email: form.email,
      position: form.position,
      bio: form.bio
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

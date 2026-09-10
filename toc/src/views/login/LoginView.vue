<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[成员端手机号登录，废除开放注册，登录后持久化租户直达企业空间]
-->
<template>
  <div class="mobile-login-container">
    <div class="glass-card">
      <div class="header">
        <div class="logo">TiKu</div>
        <h2>欢迎加入企业空间</h2>
        <p>请使用管理员录入的手机号登录</p>
      </div>

      <div class="form-group">
        <label>手机号</label>
        <input v-model="phone" type="tel" maxlength="11" placeholder="11 位手机号" class="input-field" />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="默认 123456（首次请改密）" class="input-field" />
      </div>

      <button class="submit-btn" :disabled="loading" @click="handleSubmit">
        {{ loading ? '处理中...' : '登录进入企业空间' }}
      </button>
    </div>
    <AppModal
      v-model="modalVisible"
      :title="modalTitle"
      :message="modalMessage"
      :type="modalType"
      :showCancel="false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../../store/user';
import http from '../../utils/http';
import AppModal from '../../components/AppModal.vue';

const router = useRouter();
const userStore = useUserStore();

const phone = ref('');
const password = ref('');
const loading = ref(false);

const modalVisible = ref(false);
const modalTitle = ref('提示');
const modalMessage = ref('');
const modalType = ref<'info' | 'warning' | 'success' | 'danger'>('info');

const showAlert = (msg: string, type: 'info' | 'warning' | 'success' | 'danger' = 'warning', title = '提示') => {
  modalTitle.value = title;
  modalMessage.value = msg;
  modalType.value = type;
  modalVisible.value = true;
};

const handleSubmit = async () => {
  if (!/^1[3-9]\d{9}$/.test(phone.value.trim())) {
    showAlert('请输入正确的 11 位手机号', 'warning');
    return;
  }
  if (!password.value) {
    showAlert('请输入密码', 'warning');
    return;
  }
  loading.value = true;
  try {
    const res: any = await http.post('/api/v1/auth/login', { phone: phone.value.trim(), password: password.value });
    userStore.applyLoginPayload(res);
    router.push('/');
  } catch (e: any) {
    showAlert(e.message || '请求处理失败', 'danger', '错误');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.mobile-login-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #0284c7 0%, #38bdf8 50%, #818cf8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.glass-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px 24px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 16px 36px rgba(2, 132, 199, 0.2);
}

.header {
  text-align: center;
  margin-bottom: 24px;
}

.logo {
  display: inline-block;
  background: #0284c7;
  color: white;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
}

.header h2 {
  margin: 12px 0 4px;
  font-size: 20px;
  color: #0f172a;
}

.header p {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.input-field {
  height: 44px;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  padding: 0 14px;
  font-size: 14px;
  outline: none;
}

.input-field:focus {
  border-color: #0284c7;
  background: rgba(255, 255, 255, 0.9);
}

.submit-btn {
  width: 100%;
  height: 46px;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  font-size: 15px;
  margin-top: 12px;
  cursor: pointer;
}
</style>

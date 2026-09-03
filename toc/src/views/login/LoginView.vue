<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端移动端用户登录/注册一体化毛玻璃卡片]
-->
<template>
  <div class="mobile-login-container">
    <div class="glass-card">
      <div class="header">
        <div class="logo">TiKu</div>
        <h2>{{ isRegister ? '注册智题库账号' : '欢迎使用智题库' }}</h2>
        <p>轻量在线测评 & 知识测验平台</p>
      </div>

      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" type="text" placeholder="请输入 3 位以上用户名" class="input-field" />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="请输入密码" class="input-field" />
      </div>

      <button class="submit-btn" :disabled="loading" @click="handleSubmit">
        {{ loading ? '处理中...' : isRegister ? '立即注册' : '登录体验' }}
      </button>

      <div class="toggle-mode">
        <span @click="isRegister = !isRegister">
          {{ isRegister ? '已有账号？点击去登录' : '没有账号？点击注册新用户' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import http from '../../utils/http';
import { useUserStore } from '../../store/user';

const router = useRouter();
const userStore = useUserStore();

const isRegister = ref(false);
const username = ref('');
const password = ref('');
const loading = ref(false);

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    alert('请补全用户名和密码');
    return;
  }
  loading.value = true;
  try {
    if (isRegister.value) {
      await http.post('/api/v1/auth/register', { username: username.value, password: password.value });
      alert('注册成功，请点击登录');
      isRegister.value = false;
    } else {
      const res: any = await http.post('/api/v1/auth/login', { username: username.value, password: password.value });
      userStore.setToken(res.token, res.user?.username || username.value);
      router.push('/');
    }
  } catch (e: any) {
    alert(e.message || '请求处理失败');
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

.toggle-mode {
  text-align: center;
  margin-top: 18px;
  font-size: 13px;
  color: #0284c7;
  cursor: pointer;
  font-weight: 600;
}
</style>

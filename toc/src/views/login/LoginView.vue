<!--
 * [变更日志]
 * 修改时间：2026-09-06 19:40:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.3: 注册表单扩展完整资料——昵称(必填)/性别(必选男/女)/手机号(必填)/职务(选填)/邮箱(选填);
 *          注册成功切回登录并预填用户名; 登录后 store 记录昵称]
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
        <input v-model="username" type="text" placeholder="3 位以上字母或数字" class="input-field" />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" placeholder="至少 6 位" class="input-field" />
      </div>

      <template v-if="isRegister">
        <div class="form-group">
          <label>昵称 <span class="req">*</span></label>
          <input v-model="nickname" type="text" maxlength="30" placeholder="将展示在个人中心与答题记录" class="input-field" />
        </div>

        <div class="form-group">
          <label>性别 <span class="req">*</span></label>
          <div class="gender-row">
            <button type="button" class="gender-opt male" :class="{ active: gender === 'male' }" @click="gender = 'male'">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="10" cy="14" r="6"></circle><path d="M20 4l-5.6 5.6"></path><path d="M15 4h5v5"></path>
              </svg>
              男
            </button>
            <button type="button" class="gender-opt female" :class="{ active: gender === 'female' }" @click="gender = 'female'">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">
                <circle cx="12" cy="8" r="5"></circle><line x1="12" y1="13" x2="12" y2="21"></line><line x1="9" y1="18" x2="15" y2="18"></line>
              </svg>
              女
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>手机号 <span class="req">*</span></label>
          <input v-model="phone" type="tel" maxlength="11" placeholder="11 位大陆手机号" class="input-field" />
        </div>

        <div class="form-row">
          <div class="form-group half">
            <label>职务</label>
            <input v-model="position" type="text" maxlength="50" placeholder="选填" class="input-field" />
          </div>
          <div class="form-group half">
            <label>邮箱</label>
            <input v-model="email" type="text" maxlength="100" placeholder="选填" class="input-field" />
          </div>
        </div>
      </template>

      <button class="submit-btn" :disabled="loading" @click="handleSubmit">
        {{ loading ? '处理中...' : isRegister ? '立即注册' : '登录体验' }}
      </button>

      <div class="toggle-mode">
        <span @click="toggleMode">
          {{ isRegister ? '已有账号？点击去登录' : '没有账号？点击注册新用户' }}
        </span>
      </div>
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

const isRegister = ref(false);
const username = ref('');
const password = ref('');
const nickname = ref('');
const gender = ref('');
const phone = ref('');
const position = ref('');
const email = ref('');
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

const toggleMode = () => {
  isRegister.value = !isRegister.value;
};

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    showAlert('请补全用户名和密码', 'warning');
    return;
  }
  if (isRegister.value) {
    if (!nickname.value.trim()) {
      showAlert('请填写昵称', 'warning');
      return;
    }
    if (!gender.value) {
      showAlert('请选择性别', 'warning');
      return;
    }
    if (!/^1[3-9]\d{9}$/.test(phone.value.trim())) {
      showAlert('请输入正确的 11 位手机号', 'warning');
      return;
    }
  }
  loading.value = true;
  try {
    if (isRegister.value) {
      await http.post('/api/v1/auth/register', {
        username: username.value.trim(),
        password: password.value,
        nickname: nickname.value.trim(),
        gender: gender.value,
        phone: phone.value.trim(),
        position: position.value.trim(),
        email: email.value.trim()
      });
      showAlert('注册成功，请登录', 'success', '成功');
      isRegister.value = false; // 保留已填用户名, 方便直接登录
    } else {
      const res: any = await http.post('/api/v1/auth/login', { username: username.value, password: password.value });
      userStore.setToken(res.token, res.user?.username || username.value, res.user?.nickname || '');
      router.push('/');
    }
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

.req {
  color: #e11d48;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-group.half {
  flex: 1;
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

/* 性别选择 */
.gender-row {
  display: flex;
  gap: 10px;
}

.gender-opt {
  flex: 1;
  height: 44px;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  background: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.gender-opt.male.active {
  border-color: #0284c7;
  background: #e0f2fe;
  color: #0369a1;
}

.gender-opt.female.active {
  border-color: #ec4899;
  background: #fce7f3;
  color: #be185d;
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

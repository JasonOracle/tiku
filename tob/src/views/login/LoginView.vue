<!--
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：纯手机号登录直连统一接口，初始化超管按钮已删除（改走种子脚本）]
-->
<template>
  <div class="login-container">
    <div class="glass-card">
      <div class="header">
        <div class="logo-badge">TiKu</div>
        <h2>智题库 SaaS 管理后台</h2>
        <p>Aero Glass Modern Admin Panel</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <div class="btn-group">
          <el-button type="primary" class="submit-btn" :loading="loading" @click="handleLogin">
            立即登录
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import request from '../../utils/request';
import { useUserStore } from '../../store/user';

const router = useRouter();
const userStore = useUserStore();
const formRef = ref<FormInstance>();
const loading = ref(false);

const form = reactive({
  phone: '',
  password: ''
});

const rules = {
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
};

const handleLogin = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return;
    loading.value = true;
    try {
      const res: any = await request.post('/api/v1/auth/login', {
        phone: form.phone,
        password: form.password,
      });
      userStore.applyLoginPayload(res);
      ElMessage.success('登录成功');
      if (userStore.isSuperAdmin) router.push('/super-admin/tenants');
      else router.push('/');
    } finally {
      loading.value = false;
    }
  });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0284c7 0%, #38bdf8 50%, #818cf8 100%);
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, -apple-system, sans-serif;
}

.glass-card {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 20px 40px rgba(2, 132, 199, 0.15);
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-badge {
  display: inline-block;
  background: linear-gradient(135deg, #0284c7, #38bdf8);
  color: white;
  font-weight: 800;
  font-size: 14px;
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.header h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
  font-weight: 700;
}

.header p {
  margin: 6px 0 0;
  font-size: 13px;
  color: #64748b;
}

.btn-group {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.submit-btn {
  flex: 2;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
  height: 44px;
  border-radius: 12px;
  font-weight: 600;
}

.init-btn {
  flex: 1;
  height: 44px;
  border-radius: 12px;
}
</style>

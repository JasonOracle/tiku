/**
 * [变更日志]
 * 修改时间：2026-09-08
 * AI模型：Gemini 系列
 * 修改内容：[userStore扩充个人资料字段(name, gender, position, bio, phone, email)并在loadProfile中同步]
 * 修改时间：2026-09-06 20:00:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2 RBAC: 增加 role 与今日 AI 额度余额 (loadProfile 从 /admin/auth/me 拉取)]
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import request from '../utils/request';

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('tiku_tob_token') || '');
  const username = ref<string>(localStorage.getItem('tiku_tob_username') || '');
  const role = ref<string>(localStorage.getItem('tiku_tob_role') || 'admin');
  const quotaRemaining = ref<number>(0);
  const quotaLimit = ref<number>(0);
  const name = ref<string>('');
  const gender = ref<string>('');
  const position = ref<string>('');
  const bio = ref<string>('');
  const phone = ref<string>('');
  const email = ref<string>('');

  const isSuper = () => role.value === 'super_admin';

  function setToken(newToken: string, loginUsername: string, newRole?: string) {
    token.value = newToken;
    username.value = loginUsername;
    if (newRole) role.value = newRole;
    localStorage.setItem('tiku_tob_token', newToken);
    localStorage.setItem('tiku_tob_username', loginUsername);
    if (newRole) localStorage.setItem('tiku_tob_role', newRole);
  }

  async function loadProfile() {
    try {
      const res: any = await request.get('/api/v1/admin/auth/me');
      if (res) {
        role.value = res.role || 'admin';
        quotaRemaining.value = res.daily_ai_quota || 0;
        quotaLimit.value = res.ai_quota_limit || 0;
        name.value = res.name || '';
        gender.value = res.gender || '';
        position.value = res.position || '';
        bio.value = res.bio || '';
        phone.value = res.phone || '';
        email.value = res.email || '';
        localStorage.setItem('tiku_tob_role', role.value);
      }
    } catch (e) {
      /* 未登录或接口异常时静默 */
    }
  }

  function logout() {
    token.value = '';
    username.value = '';
    role.value = 'admin';
    name.value = '';
    gender.value = '';
    position.value = '';
    bio.value = '';
    phone.value = '';
    email.value = '';
    localStorage.removeItem('tiku_tob_token');
    localStorage.removeItem('tiku_tob_username');
    localStorage.removeItem('tiku_tob_role');
  }

  return {
    token,
    username,
    role,
    quotaRemaining,
    quotaLimit,
    name,
    gender,
    position,
    bio,
    phone,
    email,
    isSuper,
    setToken,
    loadProfile,
    logout
  };
});


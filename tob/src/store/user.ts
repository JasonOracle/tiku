/**
 * [变更日志]
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

  const isSuper = () => role.value === 'super_admin';

  function setToken(newToken: string, name: string, newRole?: string) {
    token.value = newToken;
    username.value = name;
    if (newRole) role.value = newRole;
    localStorage.setItem('tiku_tob_token', newToken);
    localStorage.setItem('tiku_tob_username', name);
    if (newRole) localStorage.setItem('tiku_tob_role', newRole);
  }

  async function loadProfile() {
    try {
      const res: any = await request.get('/api/v1/admin/auth/me');
      role.value = res.role || 'admin';
      quotaRemaining.value = res.daily_ai_quota || 0;
      quotaLimit.value = res.ai_quota_limit || 0;
      localStorage.setItem('tiku_tob_role', role.value);
    } catch (e) {
      /* 未登录或接口异常时静默 */
    }
  }

  function logout() {
    token.value = '';
    username.value = '';
    role.value = 'admin';
    localStorage.removeItem('tiku_tob_token');
    localStorage.removeItem('tiku_tob_username');
    localStorage.removeItem('tiku_tob_role');
  }

  return { token, username, role, quotaRemaining, quotaLimit, isSuper, setToken, loadProfile, logout };
});

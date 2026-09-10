/**
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[多租户扩展：成员端持久化 tenantId，废除开放注册后的静默登录适配]
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('toc_user', () => {
  const token = ref<string>(localStorage.getItem('tiku_toc_token') || '');
  const username = ref<string>(localStorage.getItem('tiku_toc_username') || '');
  const nickname = ref<string>(localStorage.getItem('tiku_toc_nickname') || '');
  const tenantId = ref<string>(localStorage.getItem('tiku_toc_tenant') || '');
  const joinedTenants = ref<any[]>([]);

  function setToken(newToken: string, name: string, newNickname?: string) {
    token.value = newToken;
    username.value = name;
    if (newNickname !== undefined) nickname.value = newNickname;
    localStorage.setItem('tiku_toc_token', newToken);
    localStorage.setItem('tiku_toc_username', name);
    if (newNickname !== undefined) localStorage.setItem('tiku_toc_nickname', newNickname || '');
  }

  function setTenant(tid: string | number) {
    tenantId.value = String(tid || '');
    if (tid) localStorage.setItem('tiku_toc_tenant', String(tid));
    else localStorage.removeItem('tiku_toc_tenant');
  }

  function applyLoginPayload(res: any) {
    const u = res?.user || {};
    if (res?.token) setToken(res.token, u.phone || u.username || '', u.display_name || u.nickname || '');
    if (Array.isArray(res?.joined_tenants)) joinedTenants.value = res.joined_tenants;
    if (res?.default_tenant_id) setTenant(res.default_tenant_id);
  }

  function setNickname(newNickname: string) {
    nickname.value = newNickname;
    localStorage.setItem('tiku_toc_nickname', newNickname || '');
  }

  function logout() {
    token.value = '';
    username.value = '';
    nickname.value = '';
    tenantId.value = '';
    joinedTenants.value = [];
    localStorage.removeItem('tiku_toc_token');
    localStorage.removeItem('tiku_toc_username');
    localStorage.removeItem('tiku_toc_nickname');
    localStorage.removeItem('tiku_toc_tenant');
  }

  return { token, username, nickname, tenantId, joinedTenants, setToken, setTenant, applyLoginPayload, setNickname, logout };
});

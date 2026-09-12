/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：OpenCode / DeepSeek
 * 修改内容：[权限隔离重构：修复登录角色从未写入的缺陷——role 改为从 joined_tenants 按默认租户推导（旧代码读已废弃的 res.admin.role，导致 role 永远落默认值 'admin'，RBAC 路由守卫形同虚设）；super 标记改用 user.is_super_admin 判定，避免超管登录被误判为普通管理员]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[多租户扩展：新增 tenantId/joinedTenants/上帝模式，上线 X-Tenant-ID 持久化]
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import request from '../utils/request';

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('tiku_tob_token') || '');
  const username = ref<string>(localStorage.getItem('tiku_tob_username') || '');
  const role = ref<string>(localStorage.getItem('tiku_tob_role') || 'admin');
  const name = ref<string>('');
  const nickname = ref<string>('');
  const gender = ref<string>('');
  const position = ref<string>('');
  const occupation = ref<string>('');
  const bio = ref<string>('');
  const phone = ref<string>('');
  const email = ref<string>('');
  const age = ref<number | null>(null);
  const tenantId = ref<string>(localStorage.getItem('tiku_tob_tenant') || '');
  const joinedTenants = ref<any[]>([]);
  const isSuperAdmin = ref<boolean>(localStorage.getItem('tiku_tob_super') === '1');

  const isSuper = () => role.value === 'super_admin' || isSuperAdmin.value;

  function setTenant(tid: string | number) {
    tenantId.value = String(tid || '');
    if (tid) localStorage.setItem('tiku_tob_tenant', String(tid));
    else localStorage.removeItem('tiku_tob_tenant');
  }

  function setToken(newToken: string, loginUsername: string, newRole?: string) {
    token.value = newToken;
    username.value = loginUsername;
    if (newRole) role.value = newRole;
    localStorage.setItem('tiku_tob_token', newToken);
    localStorage.setItem('tiku_tob_username', loginUsername);
    if (newRole) localStorage.setItem('tiku_tob_role', newRole);
  }

  function applyLoginPayload(res: any) {
    // 新契约 {token,user,default_tenant_id,joined_tenants}；user 无 username 字段时用手机/展示名兜底
    const admin = res?.admin || {};
    const user = res?.user || {};
    const joined: any[] = Array.isArray(res?.joined_tenants) ? res.joined_tenants : [];
    // 角色必须从 joined_tenants 按默认租户推导：旧代码读已废弃的 res.admin.role，导致 role 永远落默认值 'admin'
    const current = joined.find((t: any) => String(t.tenant_id) === String(res?.default_tenant_id)) || joined[0];
    const loginRole = user.is_super_admin ? 'super_admin' : (admin.role || current?.role || '');
    if (res?.token) {
      setToken(res.token, admin.username || user.phone || user.display_name || '', loginRole || undefined);
    }
    const superFlag = user.is_super_admin ?? admin.is_super_admin ?? false;
    if (superFlag) {
      isSuperAdmin.value = true;
      localStorage.setItem('tiku_tob_super', '1');
      role.value = 'super_admin';
      localStorage.setItem('tiku_tob_role', 'super_admin');
    } else {
      isSuperAdmin.value = false;
      localStorage.removeItem('tiku_tob_super');
    }
    if (joined.length) joinedTenants.value = joined;
    // 上帝无默认租户：必须清掉残留视察企业，强制重新选择（否则会带着旧头进错企业）
    if (res?.default_tenant_id) setTenant(res.default_tenant_id);
    else setTenant('');
  }

  async function loadProfile() {
    try {
      const res: any = await request.get('/api/v1/auth/me');
      if (res) {
        if (res.role && res.role !== 'super') {
          role.value = res.role;
          localStorage.setItem('tiku_tob_role', role.value);
        } else if (res.is_super_admin) {
          role.value = 'super_admin';
          localStorage.setItem('tiku_tob_role', 'super_admin');
        }
        isSuperAdmin.value = !!res.is_super_admin;
        if (isSuperAdmin.value) localStorage.setItem('tiku_tob_super', '1');
        else localStorage.removeItem('tiku_tob_super');
        name.value = res.display_name || '';
        nickname.value = res.nickname || '';
        gender.value = res.gender || '';
        occupation.value = res.occupation || '';
        position.value = res.occupation || '';
        bio.value = res.bio || '';
        email.value = res.email || '';
        age.value = (res.age ?? null) as number | null;
        phone.value = res.phone || '';
        if (Array.isArray(res.joined_tenants)) joinedTenants.value = res.joined_tenants;
      }
    } catch (e) {
      /* 未登录或接口异常时静默 */
    }
  }

  function logout() {
    token.value = '';
    username.value = '';
    role.value = 'admin';
    tenantId.value = '';
    joinedTenants.value = [];
    isSuperAdmin.value = false;
    name.value = '';
    nickname.value = '';
    gender.value = '';
    position.value = '';
    occupation.value = '';
    bio.value = '';
    phone.value = '';
    email.value = '';
    age.value = null;
    localStorage.removeItem('tiku_tob_token');
    localStorage.removeItem('tiku_tob_username');
    localStorage.removeItem('tiku_tob_role');
    localStorage.removeItem('tiku_tob_tenant');
    localStorage.removeItem('tiku_tob_super');
  }

  return {
    token,
    username,
    role,
    tenantId,
    joinedTenants,
    isSuperAdmin,
    name,
    nickname,
    gender,
    position,
    occupation,
    bio,
    phone,
    email,
    age,
    isSuper,
    setToken,
    applyLoginPayload,
    setTenant,
    loadProfile,
    logout
  };
});


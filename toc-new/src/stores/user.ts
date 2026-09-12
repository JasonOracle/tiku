import { defineStore } from "pinia";

/** 登录返回的用户资料，与后端 POST /api/v1/auth/login 响应中的 data.user 逐字段对齐 */
export interface LoginUser {
  id: number;
  phone: string;
  display_name: string;
  is_super_admin: boolean;
}

/** 当前用户已加入的租户及其在该租户下的角色 */
export interface JoinedTenant {
  tenant_id: number;
  tenant_name: string;
  role: string;
}

/** 使用 type 而非 interface，保证满足 Pinia 持久化插件对 StateTree 索引签名的约束 */
type UserState = {
  token: string;
  userInfo: LoginUser | null;
  /** 当前生效的租户标识，取自登录响应的 default_tenant_id */
  tenantId: number | null;
  /** 已加入的租户列表，为后续多租户切换预留 */
  joinedTenants: JoinedTenant[];
};

export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    token: "",
    userInfo: null,
    tenantId: null,
    joinedTenants: [],
  }),
  getters: {
    /** 登录态唯一判据：token 非空 */
    isLoggedIn: (state): boolean => state.token !== "",
  },
  actions: {
    /**
     * 登录成功后写入凭证与租户上下文。
     * 后端不返回角色的顶层字段，角色来自 joined_tenants 中命中当前 tenantId 的那一项。
     */
    setLogin(payload: {
      token: string;
      user: LoginUser;
      default_tenant_id: number | null;
      joined_tenants: JoinedTenant[];
    }): void {
      this.token = payload.token;
      this.userInfo = payload.user;
      this.tenantId = payload.default_tenant_id ?? null;
      this.joinedTenants = payload.joined_tenants ?? [];
    },
    /** 切换生效租户，未加入的租户不接受 */
    setTenant(tenantId: number): void {
      if (!this.joinedTenants.some((t) => t.tenant_id === tenantId)) return;
      this.tenantId = tenantId;
    },
    /** 退出登录或登录态失效（401）时清空全部凭证 */
    clearAuth(): void {
      this.token = "";
      this.userInfo = null;
      this.tenantId = null;
      this.joinedTenants = [];
    },
  },
  // 开启持久化，应用重启后自动恢复登录态
  persist: true,
});

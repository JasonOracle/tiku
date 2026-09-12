import { request } from "@/utils/request";
import type { JoinedTenant, LoginUser } from "@/stores/user";

/**
 * 登录入参。
 * 注意：后端 backend/app/api/v1/auth.py 读取的是 phone / password，
 * 不存在 username 字段，传 username 会直接命中「请输入手机号与密码」400。
 */
export type LoginParams = {
  phone: string;
  password: string;
};

/** 登录返回体，与后端 login 接口响应中的 data 逐字段对齐 */
export type LoginResult = {
  token: string;
  user: LoginUser;
  /** 默认生效租户，无有效租户时为 null */
  default_tenant_id: number | null;
  /** 该账号已加入的全部租户及角色 */
  joined_tenants: JoinedTenant[];
};

/** 账号密码登录：POST /api/v1/auth/login */
export function login(params: LoginParams): Promise<LoginResult> {
  return request<LoginResult>({
    url: "/api/v1/auth/login",
    method: "POST",
    data: params,
    // 登录失败的文案由登录页自行呈现，避免与页面内提示重复弹出
    showError: false,
  });
}

/**
 * [变更日志]
 * 修改时间：2026-09-13
 * AI模型：Gemini 系列
 * 修改内容：[1. 增加环境自适应 baseURL 判定：在 Cloudflare Pages (pages.dev) 线上环境下自动直连 https://tiku-api.vercel.app 后端，本地或自建网关保持相对路径; 2. 彻底打通云端直连 Vercel 真实接口与鉴权]
 */
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 业务成功码判定由固定 200 放宽为 2xx 区间，兼容新增类接口返回的 201（如添加题目收藏）]
 */
import { useUserStore } from "@/stores/user";
import { useGlobalToast } from "@/stores/toast";

/** 自动解析后端 baseURL：线上 pages.dev 域名直接连 Vercel 后端 */
function getApiBaseUrl(): string {
  if (typeof window !== "undefined" && window.location.hostname.endsWith("pages.dev")) {
    return "https://tiku-api.vercel.app";
  }
  return "";
}

/** 后端统一响应包裹结构，参见 backend/app/api/saas/tasks.py 的返回约定 */
export interface ApiEnvelope<T> {
  code: number;
  message?: string;
  data: T;
}

export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

export interface RequestOptions {
  /** 相对路径或绝对路径，必须以 /api/v1 开头 */
  url: string;
  method?: HttpMethod;
  /** GET 走查询串，POST/PUT 走 JSON 体 */
  data?: Record<string, unknown>;
  header?: Record<string, string>;
  /** 业务失败时是否自动轻提示，默认开启；需要自行处理错误的场景可关闭 */
  showError?: boolean;
}

/**
 * 业务成功码的判定区间。
 * 后端新增类接口（如添加题目收藏 POST /member/favorites）返回 code 为 201，
 * 若只认 200 会把这类成功响应误判为业务失败并弹出错误提示，故按 2xx 区间判定。
 */
const SUCCESS_CODE_MIN = 200;
const SUCCESS_CODE_MAX = 300;
/** 登录页路径，401 后统一回落到此 */
const LOGIN_PAGE = "/pages/login/index";

/** 读取当前栈顶页面路由，用于阻止在登录页重复触发 401 跳转 */
function currentRoute(): string {
  const pages = getCurrentPages();
  const page = pages[pages.length - 1] as unknown as { route?: string } | undefined;
  return page?.route ? `/${page.route}` : "";
}

/** 401 统一处置：清空登录态并回登录页 */
function handleUnauthorized(): void {
  useUserStore().clearAuth();
  // 已经在登录页就不再重复跳转，否则会形成跳转死循环
  if (currentRoute() === LOGIN_PAGE) return;
  uni.reLaunch({ url: LOGIN_PAGE });
}

/**
 * 统一网络请求底座。
 * 负责三件事：注入登录凭证与租户标识、按后端业务码判定成败、失败时以轻提示告知用户。
 * 成功时直接返回业务 data，调用方拿到的是已剥离包裹层的类型化数据。
 */
export function request<T>(options: RequestOptions): Promise<T> {
  const { url, method = "GET", data, header = {}, showError = true } = options;

  // 必须在函数体内取用 Store：模块顶层取用会早于 app.use(pinia) 执行而抛异常
  const userStore = useUserStore();

  const finalHeader: Record<string, string> = {
    "Content-Type": "application/json",
    ...header,
  };
  if (userStore.token) {
    finalHeader.Authorization = `Bearer ${userStore.token}`;
  }
  if (userStore.tenantId !== null) {
    finalHeader["X-Tenant-Id"] = String(userStore.tenantId);
  }

  const fullUrl = url.startsWith("http") ? url : `${getApiBaseUrl()}${url}`;

  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: fullUrl,
      method,
      data,
      header: finalHeader,
      success: (res) => {
        const statusCode = res.statusCode;

        // 登录态失效：清凭证 + 回登录页，不再提示业务文案
        if (statusCode === 401) {
          handleUnauthorized();
          reject(new Error("登录状态已失效，请重新登录"));
          return;
        }

        if (statusCode < 200 || statusCode >= 300) {
          // 后端 FastAPI 抛出的 HTTPException 结构为 { detail }，业务接口的业务码结构为 { code, message }，
          // 两者都要能取到真实原因，否则登录失败会被吞成「服务异常（400）」
          const errorBody = res.data as { detail?: unknown; message?: unknown } | undefined;
          const detail = typeof errorBody?.detail === "string" ? errorBody.detail : "";
          const message = detail || `服务异常（${statusCode}）`;
          if (showError) useGlobalToast().error(message);
          reject(new Error(message));
          return;
        }

        const body = res.data as ApiEnvelope<T> | undefined;
        if (!body || typeof body !== "object" || typeof body.code !== "number") {
          const message = "接口返回格式异常";
          if (showError) useGlobalToast().error(message);
          reject(new Error(message));
          return;
        }

        if (body.code < SUCCESS_CODE_MIN || body.code >= SUCCESS_CODE_MAX) {
          const message = body.message || "操作失败，请稍后重试";
          if (showError) useGlobalToast().error(message);
          reject(new Error(message));
          return;
        }

        resolve(body.data);
      },
      fail: (err) => {
        const message = "网络连接失败，请检查网络后重试";
        if (showError) useGlobalToast().error(message);
        reject(new Error(err?.errMsg || message));
      },
    });
  });
}

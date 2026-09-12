/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：OpenCode / DeepSeek
 * 修改内容：[权限隔离重构：B端登录统一注入 X-Client: admin 身份标识，供后端拦截纯学员(member)登录管理后台；C端使用独立 http.ts 不受影响]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[多租户透传：所有业务请求自动携带 X-Tenant-ID，登录接口除外]
 */
import axios from 'axios';
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { ElMessage } from 'element-plus';

// 环境自适应：线上 Cloudflare Pages 域名下直接请求 Vercel 后端（已开启完整 CORS）；本地开发或 Nginx 子路径走相对路径代理
const getBaseURL = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && window.location.hostname.endsWith('pages.dev')) {
    return 'https://tiku-api.vercel.app';
  }
  return '';
};

const request: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
});

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('tiku_tob_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // 多租户上下文透传（登录/初始化接口除外）
    const url = config.url || '';
    const isAuth = url.includes('/auth/login') || url.includes('/auth/init');
    // B 端身份声明：登录时显式携带 X-Client，后端据此拦截纯学员(member)登录管理后台
    if (url.includes('/auth/login') && config.headers) {
      (config.headers as any)['X-Client'] = 'admin';
    }
    if (!isAuth && config.headers) {
      const tid = localStorage.getItem('tiku_tob_tenant') || '';
      if (tid) (config.headers as any)['X-Tenant-ID'] = tid;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data;
    if (res && typeof res.code === 'number') {
      if (res.code !== 200 && res.code !== 201) {
        ElMessage.error(res.message || '请求处理失败');
        return Promise.reject(new Error(res.message || 'Error'));
      }
      return res.data;
    }
    return res;
  },
  (error) => {
    const detail = error.response?.data?.detail || '';
    const msg = detail || '网络开小差了，请稍后再试';
    if (error.response?.status === 401) {
      localStorage.removeItem('tiku_tob_token');
      window.location.href = '/admin/login';
      return Promise.reject(error);
    }
    // 缺租户上下文由路由守卫接管（一键跳转大盘），此处不再满屏弹红字
    if (detail.includes('X-Tenant-ID') || detail.includes('视察企业')) {
      return Promise.reject(error);
    }
    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default request;

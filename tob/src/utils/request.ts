/**
 * [变更日志]
 * 修改时间：2026-09-08
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. baseURL 优化：支持环境变量 VITE_API_BASE_URL，在 Cloudflare Pages 静态托管域名下自动直连 Vercel 后端，解决 200 重写导致的 405 Method Not Allowed]
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
    const msg = error.response?.data?.detail || '网络开小差了，请稍后再试';
    if (error.response?.status === 401) {
      localStorage.removeItem('tiku_tob_token');
      window.location.href = '/admin/login';
    }
    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default request;

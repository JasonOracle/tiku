/**
 * [变更日志]
 * 修改时间：2026-09-08
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. baseURL 优化：在 Cloudflare Pages 静态托管域名下自动直连 Vercel 后端，解决 200 重写导致的 POST 405 Method Not Allowed]
 */
import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// 环境自适应：线上 Cloudflare Pages 域名下直接请求 Vercel 后端；本地开发与 Nginx 环境使用相对路径
const getBaseURL = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined' && window.location.hostname.endsWith('pages.dev')) {
    return 'https://tiku-api.vercel.app';
  }
  return '';
};

const http: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
});

// 请求拦截器：注入 tiku_toc_token 隔绝 B端凭证
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('tiku_toc_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => Promise.reject(error)
);

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data;
    if (res && typeof res.code === 'number') {
      if (res.code !== 200 && res.code !== 201) {
        return Promise.reject(new Error(res.message || '请求失败'));
      }
      return res.data;
    }
    return res;
  },
  (error: any) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('tiku_toc_token');
    }
    return Promise.reject(error);
  }
);

export default http;

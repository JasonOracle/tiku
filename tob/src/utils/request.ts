import axios from 'axios';
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { ElMessage } from 'element-plus';

// 生产经 Nginx 同源代理 /api/v1/ → backend:8000；开发经 vite server.proxy 转发，统一用相对路径避免直连 8000 跨域/端口未映射
const request: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 10000,
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

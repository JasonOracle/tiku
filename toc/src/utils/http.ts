import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// 生产经 Nginx 同源代理 /api/v1/ → backend:8000；开发经 vite server.proxy 转发，统一用相对路径
const http: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 10000,
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

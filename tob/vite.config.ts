/**
 * [变更日志]
 * 修改时间：2026-09-08
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. base 改为优先取环境变量，默认使用 '/' 适配 Cloudflare Pages 独立域名部署，兼容 Nginx 子路径]
 * 修改时间：2026-09-03 22:29:17
 * AI模型：Gemini 底层
 * 修改内容：[1. 添加 base: '/admin/'，修复 Nginx /admin/ 子路径下资源 MIME 错误白屏问题]
 */
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  // 优先取环境变量 BASE_URL，独立域名（如 Cloudflare Pages/Vercel）下使用 '/'，Nginx 子路径下使用 '/admin/'
  base: process.env.VITE_BASE_URL || process.env.BASE_URL || '/',
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/uploads': 'http://127.0.0.1:8000'
    }
  }
});

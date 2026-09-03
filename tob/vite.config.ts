/**
 * [变更日志]
 * 修改时间：2026-09-03 22:29:17
 * AI模型：Gemini 底层
 * 修改内容：[1. 添加 base: '/admin/'，修复 Nginx /admin/ 子路径下资源 MIME 错误白屏问题]
 */
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  // base 设为 /admin/ 后，打包产物中所有 /assets/ 引用变为 /admin/assets/
  // 这样 Nginx alias 到 /admin/ 时资源路径完全匹配，不会 fallback 到 toc 的 index.html
  base: '/admin/',
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/uploads': 'http://127.0.0.1:8000'
    }
  }
});

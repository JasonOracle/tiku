/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 固定开发端口为 5174 并放开局域网访问; 2. 新增 /api/v1 与 /uploads 开发代理指向后端 8000; 3. 纠正 uni-app 工具链的软链接解析开关，修复 pnpm 布局下传递依赖解析失败]
 */
import { defineConfig, type Plugin } from "vite";
import uni from "@dcloudio/vite-plugin-uni";

/**
 * uni-app 工具链内置的解析器开启了 preserveSymlinks（保留软链接路径），
 * 而 pnpm 把传递依赖隔离在 .pnpm 目录内，导致 rollup 从 node_modules/<包>/ 出发
 * 无法向上找到自己依赖的模块（典型表现：pinia 的 @vue/devtools-api 解析失败）。
 * 该插件以 post 优先级最后合并配置，把开关纠正回 vite 默认值 false。
 */
const fixPnpmSymlinkResolve: Plugin = {
  name: "toc-fix-pnpm-symlink-resolve",
  enforce: "post",
  config: () => ({
    resolve: {
      preserveSymlinks: false,
    },
  }),
};

export default defineConfig({
  plugins: [uni(), fixPnpmSymlinkResolve],
  server: {
    // 与 B 端 5173、后端 8000 错开，避免端口碰撞
    port: 5174,
    host: "0.0.0.0",
    proxy: {
      // 统一网关前缀直连本地 FastAPI，前端无需处理跨域
      "/api/v1": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      // 后端静态上传资源同源转发，避免图片直连 8000 端口产生跨域
      "/uploads": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});

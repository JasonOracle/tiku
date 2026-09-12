/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 装配 Pinia 与持久化插件，保证纯 TS 模块可在运行时安全取用 Store]
 */
import { createSSRApp } from "vue";
import App from "./App.vue";
import { pinia } from "./stores";

export function createApp() {
  const app = createSSRApp(App);
  // 必须先装配 Pinia，request.ts 等纯 TS 模块才能在运行时取到已激活的 Store 实例
  app.use(pinia);
  return {
    app,
  };
}

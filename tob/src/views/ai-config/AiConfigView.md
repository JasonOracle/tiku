# AiConfigView AI 模型配置预留页

## 设计初衷

v1.3 预留管理员模型 API Key 配置界面。当前为**静态页**：配置仅保存在本机浏览器 `localStorage`，
不调用后端接口、不落库，供后续接服务端密钥管理时替换 `saveLocal` 实现即可。

## 权限

路由 `meta.roles: ['super_admin', 'admin']`，出题人不可见菜单，越权直访由全局守卫 Toast 拦截。

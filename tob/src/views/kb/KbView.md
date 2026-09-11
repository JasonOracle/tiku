# KbView 组件自说明文档

## 💡 核心思想

本组件是 B 端企业级知识库的核心视图，承载知识库范畴切换（公共/私人）、关键统计指标概览、文档列表管理及召回测试。
为了贯彻系统统一的列表设计语言：
1. **全局统一 CSS 控制**：全面复用 `list-layout.css` 中的 `saas-modern-table` 与全局卡片样式。
2. **去除生硬边框与立体弥散阴影**：表格外层卡片剔除 `border: 1px solid #e2e8f0`，采用多层柔和深浅立体投影（Elevated Island Shadow），带来轻盈、现代的科技质感。
3. **首行表头专属着色**：表格表头第 1 行采用 `#f1f5f9` 浅底色搭配 `#e2e8f0` 细分隔线，下方数据行保持全白底色，规避视觉繁复。

---

## 💻 使用示例

在后台路由中配置：

```ts
// router/index.ts
{
  path: 'kb',
  name: 'KnowledgeBase',
  component: () => import('@/views/kb/KbView.vue'),
  meta: { title: '知识库管理', requiresAuth: true }
}
```

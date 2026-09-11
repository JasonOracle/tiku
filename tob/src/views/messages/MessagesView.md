# MessagesView 组件自说明文档

## 💡 核心思想

本组件作为企业端站内信与通知中心列表，承载各类系统预警、阅卷任务与企业动态提醒。
全面遵照系统的列表设计统一规范：
1. **全局统一 CSS 控制**：复用 `list-layout.css`，无需各页面重复编写表格、外框或分页样式。
2. **轻量无硬边框与立体弥散阴影**：外层移除硬质灰色边框，通过立体弥散阴影带来柔和悬浮感。
3. **首行标题浅色背景**：表头仅第一行具备 `#f1f5f9` 浅色底，数据行全白呈现，阅读呼吸感好。

---

## 💻 使用示例

在路由配置中引用：

```ts
// router/index.ts
{
  path: 'messages',
  name: 'Messages',
  component: () => import('@/views/messages/MessagesView.vue'),
  meta: { title: '消息中心', requiresAuth: true }
}
```

# TenantMembersDrawer 组件自说明文档

## 💡 核心思想

本组件作为企业管理页面（超管视角）下的企业成员视察抽屉，支持快速查看各企业的成员组成、联系方式及角色权限。
遵照现代 SaaS 列表系统规范：
1. **全局统一 CSS 控制**：复用 `list-layout.css` 的 `saas-modern-table` 样式类。
2. **轻盈无硬边框与首行表头高亮**：表头仅第一行应用 `#f1f5f9` 浅色底与浅边框，数据行保持全白，去除传统内部重型边框。

---

## 💻 使用示例

在 `TenantsView.vue` 中作为抽屉子组件引用：

```vue
<TenantMembersDrawer
  v-model:visible="membersDrawerVisible"
  :tenant-id="selectedTenantId"
  :tenant-name="selectedTenantName"
  @enter-tenant="handleDirectEnter"
/>
```

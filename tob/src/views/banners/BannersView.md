# BannersView 组件自说明文档

## 💡 核心思想

本组件负责管理企业 C 端学员首页的轮播 Banner 图与跳转行为。
为保持全系统高质感统一设计，本组件接入全局统一的 `list-layout.css`：
1. **立体弥散阴影与去硬边框**：剔除传统厚重实线边框，使用多层浅色立体投影卡片包裹，呈现悬浮轻盈质感。
2. **第一行表头专属高亮**：表格第一行标题底色统一为 `#f1f5f9`，下边缘配置细分隔线 `#e2e8f0`，数据内容行保持全白底色，避免视觉层级杂乱。
3. **排版防变形控制**：针对 ID 列、跳转属性标签、排序等关键信息，保证标签字样 `white-space: nowrap` 不折行变形。

---

## 💻 使用示例

作为路由组件直接在后台路由系统挂载：

```ts
// router/index.ts
{
  path: 'banners',
  name: 'Banners',
  component: () => import('@/views/banners/BannersView.vue'),
  meta: { title: 'Banner 管理', requiresAuth: true }
}
```

# CategoriesView 组件自说明文档

## 💡 核心思想

`CategoriesView` 负责智题库 SaaS 系统的基础分类管理。遵循极简交互与扁平化原则：
1. **纯粹清晰的双维度分类**：
   - 「题目分类」：专门为资源库题海条目提供知识归类（`target_type='resource'`）。
   - 「试卷分类」：专门为任务测评与组卷场景提供业务归类（`target_type='task'`）。
2. **零阻力直观拖拽排序**：
   - 彻底废弃数字输入式的“排序权重”概念，采用原生 HTML5 `draggable` 机制，直接按住表格行或拖动把手即可上下直观拖动调序。
   - 拖拽松手后触发静默 API 保存（`PUT /api/v1/admin/categories/reorder`），所见即所得。
3. **极简化弹窗与首位自动置顶**：
   - 弹窗仅保留核心必填项“分类名称”，移除所有只读或多余字段。
   - 新增的分类自动赋予当前最小排序权重，保证新增项必定自动出现在列表最上方。

---

## 💻 使用示例

本页面作为一级路由页面使用，无需复杂传参：

```vue
<!-- 路由映射配置 -->
{
  path: '/categories',
  name: 'Categories',
  component: () => import('@/views/categories/CategoriesView.vue'),
  meta: { title: '分类配置', requiresAuth: true }
}
```

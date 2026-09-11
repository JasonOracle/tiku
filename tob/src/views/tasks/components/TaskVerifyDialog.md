# TaskVerifyDialog 组件自说明文档

## 💡 核心思想

本组件是任务列表页用于全屏打开特定试卷核验记录的核验大厅弹窗组件。
遵照现代 SaaS 列表系统规范：
1. **全局统一 CSS 控制**：复用 `list-layout.css` 的 `saas-modern-table` 样式类。
2. **轻盈无硬边框与首行表头高亮**：表头首行具备 `#f1f5f9` 浅色底，数据单元格具备轻微底划线，消除繁杂冗余的实线框。

---

## 💻 使用示例

在 `TasksView.vue` 中调用：

```vue
<TaskVerifyDialog
  v-model:visible="verifyDialogVisible"
  :task-id="currentTaskId"
  :task-title="currentTaskTitle"
/>
```

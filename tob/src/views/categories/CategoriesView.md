# CategoriesView 分类配置视图组件文档

## 💡 核心思想
实现题目分类与试卷分类双维度资产树维护，支持原生表格行上下物理拖拽调序并实时持久化：

1. **统一接入企业级 SaaS 列表设计体系（list-layout.css）**：
   - **悬浮弥散卡片**：去除机械硬边框，通过复合弥散柔和阴影呈现浮岛质感。
   - **首行表头专属底色**：仅第1行表头配置清爽淡蓝灰（`#f1f5f9`）与 1px 微分隔线，下方数据行保持纯净全白通透平铺。
   - **防止文字折行**：把手图标列（60px）、ID 列（80px）、分类名称列（min-width 260px）、操作列（160px）弹性排布。
   - **微组件与状态指示**：
     - 新建按钮统一为深蓝实体微阴影按键；
     - 操作列整合为「编辑 / 删除」轻量平铺彩色文本链接。

---

## 💻 使用示例
```vue
<template>
  <CategoriesView />
</template>

<script setup lang="ts">
import CategoriesView from './CategoriesView.vue';
</script>
```

# QuestionsView 题海管理视图组件文档

## 💡 核心思想
实现 B 端全站题海库的统一 CRUD 管理。支持按分类、题型、难度和关键字筛选，具备中文难度映射（简单/中等/困难），以及设置题目默认分值（Score）。提供标准的 Excel 模板批量导入功能以及 ✨ AI 智能出题功能。

在 ✨ AI 出题模态框中：
1. 顶部表单第一项必须指定**「所属分类」**（必选项，默认选中当前视图有效分类）。
2. 高级选项中**「题目数量」**允许输入范围为 **`1 ~ 10`**。
3. 当数量设置为 1 (或 $N < \text{题型数}$) 且勾选多题型时，优先以数量 $N$ 为准并智能切片截取前 $N$ 个题型向 AI 发起硬性规范要求。

## 💻 使用示例
```vue
<template>
  <QuestionsView />
</template>

<script setup lang="ts">
import QuestionsView from './QuestionsView.vue';
</script>
```

# VerificationView 阅卷管理视图组件文档

## 💡 核心思想
实现主客观题分离式智能评阅、大模型 AI 助考预审与可视化人工终审抽屉：

1. **统一接入企业级 SaaS 列表设计体系（list-layout.css）**：
   - **悬浮弥散卡片**：去除机械硬边框，通过复合弥散柔和阴影呈现浮岛质感。
   - **首行表头专属底色**：仅第1行表头配置清爽淡蓝灰（`#f1f5f9`）与 1px 微分隔线，下方数据行保持纯净全白通透平铺。
   - **防止文字折行**：记录 ID（90px）、试卷名称（240px）、交卷时间（170px）、AI 预判（240px）、操作列（220px）精准定标。
   - **微组件与状态指示**：
     - AI 预判得分采用柔和薄荷绿胶囊；
     - 操作列提供「亮橙渐变实体胶囊（进入批阅）」与「✨ AI 助考分析」文字按钮。

---

## 💻 使用示例
```vue
<template>
  <VerificationView />
</template>

<script setup lang="ts">
import VerificationView from './VerificationView.vue';
</script>
```

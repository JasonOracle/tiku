# VerifyDrawer 试卷人工批阅抽屉组件文档

## 💡 核心思想
在试卷管理列表中，当试卷存在待核验或待批阅作答时，提供**行内原地滑出**的轻量化批阅抽屉（`VerifyDrawer`），免除页面跳转成本：

1. **统一语境与专业Tag标识**：
   - 将原有历史遗留的“任务核验”重构为 **「试卷人工批阅」蓝色微光 Tag 徽章 + 试卷标题** 双层级排版，主次分明、专业醒目，彻底告别普通黑字串联。
2. **内联实体高亮「✨ AI 帮我分析」按钮**：
   - 标题栏右侧升级为**橙红渐变实体质感操作按钮**（搭配白色纯正 SVG 矢量星光微标），配备明确的物理浮雕阴影与点击/Hover 微动效，一眼即可识别为核心操作入口；
   - 支持当前作答实时调用大模型完成评分预判，自动就地刷新建议分与详细采分理由。
3. **流水线批量批改**：
   - 顶部提供 `第 X / Y 份` 动态进度条，点击「✔ 确认定分」后自动将当前作答出队并无缝进入下一份，批阅完毕后自动关闭抽屉并通知外层列表更新角标。

---

## 💻 使用示例
```vue
<template>
  <VerifyDrawer
    :visible="gradingVisible"
    :task-id="gradingExam?.id ?? null"
    :task-title="gradingExam?.title ?? ''"
    @update:visible="gradingVisible = $event"
    @graded="handleGraded"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import VerifyDrawer from './components/VerifyDrawer.vue';

const gradingVisible = ref(false);
const gradingExam = ref<any>({ id: 33, title: '近代物理试卷' });

const handleGraded = () => {
  // 刷新外层列表
};
</script>
```

# QuizView 答题引擎视图组件文档

## 💡 核心思想
移动端 C 端刷题与测评核心引擎。融入 MBTI 经典拟物卡片 UI 设计（顶部蓝紫渐变悬挂饰条、内部大号数字与极简进度条融合），具备限时倒计时定时器清理逻辑（防止内存泄漏）、练习模式无倒计时作答、上一题自由返回修改答案，以及选项平滑刷色填充选中特效。

## 💻 使用示例
```vue
<template>
  <QuizView />
</template>

<script setup lang="ts">
import QuizView from './views/quiz/QuizView.vue';
</script>
```


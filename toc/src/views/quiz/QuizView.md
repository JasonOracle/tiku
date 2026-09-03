# QuizView 答题引擎视图组件文档

## 💡 核心思想
移动端 C端刷题与测评核心引擎。具备顶部毛玻璃进度条、限时倒计时定时器清理逻辑（防止内存泄漏）、练习模式无倒计时作答、上一题自由返回修改答案，以及题目一键加入/移出收藏夹。

## 💻 使用示例
```vue
<template>
  <QuizView />
</template>

<script setup lang="ts">
import QuizView from './views/quiz/QuizView.vue';
</script>
```

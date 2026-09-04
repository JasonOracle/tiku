<!--
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[1. 移除额外添加的背景颜色，恢复直接渲染原版矢量 SVG 图片]
-->
<template>
  <div class="cover-art" :style="{ width, height }">
    <img v-if="isUrl" :src="cover" alt="封面" />
    <img v-else :src="src" alt="封面" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { presetSrc } from '../assets/covers/index';

const props = withDefaults(defineProps<{ cover?: string | null; width?: string; height?: string }>(), {
  cover: 'preset:1',
  width: '100%',
  height: '100%'
});

const isUrl = computed(() => !!props.cover && !props.cover.startsWith('preset:'));
const src = computed(() => presetSrc(props.cover));
</script>

<style scoped>
.cover-art {
  overflow: hidden;
  border-radius: 12px;
}

.cover-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>

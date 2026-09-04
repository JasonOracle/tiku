<!-- 试卷封面：preset:1..5 渲染内置SVG，其余按图片URL显示 -->
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
.cover-art { overflow: hidden; border-radius: 8px; }
.cover-art img { width: 100%; height: 100%; object-fit: cover; display: block; }
</style>

/**
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[1. 增加 immersive 属性与 dynamic 动态滚动透明度/配色切换; 2. 优化过渡动画]
 */
<template>
  <header 
    class="nav-bar" 
    :class="{ 
      'is-immersive': immersive,
      'is-scrolled': isScrolled 
    }"
  >
    <button class="nav-back" @click="goBack">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>
    <span class="nav-title">{{ title }}</span>
    <!-- 右侧插槽：预留给收藏按钮等 -->
    <span class="nav-right">
      <slot name="right" />
    </span>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

interface Props {
  title?: string;
  /** 是否开启沉浸式（未滚动时背景透明） */
  immersive?: boolean;
  /** 滚动触发白底效果的阈值(px)，默认 30 */
  scrollThreshold?: number;
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  immersive: false,
  scrollThreshold: 30
});

const router = useRouter();
const isScrolled = ref(false);

const handleScroll = () => {
  if (!props.immersive) return;
  isScrolled.value = window.scrollY > props.scrollThreshold;
};

onMounted(() => {
  if (props.immersive) {
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // 初始校验
  }
});

onUnmounted(() => {
  if (props.immersive) {
    window.removeEventListener('scroll', handleScroll);
  }
});

/** 统一返回：优先浏览器历史回退，无历史时回首页 */
const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push('/');
  }
};
</script>

<style scoped>
.nav-bar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  transition: background-color 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              border-color 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.25s cubic-bezier(0.4, 0, 0.2, 1),
              color 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  color: #0f172a;
}

/* 沉浸模式样式（未滚动时） */
.nav-bar.is-immersive:not(.is-scrolled) {
  background: transparent;
  backdrop-filter: blur(0px);
  -webkit-backdrop-filter: blur(0px);
  border-bottom-color: transparent;
  box-shadow: none;
}

/* 沉浸模式样式（已滚动） */
.nav-bar.is-immersive.is-scrolled {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.nav-back {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  border-radius: 10px;
  flex-shrink: 0;
  transition: color 0.25s ease, background-color 0.25s ease;
}

.nav-back:active {
  background: rgba(0, 0, 0, 0.06);
}

.nav-title {
  flex: 1;
  text-align: center;
  font-size: 17px;
  font-weight: 700;
  color: inherit;
  /* 用 margin-right 负值补偿左侧按钮宽度，使标题视觉居中 */
  margin-right: -36px;
  transition: color 0.25s ease;
}

.nav-right {
  width: 36px;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  color: inherit;
}
</style>

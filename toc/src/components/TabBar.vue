/**
 * [变更日志]
 * 修改时间：2026-09-04
 * AI模型：Gemini 系列
 * 修改内容：[v1.2: TabBar 新增「我的测试」项 (三态过滤: 进行中/未开始/已考试)]
 */
<!-- C端公共浮动TabBar：首页 / 我的测试 / 个人中心 -->
<template>
  <footer class="tabbar">
    <button class="tab-item" :class="{ active: active === 'home' }" @click="router.push('/')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
      </svg>
      <span>首页</span>
    </button>
    <button class="tab-item" :class="{ active: active === 'mytasks' }" @click="router.push('/my-tasks')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 11l3 3L22 4"></path>
        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
      </svg>
      <span>我的测试</span>
    </button>
    <button class="tab-item" :class="{ active: active === 'profile' }" @click="router.push('/profile')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
      <span>个人中心</span>
    </button>
  </footer>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

withDefaults(defineProps<{ active?: 'home' | 'mytasks' | 'profile' }>(), { active: 'home' });
const router = useRouter();
</script>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 32px);
  max-width: 448px;
  /* 对齐 zbzn 晶体毛玻璃规范：60% 折射渐变背景 */
  background: linear-gradient(180deg, rgba(245, 245, 245, 0.65) 0%, rgba(255, 255, 255, 0.65) 100%);
  /* 核心毛玻璃模糊 + 饱和度 */
  backdrop-filter: blur(8px) saturate(120%) brightness(100%);
  -webkit-backdrop-filter: blur(8px) saturate(120%) brightness(100%);
  border-radius: 60px;
  /* zbzn 顶级玻璃光影：内高光 + 悬浮阴影 */
  box-shadow:
    inset 1px 1px 0 rgba(255, 255, 255, 0.9),
    0 -10px 25px 0 rgba(0, 0, 0, 0.06),
    0 8px 20px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  padding: 8px 12px;
  z-index: 100;
  box-sizing: border-box;
}

.tab-item {
  flex: 1;
  background: transparent;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: #1a1a1a;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 0;
  border-radius: 40px;
  transition: all 0.25s ease;
}

.tab-item.active {
  color: #0062ff;
  font-weight: 700;
  background: rgba(26, 26, 26, 0.06);
}

.tab-item.active svg {
  filter: drop-shadow(0 2px 6px rgba(0, 98, 255, 0.35));
}
</style>

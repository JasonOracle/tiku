<!-- C端公共浮动TabBar：首页 / 个人中心 -->
<template>
  <footer class="tabbar">
    <button class="tab-item" :class="{ active: active === 'home' }" @click="router.push('/')">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
      </svg>
      <span>首页</span>
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

withDefaults(defineProps<{ active?: 'home' | 'profile' }>(), { active: 'home' });
const router = useRouter();
</script>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 32px);
  max-width: 448px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  box-shadow: 0 8px 28px rgba(2, 132, 199, 0.12);
  display: flex;
  padding: 8px 0 10px;
  z-index: 100;
}
.tab-item {
  flex: 1;
  background: transparent;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  color: #94a3b8;
  font-size: 12px;
  cursor: pointer;
}
.tab-item.active { color: #0284c7; font-weight: 700; }
.tab-item.active svg { filter: drop-shadow(0 2px 6px rgba(2, 132, 199, 0.4)); }
</style>

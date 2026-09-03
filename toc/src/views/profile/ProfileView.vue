<!--
 * [变更日志]
 * 修改时间：2026-09-04 00:08:00
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现 C 端移动端个人中心: 精美 SVG 头像、仪表盘作答统计卡片(场次/通过率)与 Cell 项层级跳转]
-->
<template>
  <div class="profile-container">
    <!-- 顶部用户 Profile 卡片 -->
    <div class="user-card glass-panel">
      <div class="avatar-box">
        <svg class="avatar-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="50" cy="50" r="48" fill="url(#avatar-grad)" stroke="white" stroke-width="4"/>
          <path d="M50 30C57.732 30 64 36.268 64 44C64 51.732 57.732 58 50 58C42.268 58 36 51.732 36 44C36 36.268 42.268 30 50 30Z" fill="white"/>
          <path d="M26 78C26 65.8497 36.7452 56 50 56C63.2548 56 74 65.8497 74 78V82H26V78Z" fill="white" fill-opacity="0.9"/>
          <defs>
            <linearGradient id="avatar-grad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
              <stop stop-color="#38BDF8"/>
              <stop offset="1" stop-color="#0284C7"/>
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div class="user-info" v-if="userStore.token">
        <h2>{{ userStore.username || '答题学员' }}</h2>
        <span class="user-badge">VIP 学员</span>
      </div>
      <div class="user-info" v-else @click="router.push('/login')">
        <h2>未登录用户</h2>
        <span class="login-tip">点击登录 / 注册 ➔</span>
      </div>

      <button v-if="userStore.token" class="logout-btn" @click="handleLogout" title="退出登录">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
      </button>
    </div>

    <!-- 仪表盘数据统计 -->
    <div class="dashboard-grid">
      <div class="dash-card glass-panel">
        <span class="dash-num">{{ stats.total_exams_taken }} <small>场</small></span>
        <span class="dash-label">累计参加考试</span>
      </div>
      <div class="dash-card glass-panel">
        <span class="dash-num highlight">{{ stats.pass_rate }}<small>%</small></span>
        <span class="dash-label">综合及格通过率</span>
      </div>
    </div>

    <!-- 导航 Cell 菜单列表 -->
    <div class="cell-group glass-panel">
      <div class="cell-item" @click="router.push('/favorite')">
        <div class="cell-left">
          <span class="cell-icon fav">★</span>
          <span class="cell-title">我的题目收藏夹</span>
        </div>
        <div class="cell-right">
          <span class="count-badge">{{ stats.favorite_count }} 道题目</span>
          <span class="arrow">›</span>
        </div>
      </div>

      <div class="cell-divider"></div>

      <div class="cell-item" @click="router.push('/history')">
        <div class="cell-left">
          <span class="cell-icon history">📜</span>
          <span class="cell-title">历史答题记录</span>
        </div>
        <div class="cell-right">
          <span class="count-badge">{{ stats.history_count }} 份答卷</span>
          <span class="arrow">›</span>
        </div>
      </div>
    </div>

    <!-- 底部 TabBar 导航 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="router.push('/')">
        <span class="nav-icon">🏠</span>
        <span class="nav-label">首页</span>
      </div>
      <div class="nav-item active">
        <span class="nav-icon">👤</span>
        <span class="nav-label">个人中心</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../../store/user';
import http from '../../utils/http';

const router = useRouter();
const userStore = useUserStore();

const stats = ref({
  total_exams_taken: 0,
  passed_count: 0,
  pass_rate: 0.0,
  favorite_count: 0,
  history_count: 0
});

const loadStats = async () => {
  if (!userStore.token) return;
  try {
    const res: any = await http.get('/api/v1/users/me/stats');
    if (res.data) {
      stats.value = res.data;
    }
  } catch (e) {
    // 忽略未登录错误
  }
};

const handleLogout = () => {
  userStore.clearToken();
  stats.value = { total_exams_taken: 0, passed_count: 0, pass_rate: 0, favorite_count: 0, history_count: 0 };
  router.push('/login');
};

onMounted(() => {
  loadStats();
});
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #e0f2fe 0%, #f8fafc 100%);
  padding: 20px 16px 80px;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.glass-panel {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(2, 132, 199, 0.08);
}

.user-card {
  display: flex;
  align-items: center;
  padding: 20px;
  position: relative;
  margin-bottom: 16px;
}

.avatar-box {
  width: 64px;
  height: 64px;
  margin-right: 16px;
}

.avatar-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 4px 10px rgba(2, 132, 199, 0.2));
}

.user-info h2 {
  margin: 0 0 6px;
  font-size: 20px;
  color: #0f172a;
  font-weight: 700;
}

.user-badge {
  background: linear-gradient(135deg, #0284c7, #38bdf8);
  color: white;
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 600;
}

.login-tip {
  color: #0284c7;
  font-size: 14px;
  font-weight: 600;
}

.logout-btn {
  position: absolute;
  right: 16px;
  top: 20px;
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 8px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.dash-card {
  padding: 16px;
  text-align: center;
}

.dash-num {
  display: block;
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
}

.dash-num.highlight {
  color: #0284c7;
}

.dash-num small {
  font-size: 14px;
  font-weight: 500;
}

.dash-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}

.cell-group {
  padding: 4px 16px;
}

.cell-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  cursor: pointer;
}

.cell-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cell-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.cell-icon.fav {
  background: #fef3c7;
  color: #d97706;
}

.cell-icon.history {
  background: #e0f2fe;
  color: #0284c7;
}

.cell-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.cell-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.count-badge {
  font-size: 13px;
  color: #64748b;
}

.arrow {
  font-size: 18px;
  color: #94a3b8;
  font-weight: 300;
}

.cell-divider {
  height: 1px;
  background: rgba(226, 232, 240, 0.8);
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  display: flex;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  z-index: 100;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.nav-item.active {
  color: #0284c7;
  font-weight: 700;
}

.nav-icon {
  font-size: 18px;
  margin-bottom: 2px;
}

.nav-label {
  font-size: 11px;
}
</style>

<!--
 * [变更日志]
 * 修改时间：2026-09-06 19:50:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.3: 个人中心展示注册资料——昵称为主(@用户名小字)+性别/职务标签, 数据源 GET /users/me;
 *          老用户无昵称时回退用户名]
-->
<template>
  <div class="profile-container">
    <!-- 顶部用户信息 -->
    <header class="user-header">

      <div class="user-row">
        <div class="avatar-xl">
          <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="48" fill="white" fill-opacity="0.25"/>
            <path d="M50 28C57.7 28 64 34.3 64 42C64 49.7 57.7 56 50 56C42.3 56 36 49.7 36 42C36 34.3 42.3 28 50 28Z" fill="white"/>
            <path d="M24 78C24 64.7 35.7 54 50 54C64.3 54 76 64.7 76 78V84H24V78Z" fill="white" fill-opacity="0.9"/>
          </svg>
        </div>
        <div class="user-info" v-if="userStore.token">
          <h2>{{ displayName }}</h2>
          <div class="user-sub">
            <span class="at-username">@{{ userStore.username }}</span>
            <span v-if="genderLabel" class="profile-tag" :class="profile.gender">{{ genderLabel }}</span>
            <span v-if="profile.position" class="profile-tag job">{{ profile.position }}</span>
          </div>
          <p>欢迎回来，继续探索知识的世界</p>
        </div>
        <div class="user-info" v-else @click="router.push('/login')">
          <h2>未登录用户</h2>
          <p class="login-tip">点击登录 / 注册 ›</p>
        </div>
      </div>
    </header>

    <!-- 仪表盘统计 -->
    <section class="dashboard-grid">
      <div class="dash-card blue">
        <span class="dash-icon">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6M9 16h4"/>
          </svg>
        </span>
        <span class="dash-label">累计作答场次</span>
        <span class="dash-num">{{ stats.total_exams_taken }} <small>场</small></span>
      </div>
      <div class="dash-card purple">
        <span class="dash-icon">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
          </svg>
        </span>
        <span class="dash-label">综合通过率</span>
        <span class="dash-num">{{ stats.pass_rate }}<small>%</small></span>
      </div>
    </section>

    <!-- 导航 Cell -->
    <section class="cell-group">
      <div class="cell-item" @click="router.push('/favorite')">
        <span class="cell-icon fav">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </span>
        <span class="cell-title">我的题目收藏夹</span>
        <span class="cell-right"><strong>{{ stats.favorite_count }}</strong> 道题目 ›</span>
      </div>
      <div class="cell-item" @click="router.push('/history')">
        <span class="cell-icon history">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/><path d="M8 11h3M11 8v3"/>
          </svg>
        </span>
        <span class="cell-title">历史答题记录</span>
        <span class="cell-right"><strong>{{ stats.history_count }}</strong> 份答卷 ›</span>
      </div>
      <div v-if="userStore.token" class="cell-item logout-cell" @click="handleLogout">
        <span class="cell-icon logout">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </span>
        <span class="cell-title">退出登录</span>
        <span class="cell-right">›</span>
      </div>
    </section>

    <AppModal
      v-model="logoutModalVisible"
      title="退出登录"
      message="确定要退出登录吗？退出后作答与收藏记录将需要重新登录。"
      type="warning"
      confirmText="退出登录"
      @confirm="onConfirmLogout"
    />

    <TabBar active="profile" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../../store/user';
import http from '../../utils/http';
import TabBar from '../../components/TabBar.vue';
import AppModal from '../../components/AppModal.vue';

const router = useRouter();
const userStore = useUserStore();
const logoutModalVisible = ref(false);

const stats = ref({
  total_exams_taken: 0,
  passed_count: 0,
  pass_rate: 0.0,
  favorite_count: 0,
  history_count: 0
});

// v1.3 注册资料 (昵称优先展示)
const profile = ref<any>({ nickname: '', gender: '', position: '', phone: '', email: '' });
const displayName = computed(() => profile.value.nickname || userStore.nickname || userStore.username || '答题学员');
const genderLabel = computed(() => (profile.value.gender === 'male' ? '男' : profile.value.gender === 'female' ? '女' : ''));

const loadProfile = async () => {
  if (!userStore.token) return;
  try {
    const res: any = await http.get('/api/v1/users/me');
    const data = res?.data || res;
    if (data) {
      profile.value = data;
      if (data.nickname) userStore.setNickname(data.nickname);
    }
  } catch (e) {
    // 静默: 回退 store 中缓存的昵称/用户名
  }
};

const loadStats = async () => {
  if (!userStore.token) return;
  try {
    const res: any = await http.get('/api/v1/users/me/stats');
    const data = res?.data || res;
    if (data) {
      stats.value = {
        total_exams_taken: data.total_exams_taken || 0,
        passed_count: data.passed_count || 0,
        pass_rate: data.pass_rate || 0,
        favorite_count: data.favorite_count || 0,
        history_count: data.history_count ?? data.total_exams_taken ?? 0
      };
    }
  } catch (e) {
    // 忽略未登录错误
  }
};

const handleLogout = () => {
  logoutModalVisible.value = true;
};

const onConfirmLogout = () => {
  userStore.logout();
  stats.value = { total_exams_taken: 0, passed_count: 0, pass_rate: 0, favorite_count: 0, history_count: 0 };
  profile.value = { nickname: '', gender: '', position: '', phone: '', email: '' };
  router.push('/login');
};

onMounted(() => {
  loadProfile();
  loadStats();
});
</script>

<style scoped>
.profile-container {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(180deg, #eef4ff 0%, #f8fafc 45%);
  padding-bottom: 110px;
  box-sizing: border-box;
  font-family: 'Plus Jakarta Sans', 'Outfit', system-ui, sans-serif;
}

.user-header { padding: 16px 20px 0; }

/* 退出登录 cell 样式 */
.cell-icon.logout { background: #fee2e2; color: #ef4444; }
.logout-cell .cell-title { color: #ef4444; }

.user-row { display: flex; align-items: center; gap: 18px; margin-top: 6px; }

.avatar-xl {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #38bdf8, #a855f7);
  padding: 5px;
  box-shadow: 0 10px 26px rgba(168, 85, 247, 0.35);
  flex-shrink: 0;
}

.avatar-xl svg { width: 100%; height: 100%; display: block; }

.user-info h2 { margin: 0 0 6px; font-size: 24px; color: #0f172a; font-weight: 800; }
.user-info p { margin: 0; font-size: 13px; color: #94a3b8; }
.login-tip { color: #0284c7 !important; font-weight: 700; }

.user-sub {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.at-username {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
}

.profile-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
}

.profile-tag.female {
  background: #fce7f3;
  color: #be185d;
}

.profile-tag.male {
  background: #e0f2fe;
  color: #0369a1;
}

.profile-tag.job {
  background: #fef3c7;
  color: #b45309;
}

.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; padding: 22px 20px 0; }

.dash-card {
  border-radius: 24px;
  padding: 22px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 10px 26px rgba(2, 132, 199, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.9);
}

.dash-card.blue { background: linear-gradient(160deg, #f0f9ff, #e0f2fe); }
.dash-card.purple { background: linear-gradient(160deg, #faf5ff, #ede9fe); }

.dash-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dash-card.blue .dash-icon { background: linear-gradient(135deg, #38bdf8, #0284c7); }
.dash-card.purple .dash-icon { background: linear-gradient(135deg, #c084fc, #8b5cf6); }

.dash-label { font-size: 14px; font-weight: 700; color: #0f172a; }
.dash-num { font-size: 32px; font-weight: 800; color: #0284c7; }
.dash-card.purple .dash-num { color: #8b5cf6; }
.dash-num small { font-size: 14px; font-weight: 600; }

.cell-group { padding: 18px 20px 0; display: flex; flex-direction: column; gap: 14px; }

.cell-item {
  background: white;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
}

.cell-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cell-icon.fav { background: #e0f2fe; color: #0284c7; }
.cell-icon.history { background: #f3e8ff; color: #8b5cf6; }

.cell-title { flex: 1; font-size: 16px; font-weight: 700; color: #1e293b; }
.cell-right { font-size: 13px; color: #94a3b8; }
.cell-right strong { color: #6366f1; font-size: 15px; }
</style>

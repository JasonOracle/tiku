<!--
 * [变更日志]
 * 修改时间：2026-09-06 21:00:00
 * AI模型：ZCode (GLM)
 * 修改内容：[v1.2: RBAC 角色化菜单(成员/审计仅超管) + 新增阅卷大厅/消息中心入口 + 消息未读红点轮询 +
 *          头部今日AI额度展示 + 全局 AI Copilot 助手抽屉入口]
-->
<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="aside">
      <div class="brand">
        <span class="brand-badge">TiKu</span>
        <span class="brand-text">管理后台</span>
      </div>
      <el-menu
        :default-active="activePath"
        router
        class="menu"
        background-color="transparent"
        text-color="#475569"
        active-text-color="#0284c7"
      >
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类配置</span>
        </el-menu-item>
        <el-menu-item index="/questions">
          <el-icon><Document /></el-icon>
          <span>题海管理</span>
        </el-menu-item>
        <el-menu-item index="/exams">
          <el-icon><Reading /></el-icon>
          <span>试卷与组卷</span>
        </el-menu-item>
        <el-menu-item index="/grading">
          <el-icon><EditPen /></el-icon>
          <span>阅卷大厅</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户与明细</span>
        </el-menu-item>
        <el-menu-item index="/banners">
          <el-icon><Picture /></el-icon>
          <span>首页Banner</span>
        </el-menu-item>
        <el-menu-item index="/messages">
          <el-icon><Bell /></el-icon>
          <template #title>
            <span>消息中心</span>
            <el-badge v-if="unreadCount > 0" :value="unreadCount" :max="99" class="menu-badge" />
          </template>
        </el-menu-item>
        <template v-if="userStore.isSuper()">
          <el-menu-item index="/members">
            <el-icon><Avatar /></el-icon>
            <span>成员与AI额度</span>
          </el-menu-item>
          <el-menu-item index="/audit">
            <el-icon><List /></el-icon>
            <span>审计日志</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3 class="page-title">{{ currentTitle }}</h3>
        </div>
        <div class="header-right">
          <div class="quota-chip" title="今日 AI 出题/组卷/聊天剩余次数">
            <span class="quota-icon">✨</span>
            <span>AI 额度 <strong>{{ userStore.quotaRemaining }}</strong></span>
          </div>
          <div class="user-info">
            <el-avatar :size="32" class="avatar">{{ username.substring(0, 1).toUpperCase() }}</el-avatar>
            <span class="name">{{ username }}</span>
            <el-tag size="small" :type="userStore.isSuper() ? 'danger' : 'primary'" effect="plain">
              {{ userStore.isSuper() ? '超管' : '老师' }}
            </el-tag>
          </div>
          <el-button type="danger" text plain @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 全局 AI 助手悬浮按钮 -->
    <div class="ai-fab" title="AI 助手" @click="copilotRef?.open()">
      <span>✨</span>
    </div>
    <AiCopilot ref="copilotRef" />
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Document, Reading, Folder, User, Picture, SwitchButton, Bell, Avatar, List, EditPen } from '@element-plus/icons-vue';
import { useUserStore } from '../../store/user';
import AiCopilot from '../../components/AiCopilot.vue';
import request from '../../utils/request';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const copilotRef = ref<any>(null);

const activePath = computed(() => route.path);
const currentTitle = computed(() => (route.meta.title as string) || '仪表盘');
const username = computed(() => userStore.username || 'Admin');
const unreadCount = ref(0);
let pollTimer: number | undefined;

const loadUnread = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/notifications/unread-count');
    unreadCount.value = res.count || 0;
  } catch (e) {
    /* 静默 */
  }
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};

onMounted(() => {
  userStore.loadProfile();
  loadUnread();
  pollTimer = window.setInterval(loadUnread, 30000);
});

onUnmounted(() => {
  if (pollTimer) window.clearInterval(pollTimer);
});
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: #f8fafc;
}

.aside {
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.menu-badge {
  margin-left: 8px;
}

.menu-badge :deep(.el-badge__content) {
  background-color: #ef4444;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.quota-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #eff6ff, #f0f9ff);
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 13px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white;
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
  z-index: 2000;
  transition: transform 0.15s ease;
}

.ai-fab:hover {
  transform: scale(1.08);
}
</style>

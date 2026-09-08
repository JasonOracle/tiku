<!--
  * [变更日志]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[v1.4: 严格 RBAC 权限控制，仅超级管理员 (isSuper) 头像下拉菜单可见「模型中心」，普通管理员及出题人隐藏]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[v1.3: 1. 侧边栏菜单重排(分类紧跟首页,移除旧AI模型配置,私有文库改名AI文库);
  *          2. 顶栏头像改造为 el-dropdown 下拉菜单(个人资料/AI设置/退出登录);
  *          3. 移除顶栏独立退出登录按钮]
  * 修改时间：2026-09-06 21:00:00
  * AI模型：ZCode (GLM)
  * 修改内容：[v1.2: RBAC 角色化菜单(成员/审计仅超管) + 新增阅卷大厅/消息中心入口 + 消息未读红点轮询 +
  *          头部今日AI额度展示 + 全局 AI Copilot 助手抽屉入口]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.3: Dashboard 首位/AI助理最末菜单重排 + 移除 TiKu 文字品牌 + 头像个人信息弹窗入口]
  * 修改时间：2026-09-08
  * AI模型：Muse Spark
  * 修改内容：[v1.3 任务1: 菜单新增模型中心入口]
  -->
<template>
  <el-container class="layout-container">
    <el-aside width="240px" class="aside">
      <el-menu
        :default-active="activePath"
        router
        class="menu"
        background-color="transparent"
        text-color="#475569"
        active-text-color="#0284c7"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类配置</span>
        </el-menu-item>
        <el-menu-item index="/exams">
          <el-icon><Reading /></el-icon>
          <span>试卷与组卷</span>
        </el-menu-item>
        <el-menu-item index="/questions">
          <el-icon><Document /></el-icon>
          <span>题海管理</span>
        </el-menu-item>
        <el-menu-item index="/grading">
          <el-icon><EditPen /></el-icon>
          <span>阅卷大厅</span>
        </el-menu-item>
        <el-menu-item index="/rag">
          <el-icon><Collection /></el-icon>
          <span>AI 文库</span>
        </el-menu-item>
        <template v-if="userStore.isSuper() || userStore.role === 'admin'">
          <el-menu-item index="/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </template>
        <template v-if="userStore.isSuper()">
          <el-menu-item index="/banners">
            <el-icon><Picture /></el-icon>
            <span>首页Banner</span>
          </el-menu-item>
          <el-menu-item index="/audit">
            <el-icon><List /></el-icon>
            <span>审计日志</span>
          </el-menu-item>
        </template>
        <el-menu-item index="/ai-assistant">
          <el-icon><MagicStick /></el-icon>
          <span>✨ AI 助理</span>
        </el-menu-item>
      </el-menu>
      <!-- 侧边栏底部 AI 推广卡 -->
      <div class="side-promo">
        <img class="promo-img" :src="promoUrl" alt="AI 赋能教育" />
        <div class="promo-title">AI 赋能教育</div>
        <div class="promo-sub">让每一次考试都有价值</div>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3 class="page-title">{{ currentTitle }}</h3>
        </div>
        <div class="header-right">
          <div class="quota-chip" title="今日 AI 出题/组卷/聊天剩余次数" @click="router.push('/ai-assistant')" style="cursor: pointer">
            <span class="quota-icon"><el-icon><MagicStick /></el-icon></span>
            <span>AI 额度 <strong>{{ userStore.quotaRemaining }}</strong></span>
          </div>
          <el-button type="primary" plain size="small" class="ai-copilot-head-btn" @click="router.push('/ai-assistant')">
            <el-icon style="margin-right: 4px;"><MagicStick /></el-icon> AI 助理
          </el-button>
          <div class="msg-btn-wrap" title="消息中心" @click="router.push('/messages')">
            <el-badge :value="unreadCount" :max="99" :hidden="unreadCount === 0">
              <el-button circle size="default">
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
          </div>
          <!-- 头像 Dropdown 菜单 -->
          <el-dropdown trigger="hover" @command="handleDropdown">
            <div class="user-info" style="cursor: pointer">
              <el-avatar :size="32" class="avatar">{{ username.substring(0, 1).toUpperCase() }}</el-avatar>
              <span class="name">{{ username }}</span>
              <el-tag size="small" :type="userStore.isSuper() ? 'danger' : (userStore.role === 'admin' ? 'warning' : 'primary')" effect="plain">
                {{ userStore.isSuper() ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '出题人') }}
              </el-tag>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人资料
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.isSuper()" command="model-center">
                  <el-icon><Cpu /></el-icon>模型中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout" style="color: #ef4444;">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 头像个人信息弹窗 -->
    <ProfileDialog v-model="profileVisible" />
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Document, Reading, Folder, User, Picture, SwitchButton, Bell, List, EditPen, MagicStick, HomeFilled, Cpu, Collection } from '@element-plus/icons-vue';
import { useUserStore } from '../../store/user';
import request from '../../utils/request';
import ProfileDialog from './components/ProfileDialog.vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const copilotRef = ref<any>(null);
const profileVisible = ref(false);
const promoUrl = `${import.meta.env.BASE_URL}images/ai-edu.png`;

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

const handleDropdown = (command: string) => {
  if (command === 'profile') {
    profileVisible.value = true;
  } else if (command === 'model-center') {
    router.push('/model-center');
  } else if (command === 'logout') {
    userStore.logout();
    router.push('/login');
  }
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

.aside .menu {
  flex: 1;
}

.side-promo {
  margin: 12px;
  border-radius: 12px;
  background: linear-gradient(160deg, #eef4ff, #e0ecff);
  border: 1px solid #dbeafe;
  padding: 12px;
  text-align: center;
}

.promo-img {
  width: 100%;
  border-radius: 8px;
  display: block;
}

.promo-title {
  font-size: 13px;
  font-weight: 800;
  color: #0f172a;
  margin-top: 8px;
}

.promo-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
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

.msg-btn-wrap {
  cursor: pointer;
  display: flex;
  align-items: center;
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

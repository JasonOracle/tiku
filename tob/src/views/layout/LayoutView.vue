<!--
 * [变更日志]
 * 修改时间：2026-09-03
 * AI模型：Gemini 底层
 * 修改内容：[1. 实现全局 SaaS 后台导航与毛玻璃 Header 布局框架]
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
        <el-menu-item index="/questions">
          <el-icon><Document /></el-icon>
          <span>题海管理</span>
        </el-menu-item>
        <el-menu-item index="/exams">
          <el-icon><Reading /></el-icon>
          <span>试卷与组卷</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类配置</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户与明细</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3 class="page-title">{{ currentTitle }}</h3>
        </div>
        <div class="header-right">
          <div class="user-info">
            <el-avatar :size="32" class="avatar">{{ username.substring(0, 1).toUpperCase() }}</el-avatar>
            <span class="name">{{ username }}</span>
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
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Document, Reading, Folder, User, SwitchButton } from '@element-plus/icons-vue';
import { useUserStore } from '../../store/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const activePath = computed(() => route.path);
const currentTitle = computed(() => (route.meta.title as string) || '仪表盘');
const username = computed(() => userStore.username || 'Admin');

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
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

.brand {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 24px;
  border-bottom: 1px solid #f1f5f9;
}

.brand-badge {
  background: linear-gradient(135deg, #0284c7, #38bdf8);
  color: white;
  font-weight: 800;
  font-size: 14px;
  padding: 4px 10px;
  border-radius: 8px;
}

.brand-text {
  font-weight: 700;
  color: #0f172a;
  font-size: 16px;
}

.menu {
  border-right: none;
  padding: 12px 8px;
}

.header {
  height: 64px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  color: #0f172a;
  font-weight: 700;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar {
  background: #0284c7;
  color: white;
  font-weight: 700;
}

.name {
  font-weight: 600;
  color: #334155;
  font-size: 14px;
}

.main-content {
  padding: 24px 28px;
}
</style>

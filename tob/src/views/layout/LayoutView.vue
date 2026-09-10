<!--
  * [变更日志]
  * 修改时间：2026-09-10
  * AI模型：OpenCode / Gemini 底层
  * 修改内容：[将侧边栏超管菜单「我的团队」修正为「企业管理」，与「成员管理」精准划分平台级 vs 租户级边界]
  * 修改时间：2026-09-10
  * AI模型：OpenCode / Gemini 底层
  * 修改内容：[1. 清除侧边栏重复渲染的超管菜单项(我的团队、审计日志); 2. 从侧边栏移除首页Banner，迁移到右上角头像下拉菜单，且通过 v-if="userStore.isSuper() || userStore.role === 'admin'" 严格限定管理员与超管可见]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[优化侧边栏菜单层级与文案: 1. 调整菜单排序为分类配置 -> 题目管理 -> 试卷管理; 2. 原「题海管理」更名为「题目管理」，原「试卷与组卷」更名为「试卷管理」]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[严格 RBAC 权限控制，仅超级管理员 (isSuper) 头像下拉菜单可见「模型中心」，普通管理员及出题人隐藏]
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
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类配置</span>
        </el-menu-item>
        <el-menu-item index="/resources">
          <el-icon><Document /></el-icon>
          <span>题目管理</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><Reading /></el-icon>
          <span>试卷管理</span>
        </el-menu-item>
        <el-menu-item index="/verification">
          <el-icon><EditPen /></el-icon>
          <span>阅卷管理</span>
        </el-menu-item>
        <el-menu-item index="/kb">
          <el-icon><Collection /></el-icon>
          <span>AI知识库</span>
        </el-menu-item>
        <template v-if="userStore.isSuper() || userStore.role === 'admin'">
          <el-menu-item index="/members">
            <el-icon><User /></el-icon>
            <span>成员管理</span>
          </el-menu-item>
        </template>
        <template v-if="userStore.isSuper()">
          <el-menu-item index="/super-admin/tenants">
            <el-icon><OfficeBuilding /></el-icon>
            <span>企业管理</span>
          </el-menu-item>
          <el-menu-item index="/audit">
            <el-icon><List /></el-icon>
            <span>审计日志</span>
          </el-menu-item>
          <el-menu-item index="/model-center">
            <el-icon><Cpu /></el-icon>
            <span>模型中心</span>
          </el-menu-item>
        </template>
        <el-menu-item index="/ai-assistant">
          <el-icon><MagicStick /></el-icon>
          <span>✨ AI 助理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3 class="page-title">{{ currentTitle }}</h3>
        </div>
        <div class="header-right">
          <el-select
            v-if="userStore.isSuperAdmin"
            v-model="inspectTenant"
            placeholder="视察企业"
            size="small"
            style="width: 170px"
            @change="switchTenant"
          >
            <el-option
              v-for="t in tenantOptions"
              :key="t.tenant_id"
              :label="t.tenant_name"
              :value="String(t.tenant_id)"
            />
          </el-select>
          <div class="tenant-chip" :title="tenantChipTitle">
            <span class="tenant-icon"><el-icon><OfficeBuilding /></el-icon></span>
            <span>{{ tenantChipText }}</span>
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
              <el-avatar :size="32" class="avatar">{{ displayName.substring(0, 1).toUpperCase() }}</el-avatar>
              <span class="name">{{ displayName }}</span>
              <el-tag size="small" :type="userStore.isSuper() ? 'danger' : (userStore.role === 'admin' ? 'warning' : 'primary')" effect="plain">
                {{ userStore.isSuper() ? '超级管理员' : (userStore.role === 'admin' ? '管理员' : '出题人') }}
              </el-tag>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人资料
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.isSuper() || userStore.role === 'admin'" command="banners">
                  <el-icon><Picture /></el-icon>首页Banner
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
import { Document, Reading, Folder, User, Picture, SwitchButton, Bell, List, EditPen, MagicStick, HomeFilled, Cpu, Collection, OfficeBuilding } from '@element-plus/icons-vue';
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
const displayName = computed(() => userStore.name || userStore.nickname || userStore.username || 'Admin');
const unreadCount = ref(0);
const tenantOptions = ref<any[]>([]);
const inspectTenant = ref<string>(localStorage.getItem('tiku_tob_tenant') || '');
let pollTimer: number | undefined;

onMounted(() => {
  userStore.loadProfile();
});

const tenantChipText = computed(() => {
  if (!userStore.isSuperAdmin) {
    return (userStore.joinedTenants[0] && userStore.joinedTenants[0].tenant_name) || '当前企业';
  }
  const tid = inspectTenant.value;
  if (!tid) return '未选择视察企业';
  const t = tenantOptions.value.find((x: any) => String(x.tenant_id) === tid);
  return t ? `视察：${t.tenant_name}` : `企业 ${tid}`;
});

const tenantChipTitle = computed(() => tenantChipText.value);

const loadTenants = async () => {
  if (!userStore.isSuperAdmin) return;
  try {
    const res: any = await request.get('/api/v1/super-admin/tenants');
    tenantOptions.value = res.items || [];
  } catch (e) {
    /* 静默 */
  }
};

const switchTenant = () => {
  userStore.setTenant(inspectTenant.value);
  window.location.reload();
};

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
  } else if (command === 'banners') {
    router.push('/banners');
  } else if (command === 'logout') {
    userStore.logout();
    router.push('/login');
  }
};

onMounted(() => {
  userStore.loadProfile();
  loadUnread();
  loadTenants();
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

.tenant-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  background: linear-gradient(135deg, #eff6ff, #f0f9ff);
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  cursor: default;
}

.tenant-icon {
  opacity: 0.7;
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

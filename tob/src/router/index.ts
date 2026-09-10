/**
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[将超管路由 super-admin/tenants 的标题由「我的团队」修正为「企业管理」，消除概念混淆]
 * 修改时间：2026-09-10
 * AI模型：Muse Spark
 * 修改内容：[侧边栏回摆教育词汇：试卷管理/题目管理/阅卷管理/AI知识库/我的团队（仅展示层，路由与接口不变）]
 */
import { createRouter, createWebHistory, RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router';
import { ElMessage } from 'element-plus';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../views/layout/LayoutView.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/DashboardView.vue'),
        meta: { title: '数据看板' }
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('../views/resources/ResourcesView.vue'),
        meta: { title: '题目管理' }
      },
      {
        path: 'kb',
        name: 'Kb',
        component: () => import('../views/kb/KbView.vue'),
        meta: { title: 'AI知识库' }
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('../views/tasks/TasksView.vue'),
        meta: { title: '试卷管理' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/categories/CategoriesView.vue'),
        meta: { title: '分类配置' }
      },
      {
        path: 'verification',
        name: 'Verification',
        component: () => import('../views/verification/VerificationView.vue'),
        meta: { title: '阅卷管理' }
      },
      {
        path: 'users',
        redirect: '/members'
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import('../views/messages/MessagesView.vue'),
        meta: { title: '消息中心' }
      },
      {
        path: 'banners',
        name: 'Banners',
        component: () => import('../views/banners/BannersView.vue'),
        meta: { title: '首页Banner设置', roles: ['super_admin'] }
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('../views/audit/AuditView.vue'),
        meta: { title: '审计日志', roles: ['super_admin'] }
      },
      {
        path: 'ai-config',
        name: 'AiConfig',
        component: () => import('../views/ai-config/AiConfigView.vue'),
        meta: { title: 'AI 模型配置', roles: ['super_admin', 'admin'] }
      },
      {
        path: 'model-center',
        name: 'ModelCenter',
        component: () => import('../views/model-center/ModelCenterView.vue'),
        meta: { title: '模型中心', roles: ['super_admin'] }
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('../views/members/MembersView.vue'),
        meta: { title: '成员管理', roles: ['super_admin', 'admin'] }
      },
      {
        path: 'super-admin/tenants',
        name: 'SuperTenants',
        component: () => import('../views/super/TenantsView.vue'),
        meta: { title: '企业管理', roles: ['super_admin'] }
      },
      {
        path: 'ai-assistant',
        name: 'AiAssistant',
        component: () => import('../views/ai/AiAssistantView.vue'),
        meta: { title: 'AI 助理' }
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});


router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const token = localStorage.getItem('tiku_tob_token');
  if (to.meta.requiresAuth !== false && !token) {
    next('/login');
    return;
  }
  if (to.path === '/login' && token) {
    next('/');
    return;
  }
  const isSuper = localStorage.getItem('tiku_tob_super') === '1';
  // 上帝未选视察企业时只能停留在租户大盘（业务接口无租户头必 403）
  if (isSuper && !localStorage.getItem('tiku_tob_tenant') && to.path !== '/super-admin/tenants') {
    ElMessage.warning('请先选择要视察的企业');
    next('/super-admin/tenants');
    return;
  }
  if (Array.isArray(to.meta.roles)) {
    // 越权路由直接 Toast 拦截
    const role = localStorage.getItem('tiku_tob_role') || '';
    const allowed = [...(to.meta.roles as string[])];
    if (isSuper) {
      next();
      return;
    }
    if (!allowed.includes(role)) {
      ElMessage.error('当前角色无权访问该页面');
      next('/dashboard');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;

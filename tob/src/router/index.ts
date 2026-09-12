/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：OpenCode / DeepSeek
 * 修改内容：[权限隔离重构：1. Dashboard/Categories/Resources/Tasks/Verification/Kb/AiAssistant 七条业务路由补全 meta.roles（与后端 require_admin 严格对齐，含 owner）；2. 越权访问由跳 /dashboard 改为清除登录凭证后踢回 /login，杜绝带无效 token 死循环]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[将超管路由 super-admin/tenants 的标题由「我的团队」修正为「企业管理」，消除概念混淆]
 * 修改时间：2026-09-10
 * AI模型：Muse Spark
 * 修改内容：[侧边栏回摆教育词汇：试卷管理/题目管理/阅卷管理/AI知识库/我的团队（仅展示层，路由与接口不变）]
 */
import { createRouter, createWebHistory, RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router';
import { ElMessage } from 'element-plus';

// 管理后台业务路由统一角色白名单（与后端 require_admin 严格对齐：owner/admin；super_admin 由守卫额外放行）
const ADMIN_ROLES = ['super_admin', 'admin', 'owner'];

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
        meta: { title: '数据看板', roles: ADMIN_ROLES }
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('../views/resources/ResourcesView.vue'),
        meta: { title: '题目管理', roles: ADMIN_ROLES }
      },
      {
        path: 'kb',
        name: 'Kb',
        component: () => import('../views/kb/KbView.vue'),
        meta: { title: 'AI知识库', roles: ADMIN_ROLES }
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('../views/tasks/TasksView.vue'),
        meta: { title: '试卷管理', roles: ADMIN_ROLES }
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
        meta: { title: '阅卷管理', roles: ADMIN_ROLES }
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
        meta: { title: 'AI 助理', roles: ADMIN_ROLES }
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
    const role = localStorage.getItem('tiku_tob_role') || '';
    const allowed = [...(to.meta.roles as string[])];
    if (isSuper || allowed.includes(role)) {
      next();
      return;
    }
    // 越权拦截：先清空登录凭证再踢回登录页，避免残留无效 token 触发 /login → / 死循环
    ElMessage.error('当前角色无权访问管理后台，请使用管理员账号登录');
    ['tiku_tob_token', 'tiku_tob_username', 'tiku_tob_role', 'tiku_tob_tenant', 'tiku_tob_super']
      .forEach((k) => localStorage.removeItem(k));
    next('/login');
    return;
  }
  next();
});

export default router;

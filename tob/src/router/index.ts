/**
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Gemini 系列
 * 修改内容：[路由元信息 meta.title 规范更新: 原「题海管理」更名为「题目管理」，原「试卷与组卷」更名为「试卷管理」]
 * 修改时间：2026-09-03 23:41:00
 * AI模型：Gemini 底层
 * 修改内容：[1. createWebHistory 绑定 import.meta.env.BASE_URL，彻底解决 /admin/ 子路径空白白屏问题]
 * 修改时间：2026-09-07
 * AI模型：Muse Spark
  * 修改内容：[v1.7: 新增 Dashboard 首页与 AI 模型配置路由，默认重定向改仪表盘；新增 meta.roles 角色守卫，越权跳转弹 Toast 拦截]
  * 修改时间：2026-09-08
  * AI模型：Muse Spark
  * 修改内容：[v1.3 任务1: 新增模型中心路由]
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
        meta: { title: '首页' }
      },
      {
        path: 'questions',
        name: 'Questions',
        component: () => import('../views/questions/QuestionsView.vue'),
        meta: { title: '题目管理' }
      },
      {
        path: 'rag',
        name: 'Rag',
        component: () => import('../views/rag/RagView.vue'),
        meta: { title: '私有文库' }
      },
      {
        path: 'exams',
        name: 'Exams',
        component: () => import('../views/exams/ExamsView.vue'),
        meta: { title: '试卷管理' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/categories/CategoriesView.vue'),
        meta: { title: '分类配置' }
      },
      {
        path: 'grading',
        name: 'Grading',
        component: () => import('../views/grading/GradingView.vue'),
        meta: { title: '阅卷大厅' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/users/UsersView.vue'),
        meta: { title: '用户管理', roles: ['super_admin', 'admin'] }
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
        path: 'ai-assistant',
        name: 'AiAssistant',
        component: () => import('../views/ai/AiAssistantView.vue'),
        meta: { title: '✨ AI 助理' }
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
  } else if (to.path === '/login' && token) {
    next('/');
  } else if (Array.isArray(to.meta.roles)) {
    // v1.7: 越权路由直接 Toast 拦截
    const role = localStorage.getItem('tiku_tob_role') || '';
    if (!(to.meta.roles as string[]).includes(role)) {
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

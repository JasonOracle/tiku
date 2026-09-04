/**
 * [变更日志]
 * 修改时间：2026-09-03 23:41:00
 * AI模型：Gemini 底层
 * 修改内容：[1. createWebHistory 绑定 import.meta.env.BASE_URL，彻底解决 /admin/ 子路径空白白屏问题]
 */
import { createRouter, createWebHistory, RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router';

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
    redirect: '/questions',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'questions',
        name: 'Questions',
        component: () => import('../views/questions/QuestionsView.vue'),
        meta: { title: '题海管理' }
      },
      {
        path: 'exams',
        name: 'Exams',
        component: () => import('../views/exams/ExamsView.vue'),
        meta: { title: '试卷与组卷' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/categories/CategoriesView.vue'),
        meta: { title: '分类配置' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/users/UsersView.vue'),
        meta: { title: '用户与答题明细' }
      },
      {
        path: 'banners',
        name: 'Banners',
        component: () => import('../views/banners/BannersView.vue'),
        meta: { title: '首页Banner设置' }
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
  } else {
    next();
  }
});

export default router;

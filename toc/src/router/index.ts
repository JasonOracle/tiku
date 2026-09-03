/**
 * [变更日志]
 * 修改时间：2026-09-04 00:08:00
 * AI模型：Gemini 底层
 * 修改内容：[1. 补充 /profile 个人中心与 /history 历史记录路由]
 */
import { createRouter, createWebHistory, RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/index/IndexView.vue'),
    meta: { title: '智题库 - 轻测评刷题' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/LoginView.vue'),
    meta: { title: '用户登录/注册' }
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: () => import('../views/quiz/QuizView.vue'),
    meta: { title: '在线测评' }
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('../views/report/ReportView.vue'),
    meta: { title: '分析报告' }
  },
  {
    path: '/favorite',
    name: 'Favorite',
    component: () => import('../views/favorite/FavoriteView.vue'),
    meta: { title: '我的题目收藏夹' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/profile/ProfileView.vue'),
    meta: { title: '个人中心' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/history/HistoryView.vue'),
    meta: { title: '历史答题记录' }
  }
];


const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  document.title = (to.meta.title as string) || '智题库 TiKu';
  next();
});

export default router;

/**
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[通用化名词映射：测评/考试→任务，题目收藏→资源收藏，我的测试→我的任务]
 */
import { createRouter, createWebHistory, RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/index/IndexView.vue'),
    meta: { title: '企业空间' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/LoginView.vue'),
    meta: { title: '成员登录' }
  },
  {
    path: '/task',
    name: 'Task',
    component: () => import('../views/task/TaskView.vue'),
    meta: { title: '任务执行' }
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('../views/report/ReportView.vue'),
    meta: { title: '结果报告' }
  },
  {
    path: '/favorite',
    name: 'Favorite',
    component: () => import('../views/favorite/FavoriteView.vue'),
    meta: { title: '我的资源收藏' }
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
    meta: { title: '历史任务记录' }
  },
  {
    path: '/my-tasks',
    name: 'MyTasks',
    component: () => import('../views/my-tasks/MyTasksView.vue'),
    meta: { title: '我的任务' }
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

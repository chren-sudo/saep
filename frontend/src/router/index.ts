import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('@/views/HomeView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'achievements',
          name: 'AchievementList',
          component: () => import('@/views/AchievementList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'achievements/create',
          name: 'AchievementCreate',
          component: () => import('@/views/AchievementForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'achievements/:id/edit',
          name: 'AchievementEdit',
          component: () => import('@/views/AchievementForm.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'reviews',
          name: 'ReviewList',
          component: () => import('@/views/ReviewList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'public-notices',
          name: 'PublicNoticeList',
          component: () => import('@/views/PublicNoticeList.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'my-scores',
          name: 'MyScores',
          component: () => import('@/views/MyScores.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'ranking',
          name: 'RankingList',
          component: () => import('@/views/RankingList.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) return '/login'
  if (to.meta.guest && token) return '/'
})

export default router

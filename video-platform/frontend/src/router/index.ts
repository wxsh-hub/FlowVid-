import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/Home.vue'),
    },
    {
      path: '/create',
      name: 'Create',
      component: () => import('../views/Create.vue'),
    },
    {
      path: '/task/:id',
      name: 'TaskDetail',
      component: () => import('../views/TaskDetail.vue'),
    },
    {
      path: '/configs',
      name: 'Configs',
      component: () => import('../views/Configs.vue'),
    },
  ],
})

export default router

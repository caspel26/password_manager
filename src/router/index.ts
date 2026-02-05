import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'lock',
      component: () => import('../views/LockScreen.vue'),
      meta: { transition: 'fade' },
    },
    {
      path: '/vault',
      name: 'vault',
      component: () => import('../views/VaultView.vue'),
      meta: { index: 0 },
    },
    {
      path: '/generator',
      name: 'generator',
      component: () => import('../views/GeneratorView.vue'),
      meta: { index: 1 },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { index: 2 },
    },
  ],
})

export default router

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useVaultStore } from '@/stores/passwordManager'

const store = useVaultStore()
const route = useRoute()
const router = useRouter()

const isLocked = computed(() => route.path === '/' || route.path === '/lock')
const currentPath = computed(() => route.path)

// Track transition direction based on nav index
const transitionName = ref('slide-left')
const prevIndex = ref(0)

const navItems: { icon: string; label: string; path: string }[] = [
  { icon: 'mdi-shield-lock', label: 'Vault', path: '/vault' },
  { icon: 'mdi-key-variant', label: 'Generate', path: '/generator' },
  { icon: 'mdi-cog', label: 'Settings', path: '/settings' },
]

// Watch route changes to determine animation direction
watch(() => route.path, (newPath, oldPath) => {
  const newMeta = route.meta
  const oldRoute = router.options.routes.find(r => r.path === oldPath)

  // Lock screen transition
  if (oldPath === '/' || newPath === '/') {
    transitionName.value = 'fade-scale'
    return
  }

  const newIndex = typeof newMeta.index === 'number' ? newMeta.index : 0
  const oldIndex = typeof oldRoute?.meta?.index === 'number' ? oldRoute.meta.index : 0

  transitionName.value = newIndex > oldIndex ? 'slide-left' : 'slide-right'
  prevIndex.value = newIndex
})

function navigate(path: string) {
  router.push(path)
}

async function handleLock() {
  await store.lock()
  router.push('/')
}

// Handle keyboard shortcuts and auto-lock
onMounted(() => {
  window.electronAPI.onShortcutLock(() => {
    if (store.unlocked) {
      handleLock()
    }
  })

  window.electronAPI.onShortcutGenerator(() => {
    if (store.unlocked) {
      router.push('/generator')
    }
  })

  window.electronAPI.onAutoLocked(() => {
    store.unlocked = false
    store.vaultName = null
    store.entries = []
    store.searchQuery = ''
    store.generatedPassword = null
    store.notify('Vault auto-locked', 'info')
    router.push('/')
  })
})

onUnmounted(() => {
  window.electronAPI.removeAllListeners('shortcut:lock')
  window.electronAPI.removeAllListeners('shortcut:generator')
  window.electronAPI.removeAllListeners('vault:auto-locked')
})
</script>

<template>
  <v-app>
    <v-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition :name="transitionName" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </v-main>

    <!-- Bottom navigation -->
    <transition name="nav-slide">
      <nav v-if="!isLocked" class="bottom-nav">
        <button
          v-for="item in navItems"
          :key="item.path"
          :class="['nav-item', { active: currentPath === item.path }]"
          @click="navigate(item.path)"
        >
          <div class="nav-icon-wrap" :class="{ active: currentPath === item.path }">
            <v-icon size="18">{{ item.icon }}</v-icon>
          </div>
          <span class="nav-label">{{ item.label }}</span>
        </button>
        <button class="nav-item" @click="handleLock">
          <div class="nav-icon-wrap">
            <v-icon size="18">mdi-lock</v-icon>
          </div>
          <span class="nav-label">Lock</span>
        </button>
      </nav>
    </transition>

    <!-- Snackbar -->
    <v-snackbar
      v-model="store.snackbar.show"
      :color="store.snackbar.color"
      :timeout="1500"
      location="top"
      rounded="pill"
      class="custom-snackbar"
    >
      {{ store.snackbar.message }}
    </v-snackbar>
  </v-app>
</template>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.12);
}

/* Snackbar override */
.custom-snackbar .v-snackbar__wrapper {
  min-width: auto !important;
  margin-top: 8px !important;
}
.custom-snackbar .v-snackbar__content {
  font-size: 12px !important;
  padding: 8px 16px !important;
}

/* Page Transitions */

/* Slide Left (going forward) */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Slide Right (going back) */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* Fade Scale (for lock screen) */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-scale-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.fade-scale-leave-to {
  opacity: 0;
  transform: scale(1.02);
}

/* Nav slide up animation */
.nav-slide-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transition-delay: 0.15s;
}

.nav-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-slide-enter-from {
  opacity: 0;
  transform: translateY(100%);
}

.nav-slide-leave-to {
  opacity: 0;
  transform: translateY(100%);
}
</style>

<style scoped>
.app-main {
  height: 100vh;
  background: #0a0a0f;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 6px 12px 10px;
  background: rgba(10, 10, 15, 0.92);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 10px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  border-radius: 10px;
  transition: color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-item:hover {
  color: rgba(255, 255, 255, 0.6);
}

.nav-item.active {
  color: #7c6ff7;
}

.nav-icon-wrap {
  width: 32px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-icon-wrap.active {
  background: rgba(68, 52, 188, 0.2);
}

.nav-label {
  font-size: 10px;
  font-weight: 500;
}
</style>

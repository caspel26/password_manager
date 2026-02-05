<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useVaultStore } from '@/stores/passwordManager'

const store = useVaultStore()
const route = useRoute()
const router = useRouter()

const isLocked = computed(() => route.path === '/' || route.path === '/lock')
const currentPath = computed(() => route.path)

const navItems: { icon: string; label: string; path: string }[] = [
  { icon: 'mdi-shield-lock', label: 'Vault', path: '/vault' },
  { icon: 'mdi-key-variant', label: 'Generate', path: '/generator' },
]

function navigate(path: string) {
  router.push(path)
}

async function handleLock() {
  await store.lock()
  router.push('/')
}
</script>

<template>
  <v-app>
    <v-main class="app-main">
      <RouterView />
    </v-main>

    <!-- Bottom navigation -->
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
  padding: 4px 12px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  border-radius: 10px;
  transition: color 0.15s;
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
  transition: background 0.15s;
}

.nav-icon-wrap.active {
  background: rgba(68, 52, 188, 0.2);
}

.nav-label {
  font-size: 10px;
  font-weight: 500;
}
</style>

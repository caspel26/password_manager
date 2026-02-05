<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useVaultStore } from '@/stores/passwordManager'

const store = useVaultStore()
const route = useRoute()
const router = useRouter()

const isLocked = computed(() => route.path === '/' || route.path === '/lock')
const currentPath = computed(() => route.path)

const navItems = [
  { icon: 'mdi-shield-lock', label: 'Vault', path: '/vault' },
  { icon: 'mdi-refresh', label: 'Generator', path: '/generator' },
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
    <!-- Sidebar (only when unlocked) -->
    <v-navigation-drawer
      v-if="!isLocked"
      permanent
      rail
      class="app-sidebar"
      color="transparent"
    >
      <!-- Top: logo -->
      <div class="sidebar-logo">
        <div class="sidebar-logo-icon">
          <v-icon size="22" color="white">mdi-shield-lock</v-icon>
        </div>
      </div>

      <!-- Nav items -->
      <div class="sidebar-nav">
        <div
          v-for="item in navItems"
          :key="item.path"
          class="sidebar-item"
          :class="{ active: currentPath === item.path }"
          @click="navigate(item.path)"
        >
          <v-icon size="22">{{ item.icon }}</v-icon>
          <v-tooltip activator="parent" location="right">{{ item.label }}</v-tooltip>
        </div>
      </div>

      <!-- Bottom: vault info + lock -->
      <template #append>
        <div class="sidebar-bottom">
          <div
            class="sidebar-item"
            @click="handleLock"
          >
            <v-icon size="22">mdi-lock</v-icon>
            <v-tooltip activator="parent" location="right">Lock Vault</v-tooltip>
          </div>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main class="app-main" :class="{ 'with-sidebar': !isLocked }">
      <RouterView />
    </v-main>

    <!-- Global snackbar -->
    <v-snackbar
      v-model="store.snackbar.show"
      :color="store.snackbar.color"
      :timeout="2500"
      location="bottom right"
      rounded="lg"
    >
      {{ store.snackbar.message }}
      <template #actions>
        <v-btn variant="text" size="small" @click="store.snackbar.show = false">
          <v-icon size="18">mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>

<style scoped>
.app-sidebar {
  background: rgba(20, 20, 30, 0.95) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
  padding-top: 42px; /* space for macOS traffic lights */
}

.sidebar-logo {
  display: flex;
  justify-content: center;
  padding: 12px 0 20px;
}

.sidebar-logo-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 0 8px;
}

.sidebar-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  opacity: 0.5;
}
.sidebar-item:hover {
  opacity: 0.8;
  background: rgba(255, 255, 255, 0.06);
}
.sidebar-item.active {
  opacity: 1;
  background: rgba(68, 52, 188, 0.25);
  color: #7c6ff7;
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px 16px;
}

.app-main {
  height: 100vh;
  background: #1a1a2e;
}

.app-main.with-sidebar {
  padding-top: 0 !important;
}
</style>

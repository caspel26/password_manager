<template>
  <div class="lock-screen">
    <!-- Animated background -->
    <div class="bg-gradient"></div>
    <div class="bg-pattern"></div>
    <div class="bg-glow"></div>
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>

    <div class="lock-container" :class="{ 'animate-in': animateIn }">
      <!-- Logo (shown outside card for pick/register screens) -->
      <div v-if="screen !== 'login'" class="lock-logo">
        <div class="logo-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C9.243 2 7 4.243 7 7V9H6C4.897 9 4 9.897 4 11V20C4 21.103 4.897 22 6 22H18C19.103 22 20 21.103 20 20V11C20 9.897 19.103 9 18 9H17V7C17 4.243 14.757 2 12 2ZM12 4C13.654 4 15 5.346 15 7V9H9V7C9 5.346 10.346 4 12 4ZM12 14C12.552 14 13 14.448 13 15V17C13 17.552 12.552 18 12 18C11.448 18 11 17.552 11 17V15C11 14.448 11.448 14 12 14Z" fill="white"/>
          </svg>
        </div>
        <h1 class="app-title">Vault</h1>
        <p class="app-tagline">Your secrets, secured locally</p>
      </div>

      <transition name="form-switch" mode="out-in">

        <!-- User selection screen -->
        <div v-if="screen === 'pick'" key="pick" class="form-section">
          <div class="user-list">
            <button
              v-for="user in users"
              :key="user.id"
              class="user-card"
              @click="selectUser(user)"
            >
              <div class="user-avatar-sm">
                <img v-if="user.avatar" :src="user.avatar" alt="" />
                <v-icon v-else size="20" color="rgba(255,255,255,0.5)">mdi-account</v-icon>
              </div>
              <div class="user-info">
                <span class="user-display-name">{{ user.displayName }}</span>
                <span class="user-username">@{{ user.username }}</span>
              </div>
              <v-icon size="14" class="user-chevron">mdi-chevron-right</v-icon>
            </button>
          </div>
          <button class="text-btn" @click="screen = 'register'">
            <v-icon size="14" class="mr-1">mdi-plus</v-icon>
            Create new account
          </button>
        </div>

        <!-- Login screen -->
        <div v-else-if="screen === 'login'" key="login" class="login-layout">
          <div class="login-card">
            <div class="login-card-accent"></div>

            <button class="login-back-btn" @click="goBack">
              <v-icon size="14">mdi-arrow-left</v-icon>
              <span>Back</span>
            </button>

            <!-- Avatar hero -->
            <div class="login-avatar-area">
              <div class="avatar-glow"></div>
              <div class="selected-avatar-wrap">
                <div class="selected-avatar">
                  <img v-if="selectedUser?.avatar" :src="selectedUser.avatar" alt="" />
                  <v-icon v-else size="40" color="rgba(255,255,255,0.5)">mdi-account</v-icon>
                </div>
                <div class="avatar-ring"></div>
              </div>
            </div>

            <!-- User info -->
            <div class="login-identity">
              <span class="login-greeting">Welcome back</span>
              <span class="login-display-name">{{ selectedUser?.displayName }}</span>
              <span class="login-username">@{{ selectedUser?.username }}</span>
            </div>

            <!-- Password form -->
            <div class="login-fields">
              <div class="input-group" :class="{ focused: pwdFocused, error: loginError }">
                <v-icon class="input-icon" size="16">mdi-lock</v-icon>
                <input
                  ref="passwordInput"
                  v-model="password"
                  :type="showPwd ? 'text' : 'password'"
                  placeholder="Enter your password"
                  class="custom-input"
                  @focus="pwdFocused = true; loginError = false"
                  @blur="pwdFocused = false"
                  @keyup.enter="handleLogin"
                />
                <button class="toggle-btn" @click="showPwd = !showPwd" tabindex="-1">
                  <v-icon size="16">{{ showPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                </button>
              </div>
              <transition name="error-slide">
                <p v-if="loginError" class="error-text">{{ errorMessage }}</p>
              </transition>
              <button class="primary-btn" :disabled="loading || !password" @click="handleLogin">
                <v-icon v-if="!loading" size="16" class="mr-1">mdi-lock-open-variant</v-icon>
                <span v-if="!loading">Unlock</span>
                <v-progress-circular v-else indeterminate size="18" width="2" />
              </button>
            </div>

            <!-- Security footer -->
            <div class="login-badges">
              <div class="security-badge">
                <v-icon size="10">mdi-shield-check</v-icon>
                <span>AES-256-GCM</span>
              </div>
              <div class="security-badge">
                <v-icon size="10">mdi-database-lock</v-icon>
                <span>Local only</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Register screen -->
        <div v-else key="register" class="form-section">
          <button v-if="users.length > 0" class="back-btn" @click="goBack">
            <v-icon size="14">mdi-arrow-left</v-icon>
            <span>Back</span>
          </button>

          <p class="section-title">Create Account</p>

          <div class="input-group" :class="{ focused: usernameFocused }">
            <v-icon class="input-icon" size="16">mdi-account</v-icon>
            <input
              ref="usernameInput"
              v-model="username"
              type="text"
              placeholder="Username"
              class="custom-input"
              @focus="usernameFocused = true"
              @blur="usernameFocused = false"
            />
          </div>

          <div class="input-group" :class="{ focused: displayNameFocused }">
            <v-icon class="input-icon" size="16">mdi-card-account-details</v-icon>
            <input
              v-model="displayName"
              type="text"
              placeholder="Display Name (optional)"
              class="custom-input"
              @focus="displayNameFocused = true"
              @blur="displayNameFocused = false"
            />
          </div>

          <div class="input-group" :class="{ focused: pwdFocused }">
            <v-icon class="input-icon" size="16">mdi-lock</v-icon>
            <input
              v-model="password"
              :type="showPwd ? 'text' : 'password'"
              placeholder="Password"
              class="custom-input"
              @focus="pwdFocused = true"
              @blur="pwdFocused = false"
            />
            <button class="toggle-btn" @click="showPwd = !showPwd" tabindex="-1">
              <v-icon size="16">{{ showPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
            </button>
          </div>

          <transition name="strength-fade">
            <div v-if="password" class="strength-indicator">
              <div class="strength-bars">
                <div :class="['bar', { active: passwordStrength >= 1 }]"></div>
                <div :class="['bar', { active: passwordStrength >= 2 }]"></div>
                <div :class="['bar', { active: passwordStrength >= 3 }]"></div>
                <div :class="['bar', { active: passwordStrength >= 4 }]"></div>
              </div>
              <span class="strength-text">{{ strengthText }}</span>
            </div>
          </transition>

          <div class="input-group" :class="{ focused: confirmFocused }">
            <v-icon class="input-icon" size="16">mdi-lock-check</v-icon>
            <input
              v-model="confirm"
              :type="showConfirm ? 'text' : 'password'"
              placeholder="Confirm Password"
              class="custom-input"
              @focus="confirmFocused = true"
              @blur="confirmFocused = false"
              @keyup.enter="handleRegister"
            />
            <button class="toggle-btn" @click="showConfirm = !showConfirm" tabindex="-1">
              <v-icon size="16">{{ showConfirm ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
            </button>
          </div>
          <button class="primary-btn" :disabled="loading || !username || !password || !confirm" @click="handleRegister">
            <span v-if="!loading">Create Account</span>
            <v-progress-circular v-else indeterminate size="18" width="2" />
          </button>
        </div>
      </transition>

      <!-- Security info (hidden on login screen — it's inside the card) -->
      <div v-if="screen !== 'login'" class="security-footer">
        <div class="security-badge">
          <v-icon size="10">mdi-shield-check</v-icon>
          <span>AES-256-GCM</span>
        </div>
        <div class="security-badge">
          <v-icon size="10">mdi-database-lock</v-icon>
          <span>Local only</span>
        </div>
      </div>
    </div>

    <div class="version-badge">v1.0.1</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'
import { useRouter } from 'vue-router'
import type { UserProfile } from '@/types/electron'

const store = useVaultStore()
const router = useRouter()

const screen = ref<'pick' | 'login' | 'register'>('pick')
const users = ref<UserProfile[]>([])
const selectedUser = ref<UserProfile | null>(null)

const username = ref('')
const displayName = ref('')
const password = ref('')
const confirm = ref('')
const showPwd = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const pwdFocused = ref(false)
const confirmFocused = ref(false)
const usernameFocused = ref(false)
const displayNameFocused = ref(false)
const loginError = ref(false)
const errorMessage = ref('')
const animateIn = ref(false)

const passwordInput = ref<HTMLInputElement | null>(null)
const usernameInput = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  requestAnimationFrame(() => {
    animateIn.value = true
  })
  await loadUserList()
})

async function loadUserList() {
  const loaded = await store.loadUsers()
  users.value = loaded
  if (users.value.length === 0) {
    screen.value = 'register'
  } else {
    screen.value = 'pick'
  }
}

function selectUser(user: UserProfile) {
  selectedUser.value = user
  screen.value = 'login'
  password.value = ''
  loginError.value = false
  // Apply this user's accent color on the lock screen
  store.applyAccentColor(user.accentColor ?? 248)
  nextTick(() => {
    passwordInput.value?.focus()
  })
}

function goBack() {
  if (users.value.length === 0) return
  screen.value = 'pick'
  resetForm()
}

function resetForm() {
  username.value = ''
  displayName.value = ''
  password.value = ''
  confirm.value = ''
  showPwd.value = false
  showConfirm.value = false
  loginError.value = false
  errorMessage.value = ''
  selectedUser.value = null
}

const passwordStrength = computed(() => {
  const p = password.value
  let score = 0
  if (p.length >= 8) score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
  if (/[0-9]/.test(p) && /[^A-Za-z0-9]/.test(p)) score++
  return score
})

const strengthText = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return 'Weak'
  if (s === 2) return 'Fair'
  if (s === 3) return 'Good'
  return 'Strong'
})

async function handleLogin() {
  if (!password.value || !selectedUser.value) return
  loading.value = true
  loginError.value = false
  const ok = await store.login(selectedUser.value.username, password.value)
  loading.value = false
  if (ok) {
    password.value = ''
    router.push('/vault')
  } else {
    loginError.value = true
    errorMessage.value = 'Invalid password'
  }
}

async function handleRegister() {
  if (!username.value || !password.value || !confirm.value) return
  loading.value = true
  const ok = await store.register(username.value, password.value, confirm.value, displayName.value || undefined)
  loading.value = false
  if (ok) {
    resetForm()
    router.push('/vault')
  }
}
</script>

<style scoped>
.lock-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
  -webkit-app-region: drag;
}

/* ── Animated background ─────────────────────────── */

.bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 0%, hsla(var(--accent-h), var(--accent-s), 47%, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, hsla(var(--accent-h), var(--accent-s), 58%, 0.08) 0%, transparent 40%);
  animation: gradient-pulse 8s ease-in-out infinite;
}

@keyframes gradient-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.bg-pattern {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
}

.bg-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%);
  background: radial-gradient(circle, hsla(var(--accent-h), var(--accent-s), 47%, 0.2) 0%, transparent 70%);
  filter: blur(40px);
  animation: glow-pulse 4s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { transform: translate(-50%, -60%) scale(1); opacity: 0.6; }
  50% { transform: translate(-50%, -60%) scale(1.1); opacity: 0.8; }
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.12;
}

.bg-orb-1 {
  width: 120px;
  height: 120px;
  top: 15%;
  left: 10%;
  background: hsl(var(--accent-h), var(--accent-s), 58%);
  animation: orb-float-1 12s ease-in-out infinite;
}

.bg-orb-2 {
  width: 80px;
  height: 80px;
  bottom: 20%;
  right: 10%;
  background: hsl(var(--accent-h), var(--accent-s), 70%);
  animation: orb-float-2 10s ease-in-out infinite;
}

@keyframes orb-float-1 {
  0%, 100% { transform: translate(0, 0); }
  33% { transform: translate(20px, -15px); }
  66% { transform: translate(-10px, 10px); }
}

@keyframes orb-float-2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-15px, -20px); }
}

/* ── Lock container ──────────────────────────────── */

.lock-container {
  width: 100%;
  max-width: 380px;
  padding: 24px 28px;
  position: relative;
  z-index: 1;
  -webkit-app-region: no-drag;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.lock-container.animate-in {
  opacity: 1;
  transform: translateY(0);
}

/* ── Logo ────────────────────────────────────────── */

.lock-logo {
  text-align: center;
  margin-bottom: 28px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, hsl(var(--accent-h), var(--accent-s), 47%) 0%, hsl(var(--accent-h), var(--accent-s), 58%) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
  box-shadow:
    0 8px 28px hsla(var(--accent-h), var(--accent-s), 47%, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  animation: logo-float 3s ease-in-out infinite;
}

@keyframes logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.app-title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
  margin: 0 0 3px;
  color: var(--text-primary);
}

.app-tagline {
  font-size: 11px;
  color: var(--text-muted);
  margin: 0;
  letter-spacing: 0.3px;
}

/* ── User list ────────────────────────────────────── */

.user-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
  max-height: 230px;
  overflow-y: auto;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-primary);
  text-align: left;
  font-family: inherit;
  font-size: inherit;
  flex-shrink: 0;
}

.user-card:hover {
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.12);
  border-color: hsla(var(--accent-h), var(--accent-s), 47%, 0.3);
}

.user-card:active {
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.18);
  transform: scale(0.98);
}

.user-avatar-sm {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar-sm img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.user-display-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-username {
  font-size: 11px;
  color: var(--text-muted);
}

.user-chevron {
  color: var(--text-muted);
  flex-shrink: 0;
  transition: color 0.2s;
}

.user-card:hover .user-chevron {
  color: var(--text-secondary);
}

/* ── Login layout ─────────────────────────────────── */

.login-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
}

.login-back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  font-family: inherit;
  padding: 12px 16px 0;
  transition: color 0.2s;
}

.login-back-btn:hover {
  color: var(--text-primary);
}

/* ── Login card ───────────────────────────────────── */

.login-card {
  width: 100%;
  border-radius: 22px;
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow:
    0 16px 48px var(--shadow-color),
    0 0 0 1px var(--border-light) inset,
    inset 0 1px 0 var(--border-primary),
    0 0 80px hsla(var(--accent-h), var(--accent-s), 47%, 0.06);
}

.login-card-accent {
  height: 3px;
  background: linear-gradient(
    90deg,
    transparent,
    hsl(var(--accent-h), var(--accent-s), 55%),
    hsl(var(--accent-h), var(--accent-s), 70%),
    hsl(var(--accent-h), var(--accent-s), 55%),
    transparent
  );
  opacity: 0.8;
}

/* ── Avatar area ──────────────────────────────────── */

.login-avatar-area {
  position: relative;
  padding: 28px 0 16px;
  display: flex;
  justify-content: center;
}

.avatar-glow {
  position: absolute;
  width: 160px;
  height: 160px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, hsla(var(--accent-h), var(--accent-s), 50%, 0.25) 0%, transparent 65%);
  filter: blur(30px);
  pointer-events: none;
}

.selected-avatar-wrap {
  position: relative;
}

.selected-avatar {
  width: 88px;
  height: 88px;
  border-radius: 26px;
  background: linear-gradient(
    135deg,
    hsla(var(--accent-h), var(--accent-s), 47%, 0.4),
    hsla(var(--accent-h), var(--accent-s), 58%, 0.15)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.selected-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-ring {
  position: absolute;
  inset: -4px;
  border-radius: 30px;
  border: 2px solid hsla(var(--accent-h), var(--accent-s), 58%, 0.3);
  animation: ring-pulse 3s ease-in-out infinite;
}

@keyframes ring-pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.03); }
}

/* ── Identity info ────────────────────────────────── */

.login-identity {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 20px;
}

.login-greeting {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: hsla(var(--accent-h), var(--accent-s), 70%, 0.5);
  margin-bottom: 6px;
}

.login-display-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}

.login-username {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 3px;
}

/* ── Password fields ──────────────────────────────── */

.login-fields {
  padding: 0 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.login-badges {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 12px 24px 16px;
  border-top: 1px solid var(--border-light);
}

/* ── Buttons ─────────────────────────────────────── */

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  font-family: inherit;
  padding: 4px 0;
  margin-bottom: 8px;
  transition: color 0.2s;
}

.back-btn:hover {
  color: var(--text-primary);
}

.text-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  box-sizing: border-box;
  background: transparent;
  border: 1px dashed var(--border-primary);
  border-radius: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  font-family: inherit;
  padding: 12px;
  transition: all 0.2s;
}

.text-btn:hover {
  color: var(--text-primary);
  border-color: hsla(var(--accent-h), var(--accent-s), 47%, 0.4);
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.08);
  border-style: solid;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
  text-align: center;
}

/* ── Form ─────────────────────────────────────────── */

.form-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-switch-enter-active,
.form-switch-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-switch-enter-from {
  opacity: 0;
  transform: translateX(24px);
}

.form-switch-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}

.error-slide-enter-active,
.error-slide-leave-active {
  transition: all 0.2s ease;
}

.error-slide-enter-from,
.error-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.strength-fade-enter-active,
.strength-fade-leave-active {
  transition: all 0.2s ease;
}

.strength-fade-enter-from,
.strength-fade-leave-to {
  opacity: 0;
}

.input-group {
  display: flex;
  align-items: center;
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: 13px;
  padding: 0 14px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-group.focused {
  border-color: hsla(var(--accent-h), var(--accent-s), 47%, 0.5);
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.08);
  box-shadow: 0 0 0 3px hsla(var(--accent-h), var(--accent-s), 47%, 0.1);
}

.input-group.error {
  border-color: rgba(231, 76, 60, 0.5);
  background: rgba(231, 76, 60, 0.05);
  animation: shake 0.4s ease;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-6px); }
  40%, 80% { transform: translateX(6px); }
}

.input-icon {
  color: var(--text-muted);
  margin-right: 8px;
  transition: color 0.2s;
}

.input-group.focused .input-icon {
  color: hsla(var(--accent-h), var(--accent-s), 58%, 0.8);
}

.custom-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 14px;
  padding: 14px 0;
  font-family: inherit;
}

.custom-input::placeholder {
  color: var(--text-muted);
}

.toggle-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  transition: color 0.2s;
}

.toggle-btn:hover {
  color: var(--text-secondary);
}

.error-text {
  font-size: 11px;
  color: #e74c3c;
  margin: 0;
  padding-left: 4px;
}

.strength-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}

.strength-bars {
  display: flex;
  gap: 3px;
}

.strength-bars .bar {
  width: 24px;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.strength-bars .bar.active:nth-child(1) { background: #e74c3c; }
.strength-bars .bar.active:nth-child(2) { background: #f39c12; }
.strength-bars .bar.active:nth-child(3) { background: #27ae60; }
.strength-bars .bar.active:nth-child(4) { background: #27ae60; }

.strength-text {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.primary-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 48px;
  margin-top: 2px;
  background: linear-gradient(135deg, hsl(var(--accent-h), var(--accent-s), 47%) 0%, hsl(var(--accent-h), var(--accent-s), 55%) 100%);
  border: none;
  border-radius: 14px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px hsla(var(--accent-h), var(--accent-s), 47%, 0.3);
  position: relative;
  overflow: hidden;
}

.primary-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s;
}

.primary-btn:hover:not(:disabled)::before {
  transform: translateX(100%);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px hsla(var(--accent-h), var(--accent-s), 47%, 0.45);
}

.primary-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 12px hsla(var(--accent-h), var(--accent-s), 47%, 0.3);
}

.primary-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ── Footer ──────────────────────────────────────── */

.security-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.security-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.version-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 9px;
  color: var(--text-muted);
}
</style>

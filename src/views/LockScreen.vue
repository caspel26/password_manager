<template>
  <div class="lock-screen">
    <!-- Animated background -->
    <div class="bg-gradient"></div>
    <div class="bg-pattern"></div>
    <div class="bg-glow"></div>

    <div class="lock-container" :class="{ 'animate-in': animateIn }">
      <!-- Logo -->
      <div class="lock-logo">
        <div class="logo-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C9.243 2 7 4.243 7 7V9H6C4.897 9 4 9.897 4 11V20C4 21.103 4.897 22 6 22H18C19.103 22 20 21.103 20 20V11C20 9.897 19.103 9 18 9H17V7C17 4.243 14.757 2 12 2ZM12 4C13.654 4 15 5.346 15 7V9H9V7C9 5.346 10.346 4 12 4ZM12 14C12.552 14 13 14.448 13 15V17C13 17.552 12.552 18 12 18C11.448 18 11 17.552 11 17V15C11 14.448 11.448 14 12 14Z" fill="white"/>
          </svg>
        </div>
        <h1 class="app-title">Vault</h1>
        <p class="app-tagline">Your secrets, secured locally</p>
      </div>

      <!-- Mode toggle -->
      <div class="mode-toggle">
        <button
          :class="['mode-btn', { active: mode === 'unlock' }]"
          @click="mode = 'unlock'"
        >
          <v-icon size="14" class="mr-1">mdi-lock-open-variant</v-icon>
          Open
        </button>
        <button
          :class="['mode-btn', { active: mode === 'create' }]"
          @click="mode = 'create'"
        >
          <v-icon size="14" class="mr-1">mdi-plus</v-icon>
          New
        </button>
        <div class="mode-indicator" :class="{ right: mode === 'create' }"></div>
      </div>

      <!-- Unlock form -->
      <transition name="form-switch" mode="out-in">
        <div v-if="mode === 'unlock'" key="unlock" class="form-section">
          <div class="input-group" :class="{ focused: pwdFocused, error: unlockError }">
            <v-icon class="input-icon" size="16">mdi-key</v-icon>
            <input
              v-model="password"
              :type="showPwd ? 'text' : 'password'"
              placeholder="Master Password"
              class="custom-input"
              @focus="pwdFocused = true; unlockError = false"
              @blur="pwdFocused = false"
              @keyup.enter="handleUnlock"
            />
            <button class="toggle-btn" @click="showPwd = !showPwd" tabindex="-1">
              <v-icon size="16">{{ showPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
            </button>
          </div>
          <transition name="error-slide">
            <p v-if="unlockError" class="error-text">{{ errorMessage }}</p>
          </transition>
          <button class="primary-btn" :disabled="loading || !password" @click="handleUnlock">
            <span v-if="!loading">Unlock Vault</span>
            <v-progress-circular v-else indeterminate size="18" width="2" />
          </button>
        </div>

        <!-- Create form -->
        <div v-else key="create" class="form-section">
          <div class="input-group" :class="{ focused: pwdFocused }">
            <v-icon class="input-icon" size="16">mdi-key</v-icon>
            <input
              v-model="password"
              :type="showPwd ? 'text' : 'password'"
              placeholder="Master Password"
              class="custom-input"
              @focus="pwdFocused = true"
              @blur="pwdFocused = false"
            />
            <button class="toggle-btn" @click="showPwd = !showPwd" tabindex="-1">
              <v-icon size="16">{{ showPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
            </button>
          </div>

          <!-- Password strength -->
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
            <v-icon class="input-icon" size="16">mdi-key-check</v-icon>
            <input
              v-model="confirm"
              :type="showConfirm ? 'text' : 'password'"
              placeholder="Confirm Password"
              class="custom-input"
              @focus="confirmFocused = true"
              @blur="confirmFocused = false"
              @keyup.enter="handleCreate"
            />
            <button class="toggle-btn" @click="showConfirm = !showConfirm" tabindex="-1">
              <v-icon size="16">{{ showConfirm ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
            </button>
          </div>
          <button class="primary-btn" :disabled="loading || !password || !confirm" @click="handleCreate">
            <span v-if="!loading">Create Vault</span>
            <v-progress-circular v-else indeterminate size="18" width="2" />
          </button>
        </div>
      </transition>

      <!-- Security info -->
      <div class="security-footer">
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

    <!-- Version -->
    <div class="version-badge">v1.0.1</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'
import { useRouter } from 'vue-router'

const store = useVaultStore()
const router = useRouter()

const mode = ref<'unlock' | 'create'>('unlock')
const password = ref('')
const confirm = ref('')
const showPwd = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const pwdFocused = ref(false)
const confirmFocused = ref(false)
const unlockError = ref(false)
const errorMessage = ref('')
const animateIn = ref(false)

// Trigger entrance animation
onMounted(() => {
  requestAnimationFrame(() => {
    animateIn.value = true
  })
})

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

async function handleUnlock() {
  if (!password.value) return
  loading.value = true
  unlockError.value = false
  const ok = await store.unlock(password.value)
  loading.value = false
  if (ok) {
    password.value = ''
    router.push('/vault')
  } else {
    unlockError.value = true
    errorMessage.value = 'Invalid password or vault'
  }
}

async function handleCreate() {
  if (!password.value || !confirm.value) return
  loading.value = true
  const ok = await store.createVault(password.value, confirm.value)
  loading.value = false
  if (ok) {
    password.value = ''
    confirm.value = ''
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
  background: #0a0a0f;
  position: relative;
  overflow: hidden;
  -webkit-app-region: drag;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(68, 52, 188, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(108, 92, 231, 0.08) 0%, transparent 40%);
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
  background: radial-gradient(circle, rgba(68, 52, 188, 0.2) 0%, transparent 70%);
  filter: blur(40px);
  animation: glow-pulse 4s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { transform: translate(-50%, -60%) scale(1); opacity: 0.6; }
  50% { transform: translate(-50%, -60%) scale(1.1); opacity: 0.8; }
}

.lock-container {
  width: 100%;
  max-width: 280px;
  padding: 24px 20px;
  position: relative;
  z-index: 1;
  -webkit-app-region: no-drag;
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.lock-container.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.lock-logo {
  text-align: center;
  margin-bottom: 24px;
}

.logo-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #4434bc 0%, #6c5ce7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  box-shadow:
    0 8px 24px rgba(68, 52, 188, 0.35),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  animation: logo-float 3s ease-in-out infinite;
}

@keyframes logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.app-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.3px;
  margin: 0 0 2px;
  color: #fff;
}

.app-tagline {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0;
  letter-spacing: 0.2px;
}

.mode-toggle {
  display: flex;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  padding: 3px;
  margin-bottom: 20px;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px;
  transition: color 0.2s;
  position: relative;
  z-index: 1;
}

.mode-btn.active {
  color: #fff;
}

.mode-indicator {
  position: absolute;
  top: 3px;
  left: 3px;
  width: calc(50% - 3px);
  height: calc(100% - 6px);
  background: rgba(68, 52, 188, 0.35);
  border-radius: 8px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-indicator.right {
  transform: translateX(100%);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Form switch transitions */
.form-switch-enter-active,
.form-switch-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-switch-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.form-switch-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Error slide transition */
.error-slide-enter-active,
.error-slide-leave-active {
  transition: all 0.2s ease;
}

.error-slide-enter-from,
.error-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Strength fade transition */
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
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 0 12px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-group.focused {
  border-color: rgba(68, 52, 188, 0.5);
  background: rgba(68, 52, 188, 0.08);
  box-shadow: 0 0 0 3px rgba(68, 52, 188, 0.1);
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
  color: rgba(255, 255, 255, 0.25);
  margin-right: 8px;
  transition: color 0.2s;
}

.input-group.focused .input-icon {
  color: rgba(68, 52, 188, 0.7);
}

.custom-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-size: 13px;
  padding: 12px 0;
  font-family: inherit;
}

.custom-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.toggle-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.25);
  cursor: pointer;
  padding: 4px;
  display: flex;
  transition: color 0.2s;
}

.toggle-btn:hover {
  color: rgba(255, 255, 255, 0.5);
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
  height: 42px;
  margin-top: 6px;
  background: linear-gradient(135deg, #4434bc 0%, #5a4ad1 100%);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(68, 52, 188, 0.3);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(68, 52, 188, 0.4);
}

.primary-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(68, 52, 188, 0.3);
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.security-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
}

.security-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.2);
}

.version-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.15);
}
</style>

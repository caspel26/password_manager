<template>
  <div class="generator-page">
    <div class="page-header">
      <span class="page-title">Generate</span>
    </div>

    <div class="generator-content">
      <!-- Password display -->
      <div class="password-card" :class="{ empty: !store.generatedPassword }">
        <code class="password-text">
          {{ store.generatedPassword || 'Tap generate' }}
        </code>
        <button
          class="copy-btn"
          :disabled="!store.generatedPassword"
          @click="copyPassword"
        >
          <v-icon size="16">mdi-content-copy</v-icon>
        </button>
      </div>

      <!-- Strength -->
      <div v-if="store.generatedPassword" class="strength-row">
        <div class="strength-bar">
          <div class="strength-fill" :style="{ width: strengthPercent + '%' }" :class="strengthClass"></div>
        </div>
        <span class="strength-label" :class="strengthClass">{{ strengthLabel }}</span>
      </div>

      <!-- Length slider -->
      <div class="length-card">
        <div class="length-header">
          <span class="length-title">Length</span>
          <span class="length-value">{{ length }}</span>
        </div>
        <input
          v-model="length"
          type="range"
          :min="8"
          :max="64"
          class="length-slider"
        />
        <div class="length-range">
          <span>8</span>
          <span>64</span>
        </div>
      </div>

      <!-- Character types -->
      <div class="types-card">
        <span class="types-title">Character types</span>
        <div class="types-list">
          <div class="type-item">
            <v-icon size="12" color="#27ae60">mdi-check-circle</v-icon>
            <span>Lowercase (a-z)</span>
          </div>
          <div class="type-item">
            <v-icon size="12" color="#27ae60">mdi-check-circle</v-icon>
            <span>Uppercase (A-Z)</span>
          </div>
          <div class="type-item">
            <v-icon size="12" color="#27ae60">mdi-check-circle</v-icon>
            <span>Numbers (0-9)</span>
          </div>
          <div class="type-item">
            <v-icon size="12" color="#27ae60">mdi-check-circle</v-icon>
            <span>Symbols (!@#$...)</span>
          </div>
        </div>
      </div>

      <!-- Generate button -->
      <button class="generate-btn" :disabled="loading" @click="generate">
        <v-icon v-if="!loading" size="16" class="mr-1">mdi-refresh</v-icon>
        <v-progress-circular v-else indeterminate size="16" width="2" class="mr-1" />
        Generate
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'

const store = useVaultStore()
const length = ref(24)
const loading = ref(false)

const strengthPercent = computed(() => {
  const l = store.generatedPassword?.length || 0
  if (l >= 24) return 100
  if (l >= 16) return 75
  if (l >= 12) return 50
  return 25
})

const strengthClass = computed(() => {
  const p = strengthPercent.value
  if (p >= 75) return 'strong'
  if (p >= 50) return 'moderate'
  return 'weak'
})

const strengthLabel = computed(() => {
  const p = strengthPercent.value
  if (p >= 75) return 'Strong'
  if (p >= 50) return 'Moderate'
  return 'Weak'
})

async function generate() {
  loading.value = true
  await store.generatePassword(length.value)
  loading.value = false
}

function copyPassword() {
  if (store.generatedPassword) {
    navigator.clipboard.writeText(store.generatedPassword)
    store.notify('Copied', 'info')
  }
}
</script>

<style scoped>
.generator-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0a0a0f;
  padding-bottom: 60px;
}

.page-header {
  padding: 12px 16px;
  -webkit-app-region: drag;
}

.page-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.generator-content {
  flex: 1;
  padding: 8px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.password-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

.password-card.empty .password-text {
  color: rgba(255, 255, 255, 0.25);
}

.password-text {
  flex: 1;
  font-family: 'SF Mono', 'JetBrains Mono', monospace;
  font-size: 13px;
  color: #fff;
  word-break: break-all;
  line-height: 1.4;
  background: transparent;
}

.copy-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.copy-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.copy-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.strength-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px;
}

.strength-bar {
  flex: 1;
  height: 3px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s, background 0.3s;
}

.strength-fill.strong { background: #27ae60; }
.strength-fill.moderate { background: #f39c12; }
.strength-fill.weak { background: #e74c3c; }

.strength-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.strength-label.strong { color: #27ae60; }
.strength-label.moderate { color: #f39c12; }
.strength-label.weak { color: #e74c3c; }

.length-card {
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}

.length-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.length-title {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
}

.length-value {
  font-size: 13px;
  font-weight: 700;
  color: #7c6ff7;
  background: rgba(68, 52, 188, 0.15);
  padding: 3px 10px;
  border-radius: 6px;
}

.length-slider {
  width: 100%;
  height: 3px;
  appearance: none;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  outline: none;
}

.length-slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(68, 52, 188, 0.4);
}

.length-range {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.25);
}

.types-card {
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}

.types-title {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 10px;
}

.types-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.generate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 40px;
  margin-top: auto;
  background: linear-gradient(135deg, #4434bc, #5a4ad1);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
  box-shadow: 0 4px 16px rgba(68, 52, 188, 0.3);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(68, 52, 188, 0.4);
}

.generate-btn:active:not(:disabled) {
  transform: translateY(0);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

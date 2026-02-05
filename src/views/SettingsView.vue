<template>
  <div class="settings-page">
    <div class="page-header">
      <span class="page-title">Settings</span>
    </div>

    <div class="settings-content">
      <!-- Security Section -->
      <div class="settings-section">
        <span class="section-title">Security</span>

        <div class="setting-card">
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Auto-lock</span>
              <span class="setting-desc">Lock vault after inactivity</span>
            </div>
            <label class="toggle-switch">
              <input
                type="checkbox"
                :checked="store.settings.autoLockEnabled"
                @change="toggleAutoLock"
              />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row" :class="{ disabled: !store.settings.autoLockEnabled }">
            <div class="setting-info">
              <span class="setting-label">Lock timeout</span>
              <span class="setting-desc">{{ store.settings.autoLockMinutes }} {{ store.settings.autoLockMinutes === 1 ? 'minute' : 'minutes' }}</span>
            </div>
            <div class="timeout-controls">
              <button
                class="timeout-btn"
                :disabled="!store.settings.autoLockEnabled || store.settings.autoLockMinutes <= 1"
                @click="adjustTimeout(-1)"
              >
                <v-icon size="14">mdi-minus</v-icon>
              </button>
              <span class="timeout-value">{{ store.settings.autoLockMinutes }}</span>
              <button
                class="timeout-btn"
                :disabled="!store.settings.autoLockEnabled || store.settings.autoLockMinutes >= 30"
                @click="adjustTimeout(1)"
              >
                <v-icon size="14">mdi-plus</v-icon>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- About Section -->
      <div class="settings-section">
        <span class="section-title">About</span>

        <div class="setting-card">
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Version</span>
              <span class="setting-desc">v1.0.1</span>
            </div>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Encryption</span>
              <span class="setting-desc">AES-256-GCM</span>
            </div>
            <v-icon size="14" color="#27ae60">mdi-shield-check</v-icon>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Key Derivation</span>
              <span class="setting-desc">PBKDF2-SHA512 (600k iterations)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Vault Info Section -->
      <div class="settings-section">
        <span class="section-title">Current Vault</span>

        <div class="setting-card">
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">{{ store.vaultName || 'No vault' }}</span>
              <span class="setting-desc">{{ store.entryCount }} {{ store.entryCount === 1 ? 'entry' : 'entries' }} stored</span>
            </div>
            <div class="vault-icon-small">
              <v-icon size="14" color="white">mdi-database-lock</v-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Keyboard Shortcuts -->
      <div class="settings-section">
        <span class="section-title">Keyboard Shortcuts</span>

        <div class="setting-card">
          <div class="shortcut-row">
            <span class="shortcut-label">New Entry</span>
            <kbd class="shortcut-key">⌘N</kbd>
          </div>
          <div class="setting-divider"></div>
          <div class="shortcut-row">
            <span class="shortcut-label">Search</span>
            <kbd class="shortcut-key">⌘F</kbd>
          </div>
          <div class="setting-divider"></div>
          <div class="shortcut-row">
            <span class="shortcut-label">Generator</span>
            <kbd class="shortcut-key">⌘G</kbd>
          </div>
          <div class="setting-divider"></div>
          <div class="shortcut-row">
            <span class="shortcut-label">Lock Vault</span>
            <kbd class="shortcut-key">⌘L</kbd>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useVaultStore } from '@/stores/passwordManager'

const store = useVaultStore()

async function toggleAutoLock() {
  await store.updateSettings({
    autoLockEnabled: !store.settings.autoLockEnabled
  })
}

async function adjustTimeout(delta: number) {
  const newValue = Math.max(1, Math.min(30, store.settings.autoLockMinutes + delta))
  await store.updateSettings({
    autoLockMinutes: newValue
  })
}
</script>

<style scoped>
.settings-page {
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

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
}

.settings-section {
  margin-bottom: 20px;
}

.section-title {
  display: block;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.35);
  margin-bottom: 8px;
  padding-left: 4px;
}

.setting-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  overflow: hidden;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  gap: 12px;
  transition: opacity 0.2s;
}

.setting-row.disabled {
  opacity: 0.4;
  pointer-events: none;
}

.setting-info {
  flex: 1;
  min-width: 0;
}

.setting-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
}

.setting-desc {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 1px;
}

.setting-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.04);
  margin: 0 14px;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toggle-switch input:checked + .toggle-slider {
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(20px);
  background: #fff;
}

/* Timeout Controls */
.timeout-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.timeout-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.timeout-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.timeout-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.timeout-value {
  font-size: 14px;
  font-weight: 600;
  color: #7c6ff7;
  min-width: 24px;
  text-align: center;
}

/* Vault Icon */
.vault-icon-small {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Shortcuts */
.shortcut-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
}

.shortcut-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.shortcut-key {
  font-family: 'SF Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.06);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>

<template>
  <div class="settings-page">
    <div class="page-header">
      <span class="page-title">Profile</span>
    </div>

    <div class="settings-content">
      <!-- Profile Section -->
      <div class="settings-section">
        <span class="section-title">Profile</span>

        <div class="setting-card">
          <div class="profile-header">
            <button class="profile-avatar-btn" @click="changeAvatar">
              <div class="profile-avatar">
                <img v-if="store.currentUser?.avatar" :src="store.currentUser.avatar" alt="" />
                <v-icon v-else size="28" color="rgba(255,255,255,0.5)">mdi-account</v-icon>
              </div>
              <div class="avatar-edit-badge">
                <v-icon size="10" color="white">mdi-pencil</v-icon>
              </div>
            </button>
            <div class="profile-info">
              <span class="profile-display-name">{{ store.currentUser?.displayName }}</span>
              <span class="profile-username">@{{ store.currentUser?.username }}</span>
            </div>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Display Name</span>
              <span class="setting-desc">{{ editingName ? 'Press Enter to save' : store.currentUser?.displayName }}</span>
            </div>
            <div v-if="!editingName" class="edit-btn-wrap">
              <button class="icon-btn" @click="startEditName">
                <v-icon size="14">mdi-pencil</v-icon>
              </button>
            </div>
            <div v-else class="name-edit-row">
              <input
                ref="nameInput"
                v-model="newDisplayName"
                class="inline-input"
                placeholder="Display Name"
                @keyup.enter="saveName"
                @keyup.escape="editingName = false"
              />
              <button class="icon-btn save" @click="saveName">
                <v-icon size="14">mdi-check</v-icon>
              </button>
            </div>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Reset Avatar</span>
              <span class="setting-desc">Remove profile picture</span>
            </div>
            <button class="icon-btn" :disabled="!store.currentUser?.avatar" @click="resetAvatar">
              <v-icon size="14">mdi-image-remove</v-icon>
            </button>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Delete Account</span>
              <span class="setting-desc">Permanently remove your account and vault</span>
            </div>
            <button class="icon-btn danger" @click="showDeleteConfirm = true">
              <v-icon size="14">mdi-delete</v-icon>
            </button>
          </div>
        </div>
      </div>

      <!-- Settings Section -->
      <div class="settings-section">
        <span class="section-title">Settings</span>

        <div class="setting-card">
          <div class="color-wheel-section">
            <div class="color-wheel-wrap">
              <canvas
                ref="wheelCanvas"
                :width="wheelDiameter"
                :height="wheelDiameter"
                class="color-wheel"
                @mousedown="onWheelMouseDown"
                @touchstart.prevent="onWheelTouchStart"
              />
            </div>
            <div class="wheel-presets">
              <button
                v-for="c in accentPresets"
                :key="c.hue"
                class="preset-dot"
                :class="{ active: store.accentColor === c.hue }"
                :style="{ background: `hsl(${c.hue}, 56%, 55%)` }"
                :title="c.name"
                @click="changeAccent(c.hue)"
              />
            </div>
            <div class="hex-input-row">
              <div class="hex-preview" :style="{ background: currentHex }"></div>
              <input
                :value="currentHex"
                class="hex-input"
                maxlength="7"
                spellcheck="false"
                @keyup.enter="onHexSubmit($event)"
                @blur="onHexSubmit($event)"
              />
            </div>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Theme</span>
              <span class="setting-desc">{{ store.theme === 'dark' ? 'Dark mode' : 'Light mode' }}</span>
            </div>
            <button class="theme-toggle-btn" @click="toggleTheme">
              <v-icon size="16">{{ store.theme === 'dark' ? 'mdi-weather-night' : 'mdi-white-balance-sunny' }}</v-icon>
            </button>
          </div>

          <div class="setting-divider"></div>

          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Reset Settings</span>
              <span class="setting-desc">Restore default accent &amp; theme</span>
            </div>
            <button class="icon-btn" @click="resetSettings">
              <v-icon size="14">mdi-restore</v-icon>
            </button>
          </div>
        </div>
      </div>

      <!-- Delete account confirmation dialog -->
      <teleport to="body">
        <transition name="overlay-fade">
          <div v-if="showDeleteConfirm" class="delete-overlay" @click.self="showDeleteConfirm = false">
            <div class="delete-dialog">
              <div class="delete-dialog-header">
                <v-icon size="20" color="#e74c3c">mdi-alert-circle</v-icon>
                <span>Delete Account</span>
              </div>
              <p class="delete-dialog-text">This will permanently delete your account, vault, and all stored credentials. Enter your password to confirm.</p>
              <div class="delete-input-group" :class="{ focused: deleteInputFocused }">
                <input
                  v-model="deletePassword"
                  type="password"
                  placeholder="Enter password to confirm"
                  class="custom-input"
                  @focus="deleteInputFocused = true"
                  @blur="deleteInputFocused = false"
                  @keyup.enter="confirmDelete"
                />
              </div>
              <div class="delete-dialog-actions">
                <button class="cancel-btn" @click="showDeleteConfirm = false; deletePassword = ''">Cancel</button>
                <button class="confirm-delete-btn" :disabled="!deletePassword || deleting" @click="confirmDelete">
                  <span v-if="!deleting">Delete</span>
                  <v-progress-circular v-else indeterminate size="14" width="2" />
                </button>
              </div>
            </div>
          </div>
        </transition>
      </teleport>

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
        <span class="section-title">Vault</span>

        <div class="setting-card">
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">{{ store.entryCount }} {{ store.entryCount === 1 ? 'entry' : 'entries' }}</span>
              <span class="setting-desc">{{ store.favoriteCount }} favorites</span>
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
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'
import { useRouter } from 'vue-router'

const store = useVaultStore()
const router = useRouter()

// HSL ↔ Hex conversion (fixed saturation=56%, lightness=55%)
function hslToHex(h: number): string {
  const s = 0.56, l = 0.55
  const a = s * Math.min(l, 1 - l)
  const f = (n: number) => {
    const k = (n + h / 30) % 12
    const c = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    return Math.round(255 * c).toString(16).padStart(2, '0')
  }
  return `#${f(0)}${f(8)}${f(4)}`
}

function hexToHue(hex: string): number | null {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!m) return null
  const r = parseInt(m[1], 16) / 255
  const g = parseInt(m[2], 16) / 255
  const b = parseInt(m[3], 16) / 255
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  if (max === min) return 0
  const d = max - min
  let h = 0
  switch (max) {
    case r: h = ((g - b) / d + (g < b ? 6 : 0)) * 60; break
    case g: h = ((b - r) / d + 2) * 60; break
    case b: h = ((r - g) / d + 4) * 60; break
  }
  return Math.round(h) % 360
}

const currentHex = computed(() => hslToHex(store.accentColor))

async function onHexSubmit(e: Event) {
  const val = (e.target as HTMLInputElement).value.trim()
  const hue = hexToHue(val)
  if (hue !== null) {
    store.applyAccentColor(hue)
    drawWheel()
    await store.updateProfile({ accentColor: hue })
  }
  // Reset input to current hex if invalid
  (e.target as HTMLInputElement).value = currentHex.value
}

// Accent color presets
const accentPresets = [
  { name: 'Purple', hue: 248 },
  { name: 'Blue', hue: 217 },
  { name: 'Teal', hue: 174 },
  { name: 'Green', hue: 152 },
  { name: 'Rose', hue: 340 },
  { name: 'Orange', hue: 24 },
]

// Color wheel
const wheelCanvas = ref<HTMLCanvasElement | null>(null)
const wheelDiameter = 160
const OUTER_R = 74
const INNER_R = 50

function drawWheel() {
  const canvas = wheelCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  const cx = wheelDiameter / 2
  const cy = wheelDiameter / 2

  ctx.clearRect(0, 0, wheelDiameter, wheelDiameter)

  // Draw hue ring
  for (let deg = 0; deg < 360; deg++) {
    const rad = (deg - 90) * Math.PI / 180
    const rad2 = (deg + 1.5 - 90) * Math.PI / 180
    ctx.beginPath()
    ctx.arc(cx, cy, OUTER_R, rad, rad2)
    ctx.arc(cx, cy, INNER_R, rad2, rad, true)
    ctx.closePath()
    ctx.fillStyle = `hsl(${deg}, 56%, 55%)`
    ctx.fill()
  }

  // Center filled circle with current color
  ctx.beginPath()
  ctx.arc(cx, cy, INNER_R - 6, 0, Math.PI * 2)
  ctx.fillStyle = `hsl(${store.accentColor}, 56%, 55%)`
  ctx.fill()

  // Hue degree label in center
  ctx.fillStyle = '#fff'
  ctx.font = '600 14px -apple-system, BlinkMacSystemFont, sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(`${store.accentColor}°`, cx, cy)

  // Selection handle on the ring
  const hueRad = (store.accentColor - 90) * Math.PI / 180
  const midR = (OUTER_R + INNER_R) / 2
  const hx = cx + midR * Math.cos(hueRad)
  const hy = cy + midR * Math.sin(hueRad)

  // Handle outer (white ring with shadow)
  ctx.save()
  ctx.shadowColor = 'rgba(0, 0, 0, 0.4)'
  ctx.shadowBlur = 6
  ctx.shadowOffsetY = 2
  ctx.beginPath()
  ctx.arc(hx, hy, 11, 0, Math.PI * 2)
  ctx.fillStyle = '#fff'
  ctx.fill()
  ctx.restore()

  // Handle inner color
  ctx.beginPath()
  ctx.arc(hx, hy, 8, 0, Math.PI * 2)
  ctx.fillStyle = `hsl(${store.accentColor}, 56%, 55%)`
  ctx.fill()
}

function getHueFromEvent(e: MouseEvent | Touch): number {
  const canvas = wheelCanvas.value!
  const rect = canvas.getBoundingClientRect()
  const scaleX = wheelDiameter / rect.width
  const scaleY = wheelDiameter / rect.height
  const x = (e.clientX - rect.left) * scaleX - wheelDiameter / 2
  const y = (e.clientY - rect.top) * scaleY - wheelDiameter / 2
  let angle = Math.atan2(y, x) * 180 / Math.PI + 90
  if (angle < 0) angle += 360
  return Math.round(angle) % 360
}

function onWheelMouseDown(e: MouseEvent) {
  const hue = getHueFromEvent(e)
  store.applyAccentColor(hue)
  drawWheel()

  const onMove = (ev: MouseEvent) => {
    const h = getHueFromEvent(ev)
    store.applyAccentColor(h)
    drawWheel()
  }
  const onUp = async (ev: MouseEvent) => {
    const h = getHueFromEvent(ev)
    await store.updateProfile({ accentColor: h })
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function onWheelTouchStart(e: TouchEvent) {
  const touch = e.touches[0]
  const hue = getHueFromEvent(touch)
  store.applyAccentColor(hue)
  drawWheel()

  const onMove = (ev: TouchEvent) => {
    const h = getHueFromEvent(ev.touches[0])
    store.applyAccentColor(h)
    drawWheel()
  }
  const onEnd = async (ev: TouchEvent) => {
    const lastTouch = ev.changedTouches[0]
    const h = getHueFromEvent(lastTouch)
    await store.updateProfile({ accentColor: h })
    document.removeEventListener('touchmove', onMove)
    document.removeEventListener('touchend', onEnd)
  }
  document.addEventListener('touchmove', onMove)
  document.addEventListener('touchend', onEnd)
}

async function changeAccent(hue: number) {
  store.applyAccentColor(hue)
  drawWheel()
  await store.updateProfile({ accentColor: hue })
}

async function toggleTheme() {
  const next = store.theme === 'dark' ? 'light' : 'dark'
  store.applyTheme(next)
  await store.updateProfile({ theme: next })
}

async function resetAvatar() {
  await store.updateProfile({ avatar: '' })
}

async function resetSettings() {
  store.applyAccentColor(248)
  store.applyTheme('dark')
  await store.updateProfile({ accentColor: 248, theme: 'dark' })
  drawWheel()
}

onMounted(() => {
  nextTick(() => drawWheel())
})

watch(() => store.accentColor, () => drawWheel())

// Profile editing
const editingName = ref(false)
const newDisplayName = ref('')
const nameInput = ref<HTMLInputElement | null>(null)
const showDeleteConfirm = ref(false)
const deletePassword = ref('')
const deleteInputFocused = ref(false)
const deleting = ref(false)

function startEditName() {
  newDisplayName.value = store.currentUser?.displayName || ''
  editingName.value = true
  nextTick(() => {
    nameInput.value?.focus()
  })
}

async function saveName() {
  if (!newDisplayName.value.trim()) return
  await store.updateProfile({ displayName: newDisplayName.value.trim() })
  editingName.value = false
}

async function changeAvatar() {
  const icon = await store.pickImage()
  if (icon) {
    await store.updateProfile({ avatar: icon })
  }
}

async function confirmDelete() {
  if (!deletePassword.value) return
  deleting.value = true
  const ok = await store.deleteAccount(deletePassword.value)
  deleting.value = false
  if (ok) {
    showDeleteConfirm.value = false
    deletePassword.value = ''
    router.push('/')
  }
}

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
  background: var(--bg-primary);
  padding-bottom: 60px;
}

.page-header {
  padding: 12px 16px;
  -webkit-app-region: drag;
}

.page-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
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
  color: var(--text-muted);
  margin-bottom: 8px;
  padding-left: 4px;
}

.setting-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
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
  color: var(--text-primary);
}

.setting-desc {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 1px;
}

.setting-divider {
  height: 1px;
  background: var(--border-light);
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
  background: var(--bg-hover);
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
  background: linear-gradient(135deg, hsl(var(--accent-h), var(--accent-s), 47%), hsl(var(--accent-h), var(--accent-s), 58%));
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
  background: var(--bg-hover);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.timeout-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
  color: var(--text-primary);
}

.timeout-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.timeout-value {
  font-size: 14px;
  font-weight: 600;
  color: hsl(var(--accent-h), var(--accent-s), 70%);
  min-width: 24px;
  text-align: center;
}

/* Color Wheel */
.color-wheel-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 14px;
  gap: 14px;
}

.color-wheel-wrap {
  position: relative;
}

.color-wheel {
  display: block;
  width: 160px;
  height: 160px;
  cursor: crosshair;
  border-radius: 50%;
  transition: transform 0.15s;
}

.color-wheel:active {
  transform: scale(1.02);
}

.wheel-presets {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.preset-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  padding: 0;
}

.preset-dot:hover {
  transform: scale(1.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.preset-dot.active {
  border-color: var(--text-primary);
  transform: scale(1.15);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.15);
}

/* Hex Input */
.hex-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hex-preview {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 2px solid var(--border-primary);
  flex-shrink: 0;
}

.hex-input {
  width: 80px;
  background: var(--bg-hover);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  color: var(--text-primary);
  font-family: 'SF Mono', 'JetBrains Mono', monospace;
  font-size: 12px;
  padding: 6px 10px;
  outline: none;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: border-color 0.2s;
}

.hex-input:focus {
  border-color: hsla(var(--accent-h), var(--accent-s), 47%, 0.5);
}

/* Theme Toggle */
.theme-toggle-btn {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: var(--bg-hover);
  color: hsl(var(--accent-h), var(--accent-s), 65%);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.theme-toggle-btn:hover {
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.2);
  transform: scale(1.05);
}

.theme-toggle-btn:active {
  transform: scale(0.95);
}

/* Vault Icon */
.vault-icon-small {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, hsl(var(--accent-h), var(--accent-s), 47%), hsl(var(--accent-h), var(--accent-s), 58%));
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Profile */
.profile-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 14px;
}

.profile-avatar-btn {
  position: relative;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}

.profile-avatar {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: all 0.2s;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar-btn:hover .profile-avatar {
  box-shadow: 0 0 0 2px hsla(var(--accent-h), var(--accent-s), 47%, 0.5);
}

.avatar-edit-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: linear-gradient(135deg, hsl(var(--accent-h), var(--accent-s), 47%), hsl(var(--accent-h), var(--accent-s), 58%));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.profile-display-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.profile-username {
  font-size: 11px;
  color: var(--text-muted);
}

.icon-btn {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 8px;
  background: var(--bg-hover);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.icon-btn:hover {
  background: var(--scrollbar-thumb-hover);
  color: var(--text-primary);
}

.icon-btn.save {
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.3);
  color: hsl(var(--accent-h), var(--accent-s), 70%);
}

.icon-btn.save:hover {
  background: hsla(var(--accent-h), var(--accent-s), 47%, 0.5);
  color: var(--text-primary);
}

.icon-btn.danger:hover {
  background: rgba(231, 76, 60, 0.15);
  color: #e74c3c;
}

.name-edit-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.inline-input {
  background: var(--bg-hover);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 12px;
  padding: 6px 10px;
  outline: none;
  width: 120px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.inline-input:focus {
  border-color: hsla(var(--accent-h), var(--accent-s), 47%, 0.5);
}

/* Delete dialog */
.delete-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.delete-dialog {
  width: 280px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-primary);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 16px 48px var(--shadow-color);
}

.delete-dialog-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.delete-dialog-text {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 14px;
}

.delete-input-group {
  background: var(--bg-surface);
  border: 1px solid var(--border-primary);
  border-radius: 10px;
  padding: 0 12px;
  margin-bottom: 14px;
  transition: all 0.2s;
}

.delete-input-group.focused {
  border-color: rgba(231, 76, 60, 0.4);
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.08);
}

.delete-input-group .custom-input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13px;
  padding: 12px 0;
  font-family: inherit;
}

.delete-dialog-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.cancel-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.confirm-delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: #e74c3c;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-delete-btn:hover:not(:disabled) {
  background: #c0392b;
}

.confirm-delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Overlay transition */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
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
  color: var(--text-primary);
}

.shortcut-key {
  font-family: 'SF Mono', monospace;
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--bg-hover);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid var(--border-primary);
}
</style>

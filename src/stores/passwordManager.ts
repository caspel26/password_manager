import { ref, computed, toRaw } from 'vue'
import { defineStore } from 'pinia'
import type { VaultEntry, VaultSettings } from '@/types/electron'

export const useVaultStore = defineStore('vault', () => {
  // ── State ──────────────────────────────────────────────────
  const unlocked = ref(false)
  const vaultName = ref<string | null>(null)
  const entries = ref<VaultEntry[]>([])
  const searchQuery = ref('')
  const generatedPassword = ref<string | null>(null)
  const snackbar = ref({ show: false, message: '', color: 'success', action: null as (() => void) | null })
  const settings = ref<VaultSettings>({
    autoLockMinutes: 5,
    autoLockEnabled: true,
  })
  const lastDeletedEntry = ref<VaultEntry | null>(null)

  // ── Computed ───────────────────────────────────────────────
  const filteredEntries = computed(() => {
    const q = searchQuery.value.toLowerCase().trim()
    let result = entries.value
    if (q) {
      result = result.filter(
        (e) =>
          e.service.toLowerCase().includes(q) ||
          e.username.toLowerCase().includes(q) ||
          e.url.toLowerCase().includes(q),
      )
    }
    // Sort favorites first, then by service name
    return result.sort((a, b) => {
      if (a.favorite && !b.favorite) return -1
      if (!a.favorite && b.favorite) return 1
      return a.service.localeCompare(b.service)
    })
  })

  const entryCount = computed(() => entries.value.length)
  const favoriteCount = computed(() => entries.value.filter((e) => e.favorite).length)

  // ── Helpers ────────────────────────────────────────────────
  function notify(message: string, color: 'success' | 'error' | 'warning' | 'info' = 'success', action: (() => void) | null = null) {
    snackbar.value = { show: true, message, color, action }
  }

  function trackActivity() {
    window.electronAPI.activity()
  }

  // ── Vault lifecycle ────────────────────────────────────────
  async function createVault(password: string, confirm: string) {
    if (!password) { notify('Master password is required', 'error'); return false }
    if (password !== confirm) { notify('Passwords do not match', 'error'); return false }
    if (password.length < 8) { notify('Password must be at least 8 characters', 'error'); return false }

    const res = await window.electronAPI.createVault(password)
    if (!res.success) { notify(res.error || 'Failed to create vault', 'error'); return false }
    unlocked.value = true
    vaultName.value = res.vaultName || null
    entries.value = []
    settings.value = res.settings || { autoLockMinutes: 5, autoLockEnabled: true }
    notify('Vault created')
    return true
  }

  async function unlock(password: string) {
    if (!password) { notify('Master password is required', 'error'); return false }

    const res = await window.electronAPI.unlockVault(password)
    if (!res.success) { notify(res.error || 'Failed to unlock vault', 'error'); return false }
    unlocked.value = true
    vaultName.value = res.vaultName || null
    entries.value = res.entries || []
    settings.value = res.settings || { autoLockMinutes: 5, autoLockEnabled: true }
    return true
  }

  async function lock() {
    await window.electronAPI.lockVault()
    unlocked.value = false
    vaultName.value = null
    entries.value = []
    searchQuery.value = ''
    generatedPassword.value = null
  }

  // ── Entry CRUD ─────────────────────────────────────────────
  async function addEntry(data: {
    service: string; username: string; password: string; url?: string; notes?: string; icon?: string; favorite?: boolean
  }) {
    if (!data.service || !data.username || !data.password) {
      notify('Service, username, and password are required', 'error')
      return false
    }
    trackActivity()
    const res = await window.electronAPI.addEntry({ ...toRaw(data) })
    if (!res.success) { notify(res.error || 'Failed to add entry', 'error'); return false }
    if (res.entry) entries.value.push(res.entry)
    notify('Entry saved')
    return true
  }

  async function updateEntry(data: {
    id: string; service: string; username: string; password: string; url?: string; notes?: string; icon?: string; favorite?: boolean
  }) {
    if (!data.service || !data.username || !data.password) {
      notify('Service, username, and password are required', 'error')
      return false
    }
    trackActivity()
    const res = await window.electronAPI.updateEntry({ ...toRaw(data) })
    if (!res.success) { notify(res.error || 'Failed to update', 'error'); return false }
    const idx = entries.value.findIndex((e) => e.id === data.id)
    if (idx !== -1 && res.entry) entries.value[idx] = res.entry
    notify('Entry updated')
    return true
  }

  async function deleteEntry(id: string) {
    trackActivity()
    // Store entry before deleting for potential undo
    const entryToDelete = entries.value.find((e) => e.id === id)
    const res = await window.electronAPI.deleteEntry(id)
    if (!res.success) { notify(res.error || 'Failed to delete', 'error'); return false }
    entries.value = entries.value.filter((e) => e.id !== id)
    if (entryToDelete) {
      lastDeletedEntry.value = entryToDelete
      notify('Entry deleted', 'info', () => restoreEntry())
    }
    return true
  }

  async function restoreEntry() {
    if (!lastDeletedEntry.value) return false
    const entry = lastDeletedEntry.value
    trackActivity()
    const res = await window.electronAPI.addEntry({
      service: entry.service,
      username: entry.username,
      password: entry.password,
      url: entry.url,
      notes: entry.notes,
      icon: entry.icon,
      favorite: entry.favorite,
    })
    if (!res.success) { notify(res.error || 'Failed to restore', 'error'); return false }
    if (res.entry) entries.value.push(res.entry)
    lastDeletedEntry.value = null
    notify('Entry restored')
    return true
  }

  async function toggleFavorite(id: string) {
    trackActivity()
    const res = await window.electronAPI.toggleFavorite(id)
    if (!res.success) { notify(res.error || 'Failed to update favorite', 'error'); return false }
    const idx = entries.value.findIndex((e) => e.id === id)
    if (idx !== -1 && res.entry) entries.value[idx] = res.entry
    return true
  }

  // ── Settings ───────────────────────────────────────────────
  async function updateSettings(newSettings: Partial<VaultSettings>) {
    trackActivity()
    const res = await window.electronAPI.updateSettings(newSettings)
    if (!res.success) { notify(res.error || 'Failed to update settings', 'error'); return false }
    if (res.settings) settings.value = res.settings
    notify('Settings saved')
    return true
  }

  // ── Icons ────────────────────────────────────────────────────
  async function fetchFavicon(url: string) {
    trackActivity()
    const res = await window.electronAPI.fetchFavicon(url)
    if (!res.success) return null
    return res.icon || null
  }

  async function pickImage() {
    trackActivity()
    const res = await window.electronAPI.pickImage()
    if (!res.success) return null
    return res.icon || null
  }

  // ── Password generator ─────────────────────────────────────
  async function generatePassword(length?: number) {
    trackActivity()
    const res = await window.electronAPI.generatePassword(length)
    if (!res.success) { notify(res.error || 'Generation failed', 'error'); return null }
    generatedPassword.value = res.password || null
    return res.password || null
  }

  return {
    unlocked,
    vaultName,
    entries,
    searchQuery,
    generatedPassword,
    snackbar,
    settings,
    lastDeletedEntry,
    filteredEntries,
    entryCount,
    favoriteCount,
    notify,
    trackActivity,
    createVault,
    unlock,
    lock,
    addEntry,
    updateEntry,
    deleteEntry,
    restoreEntry,
    toggleFavorite,
    updateSettings,
    fetchFavicon,
    pickImage,
    generatePassword,
  }
})

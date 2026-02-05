import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { VaultEntry } from '@/types/electron'

export const useVaultStore = defineStore('vault', () => {
  // ── State ──────────────────────────────────────────────────
  const unlocked = ref(false)
  const vaultName = ref<string | null>(null)
  const entries = ref<VaultEntry[]>([])
  const searchQuery = ref('')
  const generatedPassword = ref<string | null>(null)
  const snackbar = ref({ show: false, message: '', color: 'success' })

  // ── Computed ───────────────────────────────────────────────
  const filteredEntries = computed(() => {
    const q = searchQuery.value.toLowerCase().trim()
    if (!q) return entries.value
    return entries.value.filter(
      (e) =>
        e.service.toLowerCase().includes(q) ||
        e.username.toLowerCase().includes(q) ||
        e.url.toLowerCase().includes(q),
    )
  })

  const entryCount = computed(() => entries.value.length)

  // ── Helpers ────────────────────────────────────────────────
  function notify(message: string, color: 'success' | 'error' | 'warning' | 'info' = 'success') {
    snackbar.value = { show: true, message, color }
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
    service: string; username: string; password: string; url?: string; notes?: string
  }) {
    if (!data.service || !data.username || !data.password) {
      notify('Service, username, and password are required', 'error')
      return false
    }
    const res = await window.electronAPI.addEntry(data)
    if (!res.success) { notify(res.error || 'Failed to add entry', 'error'); return false }
    if (res.entry) entries.value.push(res.entry)
    notify('Entry saved')
    return true
  }

  async function updateEntry(data: {
    id: string; service: string; username: string; password: string; url?: string; notes?: string
  }) {
    if (!data.service || !data.username || !data.password) {
      notify('Service, username, and password are required', 'error')
      return false
    }
    const res = await window.electronAPI.updateEntry(data)
    if (!res.success) { notify(res.error || 'Failed to update', 'error'); return false }
    const idx = entries.value.findIndex((e) => e.id === data.id)
    if (idx !== -1 && res.entry) entries.value[idx] = res.entry
    notify('Entry updated')
    return true
  }

  async function deleteEntry(id: string) {
    const res = await window.electronAPI.deleteEntry(id)
    if (!res.success) { notify(res.error || 'Failed to delete', 'error'); return false }
    entries.value = entries.value.filter((e) => e.id !== id)
    notify('Entry deleted')
    return true
  }

  // ── Password generator ─────────────────────────────────────
  async function generatePassword(length?: number) {
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
    filteredEntries,
    entryCount,
    notify,
    createVault,
    unlock,
    lock,
    addEntry,
    updateEntry,
    deleteEntry,
    generatePassword,
  }
})

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useVaultStore } from '@/stores/passwordManager'

const mockElectronAPI = {
  createVault: vi.fn(),
  unlockVault: vi.fn(),
  lockVault: vi.fn(),
  isUnlocked: vi.fn(),
  getEntries: vi.fn(),
  addEntry: vi.fn(),
  updateEntry: vi.fn(),
  deleteEntry: vi.fn(),
  generatePassword: vi.fn(),
}

vi.stubGlobal('window', {
  ...globalThis.window,
  electronAPI: mockElectronAPI,
})

describe('Vault Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  // ── createVault ──────────────────────────────────────────────

  describe('createVault', () => {
    it('should reject empty password', async () => {
      const store = useVaultStore()
      expect(await store.createVault('', '')).toBe(false)
      expect(store.snackbar.message).toBe('Master password is required')
      expect(mockElectronAPI.createVault).not.toHaveBeenCalled()
    })

    it('should reject mismatched passwords', async () => {
      const store = useVaultStore()
      expect(await store.createVault('password1', 'password2')).toBe(false)
      expect(store.snackbar.message).toBe('Passwords do not match')
    })

    it('should reject short passwords', async () => {
      const store = useVaultStore()
      expect(await store.createVault('short', 'short')).toBe(false)
      expect(store.snackbar.message).toBe('Password must be at least 8 characters')
    })

    it('should create vault on success', async () => {
      mockElectronAPI.createVault.mockResolvedValue({
        success: true,
        vaultName: 'passwords.vault',
      })

      const store = useVaultStore()
      const result = await store.createVault('secure-pass-123', 'secure-pass-123')

      expect(result).toBe(true)
      expect(store.unlocked).toBe(true)
      expect(store.vaultName).toBe('passwords.vault')
      expect(store.entries).toEqual([])
    })

    it('should handle API failure', async () => {
      mockElectronAPI.createVault.mockResolvedValue({
        success: false,
        error: 'Cancelled',
      })

      const store = useVaultStore()
      expect(await store.createVault('password123', 'password123')).toBe(false)
      expect(store.unlocked).toBe(false)
    })
  })

  // ── unlock ───────────────────────────────────────────────────

  describe('unlock', () => {
    it('should reject empty password', async () => {
      const store = useVaultStore()
      expect(await store.unlock('')).toBe(false)
      expect(mockElectronAPI.unlockVault).not.toHaveBeenCalled()
    })

    it('should unlock and load entries on success', async () => {
      const entries = [
        { id: '1', service: 'github', username: 'u', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
      ]
      mockElectronAPI.unlockVault.mockResolvedValue({
        success: true,
        vaultName: 'my.vault',
        entries,
      })

      const store = useVaultStore()
      expect(await store.unlock('master-pass')).toBe(true)
      expect(store.unlocked).toBe(true)
      expect(store.vaultName).toBe('my.vault')
      expect(store.entries).toEqual(entries)
    })

    it('should show error on wrong password', async () => {
      mockElectronAPI.unlockVault.mockResolvedValue({
        success: false,
        error: 'Invalid master password',
      })

      const store = useVaultStore()
      expect(await store.unlock('wrong')).toBe(false)
      expect(store.snackbar.message).toBe('Invalid master password')
      expect(store.unlocked).toBe(false)
    })
  })

  // ── lock ─────────────────────────────────────────────────────

  describe('lock', () => {
    it('should clear all state', async () => {
      mockElectronAPI.lockVault.mockResolvedValue({ success: true })

      const store = useVaultStore()
      store.unlocked = true
      store.vaultName = 'test.vault'
      store.entries = [{ id: '1', service: 's', username: 'u', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' }]
      store.searchQuery = 'query'

      await store.lock()

      expect(store.unlocked).toBe(false)
      expect(store.vaultName).toBeNull()
      expect(store.entries).toEqual([])
      expect(store.searchQuery).toBe('')
      expect(store.generatedPassword).toBeNull()
    })
  })

  // ── addEntry ─────────────────────────────────────────────────

  describe('addEntry', () => {
    it('should require service, username, and password', async () => {
      const store = useVaultStore()
      expect(await store.addEntry({ service: '', username: 'u', password: 'p' })).toBe(false)
      expect(await store.addEntry({ service: 's', username: '', password: 'p' })).toBe(false)
      expect(await store.addEntry({ service: 's', username: 'u', password: '' })).toBe(false)
      expect(mockElectronAPI.addEntry).not.toHaveBeenCalled()
    })

    it('should add entry to local state on success', async () => {
      const newEntry = {
        id: 'abc', service: 'github', username: 'user', password: 'pass',
        url: '', notes: '', createdAt: '2024-01-01', updatedAt: '2024-01-01',
      }
      mockElectronAPI.addEntry.mockResolvedValue({ success: true, entry: newEntry })

      const store = useVaultStore()
      expect(await store.addEntry({ service: 'github', username: 'user', password: 'pass' })).toBe(true)
      expect(store.entries).toHaveLength(1)
      expect(store.entries[0]).toEqual(newEntry)
    })
  })

  // ── updateEntry ──────────────────────────────────────────────

  describe('updateEntry', () => {
    it('should require all fields', async () => {
      const store = useVaultStore()
      expect(await store.updateEntry({ id: '1', service: '', username: 'u', password: 'p' })).toBe(false)
    })

    it('should update entry in local state', async () => {
      const original = {
        id: '1', service: 'github', username: 'old', password: 'old',
        url: '', notes: '', createdAt: '2024-01-01', updatedAt: '2024-01-01',
      }
      const updated = { ...original, username: 'new', updatedAt: '2024-02-01' }
      mockElectronAPI.updateEntry.mockResolvedValue({ success: true, entry: updated })

      const store = useVaultStore()
      store.entries = [original]

      expect(await store.updateEntry({ id: '1', service: 'github', username: 'new', password: 'old' })).toBe(true)
      expect(store.entries[0].username).toBe('new')
    })
  })

  // ── deleteEntry ──────────────────────────────────────────────

  describe('deleteEntry', () => {
    it('should remove entry from local state', async () => {
      mockElectronAPI.deleteEntry.mockResolvedValue({ success: true })

      const store = useVaultStore()
      store.entries = [
        { id: '1', service: 'a', username: 'u', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
        { id: '2', service: 'b', username: 'u', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
      ]

      expect(await store.deleteEntry('1')).toBe(true)
      expect(store.entries).toHaveLength(1)
      expect(store.entries[0].id).toBe('2')
    })

    it('should not modify entries on failure', async () => {
      mockElectronAPI.deleteEntry.mockResolvedValue({ success: false, error: 'Not found' })

      const store = useVaultStore()
      store.entries = [
        { id: '1', service: 'a', username: 'u', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
      ]

      expect(await store.deleteEntry('1')).toBe(false)
      expect(store.entries).toHaveLength(1)
    })
  })

  // ── generatePassword ─────────────────────────────────────────

  describe('generatePassword', () => {
    it('should set generatedPassword on success', async () => {
      mockElectronAPI.generatePassword.mockResolvedValue({
        success: true,
        password: 'Xk9!mQ2@rT5#wP8$',
      })

      const store = useVaultStore()
      const result = await store.generatePassword(24)
      expect(result).toBe('Xk9!mQ2@rT5#wP8$')
      expect(store.generatedPassword).toBe('Xk9!mQ2@rT5#wP8$')
    })

    it('should return null on failure', async () => {
      mockElectronAPI.generatePassword.mockResolvedValue({ success: false, error: 'fail' })

      const store = useVaultStore()
      expect(await store.generatePassword()).toBeNull()
    })
  })

  // ── filteredEntries ──────────────────────────────────────────

  describe('filteredEntries', () => {
    it('should return all entries when search is empty', () => {
      const store = useVaultStore()
      store.entries = [
        { id: '1', service: 'GitHub', username: 'u1', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
        { id: '2', service: 'GitLab', username: 'u2', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
      ]
      store.searchQuery = ''
      expect(store.filteredEntries).toHaveLength(2)
    })

    it('should filter by service name', () => {
      const store = useVaultStore()
      store.entries = [
        { id: '1', service: 'GitHub', username: 'u1', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
        { id: '2', service: 'GitLab', username: 'u2', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
        { id: '3', service: 'Slack', username: 'u3', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
      ]
      store.searchQuery = 'git'
      expect(store.filteredEntries).toHaveLength(2)
    })

    it('should filter by username', () => {
      const store = useVaultStore()
      store.entries = [
        { id: '1', service: 'A', username: 'admin@test.com', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
        { id: '2', service: 'B', username: 'user@test.com', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
      ]
      store.searchQuery = 'admin'
      expect(store.filteredEntries).toHaveLength(1)
      expect(store.filteredEntries[0].id).toBe('1')
    })

    it('should be case-insensitive', () => {
      const store = useVaultStore()
      store.entries = [
        { id: '1', service: 'GitHub', username: 'u', password: 'p', url: '', notes: '', createdAt: '', updatedAt: '' },
      ]
      store.searchQuery = 'GITHUB'
      expect(store.filteredEntries).toHaveLength(1)
    })
  })

  // ── notify ───────────────────────────────────────────────────

  describe('notify', () => {
    it('should update snackbar state', () => {
      const store = useVaultStore()
      store.notify('Test', 'warning')
      expect(store.snackbar).toEqual({ show: true, message: 'Test', color: 'warning' })
    })

    it('should default to success', () => {
      const store = useVaultStore()
      store.notify('OK')
      expect(store.snackbar.color).toBe('success')
    })
  })
})

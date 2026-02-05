export interface PasswordHistoryItem {
  password: string
  changedAt: string
}

export interface VaultSettings {
  autoLockMinutes: number
  autoLockEnabled: boolean
}

export interface IpcResult {
  success: boolean
  error?: string
  vaultName?: string
  password?: string
  entry?: VaultEntry
  entries?: VaultEntry[]
  settings?: VaultSettings
}

export interface VaultEntry {
  id: string
  service: string
  username: string
  password: string
  url: string
  notes: string
  favorite: boolean
  passwordHistory: PasswordHistoryItem[]
  createdAt: string
  updatedAt: string
}

export interface VaultStatus {
  unlocked: boolean
  vaultName: string | null
  entryCount: number
}

export interface ElectronAPI {
  createVault: (password: string) => Promise<IpcResult>
  unlockVault: (password: string) => Promise<IpcResult>
  lockVault: () => Promise<IpcResult>
  isUnlocked: () => Promise<VaultStatus>
  getEntries: () => Promise<IpcResult>
  addEntry: (entry: {
    service: string
    username: string
    password: string
    url?: string
    notes?: string
    favorite?: boolean
  }) => Promise<IpcResult>
  updateEntry: (entry: {
    id: string
    service: string
    username: string
    password: string
    url?: string
    notes?: string
    favorite?: boolean
  }) => Promise<IpcResult>
  deleteEntry: (id: string) => Promise<IpcResult>
  toggleFavorite: (id: string) => Promise<IpcResult>
  getSettings: () => Promise<IpcResult>
  updateSettings: (settings: Partial<VaultSettings>) => Promise<IpcResult>
  generatePassword: (length?: number) => Promise<IpcResult>
  activity: () => Promise<{ success: boolean }>
  onShortcutNewEntry: (callback: () => void) => void
  onShortcutLock: (callback: () => void) => void
  onShortcutSearch: (callback: () => void) => void
  onShortcutGenerator: (callback: () => void) => void
  onAutoLocked: (callback: () => void) => void
  removeAllListeners: (channel: string) => void
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

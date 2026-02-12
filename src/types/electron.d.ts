export interface PasswordHistoryItem {
  password: string
  changedAt: string
}

export interface VaultSettings {
  autoLockMinutes: number
  autoLockEnabled: boolean
}

export interface UserProfile {
  id: string
  username: string
  displayName: string
  avatar: string
  accentColor: number
  theme: 'light' | 'dark'
  createdAt: string
}

export interface IpcResult {
  success: boolean
  error?: string
  vaultName?: string
  password?: string
  entry?: VaultEntry
  entries?: VaultEntry[]
  settings?: VaultSettings
  user?: UserProfile
  users?: UserProfile[]
}

export interface VaultEntry {
  id: string
  service: string
  username: string
  password: string
  url: string
  notes: string
  icon?: string
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
  // User management
  listUsers: () => Promise<IpcResult>
  register: (data: { username: string; password: string; displayName?: string }) => Promise<IpcResult>
  login: (data: { username: string; password: string }) => Promise<IpcResult>
  getProfile: () => Promise<IpcResult>
  updateProfile: (data: { displayName?: string; avatar?: string; accentColor?: number; theme?: 'light' | 'dark' }) => Promise<IpcResult>
  deleteAccount: (password: string) => Promise<IpcResult>

  // Vault lifecycle
  lockVault: () => Promise<IpcResult>
  isUnlocked: () => Promise<VaultStatus>

  // Entries CRUD
  getEntries: () => Promise<IpcResult>
  addEntry: (entry: {
    service: string
    username: string
    password: string
    url?: string
    notes?: string
    icon?: string
    favorite?: boolean
  }) => Promise<IpcResult>
  updateEntry: (entry: {
    id: string
    service: string
    username: string
    password: string
    url?: string
    notes?: string
    icon?: string
    favorite?: boolean
  }) => Promise<IpcResult>
  deleteEntry: (id: string) => Promise<IpcResult>
  toggleFavorite: (id: string) => Promise<IpcResult>

  // Settings
  getSettings: () => Promise<IpcResult>
  updateSettings: (settings: Partial<VaultSettings>) => Promise<IpcResult>

  // Icons
  fetchFavicon: (url: string) => Promise<IpcResult & { icon?: string }>
  pickImage: () => Promise<IpcResult & { icon?: string }>

  // Utility
  generatePassword: (length?: number) => Promise<IpcResult>
  activity: () => Promise<{ success: boolean }>

  // Event listeners
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

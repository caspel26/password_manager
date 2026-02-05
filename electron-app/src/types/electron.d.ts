export interface IpcResult {
  success: boolean
  error?: string
  vaultName?: string
  password?: string
  entry?: VaultEntry
  entries?: VaultEntry[]
}

export interface VaultEntry {
  id: string
  service: string
  username: string
  password: string
  url: string
  notes: string
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
  }) => Promise<IpcResult>
  updateEntry: (entry: {
    id: string
    service: string
    username: string
    password: string
    url?: string
    notes?: string
  }) => Promise<IpcResult>
  deleteEntry: (id: string) => Promise<IpcResult>
  generatePassword: (length?: number) => Promise<IpcResult>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

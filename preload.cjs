const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // User management
  listUsers: () => ipcRenderer.invoke('user:list'),
  register: (data) => ipcRenderer.invoke('user:register', data),
  login: (data) => ipcRenderer.invoke('user:login', data),
  getProfile: () => ipcRenderer.invoke('user:getProfile'),
  updateProfile: (data) => ipcRenderer.invoke('user:updateProfile', data),
  deleteAccount: (password) => ipcRenderer.invoke('user:deleteAccount', { password }),

  // Vault lifecycle
  lockVault: () => ipcRenderer.invoke('vault:lock'),
  isUnlocked: () => ipcRenderer.invoke('vault:isUnlocked'),

  // Entries CRUD
  getEntries: () => ipcRenderer.invoke('vault:getEntries'),
  addEntry: (entry) => ipcRenderer.invoke('vault:addEntry', entry),
  updateEntry: (entry) => ipcRenderer.invoke('vault:updateEntry', entry),
  deleteEntry: (id) => ipcRenderer.invoke('vault:deleteEntry', { id }),
  toggleFavorite: (id) => ipcRenderer.invoke('vault:toggleFavorite', { id }),

  // Settings
  getSettings: () => ipcRenderer.invoke('vault:getSettings'),
  updateSettings: (settings) => ipcRenderer.invoke('vault:updateSettings', settings),

  // Icons
  fetchFavicon: (url) => ipcRenderer.invoke('vault:fetchFavicon', { url }),
  pickImage: () => ipcRenderer.invoke('vault:pickImage'),

  // Utility
  generatePassword: (length) => ipcRenderer.invoke('vault:generatePassword', { length }),
  activity: () => ipcRenderer.invoke('vault:activity'),

  // Event listeners
  onShortcutNewEntry: (callback) => ipcRenderer.on('shortcut:new-entry', callback),
  onShortcutLock: (callback) => ipcRenderer.on('shortcut:lock', callback),
  onShortcutSearch: (callback) => ipcRenderer.on('shortcut:search', callback),
  onShortcutGenerator: (callback) => ipcRenderer.on('shortcut:generator', callback),
  onAutoLocked: (callback) => ipcRenderer.on('vault:auto-locked', callback),
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
})

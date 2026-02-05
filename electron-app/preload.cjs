const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // Vault lifecycle
  createVault: (password) => ipcRenderer.invoke('vault:create', { password }),
  unlockVault: (password) => ipcRenderer.invoke('vault:unlock', { password }),
  lockVault: () => ipcRenderer.invoke('vault:lock'),
  isUnlocked: () => ipcRenderer.invoke('vault:isUnlocked'),

  // Entries CRUD
  getEntries: () => ipcRenderer.invoke('vault:getEntries'),
  addEntry: (entry) => ipcRenderer.invoke('vault:addEntry', entry),
  updateEntry: (entry) => ipcRenderer.invoke('vault:updateEntry', entry),
  deleteEntry: (id) => ipcRenderer.invoke('vault:deleteEntry', { id }),

  // Utility
  generatePassword: (length) => ipcRenderer.invoke('vault:generatePassword', { length }),
})

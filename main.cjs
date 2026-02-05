const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron')
const { screen } = require('electron')
const path = require('path')
const crypto = require('crypto')
const fs = require('fs')

let win
let autoLockTimer = null
const AUTO_LOCK_MINUTES = 5 // Lock after 5 minutes of inactivity

// ── State ───────────────────────────────────────────────────────

let state = {
  derivedKey: null,            // 32-byte AES key derived from master password
  vaultPath: null,             // path to the .vault file
  entries: [],                 // decrypted entries in memory
  unlocked: false,
  settings: {
    autoLockMinutes: AUTO_LOCK_MINUTES,
    autoLockEnabled: true,
  },
}

// ── Auto-lock ───────────────────────────────────────────────────

function resetAutoLockTimer() {
  if (autoLockTimer) clearTimeout(autoLockTimer)
  if (!state.unlocked || !state.settings.autoLockEnabled) return

  autoLockTimer = setTimeout(() => {
    if (state.unlocked && win) {
      // Lock the vault
      state.derivedKey = null
      state.entries = []
      state.unlocked = false
      // Notify renderer
      win.webContents.send('vault:auto-locked')
    }
  }, state.settings.autoLockMinutes * 60 * 1000)
}

// ── AES-256-GCM symmetric encryption ───────────────────────────

const SALT_LEN = 32
const IV_LEN = 16
const PBKDF2_ITERATIONS = 600000

function deriveKey(password, salt) {
  return crypto.pbkdf2Sync(password, salt, PBKDF2_ITERATIONS, 32, 'sha512')
}

function encrypt(plaintext, key) {
  const iv = crypto.randomBytes(IV_LEN)
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv)
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf-8'), cipher.final()])
  const tag = cipher.getAuthTag()
  return [
    iv.toString('base64'),
    tag.toString('base64'),
    encrypted.toString('base64'),
  ].join(':')
}

function decrypt(packed, key) {
  const [ivB64, tagB64, dataB64] = packed.split(':')
  const iv = Buffer.from(ivB64, 'base64')
  const tag = Buffer.from(tagB64, 'base64')
  const data = Buffer.from(dataB64, 'base64')
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv)
  decipher.setAuthTag(tag)
  return Buffer.concat([decipher.update(data), decipher.final()]).toString('utf-8')
}

// ── Vault file format ───────────────────────────────────────────
// JSON: { salt, verify, entries[], settings? }

function createVault(password, vaultPath) {
  const salt = crypto.randomBytes(SALT_LEN)
  const key = deriveKey(password, salt)
  const verify = encrypt('__vault_ok__', key)
  const vault = {
    salt: salt.toString('base64'),
    verify,
    entries: [],
    settings: { autoLockMinutes: AUTO_LOCK_MINUTES, autoLockEnabled: true },
  }
  fs.writeFileSync(vaultPath, JSON.stringify(vault, null, 2), 'utf-8')
  return { key, salt }
}

function loadVault(password, vaultPath) {
  const raw = fs.readFileSync(vaultPath, 'utf-8')
  const vault = JSON.parse(raw)
  const salt = Buffer.from(vault.salt, 'base64')
  const key = deriveKey(password, salt)
  const check = decrypt(vault.verify, key)
  if (check !== '__vault_ok__') throw new Error('Invalid master password')
  const entries = vault.entries.map((enc) => JSON.parse(decrypt(enc, key)))
  const settings = vault.settings || { autoLockMinutes: AUTO_LOCK_MINUTES, autoLockEnabled: true }
  return { key, salt, entries, settings }
}

function saveVault() {
  if (!state.vaultPath || !state.derivedKey) {
    throw new Error('Cannot save: vault is not open')
  }
  const raw = fs.readFileSync(state.vaultPath, 'utf-8')
  const vault = JSON.parse(raw)
  fs.copyFileSync(state.vaultPath, state.vaultPath + '.bak')
  vault.entries = state.entries.map((e) => encrypt(JSON.stringify(e), state.derivedKey))
  vault.settings = state.settings
  fs.writeFileSync(state.vaultPath, JSON.stringify(vault, null, 2), 'utf-8')
}

// ── Password generator ──────────────────────────────────────────

function generatePassword(length = 24) {
  const lower = 'abcdefghijklmnopqrstuvwxyz'
  const upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const digits = '0123456789'
  const special = '!@#$%^&*()-_=+[]{}|;:,.<>?'

  const divider = 3
  let common = Math.floor(length / divider)
  let specialLen = length - common * 3
  if (length % divider === 0) {
    common -= 1
    specialLen += divider
  }

  const pick = (chars, n) => {
    let r = ''
    for (let i = 0; i < n; i++) r += chars[crypto.randomInt(chars.length)]
    return r
  }
  const shuffle = (str) => {
    const a = str.split('')
    for (let i = a.length - 1; i > 0; i--) {
      const j = crypto.randomInt(i + 1)
      ;[a[i], a[j]] = [a[j], a[i]]
    }
    return a.join('')
  }
  const valid = (p) => {
    for (let i = 0; i < p.length - 1; i++) if (p[i] === p[i + 1]) return false
    return true
  }

  while (true) {
    const chars = pick(lower, common) + pick(upper, common) + pick(digits, common) + pick(special, specialLen)
    const pw = shuffle(chars)
    if (valid(pw)) return pw
  }
}

// ── IPC Handlers ────────────────────────────────────────────────

ipcMain.handle('vault:create', async (_event, { password }) => {
  try {
    const { filePath } = await dialog.showSaveDialog(win, {
      title: 'Create New Vault',
      defaultPath: 'passwords.vault',
      filters: [{ name: 'Vault Files', extensions: ['vault'] }, { name: 'All Files', extensions: ['*'] }],
    })
    if (!filePath) return { success: false, error: 'Cancelled' }
    const { key } = createVault(password, filePath)
    state.derivedKey = key
    state.vaultPath = filePath
    state.entries = []
    state.unlocked = true
    state.settings = { autoLockMinutes: AUTO_LOCK_MINUTES, autoLockEnabled: true }
    resetAutoLockTimer()
    return { success: true, vaultName: path.basename(filePath) }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:unlock', async (_event, { password }) => {
  try {
    const { filePaths } = await dialog.showOpenDialog(win, {
      title: 'Open Vault',
      filters: [{ name: 'Vault Files', extensions: ['vault'] }, { name: 'All Files', extensions: ['*'] }],
      properties: ['openFile'],
    })
    if (!filePaths || filePaths.length === 0) return { success: false, error: 'Cancelled' }
    const { key, entries, settings } = loadVault(password, filePaths[0])
    state.derivedKey = key
    state.vaultPath = filePaths[0]
    state.entries = entries
    state.unlocked = true
    state.settings = settings
    resetAutoLockTimer()
    return { success: true, vaultName: path.basename(filePaths[0]), entries, settings }
  } catch (e) {
    const msg = e.message.includes('Unsupported state') ? 'Invalid master password' : e.message
    return { success: false, error: msg }
  }
})

ipcMain.handle('vault:lock', async () => {
  if (autoLockTimer) clearTimeout(autoLockTimer)
  state.derivedKey = null
  state.entries = []
  state.unlocked = false
  return { success: true }
})

ipcMain.handle('vault:getEntries', async () => {
  resetAutoLockTimer()
  return { success: true, entries: state.entries }
})

ipcMain.handle('vault:addEntry', async (_event, { service, username, password, url, notes, favorite }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
    resetAutoLockTimer()
    const entry = {
      id: crypto.randomUUID(),
      service,
      username,
      password,
      url: url || '',
      notes: notes || '',
      favorite: favorite || false,
      passwordHistory: [], // Store previous passwords
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    state.entries.push(entry)
    saveVault()
    return { success: true, entry }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:updateEntry', async (_event, { id, service, username, password, url, notes, favorite }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
    resetAutoLockTimer()
    const idx = state.entries.findIndex((e) => e.id === id)
    if (idx === -1) return { success: false, error: 'Entry not found' }

    const oldEntry = state.entries[idx]
    const passwordHistory = oldEntry.passwordHistory || []

    // If password changed, save old one to history (keep last 5)
    if (oldEntry.password !== password) {
      passwordHistory.unshift({
        password: oldEntry.password,
        changedAt: new Date().toISOString(),
      })
      if (passwordHistory.length > 5) passwordHistory.pop()
    }

    state.entries[idx] = {
      ...oldEntry,
      service,
      username,
      password,
      url: url || '',
      notes: notes || '',
      favorite: favorite !== undefined ? favorite : oldEntry.favorite,
      passwordHistory,
      updatedAt: new Date().toISOString(),
    }
    saveVault()
    return { success: true, entry: state.entries[idx] }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:toggleFavorite', async (_event, { id }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
    resetAutoLockTimer()
    const idx = state.entries.findIndex((e) => e.id === id)
    if (idx === -1) return { success: false, error: 'Entry not found' }
    state.entries[idx].favorite = !state.entries[idx].favorite
    state.entries[idx].updatedAt = new Date().toISOString()
    saveVault()
    return { success: true, entry: state.entries[idx] }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:deleteEntry', async (_event, { id }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
    resetAutoLockTimer()
    const len = state.entries.length
    state.entries = state.entries.filter((e) => e.id !== id)
    if (state.entries.length === len) return { success: false, error: 'Entry not found' }
    saveVault()
    return { success: true }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:generatePassword', async (_event, { length }) => {
  try {
    resetAutoLockTimer()
    return { success: true, password: generatePassword(length || 24) }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:isUnlocked', async () => {
  return {
    unlocked: state.unlocked,
    vaultName: state.vaultPath ? path.basename(state.vaultPath) : null,
    entryCount: state.entries.length,
  }
})

ipcMain.handle('vault:updateSettings', async (_event, { autoLockMinutes, autoLockEnabled }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
    state.settings = {
      ...state.settings,
      autoLockMinutes: autoLockMinutes ?? state.settings.autoLockMinutes,
      autoLockEnabled: autoLockEnabled ?? state.settings.autoLockEnabled,
    }
    saveVault()
    resetAutoLockTimer()
    return { success: true, settings: state.settings }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:getSettings', async () => {
  return { success: true, settings: state.settings }
})

// Activity tracking for auto-lock
ipcMain.handle('vault:activity', async () => {
  resetAutoLockTimer()
  return { success: true }
})

// ── Window ──────────────────────────────────────────────────────

app.whenReady().then(() => {
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize

  const winWidth = 380
  const winHeight = 580
  const margin = 24

  win = new BrowserWindow({
    width: winWidth,
    height: winHeight,
    minWidth: 340,
    minHeight: 480,
    maxWidth: 480,
    x: screenWidth - winWidth - margin,
    y: screenHeight - winHeight - margin,
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 12, y: 12 },
    vibrancy: 'under-window',
    visualEffectState: 'active',
    backgroundColor: '#00000000',
    transparent: process.platform === 'darwin',
    roundedCorners: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.cjs'),
    },
  })

  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    win.loadURL('http://localhost:5173')
  } else {
    win.loadFile(path.join(__dirname, 'dist', 'index.html'))
  }

  // Register keyboard shortcuts
  const template = [
    ...(process.platform === 'darwin' ? [{
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' },
      ],
    }] : []),
    {
      label: 'File',
      submenu: [
        {
          label: 'New Entry',
          accelerator: 'CmdOrCtrl+N',
          click: () => win.webContents.send('shortcut:new-entry'),
        },
        {
          label: 'Lock Vault',
          accelerator: 'CmdOrCtrl+L',
          click: () => win.webContents.send('shortcut:lock'),
        },
        { type: 'separator' },
        { role: 'close' },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' },
        { type: 'separator' },
        {
          label: 'Find',
          accelerator: 'CmdOrCtrl+F',
          click: () => win.webContents.send('shortcut:search'),
        },
      ],
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Generator',
          accelerator: 'CmdOrCtrl+G',
          click: () => win.webContents.send('shortcut:generator'),
        },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'toggleDevTools' },
      ],
    },
  ]
  Menu.setApplicationMenu(Menu.buildFromTemplate(template))
})

app.on('window-all-closed', () => {
  if (autoLockTimer) clearTimeout(autoLockTimer)
  if (process.platform !== 'darwin') app.quit()
})

app.on('will-quit', () => {
  if (autoLockTimer) clearTimeout(autoLockTimer)
})

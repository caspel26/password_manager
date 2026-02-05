const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron')
const { screen } = require('electron')
const path = require('path')
const crypto = require('crypto')
const fs = require('fs')

let win

// ── State ───────────────────────────────────────────────────────

let state = {
  derivedKey: null,            // 32-byte AES key derived from master password
  vaultPath: null,             // path to the .vault file
  entries: [],                 // decrypted entries in memory
  unlocked: false,
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
  // format: iv:tag:ciphertext (all base64)
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
// JSON file: { salt: base64, verify: encrypted("__vault_ok__"), entries: [encrypted(json), ...] }

function createVault(password, vaultPath) {
  const salt = crypto.randomBytes(SALT_LEN)
  const key = deriveKey(password, salt)
  const verify = encrypt('__vault_ok__', key)
  const vault = { salt: salt.toString('base64'), verify, entries: [] }
  fs.writeFileSync(vaultPath, JSON.stringify(vault, null, 2), 'utf-8')
  return { key, salt }
}

function loadVault(password, vaultPath) {
  const raw = fs.readFileSync(vaultPath, 'utf-8')
  const vault = JSON.parse(raw)
  const salt = Buffer.from(vault.salt, 'base64')
  const key = deriveKey(password, salt)
  // verify master password
  const check = decrypt(vault.verify, key)
  if (check !== '__vault_ok__') throw new Error('Invalid master password')
  // decrypt all entries
  const entries = vault.entries.map((enc) => JSON.parse(decrypt(enc, key)))
  return { key, salt, entries }
}

function saveVault() {
  if (!state.vaultPath || !state.derivedKey) {
    throw new Error('Cannot save: vault is not open')
  }
  const raw = fs.readFileSync(state.vaultPath, 'utf-8')
  const vault = JSON.parse(raw)
  // backup before writing
  fs.copyFileSync(state.vaultPath, state.vaultPath + '.bak')
  vault.entries = state.entries.map((e) => encrypt(JSON.stringify(e), state.derivedKey))
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
    const { key, entries } = loadVault(password, filePaths[0])
    state.derivedKey = key
    state.vaultPath = filePaths[0]
    state.entries = entries
    state.unlocked = true
    return { success: true, vaultName: path.basename(filePaths[0]), entries }
  } catch (e) {
    const msg = e.message.includes('Unsupported state') ? 'Invalid master password' : e.message
    return { success: false, error: msg }
  }
})

ipcMain.handle('vault:lock', async () => {
  state.derivedKey = null
  state.entries = []
  state.unlocked = false
  return { success: true }
})

ipcMain.handle('vault:getEntries', async () => {
  return { success: true, entries: state.entries }
})

ipcMain.handle('vault:addEntry', async (_event, { service, username, password, url, notes }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
    const entry = {
      id: crypto.randomUUID(),
      service,
      username,
      password,
      url: url || '',
      notes: notes || '',
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

ipcMain.handle('vault:updateEntry', async (_event, { id, service, username, password, url, notes }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
    const idx = state.entries.findIndex((e) => e.id === id)
    if (idx === -1) return { success: false, error: 'Entry not found' }
    state.entries[idx] = {
      ...state.entries[idx],
      service,
      username,
      password,
      url: url || '',
      notes: notes || '',
      updatedAt: new Date().toISOString(),
    }
    saveVault()
    return { success: true, entry: state.entries[idx] }
  } catch (e) {
    return { success: false, error: e.message }
  }
})

ipcMain.handle('vault:deleteEntry', async (_event, { id }) => {
  try {
    if (!state.unlocked) return { success: false, error: 'Vault is locked' }
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

// ── Window ──────────────────────────────────────────────────────

app.whenReady().then(() => {
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize

  // Compact window positioned in the bottom-right corner
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
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' },
      ],
    },
  ]
  Menu.setApplicationMenu(Menu.buildFromTemplate(template))
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

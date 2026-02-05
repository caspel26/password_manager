<p align="center">
  <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/main/icons/lock.svg" width="80" alt="Vault Logo">
</p>

<h1 align="center">Vault</h1>

<p align="center">
  <strong>A secure, offline password manager for macOS, Windows, and Linux</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Electron-34-47848F?logo=electron&logoColor=white" alt="Electron">
  <img src="https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white" alt="Vue 3">
  <img src="https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Encryption-AES--256--GCM-success" alt="AES-256-GCM">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/tests-45%20passing-brightgreen" alt="Tests">
</p>

---

## Overview

Vault is a desktop password manager that stores your credentials in encrypted `.vault` files on your local machine. Nothing is sent over the network — your data stays with you.

## Security

| Layer | Implementation |
|-------|----------------|
| **Encryption** | AES-256-GCM authenticated encryption |
| **Key Derivation** | PBKDF2-SHA512 with 600,000 iterations |
| **Salt** | 32-byte random salt per vault |
| **IV** | Random initialization vector per operation |
| **Integrity** | GCM authentication tag (tamper detection) |
| **Isolation** | Context isolation enabled — renderer has no Node.js access |

All cryptographic operations run in the Electron main process. The renderer communicates via IPC only.

## Features

- **Vault Management** — Create, open, and lock encrypted `.vault` files
- **Credential Storage** — Service, username, password, URL, and notes per entry
- **Search** — Filter entries by service, username, or URL
- **Password Generator** — Configurable length with mixed character types
- **Clipboard** — One-click copy for usernames and passwords
- **Auto-backup** — `.bak` file created before every write
- **Dark Theme** — Modern UI with sidebar navigation

## Tech Stack

| Component | Technology |
|-----------|------------|
| Desktop Shell | Electron |
| UI Framework | Vue 3 + TypeScript |
| Components | Vuetify 3 (Material Design) |
| State | Pinia |
| Build | Vite |
| Tests | Vitest |
| Crypto | Node.js `crypto` module |

## Project Structure

```
├── main.cjs              # Main process (crypto, IPC, file I/O)
├── preload.cjs           # Context bridge (IPC exposure)
├── src/
│   ├── App.vue           # App shell with sidebar
│   ├── router/           # Vue Router (hash mode)
│   ├── stores/           # Pinia vault store
│   ├── types/            # TypeScript definitions
│   └── views/
│       ├── LockScreen.vue    # Unlock / create vault
│       ├── VaultView.vue     # Entry list and details
│       └── GeneratorView.vue # Password generator
└── tests/
    ├── crypto.test.ts    # Encryption unit tests
    └── store.test.ts     # Store unit tests
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 18+
- npm or yarn

### Install Dependencies

```sh
npm install
```

### Development

```sh
npm run dev
```

Starts the Vite dev server and Electron concurrently with hot reload.

### Run Tests

```sh
npm test
```

### Build Executable

Build a distributable package for your platform:

```sh
npm run build
```

This runs `vite build` followed by `electron-builder`. Output goes to the `dist/` folder.

#### Platform-specific builds

```sh
# macOS (.dmg)
npm run build -- --mac

# Windows (.exe installer)
npm run build -- --win

# Linux (.AppImage, .deb)
npm run build -- --linux
```

> **Note:** Cross-compilation has limitations. For best results, build on the target OS.

#### Build output locations

| Platform | Output |
|----------|--------|
| macOS | `dist/Vault-x.x.x.dmg` |
| Windows | `dist/Vault Setup x.x.x.exe` |
| Linux | `dist/Vault-x.x.x.AppImage` |

## Vault File Format

Vault files (`.vault`) are JSON:

```json
{
  "salt": "<base64 32-byte salt>",
  "verify": "<iv:tag:ciphertext>",
  "entries": ["<iv:tag:ciphertext>", "..."]
}
```

- **salt** — Random salt for PBKDF2 key derivation
- **verify** — Encrypted `"__vault_ok__"` token to validate the master password
- **entries** — Array of encrypted JSON entries

Each encrypted value uses format `iv:authTag:ciphertext` (all base64).

## License

MIT

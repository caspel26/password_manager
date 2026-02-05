# Vault - Secure Password Manager

A desktop password manager built with Electron, Vue 3, and Vuetify. Credentials are encrypted locally using AES-256-GCM with a master password — nothing is sent over the network.

## Security

- **AES-256-GCM** authenticated encryption for all vault entries
- **PBKDF2-SHA512** key derivation with 600,000 iterations
- 32-byte random salt per vault
- Random IV per encryption operation
- GCM auth tag protects against tampering
- Master password verified via encrypted token before decryption
- Context isolation enabled — renderer has no direct Node.js access
- All crypto runs in the main process via IPC

## Features

- Create and open encrypted `.vault` files
- Lock/unlock with a master password
- Add, edit, search, and delete credential entries
- Each entry stores: service, username, password, URL, notes
- Password generator (configurable length, mixed character types)
- Copy passwords to clipboard
- Automatic `.bak` backup before writes
- Dark theme UI with sidebar navigation

## Tech Stack

- **Electron** — desktop shell
- **Vue 3** + **TypeScript** — renderer UI
- **Vuetify 3** — Material Design components
- **Pinia** — state management
- **Vite** — build tool
- **Vitest** — test framework
- **Node.js crypto** — AES-256-GCM, PBKDF2

## Project Structure

```
electron-app/
  main.cjs            # Electron main process (crypto, IPC, file I/O)
  preload.cjs          # Context bridge (exposes IPC to renderer)
  src/
    App.vue            # App shell with sidebar navigation
    router/index.ts    # Routes: lock screen, vault, generator
    stores/
      passwordManager.ts  # Pinia vault store
    types/
      electron.d.ts    # TypeScript types for IPC API
    views/
      LockScreen.vue   # Master password / create vault
      VaultView.vue    # Entry list, search, detail drawer, add/edit dialogs
      GeneratorView.vue # Password generator with strength meter
  tests/
    crypto.test.ts     # AES-256-GCM, PBKDF2, vault format, password gen
    store.test.ts      # Pinia store unit tests with mocked IPC
```

## Setup

```sh
npm install
```

## Development

```sh
npm run dev
```

This starts both the Vite dev server and Electron concurrently.

## Tests

```sh
npm test
```

## Build

```sh
npm run build
```

## Vault File Format

Vault files (`.vault`) are JSON with this structure:

```json
{
  "salt": "<base64 32-byte random salt>",
  "verify": "<AES-256-GCM encrypted '__vault_ok__'>",
  "entries": [
    "<AES-256-GCM encrypted JSON entry>",
    "..."
  ]
}
```

Each encrypted value uses the format `iv:authTag:ciphertext` (all base64-encoded). The `verify` field is decrypted on unlock to validate the master password before attempting to decrypt entries.

## License

See repository root for license information.

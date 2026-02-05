import { describe, it, expect } from 'vitest'
import crypto from 'crypto'

// ── AES-256-GCM helpers (mirrors main.cjs logic) ────────────────

const IV_LEN = 16
const SALT_LEN = 32
const PBKDF2_ITERATIONS = 600000

function deriveKey(password: string, salt: Buffer) {
  return crypto.pbkdf2Sync(password, salt, PBKDF2_ITERATIONS, 32, 'sha512')
}

function encrypt(plaintext: string, key: Buffer) {
  const iv = crypto.randomBytes(IV_LEN)
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv)
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf-8'), cipher.final()])
  const tag = cipher.getAuthTag()
  return [iv.toString('base64'), tag.toString('base64'), encrypted.toString('base64')].join(':')
}

function decrypt(packed: string, key: Buffer) {
  const [ivB64, tagB64, dataB64] = packed.split(':')
  const iv = Buffer.from(ivB64, 'base64')
  const tag = Buffer.from(tagB64, 'base64')
  const data = Buffer.from(dataB64, 'base64')
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv)
  decipher.setAuthTag(tag)
  return Buffer.concat([decipher.update(data), decipher.final()]).toString('utf-8')
}

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

  const pick = (chars: string, n: number) => {
    let r = ''
    for (let i = 0; i < n; i++) r += chars[crypto.randomInt(chars.length)]
    return r
  }
  const shuffle = (str: string) => {
    const a = str.split('')
    for (let i = a.length - 1; i > 0; i--) {
      const j = crypto.randomInt(i + 1)
      ;[a[i], a[j]] = [a[j], a[i]]
    }
    return a.join('')
  }
  const valid = (p: string) => {
    for (let i = 0; i < p.length - 1; i++) if (p[i] === p[i + 1]) return false
    return true
  }

  while (true) {
    const chars = pick(lower, common) + pick(upper, common) + pick(digits, common) + pick(special, specialLen)
    const pw = shuffle(chars)
    if (valid(pw)) return pw
  }
}

// ── Tests ───────────────────────────────────────────────────────

describe('PBKDF2 Key Derivation', () => {
  it('should derive a 32-byte key from password and salt', () => {
    const salt = crypto.randomBytes(SALT_LEN)
    const key = deriveKey('my-master-password', salt)
    expect(key.length).toBe(32)
  })

  it('should produce the same key for the same password + salt', () => {
    const salt = crypto.randomBytes(SALT_LEN)
    const key1 = deriveKey('same-password', salt)
    const key2 = deriveKey('same-password', salt)
    expect(key1.equals(key2)).toBe(true)
  })

  it('should produce different keys for different passwords', () => {
    const salt = crypto.randomBytes(SALT_LEN)
    const key1 = deriveKey('password-one', salt)
    const key2 = deriveKey('password-two', salt)
    expect(key1.equals(key2)).toBe(false)
  })

  it('should produce different keys for different salts', () => {
    const salt1 = crypto.randomBytes(SALT_LEN)
    const salt2 = crypto.randomBytes(SALT_LEN)
    const key1 = deriveKey('same-password', salt1)
    const key2 = deriveKey('same-password', salt2)
    expect(key1.equals(key2)).toBe(false)
  })
})

describe('AES-256-GCM Encrypt / Decrypt', () => {
  const salt = crypto.randomBytes(SALT_LEN)
  const key = deriveKey('test-master-password', salt)

  it('should encrypt and decrypt a string', () => {
    const plaintext = 'Hello, Vault!'
    const encrypted = encrypt(plaintext, key)
    const decrypted = decrypt(encrypted, key)
    expect(decrypted).toBe(plaintext)
  })

  it('should encrypt and decrypt a JSON payload', () => {
    const payload = { service: 'github', username: 'user1', password: 's3cret!' }
    const encrypted = encrypt(JSON.stringify(payload), key)
    const decrypted = JSON.parse(decrypt(encrypted, key))
    expect(decrypted).toEqual(payload)
  })

  it('should produce iv:tag:ciphertext format', () => {
    const encrypted = encrypt('test', key)
    const parts = encrypted.split(':')
    expect(parts.length).toBe(3)
    // each part should be valid base64
    for (const part of parts) {
      expect(() => Buffer.from(part, 'base64')).not.toThrow()
    }
  })

  it('should produce different ciphertext each time (random IV)', () => {
    const enc1 = encrypt('same data', key)
    const enc2 = encrypt('same data', key)
    expect(enc1).not.toBe(enc2)
  })

  it('should fail to decrypt with wrong key', () => {
    const wrongKey = deriveKey('wrong-password', salt)
    const encrypted = encrypt('secret data', key)
    expect(() => decrypt(encrypted, wrongKey)).toThrow()
  })

  it('should fail if ciphertext is tampered', () => {
    const encrypted = encrypt('important data', key)
    const parts = encrypted.split(':')
    // flip a byte in the ciphertext
    const data = Buffer.from(parts[2], 'base64')
    data[0] ^= 0xff
    parts[2] = data.toString('base64')
    expect(() => decrypt(parts.join(':'), key)).toThrow()
  })

  it('should fail if auth tag is tampered', () => {
    const encrypted = encrypt('important data', key)
    const parts = encrypted.split(':')
    const tag = Buffer.from(parts[1], 'base64')
    tag[0] ^= 0xff
    parts[1] = tag.toString('base64')
    expect(() => decrypt(parts.join(':'), key)).toThrow()
  })

  it('should handle special characters', () => {
    const text = 'p@$$w0rd!<>"&\' contraseña über 日本語'
    const encrypted = encrypt(text, key)
    expect(decrypt(encrypted, key)).toBe(text)
  })

  it('should handle empty string', () => {
    const encrypted = encrypt('', key)
    expect(decrypt(encrypted, key)).toBe('')
  })

  it('should handle large payloads', () => {
    const large = 'x'.repeat(10000)
    const encrypted = encrypt(large, key)
    expect(decrypt(encrypted, key)).toBe(large)
  })
})

describe('Vault File Format', () => {
  it('should verify master password via verification token', () => {
    const password = 'master-pass-123'
    const salt = crypto.randomBytes(SALT_LEN)
    const key = deriveKey(password, salt)
    const verify = encrypt('__vault_ok__', key)

    // correct password
    const checkKey = deriveKey(password, salt)
    expect(decrypt(verify, checkKey)).toBe('__vault_ok__')

    // wrong password
    const wrongKey = deriveKey('wrong', salt)
    expect(() => decrypt(verify, wrongKey)).toThrow()
  })

  it('should encrypt and decrypt multiple entries', () => {
    const salt = crypto.randomBytes(SALT_LEN)
    const key = deriveKey('vault-test', salt)

    const entries = [
      { id: '1', service: 'github', username: 'user1', password: 'pass1', url: '', notes: '' },
      { id: '2', service: 'gitlab', username: 'user2', password: 'pass2', url: 'https://gitlab.com', notes: 'work' },
      { id: '3', service: 'bitbucket', username: 'user3', password: 'pass3', url: '', notes: '' },
    ]

    const encryptedEntries = entries.map((e) => encrypt(JSON.stringify(e), key))
    const decryptedEntries = encryptedEntries.map((enc) => JSON.parse(decrypt(enc, key)))

    expect(decryptedEntries).toEqual(entries)
  })

  it('should produce valid JSON vault structure', () => {
    const password = 'json-test'
    const salt = crypto.randomBytes(SALT_LEN)
    const key = deriveKey(password, salt)
    const verify = encrypt('__vault_ok__', key)

    const vault = {
      salt: salt.toString('base64'),
      verify,
      entries: [
        encrypt(JSON.stringify({ service: 'test', username: 'u', password: 'p' }), key),
      ],
    }

    const json = JSON.stringify(vault, null, 2)
    const parsed = JSON.parse(json)

    expect(parsed.salt).toBeDefined()
    expect(parsed.verify).toBeDefined()
    expect(parsed.entries).toHaveLength(1)

    // round-trip: load back
    const loadedSalt = Buffer.from(parsed.salt, 'base64')
    const loadedKey = deriveKey(password, loadedSalt)
    expect(decrypt(parsed.verify, loadedKey)).toBe('__vault_ok__')
    const entry = JSON.parse(decrypt(parsed.entries[0], loadedKey))
    expect(entry.service).toBe('test')
  })
})

describe('Password Generation', () => {
  it('should generate a password of the requested length', () => {
    expect(generatePassword(24).length).toBe(24)
  })

  it('should generate different length passwords', () => {
    for (const len of [8, 12, 16, 20, 32, 64]) {
      expect(generatePassword(len).length).toBe(len)
    }
  })

  it('should not have consecutive identical characters', () => {
    for (let i = 0; i < 10; i++) {
      const pwd = generatePassword(24)
      for (let j = 0; j < pwd.length - 1; j++) {
        expect(pwd[j]).not.toBe(pwd[j + 1])
      }
    }
  })

  it('should contain lowercase, uppercase, digits, and special chars', () => {
    const pwd = generatePassword(24)
    expect(pwd).toMatch(/[a-z]/)
    expect(pwd).toMatch(/[A-Z]/)
    expect(pwd).toMatch(/[0-9]/)
    expect(pwd).toMatch(/[^a-zA-Z0-9]/)
  })

  it('should generate unique passwords each time', () => {
    const set = new Set<string>()
    for (let i = 0; i < 20; i++) set.add(generatePassword(24))
    expect(set.size).toBe(20)
  })
})

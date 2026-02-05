<template>
  <div class="vault-page">
    <!-- Header -->
    <div class="vault-header">
      <div class="header-left">
        <div class="vault-icon">
          <v-icon size="14" color="white">mdi-shield-lock</v-icon>
        </div>
        <div class="header-info">
          <span class="vault-name">{{ store.vaultName || 'Vault' }}</span>
          <span class="entry-count">{{ store.entryCount }} {{ store.entryCount === 1 ? 'item' : 'items' }}</span>
        </div>
      </div>
      <button class="add-btn" @click="showAdd = true">
        <v-icon size="16">mdi-plus</v-icon>
      </button>
    </div>

    <!-- Search -->
    <div class="search-wrapper">
      <v-icon class="search-icon" size="14">mdi-magnify</v-icon>
      <input
        v-model="store.searchQuery"
        type="text"
        placeholder="Search..."
        class="search-input"
      />
      <button v-if="store.searchQuery" class="clear-btn" @click="store.searchQuery = ''">
        <v-icon size="12">mdi-close</v-icon>
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="store.filteredEntries.length === 0" class="empty-state">
      <div class="empty-icon">
        <v-icon size="28">mdi-key-plus</v-icon>
      </div>
      <p class="empty-title" v-if="store.entryCount === 0">No credentials yet</p>
      <p class="empty-title" v-else>No matches</p>
      <p class="empty-subtitle" v-if="store.entryCount === 0">Add your first password</p>
      <button v-if="store.entryCount === 0" class="empty-btn" @click="showAdd = true">
        <v-icon size="14" class="mr-1">mdi-plus</v-icon>
        Add Entry
      </button>
    </div>

    <!-- Entry list -->
    <div v-else class="entry-list">
      <div
        v-for="entry in store.filteredEntries"
        :key="entry.id"
        class="entry-card"
        @click="selectEntry(entry)"
      >
        <div class="entry-avatar" :style="{ background: getAvatarColor(entry.service) }">
          {{ entry.service.charAt(0).toUpperCase() }}
        </div>
        <div class="entry-info">
          <div class="entry-service">{{ entry.service }}</div>
          <div class="entry-username">{{ entry.username }}</div>
        </div>
        <button class="copy-btn" @click.stop="copyPassword(entry.password)">
          <v-icon size="14">mdi-content-copy</v-icon>
        </button>
      </div>
    </div>

    <!-- Detail drawer (full screen) -->
    <v-navigation-drawer
      v-model="showDetail"
      location="right"
      temporary
      width="100%"
      class="detail-drawer"
    >
      <div v-if="selectedEntry" class="detail-page">
        <div class="detail-header">
          <button class="back-btn" @click="showDetail = false">
            <v-icon size="18">mdi-arrow-left</v-icon>
          </button>
          <span class="detail-title">{{ editing ? 'Edit' : 'Details' }}</span>
          <div style="width: 32px"></div>
        </div>

        <!-- View mode -->
        <div v-if="!editing" class="detail-body">
          <div class="detail-avatar" :style="{ background: getAvatarColor(selectedEntry.service) }">
            {{ selectedEntry.service.charAt(0).toUpperCase() }}
          </div>
          <div class="detail-service">{{ selectedEntry.service }}</div>

          <div class="field-card">
            <div class="field-row">
              <div class="field-info">
                <span class="field-label">Username</span>
                <span class="field-value">{{ selectedEntry.username }}</span>
              </div>
              <button class="field-action" @click="copyText(selectedEntry.username)">
                <v-icon size="14">mdi-content-copy</v-icon>
              </button>
            </div>

            <div class="field-divider"></div>

            <div class="field-row">
              <div class="field-info">
                <span class="field-label">Password</span>
                <code class="field-value mono">{{ showDetailPwd ? selectedEntry.password : '••••••••••••' }}</code>
              </div>
              <button class="field-action" @click="showDetailPwd = !showDetailPwd">
                <v-icon size="14">{{ showDetailPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
              </button>
              <button class="field-action" @click="copyText(selectedEntry.password)">
                <v-icon size="14">mdi-content-copy</v-icon>
              </button>
            </div>

            <template v-if="selectedEntry.url">
              <div class="field-divider"></div>
              <div class="field-row">
                <div class="field-info">
                  <span class="field-label">URL</span>
                  <span class="field-value truncate">{{ selectedEntry.url }}</span>
                </div>
                <button class="field-action" @click="copyText(selectedEntry.url)">
                  <v-icon size="14">mdi-content-copy</v-icon>
                </button>
              </div>
            </template>
          </div>

          <div v-if="selectedEntry.notes" class="notes-card">
            <span class="notes-label">Notes</span>
            <p class="notes-text">{{ selectedEntry.notes }}</p>
          </div>

          <div class="meta-info">
            <v-icon size="12">mdi-clock-outline</v-icon>
            Modified {{ formatDate(selectedEntry.updatedAt) }}
          </div>

          <div class="detail-actions">
            <button class="action-btn primary" @click="startEdit">
              <v-icon size="14" class="mr-1">mdi-pencil</v-icon>
              Edit
            </button>
            <button class="action-btn danger" :disabled="deleteLoading" @click="handleDelete">
              <v-icon size="14">mdi-delete</v-icon>
            </button>
          </div>
        </div>

        <!-- Edit mode -->
        <div v-else class="detail-body">
          <div class="edit-form">
            <div class="form-group">
              <label class="form-label">Service</label>
              <input v-model="editForm.service" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Username</label>
              <input v-model="editForm.username" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Password</label>
              <div class="input-with-actions">
                <input
                  v-model="editForm.password"
                  :type="showEditPwd ? 'text' : 'password'"
                  class="form-input"
                />
                <button class="input-action" @click="showEditPwd = !showEditPwd">
                  <v-icon size="14">{{ showEditPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                </button>
                <button class="input-action" @click="fillGenerated(editForm)">
                  <v-icon size="14">mdi-refresh</v-icon>
                </button>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">URL <span class="optional">optional</span></label>
              <input v-model="editForm.url" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Notes <span class="optional">optional</span></label>
              <textarea v-model="editForm.notes" class="form-textarea" rows="2"></textarea>
            </div>
          </div>
          <div class="detail-actions">
            <button class="action-btn secondary" @click="editing = false">Cancel</button>
            <button class="action-btn primary flex-1" :disabled="saving" @click="handleUpdate">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- Add dialog -->
    <v-dialog v-model="showAdd" max-width="360" persistent>
      <div class="add-dialog">
        <div class="dialog-header">
          <span class="dialog-title">New Entry</span>
          <button class="dialog-close" @click="closeAdd">
            <v-icon size="16">mdi-close</v-icon>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label class="form-label">Service</label>
            <input v-model="addForm.service" type="text" class="form-input" placeholder="GitHub, Netflix..." />
          </div>
          <div class="form-group">
            <label class="form-label">Username</label>
            <input v-model="addForm.username" type="text" class="form-input" placeholder="user@email.com" />
          </div>
          <div class="form-group">
            <label class="form-label">Password</label>
            <div class="input-with-actions">
              <input
                v-model="addForm.password"
                :type="showAddPwd ? 'text' : 'password'"
                class="form-input"
                placeholder="Enter or generate"
              />
              <button class="input-action" @click="showAddPwd = !showAddPwd">
                <v-icon size="14">{{ showAddPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
              </button>
              <button class="input-action generate" @click="fillGenerated(addForm)">
                <v-icon size="14">mdi-refresh</v-icon>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">URL <span class="optional">optional</span></label>
            <input v-model="addForm.url" type="text" class="form-input" placeholder="https://..." />
          </div>
          <div class="form-group">
            <label class="form-label">Notes <span class="optional">optional</span></label>
            <textarea v-model="addForm.notes" class="form-textarea" rows="2" placeholder="Extra info..."></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="action-btn secondary" @click="closeAdd">Cancel</button>
          <button class="action-btn primary" :disabled="saving || !addForm.service || !addForm.username || !addForm.password" @click="handleAdd">
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'
import type { VaultEntry } from '@/types/electron'

const store = useVaultStore()

const showDetail = ref(false)
const showAdd = ref(false)
const selectedEntry = ref<VaultEntry | null>(null)
const editing = ref(false)
const saving = ref(false)
const deleteLoading = ref(false)
const showDetailPwd = ref(false)
const showEditPwd = ref(false)
const showAddPwd = ref(false)

const emptyForm = () => ({ service: '', username: '', password: '', url: '', notes: '' })
const addForm = ref(emptyForm())
const editForm = ref({ id: '', ...emptyForm() })

const avatarColors = [
  'linear-gradient(135deg, #4434bc, #6c5ce7)',
  'linear-gradient(135deg, #e84393, #fd79a8)',
  'linear-gradient(135deg, #00b894, #55efc4)',
  'linear-gradient(135deg, #0984e3, #74b9ff)',
  'linear-gradient(135deg, #fdcb6e, #f39c12)',
  'linear-gradient(135deg, #e17055, #d63031)',
  'linear-gradient(135deg, #00cec9, #81ecec)',
  'linear-gradient(135deg, #a29bfe, #6c5ce7)',
]

function getAvatarColor(service: string) {
  const hash = service.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return avatarColors[hash % avatarColors.length]
}

function selectEntry(entry: VaultEntry) {
  selectedEntry.value = entry
  editing.value = false
  showDetailPwd.value = false
  showDetail.value = true
}

function startEdit() {
  if (!selectedEntry.value) return
  editForm.value = { ...selectedEntry.value }
  showEditPwd.value = false
  editing.value = true
}

async function handleUpdate() {
  saving.value = true
  try {
    const ok = await store.updateEntry(editForm.value)
    if (ok) {
      selectedEntry.value = store.entries.find((e) => e.id === editForm.value.id) || null
      editing.value = false
    }
  } catch {
    store.notify('Failed to update', 'error')
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!selectedEntry.value) return
  deleteLoading.value = true
  try {
    const ok = await store.deleteEntry(selectedEntry.value.id)
    if (ok) showDetail.value = false
  } catch {
    store.notify('Failed to delete', 'error')
  } finally {
    deleteLoading.value = false
  }
}

async function handleAdd() {
  saving.value = true
  try {
    const ok = await store.addEntry(addForm.value)
    if (ok) closeAdd()
  } catch {
    store.notify('Failed to save', 'error')
  } finally {
    saving.value = false
  }
}

function closeAdd() {
  showAdd.value = false
  addForm.value = emptyForm()
  showAddPwd.value = false
}

async function fillGenerated(form: { password: string }) {
  const pw = await store.generatePassword(24)
  if (pw) form.password = pw
}

function copyText(text: string) {
  navigator.clipboard.writeText(text)
  store.notify('Copied', 'info')
}

function copyPassword(pw: string) {
  navigator.clipboard.writeText(pw)
  store.notify('Password copied', 'info')
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.vault-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0a0a0f;
  padding-bottom: 60px;
}

.vault-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  -webkit-app-region: drag;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vault-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.vault-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.entry-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.add-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: rgba(68, 52, 188, 0.2);
  color: #7c6ff7;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  -webkit-app-region: no-drag;
}

.add-btn:hover {
  background: rgba(68, 52, 188, 0.35);
}

.search-wrapper {
  display: flex;
  align-items: center;
  margin: 0 12px 8px;
  padding: 0 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 8px;
}

.search-icon {
  color: rgba(255, 255, 255, 0.25);
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-size: 12px;
  padding: 8px 6px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.clear-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.25);
  cursor: pointer;
  padding: 2px;
  display: flex;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
}

.empty-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: rgba(68, 52, 188, 0.12);
  color: #6c5ce7;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.empty-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 4px;
}

.empty-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0 0 16px;
}

.empty-btn {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: linear-gradient(135deg, #4434bc, #5a4ad1);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.entry-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 8px;
}

.entry-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 2px;
}

.entry-card:hover {
  background: rgba(255, 255, 255, 0.04);
}

.entry-card:hover .copy-btn {
  opacity: 1;
}

.entry-avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  color: #fff;
  flex-shrink: 0;
}

.entry-info {
  flex: 1;
  min-width: 0;
}

.entry-service {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.entry-username {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.copy-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.15s;
  flex-shrink: 0;
}

.copy-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* Detail drawer */
.detail-drawer {
  background: #0a0a0f !important;
}

.detail-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.back-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
}

.detail-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 20px;
  color: #fff;
  margin: 0 auto 8px;
}

.detail-service {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  text-align: center;
  margin-bottom: 20px;
}

.field-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
}

.field-row {
  display: flex;
  align-items: center;
  padding: 12px;
  gap: 8px;
}

.field-info {
  flex: 1;
  min-width: 0;
}

.field-label {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.35);
  margin-bottom: 2px;
}

.field-value {
  font-size: 13px;
  color: #fff;
}

.field-value.mono {
  font-family: 'SF Mono', monospace;
  font-size: 12px;
}

.field-value.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.field-action {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  padding: 6px;
  display: flex;
  border-radius: 6px;
  transition: all 0.15s;
}

.field-action:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.field-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.04);
  margin: 0 12px;
}

.notes-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.notes-label {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.35);
  margin-bottom: 4px;
}

.notes-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.5;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 20px;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.15s;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4434bc, #5a4ad1);
  color: #fff;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.7);
}

.action-btn.danger {
  background: rgba(231, 76, 60, 0.12);
  color: #e74c3c;
  padding: 10px 12px;
}

.flex-1 { flex: 1; }

/* Edit form */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
}

.form-label .optional {
  font-weight: 400;
  color: rgba(255, 255, 255, 0.25);
}

.form-input {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 10px 12px;
  color: #fff;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}

.form-input:focus {
  border-color: rgba(68, 52, 188, 0.5);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.form-textarea {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 10px 12px;
  color: #fff;
  font-size: 13px;
  outline: none;
  resize: none;
  font-family: inherit;
}

.form-textarea:focus {
  border-color: rgba(68, 52, 188, 0.5);
}

.input-with-actions {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  transition: border-color 0.15s;
}

.input-with-actions:focus-within {
  border-color: rgba(68, 52, 188, 0.5);
}

.input-with-actions .form-input {
  flex: 1;
  background: transparent;
  border: none;
  border-radius: 0;
}

.input-action {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  padding: 8px;
  display: flex;
  transition: color 0.15s;
}

.input-action:hover {
  color: rgba(255, 255, 255, 0.7);
}

.input-action.generate:hover {
  color: #6c5ce7;
}

/* Add dialog */
.add-dialog {
  background: #12121a;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.dialog-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.dialog-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 4px;
  display: flex;
}

.dialog-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}
</style>

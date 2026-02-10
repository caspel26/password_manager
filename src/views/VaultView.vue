<template>
  <div class="vault-page">
    <!-- Header -->
    <div class="vault-header">
      <div class="header-left">
        <div class="vault-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C9.243 2 7 4.243 7 7V9H6C4.897 9 4 9.897 4 11V20C4 21.103 4.897 22 6 22H18C19.103 22 20 21.103 20 20V11C20 9.897 19.103 9 18 9H17V7C17 4.243 14.757 2 12 2ZM9 7C9 5.346 10.346 4 12 4C13.654 4 15 5.346 15 7V9H9V7Z" fill="white"/>
          </svg>
        </div>
        <div class="header-info">
          <span class="vault-name">{{ store.vaultName || 'My Vault' }}</span>
          <span class="entry-count">{{ store.entryCount }} {{ store.entryCount === 1 ? 'credential' : 'credentials' }}</span>
        </div>
      </div>
      <button class="add-btn" @click="showAdd = true">
        <v-icon size="16">mdi-plus</v-icon>
      </button>
    </div>

    <!-- Search -->
    <div class="search-wrapper" :class="{ focused: searchFocused }">
      <v-icon class="search-icon" size="14">mdi-magnify</v-icon>
      <input
        ref="searchInput"
        v-model="store.searchQuery"
        type="text"
        placeholder="Search credentials..."
        class="search-input"
        @focus="searchFocused = true"
        @blur="searchFocused = false"
      />
      <transition name="fade">
        <button v-if="store.searchQuery" class="clear-btn" @click="store.searchQuery = ''">
          <v-icon size="12">mdi-close</v-icon>
        </button>
      </transition>
    </div>

    <!-- Empty state -->
    <transition name="fade" mode="out-in">
      <div v-if="store.filteredEntries.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
            <path d="M19 13H13V19H11V13H5V11H11V5H13V11H19V13Z" fill="currentColor"/>
          </svg>
        </div>
        <p class="empty-title" v-if="store.entryCount === 0">No credentials yet</p>
        <p class="empty-title" v-else>No matches found</p>
        <p class="empty-subtitle" v-if="store.entryCount === 0">Add your first credential to get started</p>
        <button v-if="store.entryCount === 0" class="empty-btn" @click="showAdd = true">
          <v-icon size="14" class="mr-1">mdi-plus</v-icon>
          Add Credential
        </button>
      </div>

      <!-- Entry list -->
      <div v-else class="entry-list">
        <TransitionGroup name="list">
          <div
            v-for="entry in store.filteredEntries"
            :key="entry.id"
            class="entry-card"
            @click="selectEntry(entry)"
          >
            <div class="entry-avatar" :style="{ background: entry.icon ? 'transparent' : getAvatarColor(entry.service) }">
              <img v-if="entry.icon" :src="entry.icon" class="avatar-img" />
              <span v-else>{{ entry.service.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="entry-info">
              <div class="entry-service">
                <span>{{ entry.service }}</span>
                <transition name="star">
                  <v-icon v-if="entry.favorite" size="11" class="fav-badge">mdi-star</v-icon>
                </transition>
              </div>
              <div class="entry-username">{{ entry.username }}</div>
            </div>
            <div class="entry-actions">
              <button class="action-icon fav" :class="{ active: entry.favorite }" @click.stop="toggleFav(entry.id)">
                <v-icon size="14">{{ entry.favorite ? 'mdi-star' : 'mdi-star-outline' }}</v-icon>
              </button>
              <button class="action-icon copy" @click.stop="copyPassword(entry.password)">
                <v-icon size="14">mdi-content-copy</v-icon>
              </button>
              <button class="action-icon delete" @click.stop="deleteFromList(entry.id)">
                <v-icon size="14">mdi-delete-outline</v-icon>
              </button>
            </div>
          </div>
        </TransitionGroup>
      </div>
    </transition>

    <!-- Detail overlay -->
    <transition name="detail">
      <div v-if="showDetail && selectedEntry" class="detail-overlay" @click.self="showDetail = false">
        <div class="detail-card">
          <div class="detail-header">
            <span class="detail-title">{{ editing ? 'Edit Credential' : 'Details' }}</span>
            <div class="header-actions">
              <button class="fav-header-btn" :class="{ active: selectedEntry.favorite }" @click="toggleFav(selectedEntry.id)">
                <v-icon size="16">{{ selectedEntry.favorite ? 'mdi-star' : 'mdi-star-outline' }}</v-icon>
              </button>
              <button class="close-header-btn" @click="showDetail = false">
                <v-icon size="16">mdi-close</v-icon>
              </button>
            </div>
          </div>

        <!-- View mode -->
        <transition name="fade" mode="out-in">
          <div v-if="!editing" key="view" class="detail-content">
            <div class="detail-body">
              <div class="detail-hero">
                <div class="detail-avatar-wrap" @click="handlePickImageForEntry">
                  <div class="detail-avatar" :style="{ background: selectedEntry.icon ? 'transparent' : getAvatarColor(selectedEntry.service) }">
                    <img v-if="selectedEntry.icon" :src="selectedEntry.icon" class="avatar-img" />
                    <span v-else>{{ selectedEntry.service.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="avatar-edit-overlay">
                    <v-icon size="16" color="white">mdi-camera</v-icon>
                  </div>
                </div>
                <h2 class="detail-service">{{ selectedEntry.service }}</h2>
                <div class="detail-icon-actions">
                  <button v-if="selectedEntry.url" class="icon-btn" :disabled="fetchingIcon" @click="handleFetchFaviconForEntry">
                    <v-icon size="12">mdi-web</v-icon>
                    {{ fetchingIcon ? 'Fetching...' : 'Fetch icon' }}
                  </button>
                  <button v-if="selectedEntry.icon" class="icon-btn remove" @click="handleRemoveIconForEntry">
                    <v-icon size="12">mdi-close</v-icon>
                    Remove
                  </button>
                </div>
              </div>

              <div class="fields-section">
                <div class="field-card">
                  <div class="field-row">
                    <div class="field-icon">
                      <v-icon size="14">mdi-account</v-icon>
                    </div>
                    <div class="field-content">
                      <span class="field-label">Username</span>
                      <span class="field-value">{{ selectedEntry.username }}</span>
                    </div>
                    <button class="field-btn" @click="copyText(selectedEntry.username)">
                      <v-icon size="14">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </div>

                <div class="field-card">
                  <div class="field-row">
                    <div class="field-icon">
                      <v-icon size="14">mdi-key</v-icon>
                    </div>
                    <div class="field-content">
                      <span class="field-label">Password</span>
                      <code class="field-value mono">{{ showDetailPwd ? selectedEntry.password : '••••••••••••' }}</code>
                    </div>
                    <button class="field-btn" @click="showDetailPwd = !showDetailPwd">
                      <v-icon size="14">{{ showDetailPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                    </button>
                    <button class="field-btn" @click="copyText(selectedEntry.password)">
                      <v-icon size="14">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </div>

                <div v-if="selectedEntry.url" class="field-card">
                  <div class="field-row">
                    <div class="field-icon">
                      <v-icon size="14">mdi-link</v-icon>
                    </div>
                    <div class="field-content">
                      <span class="field-label">Website</span>
                      <span class="field-value url">{{ selectedEntry.url }}</span>
                    </div>
                    <button class="field-btn" @click="copyText(selectedEntry.url)">
                      <v-icon size="14">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </div>

                <div v-if="selectedEntry.notes" class="field-card notes">
                  <div class="field-row">
                    <div class="field-icon">
                      <v-icon size="14">mdi-text</v-icon>
                    </div>
                    <div class="field-content">
                      <span class="field-label">Notes</span>
                      <p class="field-value notes-text">{{ selectedEntry.notes }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Password History -->
              <div v-if="selectedEntry.passwordHistory?.length" class="history-section">
                <button class="history-toggle" @click="showHistory = !showHistory">
                  <v-icon size="14">mdi-history</v-icon>
                  <span>Password History ({{ selectedEntry.passwordHistory.length }})</span>
                  <v-icon size="14" class="chevron" :class="{ open: showHistory }">mdi-chevron-down</v-icon>
                </button>
                <transition name="expand">
                  <div v-if="showHistory" class="history-list">
                    <div v-for="(h, i) in selectedEntry.passwordHistory" :key="i" class="history-item">
                      <code class="history-pwd">{{ showHistoryPwd[i] ? h.password : '••••••••' }}</code>
                      <span class="history-date">{{ formatDate(h.changedAt) }}</span>
                      <button class="field-btn sm" @click="showHistoryPwd[i] = !showHistoryPwd[i]">
                        <v-icon size="12">{{ showHistoryPwd[i] ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      </button>
                      <button class="field-btn sm" @click="copyText(h.password)">
                        <v-icon size="12">mdi-content-copy</v-icon>
                      </button>
                    </div>
                  </div>
                </transition>
              </div>

              <div class="meta-row">
                <v-icon size="12">mdi-clock-outline</v-icon>
                <span>Last modified {{ formatDate(selectedEntry.updatedAt) }}</span>
              </div>
            </div>

            <div class="detail-footer">
              <button class="btn primary flex-1" @click="startEdit">
                <v-icon size="14">mdi-pencil</v-icon>
                Edit
              </button>
              <button class="btn danger" :disabled="deleteLoading" @click="handleDelete">
                <v-icon size="14">mdi-delete</v-icon>
                Delete
              </button>
            </div>
          </div>

          <!-- Edit mode -->
          <div v-else key="edit" class="detail-content">
            <div class="detail-body">
              <div class="edit-form">
                <div class="form-field">
                  <label>Service Name</label>
                  <input v-model="editForm.service" type="text" placeholder="e.g., GitHub" />
                </div>
                <div class="form-field">
                  <label>Username / Email</label>
                  <input v-model="editForm.username" type="text" placeholder="user@example.com" />
                </div>
                <div class="form-field">
                  <label>Password</label>
                  <div class="input-group">
                    <input v-model="editForm.password" :type="showEditPwd ? 'text' : 'password'" />
                    <button class="input-btn" @click="showEditPwd = !showEditPwd">
                      <v-icon size="14">{{ showEditPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                    </button>
                    <button class="input-btn accent" @click="fillGenerated(editForm)">
                      <v-icon size="14">mdi-auto-fix</v-icon>
                    </button>
                  </div>
                </div>
                <div class="form-field">
                  <label>Website URL <span class="optional">(optional)</span></label>
                  <input v-model="editForm.url" type="text" placeholder="https://..." />
                </div>
                <div class="form-field">
                  <label>Icon <span class="optional">(optional)</span></label>
                  <div class="icon-picker">
                    <div class="icon-preview" :style="{ background: editForm.icon ? 'transparent' : getAvatarColor(editForm.service || 'A') }">
                      <img v-if="editForm.icon" :src="editForm.icon" class="avatar-img" />
                      <span v-else>{{ (editForm.service || 'A').charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="icon-actions">
                      <button type="button" class="icon-btn" :disabled="!editForm.url || fetchingIcon" @click.stop="handleFetchFavicon(editForm)">
                        <v-icon size="12">mdi-web</v-icon>
                        {{ fetchingIcon ? 'Fetching...' : 'From URL' }}
                      </button>
                      <button type="button" class="icon-btn" @click.stop="handlePickImage(editForm)">
                        <v-icon size="12">mdi-image</v-icon>
                        Upload
                      </button>
                      <button v-if="editForm.icon" type="button" class="icon-btn remove" @click.stop="editForm.icon = ''">
                        <v-icon size="12">mdi-close</v-icon>
                      </button>
                    </div>
                  </div>
                </div>
                <div class="form-field">
                  <label>Notes <span class="optional">(optional)</span></label>
                  <textarea v-model="editForm.notes" rows="3" placeholder="Additional information..."></textarea>
                </div>
              </div>
            </div>
            <div class="detail-footer">
              <button class="btn secondary" @click="editing = false">Cancel</button>
              <button class="btn primary flex-1" :disabled="saving" @click="handleUpdate">
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </div>
        </transition>
        </div>
      </div>
    </transition>

    <!-- Add dialog -->
    <v-dialog v-model="showAdd" max-width="360" persistent :scrim="true">
      <div class="add-dialog" @click.stop>
        <div class="dialog-header">
          <div class="dialog-icon">
            <v-icon size="16" color="white">mdi-plus</v-icon>
          </div>
          <span class="dialog-title">New Credential</span>
          <button class="dialog-close" @click="closeAdd">
            <v-icon size="16">mdi-close</v-icon>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-field">
            <label>Service Name</label>
            <input v-model="addForm.service" type="text" placeholder="GitHub, Netflix, etc." autofocus />
          </div>
          <div class="form-field">
            <label>Username / Email</label>
            <input v-model="addForm.username" type="text" placeholder="user@example.com" />
          </div>
          <div class="form-field">
            <label>Password</label>
            <div class="input-group">
              <input v-model="addForm.password" :type="showAddPwd ? 'text' : 'password'" placeholder="Enter or generate" />
              <button type="button" class="input-btn" @click.stop="showAddPwd = !showAddPwd">
                <v-icon size="14">{{ showAddPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
              </button>
              <button type="button" class="input-btn accent" @click.stop="fillGenerated(addForm)">
                <v-icon size="14">mdi-auto-fix</v-icon>
              </button>
            </div>
          </div>
          <div class="form-field">
            <label>Website URL <span class="optional">(optional)</span></label>
            <input v-model="addForm.url" type="text" placeholder="https://..." />
          </div>
          <div class="form-field">
            <label>Icon <span class="optional">(optional)</span></label>
            <div class="icon-picker">
              <div class="icon-preview" :style="{ background: addForm.icon ? 'transparent' : getAvatarColor(addForm.service || 'A') }">
                <img v-if="addForm.icon" :src="addForm.icon" class="avatar-img" />
                <span v-else>{{ (addForm.service || 'A').charAt(0).toUpperCase() }}</span>
              </div>
              <div class="icon-actions">
                <button type="button" class="icon-btn" :disabled="!addForm.url || fetchingIcon" @click.stop="handleFetchFavicon(addForm)">
                  <v-icon size="12">mdi-web</v-icon>
                  {{ fetchingIcon ? 'Fetching...' : 'From URL' }}
                </button>
                <button type="button" class="icon-btn" @click.stop="handlePickImage(addForm)">
                  <v-icon size="12">mdi-image</v-icon>
                  Upload
                </button>
                <button v-if="addForm.icon" type="button" class="icon-btn remove" @click.stop="addForm.icon = ''">
                  <v-icon size="12">mdi-close</v-icon>
                </button>
              </div>
            </div>
          </div>
          <div class="form-field">
            <label>Notes <span class="optional">(optional)</span></label>
            <textarea v-model="addForm.notes" rows="2" placeholder="Additional information..."></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button type="button" class="btn secondary" @click="closeAdd">Cancel</button>
          <button type="button" class="btn primary" :disabled="saving || !addForm.service || !addForm.username || !addForm.password" @click="handleAdd">
            {{ saving ? 'Saving...' : 'Save Credential' }}
          </button>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'
import type { VaultEntry } from '@/types/electron'

const store = useVaultStore()

const searchInput = ref<HTMLInputElement | null>(null)
const searchFocused = ref(false)
const showDetail = ref(false)
const showAdd = ref(false)
const selectedEntry = ref<VaultEntry | null>(null)
const editing = ref(false)
const saving = ref(false)
const deleteLoading = ref(false)
const showDetailPwd = ref(false)
const showEditPwd = ref(false)
const showAddPwd = ref(false)
const showHistory = ref(false)
const showHistoryPwd = ref<boolean[]>([])
const fetchingIcon = ref(false)

const emptyForm = () => ({ service: '', username: '', password: '', url: '', notes: '', icon: '', favorite: false })
const addForm = ref(emptyForm())
const editForm = ref({ id: '', ...emptyForm() })

const avatarColors = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
  'linear-gradient(135deg, #5ee7df 0%, #b490ca 100%)',
  'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
]

function getAvatarColor(service: string) {
  const hash = service.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return avatarColors[hash % avatarColors.length]
}

function selectEntry(entry: VaultEntry) {
  selectedEntry.value = entry
  editing.value = false
  showDetailPwd.value = false
  showHistory.value = false
  showHistoryPwd.value = (entry.passwordHistory || []).map(() => false)
  showDetail.value = true
}

function startEdit() {
  if (!selectedEntry.value) return
  editForm.value = { ...selectedEntry.value, icon: selectedEntry.value.icon || '' }
  showEditPwd.value = false
  editing.value = true
}

async function handleUpdate() {
  saving.value = true
  try {
    const { id, service, username, password, url, notes, icon, favorite } = editForm.value
    const ok = await store.updateEntry({ id, service, username, password, url, notes, icon, favorite })
    if (ok) {
      selectedEntry.value = store.entries.find((e) => e.id === id) || null
      editing.value = false
    }
  } catch (e: unknown) {
    store.notify(e instanceof Error ? e.message : 'Failed to save', 'error')
  } finally {
    saving.value = false
  }
}

async function deleteFromList(id: string) {
  await store.deleteEntry(id)
}

async function handleDelete() {
  if (!selectedEntry.value) return
  const entryId = selectedEntry.value.id
  // Close drawer first so user doesn't see stale state
  showDetail.value = false
  selectedEntry.value = null
  deleteLoading.value = true
  try {
    await store.deleteEntry(entryId)
  } finally {
    deleteLoading.value = false
  }
}

async function handleAdd() {
  saving.value = true
  try {
    const { service, username, password, url, notes, icon } = addForm.value
    const ok = await store.addEntry({ service, username, password, url, notes, icon })
    if (ok) closeAdd()
  } catch (e: unknown) {
    store.notify(e instanceof Error ? e.message : 'Failed to save', 'error')
  } finally {
    saving.value = false
  }
}

function closeAdd() {
  showAdd.value = false
  addForm.value = emptyForm()
  showAddPwd.value = false
}

async function handleFetchFavicon(form: { url: string; icon: string }) {
  if (!form.url) return
  fetchingIcon.value = true
  try {
    const icon = await store.fetchFavicon(form.url)
    if (icon) form.icon = icon
    else store.notify('Could not fetch icon', 'warning')
  } finally {
    fetchingIcon.value = false
  }
}

async function handlePickImage(form: { icon: string }) {
  const icon = await store.pickImage()
  if (icon) form.icon = icon
}

async function updateEntryIcon(icon: string) {
  if (!selectedEntry.value) return
  const entry = selectedEntry.value
  await store.updateEntry({ id: entry.id, service: entry.service, username: entry.username, password: entry.password, url: entry.url, notes: entry.notes, icon, favorite: entry.favorite })
  selectedEntry.value = store.entries.find((e) => e.id === entry.id) || null
}

async function handlePickImageForEntry() {
  const icon = await store.pickImage()
  if (icon) await updateEntryIcon(icon)
}

async function handleFetchFaviconForEntry() {
  if (!selectedEntry.value?.url) return
  fetchingIcon.value = true
  try {
    const icon = await store.fetchFavicon(selectedEntry.value.url)
    if (icon) await updateEntryIcon(icon)
    else store.notify('Could not fetch icon', 'warning')
  } finally {
    fetchingIcon.value = false
  }
}

async function handleRemoveIconForEntry() {
  await updateEntryIcon('')
}

async function fillGenerated(form: { password: string }) {
  const pw = await store.generatePassword(24)
  if (pw) form.password = pw
}

async function toggleFav(id: string) {
  await store.toggleFavorite(id)
  if (selectedEntry.value?.id === id) {
    selectedEntry.value = store.entries.find((e) => e.id === id) || null
  }
}

function copyText(text: string) {
  navigator.clipboard.writeText(text)
  store.notify('Copied to clipboard', 'info')
}

function copyPassword(pw: string) {
  navigator.clipboard.writeText(pw)
  store.notify('Password copied', 'info')
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function openNewEntry() {
  showAdd.value = true
}

function focusSearch() {
  searchInput.value?.focus()
}

onMounted(() => {
  window.electronAPI.onShortcutNewEntry(() => openNewEntry())
  window.electronAPI.onShortcutSearch(() => focusSearch())
})

onUnmounted(() => {
  window.electronAPI.removeAllListeners('shortcut:new-entry')
  window.electronAPI.removeAllListeners('shortcut:search')
})

defineExpose({ openNewEntry, focusSearch })
</script>

<style scoped>
/* ── Keyframes ──────────────────────────────────────────────── */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

/* ── Scrollbar ──────────────────────────────────────────────── */
.entry-list::-webkit-scrollbar,
.detail-body::-webkit-scrollbar,
.dialog-body::-webkit-scrollbar {
  width: 4px;
}
.entry-list::-webkit-scrollbar-track,
.detail-body::-webkit-scrollbar-track,
.dialog-body::-webkit-scrollbar-track {
  background: transparent;
}
.entry-list::-webkit-scrollbar-thumb,
.detail-body::-webkit-scrollbar-thumb,
.dialog-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
}
.entry-list::-webkit-scrollbar-thumb:hover,
.detail-body::-webkit-scrollbar-thumb:hover,
.dialog-body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* ── Page ───────────────────────────────────────────────────── */
.vault-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #0d0d14 0%, #0a0a0f 100%);
  padding-bottom: 60px;
}

/* ── Header ─────────────────────────────────────────────────── */
.vault-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  -webkit-app-region: drag;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vault-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.header-info {
  display: flex;
  flex-direction: column;
}

.vault-name {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  letter-spacing: -0.2px;
}

.entry-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 1px;
}

.add-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 10px;
  background: rgba(102, 126, 234, 0.15);
  color: #667eea;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  -webkit-app-region: no-drag;
}

.add-btn:hover {
  background: rgba(102, 126, 234, 0.25);
  transform: scale(1.05);
}

.add-btn:active {
  transform: scale(0.95);
}

/* ── Search ─────────────────────────────────────────────────── */
.search-wrapper {
  display: flex;
  align-items: center;
  margin: 0 12px 12px;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  transition: all 0.25s ease;
}

.search-wrapper.focused {
  border-color: rgba(102, 126, 234, 0.4);
  background: rgba(102, 126, 234, 0.05);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.08), 0 4px 16px rgba(102, 126, 234, 0.1);
}

.search-icon {
  color: rgba(255, 255, 255, 0.3);
  transition: color 0.2s;
}

.search-wrapper.focused .search-icon {
  color: #667eea;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-size: 13px;
  padding: 10px 8px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.clear-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 4px;
  display: flex;
  transition: all 0.15s;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* ── Empty state ────────────────────────────────────────────── */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 4px;
}

.empty-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  margin: 0 0 20px;
}

.empty-btn {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
  transition: all 0.2s ease;
}

.empty-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.45);
}

.empty-btn:active {
  transform: translateY(0);
}

/* ── Entry list ─────────────────────────────────────────────── */
.entry-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px 8px;
}

.entry-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 2px;
  border: 1px solid rgba(255, 255, 255, 0.03);
  background: rgba(255, 255, 255, 0.01);
  position: relative;
}

.entry-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  border-radius: 0 3px 3px 0;
  background: linear-gradient(180deg, #667eea, #764ba2);
  transition: height 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.entry-card:hover {
  background: rgba(255, 255, 255, 0.035);
  border-color: rgba(255, 255, 255, 0.06);
  transform: translateX(2px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.entry-card:hover::before {
  height: 60%;
}

.entry-card:active {
  transform: translateX(2px) scale(0.99);
}

.entry-card:hover .entry-actions {
  opacity: 1;
}

.entry-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 15px;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.entry-card:hover .entry-avatar {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: inherit;
}

.entry-info {
  flex: 1;
  min-width: 0;
}

.entry-service {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.entry-service span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fav-badge {
  color: #fbbf24;
  flex-shrink: 0;
}

.entry-username {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.entry-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.action-icon {
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.action-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transform: scale(1.1);
}

.action-icon:active {
  transform: scale(0.9);
}

.action-icon.fav:hover, .action-icon.fav.active {
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
}

.action-icon.copy:hover {
  background: rgba(102, 126, 234, 0.15);
  color: #667eea;
}

.action-icon.delete:hover {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

/* ── Detail floating card ───────────────────────────────────── */
.detail-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 14px;
}

.detail-card {
  width: 100%;
  max-height: calc(100vh - 40px);
  background: linear-gradient(180deg, #171730 0%, #0f0f1c 100%);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 24px 64px rgba(0, 0, 0, 0.55),
    0 0 0 1px rgba(255, 255, 255, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.07),
    0 0 80px rgba(102, 126, 234, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.015);
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.fav-header-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.fav-header-btn:hover, .fav-header-btn.active {
  color: #fbbf24;
}

.fav-header-btn:active {
  transform: scale(0.9);
}

.header-actions {
  display: flex;
  gap: 4px;
}

.close-header-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.close-header-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.close-header-btn:active {
  transform: scale(0.9);
}

.detail-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.detail-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 24px 16px;
}

.detail-footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(8px);
  flex-shrink: 0;
}

.detail-hero {
  text-align: center;
  margin-bottom: 24px;
}

.detail-avatar-wrap {
  position: relative;
  width: 64px;
  height: 64px;
  margin: 0 auto 12px;
  cursor: pointer;
}

.detail-avatar-wrap::after {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: 17px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  transition: all 0.25s ease;
  pointer-events: none;
}

.detail-avatar-wrap:hover::after {
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.15);
}

.detail-avatar-wrap:hover .avatar-edit-overlay {
  opacity: 1;
}

.avatar-edit-overlay {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.15s;
  z-index: 1;
}

.detail-icon-actions {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 6px;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 24px;
  color: #fff;
  margin: 0;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.detail-service {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: -0.3px;
}

.fields-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.field-card {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.15s ease;
}

.field-card:hover {
  background: rgba(255, 255, 255, 0.035);
  border-color: rgba(255, 255, 255, 0.07);
}

.field-row {
  display: flex;
  align-items: center;
  padding: 12px;
  gap: 12px;
}

.field-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.field-card:hover .field-icon {
  background: rgba(102, 126, 234, 0.15);
  box-shadow: 0 0 12px rgba(102, 126, 234, 0.1);
}

.field-content {
  flex: 1;
  min-width: 0;
}

.field-label {
  display: block;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.35);
  margin-bottom: 2px;
}

.field-value {
  font-size: 13px;
  color: #fff;
  word-break: break-all;
}

.field-value.mono {
  font-family: 'SF Mono', monospace;
  font-size: 12px;
  letter-spacing: 0.5px;
}

.field-value.url {
  color: #8b9cf7;
}

.field-value.notes-text {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.7);
}

.field-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.field-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.field-btn:active {
  transform: scale(0.85);
}

.field-btn.sm {
  width: 24px;
  height: 24px;
}

/* ── History ────────────────────────────────────────────────── */
.history-section {
  margin-bottom: 16px;
}

.history-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.history-toggle:hover {
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.7);
}

.history-toggle .chevron {
  margin-left: auto;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.history-toggle .chevron.open {
  transform: rotate(180deg);
}

.history-list {
  margin-top: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.history-item:last-child {
  border-bottom: none;
}

.history-pwd {
  flex: 1;
  font-family: 'SF Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.history-date {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.25);
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 20px;
}

/* ── Buttons ────────────────────────────────────────────────── */
.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4), 0 0 0 1px rgba(102, 126, 234, 0.2);
}

.btn.primary:active:not(:disabled) {
  transform: translateY(0) scale(0.97);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.1);
}

.btn.secondary:active:not(:disabled) {
  transform: scale(0.97);
}

.btn.danger {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  padding: 12px 14px;
  border: 1px solid rgba(239, 68, 68, 0.1);
}

.btn.danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.18);
  border-color: rgba(239, 68, 68, 0.2);
  box-shadow: 0 0 16px rgba(239, 68, 68, 0.1);
}

.btn.danger:active:not(:disabled) {
  transform: scale(0.97);
}

.flex-1 { flex: 1; }

/* ── Edit form ──────────────────────────────────────────────── */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
}

.form-field label .optional {
  font-weight: 400;
  color: rgba(255, 255, 255, 0.25);
}

.form-field input,
.form-field textarea {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 12px 14px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.25s ease;
  font-family: inherit;
}

.form-field input:focus,
.form-field textarea:focus {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.05);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.08);
}

.form-field input::placeholder,
.form-field textarea::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.form-field textarea {
  resize: none;
}

.input-group {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  transition: all 0.25s ease;
}

.input-group:focus-within {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.05);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.08);
}

.input-group input {
  flex: 1;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 12px 14px;
}

.input-group input:focus {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
}

.input-btn {
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  border-radius: 8px;
}

.input-btn:hover {
  color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.05);
}

.input-btn:active {
  transform: scale(0.85);
}

.input-btn.accent:hover {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

/* ── Icon picker ────────────────────────────────────────────── */
.icon-picker {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-preview {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 15px;
  color: #fff;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.icon-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.icon-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}

.icon-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.15);
}

.icon-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.icon-btn.remove {
  border-color: rgba(239, 68, 68, 0.2);
  color: rgba(239, 68, 68, 0.6);
}

.icon-btn.remove:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* ── Add dialog ─────────────────────────────────────────────── */
.add-dialog {
  background: linear-gradient(180deg, #14142a 0%, #0d0d18 100%);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 24px 64px rgba(0, 0, 0, 0.55),
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 0 60px rgba(102, 126, 234, 0.04);
  display: flex;
  flex-direction: column;
  max-height: 85vh;
  position: relative;
}

.add-dialog::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
  background-size: 200% 100%;
  animation: shimmer 3s ease-in-out infinite;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.dialog-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.dialog-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.dialog-close {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.dialog-close:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.dialog-close:active {
  transform: scale(0.85);
}

.dialog-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(8px);
  flex-shrink: 0;
}

/* ── Transitions ────────────────────────────────────────────── */
.detail-enter-active {
  transition: opacity 0.25s ease;
}
.detail-enter-active .detail-card {
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.detail-leave-active {
  transition: opacity 0.2s ease;
}
.detail-leave-active .detail-card {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.detail-enter-from {
  opacity: 0;
}
.detail-enter-from .detail-card {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}
.detail-leave-to {
  opacity: 0;
}
.detail-leave-to .detail-card {
  opacity: 0;
  transform: scale(0.95) translateY(8px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.star-enter-active,
.star-leave-active {
  transition: all 0.2s ease;
}

.star-enter-from,
.star-leave-to {
  opacity: 0;
  transform: scale(0);
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-16px);
}

.list-leave-active {
  position: absolute;
  width: calc(100% - 20px);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>

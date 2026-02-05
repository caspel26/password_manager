<template>
  <div class="vault-page">
    <!-- Header bar -->
    <div class="vault-header">
      <div class="d-flex align-center ga-3">
        <h2 class="text-h6 font-weight-bold">All Items</h2>
        <v-chip size="small" variant="tonal" color="primary">{{ store.entryCount }}</v-chip>
      </div>
      <div class="d-flex align-center ga-2">
        <v-text-field
          v-model="store.searchQuery"
          placeholder="Search vault..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          hide-details
          single-line
          style="max-width: 260px"
          bg-color="surface"
          rounded="lg"
          clearable
        />
        <v-btn color="primary" rounded="lg" @click="showAdd = true">
          <v-icon start>mdi-plus</v-icon>
          Add
        </v-btn>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="store.filteredEntries.length === 0" class="empty-state">
      <v-icon size="64" color="primary" class="mb-4" style="opacity: 0.4">mdi-shield-lock-open</v-icon>
      <p class="text-body-1 text-medium-emphasis" v-if="store.entryCount === 0">
        Your vault is empty. Add your first credential.
      </p>
      <p class="text-body-1 text-medium-emphasis" v-else>
        No results for "{{ store.searchQuery }}"
      </p>
      <v-btn v-if="store.entryCount === 0" color="primary" rounded="lg" class="mt-4" @click="showAdd = true">
        <v-icon start>mdi-plus</v-icon>
        Add Entry
      </v-btn>
    </div>

    <!-- Entry list -->
    <div v-else class="entry-list">
      <div
        v-for="entry in store.filteredEntries"
        :key="entry.id"
        class="entry-card"
        @click="selectEntry(entry)"
      >
        <div class="entry-avatar">
          {{ entry.service.charAt(0).toUpperCase() }}
        </div>
        <div class="entry-info">
          <div class="text-body-1 font-weight-medium">{{ entry.service }}</div>
          <div class="text-body-2 text-medium-emphasis">{{ entry.username }}</div>
        </div>
        <div class="entry-actions">
          <v-btn
            icon
            size="small"
            variant="text"
            color="default"
            @click.stop="copyPassword(entry.password)"
          >
            <v-icon size="18">mdi-content-copy</v-icon>
            <v-tooltip activator="parent" location="top">Copy password</v-tooltip>
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Detail / Edit Sheet -->
    <v-navigation-drawer
      v-model="showDetail"
      location="right"
      temporary
      width="420"
      class="detail-drawer"
    >
      <div v-if="selectedEntry" class="pa-6">
        <div class="d-flex align-center justify-space-between mb-6">
          <h3 class="text-h6 font-weight-bold">{{ editing ? 'Edit Entry' : 'Details' }}</h3>
          <v-btn icon variant="text" size="small" @click="showDetail = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <!-- View mode -->
        <div v-if="!editing">
          <div class="detail-avatar mx-auto mb-5">
            {{ selectedEntry.service.charAt(0).toUpperCase() }}
          </div>

          <div class="detail-field">
            <label class="detail-label">Service</label>
            <div class="detail-value">{{ selectedEntry.service }}</div>
          </div>
          <div class="detail-field">
            <label class="detail-label">Username</label>
            <div class="detail-value d-flex align-center">
              {{ selectedEntry.username }}
              <v-btn icon size="x-small" variant="text" class="ml-1" @click="copyText(selectedEntry.username)">
                <v-icon size="14">mdi-content-copy</v-icon>
              </v-btn>
            </div>
          </div>
          <div class="detail-field">
            <label class="detail-label">Password</label>
            <div class="detail-value d-flex align-center">
              <code>{{ showDetailPwd ? selectedEntry.password : '••••••••••••' }}</code>
              <v-btn icon size="x-small" variant="text" class="ml-1" @click="showDetailPwd = !showDetailPwd">
                <v-icon size="14">{{ showDetailPwd ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
              </v-btn>
              <v-btn icon size="x-small" variant="text" @click="copyText(selectedEntry.password)">
                <v-icon size="14">mdi-content-copy</v-icon>
              </v-btn>
            </div>
          </div>
          <div v-if="selectedEntry.url" class="detail-field">
            <label class="detail-label">URL</label>
            <div class="detail-value">{{ selectedEntry.url }}</div>
          </div>
          <div v-if="selectedEntry.notes" class="detail-field">
            <label class="detail-label">Notes</label>
            <div class="detail-value text-body-2" style="white-space: pre-wrap">{{ selectedEntry.notes }}</div>
          </div>
          <div class="detail-field">
            <label class="detail-label">Last modified</label>
            <div class="detail-value text-caption">{{ formatDate(selectedEntry.updatedAt) }}</div>
          </div>

          <div class="d-flex ga-2 mt-6">
            <v-btn color="primary" variant="flat" rounded="lg" class="flex-grow-1" @click="startEdit">
              <v-icon start>mdi-pencil</v-icon> Edit
            </v-btn>
            <v-btn color="error" variant="tonal" rounded="lg" :loading="deleteLoading" @click="handleDelete">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </div>
        </div>

        <!-- Edit mode -->
        <div v-else>
          <v-text-field v-model="editForm.service" label="Service" variant="outlined" density="comfortable" class="mb-2" />
          <v-text-field v-model="editForm.username" label="Username" variant="outlined" density="comfortable" class="mb-2" />
          <v-text-field
            v-model="editForm.password"
            label="Password"
            :type="showEditPwd ? 'text' : 'password'"
            :append-inner-icon="showEditPwd ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showEditPwd = !showEditPwd"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          >
            <template #append>
              <v-btn icon size="small" variant="text" @click="fillGenerated(editForm)">
                <v-icon size="18">mdi-refresh</v-icon>
                <v-tooltip activator="parent" location="top">Generate</v-tooltip>
              </v-btn>
            </template>
          </v-text-field>
          <v-text-field v-model="editForm.url" label="URL (optional)" variant="outlined" density="comfortable" class="mb-2" />
          <v-textarea v-model="editForm.notes" label="Notes (optional)" variant="outlined" density="comfortable" rows="3" class="mb-2" />
          <div class="d-flex ga-2">
            <v-btn color="primary" variant="flat" rounded="lg" class="flex-grow-1" :loading="saving" @click="handleUpdate">
              Save
            </v-btn>
            <v-btn variant="outlined" rounded="lg" @click="editing = false">Cancel</v-btn>
          </div>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- Add Entry Dialog -->
    <v-dialog v-model="showAdd" max-width="480" persistent>
      <v-card rounded="xl" class="pa-2">
        <v-card-title class="text-h6 font-weight-bold pt-4 px-6">New Entry</v-card-title>
        <v-card-text class="px-6">
          <v-text-field v-model="addForm.service" label="Service" variant="outlined" density="comfortable" class="mb-2" />
          <v-text-field v-model="addForm.username" label="Username" variant="outlined" density="comfortable" class="mb-2" />
          <v-text-field
            v-model="addForm.password"
            label="Password"
            :type="showAddPwd ? 'text' : 'password'"
            :append-inner-icon="showAddPwd ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showAddPwd = !showAddPwd"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          >
            <template #append>
              <v-btn icon size="small" variant="text" @click="fillGenerated(addForm)">
                <v-icon size="18">mdi-refresh</v-icon>
                <v-tooltip activator="parent" location="top">Generate</v-tooltip>
              </v-btn>
            </template>
          </v-text-field>
          <v-text-field v-model="addForm.url" label="URL (optional)" variant="outlined" density="comfortable" class="mb-2" />
          <v-textarea v-model="addForm.notes" label="Notes (optional)" variant="outlined" density="comfortable" rows="3" />
        </v-card-text>
        <v-card-actions class="px-6 pb-4">
          <v-spacer />
          <v-btn variant="text" rounded="lg" @click="closeAdd">Cancel</v-btn>
          <v-btn color="primary" variant="flat" rounded="lg" :loading="saving" @click="handleAdd">Save</v-btn>
        </v-card-actions>
      </v-card>
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
  } catch (e) {
    store.notify('Failed to update entry', 'error')
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
  } catch (e) {
    store.notify('Failed to delete entry', 'error')
  } finally {
    deleteLoading.value = false
  }
}

async function handleAdd() {
  saving.value = true
  try {
    const ok = await store.addEntry(addForm.value)
    if (ok) closeAdd()
  } catch (e) {
    store.notify('Failed to save entry', 'error')
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
  store.notify('Copied to clipboard', 'info')
}

function copyPassword(pw: string) {
  navigator.clipboard.writeText(pw)
  store.notify('Password copied', 'info')
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}
</script>

<style scoped>
.vault-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.vault-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.entry-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 16px;
}

.entry-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 2px;
}
.entry-card:hover {
  background: rgba(255, 255, 255, 0.04);
}

.entry-avatar {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  color: #fff;
  flex-shrink: 0;
}

.entry-info {
  flex: 1;
  min-width: 0;
}
.entry-info > div {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entry-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}
.entry-card:hover .entry-actions {
  opacity: 1;
}

.detail-drawer {
  border-left: 1px solid rgba(255, 255, 255, 0.06) !important;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 28px;
  color: #fff;
  text-align: center;
}

.detail-field {
  margin-bottom: 16px;
}
.detail-label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  opacity: 0.5;
  margin-bottom: 4px;
}
.detail-value {
  font-size: 14px;
}
.detail-value code {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 13px;
}
</style>

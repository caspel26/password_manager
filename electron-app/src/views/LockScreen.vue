<template>
  <div class="lock-screen">
    <div class="lock-container">
      <!-- Logo area -->
      <div class="lock-logo">
        <div class="logo-icon">
          <v-icon size="48" color="white">mdi-shield-lock</v-icon>
        </div>
        <h1 class="text-h4 font-weight-bold mt-5 mb-1">Vault</h1>
        <p class="text-body-2 text-medium-emphasis">Secure Password Manager</p>
      </div>

      <!-- Tab selector -->
      <v-btn-toggle v-model="mode" mandatory density="compact" class="mb-6 w-100" rounded="lg" color="primary">
        <v-btn value="unlock" class="flex-grow-1 text-none">Open Vault</v-btn>
        <v-btn value="create" class="flex-grow-1 text-none">New Vault</v-btn>
      </v-btn-toggle>

      <!-- Unlock form -->
      <div v-if="mode === 'unlock'">
        <v-text-field
          v-model="password"
          label="Master Password"
          :type="showPwd ? 'text' : 'password'"
          :append-inner-icon="showPwd ? 'mdi-eye-off' : 'mdi-eye'"
          @click:append-inner="showPwd = !showPwd"
          variant="outlined"
          density="comfortable"
          hide-details
          class="mb-4"
          bg-color="surface"
          @keyup.enter="handleUnlock"
        />
        <v-btn
          block
          size="large"
          color="primary"
          rounded="lg"
          :loading="loading"
          @click="handleUnlock"
        >
          <v-icon start>mdi-lock-open-variant</v-icon>
          Unlock
        </v-btn>
      </div>

      <!-- Create form -->
      <div v-else>
        <v-text-field
          v-model="password"
          label="Master Password"
          :type="showPwd ? 'text' : 'password'"
          :append-inner-icon="showPwd ? 'mdi-eye-off' : 'mdi-eye'"
          @click:append-inner="showPwd = !showPwd"
          variant="outlined"
          density="comfortable"
          hide-details
          class="mb-3"
          bg-color="surface"
        />
        <v-text-field
          v-model="confirm"
          label="Confirm Password"
          :type="showConfirm ? 'text' : 'password'"
          :append-inner-icon="showConfirm ? 'mdi-eye-off' : 'mdi-eye'"
          @click:append-inner="showConfirm = !showConfirm"
          variant="outlined"
          density="comfortable"
          hide-details
          class="mb-4"
          bg-color="surface"
          @keyup.enter="handleCreate"
        />
        <v-btn
          block
          size="large"
          color="primary"
          rounded="lg"
          :loading="loading"
          @click="handleCreate"
        >
          <v-icon start>mdi-plus-circle</v-icon>
          Create Vault
        </v-btn>
      </div>

      <p class="text-caption text-medium-emphasis text-center mt-6">
        AES-256-GCM &middot; PBKDF2-SHA512 &middot; 600k iterations
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'
import { useRouter } from 'vue-router'

const store = useVaultStore()
const router = useRouter()

const mode = ref<'unlock' | 'create'>('unlock')
const password = ref('')
const confirm = ref('')
const showPwd = ref(false)
const showConfirm = ref(false)
const loading = ref(false)

async function handleUnlock() {
  loading.value = true
  const ok = await store.unlock(password.value)
  loading.value = false
  if (ok) {
    password.value = ''
    router.push('/vault')
  }
}

async function handleCreate() {
  loading.value = true
  const ok = await store.createVault(password.value, confirm.value)
  loading.value = false
  if (ok) {
    password.value = ''
    confirm.value = ''
    router.push('/vault')
  }
}
</script>

<style scoped>
.lock-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.lock-container {
  width: 380px;
  padding: 40px 32px;
  background: rgba(30, 30, 46, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5);
}

.lock-logo {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: linear-gradient(135deg, #4434bc, #6c5ce7);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 8px 32px rgba(68, 52, 188, 0.4);
}
</style>

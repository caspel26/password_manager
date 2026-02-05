<template>
  <div class="generator-page pa-7">
    <h2 class="text-h6 font-weight-bold mb-6">Password Generator</h2>

    <!-- Generated password display -->
    <v-card rounded="xl" class="password-display mb-6" variant="flat" color="surface">
      <v-card-text class="d-flex align-center pa-5">
        <code class="generated-text flex-grow-1">
          {{ store.generatedPassword || 'Click generate to create a password' }}
        </code>
        <v-btn
          icon
          size="small"
          variant="text"
          :disabled="!store.generatedPassword"
          @click="copyPassword"
        >
          <v-icon size="20">mdi-content-copy</v-icon>
          <v-tooltip activator="parent" location="top">Copy</v-tooltip>
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- Length control -->
    <div class="mb-6">
      <div class="d-flex align-center justify-space-between mb-2">
        <span class="text-body-2 text-medium-emphasis">Length</span>
        <v-chip size="small" variant="tonal" color="primary">{{ length }}</v-chip>
      </div>
      <v-slider
        v-model="length"
        :min="8"
        :max="64"
        :step="1"
        color="primary"
        track-color="surface"
        hide-details
      />
    </div>

    <!-- Character types (info only, the generator always includes all) -->
    <div class="mb-6">
      <span class="text-body-2 text-medium-emphasis d-block mb-3">Includes</span>
      <div class="d-flex ga-2 flex-wrap">
        <v-chip size="small" variant="tonal" color="success" prepend-icon="mdi-check">Lowercase</v-chip>
        <v-chip size="small" variant="tonal" color="success" prepend-icon="mdi-check">Uppercase</v-chip>
        <v-chip size="small" variant="tonal" color="success" prepend-icon="mdi-check">Numbers</v-chip>
        <v-chip size="small" variant="tonal" color="success" prepend-icon="mdi-check">Symbols</v-chip>
      </div>
    </div>

    <!-- Strength indicator -->
    <div v-if="store.generatedPassword" class="mb-6">
      <span class="text-body-2 text-medium-emphasis d-block mb-2">Strength</span>
      <v-progress-linear
        :model-value="strengthPercent"
        :color="strengthColor"
        height="6"
        rounded
      />
      <span class="text-caption" :class="`text-${strengthColor}`">{{ strengthLabel }}</span>
    </div>

    <v-btn
      block
      size="large"
      color="primary"
      rounded="lg"
      :loading="loading"
      @click="generate"
    >
      <v-icon start>mdi-refresh</v-icon>
      Generate Password
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useVaultStore } from '@/stores/passwordManager'

const store = useVaultStore()
const length = ref(24)
const loading = ref(false)

const strengthPercent = computed(() => {
  const l = store.generatedPassword?.length || 0
  if (l >= 24) return 100
  if (l >= 16) return 75
  if (l >= 12) return 50
  return 25
})

const strengthColor = computed(() => {
  const p = strengthPercent.value
  if (p >= 75) return 'success'
  if (p >= 50) return 'warning'
  return 'error'
})

const strengthLabel = computed(() => {
  const p = strengthPercent.value
  if (p >= 75) return 'Strong'
  if (p >= 50) return 'Moderate'
  return 'Weak'
})

async function generate() {
  loading.value = true
  await store.generatePassword(length.value)
  loading.value = false
}

function copyPassword() {
  if (store.generatedPassword) {
    navigator.clipboard.writeText(store.generatedPassword)
    store.notify('Password copied', 'info')
  }
}
</script>

<style scoped>
.generator-page {
  max-width: 520px;
  margin: 0 auto;
}

.password-display {
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.generated-text {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 15px;
  word-break: break-all;
  line-height: 1.6;
}
</style>

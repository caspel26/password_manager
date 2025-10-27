<template>
  <main>
      <Header />
      <v-container class="mt-12">
        <v-stepper v-model="step" :items="['Step 1', 'Step 2', 'Step 3', 'Step 4', 'Step 5']" hide-actions class="elevation-0 bg-transparent">
          <template v-slot:item.1>
            <v-row align="center" justify="center" class="text-center">
              <v-col cols="12" class="mt-8">
                <v-btn block rounded="lg" color="primary" class="elevation-7" prepend-icon="mdi-key" @click="step = 2; stepSelected = 'keys'">
                  Keys management
                </v-btn>
              </v-col>
              <v-col cols="12" class="mt-8">
                <v-btn block rounded="lg" color="primary" class="elevation-7" prepend-icon="mdi-lock">Passwords management</v-btn>
              </v-col>
              <v-col cols="12" class="mt-8">
                <v-btn block rounded="lg" color="primary" class="elevation-7" prepend-icon="mdi-information">About</v-btn>
              </v-col>
            </v-row>
          </template>
          <template v-slot:item.2>

          </template>
      </v-stepper>
      </v-container>
  </main>
</template>

<script setup lang="ts">
import Header from '../components/HeaderView.vue'
import { ref } from 'vue';
const step = ref(1);
const stepSelected = ref('');
</script>

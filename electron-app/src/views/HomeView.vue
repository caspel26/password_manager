<template>
  <main>
      <Header />
      <v-container class="mt-12">
        <v-row align="center" justify="center" class="text-center">
          <v-col cols="12" class="mt-8">
        <v-btn block rounded="lg" color="primary" class="elevation-7" prepend-icon="mdi-key">
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
      </v-container>
  </main>
</template>

<script setup lang="ts">
import Header from '../components/HeaderView.vue'
</script>

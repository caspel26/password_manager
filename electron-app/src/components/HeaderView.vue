<template>
    <v-toolbar app flat density="compact" color="primary">
      <v-row>
        <v-col cols="3">
          <v-img src="/favicon.ico" width="40" height="50" class="ml-2"></v-img>
        </v-col>
      </v-row>
      <v-switch class="mt-5 mr-2" v-model="isDarkTheme" @change="toggleTheme" inset>
        <template v-slot:thumb>
          <img width="40" height="50" :src="themeIcon" alt="Theme Icon" class="theme-icon"/>
        </template>
      </v-switch>
    </v-toolbar>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import vuetify from '@/plugins/vuetify';
import moonIcon from '@/assets/moon.png';
import sunIcon from '@/assets/sun.png';

const isDarkTheme = ref(true);
const themeIcon = ref(moonIcon);

function toggleTheme() {
  themeIcon.value = isDarkTheme.value ? moonIcon : sunIcon;
  vuetify.theme.global.name.value = isDarkTheme.value ? 'dark' : 'light';
}
</script>

<style>
.theme-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}
</style>

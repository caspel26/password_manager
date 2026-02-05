<template>
  <div class="splash-screen" :class="{ 'fade-out': fadeOut }">
    <!-- Animated background -->
    <div class="splash-bg">
      <div class="bg-gradient"></div>
      <div class="bg-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
      </div>
      <div class="bg-grid"></div>
    </div>

    <!-- Content -->
    <div class="splash-content">
      <!-- Logo -->
      <div class="logo-container">
        <div class="logo-ring">
          <svg class="ring-svg" viewBox="0 0 100 100">
            <circle class="ring-bg" cx="50" cy="50" r="46" />
            <circle class="ring-progress" cx="50" cy="50" r="46" />
          </svg>
        </div>
        <div class="logo-icon">
          <div class="icon-inner">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path class="lock-body" d="M6 11V20C6 21.103 6.897 22 8 22H16C17.103 22 18 21.103 18 20V11C18 9.897 17.103 9 16 9H8C6.897 9 6 9.897 6 11Z" fill="url(#lockGradient)"/>
              <path class="lock-shackle" d="M8 9V7C8 4.791 9.791 3 12 3C14.209 3 16 4.791 16 7V9" stroke="url(#shackleGradient)" stroke-width="2" stroke-linecap="round"/>
              <circle class="lock-keyhole" cx="12" cy="15" r="1.5" fill="#0a0a0f"/>
              <rect class="lock-keyhole-line" x="11.25" y="15" width="1.5" height="3" rx="0.75" fill="#0a0a0f"/>
              <defs>
                <linearGradient id="lockGradient" x1="6" y1="9" x2="18" y2="22" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#fff"/>
                  <stop offset="100%" stop-color="#e0e0e0"/>
                </linearGradient>
                <linearGradient id="shackleGradient" x1="8" y1="3" x2="16" y2="9" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stop-color="#fff"/>
                  <stop offset="100%" stop-color="#c0c0c0"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
      </div>

      <!-- Text -->
      <div class="splash-text">
        <h1 class="app-name">
          <span class="letter" style="--i: 0">V</span>
          <span class="letter" style="--i: 1">a</span>
          <span class="letter" style="--i: 2">u</span>
          <span class="letter" style="--i: 3">l</span>
          <span class="letter" style="--i: 4">t</span>
        </h1>
        <p class="tagline">Your secrets, secured locally</p>
      </div>

      <!-- Loading indicator -->
      <div class="loading-section">
        <div class="loading-bar">
          <div class="loading-progress"></div>
        </div>
        <p class="loading-text">Initializing secure environment...</p>
      </div>
    </div>

    <!-- Version badge -->
    <div class="version-badge">v1.0.1</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits<{
  complete: []
}>()

const fadeOut = ref(false)

onMounted(() => {
  // Show splash for 2 seconds, then fade out
  setTimeout(() => {
    fadeOut.value = true
    // Wait for fade animation to complete
    setTimeout(() => {
      emit('complete')
    }, 500)
  }, 2000)
})
</script>

<style scoped>
.splash-screen {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0f;
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.splash-screen.fade-out {
  opacity: 0;
  transform: scale(1.05);
}

/* Background */
.splash-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(118, 75, 162, 0.1) 0%, transparent 40%),
    radial-gradient(ellipse at 20% 80%, rgba(102, 126, 234, 0.08) 0%, transparent 40%),
    linear-gradient(180deg, #0d0d14 0%, #0a0a0f 100%);
}

.bg-orbs {
  position: absolute;
  inset: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  animation: float 8s ease-in-out infinite;
}

.orb-1 {
  width: 300px;
  height: 300px;
  background: rgba(102, 126, 234, 0.15);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 200px;
  height: 200px;
  background: rgba(118, 75, 162, 0.12);
  bottom: -50px;
  right: -50px;
  animation-delay: -3s;
}

.orb-3 {
  width: 150px;
  height: 150px;
  background: rgba(102, 126, 234, 0.1);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -5s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(20px, -20px) scale(1.05); }
  66% { transform: translate(-15px, 15px) scale(0.95); }
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
}

/* Content */
.splash-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

/* Logo */
.logo-container {
  position: relative;
  width: 100px;
  height: 100px;
  animation: logo-enter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  opacity: 0;
}

@keyframes logo-enter {
  0% {
    opacity: 0;
    transform: scale(0.5) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.logo-ring {
  position: absolute;
  inset: 0;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.05);
  stroke-width: 2;
}

.ring-progress {
  fill: none;
  stroke: url(#ringGradient);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-dasharray: 289;
  stroke-dashoffset: 289;
  animation: ring-fill 2s ease-out forwards;
  filter: drop-shadow(0 0 6px rgba(102, 126, 234, 0.5));
}

/* Add gradient definition via CSS custom property workaround */
.ring-progress {
  stroke: #667eea;
}

@keyframes ring-fill {
  0% { stroke-dashoffset: 289; }
  100% { stroke-dashoffset: 0; }
}

.logo-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-inner {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 8px 32px rgba(102, 126, 234, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  animation: icon-pulse 2s ease-in-out infinite;
}

@keyframes icon-pulse {
  0%, 100% {
    box-shadow:
      0 8px 32px rgba(102, 126, 234, 0.4),
      0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  }
  50% {
    box-shadow:
      0 8px 48px rgba(102, 126, 234, 0.6),
      0 0 0 1px rgba(255, 255, 255, 0.15) inset;
  }
}

.lock-shackle {
  animation: shackle-unlock 0.6s ease-out 0.3s forwards;
  transform-origin: center;
}

@keyframes shackle-unlock {
  0% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
  100% { transform: translateY(0); }
}

/* Text */
.splash-text {
  text-align: center;
  animation: text-enter 0.6s ease-out 0.3s forwards;
  opacity: 0;
}

@keyframes text-enter {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.app-name {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  letter-spacing: -1px;
  display: flex;
  justify-content: center;
}

.letter {
  display: inline-block;
  animation: letter-bounce 0.5s ease-out forwards;
  animation-delay: calc(0.4s + var(--i) * 0.05s);
  opacity: 0;
  transform: translateY(20px);
}

@keyframes letter-bounce {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  60% {
    transform: translateY(-5px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.tagline {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  margin: 8px 0 0;
  font-weight: 400;
  animation: tagline-fade 0.5s ease-out 0.8s forwards;
  opacity: 0;
}

@keyframes tagline-fade {
  to { opacity: 1; }
}

/* Loading */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  animation: loading-enter 0.5s ease-out 1s forwards;
  opacity: 0;
}

@keyframes loading-enter {
  to { opacity: 1; }
}

.loading-bar {
  width: 120px;
  height: 3px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.loading-progress {
  height: 100%;
  width: 0;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
  animation: loading 1.8s ease-in-out forwards;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

@keyframes loading {
  0% { width: 0; }
  20% { width: 20%; }
  50% { width: 60%; }
  80% { width: 85%; }
  100% { width: 100%; }
}

.loading-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin: 0;
  letter-spacing: 0.5px;
}

/* Version */
.version-badge {
  position: absolute;
  bottom: 24px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.2);
  font-weight: 500;
  letter-spacing: 0.5px;
  animation: version-fade 0.5s ease-out 1.2s forwards;
  opacity: 0;
}

@keyframes version-fade {
  to { opacity: 1; }
}
</style>

<template>
  <div class="loading-spinner" :style="{ width: `${size}px`, height: `${size}px` }">
    <div class="spinner-ring"></div>
    <div class="spinner-ring delay-1"></div>
    <div class="spinner-ring delay-2"></div>
    <div class="spinner-core"></div>
  </div>
</template>

<script setup>
const props = defineProps({
  size: { type: Number, default: 40 }
})
</script>

<style scoped>
.loading-spinner {
  position: relative;
  display: inline-block;
}

.spinner-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid transparent;
  border-top-color: #00ff41;
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring.delay-1 {
  border-top-color: rgba(0, 255, 65, 0.6);
  animation-delay: -0.4s;
}

.spinner-ring.delay-2 {
  border-top-color: rgba(0, 255, 65, 0.3);
  animation-delay: -0.8s;
}

.spinner-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 30%;
  height: 30%;
  background: #00ff41;
  border-radius: 50%;
  animation: pulse 1.2s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(0.8);
  }
}
</style>

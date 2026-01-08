<template>
  <button 
    class="btn"
    :class="[variantClass, sizeClass, { 'is-loading': loading }]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <!-- Loading spinner -->
    <LoadingSpinner v-if="loading" :size="spinnerSize" />
    
    <!-- Icon (if provided) -->
    <span v-if="$slots.icon && !loading" class="btn-icon">
      <slot name="icon" />
    </span>
    
    <!-- Content -->
    <span v-if="!loading" class="btn-content">
      <slot />
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'outline', 'ghost', 'danger', 'cyber'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const variantClass = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-terminal-green text-black font-bold hover:shadow-glow-md hover:brightness-110 transition-all'
    case 'secondary':
      return 'bg-terminal-gray border border-terminal-green text-terminal-green hover:bg-terminal-green hover:text-black'
    case 'outline':
      return 'bg-transparent border border-terminal-green/50 text-terminal-green hover:bg-terminal-green/10 hover:border-terminal-green'
    case 'ghost':
      return 'bg-transparent text-terminal-green hover:bg-terminal-green/10'
    case 'danger':
      return 'bg-cyber-red text-white hover:bg-cyber-red/80'
    case 'cyber':
      return 'glass-strong border border-terminal-green/30 text-terminal-green hover:border-terminal-green/60 hover:glow-sm'
    default:
      return 'bg-terminal-green text-black'
  }
})

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-3 py-1.5 text-sm rounded-lg gap-1.5'
    case 'md':
      return 'px-4 py-2 text-base rounded-xl gap-2'
    case 'lg':
      return 'px-6 py-3 text-lg rounded-xl gap-2.5'
    default:
      return 'px-4 py-2 text-base rounded-xl gap-2'
  }
})

const spinnerSize = computed(() => {
  switch (props.size) {
    case 'sm':
      return 14
    case 'md':
      return 16
    case 'lg':
      return 20
    default:
      return 16
  }
})

const handleClick = (event) => {
  if (!props.loading && !props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped>
.btn {
  @apply inline-flex items-center justify-center;
  @apply font-medium;
  @apply transition-all duration-300;
  @apply cursor-pointer;
  @apply focus:outline-none focus:ring-2 focus:ring-terminal-green/50 focus:ring-offset-2 focus:ring-offset-black;
}

.btn:disabled:not(.is-loading) {
  @apply opacity-50 cursor-not-allowed;
}

.btn.is-loading {
  @apply cursor-wait;
  /* Mantém cor vibrante durante loading */
}

.btn:not(:disabled):not(.is-loading):hover {
  @apply transform scale-105;
}

.btn:not(:disabled):not(.is-loading):active {
  @apply transform scale-95;
}

.btn-icon {
  @apply inline-flex items-center;
}

.btn-content {
  @apply inline-flex items-center;
}
</style>

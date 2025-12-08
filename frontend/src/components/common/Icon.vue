<template>
  <component 
    :is="iconComponent" 
    :size="size"
    :stroke-width="strokeWidth"
    :class="iconClass"
    :aria-label="ariaLabel"
    :aria-hidden="!ariaLabel"
  />
</template>

<script setup>
import { computed } from 'vue'
import { getIcon } from '@/utils/iconMapping'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: [Number, String],
    default: 16
  },
  strokeWidth: {
    type: [Number, String],
    default: 1.5
  },
  class: {
    type: String,
    default: ''
  },
  ariaLabel: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'terminal-green'
  }
})

const iconComponent = computed(() => getIcon(props.name))

const iconClass = computed(() => {
  const baseClass = `text-${props.color}`
  return `${baseClass} ${props.class}`.trim()
})
</script>

<style scoped>
/* Ícones herdam a cor do texto através da classe Tailwind */
</style>



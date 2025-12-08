<template>
  <div class="metric-card" :class="{ 'metric-card-clickable': clickable }" @click="handleClick">
    <div class="metric-icon-wrapper" v-if="iconComponent">
      <component 
        :is="iconComponent" 
        :size="20"
        :stroke-width="1.5"
        class="metric-icon"
        :aria-label="label"
      />
    </div>
    <div class="metric-content">
      <div class="metric-label tech-label">{{ label.toUpperCase() }}</div>
      <div class="metric-value tech-value tabular-nums" :class="valueClass">
        {{ formattedValue }}
      </div>
      <div v-if="showProgress" class="metric-progress">
        <div 
          class="metric-progress-bar"
          :class="progressClass"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
      <div v-if="badge" class="metric-badge" :class="badgeClass">
        {{ badge }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getIcon } from '@/utils/iconMapping'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    default: null
  },
  icon: {
    type: String,
    default: null
  },
  badge: {
    type: String,
    default: null
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  progressPercent: {
    type: Number,
    default: 0
  },
  progressClass: {
    type: String,
    default: 'progress-default'
  },
  valueClass: {
    type: String,
    default: ''
  },
  badgeClass: {
    type: String,
    default: ''
  },
  format: {
    type: String,
    default: 'number' // 'number', 'price', 'percent', 'custom'
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const iconComponent = computed(() => {
  if (!props.icon) return null
  return getIcon(props.icon)
})

const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) return '--'
  
  if (props.format === 'price') {
    return `$${parseFloat(props.value).toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`
  }
  
  if (props.format === 'percent') {
    return `${parseFloat(props.value).toFixed(2)}%`
  }
  
  if (props.format === 'number') {
    return parseFloat(props.value).toLocaleString('pt-BR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    })
  }
  
  return props.value
})

const handleClick = () => {
  if (props.clickable) {
    emit('click', {
      label: props.label,
      value: props.value
    })
  }
}
</script>

<style scoped>
.metric-card {
  @apply bg-terminal-dark rounded-lg border border-terminal-green/20 p-4;
  @apply transition-all duration-300;
  @apply hover:border-terminal-green/50;
  @apply hover:shadow-lg;
  @apply hover:shadow-terminal-green/10;
}

.metric-card-clickable {
  @apply cursor-pointer;
}

.metric-card-clickable:hover {
  @apply transform scale-105;
}

.metric-icon-wrapper {
  @apply mb-2 flex items-center justify-center;
}

.metric-icon {
  @apply text-terminal-green;
}

.metric-content {
  @apply flex flex-col;
}

.metric-label {
  @apply text-xs text-terminal-green/70 mb-1 font-mono;
  letter-spacing: 0.05em;
}

.metric-value {
  @apply text-xl font-bold text-terminal-green mb-2 font-mono;
}

.metric-progress {
  @apply w-full h-2 bg-terminal-gray rounded-full overflow-hidden;
  @apply border border-terminal-green/20;
}

.metric-progress-bar {
  @apply h-full transition-all duration-500 ease-out;
}

.metric-progress-bar.progress-default {
  @apply bg-terminal-green;
}

.metric-progress-bar.progress-excellent {
  @apply bg-gradient-to-r from-green-500 to-green-600;
}

.metric-progress-bar.progress-good {
  @apply bg-gradient-to-r from-terminal-green to-green-500;
}

.metric-progress-bar.progress-medium {
  @apply bg-gradient-to-r from-yellow-500 to-yellow-600;
}

.metric-progress-bar.progress-low {
  @apply bg-gradient-to-r from-red-500 to-red-600;
}

.metric-badge {
  @apply inline-block px-2 py-1 rounded text-xs font-bold mt-2;
  @apply bg-terminal-green/20 text-terminal-green border border-terminal-green/50;
}

/* Responsividade */
@media (max-width: 768px) {
  .metric-card {
    @apply p-3;
  }
  
  .metric-value {
    @apply text-lg;
  }
}
</style>


<template>
  <div class="timeframe-selector-compact">
    <button
      ref="buttonRef"
      @click="showDropdown = !showDropdown"
      @blur="handleBlur"
      class="timeframe-btn-compact"
      :title="`${getTimeframeLabel(selected)} (Clique para ver opções)`"
    >
      <span class="timeframe-value">{{ selected }}</span>
      <span v-if="isPopular(selected)" class="popular-indicator">⭐</span>
      <span class="dropdown-arrow">▼</span>
    </button>
    
    <!-- Dropdown (Teleported to body) -->
    <Teleport to="body">
      <div 
        v-if="showDropdown"
        class="timeframe-dropdown"
        :style="dropdownStyle"
        @click.stop
      >
        <!-- Curtos -->
        <div class="dropdown-section">
          <div class="section-label">Curtos</div>
          <div class="timeframe-options">
            <button
              v-for="tf in timeframes.curtos"
              :key="tf.value"
              @click="selectTimeframe(tf.value)"
              class="timeframe-option"
              :class="{ 'active': selected === tf.value, 'popular': tf.popular }"
              :title="`${tf.label}${tf.shortcut ? ' (Atalho: ' + tf.shortcut + ')' : ''}`"
            >
              {{ tf.value }}
              <span v-if="tf.popular" class="popular-badge">⭐</span>
            </button>
          </div>
        </div>
        
        <!-- Médios -->
        <div class="dropdown-section">
          <div class="section-label">Médios</div>
          <div class="timeframe-options">
            <button
              v-for="tf in timeframes.medios"
              :key="tf.value"
              @click="selectTimeframe(tf.value)"
              class="timeframe-option"
              :class="{ 'active': selected === tf.value, 'popular': tf.popular }"
              :title="`${tf.label}${tf.shortcut ? ' (Atalho: ' + tf.shortcut + ')' : ''}`"
            >
              {{ tf.value }}
              <span v-if="tf.popular" class="popular-badge">⭐</span>
            </button>
          </div>
        </div>
        
        <!-- Longos -->
        <div class="dropdown-section">
          <div class="section-label">Longos</div>
          <div class="timeframe-options">
            <button
              v-for="tf in timeframes.longos"
              :key="tf.value"
              @click="selectTimeframe(tf.value)"
              class="timeframe-option"
              :class="{ 'active': selected === tf.value, 'popular': tf.popular }"
              :title="tf.label"
            >
              {{ tf.value }}
              <span v-if="tf.popular" class="popular-badge">⭐</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '1h' }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selected = ref(props.modelValue)
const showDropdown = ref(false)
const buttonRef = ref(null)

// Dynamic positioning for teleported dropdown
const dropdownStyle = computed(() => {
  if (!buttonRef.value) return {}
  
  const rect = buttonRef.value.getBoundingClientRect()
  return {
    position: 'fixed',
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    minWidth: `${Math.max(rect.width, 200)}px`
  }
})

const timeframes = {
  curtos: [
    { value: '1m', label: '1 Minuto', shortcut: '1' },
    { value: '3m', label: '3 Minutos', shortcut: '2' },
    { value: '5m', label: '5 Minutos', shortcut: '3' },
    { value: '15m', label: '15 Minutos', shortcut: '4' },
    { value: '30m', label: '30 Minutos', shortcut: '5' }
  ],
  medios: [
    { value: '1h', label: '1 Hora', shortcut: '6', popular: true },
    { value: '2h', label: '2 Horas', shortcut: '7' },
    { value: '4h', label: '4 Horas', shortcut: '8', popular: true },
    { value: '6h', label: '6 Horas', shortcut: '9' },
    { value: '8h', label: '8 Horas' },
    { value: '12h', label: '12 Horas' }
  ],
  longos: [
    { value: '1d', label: '1 Dia', popular: true },
    { value: '3d', label: '3 Dias' },
    { value: '1w', label: '1 Semana' },
    { value: '1M', label: '1 Mês' }
  ]
}

const getTimeframeLabel = (value) => {
  const all = [...timeframes.curtos, ...timeframes.medios, ...timeframes.longos]
  const tf = all.find(t => t.value === value)
  return tf ? tf.label : value
}

const isPopular = (value) => {
  const all = [...timeframes.curtos, ...timeframes.medios, ...timeframes.longos]
  const tf = all.find(t => t.value === value)
  return tf?.popular || false
}

const selectTimeframe = (value) => {
  selected.value = value
  emit('update:modelValue', value)
  emit('change', value)
  showDropdown.value = false
}

const handleBlur = () => {
  // Delay para permitir click em opções
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

// Atalhos de teclado
const handleKeydown = (e) => {
  // Só funciona se não estiver digitando em input
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
    return
  }
  
  const shortcuts = {
    '1': '1m', '2': '3m', '3': '5m', '4': '15m', '5': '30m',
    '6': '1h', '7': '2h', '8': '4h', '9': '6h'
  }
  
  if (shortcuts[e.key]) {
    e.preventDefault()
    selectTimeframe(shortcuts[e.key])
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.timeframe-selector-compact {
  position: relative;
  display: inline-block;
}

.timeframe-btn-compact {
  @apply px-3 py-2 rounded border border-terminal-green/30 
         bg-terminal-dark text-terminal-green
         hover:border-terminal-green hover:bg-terminal-green/10
         transition cursor-pointer
         font-mono text-sm font-semibold
         flex items-center gap-2
         min-w-[80px];
}

.timeframe-value {
  @apply font-bold;
}

.popular-indicator {
  @apply text-xs;
}

.dropdown-arrow {
  @apply text-xs text-terminal-green/70;
  transition: transform 0.2s;
}

.timeframe-btn-compact:hover .dropdown-arrow {
  transform: translateY(2px);
}

.timeframe-dropdown {
  /* Position handled by inline style (fixed positioning) */
  z-index: var(--z-modal); /* Enterprise layer system */
  background: #1a1a1a;
  border: 1px solid #00ff88;
  border-radius: 4px;
  margin-top: 0; /* Removed since spacing handled in JS */
  padding: 8px;
  max-height: 400px;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.dropdown-section {
  @apply mb-3 last:mb-0;
}

.section-label {
  @apply text-xs text-terminal-green/70 font-semibold mb-2 px-2;
}

.timeframe-options {
  @apply flex flex-wrap gap-1;
}

.timeframe-option {
  @apply px-2 py-1 rounded border border-terminal-green/20 
         bg-terminal-dark text-terminal-green
         hover:border-terminal-green hover:bg-terminal-green/10
         transition cursor-pointer relative
         font-mono text-xs font-semibold;
}

.timeframe-option.active {
  @apply bg-terminal-green text-terminal-dark border-terminal-green;
}

.timeframe-option.popular {
  @apply border-terminal-green/50;
}

.popular-badge {
  @apply absolute -top-0.5 -right-0.5 text-xs;
}
</style>

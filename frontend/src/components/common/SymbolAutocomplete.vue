<template>
  <div class="symbol-autocomplete">
    <div ref="inputWrapper" class="input-wrapper">
      <input
        v-model="searchQuery"
        @input="handleInput"
        @keydown="handleKeydown"
        @focus="showSuggestions = true"
        @blur="handleBlur"
        class="input-field w-full"
        :placeholder="placeholder"
        autocomplete="off"
      />
      <span v-if="selectedSymbol && !searchQuery" class="selected-badge">
        {{ selectedSymbol }}
      </span>
    </div>
    
    <!-- Dropdown de Sugestões (Teleported to body) -->
    <Teleport to="body">
      <div 
        v-if="showSuggestions && suggestions.length > 0"
        ref="suggestionsDropdown"
        class="suggestions-dropdown"
        :style="dropdownStyle"
      >
        <div
          v-for="(symbol, index) in suggestions"
          :key="symbol.symbol"
          @click="selectSymbol(symbol)"
          @mouseenter="hoveredIndex = index"
          class="suggestion-item"
          :class="{ 'hovered': hoveredIndex === index }"
          :ref="el => { if (el) suggestionItems[index] = el }"
        >
          <div class="symbol-info">
            <span class="symbol-code">{{ symbol.symbol }}</span>
            <span class="symbol-name">{{ symbol.name }}</span>
          </div>
          <div v-if="hasStats(symbol)" class="symbol-stats">
            <span v-if="symbol.volume_24h" class="volume">
              Vol: ${{ formatVolume(symbol.volume_24h) }}
            </span>
            <span 
              v-if="isValidChange(symbol.change_24h)"
              class="change"
              :class="symbol.change_24h >= 0 ? 'positive' : 'negative'"
            >
              {{ symbol.change_24h >= 0 ? '+' : '' }}{{ formatChange(symbol.change_24h) }}%
            </span>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- Estado vazio (Teleported to body) -->
    <Teleport to="body">
      <div 
        v-if="showSuggestions && searchQuery.length >= 1 && suggestions.length === 0 && !loading"
        class="suggestions-empty"
        :style="dropdownStyle"
      >
        Nenhum símbolo encontrado para "{{ searchQuery }}"
      </div>
    </Teleport>
    
    <!-- Loading (Teleported to body) -->
    <Teleport to="body">
      <div 
        v-if="loading"
        class="suggestions-loading"
        :style="dropdownStyle"
      >
        Buscando...
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'
import { debounce } from '@/utils/debounce'
import { formatVolume } from '@/utils/formatters'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: 'Digite 3 letras (ex: BTC, ETH)...' }
})

const emit = defineEmits(['update:modelValue', 'select'])

const searchQuery = ref(props.modelValue || '')
const suggestions = ref([])
const showSuggestions = ref(false)
const hoveredIndex = ref(-1)
const loading = ref(false)
const selectedSymbol = ref(props.modelValue || '')
const suggestionsDropdown = ref(null)
const suggestionItems = ref([])
const inputWrapper = ref(null)

// Dynamic positioning for teleported dropdown
const dropdownStyle = computed(() => {
  if (!inputWrapper.value) return {}
  
  const rect = inputWrapper.value.getBoundingClientRect()
  return {
    position: 'fixed',
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`
  }
})

// Debounce para evitar muitas requisições
const searchSymbols = debounce(async (query) => {
  if (query.length < 1) {
    suggestions.value = []
    return
  }
  
  loading.value = true
  try {
    const response = await api.searchSymbols(query)
    suggestions.value = response.symbols || []
  } catch (error) {
    console.error('Erro ao buscar símbolos:', error)
    suggestions.value = []
  } finally {
    loading.value = false
  }
}, 300)

const handleInput = (e) => {
  searchQuery.value = e.target.value.toUpperCase()
  selectedSymbol.value = ''
  searchSymbols(searchQuery.value)
}

const handleKeydown = (e) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    hoveredIndex.value = Math.min(hoveredIndex.value + 1, suggestions.value.length - 1)
    scrollToHovered()
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    hoveredIndex.value = Math.max(hoveredIndex.value - 1, -1)
    scrollToHovered()
  } else if (e.key === 'Enter' && hoveredIndex.value >= 0) {
    e.preventDefault()
    selectSymbol(suggestions.value[hoveredIndex.value])
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
  }
}

const handleBlur = () => {
  // Delay para permitir click em sugestões
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

const selectSymbol = (symbol) => {
  searchQuery.value = symbol.symbol
  selectedSymbol.value = symbol.symbol
  emit('update:modelValue', symbol.symbol)
  emit('select', symbol)
  showSuggestions.value = false
  hoveredIndex.value = -1
}

const hasStats = (symbol) => {
  return symbol.volume_24h || isValidChange(symbol.change_24h)
}

const isValidChange = (change) => {
  return change !== null && change !== undefined && typeof change === 'number' && !isNaN(change)
}

const formatChange = (change) => {
  if (!isValidChange(change)) return '0.00'
  return change.toFixed(2)
}

// Scroll automático para item hovered
const scrollToHovered = () => {
  nextTick(() => {
    if (hoveredIndex.value >= 0 && suggestionItems.value[hoveredIndex.value]) {
      const hoveredItem = suggestionItems.value[hoveredIndex.value]
      if (hoveredItem && suggestionsDropdown.value) {
        hoveredItem.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        })
      }
    }
  })
}

// Watch para atualizar quando modelValue mudar externamente
watch(() => props.modelValue, (newValue) => {
  if (newValue !== searchQuery.value) {
    searchQuery.value = newValue || ''
    selectedSymbol.value = newValue || ''
  }
})
</script>

<style scoped>
.symbol-autocomplete {
  position: relative;
}

.input-wrapper {
  position: relative;
}

.selected-badge {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  pointer-events: none;
}

.suggestions-dropdown {
  /* Position handled by inline style (fixed positioning) */
  z-index: var(--z-modal); /* Enterprise layer system */
  background: #1a1a1a;
  border: 1px solid #00ff88;
  border-radius: 4px;
  margin-top: 0; /* Removed since spacing handled in JS */
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.suggestion-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 255, 136, 0.1);
  transition: background 0.2s;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover,
.suggestion-item.hovered {
  background: rgba(0, 255, 136, 0.1);
}

.symbol-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.symbol-code {
  font-weight: bold;
  color: #00ff88;
}

.symbol-name {
  color: rgba(0, 255, 136, 0.7);
  font-size: 0.9em;
}

.symbol-stats {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 0.85em;
}

.volume {
  color: rgba(0, 255, 136, 0.6);
}

.change.positive {
  color: #00ff88;
}

.change.negative {
  color: #ff4444;
}

.suggestions-empty,
.suggestions-loading {
  /* Position handled by inline style (fixed positioning) */
  z-index: var(--z-modal); /* Enterprise layer system */
  background: #1a1a1a;
  border: 1px solid #00ff88;
  border-radius: 4px;
  margin-top: 0; /* Removed since spacing handled in JS */
  padding: 12px;
  color: rgba(0, 255, 136, 0.7);
  text-align: center;
  font-size: 0.9em;
}
</style>


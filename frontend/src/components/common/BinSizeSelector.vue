<template>
  <div class="bin-size-selector-compact">
    <button
      @click="showDropdown = !showDropdown"
      @blur="handleBlur"
      class="timeframe-btn-compact"
      :title="`${getBinLabel(selected)} (Clique para ver opções)`"
    >
      <span class="timeframe-value">Bin: ${{ selected === '0' ? '--' : formatBin(selected) }}</span>
      <span class="dropdown-arrow">▼</span>
    </button>
    
    <!-- Dropdown -->
    <div 
      v-if="showDropdown"
      class="timeframe-dropdown"
      @click.stop
    >
      <div class="dropdown-section">
        <div class="section-label">Agrupamento</div>
        <div class="timeframe-options">
          <button
            v-for="bin in binSizes"
            :key="bin.value"
            @click="selectBin(bin.value)"
            class="timeframe-option"
            :class="{ 'active': selected === bin.value }"
            :title="bin.label"
          >
            {{ bin.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '100' }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selected = ref(props.modelValue)
const showDropdown = ref(false)

const binSizes = [
  { value: '0', label: 'Sem Agrupamento' },
  { value: '100', label: 'Bin: $100', popular: true },
  { value: '500', label: 'Bin: $500' },
  { value: '1000', label: 'Bin: $1k' },
  { value: '5000', label: 'Bin: $5k' },
  { value: '10000', label: 'Bin: $10k' }
]

const getBinLabel = (value) => {
  if (value === '0') return 'Sem Agrupamento'
  const bin = binSizes.find(b => b.value === value)
  return bin ? bin.label : `Bin: $${formatBin(value)}`
}

const formatBin = (value) => {
  const num = parseInt(value)
  if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'k'
  }
  return num.toString()
}

const selectBin = (value) => {
  selected.value = value
  emit('update:modelValue', value)
  emit('change', value)
  showDropdown.value = false
}

const handleBlur = () => {
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}
</script>

<style scoped>
.bin-size-selector-compact {
  position: relative;
  display: inline-block;
}

.timeframe-btn-compact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 0.375rem;
  color: #00ff00;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
}

.timeframe-btn-compact:hover {
  background: rgba(0, 255, 0, 0.2);
  border-color: rgba(0, 255, 0, 0.5);
}

.timeframe-value {
  flex: 1;
  text-align: left;
}

.dropdown-arrow {
  font-size: 0.75rem;
  opacity: 0.7;
}

.timeframe-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.25rem;
  background: #0a0a0a;
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  min-width: 200px;
  max-height: 300px;
  overflow-y: auto;
}

.dropdown-section {
  padding: 0.5rem;
}

.section-label {
  font-size: 0.75rem;
  color: rgba(0, 255, 0, 0.5);
  text-transform: uppercase;
  margin-bottom: 0.5rem;
  padding: 0 0.5rem;
}

.timeframe-options {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.timeframe-option {
  padding: 0.5rem;
  text-align: left;
  background: transparent;
  border: none;
  color: #00ff00;
  cursor: pointer;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.timeframe-option:hover {
  background: rgba(0, 255, 0, 0.1);
}

.timeframe-option.active {
  background: rgba(0, 255, 0, 0.2);
  border-left: 2px solid #00ff00;
}
</style>


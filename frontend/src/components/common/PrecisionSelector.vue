<template>
  <div class="precision-selector-compact">
    <button
      @click="showDropdown = !showDropdown"
      @blur="handleBlur"
      class="timeframe-btn-compact"
      :title="`Precisão: ${getPrecisionLabel(selected)} (Clique para ver opções)`"
    >
      <span class="timeframe-value">Prec: {{ selected }}</span>
      <span class="dropdown-arrow">▼</span>
    </button>
    
    <!-- Dropdown -->
    <div 
      v-if="showDropdown"
      class="timeframe-dropdown"
      @click.stop
    >
      <div class="dropdown-section">
        <div class="section-label">Precisão</div>
        <div class="timeframe-options">
          <button
            v-for="prec in precisions"
            :key="prec.value"
            @click="selectPrecision(prec.value)"
            class="timeframe-option"
            :class="{ 'active': selected === prec.value }"
            :title="prec.label"
          >
            {{ prec.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '2' }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selected = ref(props.modelValue)
const showDropdown = ref(false)

const precisions = [
  { value: '0', label: 'Inteiro (0 decimais)' },
  { value: '1', label: '1 decimal' },
  { value: '2', label: '2 decimais' },
  { value: '3', label: '3 decimais' }
]

const getPrecisionLabel = (value) => {
  const prec = precisions.find(p => p.value === value)
  return prec ? prec.label : `${value} decimais`
}

const selectPrecision = (value) => {
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
.precision-selector-compact {
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
  min-width: 100px;
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
  min-width: 180px;
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




<template>
  <div class="radar-controls">
    <div class="controls-row">
      <label class="control-label">Filtro de Sinal:</label>
      <select v-model="localFilterSignal" @change="updateFilters" class="control-select">
        <option value="">Todos</option>
        <option value="BUY">BUY</option>
        <option value="SELL">SELL</option>
        <option value="NEUTRAL">NEUTRAL</option>
      </select>
    </div>
    
    <div class="controls-row">
      <label class="control-label">Score Mínimo:</label>
      <select v-model="localFilterMinScore" @change="updateFilters" class="control-select">
        <option value="-10">Todos</option>
        <option value="0">≥ 0</option>
        <option value="5">≥ 5</option>
        <option value="7">≥ 7</option>
      </select>
    </div>
    
    <div class="controls-row">
      <label class="control-label">Timeframe:</label>
      <select v-model="localTimeframe" @change="updateTimeframe" class="control-select">
        <option value="1h">1h</option>
        <option value="4h">4h</option>
        <option value="1d">1d</option>
      </select>
    </div>
    
    <div class="controls-row">
      <button 
        @click="$emit('refresh', true)"
        class="control-button"
        :disabled="loading"
      >
        <span v-if="loading">⏳</span>
        <span v-else>🔄</span>
        {{ loading ? 'Atualizando...' : 'Atualizar Radar' }}
      </button>
    </div>
    
    <div class="controls-stats">
      <div class="stat-item">
        <span class="stat-label">Blips:</span>
        <span class="stat-value">{{ blipCount }}/20</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Última varredura:</span>
        <div class="stat-value-container">
          <span class="stat-value">{{ lastUpdate || '--' }}</span>
          <div v-if="loading" class="sonar-scanner">
            <div class="sonar-pulse"></div>
            <div class="sonar-line"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  filterSignal: {
    type: String,
    default: ''
  },
  filterMinScore: {
    type: String,
    default: '-10'
  },
  timeframe: {
    type: String,
    default: '1h'
  },
  loading: {
    type: Boolean,
    default: false
  },
  blipCount: {
    type: Number,
    default: 0
  },
  lastUpdate: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:filters', 'update:timeframe', 'refresh'])

const localFilterSignal = ref(props.filterSignal)
const localFilterMinScore = ref(props.filterMinScore)
const localTimeframe = ref(props.timeframe)

watch(() => props.filterSignal, (val) => {
  localFilterSignal.value = val
})

watch(() => props.filterMinScore, (val) => {
  localFilterMinScore.value = val
})

watch(() => props.timeframe, (val) => {
  localTimeframe.value = val
})

const updateFilters = () => {
  emit('update:filters', {
    signal: localFilterSignal.value,
    minScore: localFilterMinScore.value
  })
}

const updateTimeframe = () => {
  emit('update:timeframe', localTimeframe.value)
}
</script>

<style scoped>
.radar-controls {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid #00ff0030;
  border-radius: 6px;
  padding: 12px; /* Reduzido de 16px */
  display: flex;
  flex-direction: column;
  gap: 10px; /* Reduzido de 12px */
  width: 100%;
}

.controls-row {
  display: flex;
  flex-direction: column; /* Mudado para coluna para economizar espaço */
  gap: 6px; /* Reduzido de 12px */
}

.control-label {
  color: #00ff0070;
  font-size: 10px; /* Reduzido de 12px */
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: 'JetBrains Mono', monospace;
}

.control-select {
  width: 100%;
  background: #0a0a0a;
  border: 1px solid #00ff0030;
  color: #00ff00;
  padding: 6px 10px; /* Reduzido padding */
  border-radius: 4px;
  font-size: 11px; /* Reduzido de 12px */
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'JetBrains Mono', monospace;
}

.control-select:hover {
  border-color: #00ff00;
}

.control-select:focus {
  outline: none;
  border-color: #00ff00;
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.control-button {
  width: 100%;
  background: #0a0a0a;
  border: 2px solid #00ff00;
  color: #00ff00;
  padding: 8px 12px; /* Reduzido */
  border-radius: 4px;
  font-size: 11px; /* Reduzido de 12px */
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px; /* Reduzido de 8px */
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.control-button:hover:not(:disabled) {
  background: #00ff00;
  color: #000000;
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
}

.control-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.controls-stats {
  margin-top: 6px; /* Reduzido de 8px */
  padding-top: 10px; /* Reduzido de 12px */
  border-top: 1px solid #00ff0030;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px; /* Reduzido de 11px */
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  color: #00ff0070;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 9px;
}

.stat-value {
  color: #00ff00;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.stat-value-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Scanner de Sonar - Animação */
.sonar-scanner {
  position: relative;
  width: 20px;
  height: 20px;
  display: inline-block;
}

.sonar-pulse {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid #00ff00;
  border-radius: 50%;
  animation: sonar-pulse 2s ease-out infinite;
  opacity: 0;
}

.sonar-pulse::before {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid #00ff00;
  border-radius: 50%;
  animation: sonar-pulse 2s ease-out infinite 0.5s;
  opacity: 0;
}

.sonar-line {
  position: absolute;
  width: 10px;
  height: 2px;
  background: #00ff00;
  border-radius: 1px;
  top: 50%;
  left: 50%;
  transform-origin: 0 50%;
  animation: sonar-sweep 2s linear infinite;
  box-shadow: 0 0 4px #00ff00;
}

@keyframes sonar-pulse {
  0% {
    transform: scale(0.5);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

@keyframes sonar-sweep {
  0% {
    transform: translate(-50%, -50%) rotate(0deg);
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) rotate(360deg);
    opacity: 1;
  }
}
</style>


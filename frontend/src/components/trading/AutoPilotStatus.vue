<template>
  <div class="autopilot-status">
    <div class="status-header">
      <h3>🤖 MOTOR SNE AUTÔNOMO</h3>
      <div class="status-toggle">
        <button 
          @click="toggleMotor"
          :class="['toggle-btn', motorEnabled ? 'enabled' : 'disabled']"
          :disabled="loading"
        >
          <span class="toggle-indicator"></span>
          <span class="toggle-label">{{ motorEnabled ? 'ON' : 'OFF' }}</span>
        </button>
      </div>
    </div>
    
    <div v-if="status" class="status-info">
      <div class="info-row">
        <span class="label">Status:</span>
        <span :class="['value', motorEnabled ? 'running' : 'stopped']">
          {{ motorEnabled ? '🟢 Rodando' : '🔴 Parado' }}
        </span>
      </div>
      
      <div class="info-row">
        <span class="label">Pares Monitorados:</span>
        <span class="value">{{ monitoredSymbolsCount }}</span>
      </div>
      
      <div class="info-row">
        <span class="label">Timeframe:</span>
        <span class="value">{{ status.default_timeframe || '1h' }}</span>
      </div>
      
      <div class="info-row">
        <span class="label">Confluência Mínima:</span>
        <span class="value">{{ status.min_confluencia_global || 75 }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTradingStore } from '../../stores/trading'

const tradingStore = useTradingStore()

const status = computed(() => tradingStore.autopilotStatus)
const loading = computed(() => tradingStore.loading)
const motorEnabled = computed(() => status.value?.motor_enabled || false)
const monitoredSymbolsCount = computed(() => 
  status.value?.monitored_symbols?.length || 0
)

const toggleMotor = async () => {
  if (motorEnabled.value) {
    await tradingStore.stopAutopilot()
  } else {
    await tradingStore.startAutopilot()
  }
}
</script>

<style scoped>
.autopilot-status {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 255, 0, 0.2);
}

.status-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 2px solid;
  border-radius: 20px;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: bold;
}

.toggle-btn.enabled {
  border-color: #00ff00;
  color: #00ff00;
}

.toggle-btn.disabled {
  border-color: #ff0000;
  color: #ff0000;
}

.toggle-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-row .label {
  color: rgba(0, 255, 0, 0.7);
}

.info-row .value {
  color: #00ff00;
  font-weight: 500;
}

.info-row .value.running {
  color: #00ff00;
}

.info-row .value.stopped {
  color: #ff0000;
}
</style>



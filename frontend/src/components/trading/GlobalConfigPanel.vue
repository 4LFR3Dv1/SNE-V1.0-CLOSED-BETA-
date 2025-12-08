<template>
  <div class="global-config-panel">
    <div class="panel-header">
      <h3>⚙️ FILTROS GLOBAIS DE SEGURANÇA</h3>
      <button 
        @click="showConfig = !showConfig"
        class="btn-toggle"
      >
        {{ showConfig ? '▼' : '▶' }}
      </button>
    </div>
    
    <div v-if="showConfig && config" class="config-content">
      <div class="config-group">
        <label>Confluência Mínima (%)</label>
        <input 
          v-model.number="localConfig.min_confluencia_global"
          type="number"
          min="0"
          max="100"
          step="0.1"
          class="config-input"
        />
      </div>
      
      <div class="config-group">
        <label>Risco Máximo por Trade (%)</label>
        <input 
          v-model.number="localConfig.max_risk_per_trade_pct"
          type="number"
          min="0.1"
          max="10"
          step="0.1"
          class="config-input"
        />
      </div>
      
      <div class="config-group">
        <label>Timeframe Padrão</label>
        <select v-model="localConfig.default_timeframe" class="config-input">
          <option value="1m">1m</option>
          <option value="5m">5m</option>
          <option value="15m">15m</option>
          <option value="1h">1h</option>
          <option value="4h">4h</option>
          <option value="1d">1d</option>
        </select>
      </div>
      
      <div class="config-group">
        <label>
          <input 
            type="checkbox"
            v-model="localConfig.trade_24_7"
            class="checkbox"
          />
          Operar 24/7
        </label>
      </div>
      
      <div class="config-group">
        <label>Pares Monitorados (separados por vírgula)</label>
        <input 
          v-model="symbolsInput"
          type="text"
          placeholder="BTCUSDT, ETHUSDT, BNBUSDT"
          class="config-input"
        />
        <small>Ex: BTCUSDT, ETHUSDT, BNBUSDT</small>
      </div>
      
      <div class="config-actions">
        <button @click="saveConfig" class="btn-save" :disabled="saving">
          {{ saving ? 'Salvando...' : 'Salvar Configuração' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTradingStore } from '../../stores/trading'

const tradingStore = useTradingStore()

const showConfig = ref(false)
const saving = ref(false)
const config = computed(() => tradingStore.autopilotConfig)

const localConfig = ref({
  min_confluencia_global: 75,
  max_risk_per_trade_pct: 1.5,
  default_timeframe: '1h',
  trade_24_7: true,
  monitored_symbols: []
})

const symbolsInput = computed({
  get: () => localConfig.value.monitored_symbols?.join(', ') || '',
  set: (value) => {
    localConfig.value.monitored_symbols = value
      .split(',')
      .map(s => s.trim().toUpperCase())
      .filter(s => s.length > 0)
  }
})

watch(config, (newConfig) => {
  if (newConfig) {
    localConfig.value = {
      min_confluencia_global: newConfig.min_confluencia_global || 75,
      max_risk_per_trade_pct: newConfig.max_risk_per_trade_pct || 1.5,
      default_timeframe: newConfig.default_timeframe || '1h',
      trade_24_7: newConfig.trade_24_7 !== false,
      monitored_symbols: newConfig.monitored_symbols || []
    }
  }
}, { immediate: true })

const saveConfig = async () => {
  try {
    saving.value = true
    await tradingStore.updateAutopilotConfig(localConfig.value)
  } catch (err) {
    console.error('Erro ao salvar configuração:', err)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.global-config-panel {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
}

.btn-toggle {
  background: transparent;
  border: 1px solid rgba(0, 255, 0, 0.3);
  color: #00ff00;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-group label {
  color: rgba(0, 255, 0, 0.9);
  font-size: 13px;
  font-weight: 500;
}

.config-input {
  padding: 8px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 4px;
  color: #00ff00;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.config-input:focus {
  outline: none;
  border-color: #00ff00;
  box-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
}

.config-group small {
  color: rgba(0, 255, 0, 0.5);
  font-size: 11px;
  font-style: italic;
}

.checkbox {
  margin-right: 8px;
}

.config-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 255, 0, 0.2);
}

.btn-save {
  padding: 10px 20px;
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid rgba(0, 255, 0, 0.5);
  border-radius: 4px;
  color: #00ff00;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-save:hover:not(:disabled) {
  background: rgba(0, 255, 0, 0.3);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>



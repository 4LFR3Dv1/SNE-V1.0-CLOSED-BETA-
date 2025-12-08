<template>
  <div class="strategy-card" :class="{ 'active': strategy.status === 'active', 'paused': strategy.status === 'paused', 'stopped': strategy.status === 'stopped' }">
    <div class="strategy-header">
      <div class="strategy-title">
        <h3>{{ strategy.name }}</h3>
        <span class="strategy-type">{{ strategy.type }}</span>
      </div>
      <div class="strategy-status">
        <div class="status-indicator" :class="strategy.status">
          <div class="status-dot"></div>
          <span>{{ statusLabel }}</span>
        </div>
      </div>
    </div>
    
    <div class="strategy-health">
      <div class="health-indicator" :class="healthClass">
        <div class="health-dot"></div>
        <span>{{ healthLabel }}</span>
      </div>
    </div>
    
    <div class="strategy-metrics">
      <div class="metric">
        <span class="metric-label">Capital:</span>
        <span class="metric-value">{{ strategy.capital_allocation }}%</span>
      </div>
      <div class="metric">
        <span class="metric-label">Risco/Trade:</span>
        <span class="metric-value">{{ strategy.risk_per_trade }}%</span>
      </div>
      <div class="metric">
        <span class="metric-label">Max Pos:</span>
        <span class="metric-value">{{ strategy.max_positions }}</span>
      </div>
    </div>
    
    <div class="strategy-actions">
      <button 
        v-if="strategy.status === 'inactive' || strategy.status === 'stopped'"
        @click="$emit('start', strategy.id)"
        class="btn btn-start"
      >
        ▶ Iniciar
      </button>
      <button 
        v-if="strategy.status === 'active'"
        @click="$emit('pause', strategy.id)"
        class="btn btn-pause"
      >
        ⏸ Pausar
      </button>
      <button 
        v-if="strategy.status === 'active' || strategy.status === 'paused'"
        @click="$emit('stop', strategy.id)"
        class="btn btn-stop"
      >
        ⏹ Parar
      </button>
      <button 
        @click="$emit('edit', strategy.id)"
        class="btn btn-edit"
      >
        ✏️ Editar
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  strategy: {
    type: Object,
    required: true
  }
})

defineEmits(['start', 'pause', 'stop', 'edit'])

const statusLabel = computed(() => {
  const labels = {
    'active': 'Ativa',
    'paused': 'Pausada',
    'stopped': 'Parada',
    'inactive': 'Inativa'
  }
  return labels[props.strategy.status] || props.strategy.status
})

const healthClass = computed(() => {
  return props.strategy.health_status || 'unknown'
})

const healthLabel = computed(() => {
  const labels = {
    'healthy': 'Saudável',
    'warning': 'Atenção',
    'critical': 'Crítico',
    'unknown': 'Desconhecido'
  }
  return labels[props.strategy.health_status] || 'Desconhecido'
})
</script>

<style scoped>
.strategy-card {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(0, 255, 0, 0.2);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.strategy-card.active {
  border-color: rgba(0, 255, 0, 0.5);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
}

.strategy-card.paused {
  border-color: rgba(255, 255, 0, 0.5);
}

.strategy-card.stopped {
  border-color: rgba(255, 0, 0, 0.3);
  opacity: 0.7;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.strategy-title h3 {
  margin: 0;
  color: #00ff00;
  font-size: 18px;
}

.strategy-type {
  font-size: 12px;
  color: rgba(0, 255, 0, 0.6);
  text-transform: uppercase;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
}

.status-indicator.active .status-dot {
  background: #00ff00;
  box-shadow: 0 0 6px #00ff00;
}

.status-indicator.paused .status-dot {
  background: #ffff00;
  box-shadow: 0 0 6px #ffff00;
}

.status-indicator.stopped .status-dot {
  background: #ff0000;
}

.strategy-health {
  margin-bottom: 12px;
}

.health-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}

.health-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.health-indicator.healthy .health-dot {
  background: #00ff00;
  box-shadow: 0 0 4px #00ff00;
}

.health-indicator.warning .health-dot {
  background: #ffff00;
  box-shadow: 0 0 4px #ffff00;
}

.health-indicator.critical .health-dot {
  background: #ff0000;
  box-shadow: 0 0 4px #ff0000;
}

.strategy-metrics {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
}

.metric-label {
  color: rgba(0, 255, 0, 0.6);
  font-size: 10px;
}

.metric-value {
  color: #00ff00;
  font-weight: bold;
}

.strategy-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: 1px solid rgba(0, 255, 0, 0.3);
  background: rgba(0, 255, 0, 0.1);
  color: #00ff00;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.btn:hover {
  background: rgba(0, 255, 0, 0.2);
  border-color: rgba(0, 255, 0, 0.5);
}

.btn-start {
  border-color: rgba(0, 255, 0, 0.5);
}

.btn-pause {
  border-color: rgba(255, 255, 0, 0.5);
  color: #ffff00;
}

.btn-stop {
  border-color: rgba(255, 0, 0, 0.5);
  color: #ff0000;
}
</style>



<template>
  <div class="risk-dashboard">
    <div class="dashboard-header">
      <h3>⚠️ ALERTAS DE RISCO</h3>
      <span class="alert-count" :class="criticalCount > 0 ? 'critical' : ''">
        {{ criticalCount }}
      </span>
    </div>
    
    <div v-if="alerts.length === 0" class="empty-state">
      Nenhum alerta ativo
    </div>
    
    <div v-else class="alerts-list">
      <div 
        v-for="alert in alerts" 
        :key="alert.id"
        class="alert-item"
        :class="alert.severity"
      >
        <div class="alert-header">
          <span class="alert-type">{{ alert.type }}</span>
          <span class="alert-severity" :class="alert.severity">
            {{ alert.severity.toUpperCase() }}
          </span>
        </div>
        <div class="alert-message">{{ alert.message }}</div>
        <div v-if="alert.details" class="alert-details">
          <pre>{{ JSON.stringify(alert.details, null, 2) }}</pre>
        </div>
        <div class="alert-time">{{ formatTime(alert.created_at) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  alerts: {
    type: Array,
    default: () => []
  }
})

const criticalCount = computed(() => {
  return props.alerts.filter(a => a.severity === 'critical' && !a.resolved).length
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('pt-BR')
}
</script>

<style scoped>
.risk-dashboard {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.dashboard-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
}

.alert-count {
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid rgba(0, 255, 0, 0.3);
  padding: 4px 12px;
  border-radius: 12px;
  color: #00ff00;
  font-size: 12px;
  font-weight: bold;
}

.alert-count.critical {
  background: rgba(255, 0, 0, 0.2);
  border-color: rgba(255, 0, 0, 0.5);
  color: #ff0000;
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(0, 255, 0, 0.4);
  font-style: italic;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 0, 0.2);
  border-radius: 6px;
  padding: 12px;
}

.alert-item.low {
  border-color: rgba(0, 255, 0, 0.3);
}

.alert-item.medium {
  border-color: rgba(255, 255, 0, 0.3);
}

.alert-item.high {
  border-color: rgba(255, 165, 0, 0.3);
}

.alert-item.critical {
  border-color: rgba(255, 0, 0, 0.5);
  background: rgba(255, 0, 0, 0.1);
  animation: pulse-alert 2s infinite;
}

@keyframes pulse-alert {
  0%, 100% { box-shadow: 0 0 5px rgba(255, 0, 0, 0.3); }
  50% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.6); }
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.alert-type {
  font-size: 11px;
  color: rgba(0, 255, 0, 0.7);
  text-transform: uppercase;
}

.alert-severity {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: bold;
}

.alert-severity.low {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
}

.alert-severity.medium {
  background: rgba(255, 255, 0, 0.2);
  color: #ffff00;
}

.alert-severity.high {
  background: rgba(255, 165, 0, 0.2);
  color: #ffa500;
}

.alert-severity.critical {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
}

.alert-message {
  color: #00ff00;
  font-size: 12px;
  margin-bottom: 8px;
}

.alert-details {
  background: rgba(0, 0, 0, 0.5);
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 10px;
  color: rgba(0, 255, 0, 0.7);
  overflow-x: auto;
}

.alert-details pre {
  margin: 0;
  font-family: 'Courier New', monospace;
}

.alert-time {
  font-size: 10px;
  color: rgba(0, 255, 0, 0.5);
  text-align: right;
}
</style>



<template>
  <div class="execution-control">
    <div class="control-header">
      <h3>🎮 CONTROLE DE EXECUÇÃO</h3>
      <div class="global-status" :class="executionStatus">
        <div class="status-dot"></div>
        <span>{{ statusLabel }}</span>
      </div>
    </div>
    
    <div class="control-buttons">
      <button 
        @click="$emit('start-all')"
        class="btn btn-start-all"
        :disabled="executionStatus === 'running'"
      >
        ▶ Iniciar Todas
      </button>
      <button 
        @click="$emit('pause-all')"
        class="btn btn-pause-all"
        :disabled="executionStatus !== 'running'"
      >
        ⏸ Pausar Todas
      </button>
      <button 
        @click="$emit('stop-all')"
        class="btn btn-stop-all"
        :disabled="executionStatus === 'stopped'"
      >
        ⏹ Parar Todas
      </button>
    </div>
    
    <div class="emergency-section">
      <button 
        @click="confirmPanic"
        class="btn btn-panic"
        :disabled="loading"
      >
        🚨 PANIC CLOSE ALL
      </button>
      <p class="panic-warning">
        Fecha TODAS as posições imediatamente. Ignora verificações de risco.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  executionStatus: {
    type: String,
    default: 'stopped' // 'running', 'paused', 'stopped'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['start-all', 'pause-all', 'stop-all', 'panic'])

const statusLabel = computed(() => {
  const labels = {
    'running': 'Executando',
    'paused': 'Pausado',
    'stopped': 'Parado'
  }
  return labels[props.executionStatus] || 'Desconhecido'
})

const confirmPanic = () => {
  if (confirm('🚨 ATENÇÃO: Isso fechará TODAS as posições imediatamente!\n\nTem certeza?')) {
    if (confirm('⚠️ ÚLTIMA CONFIRMAÇÃO: Panic Close All?')) {
      emit('panic')
    }
  }
}
</script>

<style scoped>
.execution-control {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.control-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
}

.global-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
}

.global-status.running .status-dot {
  background: #00ff00;
  box-shadow: 0 0 8px #00ff00;
  animation: pulse 2s infinite;
}

.global-status.paused .status-dot {
  background: #ffff00;
  box-shadow: 0 0 8px #ffff00;
}

.global-status.stopped .status-dot {
  background: #ff0000;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.control-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.btn {
  flex: 1;
  padding: 10px;
  border: 1px solid rgba(0, 255, 0, 0.3);
  background: rgba(0, 255, 0, 0.1);
  color: #00ff00;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn:hover:not(:disabled) {
  background: rgba(0, 255, 0, 0.2);
  border-color: rgba(0, 255, 0, 0.5);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-start-all {
  border-color: rgba(0, 255, 0, 0.5);
}

.btn-pause-all {
  border-color: rgba(255, 255, 0, 0.5);
  color: #ffff00;
}

.btn-stop-all {
  border-color: rgba(255, 0, 0, 0.5);
  color: #ff0000;
}

.emergency-section {
  border-top: 1px solid rgba(255, 0, 0, 0.3);
  padding-top: 16px;
  margin-top: 16px;
}

.btn-panic {
  width: 100%;
  padding: 12px;
  background: rgba(255, 0, 0, 0.2);
  border: 2px solid rgba(255, 0, 0, 0.5);
  color: #ff0000;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.2s;
  animation: pulse-red 3s infinite;
}

.btn-panic:hover:not(:disabled) {
  background: rgba(255, 0, 0, 0.3);
  border-color: rgba(255, 0, 0, 0.7);
  transform: scale(1.02);
}

.btn-panic:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  animation: none;
}

@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 10px rgba(255, 0, 0, 0.3); }
  50% { box-shadow: 0 0 20px rgba(255, 0, 0, 0.6); }
}

.panic-warning {
  margin-top: 8px;
  font-size: 10px;
  color: rgba(255, 0, 0, 0.7);
  text-align: center;
  font-style: italic;
}
</style>



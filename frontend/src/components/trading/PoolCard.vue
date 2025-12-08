<template>
  <div class="pool-card" :class="pool.status">
    <div class="pool-header">
      <div class="pool-title">
        <h4>{{ pool.name }}</h4>
        <span :class="['status-badge', pool.status]">
          {{ statusLabel }}
        </span>
      </div>
      <div class="pool-actions">
        <button 
          v-if="pool.status === 'inactive' || pool.status === 'stopped'"
          @click="$emit('start', pool.id)"
          class="btn-action start"
          title="Ativar Pool"
        >
          ▶
        </button>
        <button 
          v-if="pool.status === 'active'"
          @click="$emit('stop', pool.id)"
          class="btn-action stop"
          title="Desativar Pool"
        >
          ⏸
        </button>
        <button 
          @click="$emit('edit', pool.id)"
          class="btn-action edit"
          title="Editar Pool"
        >
          ✏️
        </button>
        <button 
          @click="$emit('delete', pool.id)"
          class="btn-action delete"
          title="Deletar Pool"
        >
          🗑️
        </button>
      </div>
    </div>
    
    <div class="pool-content">
      <div class="pool-info">
        <div class="info-item">
          <span class="label">Capital:</span>
          <span class="value">${{ formatNumber(pool.capital_allocated) }}</span>
        </div>
        <div class="info-item">
          <span class="label">Usado:</span>
          <span class="value">${{ formatNumber(pool.capital_used) }}</span>
        </div>
        <div class="info-item">
          <span class="label">Disponível:</span>
          <span class="value available">${{ formatNumber(pool.capital_available) }}</span>
        </div>
      </div>
      
      <div class="pool-symbols">
        <span class="label">Pares:</span>
        <div class="symbols-list">
          <span 
            v-for="symbol in pool.symbols" 
            :key="symbol"
            class="symbol-tag"
          >
            {{ symbol }}
          </span>
        </div>
      </div>
      
      <div class="pool-risk">
        <div class="risk-item">
          <span class="label">Risco/Trade:</span>
          <span class="value">{{ pool.risk_per_trade_pct }}%</span>
        </div>
        <div class="risk-item">
          <span class="label">Max Posições:</span>
          <span class="value">{{ pool.max_positions }}</span>
        </div>
        <div v-if="pool.min_confluencia" class="risk-item">
          <span class="label">Min Confluência:</span>
          <span class="value">{{ pool.min_confluencia }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  pool: {
    type: Object,
    required: true
  }
})

defineEmits(['start', 'stop', 'edit', 'delete'])

const statusLabel = computed(() => {
  const labels = {
    'active': '🟢 Ativo',
    'inactive': '⚪ Inativo',
    'paused': '⏸️ Pausado',
    'stopped': '🔴 Parado'
  }
  return labels[props.pool.status] || props.pool.status
})

const formatNumber = (num) => {
  if (!num) return '0.00'
  return parseFloat(num).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}
</script>

<style scoped>
.pool-card {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.pool-card:hover {
  border-color: rgba(0, 255, 0, 0.5);
  background: rgba(0, 0, 0, 0.7);
}

.pool-card.active {
  border-color: rgba(0, 255, 0, 0.6);
}

.pool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 255, 0, 0.2);
}

.pool-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pool-title h4 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
}

.status-badge.active {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
}

.status-badge.inactive,
.status-badge.stopped {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
}

.status-badge.paused {
  background: rgba(255, 255, 0, 0.2);
  color: #ffff00;
}

.pool-actions {
  display: flex;
  gap: 6px;
}

.btn-action {
  background: transparent;
  border: 1px solid rgba(0, 255, 0, 0.3);
  color: #00ff00;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-action:hover {
  background: rgba(0, 255, 0, 0.2);
  border-color: #00ff00;
}

.btn-action.delete {
  border-color: rgba(255, 0, 0, 0.3);
  color: #ff0000;
}

.btn-action.delete:hover {
  background: rgba(255, 0, 0, 0.2);
  border-color: #ff0000;
}

.pool-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pool-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 11px;
  color: rgba(0, 255, 0, 0.6);
}

.info-item .value {
  font-size: 14px;
  color: #00ff00;
  font-weight: bold;
}

.info-item .value.available {
  color: #00ff88;
}

.pool-symbols {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pool-symbols .label {
  font-size: 11px;
  color: rgba(0, 255, 0, 0.6);
}

.symbols-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.symbol-tag {
  padding: 4px 8px;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 4px;
  font-size: 11px;
  color: #00ff00;
  font-weight: 500;
}

.pool-risk {
  display: flex;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 255, 0, 0.1);
}

.risk-item {
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.risk-item .label {
  color: rgba(0, 255, 0, 0.6);
}

.risk-item .value {
  color: #00ff00;
  font-weight: 500;
}
</style>



<template>
  <div class="position-monitor">
    <div class="monitor-header">
      <h3>📊 POSIÇÕES ABERTAS</h3>
      <span class="position-count">{{ positions.length }}</span>
    </div>
    
    <div v-if="positions.length === 0" class="empty-state">
      Nenhuma posição aberta
    </div>
    
    <div v-else class="positions-table">
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Side</th>
            <th>Quantity</th>
            <th>Entry</th>
            <th>Current</th>
            <th>P&L</th>
            <th>P&L %</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="position in positions" :key="position.id" :class="{ 'profit': position.unrealized_pnl > 0, 'loss': position.unrealized_pnl < 0 }">
            <td class="symbol">{{ position.symbol }}</td>
            <td>
              <span class="side-badge" :class="position.side.toLowerCase()">
                {{ position.side.toUpperCase() }}
              </span>
            </td>
            <td class="quantity">{{ formatNumber(position.quantity) }}</td>
            <td class="price">${{ formatNumber(position.entry_price) }}</td>
            <td class="price">${{ formatNumber(position.current_price || position.entry_price) }}</td>
            <td :class="position.unrealized_pnl >= 0 ? 'profit' : 'loss'">
              ${{ formatNumber(position.unrealized_pnl) }}
            </td>
            <td :class="position.unrealized_pnl_pct >= 0 ? 'profit' : 'loss'">
              {{ formatPercent(position.unrealized_pnl_pct) }}
            </td>
            <td>
              <button @click="$emit('close', position.id)" class="btn-close">
                Fechar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  positions: {
    type: Array,
    default: () => []
  }
})

defineEmits(['close'])

const formatNumber = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8
  })
}

const formatPercent = (value) => {
  if (!value) return '0.00%'
  const num = parseFloat(value)
  const sign = num >= 0 ? '+' : ''
  return `${sign}${num.toFixed(2)}%`
}
</script>

<style scoped>
.position-monitor {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.monitor-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
}

.position-count {
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid rgba(0, 255, 0, 0.3);
  padding: 4px 12px;
  border-radius: 12px;
  color: #00ff00;
  font-size: 12px;
  font-weight: bold;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(0, 255, 0, 0.4);
  font-style: italic;
}

.positions-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

thead {
  border-bottom: 1px solid rgba(0, 255, 0, 0.2);
}

th {
  text-align: left;
  padding: 8px;
  color: rgba(0, 255, 0, 0.7);
  font-weight: normal;
  text-transform: uppercase;
  font-size: 10px;
}

td {
  padding: 8px;
  color: #00ff00;
}

tr:hover {
  background: rgba(0, 255, 0, 0.05);
}

.symbol {
  font-weight: bold;
  color: #00ff00;
}

.side-badge {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
}

.side-badge.long {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
}

.side-badge.short {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
}

.profit {
  color: #00ff00;
}

.loss {
  color: #ff0000;
}

.btn-close {
  padding: 4px 8px;
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.3);
  color: #ff0000;
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
}

.btn-close:hover {
  background: rgba(255, 0, 0, 0.3);
}
</style>



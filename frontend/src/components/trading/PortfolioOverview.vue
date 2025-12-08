<template>
  <div class="portfolio-overview">
    <div class="portfolio-header">
      <h3>💰 PORTFÓLIO</h3>
    </div>
    
    <div v-if="!portfolio" class="empty-state">
      Carregando portfólio...
    </div>
    
    <div v-else class="portfolio-metrics">
      <div class="metric-card">
        <div class="metric-label">Total Balance</div>
        <div class="metric-value">${{ formatNumber(portfolio.total_balance) }}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">Available</div>
        <div class="metric-value">${{ formatNumber(portfolio.available_balance) }}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">Equity</div>
        <div class="metric-value">${{ formatNumber(portfolio.equity) }}</div>
      </div>
      
      <div class="metric-card" :class="portfolio.unrealized_pnl >= 0 ? 'profit' : 'loss'">
        <div class="metric-label">Unrealized P&L</div>
        <div class="metric-value">
          {{ portfolio.unrealized_pnl >= 0 ? '+' : '' }}${{ formatNumber(portfolio.unrealized_pnl) }}
        </div>
      </div>
      
      <div class="metric-card" :class="portfolio.realized_pnl >= 0 ? 'profit' : 'loss'">
        <div class="metric-label">Realized P&L</div>
        <div class="metric-value">
          {{ portfolio.realized_pnl >= 0 ? '+' : '' }}${{ formatNumber(portfolio.realized_pnl) }}
        </div>
      </div>
      
      <div class="metric-card" :class="portfolio.total_pnl >= 0 ? 'profit' : 'loss'">
        <div class="metric-label">Total P&L</div>
        <div class="metric-value large">
          {{ portfolio.total_pnl >= 0 ? '+' : '' }}${{ formatNumber(portfolio.total_pnl) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  portfolio: {
    type: Object,
    default: null
  }
})

const formatNumber = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}
</script>

<style scoped>
.portfolio-overview {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.portfolio-header h3 {
  margin: 0 0 16px 0;
  color: #00ff00;
  font-size: 16px;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: rgba(0, 255, 0, 0.4);
  font-style: italic;
}

.portfolio-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.metric-card {
  background: rgba(0, 255, 0, 0.05);
  border: 1px solid rgba(0, 255, 0, 0.2);
  border-radius: 6px;
  padding: 12px;
}

.metric-label {
  font-size: 10px;
  color: rgba(0, 255, 0, 0.6);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 16px;
  color: #00ff00;
  font-weight: bold;
}

.metric-value.large {
  font-size: 20px;
}

.metric-card.profit .metric-value {
  color: #00ff00;
}

.metric-card.loss .metric-value {
  color: #ff0000;
}
</style>



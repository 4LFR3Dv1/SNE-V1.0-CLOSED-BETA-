<template>
  <div class="performance-chart">
    <div class="chart-header">
      <h3>📈 EQUITY CURVE</h3>
      <select v-model="selectedPeriod" @change="$emit('period-change', selectedPeriod)" class="period-select">
        <option value="7">7 dias</option>
        <option value="30">30 dias</option>
        <option value="90">90 dias</option>
        <option value="365">1 ano</option>
      </select>
    </div>
    
    <div class="chart-container" ref="chartContainer">
      <canvas ref="chartCanvas"></canvas>
    </div>
    
    <div v-if="performance" class="performance-metrics">
      <div class="metric">
        <span class="metric-label">Win Rate:</span>
        <span class="metric-value">{{ (performance.win_rate * 100).toFixed(1) }}%</span>
      </div>
      <div class="metric">
        <span class="metric-label">Total Trades:</span>
        <span class="metric-value">{{ performance.total_trades }}</span>
      </div>
      <div class="metric">
        <span class="metric-label">Profit Factor:</span>
        <span class="metric-value">{{ performance.profit_factor?.toFixed(2) || '0.00' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  performance: {
    type: Object,
    default: null
  },
  equityData: {
    type: Array,
    default: () => []
  }
})

defineEmits(['period-change'])

const chartContainer = ref(null)
const chartCanvas = ref(null)
const selectedPeriod = ref(30)
let chart = null

onMounted(() => {
  // TODO: Implementar gráfico com Chart.js ou Lightweight Charts
  // Por enquanto, apenas placeholder
})

watch(() => props.equityData, () => {
  // Atualizar gráfico quando dados mudarem
  updateChart()
})

const updateChart = () => {
  // TODO: Implementar atualização do gráfico
}
</script>

<style scoped>
.performance-chart {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
}

.period-select {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 0, 0.3);
  color: #00ff00;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}

.chart-container {
  height: 200px;
  margin-bottom: 16px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 255, 0, 0.4);
  font-style: italic;
}

.performance-metrics {
  display: flex;
  gap: 16px;
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
</style>



<template>
  <div class="exposure-meter">
    <div class="meter-header">
      <h3>⚠️ EXPOSIÇÃO</h3>
    </div>
    
    <div class="meter-content">
      <div class="gauge-container">
        <div class="gauge" :style="gaugeStyle">
          <div class="gauge-fill" :style="fillStyle"></div>
          <div class="gauge-value">{{ exposurePercent }}%</div>
        </div>
      </div>
      
      <div class="exposure-details">
        <div class="detail-item">
          <span class="detail-label">Total:</span>
          <span class="detail-value">${{ formatNumber(totalExposure) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Usado:</span>
          <span class="detail-value">${{ formatNumber(usedExposure) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Livre:</span>
          <span class="detail-value">${{ formatNumber(freeExposure) }}</span>
        </div>
      </div>
      
      <div class="exposure-status" :class="exposureClass">
        <div class="status-dot"></div>
        <span>{{ exposureStatus }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  portfolio: {
    type: Object,
    default: null
  }
})

const totalExposure = computed(() => {
  if (!props.portfolio) return 0
  return props.portfolio.total_balance || 0
})

const usedExposure = computed(() => {
  if (!props.portfolio) return 0
  return props.portfolio.margin_used || 0
})

const freeExposure = computed(() => {
  return totalExposure.value - usedExposure.value
})

const exposurePercent = computed(() => {
  if (totalExposure.value === 0) return 0
  return Math.round((usedExposure.value / totalExposure.value) * 100)
})

const exposureClass = computed(() => {
  if (exposurePercent.value < 50) return 'safe'
  if (exposurePercent.value < 80) return 'warning'
  return 'critical'
})

const exposureStatus = computed(() => {
  if (exposurePercent.value < 50) return 'Seguro'
  if (exposurePercent.value < 80) return 'Atenção'
  return 'Crítico'
})

const gaugeStyle = computed(() => {
  return {
    '--exposure': `${exposurePercent.value}%`
  }
})

const fillStyle = computed(() => {
  let color = '#00ff00'
  if (exposurePercent.value >= 80) color = '#ff0000'
  else if (exposurePercent.value >= 50) color = '#ffff00'
  
  return {
    width: `${exposurePercent.value}%`,
    background: color
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
.exposure-meter {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.meter-header h3 {
  margin: 0 0 16px 0;
  color: #00ff00;
  font-size: 16px;
}

.gauge-container {
  margin-bottom: 16px;
}

.gauge {
  position: relative;
  width: 100%;
  height: 120px;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.gauge-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 100%;
  background: #00ff00;
  transition: all 0.3s;
  box-shadow: 0 0 10px currentColor;
}

.gauge-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 32px;
  font-weight: bold;
  color: #00ff00;
  z-index: 1;
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

.exposure-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.detail-label {
  color: rgba(0, 255, 0, 0.6);
}

.detail-value {
  color: #00ff00;
  font-weight: bold;
}

.exposure-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.exposure-status.safe {
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid rgba(0, 255, 0, 0.3);
  color: #00ff00;
}

.exposure-status.safe .status-dot {
  background: #00ff00;
  box-shadow: 0 0 6px #00ff00;
}

.exposure-status.warning {
  background: rgba(255, 255, 0, 0.1);
  border: 1px solid rgba(255, 255, 0, 0.3);
  color: #ffff00;
}

.exposure-status.warning .status-dot {
  background: #ffff00;
  box-shadow: 0 0 6px #ffff00;
}

.exposure-status.critical {
  background: rgba(255, 0, 0, 0.1);
  border: 1px solid rgba(255, 0, 0, 0.3);
  color: #ff0000;
  animation: pulse-red 2s infinite;
}

.exposure-status.critical .status-dot {
  background: #ff0000;
  box-shadow: 0 0 6px #ff0000;
}

@keyframes pulse-red {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>



<template>
  <div class="operational-levels">
    <div class="operational-levels-title-wrapper">
      <MapPinIcon :size="18" class="text-terminal-green" />
      <h3 class="operational-levels-title tech-heading">NÍVEIS OPERACIONAIS</h3>
    </div>
    
    <div class="operational-levels-container">
      <!-- Take Profits (de cima para baixo) -->
      <div 
        v-for="(tp, index) in takeProfits" 
        :key="`tp-${index}`"
        class="level-item level-tp"
        :style="getLevelStyle(tp, 'tp')"
      >
        <div class="level-info">
          <span class="level-label tech-label">TP{{ index + 1 }}</span>
          <span class="level-price tech-value tabular-nums">${{ formatPrice(tp) }}</span>
          <span v-if="entryPrice" class="level-distance tabular-nums">
            (+{{ calculateDistance(entryPrice, tp).toFixed(2) }}%)
          </span>
        </div>
        <div class="level-bar" :style="getBarStyle(tp, 'tp')"></div>
      </div>
      
      <!-- Entry (linha destacada) -->
      <div 
        v-if="entryPrice"
        class="level-item level-entry"
        :style="getLevelStyle(entryPrice, 'entry')"
      >
        <div class="level-info">
          <span class="level-label tech-label">ENTRY</span>
          <span class="level-price level-entry-price tech-value tabular-nums">${{ formatPrice(entryPrice) }}</span>
        </div>
        <div class="level-bar level-entry-bar" :style="getBarStyle(entryPrice, 'entry')"></div>
        <div class="level-divider"></div>
      </div>
      
      <!-- Stop Loss -->
      <div 
        v-if="stopLoss"
        class="level-item level-sl"
        :style="getLevelStyle(stopLoss, 'sl')"
      >
        <div class="level-info">
          <span class="level-label tech-label">STOP LOSS</span>
          <span class="level-price level-sl-price tech-value tabular-nums">${{ formatPrice(stopLoss) }}</span>
          <span v-if="entryPrice" class="level-distance tabular-nums">
            (-{{ calculateDistance(entryPrice, stopLoss).toFixed(2) }}%)
          </span>
        </div>
        <div class="level-bar level-sl-bar" :style="getBarStyle(stopLoss, 'sl')"></div>
      </div>
    </div>
    
    <!-- Risk:Reward Visual -->
    <div v-if="riskReward" class="risk-reward-section">
      <div class="risk-reward-label tech-label">RISK:REWARD</div>
      <div class="risk-reward-value tech-value tabular-nums">{{ riskReward }}</div>
      <div class="risk-reward-chart">
        <div class="risk-reward-bar risk-bar" :style="{ width: `${riskPercent}%` }">
          <span class="risk-reward-label-small">Risk</span>
        </div>
        <div class="risk-reward-bar reward-bar" :style="{ width: `${rewardPercent}%` }">
          <span class="risk-reward-label-small">Reward</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MapPin } from 'lucide-vue-next'

const MapPinIcon = MapPin

const props = defineProps({
  entryPrice: {
    type: Number,
    default: null
  },
  stopLoss: {
    type: Number,
    default: null
  },
  takeProfits: {
    type: Array,
    default: () => []
  },
  riskReward: {
    type: String,
    default: null
  }
})

const formatPrice = (price) => {
  if (!price || isNaN(price)) return '--'
  return parseFloat(price).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const calculateDistance = (from, to) => {
  if (!from || !to || from === 0) return 0
  return Math.abs((to - from) / from) * 100
}

const getPriceRange = () => {
  const prices = []
  if (props.entryPrice) prices.push(props.entryPrice)
  if (props.stopLoss) prices.push(props.stopLoss)
  props.takeProfits.forEach(tp => {
    if (tp) prices.push(tp)
  })
  
  if (prices.length === 0) return { min: 0, max: 100, range: 100 }
  
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min
  
  // Adicionar margem de 10%
  const margin = range * 0.1
  
  return {
    min: min - margin,
    max: max + margin,
    range: range + (margin * 2)
  }
}

const getLevelStyle = (price, type) => {
  const range = getPriceRange()
  const position = ((price - range.min) / range.range) * 100
  
  return {
    top: `${100 - position}%` // Invertido: maior preço = topo
  }
}

const getBarStyle = (price, type) => {
  const range = getPriceRange()
  const width = (Math.abs(price - (props.entryPrice || range.min)) / range.range) * 100
  
  return {
    width: `${Math.max(20, width)}%`
  }
}

const riskRewardRatio = computed(() => {
  if (!props.riskReward) return null
  const match = props.riskReward.match(/1:([\d.]+)/)
  return match ? parseFloat(match[1]) : null
})

const riskPercent = computed(() => {
  if (!riskRewardRatio.value) return 50
  const total = 1 + riskRewardRatio.value
  return (1 / total) * 100
})

const rewardPercent = computed(() => {
  if (!riskRewardRatio.value) return 50
  const total = 1 + riskRewardRatio.value
  return (riskRewardRatio.value / total) * 100
})
</script>

<style scoped>
.operational-levels {
  @apply bg-terminal-dark rounded-lg border border-terminal-green/30 p-4 mb-4;
}

.operational-levels-title-wrapper {
  @apply flex items-center gap-2 mb-4;
}

.operational-levels-title {
  @apply text-lg font-bold text-terminal-green;
  letter-spacing: 0.05em;
}

.operational-levels-container {
  @apply relative;
  min-height: 300px;
  position: relative;
}

.level-item {
  @apply absolute left-0 right-0;
  @apply transition-all duration-300;
}

.level-info {
  @apply flex items-center gap-2 mb-1;
  @apply text-sm;
}

.level-label {
  @apply font-bold text-terminal-green/70 font-mono;
  min-width: 80px;
  letter-spacing: 0.05em;
}

.level-price {
  @apply font-bold text-terminal-green font-mono;
}

.level-entry-price {
  @apply text-xl;
}

.level-sl-price {
  @apply text-red-400;
}

.level-distance {
  @apply text-xs text-terminal-green/60 ml-auto font-mono;
}

.level-bar {
  @apply h-1 rounded;
  @apply transition-all duration-300;
}

.level-tp .level-bar {
  @apply bg-terminal-green/60;
  border-top: 2px solid #00ff88;
}

.level-entry .level-bar {
  @apply bg-terminal-green;
  height: 2px;
  border-top: 2px solid #00ff88;
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.5);
}

.level-sl .level-bar {
  @apply bg-red-500/60;
  border-top: 2px solid #ef5350;
}

.level-divider {
  @apply absolute left-0 right-0;
  @apply border-t border-dashed border-terminal-green/30;
  top: 50%;
  transform: translateY(-50%);
}

.risk-reward-section {
  @apply mt-6 pt-4 border-t border-terminal-green/20;
}

.risk-reward-label {
  @apply text-xs text-terminal-green/70 mb-1 font-mono;
  letter-spacing: 0.1em;
}

.risk-reward-value {
  @apply text-xl font-bold text-terminal-green mb-3 font-mono;
}

.risk-reward-chart {
  @apply flex h-8 rounded overflow-hidden;
  @apply border border-terminal-green/30;
}

.risk-reward-bar {
  @apply flex items-center justify-center;
  @apply text-xs font-bold text-white;
  @apply transition-all duration-500;
}

.risk-bar {
  @apply bg-red-500/60;
}

.reward-bar {
  @apply bg-terminal-green/60;
}

.risk-reward-label-small {
  @apply text-xs font-bold;
}

/* Responsividade */
@media (max-width: 768px) {
  .operational-levels-container {
    min-height: 250px;
  }
  
  .level-info {
    @apply text-xs;
  }
  
  .level-price {
    @apply text-sm;
  }
  
  .level-entry-price {
    @apply text-lg;
  }
}
</style>


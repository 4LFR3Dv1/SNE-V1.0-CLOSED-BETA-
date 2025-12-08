<template>
  <div class="chart-info-panel">
    <div class="info-header">
      <span class="symbol">{{ symbol }} - {{ timeframe }}</span>
    </div>
    <div class="info-content">
      <!-- Sinal e Score -->
      <div class="signal-row" :class="signalClass">
        <component 
          :is="signalIconComponent" 
          :size="16"
          :stroke-width="2"
          class="signal-icon"
          :aria-label="signal"
        />
        <span class="signal-text tech-value">{{ signal }}</span>
        <span class="score tech-value tabular-nums">SCORE: {{ score.toFixed(1) }}/10</span>
      </div>
      
      <!-- Preço -->
      <div class="price-row">
        <DollarSignIcon :size="14" class="price-label" />
        <span class="price-value tech-value tabular-nums">${{ formatPrice(currentPrice) }}</span>
        <span v-if="priceChange !== null && !activeCandle" class="price-change tech-value tabular-nums" :class="priceChangeClass">
          {{ priceChange >= 0 ? '+' : '' }}{{ priceChange.toFixed(2) }}%
        </span>
      </div>
      
      <!-- Data Window: Dados do Candle Ativo (quando mouse está sobre o gráfico) -->
      <div v-if="activeCandle" class="candle-data-row">
        <span class="candle-data-item">
          <strong class="tech-label">O</strong>
          <span class="tech-value tabular-nums">${{ formatPrice(activeCandle.open) }}</span>
        </span>
        <span class="candle-data-item">
          <strong class="tech-label">H</strong>
          <span class="tech-value tabular-nums">${{ formatPrice(activeCandle.high) }}</span>
        </span>
        <span class="candle-data-item">
          <strong class="tech-label">L</strong>
          <span class="tech-value tabular-nums">${{ formatPrice(activeCandle.low) }}</span>
        </span>
        <span class="candle-data-item">
          <strong class="tech-label">C</strong>
          <span class="tech-value tabular-nums">${{ formatPrice(activeCandle.close) }}</span>
        </span>
        <span v-if="activeCandle.volume > 0" class="candle-data-item">
          <strong class="tech-label">VOL</strong>
          <span class="tech-value tabular-nums">{{ formatVolume(activeCandle.volume) }}</span>
        </span>
      </div>
      
      <!-- Indicadores -->
      <div class="indicators-row">
        <span v-if="rsi !== null && !activeCandle" class="indicator">
          <ZapIcon :size="12" class="inline mr-1" />
          <span class="tech-label">RSI</span>
          <strong class="tech-value tabular-nums ml-1">{{ rsi.toFixed(1) }}</strong>
        </span>
        <span v-if="volumeRatio !== null && !activeCandle" class="indicator">
          <BarChart3Icon :size="12" class="inline mr-1" />
          <span class="tech-label">VOL</span>
          <strong class="tech-value tabular-nums ml-1">{{ volumeRatio.toFixed(1) }}x</strong>
        </span>
        <span v-if="riskLevel && !activeCandle" class="indicator risk" :class="riskClass">
          <TargetIcon :size="12" class="inline mr-1" />
          <strong class="tech-value">{{ riskLevel }}</strong>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TrendingUp, TrendingDown, ArrowRight, DollarSign, Zap, BarChart3, Target } from 'lucide-vue-next'

const TrendingUpIcon = TrendingUp
const TrendingDownIcon = TrendingDown
const DollarSignIcon = DollarSign
const ZapIcon = Zap
const BarChart3Icon = BarChart3
const TargetIcon = Target

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  },
  timeframe: {
    type: String,
    default: '1h'
  },
  signal: {
    type: String,
    default: 'NEUTRAL'
  },
  score: {
    type: Number,
    default: 0
  },
  currentPrice: {
    type: Number,
    default: null
  },
  priceChange: {
    type: Number,
    default: null
  },
  rsi: {
    type: Number,
    default: null
  },
  volumeRatio: {
    type: Number,
    default: null
  },
  riskLevel: {
    type: String,
    default: null
  },
  activeCandle: {
    type: Object,
    default: null
  }
})

const signalClass = computed(() => {
  if (props.signal === 'BUY') return 'signal-buy'
  if (props.signal === 'SELL') return 'signal-sell'
  return 'signal-neutral'
})

// signalIcon removido - agora usamos signalIconComponent com ícones SVG

const priceChangeClass = computed(() => {
  if (props.priceChange === null) return ''
  return props.priceChange >= 0 ? 'positive' : 'negative'
})

const riskClass = computed(() => {
  if (!props.riskLevel) return ''
  if (props.riskLevel.includes('BAIXO')) return 'risk-low'
  if (props.riskLevel.includes('MÉDIO')) return 'risk-medium'
  if (props.riskLevel.includes('ALTO')) return 'risk-high'
  return ''
})

const formatPrice = (price) => {
  if (!price || isNaN(price)) return '--'
  return parseFloat(price).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatVolume = (volume) => {
  if (!volume || isNaN(volume)) return '--'
  if (volume >= 1000000) {
    return (volume / 1000000).toFixed(2) + 'M'
  } else if (volume >= 1000) {
    return (volume / 1000).toFixed(2) + 'K'
  }
  return volume.toFixed(2)
}
</script>

<style scoped>
.chart-info-panel {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid #00ff88;
  border-radius: 6px;
  padding: 8px 12px;
  z-index: 100;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
  backdrop-filter: blur(4px);
  pointer-events: none; /* Não bloquear eventos do gráfico - apenas exibir informações */
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.info-header {
  border-right: 1px solid #00ff88;
  padding-right: 8px;
  margin-right: 8px;
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.symbol {
  font-size: 11px;
  font-weight: bold;
  color: #00ff88;
  text-transform: uppercase;
  white-space: nowrap;
}

.info-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.signal-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  border-bottom: none;
  border-right: 1px solid rgba(0, 255, 136, 0.2);
  padding-right: 8px;
  margin-right: 8px;
}

.signal-buy {
  color: #00ff88;
}

.signal-sell {
  color: #ff4444;
}

.signal-neutral {
  color: #00ff88;
  opacity: 0.7;
}

.signal-icon {
  @apply text-terminal-green;
}

.signal-text {
  font-weight: bold;
  font-size: 13px;
  flex: 1;
}

.score {
  font-size: 11px;
  color: #00ff88;
  opacity: 0.8;
}

.price-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  border-right: 1px solid rgba(0, 255, 136, 0.2);
  padding-right: 8px;
  margin-right: 8px;
}

.price-label {
  font-size: 14px;
}

.price-value {
  font-weight: bold;
  color: #00ff88;
  flex: 1;
}

.price-change {
  font-size: 11px;
  font-weight: bold;
}

.price-change.positive {
  color: #00ff88;
}

.price-change.negative {
  color: #ff4444;
}

.indicators-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  font-size: 10px;
  color: #00ff88;
  opacity: 0.9;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.indicator strong {
  color: #00ff88;
  font-weight: bold;
}

.risk.risk-low {
  color: #00ff88;
}

.risk.risk-medium {
  color: #ffaa00;
}

.risk.risk-high {
  color: #ff4444;
}

/* Data Window: Dados do Candle Ativo */
.candle-data-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  color: #00ff88;
  border-right: 1px solid rgba(0, 255, 136, 0.2);
  padding-right: 8px;
  margin-right: 8px;
}

.candle-data-item {
  display: flex;
  align-items: center;
  gap: 2px;
  white-space: nowrap;
}

.candle-data-item strong {
  color: #00ff88;
  font-weight: bold;
  opacity: 0.8;
}
</style>


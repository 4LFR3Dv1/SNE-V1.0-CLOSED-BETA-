<template>
  <div class="signal-hero">
    <div class="signal-hero-content">
      <!-- Badge de Tipo de Operação -->
      <div class="signal-type-badge tech-label">
        {{ signalType }}
      </div>
      
      <!-- Botão Principal de Ação -->
      <button 
        class="signal-action-button"
        :class="{
          'signal-buy': isBuy,
          'signal-sell': isSell,
          'signal-neutral': !isBuy && !isSell
        }"
        @click="handleActionClick"
      >
        <div class="signal-action-icon-wrapper">
          <TrendingUpIcon 
            v-if="isBuy"
            :size="48"
            :stroke-width="2"
            class="signal-icon"
            aria-label="Sinal de compra"
          />
          <TrendingDownIcon 
            v-else-if="isSell"
            :size="48"
            :stroke-width="2"
            class="signal-icon"
            aria-label="Sinal de venda"
          />
          <ArrowRight 
            v-else
            :size="48"
            :stroke-width="2"
            class="signal-icon"
            aria-label="Aguardar sinal"
          />
        </div>
        <div class="signal-action-text tech-heading">
          {{ signalText }}
        </div>
      </button>
      
      <!-- Score com Progress Bar -->
      <div class="signal-score-section">
        <div class="signal-score-header">
          <span class="signal-score-label tech-label">SCORE</span>
          <div class="signal-score-value-wrapper">
            <span class="signal-score-value tech-value tabular-nums">{{ score.toFixed(1) }}</span>
            <span class="signal-score-max">/10</span>
          </div>
        </div>
        <div class="signal-score-bar">
          <div 
            class="signal-score-fill"
            :class="{
              'score-excellent': score >= 8,
              'score-good': score >= 6 && score < 8,
              'score-medium': score >= 4 && score < 6,
              'score-low': score < 4
            }"
            :style="{ width: `${(score / 10) * 100}%` }"
          ></div>
        </div>
      </div>
      
      <!-- Recomendação -->
      <div v-if="recommendation" class="signal-recommendation">
        {{ recommendation }}
      </div>
      
      <!-- Preço de Entrada -->
      <div v-if="entryPrice" class="signal-entry">
        <div class="signal-entry-row">
          <DollarSignIcon :size="14" class="text-terminal-green/70" />
          <span class="signal-entry-label tech-label">ENTRY</span>
          <span class="signal-entry-price tech-value tabular-nums">${{ formatPrice(entryPrice) }}</span>
        </div>
      </div>
      
      <!-- Risco -->
      <div v-if="riskLevel" class="signal-risk">
        <div class="signal-risk-row">
          <ShieldIcon :size="14" class="text-terminal-green/70" />
          <span class="signal-risk-label tech-label">RISK</span>
          <span 
            class="signal-risk-badge"
            :class="{
              'risk-low': riskLevel.includes('BAIXO'),
              'risk-medium': riskLevel.includes('MÉDIO'),
              'risk-high': riskLevel.includes('ALTO')
            }"
          >
            {{ getRiskLevelOnly(riskLevel) }}
          </span>
        </div>
        <span v-if="riskMessage" class="signal-risk-message">{{ riskMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TrendingUp, TrendingDown, ArrowRight, DollarSign, Shield } from 'lucide-vue-next'

const TrendingUpIcon = TrendingUp
const TrendingDownIcon = TrendingDown
const DollarSignIcon = DollarSign
const ShieldIcon = Shield

const props = defineProps({
  signal: {
    type: String,
    default: 'NEUTRO'
  },
  score: {
    type: Number,
    default: 0
  },
  recommendation: {
    type: String,
    default: null
  },
  entryPrice: {
    type: Number,
    default: null
  },
  riskLevel: {
    type: String,
    default: null
  },
  riskMessage: {
    type: String,
    default: null
  },
  signalType: {
    type: String,
    default: 'ESPECULATIVO'
  },
  timeframe: {
    type: String,
    default: '1h'
  }
})

const emit = defineEmits(['action-click'])

const isBuy = computed(() => {
  const signal = props.signal?.toUpperCase()
  return signal === 'BUY' || signal === 'COMPRA' || signal === 'LONG'
})

const isSell = computed(() => {
  const signal = props.signal?.toUpperCase()
  return signal === 'SELL' || signal === 'VENDA' || signal === 'SHORT'
})

const signalText = computed(() => {
  if (isBuy.value) return 'COMPRAR'
  if (isSell.value) return 'VENDER'
  return 'AGUARDAR'
})

const formatPrice = (price) => {
  if (!price || isNaN(price)) return '--'
  return parseFloat(price).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const getRiskLevelOnly = (riskLevel) => {
  if (!riskLevel) return ''
  // Extrair apenas o nível (BAIXO, MÉDIO, ALTO) removendo a mensagem adicional
  if (riskLevel.includes('BAIXO')) return 'BAIXO'
  if (riskLevel.includes('MÉDIO')) return 'MÉDIO'
  if (riskLevel.includes('ALTO')) return 'ALTO'
  return riskLevel.split(' - ')[0] // Pegar apenas a primeira parte antes do hífen
}

const handleActionClick = () => {
  emit('action-click', {
    signal: props.signal,
    entryPrice: props.entryPrice,
    score: props.score
  })
}
</script>

<style scoped>
.signal-hero {
  @apply w-full mb-6;
}

.signal-hero-content {
  @apply bg-terminal-dark rounded-lg border-2 p-6 text-center;
  border-color: rgba(0, 255, 136, 0.3);
  box-shadow: 0 4px 20px rgba(0, 255, 136, 0.1);
}

.signal-type-badge {
  @apply inline-block px-3 py-1 mb-4 rounded-full text-xs font-bold;
  @apply bg-terminal-green/20 text-terminal-green border border-terminal-green/50;
}

.signal-action-button {
  @apply w-full py-6 px-8 rounded-lg font-bold text-2xl mb-4;
  @apply transition-all duration-300 transform;
  @apply hover:scale-105 active:scale-95;
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.signal-action-button.signal-buy {
  @apply bg-gradient-to-br from-green-600 to-green-800 text-white;
  @apply hover:from-green-500 hover:to-green-700;
  @apply focus:ring-green-500;
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.4);
}

.signal-action-button.signal-sell {
  @apply bg-gradient-to-br from-red-600 to-red-800 text-white;
  @apply hover:from-red-500 hover:to-red-700;
  @apply focus:ring-red-500;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
}

.signal-action-button.signal-neutral {
  @apply bg-terminal-gray text-terminal-green border-2 border-terminal-green/50;
  @apply hover:bg-terminal-gray/80;
  @apply focus:ring-terminal-green;
}

.signal-action-icon-wrapper {
  @apply flex items-center justify-center;
  width: 64px;
  height: 64px;
}

.signal-icon {
  @apply text-terminal-green;
}

.signal-action-text {
  @apply text-3xl font-mono;
  letter-spacing: 0.1em;
}

.signal-score-section {
  @apply mb-4;
}

.signal-score-header {
  @apply flex justify-between items-baseline mb-2;
}

.signal-score-label {
  @apply text-xs text-terminal-green/70;
  letter-spacing: 0.1em;
}

.signal-score-value-wrapper {
  @apply flex items-baseline gap-1;
}

.signal-score-value {
  @apply text-2xl font-bold text-terminal-green;
}

.signal-score-max {
  @apply text-sm text-terminal-green/50;
}

.signal-score-bar {
  @apply w-full h-3 bg-terminal-gray rounded-full overflow-hidden;
  border: 1px solid rgba(0, 255, 136, 0.2);
}

.signal-score-fill {
  @apply h-full transition-all duration-500 ease-out;
}

.signal-score-fill.score-excellent {
  @apply bg-gradient-to-r from-green-500 to-green-600;
}

.signal-score-fill.score-good {
  @apply bg-gradient-to-r from-terminal-green to-green-500;
}

.signal-score-fill.score-medium {
  @apply bg-gradient-to-r from-yellow-500 to-yellow-600;
}

.signal-score-fill.score-low {
  @apply bg-gradient-to-r from-red-500 to-red-600;
}

.signal-recommendation {
  @apply text-sm text-terminal-green/80 mb-3 px-4 py-2;
  @apply bg-terminal-dark/50 rounded border border-terminal-green/20;
}

.signal-entry {
  @apply mb-3;
}

.signal-entry-row {
  @apply flex items-center gap-2 justify-center;
}

.signal-entry-label {
  @apply text-xs text-terminal-green/70;
  letter-spacing: 0.1em;
}

.signal-entry-price {
  @apply text-xl font-bold text-terminal-green;
}

.signal-risk {
  @apply flex flex-col items-center gap-2;
}

.signal-risk-row {
  @apply flex items-center gap-2;
}

.signal-risk-label {
  @apply text-xs text-terminal-green/70;
  letter-spacing: 0.1em;
}

.signal-risk-badge {
  @apply px-3 py-1 rounded-full text-xs font-bold;
}

.signal-risk-badge.risk-low {
  @apply bg-green-500/20 text-green-400 border border-green-500/50;
}

.signal-risk-badge.risk-medium {
  @apply bg-yellow-500/20 text-yellow-400 border border-yellow-500/50;
}

.signal-risk-badge.risk-high {
  @apply bg-red-500/20 text-red-400 border border-red-500/50;
}

.signal-risk-message {
  @apply text-xs text-terminal-green/60;
}

/* Responsividade */
@media (max-width: 768px) {
  .signal-action-button {
    @apply py-4 px-6 text-xl;
    min-height: 100px;
  }
  
  .signal-action-icon-wrapper {
    width: 48px;
    height: 48px;
  }
  
  .signal-action-text {
    @apply text-2xl;
  }
}
</style>


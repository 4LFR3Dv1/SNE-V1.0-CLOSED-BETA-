<template>
  <div class="mtf-timeline">
    <div class="mtf-header">
      <div class="mtf-title-wrapper">
        <BarChart3Icon :size="20" class="text-terminal-green" />
        <h3 class="mtf-title tech-heading">MULTI-TIMEFRAME</h3>
      </div>
      <div v-if="summary" class="mtf-summary-alert" :class="getSummaryClass()">
        <AlertTriangleIcon 
          v-if="summary.includes('⚠️')"
          :size="14"
          class="inline mr-1"
        />
        <CheckCircle2Icon 
          v-else-if="summary.includes('✅')"
          :size="14"
          class="inline mr-1"
        />
        {{ summary.replace('⚠️', '').replace('✅', '').trim() }}
      </div>
    </div>
    
    <div v-if="confluence" class="mtf-confluence">
      <div class="mtf-confluence-item">
        <span class="mtf-confluence-label tech-label">CONFLUÊNCIA MTF</span>
        <span class="mtf-confluence-value tech-value" :class="getConfluenceClass(confluence.direcao)">
          {{ confluence.direcao }}
        </span>
      </div>
      <div class="mtf-confluence-item">
        <span class="mtf-confluence-label tech-label">SCORE</span>
        <span class="mtf-confluence-value tech-value tabular-nums">{{ confluence.score }}/10</span>
      </div>
      <div class="mtf-confluence-item">
        <span class="mtf-confluence-label tech-label">CONFIRMAÇÕES</span>
        <span class="mtf-confluence-value tech-value tabular-nums">{{ confluence.confirmacoes }}/{{ confluence.total_tfs }}</span>
      </div>
    </div>
    
    <div class="mtf-timeline-container">
      <div 
        v-for="(tf, key) in timeframes" 
        :key="key"
        class="mtf-item"
        :class="{
          'mtf-bullish': tf.tendencia === 'ALTA',
          'mtf-bearish': tf.tendencia === 'BAIXA',
          'mtf-neutral': tf.tendencia !== 'ALTA' && tf.tendencia !== 'BAIXA'
        }"
      >
        <div class="mtf-item-header">
          <div class="mtf-timeframe tech-label">{{ key }}</div>
          <div class="mtf-direction-icon">
            <ArrowUpRightIcon 
              v-if="tf.tendencia === 'ALTA'"
              :size="18"
              :stroke-width="2"
              class="text-terminal-green"
              aria-label="Tendência alta"
            />
            <ArrowDownRightIcon 
              v-else-if="tf.tendencia === 'BAIXA'"
              :size="18"
              :stroke-width="2"
              class="text-red-400"
              aria-label="Tendência baixa"
            />
            <ArrowRight 
              v-else
              :size="18"
              :stroke-width="2"
              class="text-yellow-400"
              aria-label="Tendência neutra"
            />
          </div>
        </div>
        
        <div class="mtf-tendencia tech-value" :class="getTendenciaClass(tf.tendencia)">
          {{ tf.tendencia }}
        </div>
        
        <div class="mtf-forca">
          <div class="mtf-forca-label tech-label">FORÇA</div>
          <div class="mtf-forca-value tech-value tabular-nums">{{ tf.forca?.toFixed(1) || '0' }}</div>
        </div>
        
        <div class="mtf-progress">
          <div 
            class="mtf-progress-bar"
            :class="getProgressClass(tf.forca)"
            :style="{ width: `${Math.min((tf.forca || 0) / 10 * 100, 100)}%` }"
          ></div>
        </div>
        
        <div class="mtf-status">{{ tf.status }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  BarChart3, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowUpRight, 
  ArrowDownRight, 
  ArrowRight 
} from 'lucide-vue-next'

const BarChart3Icon = BarChart3
const AlertTriangleIcon = AlertTriangle
const CheckCircle2Icon = CheckCircle2
const ArrowUpRightIcon = ArrowUpRight
const ArrowDownRightIcon = ArrowDownRight

const props = defineProps({
  timeframes: {
    type: Object,
    default: () => ({})
  },
  summary: {
    type: String,
    default: null
  },
  confluence: {
    type: Object,
    default: null
  }
})

// Função removida - agora usamos componentes de ícone diretamente no template

const getTendenciaClass = (tendencia) => {
  if (tendencia === 'ALTA') return 'tendencia-alta'
  if (tendencia === 'BAIXA') return 'tendencia-baixa'
  return 'tendencia-neutral'
}

const getConfluenceClass = (direcao) => {
  if (direcao === 'ALTA') return 'confluence-alta'
  if (direcao === 'BAIXA') return 'confluence-baixa'
  return 'confluence-neutral'
}

const getSummaryClass = () => {
  if (!props.summary) return ''
  if (props.summary.includes('⚠️')) return 'summary-warning'
  if (props.summary.includes('✅')) return 'summary-success'
  return 'summary-info'
}

const getProgressClass = (forca) => {
  if (!forca) return 'progress-neutral'
  if (forca >= 8) return 'progress-excellent'
  if (forca >= 6) return 'progress-good'
  if (forca >= 4) return 'progress-medium'
  return 'progress-low'
}
</script>

<style scoped>
.mtf-timeline {
  @apply bg-terminal-dark rounded-lg border border-terminal-green/30 p-4 mb-4;
}

.mtf-header {
  @apply mb-4;
}

.mtf-title-wrapper {
  @apply flex items-center gap-2 mb-2;
}

.mtf-title {
  @apply text-lg font-bold text-terminal-green;
  letter-spacing: 0.05em;
}

.mtf-summary-alert {
  @apply text-sm px-3 py-2 rounded border;
}

.mtf-summary-alert.summary-warning {
  @apply bg-yellow-500/20 text-yellow-400 border-yellow-500/50;
}

.mtf-summary-alert.summary-success {
  @apply bg-terminal-green/20 text-terminal-green border-terminal-green/50;
}

.mtf-summary-alert.summary-info {
  @apply bg-terminal-green/10 text-terminal-green/80 border-terminal-green/30;
}

.mtf-confluence {
  @apply flex flex-wrap gap-4 mb-4 p-3 bg-terminal-dark/50 rounded border border-terminal-green/20;
}

.mtf-confluence-item {
  @apply flex items-center gap-2;
}

.mtf-confluence-label {
  @apply text-sm text-terminal-green/70;
}

.mtf-confluence-value {
  @apply text-sm font-bold;
}

.mtf-confluence-value.confluence-alta {
  @apply text-terminal-green;
}

.mtf-confluence-value.confluence-baixa {
  @apply text-red-400;
}

.mtf-confluence-value.confluence-neutral {
  @apply text-yellow-400;
}

.mtf-timeline-container {
  @apply grid grid-cols-2 md:grid-cols-5 gap-3;
}

.mtf-item {
  @apply bg-terminal-dark/50 rounded border p-3;
  @apply transition-all duration-300;
  @apply hover:shadow-lg;
  @apply hover:scale-105;
}

.mtf-item.mtf-bullish {
  @apply border-terminal-green/50;
  @apply hover:border-terminal-green;
  @apply hover:shadow-terminal-green/20;
}

.mtf-item.mtf-bearish {
  @apply border-red-500/50;
  @apply hover:border-red-500;
  @apply hover:shadow-red-500/20;
}

.mtf-item.mtf-neutral {
  @apply border-terminal-green/20;
}

.mtf-item-header {
  @apply flex justify-between items-center mb-2;
}

.mtf-timeframe {
  @apply font-bold text-terminal-green font-mono;
  letter-spacing: 0.1em;
}

.mtf-direction-icon {
  @apply flex items-center justify-center;
}

.mtf-tendencia {
  @apply text-sm font-bold mb-2;
}

.mtf-tendencia.tendencia-alta {
  @apply text-terminal-green;
}

.mtf-tendencia.tendencia-baixa {
  @apply text-red-400;
}

.mtf-tendencia.tendencia-neutral {
  @apply text-yellow-400;
}

.mtf-forca {
  @apply flex justify-between items-center mb-2 text-xs;
}

.mtf-forca-label {
  @apply text-terminal-green/70 font-mono;
  letter-spacing: 0.05em;
}

.mtf-forca-value {
  @apply font-bold text-terminal-green font-mono;
}

.mtf-progress {
  @apply w-full h-2 bg-terminal-gray rounded-full overflow-hidden mb-2;
  @apply border border-terminal-green/20;
}

.mtf-progress-bar {
  @apply h-full transition-all duration-500 ease-out;
}

.mtf-progress-bar.progress-excellent {
  @apply bg-gradient-to-r from-green-500 to-green-600;
}

.mtf-progress-bar.progress-good {
  @apply bg-gradient-to-r from-terminal-green to-green-500;
}

.mtf-progress-bar.progress-medium {
  @apply bg-gradient-to-r from-yellow-500 to-yellow-600;
}

.mtf-progress-bar.progress-low {
  @apply bg-gradient-to-r from-red-500 to-red-600;
}

.mtf-progress-bar.progress-neutral {
  @apply bg-terminal-gray;
}

.mtf-status {
  @apply text-xs text-terminal-green/60;
}

/* Responsividade */
@media (max-width: 768px) {
  .mtf-timeline-container {
    @apply grid-cols-2;
  }
  
  .mtf-item {
    @apply p-2;
  }
}
</style>


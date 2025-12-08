<template>
  <div class="confluence-grid">
    <div class="confluence-header">
      <div class="confluence-title-wrapper">
        <TargetIcon :size="20" class="text-terminal-green" />
        <h3 class="confluence-title tech-heading">CONFLUÊNCIA</h3>
      </div>
      <div class="confluence-score-wrapper">
        <span class="confluence-score tech-value tabular-nums">{{ score.toFixed(1) }}</span>
        <span class="confluence-score-max">/10</span>
      </div>
    </div>
    
    <div v-if="interpretation" class="confluence-interpretation">
      {{ interpretation }}
    </div>
    
    <div class="confluence-cards">
      <div 
        v-for="validation in validations" 
        :key="validation.camada"
        class="confluence-card"
      >
        <div class="confluence-card-header">
          <span class="confluence-card-label">{{ validation.camada }}</span>
          <span 
            class="confluence-card-status"
            :class="{
              'status-positive': validation.contribuicao > 0,
              'status-neutral': validation.contribuicao === 0,
              'status-negative': validation.contribuicao < 0
            }"
          >
            <CheckCircle2Icon 
              v-if="validation.status === '✅' || validation.contribuicao > 0"
              :size="18"
              :stroke-width="2"
              class="status-icon"
              aria-label="Validação positiva"
            />
            <AlertTriangleIcon 
              v-else-if="validation.status === '⚠️' || validation.contribuicao === 0"
              :size="18"
              :stroke-width="2"
              class="status-icon"
              aria-label="Atenção"
            />
            <XCircleIcon 
              v-else-if="validation.status === '❌' || validation.contribuicao < 0"
              :size="18"
              :stroke-width="2"
              class="status-icon"
              aria-label="Validação negativa"
            />
            <span v-else class="status-text">{{ validation.status }}</span>
          </span>
        </div>
        
        <div class="confluence-card-contribution">
          <span 
            class="contribution-value tech-value tabular-nums"
            :class="{
              'contribution-positive': validation.contribuicao > 0,
              'contribution-neutral': validation.contribuicao === 0,
              'contribution-negative': validation.contribuicao < 0
            }"
          >
            {{ validation.contribuicao > 0 ? '+' : '' }}{{ validation.contribuicao.toFixed(1) }}
          </span>
        </div>
        
        <div class="confluence-card-progress">
          <div 
            class="confluence-progress-bar"
            :class="getProgressClass(validation.contribuicao)"
            :style="{ width: `${getProgressWidth(validation.contribuicao)}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Target, CheckCircle2, AlertTriangle, XCircle } from 'lucide-vue-next'

const TargetIcon = Target
const CheckCircle2Icon = CheckCircle2
const AlertTriangleIcon = AlertTriangle
const XCircleIcon = XCircle

const props = defineProps({
  score: {
    type: Number,
    default: 0
  },
  interpretation: {
    type: String,
    default: null
  },
  validations: {
    type: Array,
    default: () => []
  }
})

const getProgressClass = (contribution) => {
  if (contribution >= 2) return 'progress-excellent'
  if (contribution >= 1) return 'progress-good'
  if (contribution >= 0.5) return 'progress-medium'
  if (contribution > 0) return 'progress-low'
  return 'progress-neutral'
}

const getProgressWidth = (contribution) => {
  // Normalizar contribuição para 0-100% (assumindo max de 3.0)
  const max = 3.0
  const normalized = Math.min(Math.max((contribution / max) * 100, 0), 100)
  return normalized
}
</script>

<style scoped>
.confluence-grid {
  @apply bg-terminal-dark rounded-lg border border-terminal-green/30 p-4 mb-4;
}

.confluence-header {
  @apply flex justify-between items-center mb-3;
}

.confluence-title-wrapper {
  @apply flex items-center gap-2;
}

.confluence-title {
  @apply text-lg font-bold text-terminal-green;
  letter-spacing: 0.05em;
}

.confluence-score-wrapper {
  @apply flex items-baseline gap-1;
}

.confluence-score {
  @apply text-2xl font-bold text-terminal-green;
}

.confluence-score-max {
  @apply text-sm text-terminal-green/50;
}

.confluence-interpretation {
  @apply text-sm text-terminal-green/80 mb-4 px-3 py-2;
  @apply bg-terminal-dark/50 rounded border border-terminal-green/20;
}

.confluence-cards {
  @apply grid grid-cols-2 md:grid-cols-4 gap-3;
}

.confluence-card {
  @apply bg-terminal-dark/50 rounded border border-terminal-green/20 p-3;
  @apply transition-all duration-300;
  @apply hover:border-terminal-green/50;
  @apply hover:shadow-lg;
  @apply hover:shadow-terminal-green/10;
}

.confluence-card-header {
  @apply flex justify-between items-center mb-2;
}

.confluence-card-label {
  @apply text-xs text-terminal-green/70 font-medium;
}

.confluence-card-status {
  @apply flex items-center;
}

.status-icon {
  @apply transition-colors;
}

.status-text {
  @apply text-sm;
}

.status-positive .status-icon {
  @apply text-terminal-green;
}

.status-neutral .status-icon {
  @apply text-yellow-500;
}

.status-negative .status-icon {
  @apply text-red-500;
}

.confluence-card-contribution {
  @apply mb-2;
}

.contribution-value {
  @apply text-lg font-bold font-mono;
}

.contribution-positive {
  @apply text-terminal-green;
}

.contribution-neutral {
  @apply text-yellow-500;
}

.contribution-negative {
  @apply text-red-500;
}

.confluence-card-progress {
  @apply w-full h-2 bg-terminal-gray rounded-full overflow-hidden;
  @apply border border-terminal-green/20;
}

.confluence-progress-bar {
  @apply h-full transition-all duration-500 ease-out;
}

.confluence-progress-bar.progress-excellent {
  @apply bg-gradient-to-r from-green-500 to-green-600;
}

.confluence-progress-bar.progress-good {
  @apply bg-gradient-to-r from-terminal-green to-green-500;
}

.confluence-progress-bar.progress-medium {
  @apply bg-gradient-to-r from-yellow-500 to-yellow-600;
}

.confluence-progress-bar.progress-low {
  @apply bg-gradient-to-r from-green-400 to-green-500;
}

.confluence-progress-bar.progress-neutral {
  @apply bg-terminal-gray;
}

/* Responsividade */
@media (max-width: 768px) {
  .confluence-cards {
    @apply grid-cols-2;
  }
  
  .confluence-card {
    @apply p-2;
  }
}
</style>


<template>
  <div class="level-lines-container">
    <!-- Tooltip Rico -->
    <Teleport to="body">
      <div
        v-if="tooltip.visible"
        class="rich-tooltip"
        :style="{
          left: tooltip.x + 'px',
          top: tooltip.y + 'px'
        }"
      >
        <div class="tooltip-header">
          <span class="tooltip-label">{{ tooltip.label }}</span>
          <span class="tooltip-timeframe" v-if="tooltip.timeframe">{{ tooltip.timeframe }}</span>
        </div>
        <div class="tooltip-content">
          <div class="tooltip-row">
            <span class="tooltip-label-small">Preço:</span>
            <span class="tooltip-value">${{ formatPrice(tooltip.price) }}</span>
          </div>
          <div class="tooltip-row" v-if="tooltip.distance !== null">
            <span class="tooltip-label-small">Distância:</span>
            <span class="tooltip-value" :class="tooltip.distanceClass">
              {{ tooltip.distance >= 0 ? '+' : '' }}{{ tooltip.distance.toFixed(2) }}%
            </span>
          </div>
          <div class="tooltip-justification-row" v-if="tooltip.justification">
            <span class="tooltip-label-small">Justificativa:</span>
            <div class="tooltip-justification">{{ tooltip.justification }}</div>
          </div>
          <div class="tooltip-row" v-if="tooltip.age">
            <span class="tooltip-label-small">Idade:</span>
            <span class="tooltip-age">{{ tooltip.age }}</span>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- Nota: As linhas S/R são renderizadas pela biblioteca lightweight-charts via createPriceLine() -->
    <!-- Este componente apenas gerencia os tooltips -->
  </div>
</template>

<script setup>
import { ref, inject, watch } from 'vue'
import { Teleport } from 'vue'

// ============================================================================
// PROPS
// ============================================================================
const props = defineProps({
  supports: {
    type: Array,
    default: () => []
  },
  resistances: {
    type: Array,
    default: () => []
  },
  currentPrice: {
    type: Number,
    default: null
  },
  timeframe: {
    type: String,
    default: '1h'
  }
})

// ============================================================================
// REFS
// ============================================================================
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  price: 0,
  timeframe: '',
  distance: null,
  distanceClass: '',
  justification: '',
  age: ''
})

// ============================================================================
// INJECT
// ============================================================================
const chartContext = inject('chartContext', null)

// ============================================================================
// FUNÇÕES UTILITÁRIAS
// ============================================================================

/**
 * Calcula distância percentual do preço atual
 */
const calculateDistance = (price) => {
  if (!props.currentPrice) return { distance: null, class: '' }
  const distance = ((price - props.currentPrice) / props.currentPrice) * 100
  const distanceClass = distance >= 0 ? 'distance-positive' : 'distance-negative'
  return { distance, class: distanceClass }
}

/**
 * Formata preço para exibição
 */
const formatPrice = (price) => {
  if (!price || isNaN(price)) return '--'
  return parseFloat(price).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

/**
 * Obtém justificativa baseada no tipo de nível
 */
const getJustification = (levelType, price, index = null) => {
  const justifications = {
    support: `Suporte identificado em ${index !== null ? `nível ${index + 1}` : 'múltiplos toques'} - Zona de liquidez`,
    resistance: `Resistência identificada em ${index !== null ? `nível ${index + 1}` : 'múltiplos toques'} - Zona de oferta`
  }
  return justifications[levelType] || 'Nível técnico identificado'
}

/**
 * Calcula idade estimada do nível
 */
const getLevelAge = (levelType, index = null) => {
  const timeframeMinutes = {
    '1m': 1,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '1h': 60,
    '4h': 240,
    '1d': 1440
  }
  
  const minutes = timeframeMinutes[props.timeframe] || 60
  const baseCandlesAgo = {
    support: 15,
    resistance: 15
  }
  
  let candlesAgo = baseCandlesAgo[levelType] || 10
  
  if (index !== null && index !== undefined) {
    if (levelType === 'support' || levelType === 'resistance') {
      candlesAgo = 15 + (index * 15) // S1: 15, S2: 30, S3: 45
    }
  }
  
  const ageMinutes = candlesAgo * minutes
  
  if (ageMinutes < 60) {
    return `${ageMinutes}min`
  } else if (ageMinutes < 1440) {
    return `${Math.floor(ageMinutes / 60)}h`
  } else {
    return `${Math.floor(ageMinutes / 1440)}d`
  }
}

/**
 * Calcula posição do tooltip evitando sair da tela
 */
const calculateTooltipPosition = (crosshairPos) => {
  const tooltipWidth = 280
  const tooltipHeight = 180
  const offsetX = 20
  const offsetY = 15
  
  let x = crosshairPos.x + offsetX
  let y = crosshairPos.y - tooltipHeight - offsetY
  
  // Ajustar horizontalmente
  if (x + tooltipWidth > window.innerWidth) {
    x = crosshairPos.x - tooltipWidth - offsetX
  }
  if (x < 0) {
    x = Math.min(offsetX, window.innerWidth - tooltipWidth - offsetX)
  }
  
  // Ajustar verticalmente
  if (y < 0) {
    y = crosshairPos.y + offsetY
  }
  if (y + tooltipHeight > window.innerHeight) {
    y = Math.max(offsetY, window.innerHeight - tooltipHeight - offsetY)
  }
  
  return { x, y }
}

// ============================================================================
// WATCHERS
// ============================================================================

/**
 * Observa mudanças no nível ativo para exibir tooltip
 */
watch(() => chartContext?.activeLevelTooltip?.value, (nivelAtivo) => {
  if (!chartContext) {
    tooltip.value.visible = false
    return
  }
  
  if (nivelAtivo && nivelAtivo.price && nivelAtivo.price > 0) {
    const { distance, class: distanceClass } = calculateDistance(nivelAtivo.price)
    const crosshairPos = chartContext.crosshairPosition?.value
    
    if (!crosshairPos) {
      tooltip.value.visible = false
      return
    }
    
    const { x, y } = calculateTooltipPosition(crosshairPos)
    
    tooltip.value = {
      visible: true,
      x,
      y,
      label: nivelAtivo.label || 'NÍVEL',
      price: parseFloat(nivelAtivo.price),
      timeframe: props.timeframe,
      distance,
      distanceClass,
      justification: getJustification(nivelAtivo.type, nivelAtivo.price, nivelAtivo.index),
      age: getLevelAge(nivelAtivo.type, nivelAtivo.index)
    }
  } else {
    tooltip.value.visible = false
  }
}, { immediate: false, flush: 'post' })
</script>

<style scoped>
/* Container: Não bloqueia eventos */
.level-lines-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none !important;
  z-index: 1000 !important;
  isolation: isolate;
}

/* Tooltip Rico */
.rich-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #00ff88;
  border-radius: 6px;
  padding: 10px 12px;
  min-width: 220px;
  max-width: 300px;
  z-index: 10000;
  pointer-events: none;
  font-family: 'Courier New', monospace;
  box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
  backdrop-filter: blur(4px);
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(0, 255, 136, 0.3);
}

.tooltip-label {
  font-size: 13px;
  font-weight: bold;
  color: #00ff88;
  text-transform: uppercase;
}

.tooltip-timeframe {
  font-size: 10px;
  color: #00ff88;
  opacity: 0.7;
  background: rgba(0, 255, 136, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.tooltip-label-small {
  color: #00ff88;
  opacity: 0.8;
  font-weight: normal;
}

.tooltip-value {
  color: #fff;
  font-weight: bold;
}

.tooltip-justification-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
  padding-top: 6px;
  border-top: 1px solid rgba(0, 255, 136, 0.2);
}

.tooltip-justification {
  color: #00ff88;
  opacity: 0.9;
  font-size: 10px;
  line-height: 1.4;
  font-style: italic;
  text-align: left;
}

.tooltip-age {
  color: #00ff88;
  opacity: 0.8;
  font-size: 10px;
}

.distance-positive {
  color: #4caf50;
}

.distance-negative {
  color: #ef5350;
}
</style>

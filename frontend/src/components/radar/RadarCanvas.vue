<template>
  <div class="radar-container" ref="containerRef">
    <canvas
      ref="canvasRef"
      class="radar-canvas"
      @mousemove="handleMouseMove"
      @mouseleave="handleMouseLeave"
      @click="handleClick"
    ></canvas>
    
    <!-- HUDs Táticos Flutuantes -->
    <div class="tactical-huds">
      <!-- HUD Top Left: Top Ativos -->
      <div class="tactical-hud hud-top-left">
        <div class="hud-header">
          <span class="hud-title tech-label">TOP ASSETS</span>
          <div class="hud-status-indicator"></div>
        </div>
        <div class="hud-content">
          <div 
            v-for="(asset, idx) in topAssets" 
            :key="asset.symbol"
            class="hud-item"
          >
            <div class="hud-item-rank tech-value">{{ idx + 1 }}</div>
            <div class="hud-item-info">
              <div class="hud-item-symbol tech-value">{{ asset.symbol.replace('USDT', '') }}</div>
              <div class="hud-item-score tech-value tabular-nums">{{ asset.score.toFixed(1) }}</div>
            </div>
            <div 
              class="hud-item-signal"
              :class="{
                'signal-buy': asset.signal === 'BUY',
                'signal-sell': asset.signal === 'SELL',
                'signal-neutral': asset.signal === 'NEUTRAL'
              }"
            >
              {{ asset.signal }}
            </div>
          </div>
        </div>
      </div>

      <!-- HUD Top Right: Estatísticas -->
      <div class="tactical-hud hud-top-right">
        <div class="hud-header">
          <span class="hud-title tech-label">MARKET STATS</span>
          <div class="hud-status-indicator"></div>
        </div>
        <div class="hud-content">
          <div class="hud-stat-row">
            <span class="hud-stat-label tech-label">TOTAL BLIPS</span>
            <span class="hud-stat-value tech-value tabular-nums">{{ opportunities.length }}</span>
          </div>
          <div class="hud-stat-row">
            <span class="hud-stat-label tech-label">AVG SCORE</span>
            <span class="hud-stat-value tech-value tabular-nums">{{ averageScore }}</span>
          </div>
          <div class="hud-stat-row">
            <span class="hud-stat-label tech-label">BUY SIGNALS</span>
            <span class="hud-stat-value tech-value tabular-nums text-terminal-green">{{ buyCount }}</span>
          </div>
          <div class="hud-stat-row">
            <span class="hud-stat-label tech-label">SELL SIGNALS</span>
            <span class="hud-stat-value tech-value tabular-nums text-red-500">{{ sellCount }}</span>
          </div>
        </div>
      </div>

      <!-- HUD Bottom Left: Regime de Mercado -->
      <div class="tactical-hud hud-bottom-left">
        <div class="hud-header">
          <span class="hud-title tech-label">MARKET REGIME</span>
          <div class="hud-status-indicator"></div>
        </div>
        <div class="hud-content">
          <div class="hud-regime">
            <div class="hud-regime-value tech-value">{{ marketRegime }}</div>
            <div class="hud-regime-desc tech-label">{{ marketRegimeDesc }}</div>
          </div>
          <div class="hud-volatility">
            <span class="hud-volatility-label tech-label">VOLATILITY</span>
            <span class="hud-volatility-value tech-value tabular-nums">{{ volatilityLevel }}</span>
          </div>
        </div>
      </div>

      <!-- HUD Bottom Right: BTC Reference -->
      <div class="tactical-hud hud-bottom-right">
        <div class="hud-header">
          <span class="hud-title tech-label">BTC REFERENCE</span>
          <div class="hud-status-indicator"></div>
        </div>
        <div class="hud-content">
          <div class="hud-btc-price tech-value tabular-nums">{{ btcPriceFormatted }}</div>
          <div 
            class="hud-btc-change"
            :class="btcChange >= 0 ? 'text-terminal-green' : 'text-red-500'"
          >
            <span class="tech-value tabular-nums">{{ btcChangeFormatted }}</span>
          </div>
          <div class="hud-btc-status tech-label">{{ btcStatus }}</div>
        </div>
      </div>
    </div>
    
    <!-- Tooltip flutuante -->
    <div
      v-if="hoveredBlip"
      class="radar-tooltip"
      :style="{
        left: tooltipPosition.x + 'px',
        top: tooltipPosition.y + 'px'
      }"
    >
      <div class="tooltip-header">
        <span class="tooltip-symbol tech-value">{{ hoveredBlip.symbol }}</span>
        <span 
          class="tooltip-signal tech-label"
          :class="{
            'signal-buy': hoveredBlip.signal === 'BUY',
            'signal-sell': hoveredBlip.signal === 'SELL',
            'signal-neutral': hoveredBlip.signal === 'NEUTRAL'
          }"
        >
          {{ hoveredBlip.signal }}
        </span>
      </div>
      <div class="tooltip-content">
        <div class="tooltip-row">
          <span class="tech-label">SCORE</span>
          <span class="tooltip-value tech-value tabular-nums">{{ hoveredBlip.score.toFixed(1) }}/10</span>
        </div>
        <div v-if="hoveredBlip.current_price" class="tooltip-row">
          <span class="tech-label">PREÇO</span>
          <span class="tooltip-value tech-value tabular-nums">${{ formatPrice(hoveredBlip.current_price) }}</span>
        </div>
        <div v-if="hoveredBlip.entry_price" class="tooltip-row">
          <span class="tech-label">ENTRY</span>
          <span class="tooltip-value tech-value tabular-nums">${{ formatPrice(hoveredBlip.entry_price) }}</span>
        </div>
        <div v-if="hoveredBlip.risk_reward" class="tooltip-row">
          <span class="tech-label">R:R</span>
          <span class="tooltip-value tech-value tabular-nums">1:{{ parseRR(hoveredBlip.risk_reward).toFixed(1) }}</span>
        </div>
      </div>
    </div>
    
    <!-- Legenda horizontal dentro do radar -->
    <div class="radar-legend-inline">
      <div class="legend-row">
        <!-- Sinais -->
        <div class="legend-group">
          <div class="legend-item-inline">
            <div class="legend-color" style="background: #00ff00;"></div>
            <span class="legend-text">BUY</span>
          </div>
          <div class="legend-item-inline">
            <div class="legend-color" style="background: #ff0000;"></div>
            <span class="legend-text">SELL</span>
          </div>
          <div class="legend-item-inline">
            <div class="legend-color" style="background: #ffff00;"></div>
            <span class="legend-text">NEUTRAL</span>
          </div>
        </div>
        
        <!-- Separador -->
        <div class="legend-separator"></div>
        
        <!-- Zonas -->
        <div class="legend-group">
          <div class="legend-item-inline">
            <div class="legend-ring ring-1"></div>
            <span class="legend-text">8-10</span>
          </div>
          <div class="legend-item-inline">
            <div class="legend-ring ring-2"></div>
            <span class="legend-text">6-8</span>
          </div>
          <div class="legend-item-inline">
            <div class="legend-ring ring-3"></div>
            <span class="legend-text">4-6</span>
          </div>
          <div class="legend-item-inline">
            <div class="legend-ring ring-4"></div>
            <span class="legend-text">0-4</span>
          </div>
        </div>
        
        <!-- Separador -->
        <div class="legend-separator"></div>
        
        <!-- Referências -->
        <div class="legend-group">
          <div class="legend-item-inline">
            <div class="legend-center"></div>
            <span class="legend-text">CENTER</span>
          </div>
          <div class="legend-item-inline">
            <div class="legend-sweep"></div>
            <span class="legend-text">SWEEP</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  opportunities: {
    type: Array,
    default: () => []
  },
  sweepAngle: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  },
  btcPrice: {
    type: [String, Number],
    default: null
  },
  btcChange: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['blip-click'])

const containerRef = ref(null)
const canvasRef = ref(null)
const hoveredBlip = ref(null)
const tooltipPosition = ref({ x: 0, y: 0 })
const blipPositions = ref([])
const canvasSize = ref(600) // Tamanho dinâmico
const loadingSweepAngle = ref(0) // Ângulo da varredura durante loading
const idleSweepAngle = ref(0) // Ângulo da varredura idle (sempre ativo)
let loadingAnimationId = null // ID da animação de loading
let idleAnimationId = null // ID da animação idle

// Configurações do radar (agora baseadas no tamanho dinâmico)
const centerX = computed(() => canvasSize.value / 2)
const centerY = computed(() => canvasSize.value / 2)
const maxRadius = computed(() => canvasSize.value / 2 - 40) // Margem para labels
const minRadius = computed(() => Math.max(20, canvasSize.value * 0.05)) // Raio mínimo proporcional

// Calcular tamanho do canvas baseado no container
const updateCanvasSize = () => {
  if (!containerRef.value) return
  
  const container = containerRef.value
  const containerWidth = container.clientWidth
  const containerHeight = container.clientHeight
  
  // Manter proporção quadrada, ocupar o máximo possível
  // Considerar padding mínimo de 8px
  const availableWidth = containerWidth - 16
  const availableHeight = containerHeight - 16
  
  const newSize = Math.min(availableWidth, availableHeight)
  
  // Limitar tamanho mínimo e máximo (mais compacto)
  const minSize = 300
  const maxSize = 500 // Reduzido de 1000 para 500 para ser mais compacto
  
  canvasSize.value = Math.max(minSize, Math.min(maxSize, newSize))
  
  if (canvasRef.value) {
    // Canvas precisa de width/height explícitos (não CSS)
    canvasRef.value.width = canvasSize.value
    canvasRef.value.height = canvasSize.value
    
    // Definir também no CSS para garantir que o tamanho visual seja igual ao interno
    canvasRef.value.style.width = canvasSize.value + 'px'
    canvasRef.value.style.height = canvasSize.value + 'px'
    
    // Redesenhar com novo tamanho
    nextTick(() => {
      calculatePositions(props.opportunities)
      drawRadar()
    })
  }
}

// Debounce para resize (otimização)
let resizeTimeout = null
const debouncedResize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout)
  }
  resizeTimeout = setTimeout(() => {
    updateCanvasSize()
  }, 150)
}

// Calcular posições sem sobreposição
const calculatePositions = (opportunities) => {
  if (!opportunities || opportunities.length === 0) {
    blipPositions.value = []
    return
  }

  // Ordenar por score (melhor primeiro)
  const sorted = [...opportunities]
    .sort((a, b) => (parseFloat(b.score) || 0) - (parseFloat(a.score) || 0))
    .slice(0, 20) // Limitar a 20 blips

  const positions = []
  const minDistance = 40 // Distância mínima entre blips (pixels)
  
  sorted.forEach((opp, index) => {
    const score = Math.max(0, Math.min(10, parseFloat(opp.score) || 0))
    
    // Calcular distância do centro baseado no score de forma CONTÍNUA
    // Score 10 = centro (minRadius)
    // Score 0 = exterior (maxRadius)
    // Usar função inversa: score alto = distância pequena
    const normalizedScore = score / 10 // 0.0 a 1.0
    const distanceFromCenter = minRadius.value + 
      ((maxRadius.value - minRadius.value) * (1 - normalizedScore))
    
    // Distribuir uniformemente no círculo
    // Usar índice global para distribuição circular uniforme
    const angleStep = 360 / sorted.length
    let angle = angleStep * index
    
    // Ajustar para evitar sobreposição
    let finalX, finalY
    let attempts = 0
    const maxAttempts = 200
    
    do {
      const rad = (angle * Math.PI) / 180
      finalX = centerX.value + distanceFromCenter * Math.cos(rad)
      finalY = centerY.value + distanceFromCenter * Math.sin(rad)
      
      // Verificar sobreposição com blips já posicionados
      const hasOverlap = positions.some(pos => {
        const dx = pos.x - finalX
        const dy = pos.y - finalY
        const distance = Math.sqrt(dx * dx + dy * dy)
        return distance < minDistance
      })
      
      if (!hasOverlap) {
        break
      }
      
      // Tentar próximo ângulo disponível
      angle += angleStep / 2 // Incrementar metade do passo
      attempts++
    } while (attempts < maxAttempts)
    
    // Se ainda houver sobreposição após tentativas, ajustar distância
    if (attempts >= maxAttempts) {
      // Aumentar ligeiramente a distância do centro (mas manter proporcional ao score)
      const adjustedDistance = distanceFromCenter + 10
      const rad = (angle * Math.PI) / 180
      finalX = centerX.value + adjustedDistance * Math.cos(rad)
      finalY = centerY.value + adjustedDistance * Math.sin(rad)
    }
    
    positions.push({
      opportunity: opp,
      x: finalX,
      y: finalY,
      angle: angle,
      distance: distanceFromCenter,
      size: calculateBlipSize(score, opp.signal)
    })
  })
  
  blipPositions.value = positions
}

// Calcular tamanho do blip baseado no score
const calculateBlipSize = (score, signal) => {
  const baseSize = 8
  const scoreMultiplier = 1 + (score / 10) * 0.5 // 1.0x a 1.5x
  return baseSize * scoreMultiplier
}

// Formatação
const formatPrice = (price) => {
  if (!price || isNaN(price)) return '--'
  const num = parseFloat(price)
  if (num >= 1000) {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  } else {
    return num.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }
}

const parseRR = (rr) => {
  if (!rr) return 0
  if (typeof rr === 'string') {
    const match = rr.match(/1:?([\d.]+)/)
    return match ? parseFloat(match[1]) : 0
  }
  return parseFloat(rr) || 0
}

// Computed para HUDs Táticos
const topAssets = computed(() => {
  return [...props.opportunities]
    .sort((a, b) => (parseFloat(b.score) || 0) - (parseFloat(a.score) || 0))
    .slice(0, 3)
    .map(opp => ({
      symbol: opp.symbol || 'N/A',
      score: parseFloat(opp.score) || 0,
      signal: opp.signal || 'NEUTRAL'
    }))
})

const averageScore = computed(() => {
  if (props.opportunities.length === 0) return '0.0'
  const sum = props.opportunities.reduce((acc, opp) => acc + (parseFloat(opp.score) || 0), 0)
  return (sum / props.opportunities.length).toFixed(1)
})

const buyCount = computed(() => {
  return props.opportunities.filter(opp => opp.signal === 'BUY').length
})

const sellCount = computed(() => {
  return props.opportunities.filter(opp => opp.signal === 'SELL').length
})

const marketRegime = computed(() => {
  const buyRatio = props.opportunities.length > 0 ? buyCount.value / props.opportunities.length : 0
  const avgScore = parseFloat(averageScore.value)
  
  if (buyRatio >= 0.7 && avgScore >= 7.0) return 'BULLISH'
  if (buyRatio <= 0.3 && avgScore <= 4.0) return 'BEARISH'
  if (avgScore >= 6.0 && buyRatio >= 0.5) return 'ACCUMULATION'
  if (avgScore <= 5.0 && buyRatio <= 0.5) return 'DISTRIBUTION'
  return 'NEUTRAL'
})

const marketRegimeDesc = computed(() => {
  const regimes = {
    'BULLISH': 'Tendência de alta dominante',
    'BEARISH': 'Tendência de baixa dominante',
    'ACCUMULATION': 'Acumulação de posições',
    'DISTRIBUTION': 'Distribuição de posições',
    'NEUTRAL': 'Mercado lateralizado'
  }
  return regimes[marketRegime.value] || 'Aguardando dados'
})

const volatilityLevel = computed(() => {
  const scores = props.opportunities.map(opp => parseFloat(opp.score) || 0)
  if (scores.length === 0) return 'N/A'
  
  const avg = parseFloat(averageScore.value)
  const variance = scores.reduce((acc, score) => acc + Math.pow(score - avg, 2), 0) / scores.length
  const stdDev = Math.sqrt(variance)
  
  if (stdDev >= 2.5) return 'HIGH'
  if (stdDev >= 1.5) return 'MEDIUM'
  return 'LOW'
})

const btcPriceFormatted = computed(() => {
  if (!props.btcPrice) return '--'
  const price = parseFloat(props.btcPrice)
  if (isNaN(price) || !isFinite(price)) return '--'
  return price >= 1000 
    ? price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : price.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

const btcChangeFormatted = computed(() => {
  if (props.btcChange === null || props.btcChange === undefined) return '--'
  const change = parseFloat(props.btcChange)
  if (isNaN(change) || !isFinite(change)) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${change.toFixed(2)}%`
})

const btcStatus = computed(() => {
  if (props.btcChange === null || props.btcChange === undefined) return 'NO DATA'
  const change = parseFloat(props.btcChange)
  if (isNaN(change) || !isFinite(change)) return 'NO DATA'
  if (change >= 2) return 'STRONG UP'
  if (change >= 0.5) return 'UP'
  if (change <= -2) return 'STRONG DOWN'
  if (change <= -0.5) return 'DOWN'
  return 'STABLE'
})

// Desenhar radar
const drawRadar = () => {
  const canvas = canvasRef.value
  if (!canvas || canvasSize.value === 0) return
  
  const ctx = canvas.getContext('2d')
  const size = canvasSize.value
  
  // Limpar canvas
  ctx.clearRect(0, 0, size, size)
  
  // Desenhar background com profundidade
  drawBackground(ctx, size)
  
  // Desenhar círculos concêntricos (rings)
  drawRings(ctx)
  
  // Desenhar linhas de referência (N, S, E, W)
  drawReferenceLines(ctx)
  
  // Desenhar varredura (sempre ativa para parecer um radar real)
  if (props.loading) {
    // Animação de varredura rápida durante loading
    drawLoadingSweep(ctx)
  } else {
    // Varredura idle lenta e contínua (sempre ativa)
    drawIdleSweep(ctx)
    // Se houver sweepAngle do backend, desenhar também
  if (props.sweepAngle > 0) {
    drawSweep(ctx, props.sweepAngle)
    }
  }
  
  // Desenhar blips (apenas se não estiver carregando)
  if (!props.loading) {
  drawBlips(ctx)
  }
  
  // Desenhar centro (melhor oportunidade)
  drawCenter(ctx)
  
  // Texto de loading (se estiver carregando)
  if (props.loading) {
    drawLoadingText(ctx)
  }
}

// Background verde esfumaçado com estética de radar (apenas dentro do círculo)
const drawBackground = (ctx, size) => {
  // Fundo preto sólido no container inteiro (fora do radar)
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, size, size)
  
  // Criar clipping path para desenhar apenas dentro do círculo do radar
  ctx.save()
  ctx.beginPath()
  ctx.arc(centerX.value, centerY.value, maxRadius.value, 0, Math.PI * 2)
  ctx.clip() // Aplicar clipping - tudo depois disso só aparece dentro do círculo
  
  // Base verde escuro esfumaçado (apenas dentro do círculo)
  ctx.fillStyle = '#001a0a' // Verde muito escuro (quase preto com toque verde)
  ctx.fillRect(0, 0, size, size)
  
  // Gradiente radial esfumaçado (do centro para as bordas)
  const bgGradient = ctx.createRadialGradient(
    centerX.value,
    centerY.value,
    0,
    centerX.value,
    centerY.value,
    maxRadius.value
  )
  bgGradient.addColorStop(0, '#002a15') // Centro verde mais claro
  bgGradient.addColorStop(0.3, '#001f0f')
  bgGradient.addColorStop(0.6, '#001a0a')
  bgGradient.addColorStop(1, '#000d05') // Bordas verde muito escuro
  
  // Aplicar gradiente com opacidade para efeito esfumaçado
  ctx.globalAlpha = 0.7
  ctx.fillStyle = bgGradient
  ctx.fillRect(0, 0, size, size)
  ctx.globalAlpha = 1.0
  
  // Grid de referência sutil (padrão de radar) - verde esfumaçado
  ctx.strokeStyle = '#00ff8815' // Verde esfumaçado
  ctx.lineWidth = 0.5
  
  // Linhas horizontais e verticais (grid) - apenas dentro do círculo
  const gridSpacing = size / 8 // 8 linhas de grid
  for (let i = 1; i < 8; i++) {
    const pos = (size / 8) * i
    
    // Linha horizontal
    ctx.beginPath()
    ctx.moveTo(0, pos)
    ctx.lineTo(size, pos)
    ctx.stroke()
    
    // Linha vertical
    ctx.beginPath()
    ctx.moveTo(pos, 0)
    ctx.lineTo(pos, size)
    ctx.stroke()
  }
  
  // Padrão de scanlines esfumaçado (efeito CRT/radar)
  ctx.fillStyle = '#00ff8808' // Verde esfumaçado
  for (let i = 0; i < size; i += 2) {
    ctx.fillRect(0, i, size, 1)
  }
  
  // Efeito de "fumaça" adicional - círculos concêntricos muito sutis
  ctx.strokeStyle = '#00ff8805'
  ctx.lineWidth = 0.5
  for (let i = 1; i <= 6; i++) {
    const radius = maxRadius.value * (i / 6)
    ctx.beginPath()
    ctx.arc(centerX.value, centerY.value, radius, 0, Math.PI * 2)
    ctx.stroke()
  }
  
  // Restaurar contexto (remover clipping)
  ctx.restore()
  
  // Anel externo esfumaçado (borda do radar) - desenhar depois do clipping
  ctx.strokeStyle = '#00ff8820'
  ctx.lineWidth = 1.5
  ctx.beginPath()
  ctx.arc(centerX.value, centerY.value, maxRadius.value, 0, Math.PI * 2)
  ctx.stroke()
}

const drawRings = (ctx) => {
  // Visual Terminal Institucional: mais sutil
  ctx.strokeStyle = '#00ff0015' // Mais sutil
  ctx.lineWidth = 0.5 // Mais fino
  
  // 4 rings (dividir o espaço entre minRadius e maxRadius)
  const ringCount = 4
  for (let i = 1; i <= ringCount; i++) {
    const radius = minRadius.value + ((maxRadius.value - minRadius.value) / ringCount) * i
    ctx.beginPath()
    ctx.arc(centerX.value, centerY.value, radius, 0, Math.PI * 2)
    ctx.stroke()
  }
}

const drawReferenceLines = (ctx) => {
  // Eixos reforçados para melhor orientação
  ctx.strokeStyle = '#00ff0020' // Reforçado (era #00ff0008)
  ctx.lineWidth = 1 // Reforçado (era 0.5)
  
  // Linhas N, S, E, W
  const directions = [
    { angle: 0, label: 'N' },   // Norte
    { angle: 90, label: 'E' },  // Leste
    { angle: 180, label: 'S' }, // Sul
    { angle: 270, label: 'W' }  // Oeste
  ]
  
  directions.forEach(dir => {
    const rad = (dir.angle * Math.PI) / 180
    const x = centerX.value + maxRadius.value * Math.cos(rad)
    const y = centerY.value + maxRadius.value * Math.sin(rad)
    
    // Linha do eixo (reforçada)
    ctx.beginPath()
    ctx.moveTo(centerX.value, centerY.value)
    ctx.lineTo(x, y)
    ctx.stroke()
    
    // Label com tipografia técnica
    ctx.fillStyle = '#00ff0060' // Reforçado (era #00ff0040)
    const fontSize = Math.max(11, canvasSize.value * 0.018) // Ligeiramente maior
    ctx.font = `bold ${fontSize}px 'JetBrains Mono', monospace`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    const labelOffset = Math.max(12, canvasSize.value * 0.02)
    const labelX = centerX.value + (maxRadius.value + labelOffset) * Math.cos(rad)
    const labelY = centerY.value + (maxRadius.value + labelOffset) * Math.sin(rad)
    ctx.fillText(dir.label, labelX, labelY)
  })
}

const drawSweep = (ctx, angle) => {
  const rad = ((angle - 90) * Math.PI) / 180 // -90 para começar no topo
  
  // Gradiente para a linha de varredura
  const gradient = ctx.createLinearGradient(
    centerX.value,
    centerY.value,
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad)
  )
  gradient.addColorStop(0, '#00ff0080')
  gradient.addColorStop(1, '#00ff0000')
  
  // Efeito de Bloom na linha de varredura
  ctx.shadowBlur = 8
  ctx.shadowColor = '#00ff8880' // Bloom verde neon
  
  ctx.strokeStyle = gradient
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(centerX.value, centerY.value)
  ctx.lineTo(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad)
  )
  ctx.stroke()
  
  // Resetar shadow
  ctx.shadowBlur = 0
  
  // Círculo no final da varredura (com bloom)
  ctx.shadowBlur = 6
  ctx.shadowColor = '#00ff8880'
  ctx.fillStyle = '#00ff00'
  ctx.beginPath()
  ctx.arc(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad),
    4,
    0,
    Math.PI * 2
  )
  ctx.fill()
  ctx.shadowBlur = 0
}

// Animação de varredura durante loading (mais fluida e visível)
const drawLoadingSweep = (ctx) => {
  const rad = ((loadingSweepAngle.value - 90) * Math.PI) / 180
  
  // Gradiente mais intenso para a varredura de loading
  const gradient = ctx.createLinearGradient(
    centerX.value,
    centerY.value,
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad)
  )
  gradient.addColorStop(0, '#00ff00') // Mais intenso no centro
  gradient.addColorStop(0.5, '#00ff0080')
  gradient.addColorStop(1, '#00ff0000')
  
  // Efeito de Bloom na linha de varredura (loading)
  ctx.shadowBlur = 12
  ctx.shadowColor = '#00ff8880' // Bloom verde neon intenso
  
  // Linha principal de varredura (mais espessa)
  ctx.strokeStyle = gradient
  ctx.lineWidth = 3
  ctx.beginPath()
  ctx.moveTo(centerX.value, centerY.value)
  ctx.lineTo(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad)
  )
  ctx.stroke()
  
  // Resetar shadow
  ctx.shadowBlur = 0
  
  // Arco de varredura (mostra área sendo varrida)
  const sweepArcWidth = 30 // Largura do arco em graus
  ctx.strokeStyle = '#00ff0030'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.arc(
    centerX.value,
    centerY.value,
    maxRadius.value,
    ((loadingSweepAngle.value - sweepArcWidth - 90) * Math.PI) / 180,
    ((loadingSweepAngle.value - 90) * Math.PI) / 180
  )
  ctx.stroke()
  
  // Círculo brilhante no final da varredura (com bloom)
  ctx.shadowBlur = 10
  ctx.shadowColor = '#00ff8880'
  const glowGradient = ctx.createRadialGradient(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad),
    0,
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad),
    8
  )
  glowGradient.addColorStop(0, '#00ff00')
  glowGradient.addColorStop(0.5, '#00ff0080')
  glowGradient.addColorStop(1, '#00ff0000')
  
  ctx.fillStyle = glowGradient
  ctx.beginPath()
  ctx.arc(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad),
    6,
    0,
    Math.PI * 2
  )
  ctx.fill()
  
  // Círculo sólido no centro do glow
  ctx.fillStyle = '#00ff00'
  ctx.beginPath()
  ctx.arc(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad),
    3,
    0,
    Math.PI * 2
  )
  ctx.fill()
  
  // Resetar shadow
  ctx.shadowBlur = 0
}

// Texto de loading sutil no centro
const drawLoadingText = (ctx) => {
  ctx.fillStyle = '#00ff0060' // Sutil
  const fontSize = Math.max(12, canvasSize.value * 0.02)
  ctx.font = `${fontSize}px 'JetBrains Mono', monospace`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('SCANNING...', centerX.value, centerY.value)
}

// Varredura idle (lenta e contínua, sempre ativa)
const drawIdleSweep = (ctx) => {
  const rad = ((idleSweepAngle.value - 90) * Math.PI) / 180
  
  // Gradiente sutil para varredura idle
  const gradient = ctx.createLinearGradient(
    centerX.value,
    centerY.value,
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad)
  )
  gradient.addColorStop(0, '#00ff0040') // Mais sutil que loading
  gradient.addColorStop(0.7, '#00ff0020')
  gradient.addColorStop(1, '#00ff0000')
  
  // Efeito de Bloom sutil na varredura idle
  ctx.shadowBlur = 6
  ctx.shadowColor = '#00ff8840' // Bloom mais sutil
  
  // Linha de varredura (mais fina que loading)
  ctx.strokeStyle = gradient
  ctx.lineWidth = 1.5
  ctx.beginPath()
  ctx.moveTo(centerX.value, centerY.value)
  ctx.lineTo(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad)
  )
  ctx.stroke()
  
  // Resetar shadow
  ctx.shadowBlur = 0
  
  // Arco de varredura sutil (área varrida)
  const sweepArcWidth = 20 // Largura menor que loading
  ctx.strokeStyle = '#00ff0010' // Muito sutil
  ctx.lineWidth = 0.5
  ctx.beginPath()
  ctx.arc(
    centerX.value,
    centerY.value,
    maxRadius.value,
    ((idleSweepAngle.value - sweepArcWidth - 90) * Math.PI) / 180,
    ((idleSweepAngle.value - 90) * Math.PI) / 180
  )
  ctx.stroke()
  
  // Círculo pequeno no final da varredura (com bloom sutil)
  ctx.shadowBlur = 4
  ctx.shadowColor = '#00ff8840'
  ctx.fillStyle = '#00ff0040'
  ctx.beginPath()
  ctx.arc(
    centerX.value + maxRadius.value * Math.cos(rad),
    centerY.value + maxRadius.value * Math.sin(rad),
    2,
    0,
    Math.PI * 2
  )
  ctx.fill()
  ctx.shadowBlur = 0
}

// Animação idle (varredura lenta contínua)
const animateIdleSweep = () => {
  // Incrementar ângulo lentamente (360 graus em 8 segundos = 45 graus/segundo)
  idleSweepAngle.value += 0.75 // Incremento lento (0.75 graus por frame a ~60fps = ~45 graus/segundo)
  
  if (idleSweepAngle.value >= 360) {
    idleSweepAngle.value = 0 // Resetar ao completar volta
  }
  
  // Redesenhar radar
  drawRadar()
  
  // Continuar animação
  idleAnimationId = requestAnimationFrame(animateIdleSweep)
}

// Animação de varredura contínua durante loading
const animateLoadingSweep = () => {
  if (!props.loading) {
    if (loadingAnimationId) {
      cancelAnimationFrame(loadingAnimationId)
      loadingAnimationId = null
    }
    return
  }
  
  // Incrementar ângulo (360 graus em 3 segundos = 120 graus/segundo)
  loadingSweepAngle.value += 2 // Incremento suave (2 graus por frame a ~60fps = ~120 graus/segundo)
  
  if (loadingSweepAngle.value >= 360) {
    loadingSweepAngle.value = 0 // Resetar ao completar volta
  }
  
  // Redesenhar radar
  drawRadar()
  
  // Continuar animação
  loadingAnimationId = requestAnimationFrame(animateLoadingSweep)
}

const drawBlips = (ctx) => {
  blipPositions.value.forEach((blip, index) => {
    const opp = blip.opportunity
    const isHovered = hoveredBlip.value?.symbol === opp.symbol
    
    // Cor baseado no sinal
    let color = '#ffff00' // NEUTRAL (amarelo)
    let shadowColor = '#ffff0080' // Cor do bloom para neutral
    if (opp.signal === 'BUY') {
      color = '#00ff00' // Verde
      shadowColor = '#00ff8880' // Bloom verde neon
    } else if (opp.signal === 'SELL') {
      color = '#ff0000' // Vermelho
      shadowColor = '#ff444480' // Bloom vermelho
    }
    
    // Tamanho do blip
    const size = isHovered ? blip.size * 1.5 : blip.size
    
    // Efeito de Bloom (brilho neon/CRT)
    ctx.shadowBlur = isHovered ? 15 : 10 // Mais brilho quando hovered
    ctx.shadowColor = shadowColor
    
    // Desenhar círculo do blip com bloom
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.arc(blip.x, blip.y, size, 0, Math.PI * 2)
    ctx.fill()
    
    // Resetar shadow para borda
    ctx.shadowBlur = 0
    
    // Borda mais escura
    ctx.strokeStyle = color + '80'
    ctx.lineWidth = 2
    ctx.stroke()
    
    // Pulsação se hovered (com bloom)
    if (isHovered) {
      ctx.shadowBlur = 8
      ctx.shadowColor = shadowColor
      ctx.strokeStyle = color
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.arc(blip.x, blip.y, size + 5, 0, Math.PI * 2)
      ctx.stroke()
      ctx.shadowBlur = 0
    }
    
    // Label do símbolo com tipografia técnica (JetBrains Mono)
    ctx.fillStyle = '#ffffff'
    const symbolFontSize = Math.max(9, canvasSize.value * 0.015)
    // Forçar JetBrains Mono com fallback
    ctx.font = `bold ${symbolFontSize}px 'JetBrains Mono', 'Courier New', monospace`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'
    const labelOffset = Math.max(3, canvasSize.value * 0.005)
    ctx.fillText(
      opp.symbol.replace('USDT', ''),
      blip.x,
      blip.y + size + labelOffset
    )
    
    // Score pequeno abaixo do símbolo (JetBrains Mono)
    ctx.fillStyle = '#00ff0070'
    const scoreFontSize = Math.max(7, canvasSize.value * 0.012)
    ctx.font = `${scoreFontSize}px 'JetBrains Mono', 'Courier New', monospace`
    const scoreOffset = Math.max(12, canvasSize.value * 0.02)
    ctx.fillText(
      opp.score?.toFixed(1) || '0.0',
      blip.x,
      blip.y + size + scoreOffset
    )
  })
}

const drawCenter = (ctx) => {
  // Círculo central (melhor oportunidade)
  ctx.strokeStyle = '#00ff00'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.arc(centerX.value, centerY.value, minRadius.value, 0, Math.PI * 2)
  ctx.stroke()
  ctx.setLineDash([])
  
  // Ponto central
  ctx.fillStyle = '#00ff00'
  ctx.beginPath()
  ctx.arc(centerX.value, centerY.value, 3, 0, Math.PI * 2)
  ctx.fill()
  
  // Label "CENTER" ou melhor oportunidade
  if (blipPositions.value.length > 0) {
    const best = blipPositions.value[0]
    if (best.distance <= minRadius.value + 10) {
      ctx.fillStyle = '#00ff00'
      const bestFontSize = Math.max(11, canvasSize.value * 0.018)
      ctx.font = `bold ${bestFontSize}px 'JetBrains Mono', monospace`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'bottom'
      const bestOffset = Math.max(5, canvasSize.value * 0.008)
      ctx.fillText('BEST', centerX.value, centerY.value - minRadius.value - bestOffset)
    }
  }
}

// Interatividade
const handleMouseMove = (event) => {
  const canvas = canvasRef.value
  if (!canvas || blipPositions.value.length === 0) return
  
  const rect = canvas.getBoundingClientRect()
  
  // Como o canvas não usa object-fit, o tamanho visual é igual ao tamanho interno
  // Mas precisamos verificar se há alguma diferença devido ao CSS
  const canvasWidth = canvas.width
  const canvasHeight = canvas.height
  const displayWidth = rect.width
  const displayHeight = rect.height
  
  // Calcular escala (normalmente será 1:1, mas pode haver pequenas diferenças)
  const scaleX = canvasWidth / displayWidth
  const scaleY = canvasHeight / displayHeight
  
  // Converter coordenadas do mouse para coordenadas do canvas
  const x = (event.clientX - rect.left) * scaleX
  const y = (event.clientY - rect.top) * scaleY
  
  // Verificar se está sobre algum blip (com margem adequada)
  const hovered = blipPositions.value.find(blip => {
    const dx = blip.x - x
    const dy = blip.y - y
    const distance = Math.sqrt(dx * dx + dy * dy)
    // Margem de hover baseada no tamanho do blip
    return distance <= blip.size + 10
  })
  
  if (hovered) {
    hoveredBlip.value = hovered.opportunity
    tooltipPosition.value = {
      x: event.clientX + 10,
      y: event.clientY - 10
    }
  } else {
    hoveredBlip.value = null
  }
}

const handleMouseLeave = () => {
  hoveredBlip.value = null
}

const handleClick = (event) => {
  const canvas = canvasRef.value
  if (!canvas || blipPositions.value.length === 0) return
  
  const rect = canvas.getBoundingClientRect()
  
  // Calcular escala
  const canvasWidth = canvas.width
  const canvasHeight = canvas.height
  const displayWidth = rect.width
  const displayHeight = rect.height
  
  const scaleX = canvasWidth / displayWidth
  const scaleY = canvasHeight / displayHeight
  
  // Converter coordenadas do mouse para coordenadas do canvas
  const x = (event.clientX - rect.left) * scaleX
  const y = (event.clientY - rect.top) * scaleY
  
  // Verificar se clicou em algum blip
  const clicked = blipPositions.value.find(blip => {
    const dx = blip.x - x
    const dy = blip.y - y
    const distance = Math.sqrt(dx * dx + dy * dy)
    // Margem de click baseada no tamanho do blip
    return distance <= blip.size + 10
  })
  
  if (clicked) {
    emit('blip-click', clicked.opportunity)
  }
}

// Watch para redesenhar quando oportunidades mudarem
watch(() => props.opportunities, (newOpps) => {
  calculatePositions(newOpps)
  nextTick(() => {
    drawRadar()
  })
}, { deep: true, immediate: true })

watch(() => props.sweepAngle, () => {
  drawRadar()
})

// Watch para iniciar/parar animação de loading
watch(() => props.loading, (isLoading) => {
  if (isLoading) {
    loadingSweepAngle.value = 0 // Resetar ângulo
    // Parar animação idle
    if (idleAnimationId) {
      cancelAnimationFrame(idleAnimationId)
      idleAnimationId = null
    }
    animateLoadingSweep() // Iniciar animação rápida
  } else {
    if (loadingAnimationId) {
      cancelAnimationFrame(loadingAnimationId)
      loadingAnimationId = null
    }
    // Reiniciar animação idle
    if (!idleAnimationId) {
      idleSweepAngle.value = 0
      animateIdleSweep()
    }
    drawRadar() // Redesenhar
  }
}, { immediate: true })

// Inicialização
onMounted(() => {
  // Calcular tamanho inicial
  updateCanvasSize()
  
  // Adicionar listener de resize
  window.addEventListener('resize', debouncedResize)
  
  // Calcular posições e desenhar
  calculatePositions(props.opportunities)
  nextTick(() => {
    drawRadar()
    // Iniciar animação idle se não estiver em loading
    if (!props.loading && !idleAnimationId) {
      animateIdleSweep()
    }
  })
})

onUnmounted(() => {
  // Remover listener de resize
  window.removeEventListener('resize', debouncedResize)
  if (resizeTimeout) {
    clearTimeout(resizeTimeout)
  }
  
  // Parar animações
  if (loadingAnimationId) {
    cancelAnimationFrame(loadingAnimationId)
    loadingAnimationId = null
  }
  if (idleAnimationId) {
    cancelAnimationFrame(idleAnimationId)
    idleAnimationId = null
  }
})

// Redesenhar quando necessário
const redraw = () => {
  drawRadar()
}

defineExpose({
  redraw
})
</script>

<style scoped>
.radar-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 350px; /* Reduzido de 400px */
  max-height: 500px; /* Limitar altura máxima */
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000000; /* Fundo preto sólido - sem gradiente */
  border-radius: 8px;
  padding: 8px; /* Padding mínimo */
  overflow: hidden; /* Evitar scroll */
}

.radar-canvas {
  display: block;
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  aspect-ratio: 1; /* Manter proporção quadrada */
  object-fit: contain; /* Ajustar mantendo proporção */
  cursor: crosshair;
}

/* Responsividade */
@media (max-width: 1024px) {
  .radar-container {
    min-height: 400px;
    max-height: 450px;
  }
}

@media (max-width: 768px) {
  .radar-container {
    min-height: 350px;
    max-height: 400px;
    padding: 4px;
  }
}

.radar-tooltip {
  position: fixed;
  background: rgba(10, 10, 10, 0.98);
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 10px 14px;
  pointer-events: none;
  z-index: 1000;
  min-width: 220px;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  font-family: 'JetBrains Mono', monospace;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #00ff0030;
}

.tooltip-symbol {
  font-weight: 600;
  color: #00ff00;
  font-size: 14px;
  letter-spacing: 0.05em;
}

.tooltip-signal {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 2px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.signal-buy {
  background: #00ff0020;
  color: #00ff00;
}

.signal-sell {
  background: #ff000020;
  color: #ff0000;
}

.signal-neutral {
  background: #ffff0020;
  color: #ffff00;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  gap: 12px;
}

.tooltip-value {
  color: #00ff00;
  font-weight: 600;
}

/* Legenda horizontal dentro do radar */
.radar-legend-inline {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.85);
  border: 1px solid #00ff0030;
  border-radius: 4px;
  padding: 8px 16px;
  pointer-events: none;
  z-index: 100;
  backdrop-filter: blur(4px);
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.legend-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-item-inline {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid #00ff0030;
  flex-shrink: 0;
}

.legend-ring {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid #00ff0030;
  background: transparent;
  flex-shrink: 0;
}

.ring-1 {
  border-color: #00ff00;
}

.ring-2 {
  border-color: #00ff0070;
}

.ring-3 {
  border-color: #00ff0040;
}

.ring-4 {
  border-color: #00ff0020;
}

.legend-center {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1.5px dashed #00ff00;
  background: transparent;
  flex-shrink: 0;
}

.legend-sweep {
  width: 12px;
  height: 2px;
  background: #00ff00;
  position: relative;
  flex-shrink: 0;
}

.legend-sweep::after {
  content: '';
  position: absolute;
  right: -3px;
  top: -2px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #00ff00;
}

.legend-text {
  color: #00ff0070;
  font-size: 9px;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.legend-separator {
  width: 1px;
  height: 20px;
  background: #00ff0020;
  flex-shrink: 0;
}

/* Responsividade */
@media (max-width: 768px) {
  .radar-legend-inline {
    bottom: 8px;
    padding: 6px 12px;
  }
  
  .legend-row {
    gap: 12px;
  }
  
  .legend-group {
    gap: 8px;
  }
  
  .legend-text {
    font-size: 8px;
  }
}

/* HUDs Táticos Flutuantes */
.tactical-huds {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 10;
}

.tactical-hud {
  position: absolute;
  background: rgba(0, 26, 10, 0.85); /* Verde esfumaçado */
  backdrop-filter: blur(8px);
  border: 1px solid #00ff8830;
  border-radius: 6px;
  padding: 10px 12px;
  min-width: 180px;
  max-width: 220px;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
  pointer-events: auto;
  font-family: 'JetBrains Mono', monospace;
}

.tactical-hud::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(0, 255, 136, 0.05) 0%, transparent 70%);
  border-radius: 6px;
  pointer-events: none;
}

.hud-top-left {
  top: 12px;
  left: 12px;
}

.hud-top-right {
  top: 12px;
  right: 12px;
}

.hud-bottom-left {
  bottom: 12px;
  left: 12px;
}

.hud-bottom-right {
  bottom: 12px;
  right: 12px;
}

.hud-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #00ff8820;
}

.hud-title {
  font-size: 9px;
  color: #00ff8870;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
}

.hud-status-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00ff88;
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.6);
  animation: pulse-hud 2s ease-in-out infinite;
}

@keyframes pulse-hud {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}

.hud-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* HUD Top Assets */
.hud-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  border-bottom: 1px solid #00ff8808;
}

.hud-item:last-child {
  border-bottom: none;
}

.hud-item-rank {
  font-size: 10px;
  color: #00ff8880;
  font-weight: 600;
  min-width: 16px;
}

.hud-item-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hud-item-symbol {
  font-size: 11px;
  color: #00ff88;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.hud-item-score {
  font-size: 10px;
  color: #00ff8870;
}

.hud-item-signal {
  font-size: 8px;
  padding: 2px 6px;
  border-radius: 2px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hud-item-signal.signal-buy {
  background: #00ff8820;
  color: #00ff88;
}

.hud-item-signal.signal-sell {
  background: #ff444420;
  color: #ff4444;
}

.hud-item-signal.signal-neutral {
  background: #ffff0020;
  color: #ffff00;
}

/* HUD Stats */
.hud-stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 3px 0;
  border-bottom: 1px solid #00ff8808;
}

.hud-stat-row:last-child {
  border-bottom: none;
}

.hud-stat-label {
  font-size: 9px;
  color: #00ff8860;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hud-stat-value {
  font-size: 11px;
  color: #00ff88;
  font-weight: 600;
}

/* HUD Regime */
.hud-regime {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #00ff8820;
}

.hud-regime-value {
  font-size: 14px;
  color: #00ff88;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-bottom: 4px;
  text-transform: uppercase;
}

.hud-regime-desc {
  font-size: 9px;
  color: #00ff8870;
  line-height: 1.3;
}

.hud-volatility {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hud-volatility-label {
  font-size: 9px;
  color: #00ff8860;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hud-volatility-value {
  font-size: 11px;
  color: #00ff88;
  font-weight: 600;
}

/* HUD BTC */
.hud-btc-price {
  font-size: 16px;
  color: #00ff88;
  font-weight: 700;
  margin-bottom: 4px;
  letter-spacing: 0.05em;
}

.hud-btc-change {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
  letter-spacing: 0.05em;
}

.hud-btc-status {
  font-size: 9px;
  color: #00ff8870;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding-top: 6px;
  border-top: 1px solid #00ff8808;
}

/* Responsividade para HUDs */
@media (max-width: 1024px) {
  .tactical-hud {
    min-width: 160px;
    max-width: 180px;
    padding: 8px 10px;
  }
  
  .hud-top-left,
  .hud-top-right {
    top: 8px;
  }
  
  .hud-bottom-left,
  .hud-bottom-right {
    bottom: 8px;
  }
}

@media (max-width: 768px) {
  .tactical-hud {
    min-width: 140px;
    max-width: 160px;
    padding: 6px 8px;
    font-size: 0.85em;
  }
  
  .hud-top-left,
  .hud-top-right {
    top: 4px;
  }
  
  .hud-bottom-left,
  .hud-bottom-right {
    bottom: 4px;
  }
  
  .hud-title {
    font-size: 8px;
  }
}
</style>


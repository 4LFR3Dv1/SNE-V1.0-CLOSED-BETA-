<template>
  <div class="interactive-chart-container">
    <div class="chart-header">
      <h3 class="text-lg font-bold">{{ symbol }} - {{ timeframe }}</h3>
      <div class="chart-controls">
        <!-- Controles de Zoom -->
        <div class="zoom-controls">
          <button 
            @click="zoomOut"
            class="zoom-btn"
            :disabled="loading || zoomLevel <= 0.62"
            title="Diminuir zoom"
          >
            ➖
          </button>
          <span class="zoom-display">{{ (zoomLevel * 100).toFixed(0) }}%</span>
          <button 
            @click="zoomIn"
            class="zoom-btn"
            :disabled="loading || zoomLevel >= 20"
            title="Aumentar zoom"
          >
            ➕
          </button>
          <button 
            @click="resetZoom"
            class="zoom-reset-btn"
            :disabled="loading || !isZoomed"
            title="Resetar zoom"
          >
            🔄
          </button>
        </div>
        <button 
          @click="refreshChart" 
          class="px-3 py-1 rounded text-sm bg-terminal-green text-black hover:opacity-80"
          :disabled="loading"
        >
          {{ loading ? '⏳ Carregando...' : '🔄 Atualizar' }}
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-terminal-green">Carregando gráfico...</div>
    </div>
    
    <div v-else-if="error" class="flex flex-col items-center justify-center h-96">
      <div class="text-red-500 mb-4">Erro: {{ error }}</div>
      <button 
        @click="refreshChart" 
        class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80"
      >
        Tentar Novamente
      </button>
    </div>
    
    <div 
      v-else 
      ref="chartWrapper"
      class="chart-wrapper"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseLeave"
    >
      <div 
        ref="imageContainer"
        class="image-container"
        :style="imageTransform"
      >
        <img 
          v-if="chartImageUrl"
          ref="chartImage"
          :src="chartImageUrl" 
          :alt="`Gráfico ${symbol} ${timeframe}`"
          class="chart-image"
          @load="handleImageLoad"
          @error="handleImageError"
          crossorigin="anonymous"
          draggable="false"
        />
      </div>
      
      <!-- Overlay Container para elementos interativos -->
      <div 
        ref="overlayContainer"
        class="overlay-container"
      >
        <!-- Painel de Informações (fixo na tela) -->
        <ChartInfoPanel
          v-if="analysisData && chartData"
          :symbol="symbol"
          :timeframe="timeframe"
          :signal="currentSignal"
          :score="currentScore"
          :currentPrice="chartData.current_price"
          :priceChange="priceChange"
          :rsi="analysisData?.indicadores?.rsi"
          :volumeRatio="volumeRatio"
          :riskLevel="analysisData?.sintese?.risco"
        />
        
        <!-- Linhas de Níveis (se move com zoom/pan) -->
        <div 
          class="levels-overlay"
          :style="overlayTransform"
        >
          <ChartLevelLines
            v-if="chartData && priceRange && imageHeight > 1000"
            :key="`levels-${imageHeight}-${initialZoom}`"
            :entry="chartData.levels?.operational?.entry"
            :stopLoss="chartData.levels?.operational?.stop_loss"
            :takeProfits="chartData.levels?.operational?.take_profit || []"
            :supports="chartData.levels?.supports || []"
            :resistances="chartData.levels?.resistances || []"
            :minPrice="priceRange.min"
            :maxPrice="priceRange.max"
            :currentPrice="chartData.current_price"
            :imageHeight="imageHeight"
            :initialZoom="initialZoom"
            @tooltip="handleLevelTooltip"
          />
        </div>
      </div>
      
      <!-- Overlay para tooltips e informações -->
      <div 
        v-if="tooltip.visible"
        class="tooltip candle-tooltip"
        :style="tooltipStyle"
      >
        <div class="tooltip-content">
          <div class="tooltip-title">{{ tooltip.title }}</div>
          <div class="tooltip-text" v-html="tooltip.text"></div>
          <div v-if="tooltip.candle" class="candle-info">
            <div class="candle-row">
              <span class="candle-label">O:</span>
              <span class="candle-value">${{ formatPrice(tooltip.candle.open) }}</span>
              <span class="candle-label">H:</span>
              <span class="candle-value">${{ formatPrice(tooltip.candle.high) }}</span>
            </div>
            <div class="candle-row">
              <span class="candle-label">L:</span>
              <span class="candle-value">${{ formatPrice(tooltip.candle.low) }}</span>
              <span class="candle-label">C:</span>
              <span class="candle-value">${{ formatPrice(tooltip.candle.close) }}</span>
            </div>
            <div v-if="tooltip.candle.volume" class="candle-row">
              <span class="candle-label">Vol:</span>
              <span class="candle-value">{{ formatVolume(tooltip.candle.volume) }}</span>
            </div>
            <div v-if="tooltip.candle.timestamp" class="candle-row">
              <span class="candle-label">Time:</span>
              <span class="candle-value">{{ formatTime(tooltip.candle.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useMarketStore } from '@/stores/market'
import api from '@/services/api'
import ChartInfoPanel from './ChartInfoPanel.vue'
import ChartLevelLines from './ChartLevelLines.vue'

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  },
  timeframe: {
    type: String,
    default: '1h'
  }
})

const chartWrapper = ref(null)
const imageContainer = ref(null)
const chartImage = ref(null)
const overlayContainer = ref(null)

const marketStore = useMarketStore()

const loading = ref(false)
const error = ref(null)
const chartImageUrl = ref('')

// Dados de análise e gráfico
const analysisData = ref(null)
const chartData = ref(null)
const priceChange = ref(null)
const imageHeight = ref(600)
const imageWidth = ref(1906)

// Estado de zoom e pan
const zoomLevel = ref(0.62) // Zoom inicial: 62%
const initialZoom = ref(0.62) // Zoom inicial fixo em 62%
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// Tooltip
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  title: '',
  text: '',
  candle: null
})

// Transformação da imagem
const imageTransform = computed(() => {
  return {
    transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoomLevel.value})`,
    transformOrigin: 'top left',
    transition: isDragging.value ? 'none' : 'transform 0.1s ease-out',
    position: 'absolute',
    top: 0,
    left: 0
  }
})

// Transformação dos overlays (mesma da imagem)
// IMPORTANTE: O overlay deve ter as dimensões da imagem ORIGINAL
// O scale será aplicado para reduzir/aumentar proporcionalmente
const overlayTransform = computed(() => {
  return {
    transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoomLevel.value})`,
    transformOrigin: 'top left',
    position: 'absolute',
    top: 0,
    left: 0,
    width: `${imageWidth.value}px`,
    height: `${imageHeight.value}px`,
    pointerEvents: 'none'
  }
})

// Price range para cálculo de coordenadas
const priceRange = computed(() => {
  if (!chartData.value?.candles || chartData.value.candles.length === 0) {
    console.warn('⚠️ Sem candles para calcular priceRange')
    return null
  }
  
  const candles = chartData.value.candles
  const prices = candles.flatMap(c => [c.open, c.high, c.low, c.close]).filter(p => p > 0)
  
  if (prices.length === 0) {
    console.warn('⚠️ Nenhum preço válido encontrado')
    return null
  }
  
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  
  // Adicionar margem de 5% para visualização (igual ao mplfinance)
  const margin = (max - min) * 0.05
  
  const range = {
    min: min - margin,
    max: max + margin
  }
  
  console.log('📊 PriceRange calculado:', {
    min: range.min.toFixed(2),
    max: range.max.toFixed(2),
    range: (range.max - range.min).toFixed(2),
    candles: candles.length
  })
  
  return range
})

// Sinal e score atuais
const currentSignal = computed(() => {
  if (analysisData.value) {
    return marketStore.signal
  }
  return 'NEUTRAL'
})

const currentScore = computed(() => {
  if (analysisData.value) {
    return marketStore.score
  }
  return 0
})

// Volume ratio
const volumeRatio = computed(() => {
  if (!analysisData.value?.contexto?.volume_status) return null
  const volStatus = analysisData.value.contexto.volume_status
  const match = volStatus.match(/([\d.]+)x/)
  return match ? parseFloat(match[1]) : null
})

// Estilo do tooltip
const tooltipStyle = computed(() => {
  return {
    left: `${tooltip.value.x}px`,
    top: `${tooltip.value.y}px`
  }
})

// Verificar se está com zoom (diferente do zoom inicial)
const isZoomed = computed(() => {
  return Math.abs(zoomLevel.value - initialZoom.value) > 0.01 || 
         (panX.value !== 0 && Math.abs(panX.value) > 1) || 
         (panY.value !== 0 && Math.abs(panY.value) > 1)
})

// URL do gráfico
const getChartUrl = () => {
  const timestamp = new Date().getTime()
  const isDev = import.meta.env.DEV
  const baseUrl = isDev ? 'http://localhost:9999' : ''
  return `${baseUrl}/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
}

// Carregar dados de análise
const loadAnalysisData = async () => {
  try {
    await marketStore.analyze(props.symbol, props.timeframe)
    analysisData.value = marketStore.analysisData
    
    // Calcular variação de preço se disponível
    if (chartData.value?.current_price && analysisData.value?.contexto?.preco_atual) {
      const current = chartData.value.current_price
      const previous = analysisData.value.contexto.preco_atual
      if (previous && previous > 0) {
        priceChange.value = ((current - previous) / previous) * 100
      }
    }
  } catch (err) {
    console.warn('⚠️ Erro ao carregar análise:', err)
    // Não bloquear se análise falhar
  }
}

// Carregar dados do gráfico (chart-data)
const loadChartData = async () => {
  try {
    const data = await api.getChartData(props.symbol, props.timeframe, 500)
    if (data && data.success) {
      chartData.value = data
      console.log('✅ Dados do gráfico carregados:', data)
    }
  } catch (err) {
    console.warn('⚠️ Erro ao carregar dados do gráfico:', err)
    // Não bloquear se chart-data falhar
  }
}

// Carregar gráfico
const loadChart = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Carregar imagem, análise e dados em paralelo
    const [imageResponse] = await Promise.all([
      fetch(getChartUrl(), {
        method: 'GET',
        mode: 'cors',
        credentials: 'omit',
        cache: 'no-cache'
      }),
      loadChartData(),
      loadAnalysisData()
    ])
    
    if (!imageResponse.ok) {
      const text = await imageResponse.text()
      if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
        error.value = 'Servidor retornou HTML. Verifique se o Flask está rodando na porta 9999.'
      } else {
        error.value = `Erro ${imageResponse.status}: ${imageResponse.statusText}`
      }
      loading.value = false
      return
    }
    
    const contentType = imageResponse.headers.get('content-type')
    if (!contentType || !contentType.includes('image')) {
      const text = await imageResponse.text()
      error.value = `Servidor não retornou uma imagem (Content-Type: ${contentType})`
      loading.value = false
      return
    }
    
    // Limpar blob URL anterior
    if (chartImageUrl.value && chartImageUrl.value.startsWith('blob:')) {
      URL.revokeObjectURL(chartImageUrl.value)
    }
    
    const blob = await imageResponse.blob()
    const blobUrl = URL.createObjectURL(blob)
    
    chartImageUrl.value = blobUrl
    loading.value = false
  } catch (err) {
    error.value = err.message || 'Erro ao carregar gráfico'
    console.error('❌ Erro ao carregar gráfico:', err)
    loading.value = false
  }
}

// Função para limitar pan aos limites
const constrainPan = () => {
  const wrapper = chartWrapper.value
  const image = chartImage.value
  if (!wrapper || !image) return
  
  const wrapperWidth = wrapper.offsetWidth || wrapper.clientWidth
  const wrapperHeight = wrapper.offsetHeight || wrapper.clientHeight
  const imageWidth = image.naturalWidth || image.width || image.offsetWidth
  const imageHeight = image.naturalHeight || image.height || image.offsetHeight
  
  if (!imageWidth || !imageHeight || !wrapperWidth || !wrapperHeight) return
  
  const scaledWidth = imageWidth * zoomLevel.value
  const scaledHeight = imageHeight * zoomLevel.value
  
  // Limitar pan horizontal
  if (scaledWidth <= wrapperWidth) {
    // Imagem menor que wrapper - centralizar
    panX.value = (wrapperWidth - scaledWidth) / 2
  } else {
    // Imagem maior - limitar movimento
    panX.value = Math.max(wrapperWidth - scaledWidth, Math.min(0, panX.value))
  }
  
  // Limitar pan vertical
  if (scaledHeight <= wrapperHeight) {
    // Imagem menor que wrapper - centralizar
    panY.value = (wrapperHeight - scaledHeight) / 2
  } else {
    // Imagem maior - limitar movimento
    panY.value = Math.max(wrapperHeight - scaledHeight, Math.min(0, panY.value))
  }
}

// Handlers de mouse para pan
const handleMouseDown = (e) => {
  // Permitir drag sempre, não apenas após zoom
  isDragging.value = true
  const rect = chartWrapper.value?.getBoundingClientRect()
  if (rect) {
    dragStart.value = {
      x: e.clientX - panX.value,
      y: e.clientY - panY.value
    }
  }
  e.preventDefault()
  e.stopPropagation()
}

const handleMouseMove = (e) => {
  if (isDragging.value) {
    panX.value = e.clientX - dragStart.value.x
    panY.value = e.clientY - dragStart.value.y
    constrainPan()
  } else {
    // Calcular informações do candle sob o mouse
    updateCandleTooltip(e)
  }
}

const handleMouseUp = () => {
  isDragging.value = false
}

const handleMouseLeave = () => {
  isDragging.value = false
  tooltip.value.visible = false
  tooltip.value.candle = null
}

// Calcular qual candle está sob o mouse e atualizar tooltip
const updateCandleTooltip = (e) => {
  const rect = chartWrapper.value?.getBoundingClientRect()
  if (!rect || !chartData.value?.candles || chartData.value.candles.length === 0) {
    tooltip.value.visible = false
    return
  }
  
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top
  
  // Calcular posição na imagem original (considerando zoom e pan)
  const imageX = (mouseX - panX.value) / zoomLevel.value
  const imageY = (mouseY - panY.value) / zoomLevel.value
  
  // Verificar se está dentro da área do gráfico (considerando margens)
  const marginTop = imageHeight.value * 0.10
  const marginBottom = imageHeight.value * 0.20
  const chartAreaHeight = imageHeight.value - marginTop - marginBottom
  
  if (imageY < marginTop || imageY > (marginTop + chartAreaHeight)) {
    tooltip.value.visible = false
    return
  }
  
  // Calcular qual candle está na posição X
  // mplfinance com figsize=(16, 10) tem margens aproximadas:
  // - Margem esquerda: ~10-12% (para labels do eixo Y)
  // - Margem direita: ~3-5% (espaçamento)
  // - Margem superior: ~10% (título)
  // - Margem inferior: ~20% (volume)
  const marginLeft = imageWidth.value * 0.11  // 11% margem esquerda
  const marginRight = imageWidth.value * 0.04  // 4% margem direita
  const chartAreaWidth = imageWidth.value - marginLeft - marginRight
  
  if (imageX < marginLeft || imageX > (marginLeft + chartAreaWidth)) {
    tooltip.value.visible = false
    return
  }
  
  // Calcular índice do candle baseado na posição X
  // Os candles estão ordenados cronologicamente: [0] = mais antigo (esquerda), [N-1] = mais recente (direita)
  const relativeX = imageX - marginLeft
  const normalizedX = Math.max(0, Math.min(1, relativeX / chartAreaWidth)) // 0 a 1, clampado
  
  // Calcular índice: candles[0] é o mais antigo (esquerda), candles[N-1] é o mais recente (direita)
  const totalCandles = chartData.value.candles.length
  // Usar Math.round para pegar o candle mais próximo, não apenas floor
  const candleIndex = Math.round(normalizedX * (totalCandles - 1))
  const clampedIndex = Math.max(0, Math.min(totalCandles - 1, candleIndex))
  const candle = chartData.value.candles[clampedIndex]
  
  if (!candle) {
    tooltip.value.visible = false
    return
  }
  
  // Calcular preço na posição Y
  if (!priceRange.value) {
    tooltip.value.visible = false
    return
  }
  
  const { min, max, range } = priceRange.value
  const normalizedY = 1 - ((imageY - marginTop) / chartAreaHeight)
  const priceAtY = min + (normalizedY * range)
  
  // Atualizar tooltip
  tooltip.value = {
    visible: true,
    x: mouseX + 15,
    y: mouseY - 10,
    title: `${props.symbol} - ${props.timeframe}`,
    text: `Preço: $${formatPrice(priceAtY)}`,
    candle: {
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
      volume: candle.volume,
      timestamp: candle.timestamp || candle.time
    }
  }
  
  // Ajustar posição do tooltip se sair da tela
  if (tooltip.value.x + 200 > rect.width) {
    tooltip.value.x = mouseX - 220
  }
  if (tooltip.value.y + 150 > rect.height) {
    tooltip.value.y = mouseY - 160
  }
}

// Funções de formatação
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
  }
  if (volume >= 1000) {
    return (volume / 1000).toFixed(2) + 'K'
  }
  return volume.toFixed(2)
}

const formatTime = (timestamp) => {
  if (!timestamp) return '--'
  try {
    const date = new Date(timestamp * 1000 || timestamp)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '--'
  }
}

// Funções de zoom
const zoomIn = () => {
  const rect = chartWrapper.value?.getBoundingClientRect()
  const image = chartImage.value
  if (!rect || !image) return
  
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  
  const imageX = (centerX - panX.value) / zoomLevel.value
  const imageY = (centerY - panY.value) / zoomLevel.value
  
  const newZoom = Math.min(20, zoomLevel.value + 0.2)
  if (newZoom === zoomLevel.value) return
  
  zoomLevel.value = newZoom
  panX.value = centerX - (imageX * newZoom)
  panY.value = centerY - (imageY * newZoom)
  constrainPan()
}

const zoomOut = () => {
  const rect = chartWrapper.value?.getBoundingClientRect()
  const image = chartImage.value
  if (!rect || !image) return
  
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  
  const imageX = (centerX - panX.value) / zoomLevel.value
  const imageY = (centerY - panY.value) / zoomLevel.value
  
  const newZoom = Math.max(0.62, zoomLevel.value - 0.2)
  if (newZoom === zoomLevel.value) return
  
  zoomLevel.value = newZoom
  panX.value = centerX - (imageX * newZoom)
  panY.value = centerY - (imageY * newZoom)
  constrainPan()
}

const resetZoom = () => {
  zoomLevel.value = initialZoom.value
  centerImage()
}

// Handler de wheel para zoom
const handleWheel = (e) => {
  e.preventDefault()
  e.stopPropagation()
  
  const rect = chartWrapper.value?.getBoundingClientRect()
  const image = chartImage.value
  if (!rect || !image) return
  
  // Calcular posição do mouse relativa ao wrapper
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top
  
  // Calcular posição do mouse na imagem (antes do zoom)
  const imageX = (mouseX - panX.value) / zoomLevel.value
  const imageY = (mouseY - panY.value) / zoomLevel.value
  
  // Calcular novo zoom - permitir zoom até 20x (2000%)
  // Zoom mínimo fixo em 62% (0.62)
  const zoomDelta = e.deltaY > 0 ? -0.15 : 0.15
  const newZoom = Math.max(0.62, Math.min(20, zoomLevel.value + zoomDelta))
  
  if (newZoom === zoomLevel.value) return
  
  // Aplicar novo zoom
  const oldZoom = zoomLevel.value
  zoomLevel.value = newZoom
  
  // Ajustar pan para manter o ponto do mouse fixo na imagem
  panX.value = mouseX - (imageX * newZoom)
  panY.value = mouseY - (imageY * newZoom)
  
  // Limitar pan aos limites da imagem
  constrainPan()
}

// Refresh
const refreshChart = () => {
  // Resetar para zoom inicial (62%) ao recarregar
  zoomLevel.value = 0.62
  initialZoom.value = 0.62
  panX.value = 0
  panY.value = 0
  loadChart()
}

// Calcular zoom inicial para preencher o container (mínimo 62%)
const calculateInitialZoom = () => {
  const wrapper = chartWrapper.value
  const image = chartImage.value
  if (!wrapper || !image) return 0.62
  
  const wrapperWidth = wrapper.offsetWidth || wrapper.clientWidth
  const wrapperHeight = wrapper.offsetHeight || wrapper.clientHeight
  const imageWidth = image.naturalWidth || image.width || image.offsetWidth
  const imageHeight = image.naturalHeight || image.height || image.offsetHeight
  
  if (!imageWidth || !imageHeight || !wrapperWidth || !wrapperHeight) return 0.62
  
  // Calcular zoom para preencher o container (sem bordas)
  const scaleX = wrapperWidth / imageWidth
  const scaleY = wrapperHeight / imageHeight
  const calculatedZoom = Math.max(scaleX, scaleY) // Usar o maior para preencher completamente
  
  // Garantir que nunca seja menor que 62% (zoom mínimo)
  const initialZoom = Math.max(calculatedZoom, 0.62)
  
  console.log('📊 Cálculo de zoom inicial:', {
    wrapper: `${wrapperWidth}x${wrapperHeight}`,
    image: `${imageWidth}x${imageHeight}`,
    scaleX: scaleX.toFixed(2),
    scaleY: scaleY.toFixed(2),
    calculated: calculatedZoom.toFixed(2),
    final: initialZoom.toFixed(2)
  })
  
  return initialZoom
}

// Centralizar imagem no container
const centerImage = () => {
  const wrapper = chartWrapper.value
  const image = chartImage.value
  if (!wrapper || !image) return
  
  const wrapperWidth = wrapper.offsetWidth || wrapper.clientWidth
  const wrapperHeight = wrapper.offsetHeight || wrapper.clientHeight
  const imageWidth = image.naturalWidth || image.width || image.offsetWidth
  const imageHeight = image.naturalHeight || image.height || image.offsetHeight
  
  if (!imageWidth || !imageHeight || !wrapperWidth || !wrapperHeight) return
  
  const scaledWidth = imageWidth * zoomLevel.value
  const scaledHeight = imageHeight * zoomLevel.value
  
  // Centralizar horizontalmente
  if (scaledWidth < wrapperWidth) {
    panX.value = (wrapperWidth - scaledWidth) / 2
  } else {
    panX.value = 0
  }
  
  // Centralizar verticalmente
  if (scaledHeight < wrapperHeight) {
    panY.value = (wrapperHeight - scaledHeight) / 2
  } else {
    panY.value = 0
  }
}

// Handler para tooltip de níveis
const handleLevelTooltip = (tooltipData) => {
  if (tooltipData.visible) {
    const rect = chartWrapper.value?.getBoundingClientRect()
    if (rect) {
      tooltip.value = {
        visible: true,
        x: tooltipData.x - rect.left,
        y: tooltipData.y - rect.top,
        title: '',
        text: tooltipData.content.replace('\n', '<br>')
      }
    }
  } else {
    tooltip.value.visible = false
  }
}

// Handlers de imagem
const handleImageLoad = () => {
  console.log('✅ Imagem do gráfico carregada com sucesso')
  error.value = null
  loading.value = false
  
  // Obter dimensões da imagem IMEDIATAMENTE
  const image = chartImage.value
  if (image) {
    // Usar naturalHeight e naturalWidth que são as dimensões reais da imagem original
    const height = image.naturalHeight || image.height || 600
    const width = image.naturalWidth || image.width || 1906
    imageHeight.value = height
    imageWidth.value = width
    console.log('📏 Dimensões da imagem detectadas (handleImageLoad):', {
      width,
      height,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      heightProp: image.height,
      widthProp: image.width
    })
  }
  
  // Aguardar imagem estar totalmente carregada e container estar pronto
  nextTick(() => {
    setTimeout(() => {
      const image = chartImage.value
      const wrapper = chartWrapper.value
      
      if (image && image.complete && wrapper) {
        // Atualizar dimensões com valores mais precisos - FORÇAR naturalHeight/naturalWidth
        let height = image.naturalHeight
        let width = image.naturalWidth
        
        if (!height && width) {
          // mplfinance usa figsize=(16, 10), então aspect ratio é 16:10 = 1.6
          height = width / 1.6
        }
        if (!height) {
          height = image.height || 600
        }
        if (!width) {
          width = image.width || 1906
        }
        
        // FORÇAR atualização das dimensões
        imageHeight.value = height
        imageWidth.value = width
        
        console.log('📏 Altura da imagem atualizada (nextTick):', height, {
          naturalHeight: image.naturalHeight,
          height: image.height,
          clientHeight: image.clientHeight,
          naturalWidth: image.naturalWidth,
          imageHeightRef: imageHeight.value,
          '✅ imageHeight atualizado para': imageHeight.value
        })
        
        // Forçar re-renderização do ChartLevelLines com nextTick
        nextTick(() => {
          console.log('🔄 ChartLevelLines será re-renderizado com imageHeight:', imageHeight.value)
        })
        
        // Calcular zoom inicial para caber no container
        const calculatedZoom = calculateInitialZoom()
        
        // Validar zoom calculado
        if (calculatedZoom > 0 && calculatedZoom <= 1 && !isNaN(calculatedZoom)) {
          // Salvar zoom inicial ANTES de aplicar
          initialZoom.value = calculatedZoom
          zoomLevel.value = calculatedZoom
          
          console.log('📊 Zoom inicial calculado e salvo:', calculatedZoom.toFixed(2))
          
          // Centralizar imagem após aplicar zoom
          nextTick(() => {
            centerImage()
            console.log('📊 Imagem centralizada. Pan:', panX.value.toFixed(0), panY.value.toFixed(0))
          })
        } else {
          console.warn('⚠️ Zoom inicial inválido:', calculatedZoom)
          initialZoom.value = 0.62
          zoomLevel.value = 0.62
        }
      }
    }, 150) // Aumentar delay para garantir que tudo está pronto
  })
}

const handleImageError = async (e) => {
  console.error('❌ Erro ao carregar imagem do gráfico:', e)
  error.value = 'Erro ao carregar imagem do gráfico'
  loading.value = false
}

// Limpar blob URLs
onUnmounted(() => {
  if (chartImageUrl.value && chartImageUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(chartImageUrl.value)
  }
})

// Watch props
watch([() => props.symbol, () => props.timeframe], () => {
  // Resetar zoom inicial (62%) antes de carregar nova imagem
  initialZoom.value = 0.62
  zoomLevel.value = 0.62
  panX.value = 0
  panY.value = 0
  loadChart()
})

// Carregar ao montar
onMounted(() => {
  loadChart()
})
</script>

<style scoped>
.interactive-chart-container {
  @apply w-full bg-terminal-dark rounded-lg p-4;
}

.chart-header {
  @apply flex justify-between items-center mb-4;
}

.chart-controls {
  @apply flex gap-2 flex-wrap;
}

.chart-wrapper {
  @apply w-full bg-terminal-gray rounded border border-terminal-green/30;
  position: relative;
  min-height: 500px;
  max-height: 800px;
  height: 600px;
  overflow: hidden;
  cursor: grab;
  user-select: none;
  touch-action: none;
}

.chart-wrapper:active {
  cursor: grabbing;
}

.image-container {
  position: absolute;
  top: 0;
  left: 0;
  will-change: transform;
  width: fit-content;
  height: fit-content;
}

.chart-image {
  display: block;
  width: auto;
  height: auto;
  max-width: none;
  max-height: none;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
}

.tooltip {
  position: absolute;
  pointer-events: none;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #00ff88;
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 12px;
  color: #00ff88;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
  max-width: 250px;
}

.candle-tooltip {
  font-family: 'Courier New', monospace;
}

.candle-info {
  @apply mt-2 pt-2 border-t border-terminal-green/30;
}

.candle-row {
  @apply flex items-center gap-2 mb-1;
}

.candle-label {
  @apply text-terminal-green/70 font-bold min-w-[30px];
}

.candle-value {
  @apply text-terminal-green font-mono;
}

.tooltip-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.tooltip-text {
  color: #00ff88;
  opacity: 0.8;
}

.chart-controls {
  @apply flex items-center gap-3;
}

.zoom-controls {
  @apply flex items-center gap-2 bg-terminal-gray/50 rounded px-2 py-1 border border-terminal-green/30;
}

.zoom-btn {
  @apply w-8 h-8 flex items-center justify-center rounded bg-terminal-green/20 text-terminal-green hover:bg-terminal-green/30 border border-terminal-green/50 text-lg font-bold transition-colors;
}

.zoom-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.zoom-display {
  @apply text-terminal-green text-sm font-mono min-w-[50px] text-center;
}

.zoom-reset-btn {
  @apply px-2 py-1 text-xs rounded bg-terminal-gray text-terminal-green hover:bg-terminal-green/20 border border-terminal-green/50 transition-colors;
}

.zoom-reset-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.overlay-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 50;
}

.overlay-container > * {
  pointer-events: auto;
}

.levels-overlay {
  position: absolute;
  top: 0;
  left: 0;
  /* IMPORTANTE: Usar dimensões da imagem original, não do container
     O scale será aplicado pelo overlayTransform */
  width: 100%;
  height: 100%;
  pointer-events: none;
  /* Garantir que o overlay cubra toda a área da imagem */
  min-width: 100%;
  min-height: 100%;
}

.levels-overlay > * {
  pointer-events: auto;
}
</style>


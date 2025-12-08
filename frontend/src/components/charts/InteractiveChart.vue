<template>
  <div class="interactive-chart-container">
    <!-- Header com controles -->
    <div class="chart-header">
      <h3 class="text-lg font-bold">{{ symbol }} - {{ timeframe }}</h3>
      <div class="chart-controls">
        <div class="zoom-controls">
          <button @click="zoomOut" class="zoom-btn" :disabled="loading" title="Diminuir zoom">➖</button>
          <span class="zoom-display">{{ zoomLevel }}%</span>
          <button @click="zoomIn" class="zoom-btn" :disabled="loading" title="Aumentar zoom">➕</button>
        </div>
        <button @click="refreshChart" class="px-3 py-1 rounded text-sm bg-terminal-green text-black hover:opacity-80" :disabled="loading">
          {{ loading ? '⏳ Carregando...' : '🔄 Atualizar' }}
        </button>
      </div>
    </div>
    
    <!-- Sandbox: Container principal para gráfico e overlays -->
    <div ref="chartWrapper" class="chart-sandbox" :style="{ display: error ? 'none' : 'block' }">
      <!-- Loading Overlay -->
      <div v-if="showLoading" class="chart-loading-overlay">
        <div class="loading-spinner-center">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-terminal-green"></div>
        </div>
    </div>
    
      <!-- Error Overlay -->
      <div v-show="error" class="chart-error-overlay">
      <div class="text-red-500 mb-4">Erro: {{ error }}</div>
        <button @click="refreshChart" class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80">
        Tentar Novamente
      </button>
    </div>
      
      <!-- Canvas Container: DEVE receber eventos do mouse -->
      <div ref="chartContainer" class="chart-container-absolute"></div>
      
      <!-- Overlays: NÃO bloqueiam eventos (pointer-events: none) -->
      <div class="chart-overlays-absolute">
        <!-- Tooltips de níveis -->
        <ChartLevelLines
          v-if="chartData?.levels && chart && candleSeries"
          :supports="chartData.levels.supports"
          :resistances="chartData.levels.resistances"
          :currentPrice="chartData?.current_price"
          :timeframe="timeframe"
        />
        
        <!-- Linha do preço atual -->
        <div 
          v-if="currentPriceCoordinate !== null && chart && candleSeries"
          class="current-price-line"
          :style="{ top: currentPriceCoordinate + 'px' }"
        >
          <div class="current-price-line-bar"></div>
          <div class="current-price-label">
            <span class="label-text">ATUAL</span>
            <span class="label-price">${{ formatPrice(chartData?.current_price) }}</span>
          </div>
        </div>
        
        <!-- Painel de informações -->
        <ChartInfoPanel
          v-if="analysisData && chartData"
          :symbol="symbol"
          :timeframe="timeframe"
          :signal="currentSignal"
          :score="currentScore"
          :currentPrice="activeCandle ? activeCandle.close : chartData.current_price"
          :priceChange="priceChange"
          :rsi="analysisData?.indicadores?.rsi"
          :volumeRatio="volumeRatio"
          :riskLevel="analysisData?.sintese?.risco"
          :activeCandle="activeCandle"
        />
      </div>
      
      <!-- Indicador de preço no cursor (fora dos overlays) -->
      <div 
        v-if="isMouseOverChart && cursorPrice && chartWrapper"
        class="cursor-price-indicator"
        :style="{
          left: (crosshairPosition.x - (chartWrapper?.getBoundingClientRect()?.left || 0) - 100) + 'px',
          top: (crosshairPosition.y - (chartWrapper?.getBoundingClientRect()?.top || 0) - 25) + 'px'
        }"
      >
        <div class="cursor-price-badge">${{ formatPrice(cursorPrice) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, markRaw, provide } from 'vue'
import { createChart, ColorType } from 'lightweight-charts'
import { useMarketStore } from '@/stores/market'
import api from '@/services/api'
import ChartInfoPanel from './ChartInfoPanel.vue'
import ChartLevelLines from './ChartLevelLines.vue'

// ============================================================================
// PROPS
// ============================================================================
const props = defineProps({
  symbol: { type: String, default: 'BTCUSDT' },
  timeframe: { type: String, default: '1h' }
})

// ============================================================================
// REFS E ESTADO
// ============================================================================
const chartWrapper = ref(null)
const chartContainer = ref(null)
const marketStore = useMarketStore()

const loading = ref(false)
const showLoading = ref(false)
const error = ref(null)
const chartData = ref(null)
const analysisData = ref(null)
const priceChange = ref(null)

// Instâncias do gráfico (markRaw para evitar reatividade do Vue)
const chart = ref(null)
const candleSeries = ref(null)
const volumeSeries = ref(null)
const ema8Series = ref(null)
const ema21Series = ref(null)
const levelLines = ref([])

// Estado do gráfico
const zoomLevel = ref(100)
const currentPriceCoordinate = ref(null)
const activeCandle = ref(null)
const activeLevelTooltip = ref(null)
const crosshairPosition = ref({ x: 0, y: 0 })
const cursorPrice = ref(null)
const isMouseOverChart = ref(false)

// Polling
const pollingInterval = ref(null)
const isPollingActive = ref(false)
const pollingErrorCount = ref(0)
const pollingBackoffDelay = ref(0)
const pollingBackoffTimeout = ref(null)
const basePollingInterval = 5000 // 5 segundos
const maxPollingInterval = 60000 // 60 segundos máximo

// Delay para mostrar loading
let loadingTimeout = null
watch(loading, (isLoading) => {
  if (isLoading) {
    loadingTimeout = setTimeout(() => { showLoading.value = true }, 300)
  } else {
    if (loadingTimeout) {
      clearTimeout(loadingTimeout)
      loadingTimeout = null
    }
    showLoading.value = false
  }
})

// ============================================================================
// COMPUTED
// ============================================================================
const currentSignal = computed(() => analysisData.value?.sintese?.sinal || 'NEUTRO')
const currentScore = computed(() => analysisData.value?.sintese?.score || 0)
const volumeRatio = computed(() => analysisData.value?.indicadores?.volume_ratio || null)

// ============================================================================
// FUNÇÕES UTILITÁRIAS
// ============================================================================

/**
 * Ordena e limpa níveis S/R
 * Suportes: decrescente (S1 > S2 > S3)
 * Resistências: crescente (R1 < R2 < R3)
 */
const sortAndCleanLevels = (levels) => {
  if (!levels) return levels
  const newLevels = { ...levels }
  
  if (newLevels.supports && Array.isArray(newLevels.supports)) {
    newLevels.supports = [...newLevels.supports]
      .filter(s => s && s > 0 && !isNaN(s))
      .map(s => parseFloat(s))
      .sort((a, b) => b - a) // Decrescente
  }
  
  if (newLevels.resistances && Array.isArray(newLevels.resistances)) {
    newLevels.resistances = [...newLevels.resistances]
      .filter(r => r && r > 0 && !isNaN(r))
      .map(r => parseFloat(r))
      .sort((a, b) => a - b) // Crescente
  }
  
  return newLevels
}

/**
 * Converte preço para coordenada Y usando a biblioteca
 */
const priceToY = (price) => {
  if (!price || !candleSeries.value || !chart.value) return null
  try {
    return candleSeries.value.priceToCoordinate(price)
  } catch (e) {
    console.warn('⚠️ Erro ao converter preço para coordenada:', e)
    return null
  }
}

/**
 * Atualiza a posição da linha do preço atual
 */
const updatePriceLinePosition = () => {
  if (!candleSeries.value || !chart.value || !chartData.value?.current_price) {
    currentPriceCoordinate.value = null
    return
  }
  const coordinate = candleSeries.value.priceToCoordinate(chartData.value.current_price)
  currentPriceCoordinate.value = coordinate !== null ? coordinate : null
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

// ============================================================================
// CONTEXTO PARA COMPONENTES FILHOS
// ============================================================================
provide('chartContext', {
  priceToY,
  updateTrigger: ref(0),
  activeLevelTooltip,
  crosshairPosition,
  crosshairYRelative: ref(null)
})

// ============================================================================
// INICIALIZAÇÃO DO GRÁFICO
// ============================================================================

/**
 * Inicializa o gráfico lightweight-charts
 */
const initChart = async () => {
  try {
  const container = chartContainer.value
  if (!container) {
      console.error('❌ Container não encontrado')
    return
  }
  
    // Limpar container
  while (container.firstChild) {
    container.removeChild(container.firstChild)
  }
  
    // Obter dimensões
  const rect = container.getBoundingClientRect()
    const chartWidth = rect.width || container.clientWidth || 800
    const chartHeight = rect.height || container.clientHeight || 600
  
  if (chartWidth <= 0 || chartHeight <= 0) {
    error.value = 'Container sem dimensões válidas'
    return
  }
  
    // Criar gráfico
    const chartInstance = createChart(container, {
      width: chartWidth,
      height: chartHeight,
      watermark: { visible: false },
      layout: {
        background: { type: ColorType.Solid, color: '#0a0a0a' },
        textColor: '#00ff88',
        fontSize: 12
      },
      grid: {
        vertLines: { color: '#1a1a1a', style: 1 },
        horzLines: { color: '#1a1a1a', style: 1 }
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: '#00ff88',
        fixLeftEdge: false,
        fixRightEdge: false,
        lockVisibleTimeRangeOnResize: false,
        allowBoldLabels: true,
        visible: true,
        rightOffset: 10
      },
      rightPriceScale: {
        visible: true,
        borderColor: '#00ff88',
        autoScale: true,
        mode: 0,
        position: 'right',
        autoScaleMarginTop: 0.0,
        autoScaleMarginBottom: 0.0
      },
      leftPriceScale: { visible: false },
      crosshair: {
        mode: 1,
        vertLine: { color: '#00ff88', width: 1, style: 2, labelBackgroundColor: '#00ff88' },
        horzLine: { color: '#00ff88', width: 1, style: 2, labelBackgroundColor: '#00ff88' }
      }
    })
    
    chart.value = markRaw(chartInstance)
    
    // Aguardar canvas ser criado
    await new Promise(resolve => requestAnimationFrame(resolve))
    
    // Adicionar série de candles
    const candleSeriesInstance = chart.value.addCandlestickSeries({
      upColor: '#00ff88',
      downColor: '#ff4444',
      borderVisible: false,
      wickUpColor: '#00ff88',
      wickDownColor: '#ff4444',
      priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
      priceScaleId: 'right',
      priceLineVisible: false,
      lastValueVisible: false
    })
    candleSeries.value = markRaw(candleSeriesInstance)
    
    // Adicionar série de volume
    const volumeSeriesInstance = chart.value.addHistogramSeries({
      color: '#00ff88',
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
      scaleMargins: { top: 0.9, bottom: 0 }
    })
    volumeSeries.value = markRaw(volumeSeriesInstance)
    
    // Configurar escala de volume
    chart.value.priceScale('volume').applyOptions({
      visible: false,
      scaleMargins: { top: 0.9, bottom: 0 }
    })
    
    // Subscribir a mudanças de zoom/pan
    chart.value.timeScale().subscribeVisibleTimeRangeChange(() => {
      updatePriceLinePosition()
    })
    
    // Subscribir ao movimento do crosshair
    chart.value.subscribeCrosshairMove(handleCrosshairMove)
    
    // Carregar dados
    await loadChartData(container)
    
    // Iniciar polling
    startPolling()
    
  } catch (err) {
    console.error('❌ Erro ao inicializar gráfico:', err)
    error.value = err.message || 'Erro ao carregar gráfico'
  }
}

/**
 * Manipula o movimento do crosshair
 */
const handleCrosshairMove = (param) => {
      if (!param || !param.time || !candleSeries.value || !chartData.value?.candles) {
    // Mouse fora do gráfico
        if (chartData.value?.candles && chartData.value.candles.length > 0) {
          const lastCandle = chartData.value.candles[chartData.value.candles.length - 1]
          activeCandle.value = {
            time: lastCandle.time,
            open: lastCandle.open,
            high: lastCandle.high,
            low: lastCandle.low,
            close: lastCandle.close,
            volume: lastCandle.volume || 0
          }
        } else {
          activeCandle.value = null
        }
    activeLevelTooltip.value = null
        cursorPrice.value = null
        isMouseOverChart.value = false
        return
      }
      
      // Mouse sobre o gráfico
      isMouseOverChart.value = true
      
      // Calcular preço na posição Y do cursor
      if (param.point && candleSeries.value) {
        try {
          const priceAtCursor = candleSeries.value.coordinateToPrice(param.point.y)
          if (priceAtCursor !== null && priceAtCursor > 0) {
            cursorPrice.value = priceAtCursor
          }
        } catch (e) {
      // Ignorar erros
        }
      }
      
  // Encontrar candle mais próximo
      const candleTime = param.time
      const candles = chartData.value.candles
      let closestCandle = null
      let minDiff = Infinity
      
      for (const candle of candles) {
        const diff = Math.abs(candle.time - candleTime)
        if (diff < minDiff) {
          minDiff = diff
          closestCandle = candle
        }
      }
      
      if (closestCandle) {
        const crosshairPrice = param.seriesData?.get(candleSeries.value)?.close || closestCandle.close
        activeCandle.value = {
          time: closestCandle.time,
          open: closestCandle.open,
          high: closestCandle.high,
          low: closestCandle.low,
      close: crosshairPrice,
          volume: closestCandle.volume || 0
        }
        
    // Detectar níveis próximos
    detectLevelProximity(param)
  } else {
    activeCandle.value = null
    activeLevelTooltip.value = null
  }
}

/**
 * Detecta níveis S/R próximos ao cursor
 */
const detectLevelProximity = (param) => {
        const levels = chartData.value?.levels
        const containerRect = chartContainer.value?.getBoundingClientRect()
        
  if (!levels || !param.point || !containerRect || !candleSeries.value) {
    activeLevelTooltip.value = null
    return
  }
  
  const cursorY = param.point.y
  const thresholdPixels = 25
          let closestLevel = null
          let minDistancePixels = Infinity
          
  // DEBUG: Log para verificar quantas resistências temos
  if (levels.resistances && Array.isArray(levels.resistances)) {
    console.log('🔍 [DEBUG] Iniciando detecção de níveis:', {
      resistancesCount: levels.resistances.length,
      resistances: levels.resistances.map((r, i) => ({ index: i, label: `R${i + 1}`, price: r })),
      cursorY,
      chartHeight: containerRect.height
    })
  }
          
  const checkLevel = (price, levelType, label, index = null) => {
    if (!price || price <= 0 || isNaN(price)) return false
            
    try {
            const levelY = candleSeries.value.priceToCoordinate(price)
      
      // Se priceToCoordinate retorna null, o nível não está visível na escala atual
      // MAS: Para resistências no topo, pode retornar null mesmo estando visível
      // Vamos ser mais permissivos e verificar se o preço está no range visível
      if (levelY === null || isNaN(levelY)) {
        // Para resistências (especialmente R3, R4, R5), tentar verificar se estão no range de preços visível
        if (levelType === 'resistance' && index >= 2) {
          try {
            // Obter range de preços visível
            const priceScale = chart.value.priceScale('right')
            if (priceScale) {
              const visibleRange = priceScale.getVisibleRange()
              if (visibleRange && price >= visibleRange.from && price <= visibleRange.to) {
                // O nível está no range visível, mas priceToCoordinate retornou null
                // Isso pode acontecer se o nível está muito próximo da borda
                // Vamos usar uma estimativa baseada no range
                const range = visibleRange.to - visibleRange.from
                const pricePercent = (price - visibleRange.from) / range
                const estimatedY = containerRect.height * (1 - pricePercent) // Invertido: topo = menor Y
                
                // Se a estimativa está próxima do cursor, considerar
                const distancePixels = Math.abs(cursorY - estimatedY)
                if (distancePixels < thresholdPixels * 2 && distancePixels < minDistancePixels) {
              minDistancePixels = distancePixels
                  closestLevel = { type: levelType, price: parseFloat(price), label, index }
                  console.log(`✅ [DEBUG] R${index + 1} detectado via estimativa:`, {
                    price,
                    estimatedY,
                    cursorY,
                    distancePixels,
                    visibleRange
                  })
                  return true
                }
              }
            }
          } catch (e) {
            // Ignorar erros na estimativa
          }
        }
        return false
      }
      
      // Aumentar tolerância significativamente para capturar níveis próximos às bordas
      // Especialmente importante para resistências no topo do gráfico
      const chartHeight = containerRect.height
      const tolerance = 200 // Aumentado de 100 para 200 pixels
      const isResistance = levelType === 'resistance'
      const resistanceTolerance = isResistance ? 500 : tolerance // 500px para resistências (muito permissivo)
      
      // Verificar se está dentro da área visível (com tolerância maior para resistências)
      // Para resistências, ser muito permissivo - aceitar se estiver dentro de 500px da borda
      if (levelY < -resistanceTolerance || levelY > chartHeight + resistanceTolerance) {
        return false
      }
      
      const distancePixels = Math.abs(cursorY - levelY)
      
      if (distancePixels < thresholdPixels && distancePixels < minDistancePixels) {
        minDistancePixels = distancePixels
        closestLevel = { type: levelType, price: parseFloat(price), label, index }
        return true
              }
            } catch (e) {
      return false
    }
    return false
  }
  
  // Verificar suportes
  if (levels.supports && Array.isArray(levels.supports)) {
    levels.supports.forEach((support, index) => {
      if (support && support > 0 && !isNaN(support)) {
        checkLevel(support, 'support', `S${index + 1}`, index)
      }
    })
  }
  
  // Verificar resistências
  if (levels.resistances && Array.isArray(levels.resistances)) {
    levels.resistances.forEach((resistance, index) => {
      if (resistance && resistance > 0 && !isNaN(resistance)) {
        // Verificar especialmente R3, R4, R5 (índices 2, 3, 4)
        if (index >= 2) {
          // DEBUG: Log específico para R3, R4, R5
          try {
            const levelY = candleSeries.value.priceToCoordinate(resistance)
            console.log(`🔍 [DEBUG] Verificando R${index + 1} (${resistance}):`, {
              levelY,
              cursorY,
              chartHeight: containerRect.height,
              isNull: levelY === null,
              isNaN: isNaN(levelY),
              distance: levelY !== null ? Math.abs(cursorY - levelY) : 'N/A'
            })
          } catch (e) {
            console.warn(`⚠️ Erro ao verificar R${index + 1}:`, e)
          }
        }
        checkLevel(resistance, 'resistance', `R${index + 1}`, index)
      }
    })
  }
          
          activeLevelTooltip.value = closestLevel
          crosshairPosition.value = {
            x: containerRect.left + param.point.x,
            y: containerRect.top + param.point.y
          }
}

// ============================================================================
// CARREGAMENTO DE DADOS
// ============================================================================

/**
 * Carrega dados do gráfico
 */
const loadChartData = async (containerElement = null) => {
  try {
    loading.value = true
    error.value = null
    
    const actualContainer = containerElement || chartContainer.value
    
    // Carregar dados em paralelo
    const [chartDataResponse, analysisResponse] = await Promise.all([
      api.getChartData(props.symbol, props.timeframe, 500),
      marketStore.analyze(props.symbol, props.timeframe).catch(() => null)
    ])
    
    if (chartDataResponse && chartDataResponse.success) {
      chartData.value = chartDataResponse
      
      // Ordenar níveis S/R
      if (chartData.value.levels) {
        chartData.value.levels = sortAndCleanLevels(chartData.value.levels)
      }
      
      if (!chartDataResponse.candles || chartDataResponse.candles.length === 0) {
        error.value = 'Nenhum dado de candle disponível'
        loading.value = false
        return
      }
      
      // Converter candles para formato lightweight-charts
      const candles = chartDataResponse.candles
        .map((c) => {
          let timeValue = c.time || c.timestamp
          if (typeof timeValue === 'number' && timeValue > 1e10) {
            timeValue = Math.floor(timeValue / 1000)
          } else if (typeof timeValue === 'string') {
            timeValue = Math.floor(new Date(timeValue).getTime() / 1000)
          }
          timeValue = Math.floor(Number(timeValue))
          
          return {
            time: timeValue,
            open: Number(c.open),
            high: Math.max(Number(c.open), Number(c.close), Number(c.high)),
            low: Math.min(Number(c.open), Number(c.close), Number(c.low)),
            close: Number(c.close)
          }
        })
        .filter(c => c.time && c.open > 0 && c.high >= Math.max(c.open, c.close) && c.low <= Math.min(c.open, c.close))
        .sort((a, b) => a.time - b.time)
      
      // Converter volume
      const volumes = chartDataResponse.candles
        .map((c, index) => {
          let timeValue = c.time || c.timestamp
          if (typeof timeValue === 'number' && timeValue > 1e10) {
            timeValue = Math.floor(timeValue / 1000)
          }
          return {
            time: timeValue,
            value: parseFloat(c.volume || 0),
            color: parseFloat(c.close) >= parseFloat(c.open) ? '#00ff8840' : '#ff444440'
          }
        })
        .filter(v => v.time && !isNaN(v.value))
      
      // Adicionar dados ao gráfico
      if (candleSeries.value && candles.length > 0) {
          candleSeries.value.setData(candles)
          await nextTick()
          await new Promise(resolve => setTimeout(resolve, 100))
          
        // Ajustar escala
          if (chart.value && candleSeries.value) {
          chart.value.priceScale('right').applyOptions({
              visible: true,
              autoScale: true,
              autoScaleMarginTop: 0.0,
              autoScaleMarginBottom: 0.0
            })
            chart.value.timeScale().fitContent()
        }
      }
      
      if (volumeSeries.value && volumes.length > 0) {
          volumeSeries.value.setData(volumes)
      }
      
      // Adicionar EMAs se disponíveis
      await addEMAs(chartDataResponse)
      
      // Adicionar linhas de níveis
      addLevelLines()
      
      // Atualizar coordenada do preço atual
      updatePriceLinePosition()
      
      // Inicializar activeCandle
      if (chartData.value?.candles && chartData.value.candles.length > 0) {
        const lastCandle = chartData.value.candles[chartData.value.candles.length - 1]
        activeCandle.value = {
              time: lastCandle.time,
          open: lastCandle.open,
          high: lastCandle.high,
          low: lastCandle.low,
          close: lastCandle.close,
          volume: lastCandle.volume || 0
        }
      }
    }
    
    if (analysisResponse) {
      analysisData.value = marketStore.analysisData
      
      // Extrair níveis do analysisData
      if (analysisData.value?.niveis_operacionais && chartData.value) {
        if (!chartData.value.levels) chartData.value.levels = {}
        if (!chartData.value.levels.operational) chartData.value.levels.operational = {}
        
        const niveis = analysisData.value.niveis_operacionais
        if (niveis.entry_price && niveis.entry_price > 0) {
          chartData.value.levels.operational.entry = niveis.entry_price
        }
        if (niveis.stop_loss && niveis.stop_loss > 0) {
          chartData.value.levels.operational.stop_loss = niveis.stop_loss
        }
      }
      
      // Extrair S/R
      if (analysisData.value?.estrutura && chartData.value) {
        if (!chartData.value.levels) chartData.value.levels = {}
        
        if (analysisData.value.estrutura.suportes) {
          chartData.value.levels.supports = analysisData.value.estrutura.suportes
            .map(s => typeof s === 'object' ? s.preco : s)
            .filter(s => s && s > 0)
        }
        
        if (analysisData.value.estrutura.resistencias) {
          chartData.value.levels.resistances = analysisData.value.estrutura.resistencias
            .map(r => typeof r === 'object' ? r.preco : r)
            .filter(r => r && r > 0)
        }
        
        // Ordenar níveis
        if (chartData.value.levels) {
          chartData.value.levels = sortAndCleanLevels(chartData.value.levels)
        }
      }
      
      // Calcular variação de preço
      if (chartData.value?.current_price && analysisData.value?.contexto?.preco_atual) {
        const current = chartData.value.current_price
        const previous = analysisData.value.contexto.preco_atual
        if (previous && previous > 0) {
          priceChange.value = ((current - previous) / previous) * 100
        }
      }
    }
    
    loading.value = false
    
          } catch (err) {
    console.error('❌ Erro ao carregar dados:', err)
    error.value = err.message || 'Erro ao carregar dados do gráfico'
    loading.value = false
  }
}

/**
 * Adiciona EMAs ao gráfico
 */
const addEMAs = async (chartDataResponse) => {
  if (!chartDataResponse.indicators) return
  
  // EMA 8
  if (chartDataResponse.indicators.ema8 && chartDataResponse.indicators.ema8.length > 0) {
    const candles = chartData.value.candles
        const ema8Values = chartDataResponse.indicators.ema8
    const ema8Offset = candles.length - ema8Values.length
        const ema8Data = []
        
        for (let i = 0; i < ema8Values.length; i++) {
          const candleIdx = ema8Offset + i
          if (candleIdx >= 0 && candleIdx < candles.length && candles[candleIdx]) {
            const val = parseFloat(ema8Values[i])
            if (!isNaN(val) && val > 0) {
              ema8Data.push({
                time: candles[candleIdx].time,
                value: val
              })
            }
          }
        }
        
        if (ema8Data.length > 0) {
          if (!ema8Series.value) {
        ema8Series.value = markRaw(chart.value.addLineSeries({
              color: '#00ffff',
              lineWidth: 2,
              title: 'EMA 8',
          priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
          priceScaleId: 'right',
              lastValueVisible: false,
              lineVisible: true
        }))
          }
        if (ema8Series.value && typeof ema8Series.value.setData === 'function') {
          ema8Series.value.setData(ema8Data)
        }
        }
      }
      
  // EMA 21
  if (chartDataResponse.indicators.ema21 && chartDataResponse.indicators.ema21.length > 0) {
    const candles = chartData.value.candles
        const ema21Values = chartDataResponse.indicators.ema21
    const ema21Offset = candles.length - ema21Values.length
        const ema21Data = []
        
        for (let i = 0; i < ema21Values.length; i++) {
          const candleIdx = ema21Offset + i
          if (candleIdx >= 0 && candleIdx < candles.length && candles[candleIdx]) {
            const val = parseFloat(ema21Values[i])
            if (!isNaN(val) && val > 0) {
              ema21Data.push({
                time: candles[candleIdx].time,
                value: val
              })
            }
          }
        }
        
        if (ema21Data.length > 0) {
          if (!ema21Series.value) {
        ema21Series.value = markRaw(chart.value.addLineSeries({
              color: '#ff8c00',
              lineWidth: 2,
              title: 'EMA 21',
          priceFormat: { type: 'price', precision: 2, minMove: 0.01 },
          priceScaleId: 'right',
              lastValueVisible: false,
              lineVisible: true
        }))
          }
        if (ema21Series.value && typeof ema21Series.value.setData === 'function') {
          ema21Series.value.setData(ema21Data)
        }
        }
      }
}

/**
 * Adiciona linhas de níveis S/R
 */
const addLevelLines = () => {
  if (!chart.value || !chartData.value?.levels || !candleSeries.value) return
  
  // Remover linhas anteriores
  levelLines.value.forEach(line => {
    try {
      chart.value.removePriceLine(line)
    } catch (e) {
      // Ignorar
    }
  })
  levelLines.value = []
  
  const levels = sortAndCleanLevels({
    ...chartData.value.levels,
    supports: chartData.value.levels.supports ? [...chartData.value.levels.supports] : undefined,
    resistances: chartData.value.levels.resistances ? [...chartData.value.levels.resistances] : undefined
  })
  
  // Suportes
  if (levels.supports) {
    levels.supports.forEach((support) => {
      if (support) {
        const line = candleSeries.value.createPriceLine({
          price: support,
          color: '#26a69a',
          lineWidth: 1,
          lineStyle: 1,
          axisLabelVisible: false
        })
        levelLines.value.push(line)
      }
    })
        }
        
        // Resistências
  if (levels.resistances) {
    levels.resistances.forEach((resistance) => {
      if (resistance) {
        const line = candleSeries.value.createPriceLine({
          price: resistance,
          color: '#ef5350',
          lineWidth: 1,
          lineStyle: 1,
          axisLabelVisible: false
        })
        levelLines.value.push(line)
      }
    })
  }
}

// ============================================================================
// POLLING
// ============================================================================

/**
 * Inicia polling para atualização em tempo real
 */
const startPolling = () => {
  if (!chart.value || !candleSeries.value || !chartData.value) {
    console.warn('⚠️ Polling não pode iniciar: gráfico não está pronto')
    // Tentar novamente após um delay
    setTimeout(() => {
      if (chart.value && candleSeries.value && chartData.value) {
        startPolling()
      }
    }, 2000)
    return
  }
  
  if (isPollingActive.value) {
    console.log('⚠️ Polling já está ativo')
    return
  }
  
  console.log('🔄 Iniciando polling para atualização de ticks...')
  isPollingActive.value = true
  pollingErrorCount.value = 0
  pollingBackoffDelay.value = 0
  
  if (pollingBackoffTimeout.value) {
    clearTimeout(pollingBackoffTimeout.value)
    pollingBackoffTimeout.value = null
  }
  
  const interval = basePollingInterval
  
  // Primeira atualização imediata
  setTimeout(() => {
    if (isPollingActive.value && chart.value && candleSeries.value && chartData.value) {
      pollLastPrice()
    }
  }, 1000)
  
  // Polling contínuo
  pollingInterval.value = setInterval(() => {
    if (isPollingActive.value && chart.value && candleSeries.value && chartData.value) {
      pollLastPrice()
    }
  }, interval)
  
  console.log(`✅ Polling ativo - atualizando a cada ${interval / 1000}s`)
}

/**
 * Busca último preço e atualiza gráfico
 */
const pollLastPrice = async () => {
  if (!chart.value || !candleSeries.value || !chartData.value) return
  
  try {
    const response = await api.getLastPrice(props.symbol, props.timeframe)
    
    if (response && response.success && response.candle) {
      const newCandle = response.candle
      const lastCandle = chartData.value.candles[chartData.value.candles.length - 1]
      
      if (!lastCandle) return
      
      if (newCandle.time === lastCandle.time) {
        // Mesmo candle - atualizar
        if (candleSeries.value && typeof candleSeries.value.update === 'function') {
          candleSeries.value.update({
                time: newCandle.time,
                open: newCandle.open,
                high: newCandle.high,
                low: newCandle.low,
                close: newCandle.close
              })
        }
        
        if (volumeSeries.value && newCandle.volume && typeof volumeSeries.value.update === 'function') {
          volumeSeries.value.update({
                time: newCandle.time,
                value: newCandle.volume,
                color: newCandle.close >= newCandle.open ? '#00ff88' : '#ff4444'
              })
        }
        
        const candleIndex = chartData.value.candles.length - 1
        chartData.value.candles[candleIndex] = { ...newCandle }
      } else {
        // Novo candle - adicionar
        if (candleSeries.value && typeof candleSeries.value.update === 'function') {
          candleSeries.value.update({
                time: newCandle.time,
                open: newCandle.open,
                high: newCandle.high,
                low: newCandle.low,
                close: newCandle.close
              })
        }
        
        if (volumeSeries.value && newCandle.volume && typeof volumeSeries.value.update === 'function') {
          volumeSeries.value.update({
                time: newCandle.time,
                value: newCandle.volume,
                color: newCandle.close >= newCandle.open ? '#00ff88' : '#ff4444'
              })
        }
        
        chartData.value.candles.push(newCandle)
      }
      
      // Atualizar preço atual
      if (response.current_price) {
        chartData.value.current_price = response.current_price
      }
      
      // FORÇAR ATUALIZAÇÃO DO TIMESCALE PARA ATUALIZAR OS TICKS
      if (chart.value && chart.value.timeScale) {
        try {
          // Forçar recálculo do timeScale para atualizar os ticks
          const timeScale = chart.value.timeScale()
          if (timeScale) {
            // Obter range visível atual
            const visibleRange = timeScale.getVisibleRange()
            
            // Se o usuário está visualizando o final do gráfico, manter scroll no final
            if (visibleRange && visibleRange.to) {
              const isAtEnd = visibleRange.to >= lastCandle.time - 120 // 2 minutos de margem
              if (isAtEnd) {
                // Scroll para o novo candle (mantém no final)
                timeScale.scrollToPosition(-1, false) // -1 = scroll para o final
              }
            }
            
            // Forçar atualização visual do timeScale (isso atualiza os ticks)
            // Aplicar opções novamente para forçar redraw
            timeScale.applyOptions({
              timeVisible: true,
              secondsVisible: false
            })
          }
        } catch (e) {
          console.warn('⚠️ Erro ao atualizar timeScale:', e)
        }
      }
      
      updatePriceLinePosition()
      
      // Atualizar activeCandle se necessário
      if (!activeCandle.value || activeCandle.value.time === lastCandle.time) {
        activeCandle.value = {
          time: newCandle.time,
          open: newCandle.open,
          high: newCandle.high,
          low: newCandle.low,
          close: newCandle.close,
          volume: newCandle.volume || 0
        }
      }
    }
    
    // Reset contador de erros após sucesso
    if (pollingErrorCount.value > 0) {
      pollingErrorCount.value = Math.max(0, pollingErrorCount.value - 1)
      pollingBackoffDelay.value = 0
    }
    
  } catch (err) {
    const isRateLimitError = err.response?.status === 429 || err.message?.includes('429')
    
    if (isRateLimitError) {
      pollingErrorCount.value++
      const backoffMultiplier = Math.min(Math.pow(2, pollingErrorCount.value - 1), 12)
      pollingBackoffDelay.value = basePollingInterval * backoffMultiplier
      
      console.warn(`⏳ [POLL] Rate limit (429). Backoff: ${pollingBackoffDelay.value / 1000}s`)
      
      if (!pollingBackoffTimeout.value) {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
        }
        
        pollingBackoffTimeout.value = setTimeout(() => {
          pollingBackoffTimeout.value = null
          if (isPollingActive.value && chart.value && candleSeries.value && chartData.value) {
            pollingErrorCount.value = Math.max(0, pollingErrorCount.value - 1)
            pollingBackoffDelay.value = 0
            
            const interval = basePollingInterval
            pollingInterval.value = setInterval(() => {
              if (isPollingActive.value) {
                pollLastPrice()
              }
            }, interval)
          }
        }, pollingBackoffDelay.value)
      }
    } else {
      console.error('❌ [POLL] Erro:', err)
      pollingErrorCount.value = 0
      pollingBackoffDelay.value = 0
    }
  }
}

/**
 * Para o polling
 */
const stopPolling = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
  if (pollingBackoffTimeout.value) {
    clearTimeout(pollingBackoffTimeout.value)
    pollingBackoffTimeout.value = null
  }
  isPollingActive.value = false
  pollingErrorCount.value = 0
  pollingBackoffDelay.value = 0
}

// ============================================================================
// CONTROLES
// ============================================================================

const zoomIn = () => {
  if (chart.value) {
    chart.value.timeScale().scrollToPosition(-5, false)
    zoomLevel.value = Math.min(200, zoomLevel.value + 10)
  }
}

const zoomOut = () => {
  if (chart.value) {
    chart.value.timeScale().scrollToPosition(5, false)
    zoomLevel.value = Math.max(50, zoomLevel.value - 10)
  }
}

const refreshChart = () => {
  if (chart.value && chartContainer.value) {
    loadChartData(chartContainer.value)
  } else {
    initChart()
  }
}

const handleResize = () => {
  if (chart.value && chartContainer.value) {
    chart.value.applyOptions({
      width: chartContainer.value.clientWidth
    })
    updatePriceLinePosition()
  }
}

// ============================================================================
// WATCHERS E LIFECYCLE
// ============================================================================

watch([() => props.symbol, () => props.timeframe], async () => {
  stopPolling()
  chartData.value = null
  analysisData.value = null
  cursorPrice.value = null
  isMouseOverChart.value = false
  activeCandle.value = null
  activeLevelTooltip.value = null
  
  if (chart.value) {
    try {
      if (candleSeries.value) {
        chart.value.removeSeries(candleSeries.value)
        candleSeries.value = null
      }
      if (volumeSeries.value) {
        chart.value.removeSeries(volumeSeries.value)
        volumeSeries.value = null
      }
      if (ema8Series.value) {
        chart.value.removeSeries(ema8Series.value)
        ema8Series.value = null
      }
      if (ema21Series.value) {
        chart.value.removeSeries(ema21Series.value)
        ema21Series.value = null
      }
      
      levelLines.value.forEach(line => {
        try {
          chart.value.removePriceLine(line)
        } catch (e) {}
      })
      levelLines.value = []
      
      chart.value.remove()
      chart.value = null
    } catch (e) {
      console.warn('⚠️ Erro ao limpar gráfico:', e)
    }
  }
  
  if (chartContainer.value) {
    while (chartContainer.value.firstChild) {
      chartContainer.value.removeChild(chartContainer.value.firstChild)
      }
  }
  
  if (chartContainer.value) {
    await initChart()
  }
})

onMounted(async () => {
  await nextTick()
  await new Promise(resolve => setTimeout(resolve, 100))
  await initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  stopPolling()
  if (chart.value) {
    try {
      chart.value.remove()
    } catch (e) {}
    chart.value = null
  }
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

/* Sandbox: Container principal */
.chart-sandbox {
  position: relative;
  width: 100%;
  height: 600px;
  min-height: 600px;
  padding: 0 !important;
  margin: 0 !important;
  box-sizing: border-box;
  overflow: hidden;
  background: #0a0a0a;
  border-radius: 4px;
  border: 1px solid rgba(0, 255, 136, 0.3);
  isolation: isolate;
}

/* Container do gráfico: DEVE receber eventos */
.chart-container-absolute {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  background: transparent !important;
  overflow: hidden;
  z-index: 1 !important;
  pointer-events: auto !important; /* CRÍTICO: Recebe eventos do mouse */
}

/* Canvas deve receber eventos */
.chart-container-absolute :deep(canvas),
.chart-container-absolute :deep(.tv-lightweight-charts canvas) {
  pointer-events: auto !important;
  z-index: 1 !important;
}

/* Overlays: NÃO bloqueiam eventos */
.chart-overlays-absolute {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  pointer-events: none !important; /* CRÍTICO: Não bloqueia eventos */
  z-index: 2000 !important;
  padding: 0 !important;
  margin: 0 !important;
  box-sizing: border-box !important;
}

.chart-overlays-absolute > * {
  pointer-events: none !important;
}

/* Loading Overlay */
.chart-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 10, 10, 0.3);
  backdrop-filter: blur(2px);
}

.loading-spinner-center {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

/* Error Overlay */
.chart-error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(4px);
}

/* Linha do preço atual */
.current-price-line {
  position: absolute;
  left: 0;
  width: 100%;
  pointer-events: none !important;
  z-index: 1001;
}

.current-price-line-bar {
  position: absolute;
  left: 0;
  width: 100%;
  height: 1px;
  background: #00ff88;
  opacity: 0.8;
  z-index: 1;
}

.current-price-label {
  position: absolute;
  left: 0;
  top: -10px;
  background: rgba(0, 255, 136, 0.9);
  color: #000;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: bold;
  border-radius: 2px;
  white-space: nowrap;
  pointer-events: none !important;
}

.label-text {
  font-weight: bold;
}

.label-price {
  font-size: 9px;
  opacity: 0.9;
}

/* Indicador de preço no cursor */
.cursor-price-indicator {
  position: absolute;
  pointer-events: none !important;
  z-index: 3000;
  transform: translateX(-100%); /* Posiciona à esquerda do cursor */
}

.cursor-price-badge {
  background: rgba(0, 255, 136, 0.9);
  color: #000;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  font-family: 'Courier New', monospace;
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.5);
  white-space: nowrap;
}
</style>

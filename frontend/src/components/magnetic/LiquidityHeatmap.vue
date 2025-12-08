<template>
  <div class="liquidity-heatmap">
    <div v-if="loading" class="loading-overlay">
      <LoadingSpinner />
      <p class="text-terminal-green/70 mt-4">Carregando liquidez...</p>
    </div>
    
    <div v-else-if="error" class="error-message">
      <div class="text-red-500 mb-4">{{ error }}</div>
      <button 
        @click="loadData"
        class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80"
      >
        Tentar Novamente
      </button>
    </div>
    
    <div v-else class="heatmap-container">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold mb-2">Liquidity Heatmap</h1>
        <p class="text-terminal-green/70">Mapa de calor de liquidez - Order Book Depth</p>
      </div>
      
      <!-- Controles - Uma linha compacta (mesma lógica de /analysis) -->
      <div class="card mb-4">
        <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
          <div class="flex-1 w-full sm:w-auto">
            <SymbolAutocomplete
              v-model="selectedSymbol" 
              placeholder="Digite 3 letras (ex: BTC, ETH)..."
              @select="handleSymbolSelect"
            />
          </div>
          <div class="flex-shrink-0">
            <BinSizeSelector
              v-model="binSize" 
              @change="handleBinSizeChange"
            />
          </div>
          <div class="flex-shrink-0">
            <PrecisionSelector
              v-model="precision" 
              @change="handlePrecisionChange"
            />
          </div>
          <label class="flex items-center gap-2 text-sm text-terminal-green/70 cursor-pointer flex-shrink-0">
            <input 
              type="checkbox" 
              v-model="showSR"
              @change="loadSRData"
              class="w-4 h-4 rounded border-terminal-green/50 bg-terminal-dark text-terminal-green focus:ring-terminal-green"
            />
            <span>S/R</span>
          </label>
          <button 
            @click="loadData" 
            class="btn-primary flex-shrink-0"
            :disabled="loading"
          >
            {{ loading ? 'Carregando...' : '🔄 Atualizar' }}
          </button>
        </div>
      </div>
      
      <!-- Estatísticas -->
      <div v-if="data" class="stats mb-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="stat-card">
          <div class="stat-label">Preço Atual</div>
          <div class="stat-value">${{ formatPrice(data.current_price) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Spread</div>
          <div class="stat-value">{{ data.spread_pct?.toFixed(4) || '0' }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Liquidez Ratio</div>
          <div class="stat-value" :class="getRatioColor(data.statistics?.liquidity_ratio)">
            {{ data.statistics?.liquidity_ratio?.toFixed(2) || '1.00' }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Muros</div>
          <div class="stat-value">
            🟢 {{ data.statistics?.bid_walls_count || 0 }} | 
            🔴 {{ data.statistics?.ask_walls_count || 0 }}
          </div>
        </div>
      </div>
      
      <!-- Canvas do Heatmap -->
      <div class="heatmap-wrapper">
        <canvas
          ref="canvasRef"
          :width="canvasWidth"
          :height="canvasHeight"
          class="heatmap-canvas"
          style="max-width: 100%; height: auto;"
          @mousemove="handleMouseMove"
          @mouseleave="handleMouseLeave"
        ></canvas>
        
        <!-- Tooltip -->
        <div
          v-if="tooltipData"
          class="heatmap-tooltip"
          :style="{
            left: tooltipPosition.x + 'px',
            top: tooltipPosition.y + 'px'
          }"
        >
          <div class="tooltip-header">
            <span class="font-bold">
              <span v-if="tooltipData.isSR">
                {{ tooltipData.srType === 'support' ? '🔵 SUPORTE' : '🔴 RESISTÊNCIA' }}
              </span>
              <span v-else>
                {{ tooltipData.type === 'bid' ? '🟢 BID' : tooltipData.type === 'ask' ? '🔴 ASK' : '📊 ZONA' }}
              </span>
            </span>
          </div>
          <div class="tooltip-content">
            <div class="tooltip-row">
              <span>Preço:</span>
              <span class="font-bold">${{ formatPrice(tooltipData.price) }}</span>
            </div>
            <div v-if="tooltipData.isSR" class="tooltip-section mt-2 pt-2 border-t border-terminal-green/30">
              <div class="tooltip-row">
                <span>Nível:</span>
                <span class="font-bold">
                  {{ tooltipData.srType === 'support' ? `S${tooltipData.srIndex + 1}` : `R${tooltipData.srIndex + 1}` }}
                </span>
              </div>
              <div class="tooltip-row">
                <span>Tipo:</span>
                <span>{{ tooltipData.srType === 'support' ? 'Suporte Matemático' : 'Resistência Matemática' }}</span>
              </div>
              <div v-if="tooltipData.zoneIntensity" class="tooltip-row">
                <span>🌡️ Temperatura da Zona:</span>
                <span class="font-bold">{{ getTemperatureLabel(tooltipData.zoneIntensity) }}</span>
              </div>
            </div>
            <div v-if="!tooltipData.isSR && !tooltipData.isZone" class="tooltip-row">
              <span>Quantidade Total:</span>
              <span class="font-bold">{{ formatQty(tooltipData.total_qty) }}</span>
            </div>
            <div v-if="!tooltipData.isSR && !tooltipData.isZone" class="tooltip-row">
              <span>Ordens:</span>
              <span>{{ tooltipData.order_count || '--' }}</span>
            </div>
            <div v-if="!tooltipData.isSR" class="tooltip-row">
              <span>Intensidade:</span>
              <span>{{ (tooltipData.intensity * 100).toFixed(1) }}%</span>
            </div>
            <div v-if="tooltipData.isZone && !tooltipData.isSR" class="tooltip-section mt-2 pt-2 border-t border-terminal-green/30">
              <div class="tooltip-row">
                <span>🌡️ Temperatura da Zona:</span>
                <span class="font-bold">{{ getTemperatureLabel(tooltipData.zoneIntensity) }}</span>
              </div>
              <div class="tooltip-row">
                <span>🟢 BID Intensity:</span>
                <span>{{ (tooltipData.zoneBidIntensity * 100).toFixed(1) }}%</span>
              </div>
              <div class="tooltip-row">
                <span>🔴 ASK Intensity:</span>
                <span>{{ (tooltipData.zoneAskIntensity * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div v-if="tooltipData.total_qty >= (data?.statistics?.max_qty * 0.1)" class="tooltip-warning">
              ⚠️ MURO DE LIQUIDEZ
            </div>
          </div>
        </div>
      </div>
      
      <!-- Legenda -->
      <div class="legend mt-4">
        <div class="legend-title">Legenda</div>
        <div class="legend-items">
          <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(to right, #ffff00, #ffffff);"></div>
            <span>Alta Liquidez (Muro)</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #00ff00;"></div>
            <span>Liquidez Média</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: #0a0a0a;"></div>
            <span>Baixa Liquidez (Vácuo)</span>
          </div>
          <div class="legend-item">
            <div class="legend-line" style="border-top: 2px solid #00ff00;"></div>
            <span>Preço Atual</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import SymbolAutocomplete from '@/components/common/SymbolAutocomplete.vue'
import BinSizeSelector from '@/components/common/BinSizeSelector.vue'
import PrecisionSelector from '@/components/common/PrecisionSelector.vue'
import api from '@/services/api'

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  }
})

const canvasRef = ref(null)
const loading = ref(false)
const error = ref(null)
const data = ref(null)
const tooltipData = ref(null)
const tooltipPosition = ref({ x: 0, y: 0 })
const hoveredLevel = ref(null) // Nível sendo hovered
const hoveredSR = ref(null) // Linha S/R sendo hovered { type: 'support'|'resistance', price: number, index: number }
const selectedSymbol = ref(props.symbol || 'BTCUSDT')
const precision = ref('2')
const binSize = ref('100') // Bin padrão de $100
const autoRefresh = ref(false) // Desabilitado por padrão
const refreshInterval = ref(null)
const showSR = ref(true) // Mostrar S/R por padrão
const srData = ref(null) // Dados de suportes/resistências

// Canvas dimensions (responsivo)
const canvasWidth = ref(1000)
const canvasHeight = ref(700)

// Handlers para mudanças
const handleSymbolSelect = (symbol) => {
  selectedSymbol.value = symbol.symbol || symbol
  loadData()
}

const handleBinSizeChange = (value) => {
  binSize.value = value
  loadData()
}

const handlePrecisionChange = (value) => {
  precision.value = value
  loadData()
}

// Load S/R data
const loadSRData = async () => {
  if (!showSR.value) {
    srData.value = null
    if (data.value) {
      nextTick(() => drawHeatmap())
    }
    return
  }
  
  try {
    const response = await api.analyze(selectedSymbol.value, '1h')
    console.log('📊 Resposta completa da análise:', response)
    
    if (response && response.estrutura) {
      // Extrair suportes e resistências do formato do sistema
      let suportes = []
      let resistencias = []
      
      // Formato 1: estrutura.suportes e estrutura.resistencias (arrays de objetos com .preco)
      if (response.estrutura.suportes && Array.isArray(response.estrutura.suportes)) {
        suportes = response.estrutura.suportes.map(s => {
          if (typeof s === 'object' && s.preco) return s.preco
          if (typeof s === 'number') return s
          return null
        }).filter(s => s !== null)
      }
      
      if (response.estrutura.resistencias && Array.isArray(response.estrutura.resistencias)) {
        resistencias = response.estrutura.resistencias.map(r => {
          if (typeof r === 'object' && r.preco) return r.preco
          if (typeof r === 'number') return r
          return null
        }).filter(r => r !== null)
      }
      
      srData.value = {
        suportes: suportes,
        resistencias: resistencias
      }
      console.log('✅ Dados S/R carregados:', srData.value)
      if (data.value) {
        nextTick(() => drawHeatmap())
      }
    } else {
      console.warn('⚠️ Estrutura não encontrada na resposta')
      srData.value = null
    }
  } catch (err) {
    console.warn('⚠️ Erro ao carregar S/R:', err)
    srData.value = null
  }
}

// Apply binning to levels
const applyBinning = (levels, binSizeValue) => {
  if (!binSizeValue || binSizeValue === '0' || !levels || levels.length === 0) {
    return levels
  }
  
  const bin = parseFloat(binSizeValue)
  const binned = {}
  
  levels.forEach(level => {
    // Arredondar preço para o bin mais próximo
    const binnedPrice = Math.round(level.price / bin) * bin
    
    if (!binned[binnedPrice]) {
      binned[binnedPrice] = {
        price: binnedPrice,
        total_qty: 0,
        order_count: 0
      }
    }
    
    binned[binnedPrice].total_qty += level.total_qty || 0
    binned[binnedPrice].order_count += level.order_count || 1
  })
  
  return Object.values(binned)
}

// Load data
const loadData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await api.getLiquidityHeatmap(
      selectedSymbol.value,
      5000,
      parseInt(precision.value)
    )
    
    if (response.success) {
      // Aplicar binning se necessário
      const binSizeValue = binSize.value
      let processedBids = response.bid_levels || []
      let processedAsks = response.ask_levels || []
      
      if (binSizeValue && binSizeValue !== '0') {
        processedBids = applyBinning(processedBids, binSizeValue)
        processedAsks = applyBinning(processedAsks, binSizeValue)
        console.log(`📦 Binning aplicado (${binSizeValue}):`, {
          bids: processedBids.length,
          asks: processedAsks.length
        })
      }
      
      // Recalcular intensidades após binning
      const allQuantities = [
        ...processedBids.map(l => l.total_qty),
        ...processedAsks.map(l => l.total_qty)
      ]
      const maxQty = Math.max(...allQuantities, 1)
      
      processedBids = processedBids.map(level => ({
        ...level,
        intensity: level.total_qty / maxQty
      }))
      
      processedAsks = processedAsks.map(level => ({
        ...level,
        intensity: level.total_qty / maxQty
      }))
      
      data.value = {
        ...response,
        bid_levels: processedBids,
        ask_levels: processedAsks,
        statistics: {
          ...response.statistics,
          max_qty: maxQty
        }
      }
      
      console.log('✅ Dados de liquidez carregados:', {
        bids: processedBids.length,
        asks: processedAsks.length,
        current_price: response.current_price,
        max_qty: maxQty
      })
      
      // Carregar S/R se estiver ativado
      if (showSR.value) {
        await loadSRData()
      }
      
      // O watch vai redesenhar automaticamente quando data.value mudar
      // Mas vamos tentar desenhar agora também
      await nextTick()
      
      if (canvasRef.value) {
        drawHeatmap()
      } else {
        console.warn('⚠️ Canvas não disponível, aguardando...')
        // Tentar novamente após um delay
        setTimeout(() => {
          if (canvasRef.value && data.value) {
            drawHeatmap()
          }
        }, 300)
      }
    } else {
      error.value = response.error || 'Erro ao carregar dados'
    }
  } catch (err) {
    console.error('Erro ao carregar liquidez:', err)
    error.value = err.message || 'Erro ao carregar dados'
  } finally {
    loading.value = false
  }
}

// Draw heatmap
const drawHeatmap = () => {
  const canvas = canvasRef.value
  if (!canvas) {
    console.warn('⚠️ Canvas não disponível')
    return
  }
  
  if (!data.value) {
    console.warn('⚠️ Dados não disponíveis')
    return
  }
  
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    console.error('❌ Não foi possível obter contexto 2D do canvas')
    return
  }
  
  const width = canvasWidth.value
  const height = canvasHeight.value
  
  console.log('🎨 Desenhando heatmap:', { 
    width, 
    height, 
    canvas_exists: !!canvas,
    data_exists: !!data.value,
    bid_levels: data.value.bid_levels?.length || 0,
    ask_levels: data.value.ask_levels?.length || 0
  })
  
  // Clear canvas
  ctx.clearRect(0, 0, width, height)
  
  // Extrair dados primeiro
  const { bid_levels, ask_levels, current_price, statistics } = data.value
  
  if (!bid_levels || !ask_levels || !current_price) {
    console.warn('⚠️ Dados incompletos:', { bid_levels: !!bid_levels, ask_levels: !!ask_levels, current_price })
    return
  }
  
  // Calcular range de preços
  const all_prices = [
    ...bid_levels.map(l => l.price),
    ...ask_levels.map(l => l.price)
  ]
  const min_price = Math.min(...all_prices)
  const max_price = Math.max(...all_prices)
  const price_range = max_price - min_price || 1
  
  // Margens (declarar ANTES de usar)
  const margin_top = 40
  const margin_bottom = 40
  const histogram_width = 60 // Largura do histograma lateral
  const margin_left = 80 + histogram_width // Espaço extra para histograma
  const margin_right = 80
  const chart_height = height - margin_top - margin_bottom
  const chart_width = width - margin_left - margin_right
  
  console.log('📊 Desenhando:', {
    bids: bid_levels.length,
    asks: ask_levels.length,
    current_price,
    price_range: `${min_price} - ${max_price}`,
    chart_dimensions: { width: chart_width, height: chart_height }
  })
  
  // Background preto base
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, width, height)
  
  // Calcular intensidade total por nível de preço (para degradê de fundo)
  const priceIntensityMap = {}
  const allLevelsForGradient = [
    ...bid_levels.map(l => ({ ...l, type: 'bid' })),
    ...ask_levels.map(l => ({ ...l, type: 'ask' }))
  ]
  
  allLevelsForGradient.forEach(level => {
    const priceKey = Math.round(level.price * 100) / 100 // Arredondar para evitar duplicatas
    if (!priceIntensityMap[priceKey]) {
      priceIntensityMap[priceKey] = { bid: 0, ask: 0 }
    }
    if (level.type === 'bid') {
      priceIntensityMap[priceKey].bid += level.intensity || 0
    } else {
      priceIntensityMap[priceKey].ask += level.intensity || 0
    }
  })
  
  // Encontrar máxima intensidade para normalização
  const maxIntensity = Math.max(
    ...Object.values(priceIntensityMap).map(p => Math.max(p.bid, p.ask)),
    1
  )
  
  // Desenhar degradê de fundo por zonas
  const gradientStep = 2 // Resolução do degradê (pixels)
  for (let y = margin_top; y <= margin_top + chart_height; y += gradientStep) {
    // Converter Y para preço
    const normalizedY = (y - margin_top) / chart_height
    const price = max_price - (normalizedY * price_range)
    
    // Encontrar intensidade mais próxima para este preço
    let closestIntensity = { bid: 0, ask: 0 }
    let minDistance = Infinity
    
    Object.keys(priceIntensityMap).forEach(priceKey => {
      const distance = Math.abs(parseFloat(priceKey) - price)
      if (distance < minDistance) {
        minDistance = distance
        const intensities = priceIntensityMap[priceKey]
        closestIntensity = {
          bid: intensities.bid / maxIntensity,
          ask: intensities.ask / maxIntensity
        }
      }
    })
    
    // Calcular cor do degradê baseado na intensidade
    const totalIntensity = Math.max(closestIntensity.bid, closestIntensity.ask)
    const dominantType = closestIntensity.bid > closestIntensity.ask ? 'bid' : 'ask'
    
    // SEMPRE desenhar degradê (mesmo com intensidade muito baixa)
    // Aplicar gamma correction para suavizar
    const gammaIntensity = Math.pow(Math.max(0.01, totalIntensity), 1.2) // Gamma mais suave
    
    // Calcular cor do degradê
    let gradientColor
    if (dominantType === 'bid') {
      // Verde → Ciano
      if (gammaIntensity < 0.3) {
        const factor = gammaIntensity / 0.3
        const g = Math.floor(15 + factor * 85) // Verde escuro mais visível
        const b = Math.floor(factor * 50)
        // Opacidade mínima de 0.15 para garantir que nada fique preto
        const opacity = Math.max(0.15, gammaIntensity * 0.5)
        gradientColor = `rgba(0, ${g}, ${b}, ${opacity})`
      } else if (gammaIntensity < 0.6) {
        const factor = (gammaIntensity - 0.3) / 0.3
        const g = Math.floor(100 + factor * 155) // Verde médio mais brilhante
        const b = Math.floor(50 + factor * 205)
        const opacity = Math.max(0.2, gammaIntensity * 0.6)
        gradientColor = `rgba(0, ${g}, ${b}, ${opacity})`
      } else {
        const factor = (gammaIntensity - 0.6) / 0.4
        const g = 255
        const b = 255
        const r = Math.floor(factor * 50)
        const opacity = Math.max(0.3, gammaIntensity * 0.7)
        gradientColor = `rgba(${r}, ${g}, ${b}, ${opacity})` // Ciano mais visível
      }
    } else {
      // Vermelho → Amarelo Ouro
      if (gammaIntensity < 0.3) {
        const factor = gammaIntensity / 0.3
        const r = Math.floor(15 + factor * 105) // Vermelho escuro mais visível
        // Opacidade mínima de 0.15 para garantir que nada fique preto
        const opacity = Math.max(0.15, gammaIntensity * 0.5)
        gradientColor = `rgba(${r}, 0, 0, ${opacity})`
      } else if (gammaIntensity < 0.6) {
        const factor = (gammaIntensity - 0.3) / 0.3
        const r = Math.floor(120 + factor * 135) // Vermelho médio mais brilhante
        const g = Math.floor(factor * 40)
        const opacity = Math.max(0.2, gammaIntensity * 0.6)
        gradientColor = `rgba(${r}, ${g}, 0, ${opacity})`
      } else {
        const factor = (gammaIntensity - 0.6) / 0.4
        const r = 255
        const g = Math.floor(200 + factor * 55) // Amarelo ouro mais brilhante
        const b = Math.floor(factor * 80)
        const opacity = Math.max(0.3, gammaIntensity * 0.7)
        gradientColor = `rgba(${r}, ${g}, ${b}, ${opacity})` // Mais visível
      }
    }
    
    // Desenhar linha do degradê (sempre, mesmo com intensidade baixa)
    ctx.fillStyle = gradientColor
    ctx.fillRect(margin_left, y, chart_width, gradientStep)
  }
  
  // Grid de fundo sutil (sobre o degradê)
  ctx.strokeStyle = '#00ff0010'
  ctx.lineWidth = 1
  for (let i = 0; i <= 10; i++) {
    const y = margin_top + (chart_height / 10) * i
    ctx.beginPath()
    ctx.moveTo(margin_left, y)
    ctx.lineTo(margin_left + chart_width, y)
    ctx.stroke()
  }
  
  // Função para converter preço em Y
  const priceToY = (price) => {
    const normalized = (price - min_price) / price_range
    return margin_top + chart_height * (1 - normalized) // Invertido (preço alto = topo)
  }
  
  // Calcular máximo de intensidade para normalização logarítmica
  const allIntensities = [
    ...bid_levels.map(l => l.intensity || 0),
    ...ask_levels.map(l => l.intensity || 0)
  ]
  const maxIntensityForNormalization = Math.max(...allIntensities, 1)
  
  // Função para normalização logarítmica
  const normalizeLog = (intensity) => {
    if (intensity <= 0 || maxIntensityForNormalization <= 0) return 0
    // Normalização logarítmica: log(1 + x) / log(1 + max)
    const normalized = Math.log(1 + (intensity / maxIntensityForNormalization) * 9) / Math.log(10)
    return Math.max(0, Math.min(1, normalized))
  }
  
  // Gamma Correction: curva exponencial agressiva para destacar apenas muros gigantes
  const applyGamma = (normalized, gamma = 2.5) => {
    // Gamma > 1 faz com que valores baixos desapareçam mais rápido
    return Math.pow(normalized, gamma)
  }
  
  // Função para converter intensidade em cor com opacidade dinâmica (RGBA + Glow)
  const intensityToColor = (intensity, type) => {
    // Aplicar normalização logarítmica
    const logNormalized = normalizeLog(intensity)
    
    // Aplicar Gamma Correction (curva exponencial agressiva)
    const gammaCorrected = applyGamma(logNormalized, 2.5)
    
    // Calcular opacidade baseada na intensidade (mínimo 0.2 para garantir visibilidade - nada em preto)
    const alpha = Math.max(0.2, gammaCorrected * 0.7 + 0.3)
    
    // Cores base para heatmap térmico
    // Bids: Verde -> Ciano -> Branco (quente)
    // Asks: Vermelho -> Laranja -> Amarelo -> Branco (quente)
    
    if (type === 'bid') {
      // Bids: Verde escuro (baixa) -> Ciano (média) -> Branco (alta)
      if (gammaCorrected < 0.3) {
        // Verde escuro com opacidade baixa
        const brightness = Math.floor(50 + gammaCorrected * 100) // 50 -> 150
        return {
          color: `rgba(0, ${brightness}, ${Math.floor(brightness * 0.5)}, ${alpha})`,
          glow: `rgba(0, ${brightness}, ${Math.floor(brightness * 0.5)}, ${alpha * 0.5})`
        }
      } else if (gammaCorrected < 0.6) {
        // Ciano médio
        const factor = (gammaCorrected - 0.3) / 0.3
        const r = Math.floor(factor * 100)
        const g = 255
        const b = 255
        return {
          color: `rgba(${r}, ${g}, ${b}, ${alpha})`,
          glow: `rgba(${r}, ${g}, ${b}, ${alpha * 0.6})`
        }
      } else {
        // Branco brilhante (muros)
        const brightness = Math.floor(200 + (gammaCorrected - 0.6) * 55) // 200 -> 255
        return {
          color: `rgba(${brightness}, ${brightness}, ${brightness}, ${alpha})`,
          glow: `rgba(${brightness}, ${brightness}, ${brightness}, ${alpha * 0.8})`
        }
      }
    } else {
      // Asks: Vermelho escuro (baixa) -> Laranja (média) -> Amarelo (alta) -> Branco (muro)
      if (gammaCorrected < 0.3) {
        // Vermelho escuro com opacidade baixa
        const brightness = Math.floor(50 + gammaCorrected * 100) // 50 -> 150
        return {
          color: `rgba(${brightness}, 0, 0, ${alpha})`,
          glow: `rgba(${brightness}, 0, 0, ${alpha * 0.5})`
        }
      } else if (gammaCorrected < 0.5) {
        // Laranja
        const factor = (gammaCorrected - 0.3) / 0.2
        const r = 255
        const g = Math.floor(150 + factor * 105) // 150 -> 255
        const b = 0
        return {
          color: `rgba(${r}, ${g}, ${b}, ${alpha})`,
          glow: `rgba(${r}, ${g}, ${b}, ${alpha * 0.6})`
        }
      } else if (gammaCorrected < 0.7) {
        // Amarelo brilhante
        const factor = (gammaCorrected - 0.5) / 0.2
        const r = 255
        const g = 255
        const b = Math.floor(factor * 150) // 0 -> 150
        return {
          color: `rgba(${r}, ${g}, ${b}, ${alpha})`,
          glow: `rgba(${r}, ${g}, ${b}, ${alpha * 0.7})`
        }
      } else {
        // Branco brilhante (muros)
        const brightness = Math.floor(200 + (gammaCorrected - 0.7) * 55) // 200 -> 255
        return {
          color: `rgba(${brightness}, ${brightness}, ${brightness}, ${alpha})`,
          glow: `rgba(${brightness}, ${brightness}, ${brightness}, ${alpha * 0.8})`
        }
      }
    }
  }
  
  // Desenhar TODOS os níveis de liquidez (sem limite para mostrar todas as ordens)
  // Ordenar por preço para manter ordem visual, mas mostrar todos
  const sortedBids = [...bid_levels].sort((a, b) => a.price - b.price) // Ordenar por preço
  const sortedAsks = [...ask_levels].sort((a, b) => a.price - b.price) // Ordenar por preço
  
  console.log(`📊 Mostrando ${sortedBids.length} bids e ${sortedAsks.length} asks (top por intensidade)`)
  
  // Calcular histograma lateral (acumulado de liquidez por nível)
  const histogramData = {}
  const allLevels = [
    ...bid_levels.map(l => ({ ...l, type: 'bid' })),
    ...ask_levels.map(l => ({ ...l, type: 'ask' }))
  ]
  
  allLevels.forEach(level => {
    const y = priceToY(level.price)
    const yKey = Math.round(y) // Arredondar para agrupar por pixel
    
    if (!histogramData[yKey]) {
      histogramData[yKey] = {
        y: yKey,
        price: level.price,
        totalQty: 0,
        bidQty: 0,
        askQty: 0
      }
    }
    
    histogramData[yKey].totalQty += level.total_qty || 0
    if (level.type === 'bid') {
      histogramData[yKey].bidQty += level.total_qty || 0
    } else {
      histogramData[yKey].askQty += level.total_qty || 0
    }
  })
  
  // Encontrar POC (Point of Control - nível com maior liquidez)
  let pocY = null
  let maxQty = 0
  Object.values(histogramData).forEach(entry => {
    if (entry.totalQty > maxQty) {
      maxQty = entry.totalQty
      pocY = entry.y
    }
  })
  
  // Desenhar histograma lateral (à esquerda do gráfico)
  const histogramStartX = 20
  const histogramMaxWidth = histogram_width - 10
  
  Object.values(histogramData).forEach(entry => {
    const barWidth = (entry.totalQty / maxQty) * histogramMaxWidth
    
    // Cor baseada na proporção bid/ask
    const bidRatio = entry.totalQty > 0 ? entry.bidQty / entry.totalQty : 0
    const askRatio = entry.totalQty > 0 ? entry.askQty / entry.totalQty : 0
    
    // Gradiente de cor: verde para bids, vermelho para asks
    const r = Math.floor(askRatio * 255)
    const g = Math.floor(bidRatio * 255)
    const b = 0
    
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`
    ctx.fillRect(
      histogramStartX,
      entry.y - 1, // -1 para centralizar na linha
      barWidth,
      2 // Altura da barra (2px para alinhar com as linhas)
    )
  })
  
  // Desenhar marcador do POC (linha horizontal fina)
  if (pocY !== null) {
    ctx.strokeStyle = '#ffff00' // Amarelo brilhante
    ctx.lineWidth = 2
    ctx.setLineDash([3, 3])
    ctx.beginPath()
    ctx.moveTo(histogramStartX, pocY)
    ctx.lineTo(histogramStartX + histogramMaxWidth, pocY)
    ctx.stroke()
    ctx.setLineDash([])
    
    // Label do POC
    ctx.fillStyle = '#ffff00'
    ctx.font = 'bold 10px monospace'
    ctx.textAlign = 'left'
    ctx.textBaseline = 'middle'
    ctx.fillText(
      'POC',
      histogramStartX + histogramMaxWidth + 5,
      pocY
    )
  }
  
  // Função para filtrar labels e evitar sobreposição
  const filterLabels = (levels, minSpacing = 25) => {
    const filtered = []
    const usedYPositions = []
    
    // Ordenar por intensidade (maior primeiro) para priorizar labels importantes
    const sorted = [...levels].sort((a, b) => b.intensity - a.intensity)
    
    sorted.forEach(level => {
      const y = priceToY(level.price)
      
      // Verificar se há espaço suficiente para este label
      const hasSpace = usedYPositions.every(usedY => Math.abs(y - usedY) >= minSpacing)
      
      if (hasSpace) {
        filtered.push(level)
        usedYPositions.push(y)
      }
    })
    
    // Reordenar por preço para manter ordem visual
    return filtered.sort((a, b) => a.price - b.price)
  }
  
  // Filtrar labels para evitar sobreposição
  const filteredBids = filterLabels(sortedBids, 25)
  const filteredAsks = filterLabels(sortedAsks, 25)
  
  console.log(`📊 Labels filtrados: ${filteredBids.length} bids, ${filteredAsks.length} asks (de ${sortedBids.length + sortedAsks.length} total)`)
  
  // Bids (verde, abaixo do preço atual) - desenhar todas as linhas
  sortedBids.forEach(level => {
    const y = priceToY(level.price)
    const isHovered = hoveredLevel.value && 
                      hoveredLevel.value.price === level.price && 
                      hoveredLevel.value.type === 'bid'
    
    const colorInfo = intensityToColor(level.intensity, 'bid')
    let lineWidth = Math.max(1, Math.min(3, level.intensity * 2 + 1)) // Linhas mais finas para degradê
    
    // Destacar linha hovered
    if (isHovered) {
      // Linha de destaque mais brilhante e mais grossa
      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = lineWidth + 2
      ctx.shadowColor = '#00ff00'
      ctx.shadowBlur = 20
    } else {
      // Aplicar cor com opacidade e glow
      ctx.strokeStyle = colorInfo.color
      ctx.lineWidth = lineWidth
      ctx.shadowColor = colorInfo.glow
      ctx.shadowBlur = Math.max(3, level.intensity * 15) // Glow baseado na intensidade
    }
    
    ctx.beginPath()
    ctx.moveTo(margin_left, y)
    ctx.lineTo(margin_left + chart_width, y)
    ctx.stroke()
    
    // Resetar shadow para próxima linha
    if (!isHovered) {
      ctx.shadowBlur = 0
    }
  })
  
  // Resetar shadow após desenhar todas as linhas
  ctx.shadowBlur = 0
  
  // Labels de preço apenas para níveis filtrados (bids)
  filteredBids.forEach(level => {
    const y = priceToY(level.price)
    ctx.fillStyle = '#00ff00'
    ctx.font = '11px monospace'
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'
    ctx.fillText(
      `$${formatPrice(level.price)}`,
      margin_left - histogram_width - 8,
      y
    )
  })
  
  // Asks (vermelho, acima do preço atual) - desenhar todas as linhas
  sortedAsks.forEach(level => {
    const y = priceToY(level.price)
    const isHovered = hoveredLevel.value && 
                      hoveredLevel.value.price === level.price && 
                      hoveredLevel.value.type === 'ask'
    
    const colorInfo = intensityToColor(level.intensity, 'ask')
    let lineWidth = Math.max(1.5, Math.min(4, level.intensity * 3 + 1.5)) // Linhas um pouco mais grossas para melhor visibilidade
    
    // Destacar linha hovered
    if (isHovered) {
      // Linha de destaque mais brilhante e mais grossa
      ctx.strokeStyle = '#ff0000'
      ctx.lineWidth = lineWidth + 2
      ctx.shadowColor = '#ff0000'
      ctx.shadowBlur = 20
    } else {
      // Aplicar cor com opacidade e glow
      ctx.strokeStyle = colorInfo.color
      ctx.lineWidth = lineWidth
      ctx.shadowColor = colorInfo.glow
      ctx.shadowBlur = Math.max(3, level.intensity * 15) // Glow baseado na intensidade
    }
    
    ctx.beginPath()
    ctx.moveTo(margin_left, y)
    ctx.lineTo(margin_left + chart_width, y)
    ctx.stroke()
    
    // Resetar shadow para próxima linha
    if (!isHovered) {
      ctx.shadowBlur = 0
    }
  })
  
  // Resetar shadow após desenhar todas as linhas
  ctx.shadowBlur = 0
  
  // Labels de preço apenas para níveis filtrados (asks)
  filteredAsks.forEach(level => {
    const y = priceToY(level.price)
    ctx.fillStyle = '#ff0000'
    ctx.font = '11px monospace'
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'
    ctx.fillText(
      `$${formatPrice(level.price)}`,
      margin_left - histogram_width - 8,
      y
    )
  })
  
  // Linha do preço atual (mais visível)
  const currentY = priceToY(current_price)
  ctx.strokeStyle = '#00ff00'
  ctx.lineWidth = 3
  ctx.setLineDash([8, 4])
  ctx.beginPath()
  ctx.moveTo(margin_left, currentY)
  ctx.lineTo(margin_left + chart_width, currentY)
  ctx.stroke()
  ctx.setLineDash([])
  
  // Sombra/glow para linha do preço atual
  ctx.shadowColor = '#00ff00'
  ctx.shadowBlur = 10
  ctx.strokeStyle = '#00ff00'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(margin_left, currentY)
  ctx.lineTo(margin_left + chart_width, currentY)
  ctx.stroke()
  ctx.shadowBlur = 0
  
  // Label do preço atual (mais visível) - ajustado para histograma
  ctx.fillStyle = '#00ff00'
  ctx.font = 'bold 14px monospace'
  ctx.textAlign = 'right'
  ctx.textBaseline = 'bottom'
  ctx.fillText(
    `PREÇO: $${formatPrice(current_price)}`,
    margin_left - histogram_width - 8,
    currentY - 8
  )
  
  // Overlay de Suportes e Resistências (S/R)
  if (showSR.value && srData.value) {
    // Desenhar Suportes (linhas azuis pontilhadas)
    if (srData.value.suportes && Array.isArray(srData.value.suportes) && srData.value.suportes.length > 0) {
      srData.value.suportes.forEach((supportPrice, index) => {
        if (typeof supportPrice !== 'number' || isNaN(supportPrice)) return
        
        // Verificar se está dentro do range visível
        if (supportPrice < min_price || supportPrice > max_price) return
        
        const supportY = priceToY(supportPrice)
        const isHovered = hoveredSR.value && 
                          hoveredSR.value.type === 'support' && 
                          hoveredSR.value.index === index
        
        // Linha pontilhada azul (mais brilhante se hovered)
        ctx.strokeStyle = isHovered ? '#00aaff' : '#0088ff'
        ctx.lineWidth = isHovered ? 3 : 2
        ctx.shadowColor = isHovered ? '#00aaff' : 'transparent'
        ctx.shadowBlur = isHovered ? 10 : 0
        ctx.setLineDash([5, 5])
        ctx.beginPath()
        ctx.moveTo(margin_left, supportY)
        ctx.lineTo(margin_left + chart_width, supportY)
        ctx.stroke()
        ctx.setLineDash([])
        ctx.shadowBlur = 0
        
        // Label
        ctx.fillStyle = isHovered ? '#00aaff' : '#0088ff'
        ctx.font = isHovered ? 'bold 12px monospace' : '11px monospace'
        ctx.textAlign = 'right'
        ctx.textBaseline = 'middle'
        ctx.fillText(
          `S${index + 1}: $${formatPrice(supportPrice)}`,
          margin_left - histogram_width - 8,
          supportY
        )
      })
    }
    
    // Desenhar Resistências (linhas vermelhas pontilhadas)
    if (srData.value.resistencias && Array.isArray(srData.value.resistencias) && srData.value.resistencias.length > 0) {
      srData.value.resistencias.forEach((resistancePrice, index) => {
        if (typeof resistancePrice !== 'number' || isNaN(resistancePrice)) return
        
        // Verificar se está dentro do range visível
        if (resistancePrice < min_price || resistancePrice > max_price) return
        
        const resistanceY = priceToY(resistancePrice)
        const isHovered = hoveredSR.value && 
                          hoveredSR.value.type === 'resistance' && 
                          hoveredSR.value.index === index
        
        // Linha pontilhada vermelha (mais brilhante se hovered)
        ctx.strokeStyle = isHovered ? '#ff00aa' : '#ff0088'
        ctx.lineWidth = isHovered ? 3 : 2
        ctx.shadowColor = isHovered ? '#ff00aa' : 'transparent'
        ctx.shadowBlur = isHovered ? 10 : 0
        ctx.setLineDash([5, 5])
        ctx.beginPath()
        ctx.moveTo(margin_left, resistanceY)
        ctx.lineTo(margin_left + chart_width, resistanceY)
        ctx.stroke()
        ctx.setLineDash([])
        ctx.shadowBlur = 0
        
        // Label - ajustado para histograma
        ctx.fillStyle = isHovered ? '#ff00aa' : '#ff0088'
        ctx.font = isHovered ? 'bold 12px monospace' : '11px monospace'
        ctx.textAlign = 'right'
        ctx.textBaseline = 'middle'
        ctx.fillText(
          `R${index + 1}: $${formatPrice(resistancePrice)}`,
          margin_left - histogram_width - 8,
          resistanceY
        )
      })
    }
  }
  
  // Grid e eixos (mais visível)
  ctx.strokeStyle = '#00ff0040'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(margin_left, margin_top)
  ctx.lineTo(margin_left, margin_top + chart_height)
  ctx.stroke()
  
  // Linha direita
  ctx.beginPath()
  ctx.moveTo(margin_left + chart_width, margin_top)
  ctx.lineTo(margin_left + chart_width, margin_top + chart_height)
  ctx.stroke()
  
  console.log('✅ Heatmap desenhado:', {
    levels_drawn: sortedBids.length + sortedAsks.length,
    current_price_y: currentY,
    price_range: `${min_price.toFixed(2)} - ${max_price.toFixed(2)}`
  })
}

// Mouse interaction
const handleMouseMove = (event) => {
  if (!data.value || !canvasRef.value) return
  
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // Verificar se está sobre algum nível
  const all_levels = [
    ...data.value.bid_levels.map(l => ({ ...l, type: 'bid' })),
    ...data.value.ask_levels.map(l => ({ ...l, type: 'ask' }))
  ]
  
  // Calcular range de preços
  const all_prices = all_levels.map(l => l.price)
  const min_price = Math.min(...all_prices)
  const max_price = Math.max(...all_prices)
  const price_range = max_price - min_price || 1
  
  const margin_top = 40
  const margin_bottom = 40
  const histogram_width = 60
  const margin_left = 80 + histogram_width
  const chart_height = canvasHeight.value - margin_top - margin_bottom
  
  // Função para converter preço em Y (mesma lógica do drawHeatmap)
  const priceToY = (price) => {
    const normalized = (price - min_price) / price_range
    return margin_top + chart_height * (1 - normalized)
  }
  
  // Verificar se está dentro da área do gráfico
  if (x >= margin_left && x <= canvasWidth.value - 80 && y >= margin_top && y <= margin_top + chart_height) {
    // Converter Y para preço
    const normalizedY = (y - margin_top) / chart_height
    const price = max_price - (normalizedY * price_range)
    
    // Calcular intensidade da zona (para degradê)
    let zoneIntensity = { bid: 0, ask: 0, total: 0 }
    let minDistanceZone = Infinity
    
    all_levels.forEach(level => {
      const distance = Math.abs(level.price - price)
      if (distance < minDistanceZone) {
        minDistanceZone = distance
        if (level.type === 'bid') {
          zoneIntensity.bid = level.intensity || 0
        } else {
          zoneIntensity.ask = level.intensity || 0
        }
        zoneIntensity.total = Math.max(zoneIntensity.bid, zoneIntensity.ask)
      }
    })
    
    // Verificar se está sobre uma linha S/R primeiro (prioridade)
    let closestSR = null
    let minDistanceSR = Infinity
    const tolerancePixelsSR = 8
    
    if (showSR.value && srData.value) {
      // Verificar suportes
      if (srData.value.suportes && Array.isArray(srData.value.suportes)) {
        srData.value.suportes.forEach((supportPrice, index) => {
          if (typeof supportPrice === 'number' && !isNaN(supportPrice)) {
            if (supportPrice >= min_price && supportPrice <= max_price) {
              const supportY = priceToY(supportPrice)
              const distance = Math.abs(y - supportY)
              
              if (distance < tolerancePixelsSR && distance < minDistanceSR) {
                minDistanceSR = distance
                closestSR = {
                  type: 'support',
                  price: supportPrice,
                  index: index
                }
              }
            }
          }
        })
      }
      
      // Verificar resistências
      if (srData.value.resistencias && Array.isArray(srData.value.resistencias)) {
        srData.value.resistencias.forEach((resistancePrice, index) => {
          if (typeof resistancePrice === 'number' && !isNaN(resistancePrice)) {
            if (resistancePrice >= min_price && resistancePrice <= max_price) {
              const resistanceY = priceToY(resistancePrice)
              const distance = Math.abs(y - resistanceY)
              
              if (distance < tolerancePixelsSR && distance < minDistanceSR) {
                minDistanceSR = distance
                closestSR = {
                  type: 'resistance',
                  price: resistancePrice,
                  index: index
                }
              }
            }
          }
        })
      }
    }
    
    // Encontrar nível mais próximo (com tolerância de 10px em Y)
    let closest = null
    let minDistance = Infinity
    const tolerancePixels = 10
    
    all_levels.forEach(level => {
      const levelY = priceToY(level.price)
      const distance = Math.abs(y - levelY)
      
      if (distance < tolerancePixels && distance < minDistance) {
        minDistance = distance
        closest = level
      }
    })
    
    // Priorizar S/R sobre linhas de liquidez
    if (closestSR) {
      // Atualizar tooltip com informações S/R
      tooltipData.value = {
        price: closestSR.price,
        type: closestSR.type === 'support' ? 'support' : 'resistance',
        isSR: true,
        srType: closestSR.type,
        srIndex: closestSR.index,
        zoneIntensity: zoneIntensity.total,
        zoneBidIntensity: zoneIntensity.bid,
        zoneAskIntensity: zoneIntensity.ask,
        isZone: false
      }
      tooltipPosition.value = {
        x: event.clientX + 10,
        y: event.clientY - 10
      }
      
      // Atualizar hover S/R e redesenhar
      if (!hoveredSR.value || 
          hoveredSR.value.type !== closestSR.type || 
          hoveredSR.value.index !== closestSR.index) {
        hoveredSR.value = closestSR
        hoveredLevel.value = null // Limpar hover de liquidez
        // Redesenhar para destacar a linha S/R
        nextTick(() => {
          if (canvasRef.value && data.value) {
            drawHeatmap()
          }
        })
      }
    } else if (closest) {
      // Atualizar tooltip com informações do nível + zona
      tooltipData.value = {
        ...closest,
        zoneIntensity: zoneIntensity.total,
        zoneBidIntensity: zoneIntensity.bid,
        zoneAskIntensity: zoneIntensity.ask,
        isZone: false
      }
      tooltipPosition.value = {
        x: event.clientX + 10,
        y: event.clientY - 10
      }
      
      // Atualizar linha hovered e redesenhar
      if (!hoveredLevel.value || 
          hoveredLevel.value.price !== closest.price || 
          hoveredLevel.value.type !== closest.type) {
        hoveredLevel.value = closest
        hoveredSR.value = null // Limpar hover S/R
        // Redesenhar para destacar a linha
        nextTick(() => {
          if (canvasRef.value && data.value) {
            drawHeatmap()
          }
        })
      }
    } else if (zoneIntensity.total > 0.01) {
      // Mostrar informações da zona mesmo sem linha exata
      const dominantType = zoneIntensity.bid > zoneIntensity.ask ? 'bid' : 'ask'
      tooltipData.value = {
        price: price,
        type: dominantType,
        total_qty: 0,
        intensity: zoneIntensity.total,
        zoneIntensity: zoneIntensity.total,
        zoneBidIntensity: zoneIntensity.bid,
        zoneAskIntensity: zoneIntensity.ask,
        isZone: true
      }
      tooltipPosition.value = {
        x: event.clientX + 10,
        y: event.clientY - 10
      }
      
      // Limpar hover de linha e S/R
      if (hoveredLevel.value) {
        hoveredLevel.value = null
      }
      if (hoveredSR.value) {
        hoveredSR.value = null
      }
      nextTick(() => {
        if (canvasRef.value && data.value) {
          drawHeatmap()
        }
      })
    } else {
      // Limpar hover se não está sobre nenhuma linha ou zona
      if (hoveredLevel.value) {
        hoveredLevel.value = null
      }
      if (hoveredSR.value) {
        hoveredSR.value = null
      }
      if (hoveredLevel.value || hoveredSR.value) {
        nextTick(() => {
          if (canvasRef.value && data.value) {
            drawHeatmap()
          }
        })
      }
      tooltipData.value = null
    }
  } else {
    // Limpar hover se saiu da área do gráfico
    if (hoveredLevel.value) {
      hoveredLevel.value = null
    }
    if (hoveredSR.value) {
      hoveredSR.value = null
    }
    if (hoveredLevel.value || hoveredSR.value) {
      nextTick(() => {
        if (canvasRef.value && data.value) {
          drawHeatmap()
        }
      })
    }
    tooltipData.value = null
  }
}

const handleMouseLeave = () => {
  tooltipData.value = null
  hoveredLevel.value = null
  hoveredSR.value = null
  // Redesenhar para remover destaque
  nextTick(() => {
    if (canvasRef.value && data.value) {
      drawHeatmap()
    }
  })
}

// Formatting
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

const formatQty = (qty) => {
  if (!qty || isNaN(qty)) return '0'
  const num = parseFloat(qty)
  if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(2) + 'K'
  }
  return num.toFixed(2)
}

const getRatioColor = (ratio) => {
  if (!ratio) return ''
  if (ratio > 1.2) return 'text-terminal-green'
  if (ratio < 0.8) return 'text-red-500'
  return 'text-yellow-500'
}

// Função para obter label de temperatura
const getTemperatureLabel = (intensity) => {
  if (!intensity || intensity < 0.1) return 'Frio ❄️'
  if (intensity < 0.3) return 'Morno 🌤️'
  if (intensity < 0.6) return 'Quente 🔥'
  return 'Muito Quente 🔥🔥'
}

// Watch para redesenhar quando dados mudarem
watch(() => data.value, (newData) => {
  if (newData && canvasRef.value) {
    nextTick(() => {
      drawHeatmap()
    })
  }
}, { deep: true })

// Toggle auto-refresh
const toggleAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
  
  if (autoRefresh.value) {
    // Iniciar auto-refresh com intervalo maior (30 segundos)
    refreshInterval.value = setInterval(() => {
      if (canvasRef.value && !loading.value) {
        loadData()
      }
    }, 30000) // 30 segundos
    console.log('✅ Auto-refresh ativado (30s)')
  } else {
    console.log('⏸️ Auto-refresh desativado')
  }
}

// Watch para redesenhar quando dados mudarem (sem recarregar da API)
watch(() => data.value, (newData) => {
  if (newData && canvasRef.value && !loading.value) {
    nextTick(() => {
      drawHeatmap()
    })
  }
}, { deep: true })

// Quando símbolo ou precisão mudarem, recarregar dados
watch([selectedSymbol, precision, binSize], () => {
  if (canvasRef.value) {
    loadData()
  }
})

onMounted(async () => {
  // Aguardar canvas estar montado
  await nextTick()
  
  // Aguardar um pouco mais para garantir que o DOM está pronto
  setTimeout(() => {
    if (canvasRef.value) {
      console.log('✅ Canvas montado, carregando dados...')
      loadData()
    } else {
      console.error('❌ Canvas ainda não disponível após timeout')
    }
  }, 200)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.liquidity-heatmap {
  position: relative;
  min-height: 600px;
}

.loading-overlay,
.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 600px;
}

.heatmap-container {
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid #00ff0030;
  border-radius: 8px;
  padding: 20px;
}

.controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.stat-card {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #00ff0030;
  border-radius: 4px;
  padding: 12px;
}

.stat-label {
  font-size: 11px;
  color: #00ff0070;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #00ff00;
}

.heatmap-wrapper {
  position: relative;
  background: #000000;
  border: 1px solid #00ff0030;
  border-radius: 4px;
  padding: 10px;
  overflow: auto;
}

.heatmap-canvas {
  display: block;
  cursor: crosshair;
}

.heatmap-tooltip {
  position: fixed;
  background: rgba(10, 10, 10, 0.95);
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 8px 12px;
  pointer-events: none;
  z-index: 1000;
  min-width: 200px;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
}

.tooltip-header {
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #00ff0030;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #00ff0070;
}

.tooltip-warning {
  margin-top: 4px;
  padding: 4px;
  background: #ffff0020;
  border: 1px solid #ffff00;
  border-radius: 3px;
  font-size: 10px;
  color: #ffff00;
  text-align: center;
}

.legend {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #00ff0030;
  border-radius: 4px;
  padding: 12px;
}

.legend-title {
  font-size: 12px;
  color: #00ff00;
  font-weight: bold;
  margin-bottom: 8px;
}

.legend-items {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #00ff0070;
}

.legend-color {
  width: 40px;
  height: 4px;
  border-radius: 2px;
}

.legend-line {
  width: 40px;
  height: 2px;
}
</style>


<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="mb-8 flex justify-between items-center">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <TargetIcon :size="28" class="text-terminal-green" />
          <h1 class="text-3xl font-bold tech-heading">
            SNE RADAR
            <span class="text-xs text-terminal-green/50 ml-2 font-sans normal-case">Sistema Neural Estratégico</span>
          </h1>
        </div>
        <p class="text-terminal-green/70 tech-label">RADAR VISUAL DE OPORTUNIDADES</p>
      </div>
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2 text-sm text-terminal-green/70">
          <div class="w-2 h-2 rounded-full bg-terminal-green animate-pulse" :class="{ 'bg-terminal-green': isOnline, 'bg-red-500': !isOnline }"></div>
          <span class="tech-label">{{ isOnline ? 'ONLINE' : 'OFFLINE' }}</span>
        </div>
        <div v-if="lastUpdate" class="flex items-center gap-1 text-xs text-terminal-green/50">
          <ClockIcon :size="12" />
          <span class="tech-label">ÚLTIMA VARREDURA: {{ lastUpdate }}</span>
          <span v-if="isCacheValid && cacheAge" class="ml-2 text-terminal-green/40 tabular-nums">
            (Cache: {{ cacheAge.minutes }}min {{ cacheAge.seconds }}s)
          </span>
        </div>
      </div>
    </div>

    <!-- Cards de Resumo -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="card">
        <div class="text-xs text-terminal-green/70 mb-1 tech-label">BTC/USDT</div>
        <div class="text-2xl font-bold tech-value tabular-nums">{{ formatBTCPrice(btcPrice) }}</div>
        <div 
          v-if="btcChange !== null && btcChange !== undefined"
          class="text-sm flex items-center gap-1"
          :class="btcChange >= 0 ? 'text-terminal-green' : 'text-red-500'"
        >
          <ArrowUpRightIcon 
            v-if="btcChange >= 0"
            :size="14"
            :stroke-width="2"
            class="text-terminal-green"
            aria-label="Preço subindo"
          />
          <ArrowDownRightIcon 
            v-else
            :size="14"
            :stroke-width="2"
            class="text-red-500"
            aria-label="Preço caindo"
          />
          <span class="tabular-nums">{{ formatPercent(btcChange) }}</span>
        </div>
      </div>
      
      <div class="card">
        <div class="text-xs text-terminal-green/70 mb-1 tech-label">BLIPS ATIVOS</div>
        <div class="text-2xl font-bold tech-value tabular-nums">{{ radarOpportunities.length }}</div>
        <div class="text-terminal-green text-sm tabular-nums">/ 20 máx</div>
      </div>
      
      <div class="card">
        <div class="text-xs text-terminal-green/70 mb-1 flex items-center gap-1 tech-label">
          SETUPS OPERACIONAIS
          <AlertCircleIcon 
            :size="12"
            class="cursor-help text-terminal-green/50 hover:text-terminal-green"
            title="Número de oportunidades com informações operacionais completas (Entry, Stop Loss, Take Profit, R:R)"
          />
        </div>
        <div class="text-2xl font-bold tech-value tabular-nums">{{ operationalOpportunities }}</div>
        <div class="text-terminal-green text-sm tech-label">COM NÍVEIS</div>
      </div>
    </div>

    <!-- Radar Visual -->
    <div class="card mb-8">
      <div class="radar-layout">
        <!-- Radar Canvas - Ocupa mais espaço -->
        <div class="radar-wrapper">
          <div v-if="error" class="radar-error">
            <div class="text-red-500 mb-4">{{ error }}</div>
            <button 
              @click="refreshAll"
              class="px-4 py-2 rounded bg-terminal-green text-black hover:opacity-80"
            >
              Tentar Novamente
            </button>
          </div>
          
          <RadarCanvas
            v-else
            :opportunities="radarOpportunities"
            :sweep-angle="sweepAngle"
            :loading="loading"
            :btc-price="btcPrice"
            :btc-change="btcChange"
            @blip-click="selectOpportunity"
          />
        </div>
        
        <!-- Controles - Lado direito, compacto -->
        <div class="radar-controls-wrapper">
          <RadarControls
            :filter-signal="filterSignal"
            :filter-min-score="filterMinScore"
            :timeframe="selectedTimeframe"
            :loading="loading"
            :blip-count="radarOpportunities.length"
            :last-update="lastUpdate"
            @update:filters="handleFiltersUpdate"
            @update:timeframe="handleTimeframeUpdate"
            @refresh="(force) => refreshAll(force || true)"
          />
        </div>
      </div>
    </div>

    <!-- Status -->
    <div class="card mb-8">
      <h3 class="text-lg font-bold mb-4">Status</h3>
      <div class="space-y-2">
        <div class="flex justify-between">
          <span class="text-terminal-green/70 tech-label">ÚLTIMA ATUALIZAÇÃO</span>
          <span class="tech-value tabular-nums">{{ lastUpdate || '--' }}</span>
        </div>
        <div v-if="opportunities.length > 0" class="flex justify-between">
          <span class="text-terminal-green/70 tech-label">OPORTUNIDADES CARREGADAS</span>
          <span class="text-terminal-green tech-value tabular-nums">{{ opportunities.length }}</span>
        </div>
      </div>
    </div>

    <!-- Informações e Definições -->
    <div class="card">
      <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
        <span>ℹ️</span>
        <span>Informações e Definições</span>
      </h3>
      <div class="space-y-4 text-sm">
        <div>
          <h4 class="font-bold text-terminal-green mb-2">📊 Score de Confluência</h4>
          <p class="text-terminal-green/70 mb-2">
            O <strong>Score de Confluência</strong> mede a força de uma oportunidade de trading baseado na convergência (confluência) de múltiplas análises técnicas:
          </p>
          <ul class="list-disc list-inside space-y-1 text-terminal-green/70 ml-4">
            <li><strong>Multi-Timeframe:</strong> Análise em diferentes períodos (1h, 4h, 1d)</li>
            <li><strong>Fluxo DOM:</strong> Pressão de compra/venda no order book</li>
            <li><strong>Zonas Magnéticas:</strong> Níveis de suporte/resistência importantes</li>
            <li><strong>Sentiment:</strong> Medo/ganância do mercado</li>
            <li><strong>Indicadores Técnicos:</strong> RSI, MACD, EMAs, Bollinger Bands</li>
          </ul>
          <div class="mt-2 p-2 bg-terminal-dark rounded border border-terminal-green/20">
            <p class="text-xs text-terminal-green/80">
              <strong>Escala:</strong> De <span class="text-red-500">-10</span> (muito negativo) a <span class="text-terminal-green">+10</span> (muito positivo). 
              Scores acima de 7 indicam alta qualidade, abaixo de 0 indicam evitar operação.
            </p>
          </div>
        </div>
        
        <div>
          <h4 class="font-bold text-terminal-green mb-2">🎯 Sinais (BUY/SELL/NEUTRAL)</h4>
          <div class="space-y-2 text-terminal-green/70">
            <div>
              <span class="text-terminal-green font-bold">BUY (Compra):</span> 
              <span class="ml-2">Múltiplos indicadores convergem para uma oportunidade de compra (long).</span>
            </div>
            <div>
              <span class="text-red-500 font-bold">SELL (Venda):</span> 
              <span class="ml-2">Múltiplos indicadores convergem para uma oportunidade de venda (short).</span>
            </div>
            <div>
              <span class="text-terminal-green/70 font-bold">NEUTRAL (Neutro):</span> 
              <span class="ml-2">Não há confluência clara. Melhor aguardar confirmação antes de operar.</span>
            </div>
          </div>
        </div>

        <div>
          <h4 class="font-bold text-terminal-green mb-2">💰 Informações Operacionais</h4>
          <div class="space-y-2 text-terminal-green/70">
            <div>
              <span class="font-bold">Entry (Entrada):</span> 
              <span class="ml-2">Preço sugerido para abrir a posição.</span>
            </div>
            <div>
              <span class="font-bold">SL (Stop Loss):</span> 
              <span class="ml-2">Preço de proteção para limitar perdas.</span>
            </div>
            <div>
              <span class="font-bold">TP1 (Take Profit):</span> 
              <span class="ml-2">Primeiro objetivo de lucro. Considere realizar parcial aqui.</span>
            </div>
            <div>
              <span class="font-bold">R:R (Risk/Reward):</span> 
              <span class="ml-2">Razão risco/recompensa. R:R ≥ 2.0 é considerado excelente.</span>
            </div>
            <div>
              <span class="font-bold">Nível de Risco:</span> 
              <span class="ml-2">BAIXO (aumentar posição), MÉDIO (normal), ALTO (reduzir 50%).</span>
            </div>
          </div>
        </div>

        <div>
          <h4 class="font-bold text-terminal-green mb-2">💡 Como Usar</h4>
          <ul class="list-disc list-inside space-y-1 text-terminal-green/70 ml-4">
            <li>Priorize oportunidades com informações operacionais completas (Entry, SL, TP, R:R)</li>
            <li>R:R ≥ 2.0 indica setup de alta qualidade</li>
            <li>Use os filtros para encontrar oportunidades específicas</li>
            <li>Clique em uma oportunidade para ver análise detalhada completa</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Target, Clock, ArrowUpRight, ArrowDownRight, AlertCircle } from 'lucide-vue-next'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import RadarCanvas from '@/components/radar/RadarCanvas.vue'
import RadarControls from '@/components/radar/RadarControls.vue'
// RadarLegend removido - agora está integrado dentro do RadarCanvas
import { useDashboardStore } from '@/stores/dashboard'
import api from '@/services/api'

const TargetIcon = Target
const ClockIcon = Clock
const ArrowUpRightIcon = ArrowUpRight
const ArrowDownRightIcon = ArrowDownRight
const AlertCircleIcon = AlertCircle

const router = useRouter()
const dashboardStore = useDashboardStore()

// Usar store para state gerenciado
const opportunities = computed(() => dashboardStore.opportunities)
const btcPrice = computed(() => dashboardStore.btcPrice)
const btcChange = computed(() => dashboardStore.btcChange)
const lastUpdate = computed(() => dashboardStore.lastUpdate)
const isCacheValid = computed(() => dashboardStore.isCacheValid)
const cacheAge = computed(() => dashboardStore.cacheAge)

const loading = ref(false)
const error = ref(null)

// Filtros
const filterSignal = ref('')
const filterMinScore = ref('-10')
const selectedTimeframe = ref('1h')

// Radar
const sweepAngle = ref(0)
const isOnline = ref(true)
let sweepAnimationId = null

let refreshInterval = null

// Computed
const averageScore = computed(() => {
  if (opportunities.value.length === 0) return '0.0'
  const sum = opportunities.value.reduce((acc, opp) => acc + (parseFloat(opp.score) || 0), 0)
  return (sum / opportunities.value.length).toFixed(1)
})

const operationalOpportunities = computed(() => {
  // Contar oportunidades com informações operacionais completas
  return opportunities.value.filter(opp => 
    opp.entry_price && opp.stop_loss && opp.take_profit
  ).length
})

const filteredOpportunities = computed(() => {
  let filtered = [...opportunities.value]
  
  if (filterSignal.value) {
    filtered = filtered.filter(opp => opp.signal === filterSignal.value)
  }
  
  const minScore = parseFloat(filterMinScore.value) || -10
  if (minScore !== -10) {
    filtered = filtered.filter(opp => (parseFloat(opp.score) || 0) >= minScore)
  }
  
  return filtered.sort((a, b) => (parseFloat(b.score) || 0) - (parseFloat(a.score) || 0))
})
  
// Oportunidades para o radar (limitado a 20, ordenadas por score)
const radarOpportunities = computed(() => {
  return filteredOpportunities.value.slice(0, 20)
})

// Métodos
const formatPercent = (value) => {
  if (value === null || value === undefined || isNaN(value) || !isFinite(value)) return '--'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

const formatBTCPrice = (price) => {
  if (price === null || price === undefined) return '--'
  const priceNum = typeof price === 'number' ? price : parseFloat(price)
  if (isNaN(priceNum) || !isFinite(priceNum)) return '--'
  // Formatação consistente: números grandes com ponto como separador de milhar
  if (priceNum >= 1000) {
    return priceNum.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  } else {
    // Números pequenos (< 1000) com vírgula como decimal (formato brasileiro)
    return priceNum.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }
}

const formatPrice = (price) => {
  if (!price || isNaN(price)) return '--'
  const num = parseFloat(price)
  // Formatação consistente: números grandes com ponto como separador de milhar
  if (num >= 1000) {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  } else {
    // Números pequenos (< 1000) com vírgula como decimal (formato brasileiro)
    return num.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }
}

const parseRR = (rr) => {
  if (!rr) return 0
  // Pode vir como "1:2.5" ou como número 2.5
  if (typeof rr === 'string') {
    const match = rr.match(/1:?([\d.]+)/)
    return match ? parseFloat(match[1]) : 0
  }
  return parseFloat(rr) || 0
}

const getScoreTooltip = (score) => {
  const scoreNum = parseFloat(score) || 0
  if (scoreNum >= 7) {
    return 'Score Alto (7-10): Forte confluência de sinais técnicos. Múltiplas análises convergindo na mesma direção. Oportunidade de alta qualidade.'
  } else if (scoreNum >= 5) {
    return 'Score Médio (5-7): Boa confluência. Várias análises indicando a mesma direção. Oportunidade moderada.'
  } else if (scoreNum >= 0) {
    return 'Score Baixo (0-5): Confluência fraca. Análises não estão muito alinhadas. Oportunidade de baixa qualidade.'
  } else {
    return 'Score Negativo: Sinais conflitantes ou mercado desfavorável. Evitar operação.'
  }
}

const getSignalTooltip = (signal) => {
  switch(signal?.toUpperCase()) {
    case 'BUY':
      return 'Sinal de COMPRA: Análises indicam oportunidade de entrada longa (compra). Baseado em confluência de indicadores técnicos (RSI, MACD, EMAs, Volume, etc).'
    case 'SELL':
      return 'Sinal de VENDA: Análises indicam oportunidade de entrada short (venda). Baseado em confluência de indicadores técnicos.'
    case 'NEUTRAL':
    default:
      return 'Sinal NEUTRO: Não há confluência clara de sinais. Melhor aguardar confirmação antes de operar.'
  }
}

const selectOpportunity = (opp) => {
  router.push({
    name: 'Analysis',
    query: { symbol: opp.symbol, timeframe: opp.timeframe || '1h' }
  })
}

const loadBTCPrice = async () => {
  try {
    // Buscar candles para obter o preço atual
    const response = await api.getCandles('BTCUSDT', '1h', 2)
    
    // O interceptor do axios já extraiu response.data, então temos:
    // response = { success: true, data: { candles: [...] } }
    const candles = response?.data?.candles || []
    
    if (candles && candles.length > 0) {
      const lastCandle = candles[candles.length - 1]
      const price = lastCandle.close
      
      if (price) {
        const priceNum = parseFloat(price)
        
        // Validar se o preço é um número válido
        if (isNaN(priceNum) || !isFinite(priceNum)) {
          console.warn('⚠️ Preço BTC inválido:', price)
          dashboardStore.updateBTCPrice(null, null)
          return
        }
        
        let change = null
        
        // Calcular mudança percentual se houver candle anterior
        if (candles.length > 1) {
          const prevCandle = candles[candles.length - 2]
          const prevPrice = parseFloat(prevCandle.close)
          if (prevPrice && prevPrice > 0 && !isNaN(prevPrice) && isFinite(prevPrice)) {
            change = ((priceNum - prevPrice) / prevPrice) * 100
            // Validar se a mudança é um número válido
            if (isNaN(change) || !isFinite(change)) {
              change = null
            }
          }
        }
        
        // Salvar o preço como número puro (sem formatação)
        dashboardStore.updateBTCPrice(priceNum, change)
      }
    } else {
      dashboardStore.updateBTCPrice('N/A', null)
    }
  } catch (err) {
    console.warn('Erro ao carregar preço BTC:', err)
    dashboardStore.updateBTCPrice(null, null)
  }
}

const loadOpportunities = async () => {
  error.value = null
  
  try {
    const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT', 'MATICUSDT', 'DOTUSDT', 'UNIUSDT', 'ATOMUSDT', 'LTCUSDT', 'ETCUSDT', 'XLMUSDT', 'ALGOUSDT', 'VETUSDT', 'FILUSDT', 'TRXUSDT']
    const results = []
    
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))
    
    // Carregar em paralelo com limite de concorrência
    const batchSize = 5
    for (let i = 0; i < symbols.length; i += batchSize) {
      const batch = symbols.slice(i, i + batchSize)
      const batchPromises = batch.map(async (symbol) => {
        try {
          const data = await api.getSignal(symbol, selectedTimeframe.value)
        
        if (data && (data.signal !== undefined || data.score !== undefined)) {
          const signal = (data.signal || data.recommendation || 'NEUTRAL').toUpperCase()
          const score = parseFloat(data.score || data.confluence_score || 0)
          
          const operational = data.operational || {}
          
            return {
            symbol,
              timeframe: data.timeframe || selectedTimeframe.value,
            signal: signal,
            score: score,
            current_price: data.current_price,
            entry_price: operational.entry_price,
            stop_loss: operational.stop_loss,
            take_profit: operational.take_profit_1,
            risk_reward: operational.risk_reward_ratio,
            risk_level: operational.risk_level,
            recommendation: operational.recommendation,
            action: operational.action
          }
          }
          return null
      } catch (err) {
          console.warn(`Erro ao carregar ${symbol}:`, err.message)
          return null
      }
      })
      
      const batchResults = await Promise.all(batchPromises)
      results.push(...batchResults.filter(r => r !== null))
      
      // Pequeno delay entre batches para evitar rate limit
      if (i + batchSize < symbols.length) {
        await delay(500)
      }
    }
    
    if (results.length === 0) {
      error.value = 'Não foi possível carregar oportunidades. Verifique se o servidor está rodando e tente novamente.'
      return []
    } else {
      const sorted = results.sort((a, b) => (parseFloat(b.score) || 0) - (parseFloat(a.score) || 0))
      dashboardStore.updateOpportunities(sorted)
      return sorted
    }
  } catch (error) {
    console.error('Erro geral ao carregar oportunidades:', error)
    error.value = error.message || 'Erro ao carregar dados. Tente novamente.'
    return []
  }
}

// Animar varredura ao atualizar
const animateSweep = () => {
  // Resetar ângulo
  sweepAngle.value = 0
  
  // Animar de 0 a 360 graus em 2 segundos
  const duration = 2000 // 2 segundos
  const startTime = Date.now()
  const startAngle = 0
  const endAngle = 360
  
  const animate = () => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // Easing function (ease-out)
    const eased = 1 - Math.pow(1 - progress, 3)
    sweepAngle.value = startAngle + (endAngle - startAngle) * eased
    
    if (progress < 1) {
      sweepAnimationId = requestAnimationFrame(animate)
    } else {
      // Após completar, resetar após 500ms
      setTimeout(() => {
        sweepAngle.value = 0
      }, 500)
    }
  }
  
  animate()
}

const handleFiltersUpdate = ({ signal, minScore }) => {
  filterSignal.value = signal
  filterMinScore.value = minScore
}

const handleTimeframeUpdate = (timeframe) => {
  selectedTimeframe.value = timeframe
  // Forçar atualização ao mudar timeframe (cache não é válido para outro timeframe)
  refreshAll(true)
}

const refreshAll = async (force = false) => {
  error.value = null
  
  // Verificar cache se não for forçado
  if (!force && isCacheValid.value) {
    console.log('✅ Usando cache válido, pulando atualização')
    // Ainda atualizar BTC price (mais leve)
    loadBTCPrice()
    return
  }
  
  loading.value = true
  
  // Iniciar animação de varredura
  animateSweep()
  
  try {
    const [opps, btcData] = await Promise.all([
      loadOpportunities(),
      loadBTCPrice()
    ])
    
    const updateTime = new Date().toLocaleTimeString('pt-BR')
    
    // Salvar no cache
    dashboardStore.saveToCache(
      opps || dashboardStore.opportunities,
      dashboardStore.btcPrice,
      dashboardStore.btcChange,
      updateTime
    )
  } catch (err) {
    console.error('Erro ao atualizar:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Tentar carregar do cache primeiro
  const cacheLoaded = dashboardStore.loadFromCache()
  
  if (cacheLoaded) {
    console.log('✅ Dashboard carregada do cache')
    // Ainda atualizar BTC price (mais leve)
    loadBTCPrice()
  } else {
    console.log('🔄 Cache não disponível ou expirado, carregando dados...')
    refreshAll(true) // Forçar atualização
  }
  
  refreshInterval = setInterval(() => {
    if (!loading.value) {
      refreshAll(true) // Forçar atualização periódica
    }
  }, 120000) // 2 minutos
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  if (sweepAnimationId) {
    cancelAnimationFrame(sweepAnimationId)
  }
})
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 bg-terminal-dark border border-terminal-green/30 rounded text-terminal-green focus:border-terminal-green focus:outline-none;
}

/* Layout otimizado do radar - mais compacto */
.radar-layout {
  display: grid;
  grid-template-columns: 1fr 240px; /* Reduzido de 280px para 240px */
  gap: 16px; /* Reduzido de 20px */
  min-height: auto; /* Removido min-height fixo */
  max-height: 550px; /* Limitar altura total */
  align-items: start; /* Alinhar ao topo */
}

.radar-wrapper {
  width: 100%;
  height: 100%;
  min-height: 350px;
  max-height: 500px; /* Limitar altura do radar */
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-loading,
.radar-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 350px;
  text-align: center;
}

.radar-controls-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px; /* Reduzido de 16px */
  width: 100%;
  max-width: 240px; /* Limitar largura */
}

/* Responsividade */
@media (max-width: 1024px) {
  .radar-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    min-height: auto;
    max-height: none; /* Remover limite em mobile */
  }
  
  .radar-wrapper {
    min-height: 400px;
    max-height: 450px;
  }
  
  .radar-controls-wrapper {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .radar-layout {
    gap: 16px;
  }
  
  .radar-wrapper {
    min-height: 350px;
    max-height: 400px;
  }
  
  .radar-controls-wrapper {
    flex-direction: column;
  }
}
</style>

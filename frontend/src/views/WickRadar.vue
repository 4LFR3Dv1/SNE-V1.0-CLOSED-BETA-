<template>
  <div class="wick-immersive-container">
    <!-- Header HUD -->
    <div class="tactical-header">
      <div class="header-left">
        <div class="header-icon">◉</div>
        <div>
          <h1 class="header-title">WICK RADAR</h1>
          <p class="header-subtitle">MONITORAMENTO TÁTICO DE AGULHADAS</p>
        </div>
      </div>
      
      <div class="header-controls">
        <div class="monitor-status" :class="{ active: monitorRunning }">
          <div class="status-dot"></div>
          <span>{{ monitorRunning ? 'MONITOR ATIVO' : 'MONITOR INATIVO' }}</span>
        </div>
        
        <Button 
          :variant="monitorRunning ? 'danger' : 'primary'"
          :loading="toggleLoading"
          @click="toggleMonitor"
          size="sm"
        >
          {{ monitorRunning ? 'PARAR' : 'INICIAR' }}
        </Button>
        
        <Button 
          variant="secondary"
          :loading="loading"
          @click="refreshData"
          size="sm"
        >
          <template #icon><RefreshCw :size="16" :class="{ 'animate-spin': loading }" /></template>
          ATUALIZAR
        </Button>
      </div>
    </div>

    <!-- Stats HUD Overlays -->
    <div class="stats-hud-grid">
      <div class="hud-stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-content">
          <div class="stat-label">TOTAL SCANS</div>
          <div class="stat-value">{{ stats.scans_total || 0 }}</div>
        </div>
        <div class="stat-glow"></div>
      </div>

      <div class="hud-stat-card alert">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-label">ALERTAS VOLUME</div>
          <div class="stat-value">{{ stats.alerts_volume || 0 }}</div>
        </div>
        <div class="stat-glow yellow"></div>
      </div>

      <div class="hud-stat-card success">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-label">AGULHADAS</div>
          <div class="stat-value">{{ stats.alerts_pavio || 0 }}</div>
        </div>
        <div class="stat-glow green"></div>
      </div>

      <div class="hud-stat-card">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <div class="stat-label">ÚLTIMA ANÁLISE</div>
          <div class="stat-value-sm">{{ lastScanTime }}</div>
        </div>
        <div class="stat-glow"></div>
      </div>
    </div>

    <!-- Filtros Táticos -->
    <div class="tactical-filters">
      <div class="filter-label">
        <Filter :size="16" />
        <span>FILTROS:</span>
      </div>
      
      <div class="filter-buttons">
        <button 
          v-for="type in filterTypes" 
          :key="type.value"
          :class="['filter-btn', { active: filterType === type.value }]"
          @click="filterType = type.value"
        >
          {{ type.label }}
        </button>
      </div>

      <div class="filter-buttons">
        <button 
          v-for="sym in ['all', ...symbols]" 
          :key="sym"
          :class="['filter-btn symbol', { active: filterSymbol === sym }]"
          @click="filterSymbol = sym"
        >
          {{ sym === 'all' ? 'TODOS' : sym }}
        </button>
      </div>
    </div>

    <!-- Alert Cards Grid -->
    <div class="alerts-grid">
      <div 
        v-for="asset in filteredAssets" 
        :key="asset.symbol"
        class="alert-card-premium"
        :class="{ 'long': asset.tipo === 'LONG', 'short': asset.tipo === 'SHORT' }"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="symbol-badge">
            <div class="symbol-icon">{{ asset.symbol.substring(0, 3) }}</div>
            <div class="symbol-info">
              <h3>{{ asset.symbol }}</h3>
              <Badge :variant="getBadgeVariant(asset)" size="sm">
                {{ asset.badgeText }}
              </Badge>
            </div>
          </div>
          
          <div class="price-section">
            <div class="price">${{ formatPrice(asset.preco_atual) }}</div>
            <div class="metrics">
              <span v-if="asset.rvol_m30" class="metric">
                RVOL {{ asset.rvol_m30?.toFixed(2) }}x
              </span>
              <span v-if="asset.rsi_m5" :class="['metric', getRSIClass(asset.rsi_m5)]">
                RSI {{ asset.rsi_m5?.toFixed(1) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Chart -->
        <div class="chart-container">
          <div 
            :ref="`chart-${asset.symbol}`" 
            :id="`chart-${asset.symbol}`"
            class="chart"
          ></div>
          
          <!-- Wick Info Overlay -->
          <div v-if="asset.wick_info && asset.tipo" class="wick-overlay">
            <div class="wick-badge">
              <Target :size="12" />
              <span>{{ asset.tipo === 'LONG' ? 'Inferior' : 'Superior' }}</span>
              <span class="recuo">{{ asset.recuo_pct?.toFixed(2) }}%</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <span class="timestamp">{{ formatTimestamp(asset.timestamp) }}</span>
          <Button variant="ghost" size="sm">VER ANÁLISE</Button>
        </div>

        <div class="card-glow" :class="asset.tipo?.toLowerCase()"></div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredAssets.length === 0" class="empty-state-premium">
        <div class="radar-pulse-container">
          <div class="radar-pulse"></div>
          <div class="radar-ping"></div>
        </div>
        <h3>AGUARDANDO SINAIS</h3>
        <p>Os alertas aparecerão aqui em tempo real</p>
        <div class="status-hint">{{ monitorRunning ? 'Monitor ativo' : 'Inicie o monitor acima' }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { createChart, ColorType } from 'lightweight-charts'
import { RefreshCw, Filter, Target } from 'lucide-vue-next'
import Button from '@/components/common/Button.vue'
import Badge from '@/components/common/Badge.vue'
import api from '@/services/api'

// Refs
const loading = ref(false)
const toggleLoading = ref(false)
const monitorRunning = ref(false)
const stats = ref({})
const assets = ref([])
const symbols = ref(['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT'])
const filterType = ref('all')
const filterSymbol = ref('all')
const charts = ref({})
const refreshInterval = ref(null)

const filterTypes = [
  { value: 'all', label: 'TODOS' },
  { value: 'volume', label: 'VOLUME' },
  { value: 'pavio', label: 'AGULHADA' }
]

// Computed
const filteredAssets = computed(() => {
  let filtered = [...assets.value]
  
  if (filterType.value !== 'all') {
    filtered = filtered.filter(asset => {
      if (filterType.value === 'volume') return asset.type === 'volume'
      if (filterType.value === 'pavio') return asset.type === 'pavio'
      return true
    })
  }
  
  if (filterSymbol.value !== 'all') {
    filtered = filtered.filter(asset => asset.symbol === filterSymbol.value)
  }
  
  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const lastScanTime = computed(() => {
  if (!stats.value.last_scan) return 'Nunca'
  const date = new Date(stats.value.last_scan)
  return date.toLocaleTimeString('pt-BR')
})

// Methods (mantidos do arquivo original)
const loadStats = async () => {
  try {
    const response = await api.getNotificationsStats()
    if (response.success) {
      stats.value = response.stats || {}
    }
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error)
  }
}

const loadHistory = async () => {
  try {
    loading.value = true
    console.log('🔍 [WICK RADAR] Carregando histórico de alertas...')
    const response = await api.getNotificationsHistory()
    console.log('📡 [WICK RADAR] Resposta da API:', response)
    
    if (response.success && response.history) {
      console.log(`✅ [WICK RADAR] ${response.history.length} alertas recebidos`)
      
      const enrichedAssets = response.history.map((alert) => {
        const isPavio = alert.tipo !== undefined || alert.rsi_m5 !== undefined
        const type = isPavio ? 'pavio' : 'volume'
        
        let badgeText = 'Volume'
        if (isPavio) {
          badgeText = alert.tipo === 'LONG' ? 'LONG' : 'SHORT'
        }
        
        return {
          symbol: alert.symbol,
          type: type,
          timestamp: alert.timestamp,
          badgeText: badgeText,
          tipo: alert.tipo,
          preco_atual: alert.preco_atual || 0,
          rvol_m30: alert.rvol_m30 || alert.rvol || 0,
          rsi_m5: alert.rsi_m5,
          recuo_pct: alert.recuo_pct || 0,
          high_m5: alert.high_m5,
          low_m5: alert.low_m5,
          wick_info: isPavio && (alert.wick_confirmed !== false)
        }
      })
      
      console.log('📊 [WICK RADAR] Assets processados:', enrichedAssets)
      assets.value = enrichedAssets
      await createCharts()
    } else {
      console.warn('⚠️ [WICK RADAR] Resposta sem sucesso ou sem histórico:', response)
    }
  } catch (error) {
    console.error('❌ [WICK RADAR] Erro ao carregar histórico:', error)
  } finally {
    loading.value = false
  }
}

const loadMonitorStatus = async () => {
  try {
    const response = await api.getMonitorStatus()
    if (response.success) {
      monitorRunning.value = response.status.running || false
    }
  } catch (error) {
    console.error('Erro ao carregar status:', error)
  }
}

const toggleMonitor = async () => {
  try {
    toggleLoading.value = true
    const response = monitorRunning.value 
      ? await api.stopMonitor()
      : await api.startMonitor()
    
    if (response.success) {
      monitorRunning.value = !monitorRunning.value
      await loadStats()
    }
  } catch (error) {
    console.error('Erro ao alternar monitor:', error)
  } finally {
    toggleLoading.value = false
  }
}

const refreshData = async () => {
  await Promise.all([
    loadStats(),
    loadHistory(),
    loadMonitorStatus()
  ])
}

const createCharts = async () => {
  await new Promise(resolve => setTimeout(resolve, 100))
  
  for (const asset of filteredAssets.value) {
    const chartId = `chart-${asset.symbol}`
    const chartElement = document.getElementById(chartId)
    
    if (!chartElement || charts.value[asset.symbol]) {
      continue
    }
    
    try {
      const candleResponse = await api.getCandles(asset.symbol, '5m', 50)
      
      if (!candleResponse.success || !candleResponse.data?.candles) {
        continue
      }
      
      const candles = candleResponse.data.candles.map(c => ({
        time: Math.floor(c.time / 1000),
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close
      }))
      
      const chart = createChart(chartElement, {
        width: chartElement.clientWidth,
        height: 250,
        layout: {
          background: { type: ColorType.Solid, color: 'transparent' },
          textColor: '#00ff41'
        },
        grid: {
          vertLines: { color: 'rgba(0, 255, 65, 0.05)' },
          horzLines: { color: 'rgba(0, 255, 65, 0.05)' }
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
          borderColor: 'rgba(0, 255, 65, 0.2)'
        },
        rightPriceScale: {
          borderColor: 'rgba(0, 255, 65, 0.2)'
        }
      })
      
      const candleSeries = chart.addCandlestickSeries({
        upColor: '#00ff41',
        downColor: '#ff0033',
        borderVisible: false,
        wickUpColor: '#00ff41',
        wickDownColor: '#ff0033'
      })
      
      candleSeries.setData(candles)
      chart.timeScale().fitContent()
      charts.value[asset.symbol] = chart
      
    } catch (error) {
      console.error(`Erro ao criar gráfico para ${asset.symbol}:`, error)
    }
  }
}

const formatPrice = (price) => {
  if (!price) return '0.00'
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price)
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('pt-BR')
}

const getBadgeVariant = (asset) => {
  if (asset.tipo === 'LONG') return 'buy'
  if (asset.tipo === 'SHORT') return 'sell'
  if (asset.type === 'volume') return 'warning'
  return 'default'
}

const getRSIClass = (rsi) => {
  if (rsi >= 75) return 'rsi-high'
  if (rsi <= 25) return 'rsi-low'
  return 'rsi-neutral'
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  refreshInterval.value = setInterval(() => {
    refreshData()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  Object.values(charts.value).forEach(chart => {
    if (chart) chart.remove()
  })
})

watch(filteredAssets, () => {
  Object.values(charts.value).forEach(chart => {
    if (chart) chart.remove()
  })
  charts.value = {}
  createCharts()
})
</script>

<style scoped>
.wick-immersive-container {
  min-height: 100vh;
  background: #000;
  padding: 1.5rem;
  font-family: 'Share Tech Mono', monospace;
}

/* Header */
.tactical-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(0, 20, 10, 0.85);
  border: 1px solid #00ff41;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: #00ff41;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
}

.header-title {
  font-size: 24px;
  font-weight: bold;
  color: #00ff41;
  letter-spacing: 3px;
  margin: 0;
}

.header-subtitle {
  font-size: 11px;
  color: rgba(0, 255, 65, 0.6);
  letter-spacing: 2px;
  margin: 0;
  margin-top: 4px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.monitor-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 65, 0.3);
  border-radius: 6px;
  font-size: 12px;
  color: rgba(0, 255, 65, 0.6);
  letter-spacing: 1px;
}

.monitor-status.active {
  border-color: #00ff41;
  color: #00ff41;
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background: rgba(0, 255, 65, 0.3);
}

.monitor-status.active .status-dot {
  background: #00ff41;
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Stats HUD Grid */
.stats-hud-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.hud-stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(0, 20, 10, 0.85);
  border: 1px solid rgba(0, 255, 65, 0.3);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.hud-stat-card:hover {
  border-color: #00ff41;
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  filter: grayscale(1) brightness(0.8);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 10px;
  letter-spacing: 2px;
  color: rgba(0, 255, 65, 0.6);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #00ff41;
  line-height: 1;
}

.stat-value-sm {
  font-size: 16px;
  font-weight: bold;
  color: #00ff41;
}

.stat-glow {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(0, 255, 65, 0.15), transparent);
  pointer-events: none;
}

.stat-glow.yellow {
  background: radial-gradient(circle, rgba(255, 170, 0, 0.15), transparent);
}

.stat-glow.green {
  background: radial-gradient(circle, rgba(0, 255, 65, 0.25), transparent);
}

/* Tactical Filters */
.tactical-filters {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  background: rgba(0, 20, 10, 0.6);
  border: 1px solid rgba(0, 255, 65, 0.2);
  border-radius: 8px;
  margin-bottom: 2rem;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(0, 255, 65, 0.7);
  font-size: 12px;
  letter-spacing: 2px;
  font-weight: bold;
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 65, 0.3);
  border-radius: 6px;
  color: rgba(0, 255, 65, 0.7);
  font-size: 11px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Share Tech Mono', monospace;
}

.filter-btn:hover {
  border-color: #00ff41;
  color: #00ff41;
}

.filter-btn.active {
  background: rgba(0, 255, 65, 0.15);
  border-color: #00ff41;
  color: #00ff41;
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
}

.filter-btn.symbol {
  min-width: 80px;
  text-align: center;
}

/* Alerts Grid */
.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 1.5rem;
}

.alert-card-premium {
  position: relative;
  background: rgba(0, 20, 10, 0.85);
  border: 1px solid rgba(0, 255, 65, 0.2);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
}

.alert-card-premium:hover {
  border-color: #00ff41;
  box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
  transform: translateY(-4px);
}

.alert-card-premium.long {
  border-left: 3px solid #00ff41;
}

.alert-card-premium.short {
  border-left: 3px solid #ff0033;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid rgba(0, 255, 65, 0.1);
}

.symbol-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.symbol-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: rgba(0, 255, 65, 0.1);
  border: 1px solid rgba(0, 255, 65, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  color: #00ff41;
}

.symbol-info h3 {
  font-size: 18px;
  color: #fff;
  margin: 0 0 4px 0;
  letter-spacing: 1px;
}

.price-section {
  text-align: right;
}

.price {
  font-size: 24px;
  font-weight: bold;
  color: #00ff41;
  margin-bottom: 4px;
}

.metrics {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.metric {
  font-size: 11px;
  padding: 0.25rem 0.5rem;
  background: rgba(0, 255, 65, 0.1);
  border-radius: 4px;
  color: #00ff41;
}

.rsi-high { color: #ff0033; background: rgba(255, 0, 51, 0.1); }
.rsi-low { color: #00ff41; background: rgba(0, 255, 65, 0.1); }
.rsi-neutral { color: #999; background: rgba(153, 153, 153, 0.1); }

/* Chart */
.chart-container {
  position: relative;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
}

.chart {
  width: 100%;
  height: 250px;
}

.wick-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.wick-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(0, 255, 65, 0.15);
  border: 1px solid #00ff41;
  border-radius: 6px;
  font-size: 11px;
  color: #00ff41;
  backdrop-filter: blur(10px);
}

.recuo {
  font-weight: bold;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-top: 1px solid rgba(0, 255, 65, 0.1);
}

.timestamp {
  font-size: 11px;
  color: rgba(0, 255, 65, 0.5);
}

.card-glow {
  position: absolute;
  bottom: -50%;
  right: -50%;
  width: 200px;
  height: 200px;
  opacity: 0.1;
  pointer-events: none;
}

.card-glow.long {
  background: radial-gradient(circle, #00ff41, transparent);
}

.card-glow.short {
  background: radial-gradient(circle, #ff0033, transparent);
}

/* Empty State */
.empty-state-premium {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: rgba(0, 20, 10, 0.5);
  border: 1px dashed rgba(0, 255, 65, 0.2);
  border-radius: 12px;
}

.radar-pulse-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 2rem;
}

.radar-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(0, 255, 65, 0.2);
  border: 2px solid #00ff41;
}

.radar-ping {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid #00ff41;
  animation: ping 2s ease-in-out infinite;
}

@keyframes ping {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}

.empty-state-premium h3 {
  font-size: 24px;
  color: #00ff41;
  letter-spacing: 3px;
  margin: 0 0 0.5rem 0;
}

.empty-state-premium p {
  font-size: 14px;
  color: rgba(0, 255, 65, 0.6);
  margin: 0 0 1rem 0;
}

.status-hint {
  font-size: 11px;
  color: rgba(0, 255, 65, 0.4);
  letter-spacing: 1px;
}

/* Responsive */
@media (max-width: 768px) {
  .tactical-header {
    flex-direction: column;
    gap: 1rem;
  }

  .alerts-grid {
    grid-template-columns: 1fr;
  }

  .tactical-filters {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

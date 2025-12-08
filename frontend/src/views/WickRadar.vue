<template>
  <div class="wick-radar-container">
    <!-- Header -->
    <div class="wick-radar-header">
      <div class="header-content">
        <h1 class="text-2xl font-bold text-terminal-green">
          🎯 Wick Radar
        </h1>
        <p class="text-gray-400 text-sm">
          Monitoramento de Agulhadas em Formação - Volume M30 + RSI M5 + Confirmação de Wick
        </p>
      </div>
      <div class="header-controls">
        <div class="status-indicator" :class="{ active: monitorRunning }">
          <span class="status-dot"></span>
          <span>{{ monitorRunning ? 'Monitor Ativo' : 'Monitor Inativo' }}</span>
        </div>
        <button 
          @click="toggleMonitor" 
          class="control-btn"
          :disabled="toggleLoading"
        >
          {{ toggleLoading ? '⏳' : (monitorRunning ? '⏸️ Parar' : '▶️ Iniciar') }}
        </button>
        <button @click="refreshData" class="control-btn" :disabled="loading">
          {{ loading ? '⏳' : '🔄 Atualizar' }}
        </button>
      </div>
    </div>

    <!-- Estatísticas -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total de Scans</div>
        <div class="stat-value">{{ stats.scans_total || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Alertas de Volume</div>
        <div class="stat-value text-yellow-400">{{ stats.alerts_volume || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Alertas de Agulhada</div>
        <div class="stat-value text-terminal-green">{{ stats.alerts_pavio || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Última Análise</div>
        <div class="stat-value text-sm">{{ lastScanTime }}</div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters-section">
      <div class="filter-group">
        <label class="filter-label">Tipo de Alerta:</label>
        <select v-model="filterType" class="filter-select">
          <option value="all">Todos</option>
          <option value="volume">Volume Explosivo</option>
          <option value="pavio">Agulhada</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">Símbolo:</label>
        <select v-model="filterSymbol" class="filter-select">
          <option value="all">Todos</option>
          <option v-for="symbol in symbols" :key="symbol" :value="symbol">{{ symbol }}</option>
        </select>
      </div>
    </div>

    <!-- Dashboard de Ativos -->
    <div class="assets-dashboard">
      <div 
        v-for="asset in filteredAssets" 
        :key="asset.symbol"
        class="asset-card"
      >
        <div class="asset-header">
          <div class="asset-info">
            <h3 class="asset-symbol">{{ asset.symbol }}</h3>
            <span 
              class="asset-badge"
              :class="{
                'badge-long': asset.tipo === 'LONG',
                'badge-short': asset.tipo === 'SHORT',
                'badge-volume': asset.type === 'volume'
              }"
            >
              {{ asset.badgeText }}
            </span>
          </div>
          <div class="asset-metrics">
            <div class="metric">
              <span class="metric-label">Preço:</span>
              <span class="metric-value">${{ formatPrice(asset.preco_atual) }}</span>
            </div>
            <div class="metric" v-if="asset.rvol_m30">
              <span class="metric-label">RVOL M30:</span>
              <span class="metric-value text-terminal-green">{{ asset.rvol_m30?.toFixed(2) }}x</span>
            </div>
            <div class="metric" v-if="asset.rsi_m5">
              <span class="metric-label">RSI M5:</span>
              <span class="metric-value" :class="getRSIClass(asset.rsi_m5)">{{ asset.rsi_m5?.toFixed(1) }}</span>
            </div>
          </div>
        </div>

        <!-- Gráfico do Ativo -->
        <div class="asset-chart-container">
          <div 
            :ref="`chart-${asset.symbol}`" 
            class="asset-chart"
            :id="`chart-${asset.symbol}`"
          ></div>
          
          <!-- Overlay com informações do Wick -->
          <div v-if="asset.wick_info && asset.tipo" class="wick-overlay">
            <div class="wick-info-card">
              <div class="wick-info-header">
                <span class="wick-icon">🎯</span>
                <span class="wick-title">Wick Detectado</span>
              </div>
              <div class="wick-details">
                <div class="wick-detail">
                  <span class="wick-label">Tipo:</span>
                  <span class="wick-value">{{ asset.tipo === 'LONG' ? 'Wick Inferior' : 'Wick Superior' }}</span>
                </div>
                <div class="wick-detail">
                  <span class="wick-label">Recuo:</span>
                  <span class="wick-value text-terminal-green">{{ asset.recuo_pct?.toFixed(2) }}%</span>
                </div>
                <div class="wick-detail" v-if="asset.high_m5">
                  <span class="wick-label">Máxima:</span>
                  <span class="wick-value">${{ formatPrice(asset.high_m5) }}</span>
                </div>
                <div class="wick-detail" v-if="asset.low_m5">
                  <span class="wick-label">Mínima:</span>
                  <span class="wick-value">${{ formatPrice(asset.low_m5) }}</span>
                </div>
                <div class="wick-detail">
                  <span class="wick-label">Fechamento:</span>
                  <span class="wick-value">${{ formatPrice(asset.preco_atual) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Timestamp -->
        <div class="asset-footer">
          <span class="asset-timestamp">{{ formatTimestamp(asset.timestamp) }}</span>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredAssets.length === 0" class="empty-state">
        <div class="empty-icon">📊</div>
        <div class="empty-text">Nenhum alerta encontrado</div>
        <div class="empty-subtext">Os alertas aparecerão aqui quando detectados</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { createChart, ColorType } from 'lightweight-charts'
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

// Methods
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
    const response = await api.getNotificationsHistory()
    if (response.success && response.history) {
      // O histórico retorna apenas timestamps básicos
      // Para dados completos, precisamos buscar do estado ou da API de estatísticas
      // Por enquanto, vamos criar uma estrutura básica
      const enrichedAssets = response.history.map((alert) => {
        // Determinar tipo baseado no símbolo e timestamp
        // Se tiver dados adicionais, usar; senão, assumir volume
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
      
      assets.value = enrichedAssets
      
      // Criar gráficos após dados carregados
      await createCharts()
    }
  } catch (error) {
    console.error('Erro ao carregar histórico:', error)
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
  // Aguardar próximo tick para garantir que DOM está atualizado
  await new Promise(resolve => setTimeout(resolve, 100))
  
  for (const asset of filteredAssets.value) {
    const chartId = `chart-${asset.symbol}`
    const chartElement = document.getElementById(chartId)
    
    if (!chartElement || charts.value[asset.symbol]) {
      continue
    }
    
    try {
      // Buscar dados de candles
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
      
      // Criar gráfico
      const chart = createChart(chartElement, {
        width: chartElement.clientWidth,
        height: 300,
        layout: {
          background: { type: ColorType.Solid, color: '#0a0a0a' },
          textColor: '#00ff88'
        },
        grid: {
          vertLines: { color: '#1a1a1a' },
          horzLines: { color: '#1a1a1a' }
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false
        }
      })
      
      // Adicionar série de candles
      const candleSeries = chart.addCandlestickSeries({
        upColor: '#00ff88',
        downColor: '#ff4444',
        borderVisible: false,
        wickUpColor: '#00ff88',
        wickDownColor: '#ff4444'
      })
      
      candleSeries.setData(candles)
      
      // Destacar wick se houver
      if (asset.wick_info && asset.tipo) {
        if (asset.tipo === 'SHORT' && asset.high_m5) {
          // Marcar máxima (wick superior)
          chart.addPriceLine({
            price: asset.high_m5,
            color: '#ffaa00',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'Máxima (Wick Superior)'
          })
        }
        
        if (asset.tipo === 'LONG' && asset.low_m5) {
          // Marcar mínima (wick inferior)
          chart.addPriceLine({
            price: asset.low_m5,
            color: '#00aaff',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'Mínima (Wick Inferior)'
          })
        }
      }
      
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

const getRSIClass = (rsi) => {
  if (rsi >= 75) return 'text-red-400'
  if (rsi <= 25) return 'text-green-400'
  return 'text-gray-400'
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  
  // Auto-refresh a cada 30 segundos
  refreshInterval.value = setInterval(() => {
    refreshData()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  // Destruir gráficos
  Object.values(charts.value).forEach(chart => {
    if (chart) chart.remove()
  })
})

// Watch para recriar gráficos quando filtros mudarem
watch(filteredAssets, () => {
  // Limpar gráficos antigos
  Object.values(charts.value).forEach(chart => {
    if (chart) chart.remove()
  })
  charts.value = {}
  
  // Recriar gráficos
  createCharts()
})
</script>

<style scoped>
.wick-radar-container {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
}

.wick-radar-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #1a1a1a;
}

.header-content h1 {
  margin-bottom: 0.5rem;
}

.header-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: #1a1a1a;
  color: #666;
}

.status-indicator.active {
  color: #00ff88;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
}

.status-indicator.active .status-dot {
  background: #00ff88;
  box-shadow: 0 0 8px #00ff88;
}

.control-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: #00ff88;
  color: #000;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.control-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  padding: 1rem;
  border-radius: 0.5rem;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #00ff88;
}

.filters-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #1a1a1a;
  border-radius: 0.5rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  color: #999;
  font-size: 0.875rem;
}

.filter-select {
  padding: 0.5rem;
  border-radius: 0.25rem;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  color: #00ff88;
  outline: none;
}

.assets-dashboard {
  display: grid;
  gap: 1.5rem;
}

.asset-card {
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: border-color 0.2s;
}

.asset-card:hover {
  border-color: #00ff88;
}

.asset-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.asset-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.asset-symbol {
  font-size: 1.25rem;
  font-weight: bold;
  color: #00ff88;
}

.asset-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-long {
  background: #00ff8820;
  color: #00ff88;
  border: 1px solid #00ff88;
}

.badge-short {
  background: #ff444420;
  color: #ff4444;
  border: 1px solid #ff4444;
}

.badge-volume {
  background: #ffaa0020;
  color: #ffaa00;
  border: 1px solid #ffaa00;
}

.asset-metrics {
  display: flex;
  gap: 1.5rem;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: #666;
}

.metric-value {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
}

.asset-chart-container {
  position: relative;
  margin: 1rem 0;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #0a0a0a;
}

.asset-chart {
  width: 100%;
  height: 300px;
}

.wick-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
}

.wick-info-card {
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid #00ff88;
  border-radius: 0.5rem;
  padding: 1rem;
  min-width: 250px;
}

.wick-info-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #2a2a2a;
}

.wick-icon {
  font-size: 1.25rem;
}

.wick-title {
  font-weight: 600;
  color: #00ff88;
}

.wick-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.wick-detail {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.wick-label {
  color: #666;
}

.wick-value {
  color: #fff;
  font-weight: 600;
}

.asset-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #2a2a2a;
}

.asset-timestamp {
  font-size: 0.75rem;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: #1a1a1a;
  border-radius: 0.5rem;
  border: 1px dashed #2a2a2a;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.25rem;
  color: #999;
  margin-bottom: 0.5rem;
}

.empty-subtext {
  font-size: 0.875rem;
  color: #666;
}
</style>


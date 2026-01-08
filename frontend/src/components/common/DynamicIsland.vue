<template>
  <header 
    ref="islandRef"
    class="tactical-island"
    :class="{ 
      'is-expanded': isExpanded,
      'has-notification': hasActiveNotification,
      'is-idle': isIdle
    }"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Collapsed State -->
    <div v-show="!isExpanded" class="island-collapsed">
      <div class="island-left">
        <router-link to="/" class="island-logo">
          <div class="logo-wrapper">
            <Target :size="20" class="logo-icon" />
          </div>
          <span class="logo-text">SNE RADAR</span>
        </router-link>
      </div>
      
      <div class="island-center">
        <div class="stat-compact">
          <span class="stat-label">ALVOS</span>
          <span class="stat-value">{{ blipsCount }}</span>
        </div>
        <div class="stat-divider">|</div>
        <div class="stat-compact">
          <span class="stat-label">BTC</span>
          <span class="stat-value">{{ btcPriceFormatted }}</span>
        </div>
      </div>
      
      <div class="island-right">
        <button 
          class="island-btn" 
          @click.stop="toggleNotifications"
          :class="{ 'has-badge': unreadCount > 0 }"
        >
          <Bell :size="16" />
          <span v-if="unreadCount > 0" class="notification-badge">
            {{ unreadCount }}
          </span>
        </button>
        
        <button class="island-btn" @click.stop="toggleUserMenu">
          <User :size="16" />
        </button>
      </div>
    </div>
    
    <!-- Expanded State -->
    <div v-show="isExpanded" class="island-expanded">
      <!-- Navigation -->
      <nav class="island-nav">
        <router-link to="/" class="nav-link" :class="{ active: route.path === '/' }">
          <LayoutDashboard :size="14" />
          <span>DASHBOARD</span>
        </router-link>
        <router-link to="/analysis" class="nav-link" :class="{ active: route.path === '/analysis' }">
          <LineChart :size="14" />
          <span>ANÁLISE</span>
        </router-link>
        <router-link to="/wick-radar" class="nav-link" :class="{ active: route.path === '/wick-radar' }">
          <Target :size="14" />
          <span>WICK RADAR</span>
        </router-link>
        <router-link to="/magnetic" class="nav-link" :class="{ active: route.path === '/magnetic' }">
          <Layers :size="14" />
          <span>HEATMAP</span>
        </router-link>
        <router-link to="/automated-trading" class="nav-link" :class="{ active: route.path === '/automated-trading' }">
          <Bot :size="14" />
          <span>TRADING</span>
        </router-link>
      </nav>
      
      <!-- Metrics Grid -->
      <div class="island-metrics">
        <div class="mini-metric">
          <div class="mini-metric-label">{{ contextualMetrics.metric1.label }}</div>
          <div class="mini-metric-value">{{ contextualMetrics.metric1.value }}</div>
          <div 
            v-if="contextualMetrics.metric1.change !== undefined" 
            class="mini-metric-change" 
            :class="{ 'positive': contextualMetrics.metric1.change > 0, 'negative': contextualMetrics.metric1.change < 0 }"
          >
            {{ contextualMetrics.metric1.change > 0 ? '▲' : '▼' }}{{ Math.abs(contextualMetrics.metric1.change).toFixed(2) }}%
          </div>
        </div>
        
        <div class="mini-metric">
          <div class="mini-metric-label">{{ contextualMetrics.metric2.label }}</div>
          <div class="mini-metric-value">{{ contextualMetrics.metric2.value }}</div>
        </div>
        
        <div class="mini-metric">
          <div class="mini-metric-label">{{ contextualMetrics.metric3.label }}</div>
          <div class="mini-metric-value">{{ contextualMetrics.metric3.value }}</div>
        </div>
        
        <div class="mini-metric">
          <div class="mini-metric-label">{{ contextualMetrics.metric4.label }}</div>
          <div class="mini-metric-value">
            <span 
              v-if="contextualMetrics.metric4.indicator !== undefined" 
              class="status-indicator" 
              :class="{ 'online': contextualMetrics.metric4.indicator }"
            ></span>
            {{ contextualMetrics.metric4.value }}
          </div>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="island-actions">
        <button class="action-btn" @click="$emit('search')">
          <Search :size="14" />
          <span>BUSCA (⌘K)</span>
        </button>
        
        <button class="action-btn" @click="$emit('refresh')">
          <RefreshCw :size="14" :class="{ 'animate-spin': isRefreshing }" />
          <span>ATUALIZAR</span>
        </button>
      </div>
    </div>
    
    <!-- Notification Banner -->
    <Transition name="slide-down">
      <div v-if="hasActiveNotification" class="island-notification">
        <div class="notification-content">
          <span class="notification-icon">⚡</span>
          <span class="notification-text">{{ notificationText }}</span>
        </div>
        <div class="notification-actions">
          <button class="notify-btn primary" @click="viewNotification">
            VER
          </button>
          <button class="notify-btn" @click="dismissNotification">
            DISPENSAR
          </button>
        </div>
      </div>
    </Transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { 
  Target, Bell, User, Search, RefreshCw,
  LayoutDashboard, LineChart, Bot, Layers
} from 'lucide-vue-next'
import { useDashboardStore } from '@/stores/dashboard'
import { useMarketStore } from '@/stores/market'

const dashboardStore = useDashboardStore()
const marketStore = useMarketStore()
const route = useRoute()

const islandRef = ref(null)
const isExpanded = ref(false)
const isRefreshing = ref(false)
const hasActiveNotification = ref(false)
const notificationText = ref('')
const unreadCount = ref(0)
const isIdle = ref(false) // NEW: Idle state (5s sem interação)

let idleTimer = null

// Reset idle timer on any user activity
const resetIdleTimer = () => {
  isIdle.value = false
  clearTimeout(idleTimer)
  
  idleTimer = setTimeout(() => {
    if (!isExpanded.value && !hasActiveNotification.value) {
      isIdle.value = true
    }
  }, 5000) // 5 segundos
}

// Computed properties
const blipsCount = computed(() => {
  const opps = dashboardStore.radarOpportunities || []
  return opps.length
})

const btcPrice = computed(() => {
  return dashboardStore.btcPrice || 0
})

const btcChange = computed(() => {
  return dashboardStore.btcChange || 0
})

const isOnline = computed(() => {
  return dashboardStore.isOnline ?? true
})

const btcPriceFormatted = computed(() => {
  if (!btcPrice.value || btcPrice.value === 0) {
    return '--'
  }
  return `$${btcPrice.value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
})

const averageScore = computed(() => {
  const opps = dashboardStore.radarOpportunities || []
  if (opps.length === 0) return 0
  const sum = opps.reduce((acc, opp) => acc + (opp.score || 0), 0)
  return sum / opps.length
})

// Contextual metrics based on route
const contextualMetrics = computed(() => {
  const path = route.path
  
  if (path === '/' || path.includes('dashboard')) {
    return {
      metric1: { label: 'BTC/USDT', value: btcPriceFormatted.value, change: btcChange.value },
      metric2: { label: 'ALVOS ATIVOS', value: `${blipsCount.value}/20` },
      metric3: { label: 'SCORE MÉDIO', value: `${averageScore.value.toFixed(1)}/10` },
      metric4: { label: 'STATUS', value: 'ONLINE', indicator: isOnline.value }
    }
  }
  
  if (path.includes('analysis')) {
    // Get symbol and timeframe from route or defaults
    const symbol = route.query.symbol || 'BTCUSDT'
    const timeframe = route.query.timeframe || '1h'
    
    // Get signal and score from marketStore
    const signal = marketStore.signal || 'NEUTRO'
    const score = marketStore.score || 0
    
    return {
      metric1: { label: 'SÍMBOLO', value: symbol },
      metric2: { label: 'TIMEFRAME', value: timeframe },
      metric3: { label: 'SINAL', value: signal },
      metric4: { label: 'SCORE', value: score ? `${score.toFixed(1)}/10` : '--' }
    }
  }
  
  if (path.includes('wick-radar')) {
    const opportunities = dashboardStore.radarOpportunities || []
    const buyCount = opportunities.filter(o => o.signal === 'BUY').length
    const sellCount = opportunities.filter(o => o.signal === 'SELL').length
    
    return {
      metric1: { label: 'TOTAL', value: opportunities.length },
      metric2: { label: 'COMPRA', value: buyCount },
      metric3: { label: 'VENDA', value: sellCount },
      metric4: { label: 'SCORE MAX', value: opportunities.length > 0 ? `${Math.max(...opportunities.map(o => o.score || 0)).toFixed(1)}` : '0.0' }
    }
  }

  if (path.includes('magnetic')) {
    return {
      metric1: { label: 'LIQUIDEZ', value: 'ALTA' },
      metric2: { label: 'PROFUNDIDADE', value: '$240M' },
      metric3: { label: 'SENTIMENTO', value: 'BULLISH' },
      metric4: { label: 'STATUS', value: 'LIVE', indicator: true }
    }
  }
  
  if (path.includes('automated-trading')) {
    return {
      metric1: { label: 'BOTS ATIVOS', value: '0' },
      metric2: { label: 'P&L HOJE', value: '$0.00' },
      metric3: { label: 'WIN RATE', value: '0%' },
      metric4: { label: 'STATUS', value: 'INATIVO', indicator: false }
    }
  }
  
  return {
    metric1: { label: 'BTC/USDT', value: btcPriceFormatted.value, change: btcChange.value },
    metric2: { label: 'ALVOS ATIVOS', value: `${blipsCount.value}/20` },
    metric3: { label: 'SCORE MÉDIO', value: `${averageScore.value.toFixed(1)}/10` },
    metric4: { label: 'STATUS', value: 'ONLINE', indicator: isOnline.value }
  }
})

const handleMouseEnter = () => {
  resetIdleTimer()
  if (!hasActiveNotification.value) {
    isExpanded.value = true
  }
}

const handleMouseLeave = () => {
  if (!hasActiveNotification.value) {
    isExpanded.value = false
  }
}

const toggleNotifications = () => {
  resetIdleTimer()
  console.log('Toggle notifications')
}

const toggleUserMenu = () => {
  resetIdleTimer()
  console.log('Toggle user menu')
}

const viewNotification = () => {
  hasActiveNotification.value = false
  resetIdleTimer()
}

const dismissNotification = () => {
  hasActiveNotification.value = false
  resetIdleTimer()
}

defineEmits(['search', 'refresh'])

onMounted(() => {
  if (dashboardStore.refreshAll) {
    dashboardStore.refreshAll()
  }
  
  // Global activity listeners para resetar idle (SEM mousemove)
  // Apenas click e keyboard resetam o timer
  // Hover na ilha expande via handleMouseEnter
  window.addEventListener('click', resetIdleTimer)
  window.addEventListener('keydown', resetIdleTimer)
  
  // Iniciar idle timer
  resetIdleTimer()
})

onUnmounted(() => {
  clearTimeout(idleTimer)
  window.removeEventListener('click', resetIdleTimer)
  window.removeEventListener('keydown', resetIdleTimer)
})
</script>

<style scoped>
.tactical-island {
  pointer-events: auto; /* Volta clique na ilha */
  position: relative;   /* Não sticky, não fixed */
  z-index: 1;
  
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  
  /* HUD militar style */
  background: rgba(0, 20, 10, 0.95);
  backdrop-filter: blur(16px);
  border: 1px solid #00ff41;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.8),
    0 0 40px rgba(0, 255, 65, 0.4),
    inset 0 0 20px rgba(0, 0, 0, 0.5);
}

/* Collapsed */
.tactical-island:not(.is-expanded) {
  width: min(90vw, 600px);
  height: 50px;
  border-radius: 25px;
}

/* Expanded */
.tactical-island.is-expanded {
  width: min(95vw, 800px);
  height: auto;
  min-height: 220px;
  border-radius: 12px;
}

/* Idle State (5s sem interação) - Ultra Minimal iOS Push Style */
.tactical-island.is-idle:not(.is-expanded) {
  width: 140px;
  height: 32px;
  border-radius: 16px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.8),
    0 0 12px rgba(0, 255, 65, 0.15);
  opacity: 0.9;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.tactical-island.is-idle:not(.is-expanded):hover {
  opacity: 1;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.9),
    0 0 20px rgba(0, 255, 65, 0.3);
}

/* Hide everything except logo when idle */
.tactical-island.is-idle .island-center,
.tactical-island.is-idle .island-right {
  display: none;
}

.tactical-island.is-idle .island-left {
  justify-content: center;
  width: 100%;
  gap: 8px;
}

.tactical-island.is-idle .logo-text {
  font-size: 11px;
  letter-spacing: 1.2px;
}

/* Replace icon with radar pulse (concentric circles) */
.tactical-island.is-idle .logo-wrapper {
  width: 24px;
  height: 24px;
  background: transparent;
  box-shadow: none;
  position: relative;
}

.tactical-island.is-idle .logo-icon {
  display: none;
}

/* Radar pulse circles */
.tactical-island.is-idle .logo-wrapper::before,
.tactical-island.is-idle .logo-wrapper::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border: 2px solid #00ff41;
  border-radius: 50%;
  animation: radar-pulse-ring 2s ease-out infinite;
}

.tactical-island.is-idle .logo-wrapper::before {
  width: 12px;
  height: 12px;
  animation-delay: 0s;
}

.tactical-island.is-idle .logo-wrapper::after {
  width: 12px;
  height: 12px;
  animation-delay: 1s;
}

@keyframes radar-pulse-ring {
  0% {
    width: 12px;
    height: 12px;
    opacity: 1;
  }
  100% {
    width: 24px;
    height: 24px;
    opacity: 0;
  }
}

/* Idle State (5s sem interação) */
.tactical-island.is-idle:not(.is-expanded) {
  width: min(60vw, 350px);
  height: 40px;
  border-radius: 20px;
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.6),
    0 0 20px rgba(0, 255, 65, 0.2),
    inset 0 0 10px rgba(0, 0, 0, 0.3);
  opacity: 0.85;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.tactical-island.is-idle:not(.is-expanded):hover {
  opacity: 1;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.8),
    0 0 40px rgba(0, 255, 65, 0.4),
    inset 0 0 20px rgba(0, 0, 0, 0.5);
}

/* === COLLAPSED STATE === */
.island-collapsed {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 100%;
}

.island-left,
.island-center,
.island-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.island-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s;
  text-decoration: none;
}

.island-logo:hover {
  opacity: 0.8;
}

.logo-wrapper {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #00ff41;
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.5);
}

.logo-icon {
  color: #000;
}

.logo-text {
  font-family: 'Share Tech Mono', monospace;
  font-weight: bold;
  font-size: 16px;
  color: #00ff41;
  letter-spacing: 2px;
  display: none;
}

@media (min-width: 640px) {
  .logo-text {
    display: inline;
  }
}

.stat-compact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  color: rgba(0, 255, 65, 0.6);
  letter-spacing: 1px;
}

.stat-value {
  font-family: 'Share Tech Mono', monospace;
  font-size: 13px;
  color: #00ff41;
  font-weight: bold;
}

.stat-divider {
  color: rgba(0, 255, 65, 0.3);
  font-size: 12px;
}

.island-btn {
  position: relative;
  width: 34px;
  height: 34px;
  border-radius: 17px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00ff41;
  background: transparent;
  border: 1px solid rgba(0, 255, 65, 0.2);
  transition: all 0.3s;
  cursor: pointer;
}

.island-btn:hover {
  background: rgba(0, 255, 65, 0.1);
  border-color: #00ff41;
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  border-radius: 9px;
  background: #ff0033;
  color: #fff;
  font-size: 10px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Share Tech Mono', monospace;
}

/* === EXPANDED STATE === */
.island-expanded {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.island-nav {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: rgba(0, 255, 65, 0.05);
  border: 1px solid rgba(0, 255, 65, 0.2);
  color: rgba(0, 255, 65, 0.7);
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  letter-spacing: 1px;
  text-decoration: none;
  transition: all 0.3s;
}

.nav-link:hover,
.nav-link.active {
  background: rgba(0, 255, 65, 0.15);
  border-color: #00ff41;
  color: #00ff41;
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
}

.island-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

@media (min-width: 768px) {
  .island-metrics {
    grid-template-columns: repeat(4, 1fr);
  }
}

.mini-metric {
  padding: 0.75rem;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(0, 255, 65, 0.15);
  transition: all 0.3s;
}

.mini-metric:hover {
  border-color: rgba(0, 255, 65, 0.4);
  background: rgba(0, 255, 65, 0.05);
}

.mini-metric-label {
  font-size: 9px;
  color: rgba(0, 255, 65, 0.6);
  margin-bottom: 0.25rem;
  font-family: 'Share Tech Mono', monospace;
  letter-spacing: 1px;
}

.mini-metric-value {
  font-size: 16px;
  font-family: 'Share Tech Mono', monospace;
  font-weight: bold;
  color: #00ff41;
}

.mini-metric-change {
  font-size: 11px;
  font-family: 'Share Tech Mono', monospace;
  margin-top: 0.25rem;
}

.mini-metric-change.positive {
  color: #00ff41;
}

.mini-metric-change.negative {
  color: #ff0033;
}

.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 4px;
  margin-right: 0.25rem;
  background: rgba(0, 255, 65, 0.3);
}

.status-indicator.online {
  background: #00ff41;
  box-shadow: 0 0 8px rgba(0, 255, 65, 0.6);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.island-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: transparent;
  border: 1px solid rgba(0, 255, 65, 0.3);
  color: #00ff41;
  font-family: 'Share Tech Mono', monospace;
  font-size: 11px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: rgba(0, 255, 65, 0.1);
  border-color: #00ff41;
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
}

/* === NOTIFICATION === */
.island-notification {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  margin-top: 0.5rem;
  border-top: 1px solid rgba(0, 255, 65, 0.2);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.notification-text {
  font-size: 12px;
  color: #00ff41;
  font-family: 'Share Tech Mono', monospace;
}

.notification-actions {
  display: flex;
  gap: 0.5rem;
}

.notify-btn {
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  background: transparent;
  border: 1px solid rgba(0, 255, 65, 0.3);
  color: #00ff41;
  font-family: 'Share Tech Mono', monospace;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.notify-btn:hover {
  background: rgba(0, 255, 65, 0.1);
  border-color: #00ff41;
}

.notify-btn.primary {
  background: rgba(0, 255, 65, 0.2);
  border-color: #00ff41;
}

/* Transitions */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 640px) {
  .tactical-island:not(.is-expanded) {
    width: calc(100vw - 2rem);
  }
  
  .island-center {
    display: none;
  }
}
</style>

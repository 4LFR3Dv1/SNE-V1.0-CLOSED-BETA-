<template>
  <div class="automated-trading">
    <!-- Header -->
    <div class="trading-header">
      <div class="header-left">
        <h1 class="page-title">
          🏦 TRADING AUTOMATIZADO
          <span class="subtitle">Cockpit de Execução</span>
        </h1>
      </div>
      <div class="header-right">
        <div class="status-indicator" :class="executionStatus">
          <div class="status-dot"></div>
          <span>{{ statusLabel }}</span>
        </div>
        <div class="total-pnl" :class="totalPnL >= 0 ? 'profit' : 'loss'">
          <span class="pnl-label">Total P&L:</span>
          <span class="pnl-value">
            {{ totalPnL >= 0 ? '+' : '' }}${{ formatNumber(totalPnL) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Layout: 3 Colunas (Cockpit) -->
    <div class="cockpit-layout">
      <!-- Coluna Esquerda: Motor e Pools -->
      <div class="cockpit-column left-column">
        <div class="column-header">
          <h2>🤖 MOTOR SNE AUTÔNOMO</h2>
        </div>
        
        <AutoPilotStatus />
        
        <GlobalConfigPanel />
        
        <div class="column-header">
          <h2>💰 POOLS DE ALOCAÇÃO</h2>
          <button @click="showCreatePool = true" class="btn-new">
            + Novo Pool
          </button>
        </div>
        
        <div class="pools-list">
          <PoolCard
            v-for="pool in pools"
            :key="pool.id"
            :pool="pool"
            @start="handleStartPool"
            @stop="handleStopPool"
            @edit="handleEditPool"
            @delete="handleDeletePool"
          />
          <div v-if="pools.length === 0" class="empty-state">
            Nenhum pool criado. Crie um pool para começar.
          </div>
        </div>
        
        <ExecutionControl
          :execution-status="executionStatus"
          :loading="loading"
          @start-all="handleStartAll"
          @pause-all="handlePauseAll"
          @stop-all="handleStopAll"
          @panic="handlePanic"
        />
      </div>

      <!-- Coluna Centro: Execução (Terminal de Log) -->
      <div class="cockpit-column center-column">
        <div class="column-header">
          <h2>📺 TERMINAL DE LOG</h2>
        </div>
        
        <TerminalLog
          :logs="terminalLogs"
          @clear="clearTerminalLogs"
        />
        
        <div class="orders-section">
          <h3>📋 ORDENS PENDENTES</h3>
          <div v-if="pendingOrders.length === 0" class="empty-state">
            Nenhuma ordem pendente
          </div>
          <div v-else class="orders-list">
            <div 
              v-for="order in pendingOrders.slice(0, 5)" 
              :key="order.id"
              class="order-item"
            >
              <span class="order-symbol">{{ order.symbol }}</span>
              <span class="order-side" :class="order.side">{{ order.side.toUpperCase() }}</span>
              <span class="order-quantity">{{ formatNumber(order.quantity) }}</span>
              <span class="order-status">{{ order.status }}</span>
            </div>
          </div>
        </div>
        
        <PositionMonitor
          :positions="openPositions"
          @close="handleClosePosition"
        />
      </div>

      <!-- Coluna Direita: Financeiro -->
      <div class="cockpit-column right-column">
        <div class="column-header">
          <h2>💰 FINANCEIRO</h2>
        </div>
        
        <PortfolioOverview :portfolio="portfolio" />
        
        <ExposureMeter :portfolio="portfolio" />
        
        <PerformanceChart
          :performance="performance"
          :equity-data="equityData"
          @period-change="handlePeriodChange"
        />
        
        <RiskDashboard :alerts="riskAlerts" />
      </div>
    </div>

    <!-- Modal de Criação de Pool -->
    <div v-if="showCreatePool" class="modal-overlay" @click="showCreatePool = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>➕ Criar Novo Pool de Alocação</h3>
          <button @click="showCreatePool = false" class="btn-close-modal">×</button>
        </div>
        
        <form @submit.prevent="handleCreatePool" class="strategy-form">
          <div class="form-group">
            <label>Nome do Pool *</label>
            <input 
              v-model="newPool.name" 
              type="text" 
              placeholder="Ex: Scalper BTC"
              required
            />
          </div>
          
          <div class="form-group">
            <label>Descrição</label>
            <textarea 
              v-model="newPool.description" 
              placeholder="Descrição do pool..."
              rows="2"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>Capital Alocado ($) *</label>
            <input 
              v-model.number="newPool.capital_allocated" 
              type="number" 
              step="100"
              min="100"
              placeholder="5000"
              required
            />
            <small>Valor em dólares (ex: 5000)</small>
          </div>
          
          <div class="form-group">
            <label>Símbolos * (separados por vírgula)</label>
            <input 
              v-model="newPool.symbolsInput" 
              type="text" 
              placeholder="BTCUSDT, ETHUSDT"
              required
            />
            <small>Ex: BTCUSDT, ETHUSDT</small>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Risco por Trade (%) *</label>
              <input 
                v-model.number="newPool.risk_per_trade_pct" 
                type="number" 
                step="0.1"
                min="0.1"
                max="5"
                placeholder="1.0"
                required
              />
            </div>
            
            <div class="form-group">
              <label>Máximo de Posições</label>
              <input 
                v-model.number="newPool.max_positions" 
                type="number" 
                min="1"
                max="20"
                placeholder="5"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>Confluência Mínima (%)</label>
            <input 
              v-model.number="newPool.min_confluencia" 
              type="number" 
              step="1"
              min="0"
              max="100"
              placeholder="Deixe vazio para usar o global"
            />
            <small>Deixe vazio para usar o valor global</small>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showCreatePool = false" class="btn-cancel">
              Cancelar
            </button>
            <button type="submit" class="btn-submit" :disabled="creatingPool">
              {{ creatingPool ? 'Criando...' : 'Criar Pool' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTradingStore } from '../stores/trading'
import StrategyCard from '../components/trading/StrategyCard.vue'
import PoolCard from '../components/trading/PoolCard.vue'
import AutoPilotStatus from '../components/trading/AutoPilotStatus.vue'
import GlobalConfigPanel from '../components/trading/GlobalConfigPanel.vue'
import TerminalLog from '../components/trading/TerminalLog.vue'
import PositionMonitor from '../components/trading/PositionMonitor.vue'
import ExecutionControl from '../components/trading/ExecutionControl.vue'
import PortfolioOverview from '../components/trading/PortfolioOverview.vue'
import ExposureMeter from '../components/trading/ExposureMeter.vue'
import PerformanceChart from '../components/trading/PerformanceChart.vue'
import RiskDashboard from '../components/trading/RiskDashboard.vue'

const tradingStore = useTradingStore()

// State local
const showCreatePool = ref(false)
const creatingPool = ref(false)
const equityData = ref([])
let updateInterval = null

// Computed do store - Pools
const pools = computed(() => tradingStore.pools)

// Formulário de novo pool
const newPool = ref({
  name: '',
  description: '',
  symbolsInput: 'BTCUSDT',
  capital_allocated: 5000,
  risk_per_trade_pct: 1.0,
  max_positions: 5,
  min_confluencia: null
})

// Computed do store
const strategies = computed(() => tradingStore.strategies)
const positions = computed(() => tradingStore.positions)
const openPositions = computed(() => tradingStore.openPositions)
const orders = computed(() => tradingStore.orders)
const pendingOrders = computed(() => tradingStore.pendingOrders)
const portfolio = computed(() => tradingStore.portfolio)
const performance = computed(() => tradingStore.performance)
const riskAlerts = computed(() => tradingStore.riskAlerts)
const terminalLogs = computed(() => tradingStore.terminalLogs)
const loading = computed(() => tradingStore.loading)
const executionStatus = computed(() => tradingStore.executionStatus)
const totalPnL = computed(() => tradingStore.totalPnL)

const statusLabel = computed(() => {
  const labels = {
    'running': 'Executando',
    'paused': 'Pausado',
    'stopped': 'Parado'
  }
  return labels[executionStatus.value] || 'Desconhecido'
})

// Handlers
const handleStartStrategy = async (id) => {
  try {
    await tradingStore.startStrategy(id)
  } catch (err) {
    console.error('Erro ao iniciar estratégia:', err)
  }
}

const handlePauseStrategy = async (id) => {
  try {
    await tradingStore.pauseStrategy(id)
  } catch (err) {
    console.error('Erro ao pausar estratégia:', err)
  }
}

const handleStopStrategy = async (id) => {
  try {
    await tradingStore.stopStrategy(id)
  } catch (err) {
    console.error('Erro ao parar estratégia:', err)
  }
}

const handleEditStrategy = (id) => {
  tradingStore.addTerminalLog('INFO', `Editando estratégia ${id} (funcionalidade em desenvolvimento)`)
}

// Handlers - Pools
const handleStartPool = async (id) => {
  try {
    await tradingStore.startPool(id)
  } catch (err) {
    console.error('Erro ao ativar pool:', err)
  }
}

const handleStopPool = async (id) => {
  try {
    await tradingStore.stopPool(id)
  } catch (err) {
    console.error('Erro ao desativar pool:', err)
  }
}

const handleEditPool = (id) => {
  tradingStore.addTerminalLog('INFO', `Editando pool ${id} (funcionalidade em desenvolvimento)`)
}

const handleDeletePool = async (id) => {
  if (!confirm('Tem certeza que deseja deletar este pool?')) {
    return
  }
  
  try {
    await tradingStore.deletePool(id)
  } catch (err) {
    console.error('Erro ao deletar pool:', err)
  }
}

const handleCreatePool = async () => {
  try {
    creatingPool.value = true
    
    // Converter símbolos de string para array
    const symbols = newPool.value.symbolsInput
      .split(',')
      .map(s => s.trim().toUpperCase())
      .filter(s => s.length > 0)
    
    if (symbols.length === 0) {
      tradingStore.addTerminalLog('ERROR', 'Pelo menos um símbolo é obrigatório')
      return
    }
    
    const poolData = {
      name: newPool.value.name,
      description: newPool.value.description,
      symbols: symbols,
      capital_allocated: newPool.value.capital_allocated,
      risk_per_trade_pct: newPool.value.risk_per_trade_pct,
      max_positions: newPool.value.max_positions,
      min_confluencia: newPool.value.min_confluencia || null
    }
    
    tradingStore.addTerminalLog('INFO', `Criando pool "${poolData.name}"...`)
    
    await tradingStore.createPool(poolData)
    
    // Resetar formulário
    newPool.value = {
      name: '',
      description: '',
      symbolsInput: 'BTCUSDT',
      capital_allocated: 5000,
      risk_per_trade_pct: 1.0,
      max_positions: 5,
      min_confluencia: null
    }
    
    showCreatePool.value = false
    tradingStore.addTerminalLog('SUCCESS', `Pool "${poolData.name}" criado com sucesso!`)
    
  } catch (err) {
    console.error('Erro ao criar pool:', err)
    tradingStore.addTerminalLog('ERROR', `Erro ao criar pool: ${err.message}`)
  } finally {
    creatingPool.value = false
  }
}

const handleStartAll = async () => {
  tradingStore.addTerminalLog('INFO', 'Iniciando todas as estratégias...')
  for (const strategy of strategies.value) {
    if (strategy.status === 'inactive' || strategy.status === 'stopped') {
      await handleStartStrategy(strategy.id)
    }
  }
}

const handlePauseAll = async () => {
  tradingStore.addTerminalLog('INFO', 'Pausando todas as estratégias...')
  for (const strategy of strategies.value) {
    if (strategy.status === 'active') {
      await handlePauseStrategy(strategy.id)
    }
  }
}

const handleStopAll = async () => {
  tradingStore.addTerminalLog('WARNING', 'Parando todas as estratégias...')
  for (const strategy of strategies.value) {
    if (strategy.status === 'active' || strategy.status === 'paused') {
      await handleStopStrategy(strategy.id)
    }
  }
}

const handlePanic = async () => {
  try {
    await tradingStore.panicCloseAll()
  } catch (err) {
    console.error('Erro no Panic Close:', err)
  }
}

const handleClosePosition = async (id) => {
  tradingStore.addTerminalLog('INFO', `Fechando posição ${id}...`)
  // TODO: Implementar fechamento de posição
}

const handlePeriodChange = async (period) => {
  await tradingStore.fetchPerformance(period)
}

const clearTerminalLogs = () => {
  tradingStore.clearTerminalLogs()
}

const formatNumber = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// Lifecycle
onMounted(async () => {
  tradingStore.addTerminalLog('INFO', '🚀 Trading Automatizado iniciado')
  tradingStore.addTerminalLog('INFO', 'Carregando dados...')
  
  await tradingStore.initialize()
  
  tradingStore.addTerminalLog('SUCCESS', '✅ Dados carregados com sucesso')
  
  // Atualizar dados periodicamente
  updateInterval = setInterval(async () => {
    await Promise.all([
      tradingStore.fetchPositions(),
      tradingStore.fetchOrders(),
      tradingStore.fetchPortfolio(),
      tradingStore.fetchRiskAlerts()
    ])
  }, 10000) // A cada 10 segundos
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.automated-trading {
  min-height: 100vh;
  background: #0a0a0a;
  color: #00ff00;
  padding: 24px;
  font-family: 'Courier New', monospace;
}

.trading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(0, 255, 0, 0.3);
}

.page-title {
  margin: 0;
  color: #00ff00;
  font-size: 28px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.subtitle {
  font-size: 12px;
  color: rgba(0, 255, 0, 0.6);
  text-transform: uppercase;
  font-weight: normal;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 20px;
  background: rgba(0, 255, 0, 0.1);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #666;
}

.status-indicator.running .status-dot {
  background: #00ff00;
  box-shadow: 0 0 10px #00ff00;
  animation: pulse 2s infinite;
}

.status-indicator.paused .status-dot {
  background: #ffff00;
  box-shadow: 0 0 10px #ffff00;
}

.status-indicator.stopped .status-dot {
  background: #ff0000;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.total-pnl {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.pnl-label {
  font-size: 11px;
  color: rgba(0, 255, 0, 0.6);
  text-transform: uppercase;
}

.pnl-value {
  font-size: 24px;
  font-weight: bold;
}

.total-pnl.profit .pnl-value {
  color: #00ff00;
}

.total-pnl.loss .pnl-value {
  color: #ff0000;
}

/* Layout Cockpit: 3 Colunas */
.cockpit-layout {
  display: grid;
  grid-template-columns: 350px 1fr 350px;
  gap: 24px;
  height: calc(100vh - 200px);
}

.cockpit-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.column-header h2 {
  margin: 0;
  color: #00ff00;
  font-size: 16px;
  text-transform: uppercase;
}

.btn-new {
  padding: 6px 12px;
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid rgba(0, 255, 0, 0.3);
  color: #00ff00;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.btn-new:hover {
  background: rgba(0, 255, 0, 0.3);
}

.strategies-list {
  flex: 1;
  overflow-y: auto;
}

.orders-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 255, 0, 0.2);
}

.orders-section h3 {
  margin: 0 0 12px 0;
  color: #00ff00;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: rgba(0, 255, 0, 0.4);
  font-style: italic;
  font-size: 12px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 0, 0.2);
  border-radius: 4px;
  font-size: 11px;
}

.order-symbol {
  font-weight: bold;
  color: #00ff00;
}

.order-side {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: bold;
}

.order-side.buy {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
}

.order-side.sell {
  background: rgba(255, 0, 0, 0.2);
  color: #ff0000;
}

.order-quantity {
  color: rgba(0, 255, 0, 0.8);
}

.order-status {
  color: rgba(0, 255, 0, 0.6);
  text-transform: uppercase;
  font-size: 9px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(10, 10, 10, 0.95);
  border: 2px solid rgba(0, 255, 0, 0.5);
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  color: #00ff00;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 255, 0, 0.2);
}

.modal-header h3 {
  margin: 0;
  color: #00ff00;
}

.btn-close-modal {
  background: transparent;
  border: none;
  color: #00ff00;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-close-modal:hover {
  background: rgba(255, 0, 0, 0.2);
}

.strategy-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  color: rgba(0, 255, 0, 0.9);
  font-size: 13px;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 10px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 4px;
  color: #00ff00;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #00ff00;
  box-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
}

.form-group small {
  color: rgba(0, 255, 0, 0.5);
  font-size: 11px;
  font-style: italic;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 255, 0, 0.2);
}

.btn-cancel {
  padding: 10px 20px;
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.5);
  border-radius: 4px;
  color: #ff0000;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: rgba(255, 0, 0, 0.3);
}

.btn-submit {
  padding: 10px 20px;
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid rgba(0, 255, 0, 0.5);
  border-radius: 4px;
  color: #00ff00;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: rgba(0, 255, 0, 0.3);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-note {
  color: rgba(0, 255, 0, 0.7);
  margin-bottom: 16px;
  font-size: 12px;
}

.btn-close-modal-old {
  padding: 8px 16px;
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.3);
  color: #ff0000;
  border-radius: 4px;
  cursor: pointer;
}

/* Scrollbar */
.cockpit-column::-webkit-scrollbar {
  width: 6px;
}

.cockpit-column::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.5);
}

.cockpit-column::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 0, 0.3);
  border-radius: 3px;
}

.cockpit-column::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 0, 0.5);
}

/* Responsive */
@media (max-width: 1400px) {
  .cockpit-layout {
    grid-template-columns: 300px 1fr 300px;
  }
}

@media (max-width: 1200px) {
  .cockpit-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .cockpit-column {
    max-height: 600px;
  }
}
</style>


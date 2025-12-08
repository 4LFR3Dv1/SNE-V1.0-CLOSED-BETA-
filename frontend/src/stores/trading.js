import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import tradingApi from '../services/tradingApi'

export const useTradingStore = defineStore('trading', () => {
  // State
  const strategies = ref([])
  const positions = ref([])
  const orders = ref([])
  const portfolio = ref(null)
  const performance = ref(null)
  const riskAlerts = ref([])
  const complianceLogs = ref([])
  const terminalLogs = ref([])
  
  const loading = ref(false)
  const error = ref(null)
  const executionStatus = ref('stopped') // 'running', 'paused', 'stopped'
  
  // Getters
  const activeStrategies = computed(() => 
    strategies.value.filter(s => s.status === 'active')
  )
  
  const pausedStrategies = computed(() => 
    strategies.value.filter(s => s.status === 'paused')
  )
  
  const openPositions = computed(() => 
    positions.value.filter(p => p.status !== 'closed')
  )
  
  const pendingOrders = computed(() => 
    orders.value.filter(o => o.status === 'pending')
  )
  
  const criticalAlerts = computed(() => 
    riskAlerts.value.filter(a => a.severity === 'critical' && !a.resolved)
  )
  
  const totalPnL = computed(() => {
    if (!portfolio.value) return 0
    return portfolio.value.total_pnl || 0
  })
  
  const unrealizedPnL = computed(() => {
    if (!portfolio.value) return 0
    return portfolio.value.unrealized_pnl || 0
  })
  
  // Actions - Strategies
  const fetchStrategies = async () => {
    try {
      loading.value = true
      const response = await tradingApi.getStrategies()
      if (response.success) {
        strategies.value = response.strategies || []
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao buscar estratégias: ${err.message}`)
    } finally {
      loading.value = false
    }
  }
  
  const createStrategy = async (data) => {
    try {
      loading.value = true
      const response = await tradingApi.createStrategy(data)
      if (response.success) {
        await fetchStrategies()
        addTerminalLog('SUCCESS', `Estratégia "${data.name}" criada com sucesso`)
        return response.strategy
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao criar estratégia: ${err.message}`)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const startStrategy = async (id) => {
    try {
      const response = await tradingApi.startStrategy(id)
      if (response.success) {
        await fetchStrategies()
        const strategy = strategies.value.find(s => s.id === id)
        addTerminalLog('INFO', `Estratégia "${strategy?.name || id}" iniciada`)
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao iniciar estratégia: ${err.message}`)
      throw err
    }
  }
  
  const stopStrategy = async (id) => {
    try {
      const response = await tradingApi.stopStrategy(id)
      if (response.success) {
        await fetchStrategies()
        const strategy = strategies.value.find(s => s.id === id)
        addTerminalLog('INFO', `Estratégia "${strategy?.name || id}" parada`)
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao parar estratégia: ${err.message}`)
      throw err
    }
  }
  
  const pauseStrategy = async (id) => {
    try {
      const response = await tradingApi.pauseStrategy(id)
      if (response.success) {
        await fetchStrategies()
        const strategy = strategies.value.find(s => s.id === id)
        addTerminalLog('INFO', `Estratégia "${strategy?.name || id}" pausada`)
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao pausar estratégia: ${err.message}`)
      throw err
    }
  }
  
  // Actions - Positions
  const fetchPositions = async () => {
    try {
      const response = await tradingApi.getPositions()
      if (response.success) {
        positions.value = response.positions || []
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao buscar posições: ${err.message}`)
    }
  }
  
  // Actions - Orders
  const fetchOrders = async (status = null) => {
    try {
      const response = await tradingApi.getOrders({ status })
      if (response.success) {
        orders.value = response.orders || []
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao buscar ordens: ${err.message}`)
    }
  }
  
  // Actions - Portfolio
  const fetchPortfolio = async () => {
    try {
      const response = await tradingApi.getPortfolio()
      if (response.success) {
        portfolio.value = response.portfolio
      }
    } catch (err) {
      error.value = err.message
    }
  }
  
  const fetchPerformance = async (periodDays = 30) => {
    try {
      const response = await tradingApi.getPerformance(periodDays)
      if (response.success) {
        performance.value = response.performance
      }
    } catch (err) {
      error.value = err.message
    }
  }
  
  // Actions - Risk Alerts
  const fetchRiskAlerts = async () => {
    try {
      const response = await tradingApi.getRiskAlerts(false)
      if (response.success) {
        riskAlerts.value = response.alerts || []
      }
    } catch (err) {
      error.value = err.message
    }
  }
  
  // Actions - Terminal Logs
  const addTerminalLog = (type, message) => {
    const timestamp = new Date().toLocaleTimeString('pt-BR')
    terminalLogs.value.push({
      id: Date.now(),
      type, // 'INFO', 'SUCCESS', 'WARNING', 'ERROR'
      message,
      timestamp
    })
    
    // Manter apenas últimos 100 logs
    if (terminalLogs.value.length > 100) {
      terminalLogs.value.shift()
    }
  }
  
  const clearTerminalLogs = () => {
    terminalLogs.value = []
  }
  
  // Actions - Emergency
  const panicCloseAll = async () => {
    try {
      loading.value = true
      addTerminalLog('WARNING', '🚨 PANIC CLOSE ALL iniciado...')
      const response = await tradingApi.panicCloseAll()
      if (response.success) {
        addTerminalLog('SUCCESS', `Panic Close: ${response.closed_count} posições fechadas`)
        await fetchPositions()
        await fetchOrders()
      }
      return response
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro no Panic Close: ${err.message}`)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // Initialize
  // State - Pools
  const pools = ref([])
  const autopilotStatus = ref(null)
  const autopilotConfig = ref(null)
  
  // Getters - Pools
  const activePools = computed(() => 
    pools.value.filter(p => p.status === 'active')
  )
  
  const totalCapitalAllocated = computed(() => 
    pools.value.reduce((sum, p) => sum + (p.capital_allocated || 0), 0)
  )
  
  // Actions - Pools
  const fetchPools = async () => {
    try {
      loading.value = true
      const response = await tradingApi.getPools()
      if (response.success) {
        pools.value = response.pools || []
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao buscar pools: ${err.message}`)
    } finally {
      loading.value = false
    }
  }
  
  const createPool = async (data) => {
    try {
      loading.value = true
      const response = await tradingApi.createPool(data)
      if (response.success) {
        await fetchPools()
        addTerminalLog('SUCCESS', `Pool "${data.name}" criado com sucesso`)
        return response.pool
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao criar pool: ${err.message}`)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const updatePool = async (id, data) => {
    try {
      const response = await tradingApi.updatePool(id, data)
      if (response.success) {
        await fetchPools()
        addTerminalLog('SUCCESS', `Pool atualizado com sucesso`)
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao atualizar pool: ${err.message}`)
      throw err
    }
  }
  
  const deletePool = async (id) => {
    try {
      const response = await tradingApi.deletePool(id)
      if (response.success) {
        await fetchPools()
        addTerminalLog('SUCCESS', `Pool deletado com sucesso`)
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao deletar pool: ${err.message}`)
      throw err
    }
  }
  
  const startPool = async (id) => {
    try {
      const response = await tradingApi.startPool(id)
      if (response.success) {
        await fetchPools()
        const pool = pools.value.find(p => p.id === id)
        addTerminalLog('INFO', `Pool "${pool?.name || id}" ativado`)
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao ativar pool: ${err.message}`)
      throw err
    }
  }
  
  const stopPool = async (id) => {
    try {
      const response = await tradingApi.stopPool(id)
      if (response.success) {
        await fetchPools()
        const pool = pools.value.find(p => p.id === id)
        addTerminalLog('INFO', `Pool "${pool?.name || id}" desativado`)
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao desativar pool: ${err.message}`)
      throw err
    }
  }
  
  // Actions - AutoPilot
  const fetchAutopilotStatus = async () => {
    try {
      const response = await tradingApi.getAutopilotStatus()
      if (response.success) {
        autopilotStatus.value = response
        executionStatus.value = response.motor_enabled ? 'running' : 'stopped'
      }
    } catch (err) {
      error.value = err.message
    }
  }
  
  const fetchAutopilotConfig = async () => {
    try {
      const response = await tradingApi.getAutopilotConfig()
      if (response.success) {
        autopilotConfig.value = response.config
      }
    } catch (err) {
      error.value = err.message
    }
  }
  
  const updateAutopilotConfig = async (data) => {
    try {
      const response = await tradingApi.updateAutopilotConfig(data)
      if (response.success) {
        await fetchAutopilotConfig()
        addTerminalLog('SUCCESS', 'Configuração do motor atualizada')
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao atualizar configuração: ${err.message}`)
      throw err
    }
  }
  
  const startAutopilot = async () => {
    try {
      const response = await tradingApi.startAutopilot()
      if (response.success) {
        await fetchAutopilotStatus()
        addTerminalLog('SUCCESS', 'Motor autônomo iniciado')
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao iniciar motor: ${err.message}`)
      throw err
    }
  }
  
  const stopAutopilot = async () => {
    try {
      const response = await tradingApi.stopAutopilot()
      if (response.success) {
        await fetchAutopilotStatus()
        addTerminalLog('WARNING', 'Motor autônomo parado')
      }
    } catch (err) {
      error.value = err.message
      addTerminalLog('ERROR', `Erro ao parar motor: ${err.message}`)
      throw err
    }
  }
  
  const initialize = async () => {
    await Promise.all([
      fetchPools(),
      fetchAutopilotStatus(),
      fetchAutopilotConfig(),
      fetchStrategies(),
      fetchPositions(),
      fetchOrders(),
      fetchPortfolio(),
      fetchRiskAlerts()
    ])
  }
  
  return {
    // State
    strategies,
    positions,
    orders,
    portfolio,
    performance,
    riskAlerts,
    complianceLogs,
    terminalLogs,
    loading,
    error,
    executionStatus,
    pools,
    autopilotStatus,
    autopilotConfig,
    
    // Getters
    activeStrategies,
    pausedStrategies,
    openPositions,
    pendingOrders,
    criticalAlerts,
    totalPnL,
    unrealizedPnL,
    activePools,
    totalCapitalAllocated,
    
    // Actions
    fetchStrategies,
    createStrategy,
    startStrategy,
    stopStrategy,
    pauseStrategy,
    fetchPositions,
    fetchOrders,
    fetchPortfolio,
    fetchPerformance,
    fetchRiskAlerts,
    addTerminalLog,
    clearTerminalLogs,
    panicCloseAll,
    // Pools
    fetchPools,
    createPool,
    updatePool,
    deletePool,
    startPool,
    stopPool,
    // AutoPilot
    fetchAutopilotStatus,
    fetchAutopilotConfig,
    updateAutopilotConfig,
    startAutopilot,
    stopAutopilot,
    initialize
  }
})


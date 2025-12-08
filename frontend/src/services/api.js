import axios from 'axios'

// Detectar se está rodando no Electron (produção) ou navegador (desenvolvimento)
const isElectron = typeof window !== 'undefined' && window.electronAPI

// URL da API: Cloud em produção (Electron), local em desenvolvimento
const getBaseURL = () => {
  // Se estiver no Electron (app desktop), usar API cloud
  if (isElectron) {
    return import.meta.env.VUE_APP_API_URL || import.meta.env.VITE_API_URL || 'https://api.sne-radar.com/api/v1'
  }
  
  // Se estiver em desenvolvimento (navegador), usar local ou proxy
  if (import.meta.env.DEV) {
    return import.meta.env.VITE_API_URL || '/api'
  }
  
  // Produção web (se houver)
  return import.meta.env.VITE_API_URL || '/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  // Em Electron, não usar cookies (usar JWT)
  // Em desenvolvimento local, usar cookies para Flask-Login
  withCredentials: !isElectron
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // Em Electron (cloud), usar JWT token
    // Em desenvolvimento local, usar cookies (Flask-Login)
    if (isElectron) {
      const token = localStorage.getItem('jwt_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } else {
      // Modo desenvolvimento: usar cookies
      config.withCredentials = true
      // Também tentar token se existir
      const token = localStorage.getItem('token') || localStorage.getItem('jwt_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  response => {
    // Cloud API retorna { success: true, data: {...} }
    // Se for formato cloud, retornar data diretamente
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      if (response.data.success) {
        return response.data.data || response.data
      } else {
        // Erro no formato cloud
        throw new Error(response.data.error || 'Erro na requisição')
      }
    }
    // Formato tradicional (desenvolvimento local)
    return response.data
  },
  error => {
    // Tratar erro 401 (não autenticado)
    if (error.response?.status === 401) {
      // Limpar token
      localStorage.removeItem('jwt_token')
      localStorage.removeItem('token')
      
      // Se estiver no Electron, redirecionar para login
      if (isElectron && window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    const message = error.response?.data?.error || error.message || 'Erro na requisição'
    console.error('API Error:', message, error)
    return Promise.reject(new Error(message))
  }
)

export default {
  // Auth (Cloud API)
  login: (username, password) => api.post('/auth/login', { username, password }),
  verifyToken: () => api.get('/auth/verify'),
  
  // Health
  health: () => api.get('/health'),
  
  // Analysis (Cloud API)
  analyze: (symbol, timeframe) => 
    api.post('/analyze', { symbol, timeframe }),
  
  // Trading (Cloud API)
  getAutopilotStatus: () => api.get('/trading/autopilot/status'),
  startAutopilot: () => api.post('/trading/autopilot/start'),
  stopAutopilot: () => api.post('/trading/autopilot/stop'),
  getPositions: () => api.get('/trading/positions'),
  getPortfolio: () => api.get('/trading/portfolio'),
  
  // Market Data (Cloud API)
  getSymbols: () => api.get('/market/symbols'),
  getPrice: (symbol) => api.get(`/market/price/${symbol}`),
  
  getSignal: (symbol, timeframe) => 
    api.get('/signal', { params: { symbol, timeframe } }),
  
  // Market Data
  getCandles: (symbol, timeframe, limit = 500) =>
    api.get('/market/candles', { 
      params: { symbol, timeframe, limit } 
    }),
  
  // Magnetic Field (deprecated - usar getLiquidityHeatmap)
  getMagneticField: (symbol) =>
    api.get('/magnetic/field', { params: { symbol } }),
  
  // Liquidity Heatmap
  getLiquidityHeatmap: (symbol, limit = 5000, precision = 2) =>
    api.get('/v1/magnetic/liquidity', { 
      params: { symbol, limit, precision } 
    }),
  
  // Backtesting
  runBacktest: (config) =>
    api.post('/backtest/run', config),
  
  getBacktestResults: (id) =>
    api.get(`/backtest/results/${id}`),
  
  // Alerts
  getAlerts: () => api.get('/alerts'),
  createAlert: (alert) => api.post('/alerts', alert),
  deleteAlert: (id) => api.delete(`/alerts/${id}`),
  
  // User
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data) => api.put('/user/profile', data),
  
  // Chart Data
  getCandles: (symbol, interval = '1h', limit = 500) => {
    return api.get('/v1/candles', {
      params: { symbol, interval, limit }
    }).then(response => {
      // A API retorna { success: true, data: { candles: [...] } }
      // Retornar diretamente o objeto response (interceptor já extraiu response.data)
      return response
    })
  },
  
  getChartLevels: (symbol, timeframe = '1h') => {
    return api.get('/chart/levels', {
      params: { symbol, timeframe }
    })
  },
  
  getAdvancedIndicators: (symbol, interval = '1h', limit = 500) => {
    return api.get('/v1/advanced-indicators', {
      params: { symbol, interval, limit }
    })
  },
  
  // Chart Data (consolidated endpoint for interactive charts)
  getChartData: (symbol, interval = '1h', limit = 500) => {
    return api.get('/v1/chart-data', {
      params: { symbol, interval, limit }
    })
  },
  
  // Last Price (lightweight endpoint for polling)
  getLastPrice: (symbol, interval = '1h') => {
    return api.get('/v1/last-price', {
      params: { symbol, interval }
    })
  },
  
  // Global Metrics
  getGlobalMetrics: () => api.get('/v1/global-metrics'),
  
  // Derivatives
  getDerivatives: () => api.get('/v1/derivatives'),
  
  // TA Summary
  getTASummary: (symbol) => api.get('/v1/ta-summary', { params: { symbol } }),
  
  // System Status
  getSystemStatus: () => api.get('/v1/system/status'),
  
  // Alerts (with v1 prefix)
  getAlertsV1: () => api.get('/v1/alerts'),
  createAlertV1: (alert) => api.post('/v1/alerts', alert),
  deleteAlertV1: (id) => api.delete(`/v1/alerts/${id}`),
  getTriggeredAlerts: () => api.get('/v1/alerts/triggered'),
  
  // Symbol Search
  searchSymbols: (query, limit = 20) => 
    api.get('/v1/symbols/search', { params: { q: query, limit } }),
  
  // Notifications & Monitor
  getNotificationsStats: () => api.get('/v1/notifications/stats'),
  getNotificationsHistory: () => api.get('/v1/notifications/history'),
  getMonitorStatus: () => api.get('/v1/notifications/monitor/status'),
  startMonitor: () => api.post('/v1/notifications/monitor/start'),
  stopMonitor: () => api.post('/v1/notifications/monitor/stop')
}


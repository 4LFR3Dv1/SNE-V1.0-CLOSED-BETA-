import axios from 'axios'

// Criar instância do axios para trading API (mesma configuração do api.js)
const tradingApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// Request interceptor
tradingApi.interceptors.request.use(
  config => {
    config.withCredentials = true
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor (retorna response.data diretamente)
tradingApi.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.error || error.message || 'Erro na requisição'
    console.error('Trading API Error:', message, error)
    return Promise.reject(new Error(message))
  }
)

export default {
  // Strategies
  getStrategies: () => tradingApi.get('/trading/strategies'),
  createStrategy: (data) => tradingApi.post('/trading/strategies', data),
  getStrategy: (id) => tradingApi.get(`/trading/strategies/${id}`),
  updateStrategy: (id, data) => tradingApi.put(`/trading/strategies/${id}`, data),
  deleteStrategy: (id) => tradingApi.delete(`/trading/strategies/${id}`),
  startStrategy: (id) => tradingApi.post(`/trading/strategies/${id}/start`),
  stopStrategy: (id) => tradingApi.post(`/trading/strategies/${id}/stop`),
  pauseStrategy: (id) => tradingApi.post(`/trading/strategies/${id}/pause`),
  
  // Pools de Alocação
  getPools: () => tradingApi.get('/trading/pools'),
  createPool: (data) => tradingApi.post('/trading/pools', data),
  updatePool: (id, data) => tradingApi.put(`/trading/pools/${id}`, data),
  deletePool: (id) => tradingApi.delete(`/trading/pools/${id}`),
  startPool: (id) => tradingApi.post(`/trading/pools/${id}/start`),
  stopPool: (id) => tradingApi.post(`/trading/pools/${id}/stop`),
  
  // AutoPilot
  getAutopilotStatus: () => tradingApi.get('/trading/autopilot/status'),
  getAutopilotConfig: () => tradingApi.get('/trading/autopilot/config'),
  updateAutopilotConfig: (data) => tradingApi.put('/trading/autopilot/config', data),
  startAutopilot: () => tradingApi.post('/trading/autopilot/start'),
  stopAutopilot: () => tradingApi.post('/trading/autopilot/stop'),
  
  // Orders
  createOrder: (data) => tradingApi.post('/trading/orders', data),
  getOrders: (params) => tradingApi.get('/trading/orders', { params }),
  getOrder: (id) => tradingApi.get(`/trading/orders/${id}`),
  cancelOrder: (id) => tradingApi.post(`/trading/orders/${id}/cancel`),
  
  // Positions
  getPositions: () => tradingApi.get('/trading/positions'),
  getPosition: (id) => tradingApi.get(`/trading/positions/${id}`),
  closePosition: (id) => tradingApi.post(`/trading/positions/${id}/close`),
  
  // Portfolio
  getPortfolio: () => tradingApi.get('/trading/portfolio'),
  getPerformance: (periodDays = 30) => tradingApi.get('/trading/portfolio/performance', { params: { period_days: periodDays } }),
  getReport: (periodDays = 30) => tradingApi.get('/trading/portfolio/report', { params: { period_days: periodDays } }),
  
  // Compliance
  getComplianceLogs: (days = 7) => tradingApi.get('/trading/compliance/logs', { params: { days } }),
  getRiskAlerts: (resolved = false) => tradingApi.get('/trading/compliance/risk-alerts', { params: { resolved } }),
  
  // Emergency
  panicCloseAll: () => tradingApi.post('/trading/emergency/panic-close-all')
}


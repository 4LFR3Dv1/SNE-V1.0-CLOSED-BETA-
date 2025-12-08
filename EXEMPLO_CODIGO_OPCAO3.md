# 💻 EXEMPLOS DE CÓDIGO - OPÇÃO 3

Exemplos práticos de implementação para a Opção 3 (Híbrida).

---

## 🔧 CONFIGURAÇÃO FLASK

### Modificação em `sne_radar_web.py`

```python
import os
from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO

# ============================================
# CONFIGURAÇÃO FRONTEND VUE.JS
# ============================================

# Caminhos do frontend build
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')
FRONTEND_STATIC = os.path.join(FRONTEND_DIR, 'assets')
FRONTEND_INDEX = os.path.join(FRONTEND_DIR, 'index.html')

# Verificar se frontend foi buildado
FRONTEND_EXISTS = os.path.exists(FRONTEND_INDEX)

# ============================================
# INICIALIZAÇÃO FLASK
# ============================================

app = Flask(__name__,
    static_folder=FRONTEND_STATIC if FRONTEND_EXISTS else None,
    template_folder=FRONTEND_DIR if FRONTEND_EXISTS else 'templates'
)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

socketio = SocketIO(app, cors_allowed_origins="*")

# ============================================
# ROTAS PARA SERVIR FRONTEND
# ============================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """
    Serve o frontend Vue.js.
    Vue Router cuida do roteamento no frontend.
    """
    if FRONTEND_EXISTS:
        # Arquivos estáticos (assets)
        if path.startswith('assets/'):
            return send_from_directory(FRONTEND_DIR, path)
        
        # Todas as outras rotas servem index.html
        # Vue Router cuida do roteamento
        return send_from_directory(FRONTEND_DIR, 'index.html')
    else:
        # Fallback: usar template antigo se frontend não estiver buildado
        from flask import render_template
        return render_template('dashboard.html')

# ============================================
# APIs (MANTÉM EXISTENTES)
# ============================================

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'frontend': FRONTEND_EXISTS,
        'service': 'sne-web'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Análise técnica completa"""
    from flask import request
    data = request.get_json()
    symbol = data.get('symbol', 'BTCUSDT')
    timeframe = data.get('timeframe', '1h')
    
    # ... código existente de análise ...
    result = {
        'symbol': symbol,
        'timeframe': timeframe,
        'signal': 'BUY',
        'score': 8.5
    }
    
    return jsonify(result)

# Todas as outras rotas /api/* continuam funcionando normalmente

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    if FRONTEND_EXISTS:
        print("✅ Frontend Vue.js detectado e será servido")
    else:
        print("⚠️ Frontend não encontrado. Use templates antigos.")
        print(f"   Build frontend: cd frontend && npm run build")
    
    socketio.run(app, host='0.0.0.0', port=9999, debug=True)
```

---

## 📱 COMPONENTE VUE: Dashboard

### `frontend/src/views/Dashboard.vue`

```vue
<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">Dashboard</h1>
      <p class="text-terminal-green/70">Visão geral do mercado</p>
    </div>

    <!-- Cards de Resumo -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="card">
        <div class="text-sm text-terminal-green/70 mb-1">BTC/USDT</div>
        <div class="text-2xl font-bold">$43,250</div>
        <div class="text-terminal-green text-sm">+2.5%</div>
      </div>
      
      <div class="card">
        <div class="text-sm text-terminal-green/70 mb-1">Sinais Hoje</div>
        <div class="text-2xl font-bold">{{ signalsCount }}</div>
        <div class="text-terminal-green text-sm">Ativos</div>
      </div>
      
      <div class="card">
        <div class="text-sm text-terminal-green/70 mb-1">Score Médio</div>
        <div class="text-2xl font-bold">{{ averageScore }}</div>
        <div class="text-terminal-green text-sm">Confluência</div>
      </div>
    </div>

    <!-- Top Oportunidades -->
    <div class="card mb-8">
      <h2 class="text-xl font-bold mb-4">Top Oportunidades</h2>
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner />
      </div>
      <div v-else-if="opportunities.length === 0" class="text-center py-8 text-terminal-green/70">
        Nenhuma oportunidade encontrada
      </div>
      <div v-else class="space-y-2">
        <div 
          v-for="opp in opportunities" 
          :key="opp.symbol"
          class="flex justify-between items-center p-3 bg-terminal-dark rounded border border-terminal-green/30 hover:border-terminal-green transition"
        >
          <div>
            <div class="font-bold">{{ opp.symbol }}</div>
            <div class="text-sm text-terminal-green/70">{{ opp.timeframe }}</div>
          </div>
          <div class="text-right">
            <div class="font-bold" :class="opp.signal === 'BUY' ? 'text-terminal-green' : 'text-red-500'">
              {{ opp.signal }}
            </div>
            <div class="text-sm">Score: {{ opp.score }}/10</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Gráfico Principal -->
    <div class="card">
      <h2 class="text-xl font-bold mb-4">Gráfico Principal</h2>
      <TradingChart 
        :symbol="selectedSymbol"
        :timeframe="selectedTimeframe"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMarketStore } from '@/stores/market'
import TradingChart from '@/components/charts/TradingChart.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import websocket from '@/services/websocket'

const marketStore = useMarketStore()

const selectedSymbol = ref('BTCUSDT')
const selectedTimeframe = ref('1h')
const opportunities = ref([])
const loading = ref(false)

const signalsCount = computed(() => opportunities.value.length)
const averageScore = computed(() => {
  if (opportunities.value.length === 0) return 0
  const sum = opportunities.value.reduce((acc, opp) => acc + opp.score, 0)
  return (sum / opportunities.value.length).toFixed(1)
})

const loadOpportunities = async () => {
  loading.value = true
  try {
    // Carregar top oportunidades
    const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']
    const results = await Promise.all(
      symbols.map(symbol => marketStore.analyze(symbol, '1h'))
    )
    
    opportunities.value = results
      .map((data, idx) => ({
        symbol: symbols[idx],
        timeframe: '1h',
        signal: data.signal || 'NEUTRAL',
        score: data.confluence_score || 0
      }))
      .filter(opp => opp.score >= 7)
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
  } catch (error) {
    console.error('Erro ao carregar oportunidades:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOpportunities()
  
  // Conectar WebSocket para updates em tempo real
  websocket.connect()
  websocket.on('market_update', (data) => {
    // Atualizar oportunidades quando receber update
    loadOpportunities()
  })
})
</script>
```

---

## 📊 COMPONENTE: Trading Chart

### `frontend/src/components/charts/TradingChart.vue`

```vue
<template>
  <div class="trading-chart">
    <div ref="chartContainer" class="w-full h-96"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  },
  timeframe: {
    type: String,
    default: '1h'
  }
})

const chartContainer = ref(null)
let chart = null
let candleSeries = null

const initChart = () => {
  if (!chartContainer.value) return

  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: {
      background: { color: '#000000' },
      textColor: '#00ff00',
    },
    grid: {
      vertLines: { color: '#1a1a1a' },
      horzLines: { color: '#1a1a1a' },
    },
  })

  candleSeries = chart.addCandlestickSeries({
    upColor: '#00ff00',
    downColor: '#ff0000',
    borderVisible: false,
    wickUpColor: '#00ff00',
    wickDownColor: '#ff0000',
  })

  // Carregar dados iniciais
  loadData()
}

const loadData = async () => {
  try {
    const response = await fetch(`/api/market/candles?symbol=${props.symbol}&timeframe=${props.timeframe}`)
    const data = await response.json()
    
    const candles = data.candles.map(c => ({
      time: c.time,
      open: parseFloat(c.open),
      high: parseFloat(c.high),
      low: parseFloat(c.low),
      close: parseFloat(c.close),
    }))
    
    candleSeries.setData(candles)
    chart.timeScale().fitContent()
  } catch (error) {
    console.error('Erro ao carregar dados:', error)
  }
}

watch([() => props.symbol, () => props.timeframe], () => {
  loadData()
})

onMounted(() => {
  initChart()
  
  // Redimensionar chart quando window resize
  window.addEventListener('resize', () => {
    if (chart && chartContainer.value) {
      chart.applyOptions({
        width: chartContainer.value.clientWidth
      })
    }
  })
})
</script>
```

---

## 🧲 COMPONENTE: Campo Magnético 3D

### `frontend/src/components/magnetic/MagneticField3D.vue`

```vue
<template>
  <div class="magnetic-field-3d">
    <div ref="container" class="w-full h-screen"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const props = defineProps({
  symbol: {
    type: String,
    default: 'BTCUSDT'
  }
})

const container = ref(null)
let scene, camera, renderer, zones = []

const initThreeJS = () => {
  if (!container.value) return

  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x000000)

  // Camera
  camera = new THREE.PerspectiveCamera(
    75,
    container.value.clientWidth / container.value.clientHeight,
    0.1,
    1000
  )
  camera.position.z = 5

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(container.value.clientWidth, container.value.clientHeight)
  container.value.appendChild(renderer.domElement)

  // Controls (opcional - adicionar OrbitControls se necessário)
  // const controls = new OrbitControls(camera, renderer.domElement)

  // Load magnetic zones
  loadMagneticZones()

  // Animation loop
  animate()
}

const loadMagneticZones = async () => {
  try {
    const response = await fetch(`/api/magnetic/field?symbol=${props.symbol}`)
    const data = await response.json()
    
    // Criar esferas para cada zona magnética
    data.zones.forEach(zone => {
      const geometry = new THREE.SphereGeometry(zone.radius, 32, 32)
      const material = new THREE.MeshBasicMaterial({
        color: zone.strength > 0.7 ? 0x00ff00 : 0x00aa00,
        transparent: true,
        opacity: 0.5
      })
      
      const sphere = new THREE.Mesh(geometry, material)
      sphere.position.set(zone.x, zone.y, zone.z)
      scene.add(sphere)
      zones.push(sphere)
    })
  } catch (error) {
    console.error('Erro ao carregar zonas magnéticas:', error)
  }
}

const animate = () => {
  requestAnimationFrame(animate)
  
  // Rotação suave das zonas
  zones.forEach((zone, index) => {
    zone.rotation.x += 0.01
    zone.rotation.y += 0.01
  })
  
  renderer.render(scene, camera)
}

onMounted(() => {
  initThreeJS()
})

onUnmounted(() => {
  // Cleanup
  if (renderer) {
    renderer.dispose()
  }
})
</script>
```

---

## 🔌 STORE: Market Store Completo

### `frontend/src/stores/market.js`

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useMarketStore = defineStore('market', () => {
  // State
  const currentSymbol = ref('BTCUSDT')
  const currentTimeframe = ref('1h')
  const analysisData = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // Getters
  const signal = computed(() => {
    if (!analysisData.value) return 'NEUTRAL'
    return analysisData.value.signal || 'NEUTRAL'
  })

  const score = computed(() => {
    if (!analysisData.value) return 0
    return analysisData.value.confluence_score || 0
  })

  const isBullish = computed(() => signal.value === 'BUY')
  const isBearish = computed(() => signal.value === 'SELL')

  // Actions
  const analyze = async (symbol, timeframe) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await api.analyze(symbol, timeframe)
      analysisData.value = data
      currentSymbol.value = symbol
      currentTimeframe.value = timeframe
      lastUpdate.value = new Date()
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSignal = async (symbol, timeframe) => {
    try {
      const data = await api.getSignal(symbol, timeframe)
      return data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const reset = () => {
    analysisData.value = null
    error.value = null
    loading.value = false
  }

  return {
    // State
    currentSymbol,
    currentTimeframe,
    analysisData,
    loading,
    error,
    lastUpdate,
    
    // Getters
    signal,
    score,
    isBullish,
    isBearish,
    
    // Actions
    analyze,
    getSignal,
    reset
  }
})
```

---

## 📡 SERVICE: API Service Completo

### `frontend/src/services/api.js`

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // Adicionar token se necessário
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.error || error.message || 'Erro na requisição'
    console.error('API Error:', message, error)
    return Promise.reject(new Error(message))
  }
)

export default {
  // Health
  health: () => api.get('/health'),
  
  // Analysis
  analyze: (symbol, timeframe) => 
    api.post('/analyze', { symbol, timeframe }),
  
  getSignal: (symbol, timeframe) => 
    api.get('/signal', { params: { symbol, timeframe } }),
  
  // Market Data
  getCandles: (symbol, timeframe, limit = 500) =>
    api.get('/market/candles', { 
      params: { symbol, timeframe, limit } 
    }),
  
  // Magnetic Field
  getMagneticField: (symbol) =>
    api.get('/magnetic/field', { params: { symbol } }),
  
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
  updateProfile: (data) => api.put('/user/profile', data)
}
```

---

## 🎨 COMPONENTE: Header

### `frontend/src/components/common/Header.vue`

```vue
<template>
  <header class="bg-terminal-gray border-b border-terminal-green">
    <div class="container mx-auto px-4 py-4">
      <div class="flex justify-between items-center">
        <!-- Logo -->
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-2xl font-bold text-terminal-green">
            🚀 SNE RADAR
          </router-link>
          <span class="text-sm text-terminal-green/70">
            Sistema Neural Estratégico
          </span>
        </div>

        <!-- Navigation -->
        <nav class="flex space-x-4">
          <router-link 
            to="/" 
            class="px-4 py-2 hover:text-terminal-green transition"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            Dashboard
          </router-link>
          <router-link 
            to="/analysis" 
            class="px-4 py-2 hover:text-terminal-green transition"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            Análise
          </router-link>
          <router-link 
            to="/magnetic" 
            class="px-4 py-2 hover:text-terminal-green transition"
            active-class="text-terminal-green border-b-2 border-terminal-green"
          >
            Campo Magnético
          </router-link>
        </nav>

        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <span class="text-sm text-terminal-green/70">
            {{ userStore.username || 'Usuário' }}
          </span>
          <button 
            @click="logout"
            class="px-4 py-2 bg-red-500/20 text-red-500 rounded hover:bg-red-500/30 transition"
          >
            Sair
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>
```

---

## 📝 ENV FILE

### `frontend/.env.example`

```env
# API URL (deixar vazio para usar relativo)
VITE_API_URL=

# WebSocket URL (deixar vazio para usar relativo)
VITE_WS_URL=

# Environment
VITE_ENV=development
```

### `frontend/.env.local` (não commitado)

```env
VITE_API_URL=http://localhost:9999/api
VITE_WS_URL=http://localhost:9999
VITE_ENV=development
```

---

## 🚀 SCRIPT DE DEPLOY

### `deploy_frontend.sh`

```bash
#!/bin/bash

set -e

PROJECT_ID="sne-v1"
REGION="europe-west1"
SERVICE_NAME="sne-web"

echo "🔨 Building frontend..."
cd frontend

# Instalar dependências se necessário
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Build
echo "🏗️ Building..."
npm run build

# Verificar build
if [ ! -f "dist/index.html" ]; then
  echo "❌ Build failed! dist/index.html not found"
  exit 1
fi

echo "✅ Frontend built successfully"
cd ..

echo "📦 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --port 9999

echo "✅ Deploy complete!"
echo "🌐 URL: https://$SERVICE_NAME-$(echo $REGION | tr '-' '')-$(gcloud config get-value project | cut -d'-' -f2).a.run.app"
```

---

**Status:** ✅ **EXEMPLOS COMPLETOS - PRONTO PARA USO**

**Criado em:** 26 de Novembro de 2025


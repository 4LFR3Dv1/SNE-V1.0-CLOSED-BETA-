# 🚀 PLANO DE DESENVOLVIMENTO - OPÇÃO 3 (HÍBRIDA)

**Arquitetura:** Flask serve Vue.js build  
**Objetivo:** Plataforma web moderna com deploy simples  
**Timeline:** 4-6 semanas (MVP)

---

## 📋 SUMÁRIO

1. [Visão Geral](#visão-geral)
2. [Setup Inicial](#setup-inicial)
3. [Estrutura de Projeto](#estrutura-de-projeto)
4. [Configuração Vue.js + Vite](#configuração-vuejs--vite)
5. [Integração com Flask](#integração-com-flask)
6. [Desenvolvimento Incremental](#desenvolvimento-incremental)
7. [Deploy](#deploy)
8. [Checklist Completo](#checklist-completo)

---

## 🎯 VISÃO GERAL

### Fluxo de Desenvolvimento

```
1. SETUP (Dia 1)
   ├─ Criar projeto Vue.js
   ├─ Configurar Vite
   └─ Estrutura básica

2. INTEGRAÇÃO FLASK (Dia 2-3)
   ├─ Configurar Flask para servir estáticos
   ├─ Rota catch-all para Vue Router
   └─ Testar integração

3. DESENVOLVIMENTO (Semana 1-4)
   ├─ Componentes base
   ├─ Páginas principais
   ├─ Integração APIs
   └─ Polimento

4. BUILD E DEPLOY (Semana 5-6)
   ├─ Otimização build
   ├─ Testes
   └─ Deploy produção
```

---

## 🛠️ SETUP INICIAL

### Pré-requisitos

```bash
# Verificar versões
node --version    # >= 18.0.0
npm --version     # >= 9.0.0
python3 --version # >= 3.8
```

### Passo 1: Criar Estrutura de Pastas

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Criar estrutura frontend
mkdir -p frontend/src/{components,views,stores,services,utils,router,assets}
mkdir -p frontend/public
mkdir -p frontend/dist  # Build output (será servido pelo Flask)

# Criar estrutura backend (melhorias)
mkdir -p backend/api/v1
mkdir -p backend/services
```

### Passo 2: Inicializar Projeto Vue.js

```bash
cd frontend

# Criar package.json
npm init -y

# Instalar dependências principais
npm install vue@^3.4.0 vue-router@^4.2.0 pinia@^2.1.0

# Instalar Vite e plugins
npm install -D vite@^5.0.0 @vitejs/plugin-vue

# Instalar bibliotecas de UI e utilidades
npm install axios@^1.6.0 socket.io-client@^4.7.2
npm install three@^0.160.0 lightweight-charts@^4.1.0
npm install date-fns@^3.0.0

# Instalar Tailwind CSS (opcional mas recomendado)
npm install -D tailwindcss@^3.4.0 postcss@^8.4.0 autoprefixer@^10.4.0
npx tailwindcss init -p
```

### Passo 3: Configurar Vite

**`frontend/vite.config.js`:**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'charts': ['lightweight-charts'],
          'three': ['three']
        }
      }
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:9999',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:9999',
        ws: true
      }
    }
  }
})
```

### Passo 4: Configurar Tailwind CSS

**`frontend/tailwind.config.js`:**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'terminal-green': '#00ff00',
        'terminal-dark': '#000000',
        'terminal-gray': '#1a1a1a',
      },
      fontFamily: {
        'mono': ['Courier New', 'monospace'],
      }
    },
  },
  plugins: [],
}
```

**`frontend/src/assets/css/main.css`:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-terminal-dark text-terminal-green font-mono;
  }
}

@layer components {
  .btn-primary {
    @apply bg-terminal-green text-terminal-dark px-4 py-2 rounded font-bold hover:opacity-80 transition;
  }
  
  .card {
    @apply bg-terminal-gray border border-terminal-green p-4 rounded;
  }
}
```

---

## 📁 ESTRUTURA DE PROJETO DETALHADA

```
SNE_BACKUP_CLEAN/
│
├── 📱 frontend/                    # NOVO - Frontend Vue.js
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   ├── Footer.vue
│   │   │   │   └── LoadingSpinner.vue
│   │   │   ├── charts/
│   │   │   │   ├── TradingChart.vue
│   │   │   │   ├── ConfluenceChart.vue
│   │   │   │   └── MTFHeatmap.vue
│   │   │   ├── analysis/
│   │   │   │   ├── AnalysisPanel.vue
│   │   │   │   ├── SignalCard.vue
│   │   │   │   ├── RiskMetrics.vue
│   │   │   │   └── TimeframeSelector.vue
│   │   │   └── magnetic/
│   │   │       ├── MagneticField3D.vue
│   │   │       └── MagneticZones.vue
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Analysis.vue
│   │   │   ├── Backtesting.vue
│   │   │   ├── MagneticField.vue
│   │   │   ├── Settings.vue
│   │   │   └── Profile.vue
│   │   ├── stores/
│   │   │   ├── market.js
│   │   │   ├── analysis.js
│   │   │   ├── user.js
│   │   │   └── magnetic.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── websocket.js
│   │   │   └── cloud-api.js
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── utils/
│   │   │   ├── formatters.js
│   │   │   └── validators.js
│   │   ├── assets/
│   │   │   ├── css/
│   │   │   │   └── main.css
│   │   │   └── images/
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   │   └── index.html
│   ├── dist/                       # Build output (gitignored)
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── 🔧 backend/                     # MELHORADO - Backend organizado
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── analysis.py
│   │       ├── signals.py
│   │       └── magnetic.py
│   └── services/
│       └── cloud_integration.py
│
├── 🎨 templates/                   # MANTÉM - Templates existentes
│   └── (templates antigos - podem ser removidos depois)
│
└── 📄 sne_radar_web.py            # MODIFICADO - Adiciona servir frontend
```

---

## ⚙️ CONFIGURAÇÃO VUE.JS + VITE

### 1. Entry Point: `frontend/src/main.js`

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
```

### 2. App Component: `frontend/src/App.vue`

```vue
<template>
  <div id="app">
    <Header />
    <div class="container mx-auto px-4 py-8">
      <router-view />
    </div>
    <Footer />
  </div>
</template>

<script setup>
import Header from './components/common/Header.vue'
import Footer from './components/common/Footer.vue'
</script>

<style>
#app {
  min-height: 100vh;
  background: #000000;
}
</style>
```

### 3. Router: `frontend/src/router/index.js`

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Analysis from '../views/Analysis.vue'
import Backtesting from '../views/Backtesting.vue'
import MagneticField from '../views/MagneticField.vue'
import Settings from '../views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis
  },
  {
    path: '/backtesting',
    name: 'Backtesting',
    component: Backtesting
  },
  {
    path: '/magnetic',
    name: 'MagneticField',
    component: MagneticField
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

### 4. Store (Pinia): `frontend/src/stores/market.js`

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useMarketStore = defineStore('market', () => {
  const currentSymbol = ref('BTCUSDT')
  const currentTimeframe = ref('1h')
  const analysisData = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const analyze = async (symbol, timeframe) => {
    loading.value = true
    error.value = null
    
    try {
      const data = await api.analyze(symbol, timeframe)
      analysisData.value = data
      currentSymbol.value = symbol
      currentTimeframe.value = timeframe
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const signal = computed(() => {
    if (!analysisData.value) return null
    return analysisData.value.signal || 'NEUTRAL'
  })

  return {
    currentSymbol,
    currentTimeframe,
    analysisData,
    loading,
    error,
    signal,
    analyze
  }
})
```

### 5. API Service: `frontend/src/services/api.js`

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000
})

// Interceptors para tratamento de erros
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    throw new Error(error.response?.data?.error || 'Erro na requisição')
  }
)

export default {
  // Health check
  health: () => api.get('/health'),
  
  // Análise completa
  analyze: (symbol, timeframe) => 
    api.post('/analyze', { symbol, timeframe }),
  
  // Obter sinal
  getSignal: (symbol, timeframe) => 
    api.get('/signal', { params: { symbol, timeframe } }),
  
  // Campo magnético
  getMagneticField: (symbol) => 
    api.get('/magnetic/field', { params: { symbol } }),
  
  // Backtesting
  runBacktest: (config) => 
    api.post('/backtest/run', config),
  
  // Alertas
  getAlerts: () => api.get('/alerts'),
  createAlert: (alert) => api.post('/alerts', alert)
}
```

### 6. WebSocket Service: `frontend/src/services/websocket.js`

```javascript
import { io } from 'socket.io-client'

class WebSocketService {
  constructor() {
    this.socket = null
    this.listeners = new Map()
  }

  connect() {
    if (this.socket?.connected) return

    this.socket = io({
      path: '/socket.io',
      transports: ['websocket', 'polling']
    })

    this.socket.on('connect', () => {
      console.log('✅ WebSocket conectado')
    })

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket desconectado')
    })

    // Re-registrar listeners existentes
    this.listeners.forEach((callback, event) => {
      this.socket.on(event, callback)
    })
  }

  on(event, callback) {
    this.listeners.set(event, callback)
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  emit(event, data) {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }
}

export default new WebSocketService()
```

---

## 🔗 INTEGRAÇÃO COM FLASK

### Modificação em `sne_radar_web.py`

**Adicionar no início do arquivo:**

```python
import os
from flask import send_from_directory

# Configurar caminhos do frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
FRONTEND_STATIC = os.path.join(FRONTEND_DIR, 'assets')
FRONTEND_INDEX = os.path.join(FRONTEND_DIR, 'index.html')
```

**Modificar inicialização do Flask:**

```python
# ANTES:
app = Flask(__name__)

# DEPOIS:
app = Flask(__name__,
    static_folder=FRONTEND_STATIC if os.path.exists(FRONTEND_STATIC) else None,
    template_folder=FRONTEND_DIR if os.path.exists(FRONTEND_DIR) else None
)
```

**Adicionar rotas para servir frontend:**

```python
# Rota para servir index.html (Vue Router cuida do resto)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve o frontend Vue.js"""
    if os.path.exists(FRONTEND_INDEX):
        # Se for arquivo estático (assets), servir normalmente
        if path.startswith('assets/'):
            return send_from_directory(FRONTEND_DIR, path)
        
        # Para todas as outras rotas, servir index.html
        # Vue Router cuida do roteamento no frontend
        return send_from_directory(FRONTEND_DIR, 'index.html')
    else:
        # Fallback: se frontend não estiver buildado, usar template antigo
        return render_template('dashboard.html')
```

**Manter APIs existentes:**

```python
# APIs continuam funcionando normalmente
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # ... código existente ...
    pass

# Todas as outras rotas /api/* continuam funcionando
```

**Modificar Socket.IO (se necessário):**

```python
# Socket.IO já funciona normalmente
# Mas pode adicionar CORS se necessário (não precisa se mesmo domínio)
socketio = SocketIO(app, cors_allowed_origins="*" if not IS_PRODUCTION else None)
```

---

## 📦 DESENVOLVIMENTO INCREMENTAL

### Sprint 1: Fundação (Semana 1)

#### Dia 1-2: Setup e Estrutura Base
- [ ] Criar projeto Vue.js
- [ ] Configurar Vite
- [ ] Configurar Tailwind CSS
- [ ] Criar estrutura de pastas
- [ ] Setup Router e Pinia

#### Dia 3-4: Componentes Base
- [ ] Criar `Header.vue`
- [ ] Criar `Sidebar.vue`
- [ ] Criar `Footer.vue`
- [ ] Criar `LoadingSpinner.vue`
- [ ] Criar layout base

#### Dia 5: Integração Flask
- [ ] Modificar `sne_radar_web.py`
- [ ] Testar servir frontend
- [ ] Testar rotas API
- [ ] Testar WebSocket

**Checkpoint Sprint 1:**
- ✅ Frontend compila
- ✅ Flask serve frontend
- ✅ APIs funcionam
- ✅ Layout base visível

---

### Sprint 2: Dashboard Principal (Semana 2)

#### Dia 1-2: Dashboard View
- [ ] Criar `Dashboard.vue`
- [ ] Cards de resumo
- [ ] Top oportunidades
- [ ] Gráfico principal

#### Dia 3-4: Integração APIs
- [ ] Criar `api.js` service
- [ ] Criar `market.js` store
- [ ] Integrar com `/api/analyze`
- [ ] Integrar com `/api/signal`

#### Dia 5: WebSocket Real-time
- [ ] Criar `websocket.js` service
- [ ] Conectar Socket.IO
- [ ] Atualizar dados em tempo real
- [ ] Testar desconexão/reconexão

**Checkpoint Sprint 2:**
- ✅ Dashboard funcional
- ✅ Dados reais sendo exibidos
- ✅ Updates em tempo real
- ✅ Loading states

---

### Sprint 3: Análise Técnica (Semana 3)

#### Dia 1-2: Página de Análise
- [ ] Criar `Analysis.vue`
- [ ] Seletor de par/timeframe
- [ ] Painel de resultados
- [ ] Score de confluência

#### Dia 3-4: Componentes de Análise
- [ ] Criar `AnalysisPanel.vue`
- [ ] Criar `SignalCard.vue`
- [ ] Criar `RiskMetrics.vue`
- [ ] Criar `TimeframeSelector.vue`

#### Dia 5: Gráficos
- [ ] Integrar Lightweight Charts
- [ ] Criar `TradingChart.vue`
- [ ] Exibir indicadores
- [ ] Níveis Entry/SL/TP

**Checkpoint Sprint 3:**
- ✅ Análise completa funcional
- ✅ Gráficos interativos
- ✅ Dados formatados
- ✅ UX polida

---

### Sprint 4: Funcionalidades Avançadas (Semana 4)

#### Dia 1-2: Campo Magnético 3D
- [ ] Criar `MagneticField.vue`
- [ ] Integrar Three.js
- [ ] Visualização básica
- [ ] Interatividade

#### Dia 3-4: Backtesting Visual
- [ ] Criar `Backtesting.vue`
- [ ] Interface de configuração
- [ ] Execução visual
- [ ] Resultados

#### Dia 5: Polimento
- [ ] Error handling
- [ ] Loading states
- [ ] Validações
- [ ] Testes básicos

**Checkpoint Sprint 4:**
- ✅ Campo Magnético funcional
- ✅ Backtesting funcional
- ✅ Erros tratados
- ✅ UX completa

---

## 🚀 BUILD E DEPLOY

### 1. Script de Build

**`frontend/package.json`:**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "build:prod": "vite build --mode production"
  }
}
```

### 2. Processo de Build

```bash
# Desenvolvimento
cd frontend
npm run dev  # Servidor Vite em http://localhost:5173

# Build para produção
npm run build  # Gera arquivos em frontend/dist/

# Preview do build
npm run preview  # Testa build localmente
```

### 3. Integração com Flask (Local)

```bash
# Terminal 1: Frontend dev server
cd frontend
npm run dev

# Terminal 2: Flask (modo dev)
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_radar_web.py

# Acessar: http://localhost:5173 (Vite proxy para Flask)
```

### 4. Build para Produção

```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Verificar build
ls -la dist/
# Deve ter: index.html, assets/, etc.

# 3. Flask já está configurado para servir dist/
# 4. Testar localmente
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

### 5. Deploy Cloud Run

**Modificar Dockerfile (se necessário):**

```dockerfile
# Adicionar ao Dockerfile existente
# Copiar frontend build
COPY frontend/dist /app/frontend/dist

# Flask já serve automaticamente
```

**Ou criar script de deploy:**

**`deploy_frontend.sh`:**

```bash
#!/bin/bash

PROJECT_ID="sne-v1"
REGION="europe-west1"
SERVICE_NAME="sne-web"

echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Frontend built successfully"
echo "📦 Deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated

echo "✅ Deploy complete!"
```

---

## ✅ CHECKLIST COMPLETO

### Setup Inicial
- [ ] Node.js e npm instalados
- [ ] Estrutura de pastas criada
- [ ] Projeto Vue.js inicializado
- [ ] Dependências instaladas
- [ ] Vite configurado
- [ ] Tailwind CSS configurado

### Integração Flask
- [ ] `sne_radar_web.py` modificado
- [ ] Rotas para servir frontend adicionadas
- [ ] APIs mantidas funcionando
- [ ] WebSocket funcionando
- [ ] Testado localmente

### Desenvolvimento
- [ ] Router configurado
- [ ] Pinia stores criados
- [ ] API service criado
- [ ] WebSocket service criado
- [ ] Componentes base criados
- [ ] Views principais criadas

### Funcionalidades
- [ ] Dashboard funcional
- [ ] Análise técnica funcional
- [ ] Gráficos integrados
- [ ] Campo Magnético 3D (opcional)
- [ ] Backtesting visual (opcional)

### Build e Deploy
- [ ] Build funciona (`npm run build`)
- [ ] Flask serve build localmente
- [ ] Testes básicos passando
- [ ] Dockerfile atualizado (se necessário)
- [ ] Deploy Cloud Run funcionando

### Polimento
- [ ] Error handling implementado
- [ ] Loading states em todos lugares
- [ ] Validações de formulários
- [ ] Responsividade mobile
- [ ] Performance otimizada

---

## 🎯 COMANDOS RÁPIDOS

### Desenvolvimento

```bash
# Terminal 1: Frontend (Vite dev server)
cd frontend
npm run dev

# Terminal 2: Backend (Flask)
python3 sne_radar_web.py

# Acessar: http://localhost:5173
```

### Build

```bash
# Build frontend
cd frontend
npm run build

# Testar build localmente
python3 sne_radar_web.py
# Acessar: http://localhost:9999
```

### Deploy

```bash
# Build + Deploy
./deploy_frontend.sh
```

---

## 📚 ESTRUTURA DE ARQUIVOS FINAL

```
SNE_BACKUP_CLEAN/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── router/
│   │   ├── utils/
│   │   ├── assets/
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   ├── dist/              # Build output (gitignored)
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── sne_radar_web.py       # MODIFICADO - Serve frontend
├── deploy_frontend.sh     # NOVO - Script de deploy
└── ...
```

---

## 🎉 PRÓXIMOS PASSOS

1. **Revisar este plano**
2. **Aprovar estrutura**
3. **Começar Sprint 1**
4. **Desenvolvimento incremental**
5. **Deploy quando MVP pronto**

---

**Status:** 📋 **PLANO COMPLETO - PRONTO PARA IMPLEMENTAÇÃO**

**Criado em:** 26 de Novembro de 2025  
**Versão:** 1.0


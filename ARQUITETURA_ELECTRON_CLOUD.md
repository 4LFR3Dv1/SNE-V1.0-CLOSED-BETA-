# 🚀 ARQUITETURA ELECTRON + CLOUD (Modelo Spotify/Slack)

**Data:** 02 de Janeiro de 2025  
**Modelo:** Cliente Desktop (Electron) + Backend Cloud (Google Cloud Run)

---

## 🎯 VISÃO GERAL

### **O que o usuário baixa:**
- ✅ Aplicativo desktop (.exe/.dmg/.AppImage)
- ✅ Interface Vue.js empacotada em Electron
- ✅ Navegador embutido (Chromium)
- ❌ **ZERO lógica de negócio**
- ❌ **ZERO código Python**

### **O que fica na nuvem:**
- 🔐 **Todo o código Python** (motor_renan.py, AutoPilot, etc.)
- 🔐 **Banco de dados** (PostgreSQL)
- 🔐 **Lógica de trading**
- 🔐 **Análises e cálculos**

### **Resultado:**
- 🛡️ **100% de proteção de IP** (código nunca sai do servidor)
- 🎨 **Experiência de app nativo** (como Spotify/Slack)
- 🔄 **Atualizações automáticas** (backend)
- 📊 **Controle total** (licenciamento, analytics)

---

## 🏗️ ARQUITETURA

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (Desktop)                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Electron App (.exe/.dmg)                        │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  Vue.js Frontend (HTML/CSS/JS)             │ │  │
│  │  │  - Dashboard                                │ │  │
│  │  │  - Gráficos (Lightweight Charts)           │ │  │
│  │  │  - Formulários                              │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  Chromium (Navegador Embutido)             │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS/REST API
                        │ WebSocket
                        ▼
┌─────────────────────────────────────────────────────────┐
│              GOOGLE CLOUD RUN (Backend)                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Flask API (Python)                              │  │
│  │  - /api/v1/analyze                               │  │
│  │  - /api/v1/trading/execute                       │  │
│  │  - /api/v1/positions                             │  │
│  │  - /api/v1/portfolio                             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Motor SNE (Python) 🔐                           │  │
│  │  - motor_renan.py                                │  │
│  │  - AutoPilotEngine                               │  │
│  │  - RiskManager                                   │  │
│  │  - StrategyEngine                                │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Cloud SQL (PostgreSQL)                          │  │
│  │  - Usuários                                      │  │
│  │  - Posições                                      │  │
│  │  - Histórico                                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### **FASE 1: Preparar Backend para API Pura** ✅

- [ ] Converter Flask para API REST pura (sem render_template)
- [ ] Criar rotas `/api/v1/*` para todas as funcionalidades
- [ ] Adicionar autenticação JWT
- [ ] Adicionar CORS para permitir Electron
- [ ] Testar endpoints com Postman/curl

### **FASE 2: Deploy Backend na Cloud** ☁️

- [ ] Configurar Google Cloud Run
- [ ] Criar Dockerfile para Flask
- [ ] Configurar Cloud SQL (PostgreSQL)
- [ ] Configurar variáveis de ambiente
- [ ] Deploy e testar API pública

### **FASE 3: Adicionar Electron ao Frontend** 🖥️

- [ ] Instalar Electron no projeto Vue
- [ ] Configurar background.js
- [ ] Conectar frontend à API cloud
- [ ] Testar em modo desenvolvimento

### **FASE 4: Build e Distribuição** 📦

- [ ] Configurar electron-builder
- [ ] Criar ícones para cada plataforma
- [ ] Build executáveis (.exe/.dmg/.AppImage)
- [ ] Testar instalação
- [ ] Criar instaladores profissionais

---

## 🔧 IMPLEMENTAÇÃO PASSO A PASSO

### **PASSO 1: Converter Flask para API Pura**

O Flask atual serve HTML. Precisamos converter para API REST pura.

#### **1.1. Criar `app/api/cloud_api.py`:**

```python
"""
API Cloud - Versão pura REST para Electron
Todas as rotas retornam JSON, nunca HTML
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.autopilot_engine import AutoPilotEngine
from motor_renan import analise_completa

cloud_api = Blueprint('cloud_api', __name__, url_prefix='/api/v1')

@cloud_api.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'SNE Radar API',
        'version': '1.0.0'
    })

@cloud_api.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    """Análise completa de um símbolo"""
    data = request.get_json()
    symbol = data.get('symbol', 'BTCUSDT')
    timeframe = data.get('timeframe', '1h')
    
    try:
        resultado = analise_completa(symbol, timeframe)
        return jsonify({
            'success': True,
            'data': resultado
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cloud_api.route('/trading/autopilot/status', methods=['GET'])
@jwt_required()
def autopilot_status():
    """Status do AutoPilot"""
    user_id = get_jwt_identity()
    # Buscar status do AutoPilot do usuário
    return jsonify({
        'success': True,
        'running': False,
        'pools': []
    })

@cloud_api.route('/trading/positions', methods=['GET'])
@jwt_required()
def get_positions():
    """Lista posições do usuário"""
    user_id = get_jwt_identity()
    # Buscar posições do banco
    return jsonify({
        'success': True,
        'positions': []
    })
```

#### **1.2. Atualizar `app/__init__.py`:**

```python
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    
    # CORS para permitir Electron
    CORS(app, origins=['*'])  # Em produção, restringir
    
    # JWT para autenticação
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    jwt = JWTManager(app)
    
    # Registrar blueprints
    from app.api.cloud_api import cloud_api
    app.register_blueprint(cloud_api)
    
    return app
```

---

### **PASSO 2: Deploy na Google Cloud Run**

#### **2.1. Criar `Dockerfile`:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Variáveis de ambiente
ENV FLASK_APP=app.main:app
ENV FLASK_ENV=production

# Expor porta
EXPOSE 8080

# Comando
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app.main:app
```

#### **2.2. Criar `cloudbuild.yaml`:**

```yaml
steps:
  # Build da imagem
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/sne-api', '.']
  
  # Push para Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/sne-api']
  
  # Deploy no Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'sne-api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/sne-api'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

#### **2.3. Deploy:**

```bash
# Build e deploy
gcloud builds submit --config cloudbuild.yaml

# Ou manualmente
gcloud run deploy sne-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

---

### **PASSO 3: Adicionar Electron ao Frontend**

#### **3.1. Instalar Electron:**

```bash
cd frontend
npm install --save-dev electron electron-builder
npm install --save-dev vue-cli-plugin-electron-builder
```

#### **3.2. Criar `frontend/src/background.js`:**

```javascript
import { app, protocol, BrowserWindow } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import installExtension, { VUEJS_DEVTOOLS } from 'electron-devtools-installer'

const isDevelopment = process.env.NODE_ENV !== 'production'

// Scheme deve ser registrado antes do app estar pronto
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])

async function createWindow() {
  // Criar janela do navegador
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    webPreferences: {
      // Segurança: desabilitar nodeIntegration
      nodeIntegration: false,
      contextIsolation: true,
      // Permitir requisições HTTPS
      webSecurity: true
    },
    // Visual moderno
    titleBarStyle: 'hiddenInset', // macOS
    frame: true,
    backgroundColor: '#1a1a1a'
  })

  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Modo desenvolvimento
    await win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    if (!process.env.IS_TEST) win.webContents.openDevTools()
  } else {
    // Modo produção
    createProtocol('app')
    win.loadURL('app://./index.html')
  }

  // Verificar conexão com API
  win.webContents.on('did-finish-load', () => {
    win.webContents.executeJavaScript(`
      // Verificar se API está acessível
      fetch('${process.env.VUE_APP_API_URL || 'https://api.sne-radar.com'}/api/v1/health')
        .then(r => r.json())
        .then(data => {
          if (!data.status || data.status !== 'ok') {
            console.error('API não está acessível')
          }
        })
        .catch(err => {
          console.error('Erro ao conectar com API:', err)
          // Mostrar aviso ao usuário
        })
    `)
  })
}

// Este método será chamado quando Electron terminar de inicializar
app.on('ready', async () => {
  if (isDevelopment && !process.env.IS_TEST) {
    // Instalar Vue Devtools
    try {
      await installExtension(VUEJS_DEVTOOLS)
    } catch (e) {
      console.error('Vue Devtools failed to install:', e.toString())
    }
  }
  createWindow()
})

// Sair quando todas as janelas estiverem fechadas
app.on('window-all-closed', () => {
  // No macOS, aplicativos normalmente ficam ativos até o usuário sair explicitamente
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // No macOS, recriar janela quando o ícone do dock é clicado
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
```

#### **3.3. Atualizar `frontend/vue.config.js`:**

```javascript
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  pluginOptions: {
    electronBuilder: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: 'src/preload.js',
      builderOptions: {
        appId: 'com.sne.radar',
        productName: 'SNE Radar',
        copyright: 'Copyright © 2025 SNE Trading Systems',
        directories: {
          output: 'dist_electron'
        },
        win: {
          target: ['nsis'],
          icon: 'build/icon.ico'
        },
        mac: {
          target: ['dmg'],
          icon: 'build/icon.icns',
          category: 'public.app-category.finance'
        },
        linux: {
          target: ['AppImage'],
          icon: 'build/icon.png',
          category: 'Finance'
        },
        nsis: {
          oneClick: false,
          allowToChangeInstallationDirectory: true
        }
      }
    }
  }
})
```

#### **3.4. Criar `frontend/src/preload.js`:**

```javascript
// Preload script (bridge seguro entre Electron e Vue)
const { contextBridge, ipcRenderer } = require('electron')

// Expor APIs seguras para o Vue
contextBridge.exposeInMainWorld('electronAPI', {
  // Versão do app
  getVersion: () => process.env.npm_package_version,
  
  // Informações do sistema
  getPlatform: () => process.platform,
  
  // Eventos (se necessário)
  on: (channel, callback) => {
    ipcRenderer.on(channel, callback)
  }
})
```

#### **3.5. Atualizar `frontend/src/services/api.js`:**

```javascript
import axios from 'axios'

// URL da API: Cloud em produção, local em desenvolvimento
const API_URL = process.env.NODE_ENV === 'production'
  ? process.env.VUE_APP_API_URL || 'https://api.sne-radar.com'
  : 'http://localhost:5000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para adicionar token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('jwt_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para tratar erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido, redirecionar para login
      localStorage.removeItem('jwt_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

#### **3.6. Criar `.env.production`:**

```bash
# frontend/.env.production
VUE_APP_API_URL=https://api.sne-radar.com
```

---

### **PASSO 4: Build e Distribuição**

#### **4.1. Adicionar scripts ao `package.json`:**

```json
{
  "scripts": {
    "electron:serve": "vue-cli-service electron:serve",
    "electron:build": "vue-cli-service electron:build",
    "electron:build:win": "vue-cli-service electron:build --win",
    "electron:build:mac": "vue-cli-service electron:build --mac",
    "electron:build:linux": "vue-cli-service electron:build --linux"
  }
}
```

#### **4.2. Build:**

```bash
# Desenvolvimento
npm run electron:serve

# Produção (todas as plataformas)
npm run electron:build

# Plataforma específica
npm run electron:build:win   # Windows
npm run electron:build:mac   # macOS
npm run electron:build:linux # Linux
```

#### **4.3. Resultado:**

```
frontend/dist_electron/
├── SNE_RADAR Setup 1.0.0.exe  (Windows)
├── SNE_RADAR-1.0.0.dmg        (macOS)
└── SNE_RADAR-1.0.0.AppImage   (Linux)
```

---

## 🔐 SEGURANÇA E AUTENTICAÇÃO

### **JWT Authentication:**

```python
# Backend: app/api/auth.py
from flask_jwt_extended import create_access_token

@cloud_api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Validar credenciais
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        # Criar token JWT
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'success': True,
            'token': access_token
        })
    
    return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401
```

### **Frontend: Login:**

```javascript
// frontend/src/services/auth.js
import api from './api'

export async function login(username, password) {
  const response = await api.post('/auth/login', { username, password })
  if (response.data.success) {
    localStorage.setItem('jwt_token', response.data.token)
    return true
  }
  return false
}
```

---

## 📊 VANTAGENS DESTA ARQUITETURA

### **✅ Proteção de IP:**
- Código Python **NUNCA** sai do servidor
- Cliente só tem HTML/CSS/JS (frontend)
- Impossível extrair lógica de negócio

### **✅ Experiência Nativa:**
- App instalável (.exe/.dmg)
- Ícone no desktop
- Janela dedicada
- Atalhos de teclado

### **✅ Controle Total:**
- Licenciamento no servidor
- Desativar usuários instantaneamente
- Analytics e telemetria
- Atualizações automáticas (backend)

### **✅ Escalabilidade:**
- Cloud Run escala automaticamente
- Suporta milhares de usuários
- Pay-per-use (só paga o que usa)

---

## 🚀 PRÓXIMOS PASSOS

1. **Implementar API REST pura** no Flask
2. **Deploy na Cloud Run**
3. **Adicionar Electron** ao frontend
4. **Testar conexão** cliente ↔ cloud
5. **Build executáveis** e distribuir

---

**Status:** 📋 Plano Completo - Pronto para Implementação



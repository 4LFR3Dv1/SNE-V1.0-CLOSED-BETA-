# 📦 PLANO DE DISTRIBUIÇÃO STANDALONE - SNE RADAR

**Data:** Janeiro 2025  
**Objetivo:** Criar distribuição standalone do SNE Radar que funcione sem instalação de dependências

---

## 🎯 OBJETIVOS

1. ✅ **Executável único** ou pacote fácil de instalar
2. ✅ **Sem necessidade de Python/Node instalados** no sistema do usuário
3. ✅ **Banco de dados embutido** (SQLite)
4. ✅ **Frontend pré-buildado** incluído
5. ✅ **Funciona offline** (exceto para dados da Binance)
6. ✅ **Multiplataforma** (Windows, macOS, Linux)

---

## 🏗️ ARQUITETURA PROPOSTA

### Opção 1: Aplicação Desktop Híbrida (RECOMENDADA)

```
┌─────────────────────────────────────────────────┐
│         SNE RADAR Desktop Application            │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │     Electron / Tauri (Container)         │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  Frontend Vue.js (Pré-buildado)    │  │  │
│  │  │  - Dashboard                       │  │  │
│  │  │  - Gráficos                        │  │  │
│  │  │  - Análises                        │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │                                           │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │  Backend Python (PyInstaller)      │  │  │
│  │  │  - Flask API                       │  │  │
│  │  │  - Motor de Análise                │  │  │
│  │  │  - SQLite (embutido)               │  │  │
│  │  └────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Interface nativa
- ✅ Fácil distribuição
- ✅ Auto-atualização possível
- ✅ Melhor UX

**Desvantagens:**
- ⚠️ Tamanho maior (~200-300 MB)
- ⚠️ Mais complexo de desenvolver

---

### Opção 2: Executável Python Monolítico

```
┌─────────────────────────────────────────────────┐
│         SNE RADAR Executável                    │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  PyInstaller Bundle                      │  │
│  │  - Python Runtime (embutido)             │  │
│  │  - Todas as dependências                 │  │
│  │  - Flask Server                          │  │
│  │  - Motor de Análise                      │  │
│  │  - SQLite (embutido)                     │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Frontend (dist/)                        │  │
│  │  - Arquivos estáticos pré-buildados      │  │
│  │  - Servido pelo Flask                    │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Mais simples de implementar
- ✅ Tamanho menor (~150-200 MB)
- ✅ Funciona como servidor local

**Desvantagens:**
- ⚠️ Abre navegador automaticamente
- ⚠️ Menos "nativo"

---

### Opção 3: Docker Desktop App

```
┌─────────────────────────────────────────────────┐
│         SNE RADAR Desktop                        │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Docker Container                        │  │
│  │  - Backend + Frontend                    │  │
│  │  - SQLite                                │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  Launcher Desktop                        │  │
│  │  - Inicia container                       │  │
│  │  - Abre navegador                        │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Isolamento completo
- ✅ Fácil de atualizar
- ✅ Funciona igual em todas as plataformas

**Desvantagens:**
- ⚠️ Requer Docker Desktop instalado
- ⚠️ Não é verdadeiramente standalone

---

## 📋 PLANO DETALHADO - OPÇÃO 2 (RECOMENDADA)

### Fase 1: Preparação do Backend

#### 1.1 Criar Entry Point Standalone

**Arquivo:** `standalone_launcher.py`

```python
#!/usr/bin/env python3
"""
Launcher standalone do SNE Radar
Inicia servidor Flask e abre navegador automaticamente
"""
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Configurar ambiente standalone
os.environ['FLASK_ENV'] = 'standalone'
os.environ['DATABASE_URL'] = f'sqlite:///{ROOT_DIR}/data/sne_radar.db'
os.environ['STANDALONE_MODE'] = 'true'

def start_server():
    """Inicia servidor Flask"""
    from sne_radar_web import app, socketio
    
    # Criar diretório de dados se não existir
    data_dir = ROOT_DIR / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Iniciar servidor
    port = 9999
    url = f'http://localhost:{port}'
    
    print(f"🚀 Iniciando SNE Radar...")
    print(f"📊 Dashboard: {url}")
    
    # Abrir navegador após 2 segundos
    def open_browser():
        time.sleep(2)
        webbrowser.open(url)
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor
    socketio.run(app, host='127.0.0.1', port=port, debug=False)

if __name__ == '__main__':
    start_server()
```

#### 1.2 Configurar PyInstaller

**Arquivo:** `build_standalone.spec`

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Coletar todos os módulos Python necessários
a = Analysis(
    ['standalone_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),  # Frontend buildado
        ('instance', 'instance'),            # Templates e dados
        ('config', 'config'),                # Configurações
    ],
    hiddenimports=[
        'flask',
        'flask_socketio',
        'flask_sqlalchemy',
        'motor_renan',
        'contexto_global',
        'estrutura_mercado',
        'multi_timeframe',
        'confluencia',
        'fluxo_ativo',
        'catalogo_magnetico',
        'padroes_graficos',
        'indicadores',
        'indicadores_avancados',
        'analise_candles_detalhada',
        'gestao_risco_profissional',
        'relatorio_profissional',
        'calcular_suportes_resistencias',
        'niveis_operacionais',
        'pandas',
        'numpy',
        'matplotlib',
        'mplfinance',
        'scipy',
        'sklearn',
        'sqlalchemy',
        'alembic',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SNE_Radar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mudar para False para ocultar console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
```

#### 1.3 Script de Build

**Arquivo:** `build_standalone.sh` (Linux/macOS) e `build_standalone.bat` (Windows)

```bash
#!/bin/bash
# build_standalone.sh

set -e

echo "🔨 Construindo SNE Radar Standalone..."

# 1. Build do frontend
echo "📦 Buildando frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Criar diretório de dados
mkdir -p data
mkdir -p instance

# 3. Inicializar banco SQLite
python3 -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Banco de dados inicializado')
"

# 4. Instalar PyInstaller se necessário
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip install pyinstaller
fi

# 5. Build executável
echo "🔨 Criando executável..."
pyinstaller build_standalone.spec --clean

# 6. Copiar arquivos adicionais
echo "📋 Copiando arquivos adicionais..."
cp -r frontend/dist dist/SNE_Radar/frontend/dist
cp -r data dist/SNE_Radar/data
cp -r instance dist/SNE_Radar/instance

# 7. Criar README
cat > dist/SNE_Radar/README.txt <<EOF
SNE RADAR - Sistema Neural Estratégico
=======================================

INSTRUÇÕES:
1. Execute SNE_Radar (ou SNE_Radar.exe no Windows)
2. Aguarde o navegador abrir automaticamente
3. O dashboard estará disponível em http://localhost:9999

DADOS:
- Banco de dados: data/sne_radar.db
- Logs: logs/

SUPORTE:
- Consulte a documentação em: https://github.com/seu-repo/sne-radar
EOF

echo "✅ Build completo! Executável em: dist/SNE_Radar/"
```

---

### Fase 2: Preparação do Frontend

#### 2.1 Ajustar Vite Config para Standalone

**Arquivo:** `frontend/vite.config.standalone.js`

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
  base: './', // IMPORTANTE: Para funcionar como arquivo local
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
  // Remover proxy em modo standalone
  server: {
    port: 5173,
    strictPort: false,
    host: true
  }
})
```

#### 2.2 Ajustar API Service

**Arquivo:** `frontend/src/services/api.js`

```javascript
import axios from 'axios'

// Detectar modo standalone
const isStandalone = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1'

// URL base da API
const API_BASE_URL = isStandalone 
  ? 'http://localhost:9999/api'  // Standalone
  : import.meta.env.VITE_API_URL || '/api'  // Produção

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ... resto do código
```

---

### Fase 3: Configuração de Banco de Dados

#### 3.1 Modificar Database Config para Standalone

**Arquivo:** `database_config_standalone.py`

```python
"""
Configuração de banco para modo standalone
Sempre usa SQLite
"""
import os
from pathlib import Path

def get_standalone_db_path():
    """Retorna caminho do banco SQLite no modo standalone"""
    # Se executando como PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    
    # Diretório de dados
    data_dir = base_path / 'data'
    data_dir.mkdir(exist_ok=True)
    
    return data_dir / 'sne_radar.db'

def get_database_url():
    """Retorna URL do banco para modo standalone"""
    db_path = get_standalone_db_path()
    return f'sqlite:///{db_path}'
```

#### 3.2 Script de Inicialização

**Arquivo:** `init_standalone_db.py`

```python
"""
Inicializa banco de dados SQLite para modo standalone
"""
from app import create_app, db
from app.models.models import User, Signal, Trade  # Ajustar conforme modelos

def init_database():
    """Cria todas as tabelas"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados inicializado")
        
        # Criar usuário admin padrão se não existir
        from app.utils.security import hash_password
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@sne.local',
                password_hash=hash_password('admin123'),
                plan='PREMIUM'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado (senha: admin123)")
```

---

### Fase 4: Build e Distribuição

#### 4.1 Estrutura Final do Pacote

```
SNE_Radar_Standalone/
├── SNE_Radar              # Executável principal
│   ├── SNE_Radar          # (Linux/macOS)
│   └── SNE_Radar.exe      # (Windows)
├── data/                   # Dados do usuário
│   └── sne_radar.db       # Banco SQLite
├── logs/                   # Logs da aplicação
├── README.txt             # Instruções
└── LICENSE                # Licença
```

#### 4.2 Script de Empacotamento

**Arquivo:** `package_standalone.sh`

```bash
#!/bin/bash
# package_standalone.sh

VERSION="1.0.0"
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

echo "📦 Empacotando SNE Radar Standalone v${VERSION} para ${PLATFORM} ${ARCH}..."

# 1. Build
./build_standalone.sh

# 2. Criar diretório de distribuição
DIST_DIR="dist/SNE_Radar_${VERSION}_${PLATFORM}_${ARCH}"
mkdir -p "$DIST_DIR"

# 3. Copiar executável
cp -r dist/SNE_Radar/* "$DIST_DIR/"

# 4. Criar script de inicialização (opcional)
cat > "$DIST_DIR/start.sh" <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./SNE_Radar
EOF
chmod +x "$DIST_DIR/start.sh"

# 5. Criar arquivo de versão
echo "$VERSION" > "$DIST_DIR/VERSION"

# 6. Criar ZIP
cd dist
zip -r "SNE_Radar_${VERSION}_${PLATFORM}_${ARCH}.zip" "SNE_Radar_${VERSION}_${PLATFORM}_${ARCH}"
cd ..

echo "✅ Pacote criado: dist/SNE_Radar_${VERSION}_${PLATFORM}_${ARCH}.zip"
```

---

## 🎨 ALTERNATIVA: Electron/Tauri (Opção 1)

### Estrutura Electron

```
sne-desktop/
├── package.json
├── electron/
│   ├── main.js           # Processo principal
│   └── preload.js        # Preload script
├── src/                  # Frontend Vue.js
│   └── (mesmo frontend)
└── python-server/        # Backend Python
    └── (mesmo backend)
```

### package.json (Electron)

```json
{
  "name": "sne-radar-desktop",
  "version": "1.0.0",
  "main": "electron/main.js",
  "scripts": {
    "dev": "concurrently \"npm run dev:vue\" \"npm run dev:electron\"",
    "build": "npm run build:vue && npm run build:electron",
    "build:vue": "cd ../frontend && npm run build",
    "build:electron": "electron-builder",
    "package": "electron-builder --dir"
  },
  "build": {
    "appId": "com.sne.radar",
    "productName": "SNE Radar",
    "directories": {
      "output": "dist-electron"
    },
    "files": [
      "electron/**/*",
      "../frontend/dist/**/*",
      "../python-server/**/*"
    ],
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": "AppImage",
      "icon": "assets/icon.png"
    }
  },
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-builder": "^24.9.1",
    "concurrently": "^8.2.2"
  }
}
```

### electron/main.js

```javascript
const { app, BrowserWindow } = require('electron')
const { spawn } = require('child_process')
const path = require('path')

let mainWindow
let pythonProcess

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // Iniciar servidor Python
  startPythonServer()

  // Carregar frontend
  mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'))
  
  // Abrir DevTools em desenvolvimento
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools()
  }
}

function startPythonServer() {
  const pythonScript = path.join(__dirname, '../python-server/standalone_launcher.py')
  pythonProcess = spawn('python', [pythonScript], {
    cwd: path.join(__dirname, '../python-server')
  })

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`)
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`)
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})
```

---

## 📊 COMPARAÇÃO DAS OPÇÕES

| Critério | Opção 1 (Electron) | Opção 2 (PyInstaller) | Opção 3 (Docker) |
|----------|-------------------|----------------------|-----------------|
| **Tamanho** | ~250-300 MB | ~150-200 MB | ~500 MB+ |
| **Complexidade** | Alta | Média | Baixa |
| **Tempo de Build** | 10-15 min | 5-10 min | 2-5 min |
| **UX** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Manutenção** | Média | Baixa | Alta |
| **Distribuição** | Fácil | Fácil | Requer Docker |
| **Auto-update** | Sim | Não | Sim |
| **Recomendação** | ✅ Melhor UX | ✅ Mais simples | ⚠️ Requer Docker |

---

## 🚀 ROADMAP DE IMPLEMENTAÇÃO

### Fase 1: MVP (2-3 semanas)
- [ ] Implementar Opção 2 (PyInstaller)
- [ ] Criar `standalone_launcher.py`
- [ ] Configurar build do frontend
- [ ] Testar em Windows, macOS, Linux
- [ ] Criar scripts de build

### Fase 2: Melhorias (1-2 semanas)
- [ ] Adicionar auto-atualização
- [ ] Melhorar UX (splash screen, ícones)
- [ ] Otimizar tamanho do executável
- [ ] Adicionar logs e diagnóstico

### Fase 3: Opção 1 (Opcional - 3-4 semanas)
- [ ] Migrar para Electron/Tauri
- [ ] Implementar interface nativa
- [ ] Adicionar notificações desktop
- [ ] Melhorar integração com SO

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Preparação
- [ ] Criar `standalone_launcher.py`
- [ ] Criar `build_standalone.spec`
- [ ] Criar scripts de build (`.sh` e `.bat`)
- [ ] Ajustar `vite.config.js` para modo standalone
- [ ] Modificar `database_config.py` para SQLite standalone
- [ ] Criar `init_standalone_db.py`

### Build
- [ ] Testar build no Linux
- [ ] Testar build no macOS
- [ ] Testar build no Windows
- [ ] Verificar tamanho do executável
- [ ] Testar execução sem Python instalado

### Distribuição
- [ ] Criar scripts de empacotamento
- [ ] Criar README para usuários
- [ ] Criar ícones para cada plataforma
- [ ] Configurar assinatura de código (Windows/macOS)
- [ ] Criar instalador (NSIS para Windows, DMG para macOS)

### Testes
- [ ] Testar em máquina limpa (sem Python)
- [ ] Testar inicialização do banco
- [ ] Testar conexão com Binance API
- [ ] Testar todas as funcionalidades
- [ ] Testar performance

---

## 🔧 CONFIGURAÇÕES ESPECÍFICAS POR PLATAFORMA

### Windows
- **Formato:** `.exe` (PyInstaller) ou `.msi` (Instalador)
- **Tamanho estimado:** ~180 MB
- **Requisitos:** Windows 10+
- **Assinatura:** Recomendado (evita avisos do Windows Defender)

### macOS
- **Formato:** `.app` (Bundle) ou `.dmg` (Instalador)
- **Tamanho estimado:** ~200 MB
- **Requisitos:** macOS 11+
- **Notarização:** Necessária para distribuição fora da App Store

### Linux
- **Formato:** Executável binário ou `.AppImage`
- **Tamanho estimado:** ~150 MB
- **Requisitos:** glibc 2.31+
- **Dependências:** Nenhuma (tudo embutido)

---

## 📦 ESTRUTURA DE DISTRIBUIÇÃO FINAL

```
SNE_Radar_v1.0.0/
├── SNE_Radar              # Executável
├── data/                  # Dados do usuário (criado na primeira execução)
│   └── sne_radar.db
├── logs/                  # Logs (criado automaticamente)
├── README.txt
├── LICENSE
└── CHANGELOG.txt
```

---

## 🎯 PRÓXIMOS PASSOS

1. **Decidir qual opção implementar** (Recomendo Opção 2 para começar)
2. **Criar branch `feature/standalone`**
3. **Implementar `standalone_launcher.py`**
4. **Configurar PyInstaller**
5. **Testar build local**
6. **Criar CI/CD para builds automáticos**
7. **Testar em máquinas limpas**
8. **Preparar distribuição**

---

**Status:** 📋 Planejamento Completo - Pronto para implementação



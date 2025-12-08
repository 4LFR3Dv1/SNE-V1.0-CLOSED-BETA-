# 🚀 SNE RADAR - Sistema Neural Estratégico

Sistema profissional completo de análise técnica e trading assistido para criptomoedas, com múltiplas interfaces (CLI, Web, Desktop) e arquitetura híbrida.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-green.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Proprietary-yellow.svg)](LICENSE)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Características](#-características)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Build](#-build)
- [Uso](#-uso)
- [Documentação](#-documentação)
- [Contribuição](#-contribuição)

---

## 🎯 Visão Geral

O **SNE RADAR** é uma plataforma profissional de análise técnica para trading de criptomoedas, integrando:

- ✅ **12+ camadas de análise técnica** multi-timeframe
- ✅ **Interface web moderna** (Vue.js 3 + Vite)
- ✅ **Aplicação desktop nativa** (macOS/Windows)
- ✅ **Trading automatizado** com gestão de risco
- ✅ **Backtesting profissional** com múltiplas estratégias
- ✅ **Integração Telegram** para alertas
- ✅ **Arquitetura de microserviços** (GCP)

---

## ✨ Características

### **Análise Técnica Avançada**
- Análise multi-timeframe (1m, 5m, 15m, 1h, 4h, 1d)
- 50+ indicadores técnicos (RSI, MACD, Bollinger, Ichimoku, Fibonacci, etc.)
- Detecção de padrões gráficos (triângulos, wedges, etc.)
- Zonas magnéticas (suporte/resistência)
- Análise de confluência
- Análise de fluxo DOM (Depth of Market)
- Machine Learning para previsão de preços

### **Trading Automatizado**
- Execução automática de ordens (Bybit)
- Gestão de risco profissional
- Múltiplas estratégias configuráveis
- Pool de capital por estratégia
- Sistema de compliance
- Reconciliação automática

### **Monitoramento**
- Radar de oportunidades em tempo real
- Scanner de volume
- Scanner de pavios (wick radar)
- Alertas inteligentes (Telegram)
- Dashboard operacional

### **Backtesting**
- Backtest multi-estratégia
- Otimização de parâmetros
- Métricas profissionais (Sharpe, Sortino, etc.)
- Visualização de resultados

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    SNE RADAR SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   DESKTOP    │  │    WEB       │  │   CLOUD      │     │
│  │   APP        │  │  DASHBOARD   │  │  SERVICES    │     │
│  │ (PyInstaller)│  │  (Vue.js 3)  │  │  (GCP)       │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                           │                                 │
│         ┌─────────────────┴─────────────────┐              │
│         ▼                                   ▼               │
│  ┌──────────────┐                  ┌──────────────┐        │
│  │   BACKEND    │                  │    MOTOR     │        │
│  │   Flask      │◄─────────────────┤   ANÁLISE    │        │
│  │   + SocketIO │                  │  (Python)    │        │
│  └──────┬───────┘                  └──────────────┘        │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                          │
│  │   DATABASE   │                                          │
│  │ SQLite/Postgres│                                        │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

### **Componentes Principais**

- **Backend**: Flask + SocketIO (API REST + WebSocket)
- **Frontend**: Vue.js 3 + Vite + Tailwind CSS
- **Desktop**: PyInstaller + pywebview
- **Database**: SQLite (local) / PostgreSQL (produção)
- **Cloud**: Google Cloud Platform (microserviços)

---

## 🚀 Instalação

### **Pré-requisitos**

- **Python**: 3.10 ou superior
- **Node.js**: 18+ (LTS recomendado)
- **Git**: Para clonar o repositório

### **1. Clonar Repositório**

```bash
git clone https://github.com/seu-usuario/SNE_RADAR.git
cd SNE_RADAR
```

### **2. Configurar Ambiente Python**

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### **3. Configurar Frontend**

```bash
cd frontend
npm install
cd ..
```

### **4. Configurar Variáveis de Ambiente**

```bash
# Copiar template
cp .env.example .env

# Editar .env com suas configurações
# (API keys, tokens, etc.)
```

### **5. Inicializar Banco de Dados**

```bash
# Executar migrações Alembic
alembic upgrade head
```

---

## 🔨 Build

### **Build Frontend**

```bash
cd frontend
npm run build
cd ..
```

### **Build Desktop App (macOS)**

```bash
# Build frontend primeiro
cd frontend && npm run build && cd ..

# Build app
python -m PyInstaller build_mac.spec --clean --noconfirm
```

**Resultado**: `dist/SNE_RADAR.app`

### **Build Desktop App (Windows)**

```powershell
# PowerShell
.\build_windows.ps1

# Ou Batch
build_windows.bat
```

**Resultado**: `dist/SNE_RADAR.exe`

Para mais detalhes, veja: [docs/BUILD_WINDOWS_COMPLETO.md](docs/BUILD_WINDOWS_COMPLETO.md)

---

## 💻 Uso

### **Modo Web (Desenvolvimento)**

```bash
# Terminal 1: Backend
python sne_radar_web.py

# Terminal 2: Frontend (desenvolvimento)
cd frontend
npm run dev
```

Acesse: `http://localhost:5173`

### **Modo Desktop**

```bash
# Executar app desktop
python sne_desktop.py
```

### **Modo Terminal (CLI)**

```bash
python main.py
```

---

## 📚 Documentação

Documentação completa disponível em `docs/`:

- [Guia de Build Windows](docs/BUILD_WINDOWS_COMPLETO.md)
- [Guia de Deploy](docs/DEPLOYMENT_GUIDE.md)
- [Trading Automatizado](docs/COMO_FUNCIONA_TRADING_AUTOMATIZADO.md)
- [Proteção IP](docs/GUIA_PROTECAO_IP_DISTRIBUICAO.md)

---

## 🏗️ Estrutura do Projeto

```
SNE_RADAR/
├── app/                    # Aplicação Flask modular
├── frontend/               # Frontend Vue.js
├── services/               # Microserviços (GCP)
├── integrations/           # Integrações externas
├── monitors/               # Monitores de mercado
├── scanners/               # Scanners de oportunidades
├── notifications/          # Sistema de notificações
├── alembic/                # Migrações de banco
├── assets/                 # Assets (ícones, logos)
├── docs/                   # Documentação
├── sne_radar_web.py        # Aplicação Flask principal
├── sne_desktop.py          # Launcher desktop
├── motor_renan.py          # Motor de análise
└── requirements.txt        # Dependências Python
```

---

## 🔧 Configuração

### **Variáveis de Ambiente Principais**

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key

# Database
DATABASE_URL=sqlite:///data/sne_radar.db

# APIs (Opcional)
BINANCE_API_KEY=your_key
BYBIT_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
```

Veja `.env.example` para todas as variáveis disponíveis.

---

## 🧪 Desenvolvimento

### **Executar Testes**

```bash
# Backend
pytest tests/

# Frontend
cd frontend
npm run test
```

### **Linting**

```bash
# Python
flake8 .
black .

# Frontend
cd frontend
npm run lint
```

---

## 📦 Deploy

### **Deploy Cloud (GCP)**

Veja [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) para instruções completas.

### **Deploy Local**

```bash
# Build completo
./build_completo.sh

# Ou Windows
.\build_windows.ps1
```

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é proprietário. Todos os direitos reservados.

---

## 📞 Suporte

Para questões e suporte:
- Abra uma [Issue](https://github.com/seu-usuario/SNE_RADAR/issues)
- Consulte a [Documentação](docs/)

---

## 🎯 Roadmap

- [ ] Suporte para mais exchanges
- [ ] Interface mobile
- [ ] Mais estratégias de trading
- [ ] Dashboard analytics avançado
- [ ] API pública

---

**SNE RADAR** - Sistema Neural Estratégico para Trading de Criptomoedas 🚀

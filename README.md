# 🚀 SNE RADAR - Neural Trading Engine (Scroll Edition)

> **A Primeira Engine Neural de Trading Híbrida: Inteligência Off-Chain (Python) + Validação On-Chain (Scroll L2).**

![Scroll L2](https://img.shields.io/badge/Network-Scroll_Sepolia-FFA500?style=for-the-badge&logo=ethereum)
![License](https://img.shields.io/badge/License-On--Chain_Staking-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Distribution_Ready-blue?style=for-the-badge)

**Contract Address (Node Registry)**: [`0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7`](https://sepolia-blockscout.scroll.io/address/0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7) 📜

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
- [Smart Contract (Web3)](#-smart-contract-web3)
- [Instalação](#-instalação)
- [Build](#-build)
- [Uso](#-uso)
- [Documentação](#-documentação)
- [Contribuição](#-contribuição)

---

## 🎯 Visão Geral

O **SNE RADAR** é uma plataforma profissional de análise técnica para trading de criptomoedas, integrando:

1. **Cérebro (Off-Chain)**: Microsserviços Python processam 20+ indicadores e Machine Learning em tempo real.
2. **Verdade (On-Chain)**: A rede Scroll é usada para validação de licenças (DRM Descentralizado) e registro imutável de atividade dos nós (Proof of Uptime).

**Destaques:**

• ✅ **Tokenized Access**: O software só inicia se a carteira conectada possuir o Stake da Licença na Scroll.  
• ✅ **Relatórios Técnicos**: Gere dossiês visuais de cada sinal, não apenas alertas de compra/venda.  
• ✅ **DePIN Ready**: Preparado para rodar na futura SNE Box (Hardware Proprietário).

- ✅ **12+ camadas de análise técnica** multi-timeframe
- ✅ **Interface web moderna** (Vue.js 3 + Vite)
- ✅ **Aplicação desktop nativa** (macOS/Windows)
- ✅ **Trading automatizado** com gestão de risco
- ✅ **Backtesting profissional** com múltiplas estratégias
- ✅ **Integração Telegram** para alertas
- ✅ **Arquitetura de microserviços** (GCP)

---

## ✨ Características

### 🛡️ Integração Web3 (Scroll Layer 2)

• **Smart License Check**: Sistema anti-pirataria onde a licença é um ativo líquido (NFT/Token) em Stake.  
• **Healthcheck On-Chain**: Cada inicialização do sistema grava um hash na blockchain, criando um histórico auditável de uptime.  
• **Sovereign Wallet**: Integração nativa para assinatura de transações de alta frequência.

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

## 🔐 Smart Contract (Web3)

### ✅ SNELicenseRegistry - DEPLOYADO

O contrato **SNELicenseRegistry** está **operacional** na Scroll Sepolia Testnet e implementa o sistema de DRM descentralizado do SNE Radar.

**Informações do Contrato:**

- **Endereço**: [`0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7`](https://sepolia-blockscout.scroll.io/address/0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7)
- **Rede**: Scroll Sepolia Testnet
- **Chain ID**: 534351
- **Status**: ✅ Operacional
- **Explorer**: [Ver no Blockscout](https://sepolia-blockscout.scroll.io/address/0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7)

**Funcionalidades:**

- ✅ Verificação de licenças on-chain (`checkAccess`)
- ✅ Concessão de licenças vitalícias (`grantLifetimeLicense`)
- ✅ Revogação de licenças (`revokeLicense`)
- ✅ Distribuição em batch (até 100 licenças)
- ✅ Auditoria completa via eventos on-chain

**Documentação Completa:**

- 📄 [Arquitetura Técnica V2](TECHNICAL_ARCHITECTURE_V2.md) - Arquitetura alvo completa
- 📄 [Informações de Deploy](CONTRACT_DEPLOYMENT_INFO.md) - Detalhes do contrato deployado
- 📄 [Contrato Solidity](contracts/SNELicenseRegistry.sol) - Código-fonte do contrato

**Integração Python:**

```python
from web3 import Web3

# Conectar à Scroll Sepolia
w3 = Web3(Web3.HTTPProvider("https://sepolia-rpc.scroll.io"))
contract_address = "0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7"

# Carregar ABI e verificar licença
contract = w3.eth.contract(address=contract_address, abi=abi)
is_valid = contract.functions.checkAccess(wallet_address).call()

if is_valid:
    print("✅ Licença válida - Iniciando SNE Radar...")
else:
    print("❌ Acesso negado - Licença inválida")
```

---


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

- [Arquitetura Técnica V2](TECHNICAL_ARCHITECTURE_V2.md) - Arquitetura alvo Web3/Scroll L2
- [Informações de Deploy](CONTRACT_DEPLOYMENT_INFO.md) - Detalhes do contrato deployado
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
├── contracts/              # Smart Contracts (Solidity)
│   ├── SNELicenseRegistry.sol
│   └── deploy_info.json
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

# Web3 (Scroll L2)
SCROLL_RPC_URL=https://sepolia-rpc.scroll.io
SCROLL_CHAIN_ID=534351
LICENSE_CONTRACT_ADDRESS=0x2577879dE5bC7bc87db820C79f7d65bFfE2d9fb7

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

- Abra uma [Issue](https://github.com/4LFR3Dv1/SNE-V1.0-CLOSED-BETA-/issues)
- Consulte a [Documentação](docs/)

---

## 🗺️ Roadmap & Visão DePIN

### **Fase 1: Distribution (Atual)**
- [x] MVP da Engine Python (10 Meses de Dev)
- [x] Integração com Scroll Testnet (Sepolia)
- [x] **Smart Contract SNELicenseRegistry deployado** ✅
- [ ] Lançamento das primeiras 100 Licenças Vitalícias (Stake)
- [ ] Integração completa com cliente Python

### **Fase 2: The SNE Box (Q1 2026)**
- [ ] Desenvolvimento de Hardware Proprietário (Raspberry Pi Custom)
- [ ] Integração com Starlink para trading incensurável
- [ ] Mineração de Tokens via "Proof of Stake"

### **Fase 3: The Sovereign Network**
- [ ] Rede Mesh de dados financeiros descentralizados
- [ ] Governança descentralizada
- [ ] Healthcheck On-Chain completo (Proof of Uptime)

---

**SNE RADAR** - Sistema Neural Estratégico para Trading de Criptomoedas 🚀


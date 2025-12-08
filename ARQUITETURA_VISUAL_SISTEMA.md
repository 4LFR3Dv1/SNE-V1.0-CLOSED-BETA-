# 🏗️ ARQUITETURA VISUAL DO SISTEMA SNE

**Sistema:** SNE_BACKUP_CLEAN v3.0 Professional  
**Data:** Janeiro 2025

---

## 📊 DIAGRAMA GERAL DA ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE APRESENTAÇÃO                      │
├─────────────────────────────┬───────────────────────────────────────┤
│   TERMINAL (CLI)            │   DASHBOARD WEB (Browser)             │
│                             │                                       │
│   ┌─────────────────────┐   │   ┌─────────────────────────────┐   │
│   │   main.py           │   │   │   Vue.js 3 Application      │   │
│   │   (2,512 linhas)    │   │   │                             │   │
│   │                     │   │   │   ├─ Dashboard.vue          │   │
│   │   • Menu interativo │   │   │   ├─ Analysis.vue           │   │
│   │   • Radar visual    │   │   │   ├─ InteractiveChart.vue   │   │
│   │   • 11+ opções      │   │   │   └─ Backtesting.vue        │   │
│   └─────────────────────┘   │   └─────────────────────────────┘   │
│                             │              │                        │
│                             │              │ HTTP/WebSocket         │
└─────────────────────────────┴──────────────┼────────────────────────┘
                                             │
┌────────────────────────────────────────────▼────────────────────────┐
│                         CAMADA DE APLICAÇÃO                         │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │              sne-web (API Principal)                       │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │  │  Flask API   │  │  WebSocket   │  │  Motor Renan │    │   │
│   │  │  (REST)      │  │  (SocketIO)  │  │  (Análise)   │    │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │              sne-worker (Jobs Pesados)                     │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │  │  Backtest    │  │  Análises    │  │  Process.    │    │   │
│   │  │  Engine      │  │  Pesadas     │  │  Assíncrono  │    │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │              sne-auto (Automação)                          │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │  │  Scanner     │  │  Monitor     │  │  Cloud       │    │   │
│   │  │  Automático  │  │  24/7        │  │  Scheduler   │    │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │              sne-telegram (Integração)                     │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │  │  Webhook     │  │  Bot         │  │  Alertas     │    │   │
│   │  │  Handler     │  │  Telegram    │  │  Automáticos │    │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│   └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                         CAMADA DE DADOS                             │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│   │  SQLite      │  │  PostgreSQL  │  │  Redis       │           │
│   │  (Local Dev) │  │  (Cloud SQL) │  │  (Cache)     │           │
│   │              │  │              │  │              │           │
│   │  • MarketData│  │  • MarketData│  │  • Análises  │           │
│   │  • Alerts    │  │  • Users     │  │  • Sinais    │           │
│   │  • Users     │  │  • Alerts    │  │  • Cache     │           │
│   └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │                  APIs Externas                             │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │  │  Binance     │  │  Telegram    │  │  CoinGlass   │    │   │
│   │  │  API         │  │  Bot API     │  │  (Dados)     │    │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│   └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 FLUXO DE ANÁLISE TÉCNICA

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUXO DE ANÁLISE COMPLETA                        │
└─────────────────────────────────────────────────────────────────────┘

1. REQUISIÇÃO
   │
   ├─ Usuário solicita análise (symbol, timeframe)
   │
   ▼
2. COLETA DE DADOS
   │
   ├─ Binance API
   │  ├─ OHLCV (candles)
   │  ├─ Volume
   │  ├─ Order Book
   │  └─ Trades
   │
   ▼
3. PROCESSAMENTO
   │
   ├─ Normalização de timestamps
   ├─ Validação de dados
   └─ Preparação DataFrame (Pandas)
   │
   ▼
4. CÁLCULO DE INDICADORES
   │
   ├─ Indicadores Básicos
   │  ├─ EMA 8, 21
   │  ├─ RSI
   │  ├─ MACD
   │  └─ Bollinger Bands
   │
   ├─ Indicadores Avançados (20+)
   │  ├─ Stochastic
   │  ├─ ATR
   │  ├─ ADX
   │  ├─ Ichimoku
   │  └─ ... (15+ outros)
   │
   ▼
5. ANÁLISE DE CONTEXTO
   │
   ├─ Regime de Mercado
   │  ├─ BULL_TREND
   │  ├─ BEAR_TREND
   │  ├─ CONSOLIDATION
   │  └─ VOLATILE
   │
   ├─ Volatilidade (ATR %)
   ├─ Volume e Liquidez
   └─ Sessão Ativa (Londres/NY/Asiática)
   │
   ▼
6. ESTRUTURA DE MERCADO
   │
   ├─ Identificação de Topos/Fundos
   ├─ Higher Highs / Higher Lows
   ├─ Lower Highs / Lower Lows
   ├─ Suportes e Resistências (automático)
   └─ Price Action
   │
   ▼
7. MULTI-TIMEFRAME
   │
   ├─ Análise em 5+ TFs simultâneos
   │  ├─ 1m, 5m, 15m, 1h, 4h
   │  └─ Indicadores por TF
   │
   ├─ Score de Confluência
   └─ Alinhamento Direcional
   │
   ▼
8. DETECÇÃO DE PADRÕES
   │
   ├─ Padrões de Candlestick
   │  ├─ Doji, Martelo, Engolfo
   │  └─ ... (20+ padrões)
   │
   ├─ Chart Patterns
   │  ├─ Triângulos
   │  ├─ Flags
   │  └─ Wedges
   │
   └─ Divergências (RSI/MACD)
   │
   ▼
9. ZONAS MAGNÉTICAS
   │
   ├─ Sistema proprietário
   ├─ Zonas de atração
   └─ Distância a zonas
   │
   ▼
10. FLUXO ATIVO (DOM)
    │
    ├─ Depth of Market
    ├─ Pressão de Liquidez
    └─ Order Flow
    │
    ▼
11. CÁLCULO DE CONFLUÊNCIA
    │
    ├─ Confluência de Indicadores
    ├─ Confluência de Timeframes
    └─ Confluência de Níveis
    │
    ▼
12. GERAÇÃO DE SINAIS
    │
    ├─ Determinação de Sinal
    │  ├─ COMPRAR
    │  ├─ VENDER
    │  └─ AGUARDAR
    │
    ├─ Score de Confiança (0-100)
    └─ Priorização
    │
    ▼
13. NÍVEIS OPERACIONAIS
    │
    ├─ Entry Price
    ├─ Stop Loss
    └─ Take Profit
    │
    ▼
14. GESTÃO DE RISCO
    │
    ├─ Risk:Reward Ratio
    ├─ Análise de Risco
    └─ Recomendações
    │
    ▼
15. GERAÇÃO DE RELATÓRIO
    │
    ├─ Formatação
    ├─ Salvar em arquivo
    ├─ Enviar via Telegram
    └─ Retornar JSON/HTML
    │
    ▼
    RESULTADO FINAL
```

---

## 🌐 ARQUITETURA CLOUD (GCP)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GOOGLE CLOUD PLATFORM (GCP)                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         CLOUD RUN                                   │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│   │  sne-web     │  │ sne-worker   │  │  sne-auto    │           │
│   │              │  │              │  │              │           │
│   │  • API REST  │  │  • Backtest  │  │  • Scanner   │           │
│   │  • WebSocket │  │  • Jobs      │  │  • Monitor   │           │
│   │  • Motor     │  │  • Process.  │  │  • Alertas   │           │
│   │              │  │              │  │              │           │
│   │  Auto-scale: │  │  Auto-scale: │  │  Auto-scale: │           │
│   │  0-10 inst.  │  │  0-10 inst.  │  │  0-10 inst.  │           │
│   └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                      │
│   ┌──────────────┐                                                  │
│   │sne-telegram  │                                                  │
│   │              │                                                  │
│   │  • Webhook   │                                                  │
│   │  • Bot       │                                                  │
│   │              │                                                  │
│   │  Auto-scale: │                                                  │
│   │  0-10 inst.  │                                                  │
│   └──────────────┘                                                  │
└──────────────┬───────────────────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────────────────┐
│                    CLOUD SQL (PostgreSQL 15)                        │
│                                                                      │
│   • Instância gerenciada                                            │
│   • Backup automático                                               │
│   • Alta disponibilidade                                            │
│   • Conexão privada (VPC)                                           │
└──────────────┬───────────────────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────────────────┐
│                    OUTROS SERVIÇOS GCP                              │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│   │  Secret      │  │  Cloud       │  │  Artifact    │           │
│   │  Manager     │  │  Scheduler   │  │  Registry    │           │
│   │              │  │              │  │              │           │
│   │  • API Keys  │  │  • Jobs      │  │  • Docker    │           │
│   │  • Passwords │  │  • Cron      │  │  • Imagens   │           │
│   │  • Secrets   │  │  • Trigger   │  │              │           │
│   └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│   │  Cloud       │  │  VPC         │  │  Cloud       │           │
│   │  Build       │  │  Connector   │  │  Monitoring  │           │
│   │              │  │              │  │              │           │
│   │  • CI/CD     │  │  • Conexão   │  │  • Logs      │           │
│   │  • Pipeline  │  │  • Privada   │  │  • Métricas  │           │
│   │              │  │              │  │  • Alerts    │           │
│   └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📱 COMPONENTES DO FRONTEND

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VUE.JS 3 APPLICATION                             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         ROUTER (Vue Router)                         │
│                                                                      │
│   /dashboard  →  Dashboard.vue                                      │
│   /analysis   →  Analysis.vue                                       │
│   /chart      →  InteractiveChart.vue                               │
│   /backtest   →  Backtesting.vue                                    │
│   /settings   →  Settings.vue                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      STORES (Pinia)                                 │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│   │  market.js   │  │ dashboard.js │  │  user.js     │           │
│   │              │  │              │  │              │           │
│   │  • Symbol    │  │  • Settings  │  │  • Auth      │           │
│   │  • Timeframe │  │  • Layout    │  │  • Profile   │           │
│   │  • Analysis  │  │  • State     │  │              │           │
│   └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    COMPONENTES PRINCIPAIS                           │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │              INTERACTIVE CHART                             │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │  │ Candlesticks │  │  Indicators  │  │  S/R Lines   │    │   │
│   │  │  (Real-time) │  │  (EMA/RSI)   │  │  (Dynamic)   │    │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │  │  Tooltips    │  │  Zoom/Pan    │  │  Price Line  │    │   │
│   │  │  (On hover)  │  │  Controls    │  │  (Current)   │    │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│   │                                                             │   │
│   │  • Polling: 5s                                             │   │
│   │  • Library: lightweight-charts                            │   │
│   │  • Responsive: Yes                                         │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │              ANALYSIS COMPONENTS                           │   │
│   │  • SignalHero.vue          - Exibe sinal e score           │   │
│   │  • OperationalLevels.vue   - Entry/SL/TP                   │   │
│   │  • ConfluenceGrid.vue      - Grid de confluência           │   │
│   │  • MultiTimeframeTimeline.vue - Timeline multi-TF          │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │              SERVICES                                      │   │
│   │  • api.js       - HTTP/REST client                         │   │
│   │  • websocket.js - WebSocket client                         │   │
│   └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 SEGURANÇA E INFRAESTRUTURA

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAMADAS DE SEGURANÇA                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         AUTENTICAÇÃO                                │
│                                                                      │
│   • Flask-Login (Básico)                                            │
│   • Service Accounts (GCP)                                          │
│   ⚠️  Recomendado: JWT tokens                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         SEGREDOS                                    │
│                                                                      │
│   • Secret Manager (GCP)                                            │
│   • Nunca em código/env                                             │
│   • Rotação automática                                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         COMUNICAÇÃO                                 │
│                                                                      │
│   • HTTPS obrigatório (Cloud Run)                                   │
│   • VPC Connector (Conexão privada)                                 │
│   • Rate Limiting (Flask-Limiter)                                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         PERMISSÕES                                  │
│                                                                      │
│   • Service Accounts com permissões mínimas                         │
│   • IAM roles específicas                                           │
│   • Segregamento de responsabilidades                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 FLUXO DE DADOS ENTRE COMPONENTES

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUXO DE DADOS                                   │
└─────────────────────────────────────────────────────────────────────┘

FRONTEND (Vue.js)
    │
    │ HTTP GET /api/analyze?symbol=BTCUSDT&timeframe=1h
    │
    ▼
BACKEND (sne-web)
    │
    │ motor_renan.analise_completa()
    │
    ├─→ Binance API (Dados de mercado)
    │
    ├─→ Módulos de Análise
    │   ├─ contexto_global.py
    │   ├─ estrutura_mercado.py
    │   ├─ multi_timeframe.py
    │   ├─ indicadores_avancados.py
    │   └─ ... (10+ módulos)
    │
    ├─→ Database (Cache/Storage)
    │   └─ PostgreSQL
    │
    ▼
RESULTADO JSON
    │
    ├─ Sinal (COMPRAR/VENDER/AGUARDAR)
    ├─ Score (0-100)
    ├─ Níveis (Entry/SL/TP)
    ├─ Indicadores
    ├─ Candles
    └─ Análises detalhadas
    │
    ▼
FRONTEND (Vue.js)
    │
    ├─ Renderiza no gráfico
    ├─ Atualiza componentes
    └─ Exibe informações
```

---

## 🎯 MÓDULOS DE ANÁLISE E SUAS DEPENDÊNCIAS

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEPENDÊNCIAS ENTRE MÓDULOS                      │
└─────────────────────────────────────────────────────────────────────┘

motor_renan.py (ORQUESTRADOR)
    │
    ├─→ contexto_global.py
    │   └─→ estrutura_mercado.py
    │
    ├─→ multi_timeframe.py
    │   ├─→ indicadores.py
    │   └─→ indicadores_avancados.py
    │
    ├─→ padroes_graficos.py
    │   └─→ indicadores.py
    │
    ├─→ catalogo_magnetico.py
    │
    ├─→ fluxo_ativo.py
    │
    ├─→ confluencia.py
    │   ├─→ multi_timeframe.py
    │   └─→ fluxo_ativo.py
    │
    ├─→ gestao_risco_profissional.py
    │   └─→ estrutura_mercado.py
    │
    └─→ relatorio_profissional.py
        └─→ Todos os módulos acima
```

---

**Diagramas criados para facilitar o entendimento da arquitetura!** ✅



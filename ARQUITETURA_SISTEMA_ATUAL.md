# 🏗️ ARQUITETURA DO SISTEMA SNE RADAR 3.0

## 📊 VISÃO GERAL

**SNE RADAR 3.0** é um sistema profissional de análise técnica e trading assistido, desenvolvido em Python, que integra múltiplas camadas de análise para fornecer insights acionáveis em tempo real.

---

## 🎯 COMPONENTES PRINCIPAIS

### **1. NÚCLEO DE ANÁLISE**

#### **Motor Renan** (`motor_renan.py`)
- **Função:** Orquestrador principal de análise multi-camada
- **Inputs:** Par, Timeframe
- **Processo:**
  1. Coleta dados da Binance
  2. Análise de contexto global (regime, volatilidade, sessão)
  3. Análise de estrutura (HH/HL, S/R)
  4. Multi-timeframe (5 TFs: 1m, 5m, 15m, 1h, 4h)
  5. Detecção de zonas magnéticas
  6. Análise de fluxo DOM
  7. Cálculo de confluência
  8. Geração de síntese inteligente
- **Output:** Análise completa com recomendação e score de confiança

---

### **2. CAMADAS DE ANÁLISE**

#### **A. Contexto Global** (`contexto_global.py`)
- Identificação de regime (BULL_TREND, BEAR_TREND, CONSOLIDATION, VOLATILE)
- Cálculo de volatilidade (ATR %)
- Análise de volume (ratio, status)
- Detecção de sessão ativa (Londres, NY, Asiática)
- Score de liquidez (0-10)

#### **B. Estrutura de Mercado** (`estrutura_mercado.py`)
- Identificação de topos e fundos (scipy.signal.find_peaks)
- Classificação de tendência (HH/HL, LH/LL)
- Detecção de suportes e resistências (agrupamento por tolerância)
- Análise de price action (tipo de vela, corpo, sombras)

#### **C. Multi-Timeframe** (`multi_timeframe.py`)
- Análise simultânea em 5 timeframes
- Cálculo de EMAs, RSI, MACD por TF
- Score de confluência entre TFs
- Resumo de alinhamento direcional

#### **D. Padrões Gráficos** (`padroes_graficos.py`)
- Detecção de divergências RSI/MACD
- Padrões de candlestick (Doji, Martelo, Engolfo)
- Chart patterns (Triângulos, Flags)
- Níveis de Fibonacci (retracements)

#### **E. Zonas Magnéticas** (`catalogo_magnetico.py`)
- Sistema proprietário de detecção de zonas de atração
- Catálogo histórico de zonas
- Cálculo de força de zona
- Probabilidade de ruptura

#### **F. Fluxo de Liquidez** (`fluxo_ativo.py`)
- Análise de Order Book (DOM)
- Cálculo de pressão Bid/Ask
- Detecção de paredes de liquidez
- Score de desequilíbrio

#### **G. Confluência** (`confluencia.py`)
- Sistema de pesos adaptativos:
  - Multi-TF: 3.0 pts
  - Fluxo DOM: 2.5 pts
  - Zonas Magnéticas: 2.0 pts
  - Sentiment: 1.5 pts
  - Volume: 1.0 pts
- Score final: 0-10
- Interpretação qualitativa

---

### **3. MÓDULOS DE CONTEXTO**

#### **Contexto Macro** (`contexto_macro.py`)
- Análise de múltiplos pares (BTC, ETH, BNB)
- Detecção de regime dominante
- Sentiment global (Fear & Greed, Funding Rate)

#### **Sentiment Global** (`sentimento_global.py`)
- Fear & Greed Index
- Funding Rate (Binance Futures)
- Open Interest
- Correlações entre ativos

#### **Projeções** (`projecoes.py`)
- 3 cenários probabilísticos:
  - Base (maior probabilidade)
  - Otimista (continuação)
  - Pessimista (correção)
- Cálculo dinâmico de targets
- Estimativa de timeframes

---

### **4. SISTEMAS DE RELATÓRIOS**

#### **Relatório Técnico** (`relatorio_tecnico.py`)
- Orquestrador de relatórios completos
- Integra todas as camadas de análise
- Formatação profissional (texto)
- Salvamento automático em `/reports/`

#### **Relatórios Periódicos** (`relatorios_periodicos.py`)
- **Horário (RH):** Timeframe 1h
- **Diário (RD):** Timeframe 4h, salvo em `/reports/daily/`
- **Semanal (RS):** Timeframe 1d, salvo em `/reports/weekly/`

#### **Formatter** (`formatter_relatorio.py`)
- Templates de texto institucional
- Formatação com emojis e estrutura
- Natural language generation
- IDs únicos de rastreamento

---

### **5. ANÁLISE MULTI-PAR**

#### **Multi-Pair Análise** (`multi_pair_analise.py`)
- Análise comparativa de 5 pares principais
- Ranking por confluência
- Identificação de melhor/pior setup

#### **DOM Profundo** (`dom_profundo.py`)
- Análise avançada de Order Book
- Cálculo de spread e densidade
- Detecção de paredes de liquidez
- Interpretação de pressão de mercado

---

### **6. VISUALIZAÇÃO E MONITORAMENTO**

#### **Dashboard Tempo Real** (`dashboard_tempo_real.py`)
- Monitoramento contínuo (atualização 30s)
- Top 3 pares em tabela
- Score visual (🟢🟡🔴)
- Execução em loop (Ctrl+C para sair)

#### **Heatmap Correlações** (`heatmap_correlacoes.py`)
- Matriz de correlações entre pares
- Visualização em emoji (🟢🟡⚪🔴)
- Identificação de pares correlacionados
- Base: últimos 100 períodos

#### **Radar Visual** (integrado em `main.py`)
- Gráfico de candlestick com indicadores
- Zonas magnéticas sobrepostas
- Análise de ruptura em tempo real

---

### **7. AUTOMAÇÃO E ALERTAS**

#### **Auto Análise** (`auto_analise.py`)
- Ciclos automáticos programáveis
- Envio para Telegram quando score >= 7
- Execução assíncrona (asyncio)
- Monitoramento 24/7

#### **Alertas Técnicos** (`alertas_tecnicos.py`)
- 4 tipos de alerta:
  1. Score de confluência >= X
  2. Regime específico (Bull/Bear)
  3. Ruptura de zona magnética
  4. Pressão DOM extrema
- Notificação automática via Telegram
- Monitoramento contínuo configurável

---

### **8. INTEGRAÇÃO TELEGRAM**

#### **Xenos Bot** (`xenos_bot.py`)
- Envio de mensagens formatadas
- Sanitização automática de HTML
- Controle de duplicidade
- Retry automático (3 tentativas)
- Parse mode: HTML (tags suportadas: `<b>`, `<i>`, `<code>`)

#### **Mensagens Suportadas:**
- Análises completas (Motor Renan)
- Sinais de trading (Modo Agressivo)
- Relatórios técnicos
- Alertas automáticos
- Mensagens manuais

---

### **9. INDICADORES TÉCNICOS**

#### **Módulo de Indicadores** (`indicadores.py`)
- **Médias Móveis:** EMA8, EMA21, SMA50, SMA200
- **Osciladores:** RSI, Stochastic, Williams %R, CCI
- **Momentum:** MACD (linha, sinal, histograma)
- **Volatilidade:** Bollinger Bands, ATR
- **Volume:** OBV (On-Balance Volume)
- **Tendência:** ADX, Ichimoku
- **Níveis:** Pivot Points, Volume Profile

---

### **10. MODOS DE TRADING**

#### **Modo Agressivo** (`modo_agressivo.py`)
- Sinais sem filtros restritivos
- Sempre retorna um setup
- TP1/TP2/TP3 escalonados
- SL calculado (0.3%)
- R/R: 1:1.5 a 1:2.0
- Aviso de risco explícito

#### **Trader Direto** (`trader_direto.py`)
- Filtros de qualidade aplicados
- Validação multi-critério
- Setup apenas se confluência >= 6
- Cálculo de posição (gestão de risco)

#### **Modo Renan Ultra** (`modo_renan.py`)
- Integração de campos magnéticos
- Decisão baseada em zonas
- Contexto + Estrutura + Magnetismo
- Setup completo com entry/tp/sl

---

## 🔄 FLUXO DE DADOS

```
┌─────────────────┐
│  BINANCE API    │ (Klines, Order Book, Funding)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  COLETA E NORMALIZAÇÃO DE DADOS     │
│  - Timeframe normalizado (.lower()) │
│  - DataFrame com OHLCV              │
│  - Cálculo de indicadores           │
└────────┬────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│           CAMADAS DE ANÁLISE (PARALELAS)         │
├──────────────────────────────────────────────────┤
│ Contexto │ Estrutura │ MTF │ Padrões │ Zonas │   │
│  Global  │  Mercado  │     │ Gráficos│ Magn. │   │
└────┬─────┴─────┬─────┴──┬──┴────┬────┴───┬───────┘
     │           │        │       │        │
     └───────────┴────────┴───────┴────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │  CÁLCULO DE CONFLUÊNCIA │
         │  Score ponderado (0-10) │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │  SÍNTESE INTELIGENTE    │
         │  - Viés               │
         │  - Recomendação       │
         │  - Entry type         │
         │  - Risco              │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │  FORMATAÇÃO E SAÍDA     │
         │  - Terminal             │
         │  - Telegram             │
         │  - Arquivo (reports/)   │
         └─────────────────────────┘
```

---

## 🗄️ ESTRUTURA DE ARQUIVOS

```
SNE_BACKUP_CLEAN/
│
├── main.py                      # Terminal principal
├── xenos_bot.py                 # Integração Telegram
│
├── NÚCLEO DE ANÁLISE
│   ├── motor_renan.py           # Orquestrador principal
│   ├── contexto_global.py       # Regime, volatilidade, sessão
│   ├── estrutura_mercado.py     # HH/HL, S/R
│   ├── multi_timeframe.py       # Análise 5 TFs
│   ├── confluencia.py           # Score de confluência
│   └── indicadores.py           # Indicadores técnicos
│
├── MÓDULOS DE CONTEXTO
│   ├── contexto_macro.py        # Análise macro
│   ├── sentimento_global.py     # Sentiment analysis
│   ├── padroes_graficos.py      # Padrões técnicos
│   └── projecoes.py             # Cenários probabilísticos
│
├── SISTEMAS ESPECIALIZADOS
│   ├── catalogo_magnetico.py    # Zonas magnéticas
│   ├── fluxo_ativo.py           # DOM e liquidez
│   ├── dom_profundo.py          # Análise avançada DOM
│   └── multi_pair_analise.py    # Comparação pares
│
├── RELATÓRIOS
│   ├── relatorio_tecnico.py     # Relatório completo
│   ├── relatorios_periodicos.py # RH/RD/RS
│   └── formatter_relatorio.py   # Formatador de texto
│
├── VISUALIZAÇÃO
│   ├── dashboard_tempo_real.py  # Monitor ao vivo
│   └── heatmap_correlacoes.py   # Matriz correlações
│
├── AUTOMAÇÃO
│   ├── auto_analise.py          # Análise 24/7
│   └── alertas_tecnicos.py      # Sistema de alertas
│
├── MODOS DE TRADING
│   ├── modo_agressivo.py        # Sinais agressivos
│   ├── trader_direto.py         # Sinais filtrados
│   └── modo_renan.py            # Campos magnéticos
│
├── MÓDULOS DE SUPORTE
│   ├── backtest.py              # Backtesting
│   ├── mente_fluida.py          # Ressonância
│   └── gestao_risco.py          # Risk management
│
└── OUTPUTS
    ├── reports/                 # Relatórios salvos
    ├── reports/daily/          # Relatórios diários
    ├── reports/weekly/         # Relatórios semanais
    └── logs/                   # Logs de sistema
```

---

## 🎛️ INTERFACE DE TERMINAL

### **Menu Principal:**
```
🔍 ANÁLISE TÉCNICA:
R)     Motor Renan (Análise Completa)
CTX)   Contexto Macro
MULT)  Multi-Pair Análise
DOM)   Análise DOM Profunda

📊 RELATÓRIOS:
RT)    Relatório Técnico
RH)    Relatório Horário
RD)    Relatório Diário
RS)    Relatório Semanal

📈 VISUALIZAÇÃO:
1)     Radar Visual (Gráfico)
DASH)  Dashboard Tempo Real
HEAT)  Heatmap Correlações

🤖 AUTOMAÇÃO:
AUTO)  Análise Automática 24/7
ALERT) Sistema de Alertas

📱 TELEGRAM:
TG)    Configurar Telegram
SEND)  Enviar Manual

⚙️ SISTEMA:
CFG)   Configurações
INFO)  Informações
3)     Sair
```

---

## 🔐 CONFIGURAÇÃO

### **Variáveis de Ambiente:**
- `TELEGRAM_BOT_TOKEN` - Token do bot
- `TELEGRAM_CHAT_ID` - ID do chat
- `BINANCE_API_KEY` - API key (opcional)
- `BINANCE_SECRET_KEY` - Secret key (opcional)

### **Parâmetros Configuráveis:**
- Pares principais
- Intervalos de atualização
- Thresholds de alertas
- Capital de trading
- Risk per trade (%)
- R/R mínimo

---

## 📊 TECNOLOGIAS UTILIZADAS

### **Core:**
- Python 3.8+
- pandas (análise de dados)
- numpy (cálculos numéricos)
- requests (API calls)

### **Análise Técnica:**
- scipy (detecção de picos)
- TA-Lib equivalente (indicadores)

### **Visualização:**
- matplotlib (gráficos)
- mplfinance (candlesticks)

### **Async:**
- asyncio (operações assíncronas)

### **Outros:**
- pytz (timezone handling)
- datetime (timestamps)

---

## 🛡️ ROBUSTEZ E CONFIABILIDADE

### **Tratamento de Erros:**
- ✅ Try/except em todas as funções críticas
- ✅ Fallbacks para dados ausentes
- ✅ Validação de NaN e zero
- ✅ Retry automático (Telegram)
- ✅ Timeouts configurados (API calls)

### **Validações:**
- ✅ Normalização de timeframes (.lower())
- ✅ Sanitização de HTML (Telegram)
- ✅ Proteção contra divisão por zero
- ✅ Verificação de listas vazias
- ✅ Validação de tipos de dados

### **Logging:**
- ✅ Feedback visual de processos
- ✅ Mensagens de erro descritivas
- ✅ Logs de rupturas (arquivo)
- ✅ Histórico de sinais (memória)

---

## 🎯 CASOS DE USO

### **1. Day Trader:**
```
Comando >> R (par: BTC, tf: 15m)
→ Análise rápida com confluência
→ Decisão de entrada/saída
```

### **2. Swing Trader:**
```
Comando >> RT (par: ETH, tf: 4h)
→ Relatório completo salvo
→ Análise estrutural profunda
```

### **3. Analista:**
```
Comando >> MULT (tf: 1h)
→ Ranking de pares
→ Identificação de oportunidades
```

### **4. Automação:**
```
Comando >> AUTO
→ Monitoramento 24/7
→ Alertas automáticos Telegram
```

---

## 🚀 DIFERENCIAIS

### **1. Sistema Modular:**
- Cada componente independente
- Fácil manutenção e expansão
- Reutilização de código

### **2. Inteligência Multi-Camada:**
- Confluência adaptativa
- Pesos dinâmicos por contexto
- Aprendizado histórico (memória)

### **3. Integração Completa:**
- Telegram nativo
- Múltiplos timeframes
- Análise técnica + DOM + Sentiment

### **4. Profissional:**
- Formatação institucional
- Rastreabilidade (IDs únicos)
- Gestão de risco integrada
- Relatórios salvos

---

## 📈 ROADMAP FUTURO

### **Melhorias Planejadas:**
1. Machine Learning para ajuste automático de pesos
2. Backtesting avançado com métricas
3. API REST para integração externa
4. Dashboard web interativo
5. Mobile app (notificações push)
6. Trading automatizado (com aprovação)

---

## ✅ STATUS ATUAL

**VERSÃO:** 3.0 Professional
**STATUS:** ✅ Operacional e testado
**COMANDOS:** 15+ funcionais
**MÓDULOS:** 25+ integrados
**COBERTURA:** Análise técnica completa

---

**Sistema profissional de análise técnica e trading assistido, pronto para uso em produção! 🎯**





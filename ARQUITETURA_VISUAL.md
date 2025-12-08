# 🏗️ ARQUITETURA VISUAL DO SNE RADAR

## 📊 DIAGRAMA GERAL DO SISTEMA

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUÁRIO / TRADER                             │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   TERMINAL    │               │   WEB APP     │
│   (main.py)   │               │(sne_radar_web)│
└───────┬───────┘               └───────┬───────┘
        │                               │
        │ ┌─────────────────────────────┘
        │ │
        ▼ ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE NEGÓCIO                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   SINAIS     │  │   ANÁLISE    │  │   CONTEXTO   │              │
│  │   RÁPIDOS    │  │ ESTRATÉGICA  │  │   MERCADO    │              │
│  │              │  │              │  │              │              │
│  │ • Momentum   │  │ • Backtest   │  │ • Regime     │              │
│  │ • Volume     │  │ • Mente      │  │ • Força      │              │
│  │ • Volatil.   │  │   Fluida     │  │ • Score      │              │
│  └──────────────┘  │ • Ciclos     │  │ • Ranking    │              │
│                    │ • Fluxo      │  └──────────────┘              │
│                    │ • Catálogo   │                                 │
│                    └──────────────┘                                 │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ PRIORIZAÇÃO  │  │   ALERTAS    │  │   TELEGRAM   │              │
│  │              │  │ INTELIGENTES │  │              │              │
│  │ • Ponderação │  │              │  │ • Mensagens  │              │
│  │ • Entrada    │  │ • Críticos   │  │ • Imagens    │              │
│  │ • Recomend.  │  │ • Altos      │  │ • Relatórios │              │
│  └──────────────┘  │ • Médios     │  └──────────────┘              │
│                    └──────────────┘                                 │
└─────────────────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐               ┌───────────────┐
│   BINANCE     │               │   COINGLASS   │
│     API       │               │   CMC API     │
└───────────────┘               └───────────────┘
```

---

## 🔄 FLUXO DE DADOS - SINAIS RÁPIDOS (Opção 0)

```
┌──────────┐
│ USUÁRIO  │
│ Digite 0 │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   trading_signals.py                    │
│   encontrar_melhor_oportunidade()       │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   Loop: 12 pares                        │
│   ┌─────────────────────────────────┐   │
│   │ buscar_dados_rapido(symbol)     │   │
│   │         ↓                       │   │
│   │ analisar_oportunidade_real()    │   │
│   │         ↓                       │   │
│   │ ┌─────────────────────────┐     │   │
│   │ │ Calcular Momentum       │     │   │
│   │ │ (5 velas, ≥0.5%)        │     │   │
│   │ │ Score: 0-40 pontos      │     │   │
│   │ └─────────────────────────┘     │   │
│   │         ↓                       │   │
│   │ ┌─────────────────────────┐     │   │
│   │ │ Calcular Volume         │     │   │
│   │ │ (ratio ≥1.3x)           │     │   │
│   │ │ Score: 0-30 pontos      │     │   │
│   │ └─────────────────────────┘     │   │
│   │         ↓                       │   │
│   │ ┌─────────────────────────┐     │   │
│   │ │ Calcular Volatilidade   │     │   │
│   │ │ (0.3% < vol < 3%)       │     │   │
│   │ │ Score: 0-30 pontos      │     │   │
│   │ └─────────────────────────┘     │   │
│   │         ↓                       │   │
│   │ Score Total = Σ (0-100)         │   │
│   │         ↓                       │   │
│   │ Score < 60? → None              │   │
│   │ Score ≥ 60? → Continuar         │   │
│   │         ↓                       │   │
│   │ ┌─────────────────────────┐     │   │
│   │ │ Determinar Ação         │     │   │
│   │ │ Momentum > 0: COMPRAR   │     │   │
│   │ │ Momentum < 0: VENDER    │     │   │
│   │ └─────────────────────────┘     │   │
│   │         ↓                       │   │
│   │ ┌─────────────────────────┐     │   │
│   │ │ Calcular Níveis         │     │   │
│   │ │ • Entrada: preço atual  │     │   │
│   │ │ • Alvo: resist/suporte  │     │   │
│   │ │ • Stop: 0.5% fora       │     │   │
│   │ └─────────────────────────┘     │   │
│   │         ↓                       │   │
│   │ R/R < 1.5? → None               │   │
│   │ R/R ≥ 1.5? → Retornar           │   │
│   └─────────────────────────────┘   │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   Ordenar por:                          │
│   1. Score (maior primeiro)             │
│   2. Risco/Retorno (maior primeiro)     │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   Retornar melhor oportunidade          │
│   (ou None se nenhuma)                  │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   exibir_oportunidade()                 │
│   ┌─────────────────────────────────┐   │
│   │ 🎯 MELHOR OPORTUNIDADE          │   │
│   │ Symbol: LINKUSDT                │   │
│   │ Ação: COMPRAR                   │   │
│   │ Entrada: $19.56                 │   │
│   │ Alvo: $20.10 (+2.76%)           │   │
│   │ Stop: $19.35 (-1.07%)           │   │
│   │ R/R: 1:2.6                      │   │
│   │ Score: 75/100                   │   │
│   │ Razões:                         │   │
│   │ • Momentum +1.2%                │   │
│   │ • Volume 45% acima              │   │
│   │ • Volatilidade ideal            │   │
│   └─────────────────────────────────┘   │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   Enviar para Telegram? (s/n)           │
└────┬────────────────────────────────────┘
     │
     ▼ (se sim)
┌─────────────────────────────────────────┐
│   gerar_mensagem_telegram()             │
│            ↓                            │
│   enviar_oraculo()                      │
│            ↓                            │
│   ✅ Enviado!                           │
└─────────────────────────────────────────┘

Tempo Total: ~30 segundos
```

---

## 🔄 FLUXO DE DADOS - RADAR VISUAL (Opção 1)

```
┌──────────┐
│ USUÁRIO  │
│ Digite 1 │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   main.py                               │
│   iniciar_radar()                       │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   Inicialização Assíncrona              │
│   ┌─────────────────────────────────┐   │
│   │ Criar loop asyncio              │   │
│   │         ↓                       │   │
│   │ iniciar_oraculo()               │   │
│   │ (Telegram)                      │   │
│   │         ↓                       │   │
│   │ iniciar_contexto_tempo_real()   │   │
│   │ (Thread separada)               │   │
│   │         ↓                       │   │
│   │ Configurar figura matplotlib    │   │
│   │ (3 subplots)                    │   │
│   └─────────────────────────────────┘   │
└────┬────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│   FuncAnimation                         │
│   (atualizar, interval=5000ms)          │
└────┬────────────────────────────────────┘
     │
     │ ┌───────────────────────────────────┐
     │ │ Loop Infinito (a cada 5 segundos) │
     └─┤                                   │
       │   ┌───────────────────────────┐   │
       │   │ atualizar(frame)          │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Limpar eixos              │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ buscar_dados_binance()    │   │
       │   │ → DataFrame (100 velas)   │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ buscar_book()             │   │
       │   │ → Bids/Asks (DOM)         │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Plotar Gráfico            │   │
       │   │ • Candles                 │   │
       │   │ • EMA8, EMA21, SMA200     │   │
       │   │ • Bollinger Bands         │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Detecção de Rupturas      │   │
       │   │ detectar_ruptura_         │   │
       │   │ gravitacional()           │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Módulos Estratégicos      │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ mente_fluidica_     │   │   │
       │   │ │ verificar_          │   │   │
       │   │ │ resonancia()        │   │   │
       │   │ └─────────────────────┘   │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ mente_fluidica_     │   │   │
       │   │ │ detectar_ciclos()   │   │   │
       │   │ └─────────────────────┘   │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ analisar_fluxo_     │   │   │
       │   │ │ mental()            │   │   │
       │   │ └─────────────────────┘   │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ atualizar_catalogo()│   │   │
       │   │ └─────────────────────┘   │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ executar_backtest() │   │   │
       │   │ └─────────────────────┘   │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Análise de Contexto       │   │
       │   │ analisar_contexto_radar() │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ Análise Local       │   │   │
       │   │ │ (par atual)         │   │   │
       │   │ └─────────────────────┘   │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ Análise Global      │   │   │
       │   │ │ (12 pares)          │   │   │
       │   │ └─────────────────────┘   │   │
       │   │ ┌─────────────────────┐   │   │
       │   │ │ Recomendação        │   │   │
       │   │ └─────────────────────┘   │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Plotar DOM                │   │
       │   │ (Book de Ordens)          │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Atualizar HUDs            │   │
       │   │ • Zona Ativa              │   │
       │   │ • Energia Magnética       │   │
       │   │ • Sinal                   │   │
       │   │ • Score                   │   │
       │   │ • Regime                  │   │
       │   │ • Risco                   │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   ┌───────────────────────────┐   │
       │   │ Exibir Gráfico            │   │
       │   │ (matplotlib window)       │   │
       │   └───────────────────────────┘   │
       │            ↓                      │
       │   Aguardar 5 segundos             │
       │            ↓                      │
       │   Repetir (próxima iteração)      │
       └───────────────────────────────────┘

Atualização: A cada 5 segundos
Módulos: Todos ativos
```

---

## 🗂️ ESTRUTURA DE MÓDULOS

```
SNE_BACKUP_CLEAN/
│
├── 🎯 CORE (Sistema Principal)
│   ├── main.py ⭐ (1107 linhas)
│   │   ├─ Terminal interativo
│   │   ├─ Radar visual
│   │   ├─ Orquestração
│   │   └─ Integração Telegram
│   │
│   ├── trading_signals.py 🆕 (267 linhas)
│   │   ├─ Sinais rápidos
│   │   ├─ Análise objetiva
│   │   └─ Output direto
│   │
│   └── backtest.py
│       ├─ Simulação histórica
│       ├─ Métricas
│       └─ Estado global
│
├── 🧠 ANÁLISE ESTRATÉGICA
│   ├── mente_fluida.py
│   │   └─ Ressonância neural
│   │
│   ├── mente_fluida_ciclica.py
│   │   └─ Detecção de ciclos
│   │
│   ├── fluxo_mental.py
│   │   ├─ Congestão magnética
│   │   ├─ Túneis gravitacionais
│   │   └─ Ressonância histórica
│   │
│   └── catalogo_magnetico.py
│       ├─ Mapeamento de zonas
│       └─ Força magnética
│
├── 📊 CONTEXTO DE MERCADO
│   ├── contexto_mercado.py
│   │   ├─ Regime de mercado
│   │   ├─ Força do sinal
│   │   ├─ Score de oportunidade
│   │   └─ Interpretação textual
│   │
│   ├── contexto_tempo_real.py
│   │   ├─ Thread separada
│   │   ├─ Análise contínua
│   │   └─ Ranking global
│   │
│   └── multi_pair_context.py
│       ├─ 12 pares simultâneos
│       ├─ Relatório comparativo
│       └─ Recomendações
│
├── 🎯 PRIORIZAÇÃO E ALERTAS
│   ├── priorizacao_automatica.py
│   │   ├─ Score ponderado
│   │   ├─ Pontos de entrada
│   │   └─ Recomendações
│   │
│   └── alertas_inteligentes.py
│       ├─ Alertas contextuais
│       ├─ Prioridades
│       └─ Ações recomendadas
│
├── 📱 INTEGRAÇÃO
│   └── xenos_bot.py
│       ├─ Telegram Bot
│       ├─ Mensagens formatadas
│       ├─ Relatórios
│       └─ Controle de spam
│
├── 🌐 WEB (Complementar)
│   ├── sne_radar_web.py (2000+ linhas)
│   │   ├─ Flask + SocketIO
│   │   ├─ Dashboard profissional
│   │   ├─ API REST
│   │   └─ Sistema de usuários
│   │
│   ├── services/
│   │   ├─ indicators.py
│   │   ├─ advanced_indicators.py
│   │   ├─ professional_indicators.py
│   │   ├─ ml_predictions.py
│   │   ├─ advanced_backtesting.py
│   │   ├─ alert_system.py
│   │   ├─ export_system.py
│   │   └─ ta_summary.py
│   │
│   └── integrations/
│       ├─ coinglass.py
│       └─ cmc.py
│
└── 📄 DADOS
    ├── catalogo_magnetico.csv
    ├── sne_memoria_neural.txt
    ├── sne_memoria_ciclica.txt
    ├── log_rupturas.txt
    └── codice_fluxo.txt
```

---

## 🔄 INTEGRAÇÃO ENTRE MÓDULOS

```
                    ┌─────────────┐
                    │   main.py   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ trading_      │  │  contexto_    │  │  backtest.py  │
│ signals.py    │  │  mercado.py   │  │               │
│               │  │               │  │  ┌─────────┐  │
│ • Sinais      │  │ • Regime      │  │  │ estado  │  │
│   Rápidos     │  │ • Score       │  │  │ (global)│  │
│               │  │ • Força       │  │  └─────────┘  │
└───────────────┘  └───────┬───────┘  └───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ mente_        │  │ fluxo_        │  │ catalogo_     │
│ fluida.py     │  │ mental.py     │  │ magnetico.py  │
│               │  │               │  │               │
│ • Ressonância │  │ • Congestão   │  │ • Zonas       │
│ • Memória     │  │ • Túneis      │  │ • Força       │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                  ┌───────────────┐
                  │  xenos_bot.py │
                  │               │
                  │ • Telegram    │
                  │ • Alertas     │
                  └───────────────┘
```

---

## 📊 FLUXO DE DECISÃO - SCORE DE OPORTUNIDADE

```
                    ┌─────────────┐
                    │  DataFrame  │
                    │  (100 velas)│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   MOMENTUM    │  │    VOLUME     │  │ VOLATILIDADE  │
│               │  │               │  │               │
│ Δ% em 5 velas │  │ Ratio vs Média│  │ Std Dev %     │
│               │  │               │  │               │
│ |Δ| > 0.5%?   │  │ Ratio > 1.3x? │  │ 0.3% < σ < 3%?│
│               │  │               │  │               │
│ ✅ 40 pontos  │  │ ✅ 30 pontos  │  │ ✅ 30 pontos  │
│ ❌ 0 pontos   │  │ ❌ 0 pontos   │  │ ❌ 0 pontos   │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                  ┌───────────────┐
                  │  SCORE TOTAL  │
                  │   (0-100)     │
                  └───────┬───────┘
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │  Score < 60  │    │  Score ≥ 60  │
        │              │    │              │
        │ ⏸️ AGUARDAR  │    │ ✅ CONTINUAR │
        │              │    │              │
        │ Retornar None│    │ Calcular     │
        │              │    │ Níveis       │
        └──────────────┘    └──────┬───────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
            ┌──────────────┐            ┌──────────────┐
            │ Momentum > 0 │            │ Momentum < 0 │
            │              │            │              │
            │ 🟢 COMPRAR   │            │ 🔴 VENDER    │
            │              │            │              │
            │ Entrada: Now │            │ Entrada: Now │
            │ Alvo: Resist │            │ Alvo: Suporte│
            │ Stop: -0.5%  │            │ Stop: +0.5%  │
            └──────┬───────┘            └──────┬───────┘
                   │                           │
                   └───────────┬───────────────┘
                               │
                               ▼
                      ┌───────────────┐
                      │ Calcular R/R  │
                      │               │
                      │ R/R = Retorno │
                      │       ─────── │
                      │        Risco  │
                      └───────┬───────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │  R/R < 1.5   │    │  R/R ≥ 1.5   │
            │              │    │              │
            │ ❌ Rejeitar  │    │ ✅ Aceitar   │
            │              │    │              │
            │ Retornar None│    │ Retornar     │
            │              │    │ Oportunidade │
            └──────────────┘    └──────────────┘
```

---

## 🎯 MENU INTERATIVO - FLUXO DE NAVEGAÇÃO

```
┌─────────────────────────────────────────────────────────┐
│           TERMINAL SNE RADAR - MENU PRINCIPAL           │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   RÁPIDO     │  │   COMPLETO   │  │  AVANÇADO    │
├──────────────┤  ├──────────────┤  ├──────────────┤
│              │  │              │  │              │
│ 0) ⚡ Melhor │  │ 1) 🎯 Radar  │  │ 7) 📊 Multi  │
│    Oportun.  │  │    Visual    │  │    Pair      │
│    (~30s)    │  │    (Tempo    │  │    (1-2min)  │
│              │  │    Real)     │  │              │
│ 00) 🏆 Top 3 │  │              │  │ 8) 🎯 Prior. │
│     Oportun. │  │ 2) 🔇 Modo   │  │    Auto      │
│     (~30s)   │  │    Silêncio  │  │              │
│              │  │              │  │ 9) 🚨 Alertas│
│              │  │ 3) ❌ Sair   │  │    Intel.    │
│              │  │              │  │              │
│              │  │ 4) 📜 Histór.│  │              │
│              │  │              │  │              │
│              │  │ 5) 🧠 Context│  │              │
│              │  │              │  │              │
│              │  │ 6) 🏆 Ranking│  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                  ┌───────────────┐
                  │  RESULTADO    │
                  │  • Ação       │
                  │  • Níveis     │
                  │  • Razões     │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  Telegram?    │
                  │  (opcional)   │
                  └───────────────┘
```

---

## 📈 PERFORMANCE E RECURSOS

```
┌─────────────────────────────────────────────────────────┐
│                  MÉTRICAS DE PERFORMANCE                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Operação              │ Tempo    │ Módulo              │
│  ──────────────────────┼──────────┼─────────────────── │
│  Sinal Rápido (1 par)  │ ~2-3s    │ trading_signals    │
│  Sinais Rápidos (12)   │ ~30s     │ trading_signals    │
│  Análise Multi-Pair    │ ~1-2min  │ multi_pair_context │
│  Atualização Radar     │ 5s       │ main.atualizar()   │
│  Backtest (100 velas)  │ ~1s      │ backtest           │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Recurso     │ Terminal  │ Web       │ Observação       │
│  ────────────┼───────────┼───────────┼───────────────  │
│  RAM         │ 200-300MB │ 500-800MB │ Análise contínua│
│  CPU         │ 10-20%    │ 15-30%    │ Multi-threading │
│  Disco       │ ~50MB     │ ~100MB    │ Logs + CSV + DB │
│  Rede        │ 1-2 MB/min│ 2-4 MB/min│ APIs Binance    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 CONCLUSÃO

O SNE Radar possui uma arquitetura **modular, escalável e robusta**, com:

✅ **Separação clara de responsabilidades**
✅ **Múltiplas interfaces** (terminal, web, Telegram)
✅ **Análise abrangente** (técnica + fundamental + ML)
✅ **Sistema de sinais focado** (rápido e prático)
✅ **Integração perfeita** entre módulos
✅ **Performance otimizada**

**Pronto para uso profissional em day-trading!** 🚀






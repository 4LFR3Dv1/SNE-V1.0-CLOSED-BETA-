# 📊 SNE RADAR - ANÁLISE COMPLETA DO SISTEMA

**Data:** 14/10/2025  
**Versão:** 3.0 Professional  
**Autor:** Sistema de Análise Técnica Avançada

---

## 📑 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Comandos Principais](#comandos-principais)
4. [Módulos Essenciais](#módulos-essenciais)
5. [Fluxo de Dados](#fluxo-de-dados)
6. [Integrações](#integrações)

---

## 🎯 VISÃO GERAL

### O que é o SNE RADAR?

**SNE RADAR** (Sistema Neural de Estratégia - Radar Avançado de Análise e Recomendações) é um sistema profissional de análise técnica para day trading em criptomoedas, especializado em:

- ✅ Análise técnica multi-timeframe
- ✅ Detecção de setups operacionais (Entry, SL, TP)
- ✅ Monitoramento 24/7 automatizado
- ✅ Alertas inteligentes em tempo real
- ✅ Visualização gráfica avançada
- ✅ Integração com Telegram

### Objetivo Principal

Fornecer análises técnicas precisas e acionáveis para traders, com foco em:
- **Setups claros** (Entry, Stop Loss, Take Profit)
- **Confluência técnica** (múltiplos indicadores)
- **Gestão de risco** (R:R mínimo 1:2)
- **Estratégias por timeframe** (SCALP, DAY, INTRA, SWING, POSITION)

---

## ��️ ARQUITETURA DO SISTEMA

### Estrutura de Arquivos

```
SNE_BACKUP_CLEAN/
│
├── main.py                          # Terminal principal (interface usuário)
├── motor_renan.py                   # Motor de análise (SNE Scanner)
├── xenos_bot.py                     # Integração Telegram
│
├── ANÁLISE TÉCNICA
│   ├── indicadores.py               # Cálculo de indicadores técnicos
│   ├── calcular_suportes_resistencias.py
│   ├── estrutura_mercado.py
│   └── padroes_graficos.py
│
├── CONTEXTO & REGIME
│   ├── contexto_mercado.py          # Análise macro
│   ├── contexto_macro_visual.py     # Visualização macro
│   ├── contexto_adaptativo.py       # Ajuste dinâmico
│   └── sentimento_global.py
│
├── AUTOMAÇÃO
│   ├── auto_analise.py              # Sistema 24/7
│   ├── dashboard_tempo_real.py      # Dashboard ondas
│   └── alertas_tecnicos.py          # Alertas S/R
│
├── VISUALIZAÇÃO
│   ├── grafico_candlestick.py       # Gráficos principais
│   ├── dashboard_graficos.py        # Gráficos dashboard
│   ├── dom_heatmap.py               # Heatmap liquidez
│   └── multi_pair_visual.py         # Multi-pair
│
├── RELATÓRIOS
│   ├── relatorio_tecnico.py         # Relatórios completos
│   ├── relatorios_periodicos.py     # Horário/Diário/Semanal
│   └── relatorios_multi_tf.py       # Multi-timeframe
│
├── GESTÃO & RISCO
│   ├── gestao_risco.py              # Gestão de risco
│   ├── memoria_operacional.py       # Histórico trades
│   └── consistencia_sinal.py        # Validação sinais
│
└── LIQUIDEZ & DOM
    ├── fluxo_ativo.py               # Análise order book
    ├── dom_profundo.py              # DOM profundo
    └── dom_consolidado.py           # DOM consolidado
```

### Camadas do Sistema

```
┌─────────────────────────────────────┐
│      INTERFACE (main.py)            │
│   Terminal interativo p/ usuário    │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   MOTOR DE ANÁLISE (motor_renan.py) │
│   • Coleta dados Binance API        │
│   • Calcula indicadores técnicos    │
│   • Gera setup operacional          │
│   • Determina confluência           │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   MÓDULOS ESPECIALIZADOS            │
│   • Contexto Macro                  │
│   • Estrutura Mercado               │
│   • Zonas Magnéticas                │
│   • Fluxo DOM                       │
│   • Multi-Timeframe                 │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   SAÍDA & COMUNICAÇÃO               │
│   • Terminal (exibição)             │
│   • Telegram (alertas)              │
│   • Gráficos (visualização)         │
└─────────────────────────────────────┘
```

---

## 🎮 COMANDOS PRINCIPAIS

### Menu Interativo

```
🚀 SNE RADAR - ANALISTA DE MERCADO PROFISSIONAL

🔍 ANÁLISE TÉCNICA:
R)     🔍 Scanner Técnico (Análise Completa)
CTX)   🌍 Contexto de Mercado Macro
MULT)  📊 Multi-Pair Análise Técnica
DOM)   🌊 Análise Profunda de Liquidez

📊 RELATÓRIOS:
RT)    📄 Relatório Técnico Completo
RH)    📈 Relatório Horário
RD)    📅 Relatório Diário
RS)    📅 Relatório Semanal

📈 VISUALIZAÇÃO:
1)     📈 Radar Visual (Gráfico)
DASH)  🎛️ Dashboard Técnico Tempo Real
HEAT)  🔥 Heatmap Correlações

🤖 AUTOMAÇÃO:
AUTO)  🔄 Análise Automática 24/7
ALERT) 🔔 Sistema de Alertas Técnicos

📱 TELEGRAM:
TG)    📱 Configurar Telegram
SEND)  📤 Enviar Relatório Manual

⚙️ SISTEMA:
CFG)   ⚙️ Configurações
INFO)  ℹ️ Informações do Sistema
3)     ❌ Sair
```

---

## 📋 DETALHAMENTO DOS COMANDOS

### 1. **R - SCANNER TÉCNICO**

**Função:** Análise técnica completa de um par em timeframe específico

**Fluxo de Execução:**

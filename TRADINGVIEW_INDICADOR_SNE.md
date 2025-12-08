# 📊 INDICADOR SNE RADAR PARA TRADINGVIEW

## 🎯 VISÃO GERAL

Este documento descreve como adaptar o motor de análise do SNE Radar para criar um indicador profissional no TradingView usando Pine Script v5.

---

## 🏗️ ARQUITETURA DO INDICADOR

### **Componentes Principais:**

```
┌─────────────────────────────────────────┐
│     SNE RADAR INDICATOR (Pine Script)   │
├─────────────────────────────────────────┤
│                                         │
│  1. MULTI-TIMEFRAME ANALYSIS            │
│     - request.security() para 5 TFs     │
│     - EMA8, EMA21, RSI, MACD por TF     │
│     - Score de confluência MTF           │
│                                         │
│  2. ANÁLISE DE ESTRUTURA                │
│     - Detecção de HH/HL, LH/LL          │
│     - Suportes e Resistências            │
│     - Price Action                      │
│                                         │
│  3. INDICADORES TÉCNICOS                │
│     - EMA8, EMA21, SMA200               │
│     - RSI (14), MACD                    │
│     - Bollinger Bands, ATR              │
│                                         │
│  4. CÁLCULO DE CONFLUÊNCIA              │
│     - Multi-TF: 3.0 pts                 │
│     - Fluxo DOM: 2.5 pts (simulado)     │
│     - Zonas Magnéticas: 2.0 pts          │
│     - Sentiment: 1.5 pts (simulado)    │
│     - Volume: 1.0 pts                   │
│     - Score Final: 0-10                  │
│                                         │
│  5. NÍVEIS OPERACIONAIS                 │
│     - Entry Price                       │
│     - Stop Loss (baseado em ATR)         │
│     - Take Profit 1, 2, 3               │
│     - Risk/Reward Ratio                  │
│                                         │
│  6. VISUALIZAÇÃO                        │
│     - Score visual (0-10)                │
│     - Sinais LONG/SHORT                  │
│     - Labels de níveis                  │
│     - Tabela de informações              │
│                                         │
└─────────────────────────────────────────┘
```

---

## 📝 IMPLEMENTAÇÃO PINE SCRIPT

### **Estrutura Base:**

```pinescript
//@version=5
indicator("SNE Radar - Sistema Neural Estratégico", shorttitle="SNE Radar", overlay=true, max_bars_back=500)

// ============================================
// CONFIGURAÇÕES
// ============================================
// Timeframes para análise
tf1 = input.timeframe("1", "Timeframe 1", group="Multi-Timeframe")
tf2 = input.timeframe("5", "Timeframe 2", group="Multi-Timeframe")
tf3 = input.timeframe("15", "Timeframe 3", group="Multi-Timeframe")
tf4 = input.timeframe("60", "Timeframe 4", group="Multi-Timeframe")
tf5 = input.timeframe("240", "Timeframe 5", group="Multi-Timeframe")

// Parâmetros de indicadores
ema_fast = input.int(8, "EMA Rápida", group="Indicadores")
ema_slow = input.int(21, "EMA Lenta", group="Indicadores")
sma_long = input.int(200, "SMA Longa", group="Indicadores")
rsi_period = input.int(14, "RSI Período", group="Indicadores")
atr_period = input.int(14, "ATR Período", group="Indicadores")

// Configurações de gestão de risco
sl_atr_mult = input.float(1.0, "Stop Loss (x ATR)", group="Gestão de Risco")
tp1_atr_mult = input.float(1.5, "Take Profit 1 (x ATR)", group="Gestão de Risco")
tp2_atr_mult = input.float(2.0, "Take Profit 2 (x ATR)", group="Gestão de Risco")
tp3_atr_mult = input.float(3.0, "Take Profit 3 (x ATR)", group="Gestão de Risco")

// Visualização
show_labels = input.bool(true, "Mostrar Labels", group="Visualização")
show_table = input.bool(true, "Mostrar Tabela", group="Visualização")
show_levels = input.bool(true, "Mostrar Níveis", group="Visualização")

// ============================================
// FUNÇÕES AUXILIARES
// ============================================

// Calcular RSI
rsi(src, length) =>
    up = ta.rma(math.max(ta.change(src), 0), length)
    down = ta.rma(-math.min(ta.change(src), 0), length)
    rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))
    rsi

// Calcular MACD
[macd_line, signal_line, hist] = ta.macd(close, 12, 26, 9)

// Calcular ATR
atr_value = ta.atr(atr_period)

// ============================================
// ANÁLISE MULTI-TIMEFRAME
// ============================================

// Função para analisar um timeframe
analisar_tf(tf) =>
    // Buscar dados do timeframe superior
    [close_tf, ema8_tf, ema21_tf, rsi_tf, macd_tf] = request.security(
        syminfo.tickerid, tf,
        [close, ta.ema(close, ema_fast), ta.ema(close, ema_slow), 
         rsi(close, rsi_period), ta.macd(close, 12, 26, 9)[0]],
        lookahead=barmerge.lookahead_off
    )
    
    // Determinar tendência
    tendencia = ema8_tf > ema21_tf ? 1 : ema8_tf < ema21_tf ? -1 : 0
    
    // Calcular força (gap entre EMAs)
    gap_pct = math.abs(ema8_tf - ema21_tf) / ema21_tf * 100
    forca = math.min(10, gap_pct * 20)
    
    // Score baseado em múltiplos fatores
    score = 0.0
    
    // Tendência (0-3 pontos)
    if tendencia == 1
        score += 3.0
    else if tendencia == -1
        score -= 3.0
    
    // RSI (0-2 pontos)
    if rsi_tf < 30
        score += 2.0  // Oversold = oportunidade LONG
    else if rsi_tf > 70
        score -= 2.0  // Overbought = oportunidade SHORT
    else if rsi_tf > 50
        score += 1.0
    else
        score -= 1.0
    
    // MACD (0-2 pontos)
    if macd_tf > 0
        score += 1.0
    else
        score -= 1.0
    
    // Força da tendência (0-2 pontos)
    score += (forca / 10) * 2
    
    // Normalizar para 0-10
    score_normalizado = (score + 5) / 10 * 10
    score_normalizado := math.max(0, math.min(10, score_normalizado))
    
    [score_normalizado, tendencia, forca, rsi_tf, ema8_tf, ema21_tf]

// Analisar todos os timeframes
[score_tf1, tend_tf1, forca_tf1, rsi_tf1, ema8_tf1, ema21_tf1] = analisar_tf(tf1)
[score_tf2, tend_tf2, forca_tf2, rsi_tf2, ema8_tf2, ema21_tf2] = analisar_tf(tf2)
[score_tf3, tend_tf3, forca_tf3, rsi_tf3, ema8_tf3, ema21_tf3] = analisar_tf(tf3)
[score_tf4, tend_tf4, forca_tf4, rsi_tf4, ema8_tf4, ema21_tf4] = analisar_tf(tf4)
[score_tf5, tend_tf5, forca_tf5, rsi_tf5, ema8_tf5, ema21_tf5] = analisar_tf(tf5)

// Calcular confluência multi-timeframe
scores_mtf = array.from(score_tf1, score_tf2, score_tf3, score_tf4, score_tf5)
tendencias_mtf = array.from(tend_tf1, tend_tf2, tend_tf3, tend_tf4, tend_tf5)

// Contar tendências alinhadas
altas = 0
baixas = 0
for i = 0 to array.size(tendencias_mtf) - 1
    if array.get(tendencias_mtf, i) == 1
        altas += 1
    else if array.get(tendencias_mtf, i) == -1
        baixas += 1

total_tfs = 5
confluencia_mtf = altas > baixas ? (altas / total_tfs) * 10 : baixas > altas ? (baixas / total_tfs) * 10 : 5.0

// Score médio dos timeframes
score_medio_mtf = (score_tf1 + score_tf2 + score_tf3 + score_tf4 + score_tf5) / 5

// ============================================
// ANÁLISE DE ESTRUTURA (TIMEFRAME ATUAL)
// ============================================

// Calcular EMAs no timeframe atual
ema8 = ta.ema(close, ema_fast)
ema21 = ta.ema(close, ema_slow)
sma200 = ta.sma(close, sma_long)

// RSI atual
rsi_atual = rsi(close, rsi_period)

// Detectar estrutura (simplificado)
// Em Pine Script completo, usar ta.pivothigh() e ta.pivotlow()
tendencia_atual = ema8 > ema21 ? 1 : ema8 < ema21 ? -1 : 0

// Score de estrutura
score_estrutura = 0.0
if ema8 > ema21 > sma200
    score_estrutura = 8.0  // Estrutura bullish forte
else if ema8 < ema21 < sma200
    score_estrutura = 2.0  // Estrutura bearish forte
else if ema8 > ema21
    score_estrutura = 6.0  // Estrutura bullish moderada
else if ema8 < ema21
    score_estrutura = 4.0  // Estrutura bearish moderada
else
    score_estrutura = 5.0  // Lateral

// ============================================
// ANÁLISE DE VOLUME
// ============================================

// Volume relativo
volume_medio = ta.sma(volume, 20)
volume_ratio = volume / volume_medio
score_volume = volume_ratio > 1.5 ? 8.0 : volume_ratio > 1.2 ? 6.0 : volume_ratio > 0.8 ? 5.0 : 3.0

// ============================================
// CÁLCULO DE CONFLUÊNCIA FINAL
// ============================================

// Pesos (conforme motor SNE)
peso_mtf = 3.0
peso_fluxo_dom = 2.5  // Simulado - não temos DOM real no TradingView
peso_zonas = 2.0      // Simulado - zonas magnéticas
peso_sentiment = 1.5  // Simulado - sentiment
peso_volume = 1.0

// Componentes
componente_mtf = (confluencia_mtf / 10) * peso_mtf
componente_estrutura = (score_estrutura / 10) * peso_mtf  // Usar estrutura como proxy
componente_volume = (score_volume / 10) * peso_volume

// Fluxo DOM simulado (baseado em RSI e MACD)
fluxo_dom_score = 0.0
if rsi_atual < 30 and macd_line > signal_line
    fluxo_dom_score = 8.0  // Pressão de compra
else if rsi_atual > 70 and macd_line < signal_line
    fluxo_dom_score = 2.0  // Pressão de venda
else
    fluxo_dom_score = 5.0
componente_fluxo = (fluxo_dom_score / 10) * peso_fluxo_dom

// Zonas magnéticas simulado (baseado em suportes/resistências)
// Em versão completa, calcular zonas baseadas em volume profile
zonas_score = 5.0  // Neutro por padrão
componente_zonas = (zonas_score / 10) * peso_zonas

// Sentiment simulado (baseado em RSI e estrutura)
sentiment_score = 5.0
if rsi_atual < 40 and tendencia_atual == 1
    sentiment_score = 7.0  // Sentiment positivo
else if rsi_atual > 60 and tendencia_atual == -1
    sentiment_score = 3.0  // Sentiment negativo
componente_sentiment = (sentiment_score / 10) * peso_sentiment

// Score final de confluência
total_peso = peso_mtf + peso_fluxo_dom + peso_zonas + peso_sentiment + peso_volume
score_confluencia = (componente_mtf + componente_fluxo + componente_zonas + componente_sentiment + componente_volume) / total_peso * 10
score_confluencia := math.max(0, math.min(10, score_confluencia))

// ============================================
// DETERMINAÇÃO DE SINAL
// ============================================

// Viés principal
vies = score_confluencia >= 7 ? 1 : score_confluencia <= 3 ? -1 : 0

// Sinais de alta
sinais_alta = 0
if tendencia_atual == 1
    sinais_alta += 1
if rsi_atual < 45
    sinais_alta += 1
if ema8 > ema21
    sinais_alta += 1
if macd_line > signal_line
    sinais_alta += 1
if score_confluencia >= 6
    sinais_alta += 1

// Sinais de baixa
sinais_baixa = 0
if tendencia_atual == -1
    sinais_baixa += 1
if rsi_atual > 55
    sinais_baixa += 1
if ema8 < ema21
    sinais_baixa += 1
if macd_line < signal_line
    sinais_baixa += 1
if score_confluencia <= 4
    sinais_baixa += 1

// Sinal final
sinal = sinais_alta > sinais_baixa ? 1 : sinais_baixa > sinais_alta ? -1 : 0

// ============================================
// NÍVEIS OPERACIONAIS
// ============================================

// Preço atual
preco_atual = close

// Calcular níveis baseados em ATR
atr_mult_sl = sl_atr_mult
atr_mult_tp1 = tp1_atr_mult
atr_mult_tp2 = tp2_atr_mult
atr_mult_tp3 = tp3_atr_mult

// Entry (preço atual)
entry_price = preco_atual

// Stop Loss e Take Profits
var float stop_loss = na
var float tp1 = na
var float tp2 = na
var float tp3 = na

if sinal == 1  // LONG
    stop_loss := entry_price - (atr_value * atr_mult_sl)
    tp1 := entry_price + (atr_value * atr_mult_tp1)
    tp2 := entry_price + (atr_value * atr_mult_tp2)
    tp3 := entry_price + (atr_value * atr_mult_tp3)
else if sinal == -1  // SHORT
    stop_loss := entry_price + (atr_value * atr_mult_sl)
    tp1 := entry_price - (atr_value * atr_mult_tp1)
    tp2 := entry_price - (atr_value * atr_mult_tp2)
    tp3 := entry_price - (atr_value * atr_mult_tp3)
else
    stop_loss := na
    tp1 := na
    tp2 := na
    tp3 := na

// Risk/Reward Ratio
rr_ratio = sinal != 0 ? math.abs(tp1 - entry_price) / math.abs(stop_loss - entry_price) : na

// ============================================
// VISUALIZAÇÃO
// ============================================

// Cores baseadas no score
cor_score = score_confluencia >= 7 ? color.new(color.green, 0) : 
            score_confluencia >= 5 ? color.new(color.yellow, 0) : 
            score_confluencia >= 3 ? color.new(color.orange, 0) : 
            color.new(color.red, 0)

// Plot do score (como linha)
plot(score_confluencia, "SNE Score", color=cor_score, linewidth=2)

// Plot das EMAs
plot(ema8, "EMA 8", color=color.blue, linewidth=1)
plot(ema21, "EMA 21", color=color.orange, linewidth=1)
plot(sma200, "SMA 200", color=color.red, linewidth=2)

// Plot dos níveis operacionais
plot(show_levels ? stop_loss : na, "Stop Loss", color=color.red, linewidth=2, style=plot.style_linebr)
plot(show_levels ? tp1 : na, "TP1", color=color.green, linewidth=1, style=plot.style_linebr)
plot(show_levels ? tp2 : na, "TP2", color=color.green, linewidth=1, style=plot.style_linebr)
plot(show_levels ? tp3 : na, "TP3", color=color.green, linewidth=1, style=plot.style_linebr)

// Labels de sinais
if show_labels and sinal != 0 and barstate.isconfirmed
    label_text = sinal == 1 ? "🟢 LONG\nScore: " + str.tostring(score_confluencia, "#.#") + "/10" : 
                  "🔴 SHORT\nScore: " + str.tostring(score_confluencia, "#.#") + "/10"
    label_color = sinal == 1 ? color.new(color.green, 20) : color.new(color.red, 20)
    label.new(bar_index, high, label_text, color=label_color, textcolor=color.white, 
              style=label.style_label_down, size=size.normal)

// Tabela de informações
if show_table and barstate.islast
    var table info_table = table.new(position.top_right, 2, 10, bgcolor=color.new(color.black, 80), 
                                     border_width=1, border_color=color.gray)
    
    table.cell(info_table, 0, 0, "SNE RADAR", text_color=color.white, bgcolor=color.new(color.blue, 70), text_size=size.normal)
    table.cell(info_table, 1, 0, "Valor", text_color=color.white, bgcolor=color.new(color.blue, 70), text_size=size.normal)
    
    table.cell(info_table, 0, 1, "Score Confluência", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 1, str.tostring(score_confluencia, "#.#") + "/10", 
               text_color=cor_score, text_size=size.small)
    
    table.cell(info_table, 0, 2, "Sinal", text_color=color.white, text_size=size.small)
    sinal_text = sinal == 1 ? "🟢 LONG" : sinal == -1 ? "🔴 SHORT" : "⚪ NEUTRO"
    table.cell(info_table, 1, 2, sinal_text, text_color=color.white, text_size=size.small)
    
    table.cell(info_table, 0, 3, "Confluência MTF", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 3, str.tostring(confluencia_mtf, "#.#") + "/10", text_color=color.white, text_size=size.small)
    
    table.cell(info_table, 0, 4, "RSI", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 4, str.tostring(rsi_atual, "#.#"), text_color=color.white, text_size=size.small)
    
    table.cell(info_table, 0, 5, "Entry", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 5, str.tostring(entry_price, "#.##"), text_color=color.white, text_size=size.small)
    
    table.cell(info_table, 0, 6, "Stop Loss", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 6, str.tostring(stop_loss, "#.##"), text_color=color.red, text_size=size.small)
    
    table.cell(info_table, 0, 7, "TP1", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 7, str.tostring(tp1, "#.##"), text_color=color.green, text_size=size.small)
    
    table.cell(info_table, 0, 8, "R/R Ratio", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 8, str.tostring(rr_ratio, "#.##"), text_color=color.white, text_size=size.small)
    
    table.cell(info_table, 0, 9, "ATR", text_color=color.white, text_size=size.small)
    table.cell(info_table, 1, 9, str.tostring(atr_value, "#.##"), text_color=color.white, text_size=size.small)

// Alertas
alertcondition(sinal == 1 and sinal[1] != 1, "SNE LONG Signal", "SNE Radar: Sinal de COMPRA detectado!")
alertcondition(sinal == -1 and sinal[1] != -1, "SNE SHORT Signal", "SNE Radar: Sinal de VENDA detectado!")
alertcondition(score_confluencia >= 8, "SNE High Score", "SNE Radar: Score de confluência alto (≥8)!")

```

---

## 🔄 ADAPTAÇÕES NECESSÁRIAS

### **1. Componentes que Funcionam Diretamente:**

✅ **Multi-Timeframe Analysis**
- Usar `request.security()` para buscar dados de timeframes superiores
- Calcular indicadores em cada TF
- Calcular confluência entre TFs

✅ **Indicadores Técnicos**
- EMA, SMA, RSI, MACD nativos do Pine Script
- Bollinger Bands, ATR disponíveis
- Cálculos idênticos ao Python

✅ **Análise de Estrutura**
- Detecção de HH/HL usando `ta.pivothigh()` e `ta.pivotlow()`
- Alinhamento de EMAs
- Classificação de tendência

✅ **Cálculo de Confluência**
- Sistema de pesos idêntico
- Score final 0-10
- Interpretação qualitativa

✅ **Níveis Operacionais**
- Cálculo baseado em ATR
- Entry, SL, TP1, TP2, TP3
- Risk/Reward Ratio

---

### **2. Componentes que Precisam de Adaptação:**

⚠️ **Fluxo DOM (Order Book)**
- **Problema:** TradingView não tem acesso direto ao Order Book
- **Solução:** Simular usando:
  - RSI (pressão de compra/venda)
  - MACD (momentum)
  - Volume relativo
  - Spread bid/ask (se disponível)

⚠️ **Zonas Magnéticas**
- **Problema:** Sistema proprietário baseado em histórico
- **Solução:** Implementar versão simplificada:
  - Volume Profile (POC, VAL, VAH)
  - Suportes/Resistências baseados em pivots
  - Níveis de Fibonacci
  - Zonas de alta liquidez histórica

⚠️ **Sentiment Global**
- **Problema:** Depende de APIs externas (Fear & Greed, Funding Rate)
- **Solução:** Simular usando:
  - RSI e estrutura de mercado
  - Divergências
  - Padrões de candlestick
  - Volume analysis

---

### **3. Componentes que Não Podem Ser Implementados:**

❌ **Análise de Order Book em Tempo Real**
- TradingView não fornece acesso ao Order Book
- Usar proxies (RSI, Volume, MACD)

❌ **APIs Externas Diretas**
- Fear & Greed Index
- Funding Rate da Binance
- Dados on-chain
- **Solução:** Usar dados disponíveis no TradingView ou simular

❌ **Sistema de Memória Neural**
- Pine Script não mantém estado entre execuções
- **Solução:** Usar apenas dados históricos disponíveis

---

## 📊 FUNCIONALIDADES DO INDICADOR

### **1. Visualizações:**

- **Score de Confluência (0-10)**
  - Linha colorida no gráfico
  - Verde: ≥7 (Alta confluência)
  - Amarelo: 5-7 (Média confluência)
  - Laranja: 3-5 (Baixa confluência)
  - Vermelho: <3 (Muito baixa)

- **Sinais LONG/SHORT**
  - Labels no gráfico
  - Cores: Verde (LONG), Vermelho (SHORT)
  - Apenas em barras confirmadas

- **Níveis Operacionais**
  - Linhas horizontais
  - Entry (preço atual)
  - Stop Loss (vermelho)
  - Take Profit 1, 2, 3 (verde)

- **Tabela de Informações**
  - Canto superior direito
  - Score, Sinal, RSI, Níveis, R/R Ratio

- **EMAs e SMAs**
  - EMA 8 (azul)
  - EMA 21 (laranja)
  - SMA 200 (vermelho)

---

### **2. Alertas:**

- **Sinal LONG:** Quando sinal muda para LONG
- **Sinal SHORT:** Quando sinal muda para SHORT
- **Score Alto:** Quando score ≥ 8
- **Score Baixo:** Quando score ≤ 2

---

### **3. Configurações:**

- **Timeframes:** 5 timeframes configuráveis
- **Indicadores:** Períodos de EMA, RSI, ATR
- **Gestão de Risco:** Multiplicadores de ATR para SL/TP
- **Visualização:** Mostrar/ocultar labels, tabela, níveis

---

## 🚀 COMO USAR

### **1. Instalação:**
1. Abrir TradingView
2. Ir em Pine Editor
3. Colar o código completo
4. Clicar em "Add to Chart"

### **2. Configuração:**
1. Ajustar timeframes (padrão: 1m, 5m, 15m, 1h, 4h)
2. Ajustar períodos de indicadores
3. Configurar multiplicadores de ATR
4. Ativar/desativar visualizações

### **3. Uso:**
- **Score ≥ 7:** Alta confluência - considerar entrada
- **Score 5-7:** Confluência média - aguardar confirmação
- **Score < 5:** Baixa confluência - evitar entrada
- **Sinal LONG/SHORT:** Seguir níveis operacionais

---

## 📈 MELHORIAS FUTURAS

### **Versão 2.0:**
1. **Volume Profile Real**
   - Cálculo de POC, VAL, VAH
   - Zonas de alta liquidez

2. **Padrões Gráficos**
   - Detecção de wedges, triângulos
   - Padrões de candlestick

3. **Divergências**
   - RSI/MACD divergences
   - Alertas automáticos

4. **Backtesting Integrado**
   - Testar estratégia no histórico
   - Métricas de performance

5. **Multi-Pair Analysis**
   - Comparar múltiplos ativos
   - Ranking de oportunidades

---

## ⚠️ LIMITAÇÕES

1. **Order Book:** Não disponível no TradingView
2. **APIs Externas:** Limitado a dados do TradingView
3. **Memória:** Não mantém estado entre execuções
4. **Performance:** Pode ser lento com muitos timeframes
5. **Zonas Magnéticas:** Versão simplificada

---

## ✅ VANTAGENS

1. **Integração Nativa:** Funciona diretamente no TradingView
2. **Visualização Profissional:** Gráficos e tabelas
3. **Alertas Automáticos:** Notificações em tempo real
4. **Multi-Timeframe:** Análise completa
5. **Níveis Operacionais:** Entry, SL, TP calculados automaticamente

---

## 📝 CONCLUSÃO

O indicador SNE Radar para TradingView adapta os principais componentes do motor de análise Python para Pine Script, mantendo a essência do sistema de confluência multi-camada. Embora alguns componentes precisem ser simulados (DOM, Zonas Magnéticas, Sentiment), o indicador oferece uma análise profissional e acionável diretamente no TradingView.

**Status:** ✅ Implementável  
**Complexidade:** Média  
**Tempo de Desenvolvimento:** 2-3 dias para versão completa

---

**Desenvolvido para:** TradingView Pine Script v5  
**Baseado em:** SNE Radar Motor de Análise (Python)  
**Versão:** 1.0







# 🚀 BACKTEST SNE RADAR - SISTEMA DE VALIDAÇÃO

## 📋 VISÃO GERAL

O sistema de backtest do SNE Radar permite validar a eficácia das análises técnicas e estratégias usando dados históricos reais. Ele simula operações baseadas nos sinais gerados pelo sistema SNE e calcula métricas de performance.

## 🎯 FUNCIONALIDADES

### **1. 📊 Coleta de Dados Históricos**
- **API Binance**: Coleta dados OHLCV reais
- **Múltiplos Timeframes**: 1m, 5m, 15m, 30m, 1h, 4h, 1d
- **Cache Local**: Salva dados para reutilização
- **Períodos Flexíveis**: Qualquer período histórico

### **2. 🔧 Engine de Backtest**
- **Análise SNE Completa**: RSI, MACD, Bollinger Bands, ATR
- **Sistema de Sinais**: Baseado em confluência e confiança
- **Gestão de Risco**: Stop Loss e Take Profit automáticos
- **Comissões**: Inclui custos de transação

### **3. 📈 Métricas de Performance**
- **Retorno Total**: Ganho/perda percentual
- **Win Rate**: Percentual de trades lucrativos
- **Sharpe Ratio**: Retorno ajustado ao risco
- **Max Drawdown**: Maior perda consecutiva
- **Profit Factor**: Razão lucros/prejuízos

### **4. 📊 Visualizações**
- **Curva de Equity**: Evolução do capital
- **Distribuição de Retornos**: Histograma dos resultados
- **Timeline de Trades**: Sequência de operações
- **Métricas Radar**: Performance em gráfico polar
- **Painel Completo**: Todos os gráficos em um

## 🚀 COMO USAR

### **Execução Rápida:**
```bash
python3 backtest_main.py
```

### **Execução Direta:**
```bash
python3 backtest_sne.py
```

### **Visualização:**
```bash
python3 visualizacao_backtest.py
```

## 📋 EXEMPLOS DE USO

### **1. Backtest Rápido (BTC 6 meses)**
```python
from backtest_sne import executar_backtest_completo

metricas = executar_backtest_completo(
    symbol='BTCUSDT',
    interval='1h',
    start_date='2024-01-01',
    end_date='2024-06-30'
)
```

### **2. Coleta de Dados**
```python
from backtest_sne import ColetorDadosHistoricos

coletor = ColetorDadosHistoricos()
df = coletor.coletar_dados('BTCUSDT', '1h', '2024-01-01', '2024-12-31')
coletor.salvar_dados(df, 'BTCUSDT', '1h')
```

### **3. Visualização de Resultados**
```python
from visualizacao_backtest import visualizar_backtest_completo

visualizar_backtest_completo('backtest_results_BTCUSDT_1h_2024-01-01.json')
```

## ⚙️ CONFIGURAÇÕES

### **Parâmetros de Trading:**
```python
# No arquivo backtest_sne.py
self.capital_inicial = 10000      # Capital inicial
self.stop_loss_pct = 0.02         # Stop Loss 2%
self.take_profit_pct = 0.04       # Take Profit 4%
self.comissao_pct = 0.001         # Comissão 0.1%
```

### **Thresholds de Confiança:**
```python
# Só entra com confiança >= 70%
if confianca >= 70:
    if acao == 'LONG' and score >= 7:
        self._abrir_posicao('LONG', preco_atual, index, confianca)
```

## 📊 MÉTRICAS CALCULADAS

### **Performance Financeira:**
- **Retorno Total**: `((capital_final / capital_inicial) - 1) * 100`
- **Retorno Médio**: Média dos retornos por trade
- **Volatilidade**: Desvio padrão dos retornos

### **Métricas de Trading:**
- **Win Rate**: `(trades_lucrativos / total_trades) * 100`
- **Profit Factor**: `lucros_totais / prejuizos_totais`
- **Sharpe Ratio**: `retorno_medio / volatilidade`

### **Métricas de Risco:**
- **Max Drawdown**: Maior queda do pico ao vale
- **Drawdown Médio**: Drawdown médio dos períodos negativos
- **VaR (95%)**: Valor em risco com 95% de confiança

## 📈 INTERPRETAÇÃO DOS RESULTADOS

### **✅ Estratégia Lucrativa:**
- Retorno Total > 0%
- Win Rate > 50%
- Sharpe Ratio > 1.0
- Max Drawdown < -20%

### **⚠️ Estratégia Questionável:**
- Retorno Total próximo de 0%
- Win Rate entre 40-50%
- Sharpe Ratio entre 0.5-1.0
- Max Drawdown entre -20% e -30%

### **❌ Estratégia Problemática:**
- Retorno Total < 0%
- Win Rate < 40%
- Sharpe Ratio < 0.5
- Max Drawdown > -30%

## 🔧 PERSONALIZAÇÃO

### **Modificar Indicadores:**
```python
def _calcular_indicadores(self, df: pd.DataFrame) -> Dict:
    # Adicionar novos indicadores
    # Modificar períodos
    # Ajustar fórmulas
```

### **Alterar Lógica de Sinais:**
```python
def _processar_sinal(self, analise: Dict, candle_atual: pd.Series, index: int):
    # Modificar condições de entrada
    # Ajustar thresholds
    # Adicionar filtros
```

### **Customizar Gestão de Risco:**
```python
def _abrir_posicao(self, direcao: str, preco: float, index: int, confianca: float):
    # Modificar stop loss/take profit
    # Implementar trailing stop
    # Adicionar position sizing
```

## 📁 ESTRUTURA DE ARQUIVOS

```
backtest_data/
├── BTCUSDT_1h_historico.csv
├── ETHUSDT_1h_historico.csv
└── SOLUSDT_1h_historico.csv

backtest_results/
├── backtest_results_BTCUSDT_1h_2024-01-01.json
├── backtest_results_ETHUSDT_1h_2024-01-01.json
└── backtest_results_SOLUSDT_1h_2024-01-01.json

Gráficos Gerados:
├── backtest_equity_curve_BTCUSDT.png
├── backtest_distribuicao_BTCUSDT.png
├── backtest_metricas_BTCUSDT.png
├── backtest_timeline_BTCUSDT.png
└── backtest_painel_completo_BTCUSDT.png
```

## 🎯 CASOS DE USO

### **1. Validação de Estratégia**
- Testar nova configuração de indicadores
- Validar thresholds de confiança
- Comparar diferentes timeframes

### **2. Otimização de Parâmetros**
- Encontrar melhores stop loss/take profit
- Otimizar períodos de indicadores
- Ajustar filtros de volume

### **3. Análise de Robustez**
- Testar em diferentes períodos
- Validar em múltiplos pares
- Analisar performance em diferentes regimes

### **4. Comparação de Estratégias**
- Comparar SNE vs estratégias simples
- Avaliar diferentes configurações
- Identificar melhores setups

## ⚠️ LIMITAÇÕES E CONSIDERAÇÕES

### **Limitações:**
- **Slippage**: Não considera deslizamento de preço
- **Liquidez**: Assume execução perfeita
- **Emoções**: Não considera fatores psicológicos
- **Overfitting**: Risco de otimização excessiva

### **Melhorias Futuras:**
- **Walk-Forward Analysis**: Validação em janelas deslizantes
- **Monte Carlo**: Simulação estatística
- **Multi-Asset**: Backtest em portfólio
- **Regime Detection**: Adaptação a diferentes mercados

## 📚 DEPENDÊNCIAS

```bash
pip install requests pandas numpy matplotlib
```

## 🚀 PRÓXIMOS PASSOS

1. **Implementar Walk-Forward Analysis**
2. **Adicionar Monte Carlo Simulation**
3. **Criar Dashboard Web**
4. **Integrar com Sistema Principal**
5. **Adicionar Alertas Automáticos**

---

**Status:** ✅ **SISTEMA COMPLETO E FUNCIONAL**
**Versão:** 1.0
**Data:** 14/10/2025
**Arquivos:** 
- `backtest_sne.py` (Engine principal)
- `visualizacao_backtest.py` (Gráficos e análises)
- `backtest_main.py` (Interface principal)


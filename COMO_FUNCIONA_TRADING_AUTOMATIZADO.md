# 🏦 COMO FUNCIONA A ABA DE TRADING AUTOMATIZADO

**Data:** 02 de Janeiro de 2025  
**Versão:** Sistema de Pools de Alocação (Hedge Fund Style)

---

## 🎯 VISÃO GERAL

A aba de **Trading Automatizado** implementa o sistema de **Pools de Alocação** conforme descrito no `PLANO_POOLS_ALOCACAO.md`. É um cockpit completo para gerenciar trading automatizado com arquitetura estilo hedge fund.

---

## 🏗️ ARQUITETURA

### **Conceito Principal:**

```
Motor SNE Autônomo
    ↓
Analisa mercado (UMA VEZ por par)
    ↓
Gera sinais
    ↓
Distribui para Pools interessados
    ↓
Cada Pool executa proporcionalmente ao seu capital
```

### **Componentes:**

1. **Motor SNE Autônomo** - Analisa mercado continuamente
2. **Pools de Alocação** - Gestão de capital por perfil
3. **Configuração Global** - Filtros de segurança
4. **Terminal de Log** - Monitoramento em tempo real
5. **Painel Financeiro** - Portfólio, P&L, exposição

---

## 📊 INTERFACE (Layout Cockpit)

### **Layout em 3 Colunas:**

```
┌─────────────────────────────────────────────────────────┐
│  🏦 TRADING AUTOMATIZADO - Cockpit de Execução          │
│  Status: 🟢 ON | Total P&L: +$1,234.56                 │
├──────────────┬──────────────────────┬───────────────────┤
│ COLUNA 1     │ COLUNA 2             │ COLUNA 3          │
│ Motor & Pools│ Terminal & Execução  │ Financeiro        │
├──────────────┼──────────────────────┼───────────────────┤
│              │                      │                   │
│ 🤖 Motor SNE │ 📺 Terminal de Log   │ 💰 Portfólio      │
│ ⚙️ Config    │ 📋 Ordens Pendentes  │ 📊 Performance    │
│ 💰 Pools     │ 📈 Posições Abertas  │ ⚠️ Risco          │
│ 🎮 Controles │                      │                   │
│              │                      │                   │
└──────────────┴──────────────────────┴───────────────────┘
```

---

## 🤖 COLUNA 1: MOTOR E POOLS

### **1.1. Motor SNE Autônomo**

**Componente:** `AutoPilotStatus.vue`

**Funcionalidades:**
- ✅ Toggle ON/OFF do motor
- ✅ Status em tempo real (🟢 Rodando / 🔴 Parado)
- ✅ Informações:
  - Pares monitorados
  - Timeframe padrão
  - Confluência mínima global

**Como Funciona:**
```javascript
// Frontend
toggleMotor() → tradingStore.startAutopilot() / stopAutopilot()

// Backend
POST /api/trading/autopilot/start
POST /api/trading/autopilot/stop
```

**Backend (`AutoPilotEngine`):**
- Loop contínuo que analisa mercado
- Usa `motor_renan.py` para análise
- Distribui sinais para pools interessados

---

### **1.2. Configuração Global**

**Componente:** `GlobalConfigPanel.vue`

**Configurações:**
- **Confluência Mínima Global:** % mínimo para executar trade
- **Risco Máximo por Trade:** % do capital por operação
- **Pares Monitorados:** Lista de símbolos (BTCUSDT, ETHUSDT, etc.)
- **Timeframe Padrão:** 1m, 5m, 15m, 1h, 4h, 1d
- **Horário de Operação:** 24/7 ou customizado

**Armazenado em:**
- Modelo: `TradingGlobalConfig`
- Tabela: `trading_global_config`
- Um registro por usuário

---

### **1.3. Pools de Alocação**

**Componente:** `PoolCard.vue`

**O que é um Pool:**
Um pool é um "fundo" de capital com configurações específicas:

```javascript
{
  name: "Scalper BTC",
  capital_allocated: 5000,      // Capital total
  capital_used: 2000,           // Em posições
  capital_available: 3000,      // Disponível
  symbols: ["BTCUSDT"],         // Pares de interesse
  risk_per_trade_pct: 1.5,      // Risco por trade
  max_positions: 5,             // Máximo de posições
  min_confluencia: 80,          // Confluência mínima (override)
  status: "active"              // active, paused, stopped
}
```

**Funcionalidades:**
- ✅ Criar novo pool (botão "+ Novo Pool")
- ✅ Ativar/Desativar pool
- ✅ Editar pool
- ✅ Deletar pool
- ✅ Visualizar capital (alocado, usado, disponível)

**Como Funciona:**
```javascript
// Criar Pool
handleCreatePool() → tradingStore.createPool(data)
  → POST /api/trading/pools
  → Cria registro em CapitalPool

// Ativar Pool
handleStartPool(id) → tradingStore.startPool(id)
  → POST /api/trading/pools/{id}/start
  → Atualiza status para 'active'
```

---

### **1.4. Controles de Execução**

**Componente:** `ExecutionControl.vue`

**Botões:**
- **▶ Iniciar Tudo** - Ativa todos os pools
- **⏸ Pausar Tudo** - Pausa todos os pools
- **⏹ Parar Tudo** - Para todos os pools
- **🚨 PANIC CLOSE** - Fecha todas as posições imediatamente

---

## 📺 COLUNA 2: TERMINAL E EXECUÇÃO

### **2.1. Terminal de Log**

**Componente:** `TerminalLog.vue`

**Funcionalidades:**
- ✅ Logs em tempo real
- ✅ Tipos: INFO, SUCCESS, WARNING, ERROR
- ✅ Timestamp de cada log
- ✅ Botão "Limpar" logs
- ✅ Scroll automático

**Exemplos de Logs:**
```
[10:30:15] INFO: 🚀 Trading Automatizado iniciado
[10:30:16] SUCCESS: ✅ Dados carregados com sucesso
[10:30:20] INFO: Pool "Scalper BTC" ativado
[10:30:25] WARNING: Risco alto detectado em BTCUSDT
[10:30:30] ERROR: Erro ao executar ordem: Connection timeout
```

**Como Funciona:**
```javascript
// Adicionar log
tradingStore.addTerminalLog('INFO', 'Mensagem')

// Limpar logs
tradingStore.clearTerminalLogs()
```

---

### **2.2. Ordens Pendentes**

**Exibe:**
- Símbolo
- Lado (BUY/SELL)
- Quantidade
- Status (pending, filled, cancelled)

**Atualização:** A cada 10 segundos

---

### **2.3. Monitor de Posições**

**Componente:** `PositionMonitor.vue`

**Exibe posições abertas:**
- Símbolo
- Lado (LONG/SHORT)
- Entry Price
- Current Price
- P&L (realizado e não realizado)
- Leverage
- Botão "Fechar Posição"

---

## 💰 COLUNA 3: FINANCEIRO

### **3.1. Visão Geral do Portfólio**

**Componente:** `PortfolioOverview.vue`

**Métricas:**
- **Capital Total:** Capital alocado em todos os pools
- **Capital Usado:** Capital em posições abertas
- **Capital Disponível:** Capital livre para novos trades
- **P&L Total:** Lucro/Prejuízo total
- **ROI:** Return on Investment (%)

---

### **3.2. Medidor de Exposição**

**Componente:** `ExposureMeter.vue`

**Mostra:**
- Exposição atual (% do capital)
- Limite de exposição
- Gráfico visual de exposição

---

### **3.3. Gráfico de Performance**

**Componente:** `PerformanceChart.vue`

**Exibe:**
- Equity curve (curva de patrimônio)
- P&L ao longo do tempo
- Seleção de período (1d, 7d, 30d, 90d, 1y)

---

### **3.4. Dashboard de Risco**

**Componente:** `RiskDashboard.vue`

**Alertas de Risco:**
- ⚠️ Exposição alta
- ⚠️ Drawdown excessivo
- ⚠️ Múltiplas posições no mesmo par
- ⚠️ Risco por trade acima do limite

---

## 🔄 FLUXO DE EXECUÇÃO

### **1. Inicialização**

```javascript
// AutomatedTrading.vue - onMounted
tradingStore.initialize()
  → fetchPools()
  → fetchAutopilotStatus()
  → fetchAutopilotConfig()
  → fetchStrategies()
  → fetchPositions()
  → fetchOrders()
  → fetchPortfolio()
  → fetchRiskAlerts()
```

### **2. Motor Autônomo em Ação**

```python
# AutoPilotEngine._main_loop()
while running:
    # 1. Buscar configuração global
    config = TradingGlobalConfig.query.filter_by(user_id=user_id).first()
    
    # 2. Para cada par monitorado
    for symbol in config.monitored_symbols:
        # 3. Analisar com motor_renan
        analysis = motor_renan.analise_completa(symbol, timeframe)
        
        # 4. Extrair sinal
        signal = extract_signal(analysis)
        
        # 5. Se sinal válido, buscar pools interessados
        if signal['action'] != 'HOLD':
            pools = get_interested_pools(user_id, symbol)
            
            # 6. Para cada pool, executar trade
            for pool in pools:
                if validate_pool_trade(pool, signal):
                    execute_pool_trade(pool, signal)
    
    # Aguardar antes da próxima análise
    time.sleep(60)  # 1 minuto
```

### **3. Execução de Trade**

```python
# AutoPilotEngine._execute_pool_trade()
def _execute_pool_trade(pool, signal):
    # 1. Calcular quantidade baseado no capital do pool
    quantity = calculate_quantity(pool, signal)
    
    # 2. Validar risco
    if not risk_manager.validate_trade(pool, quantity):
        return False
    
    # 3. Criar ordem
    order = OrderManager.create_order({
        'symbol': signal['symbol'],
        'side': signal['action'],  # BUY ou SELL
        'quantity': quantity,
        'pool_id': pool.id,
        'user_id': pool.user_id
    })
    
    # 4. Executar na exchange
    result = OrderManager.execute_order(order)
    
    # 5. Atualizar pool
    pool.capital_used += order.quantity * order.price
    pool.capital_available -= order.quantity * order.price
```

---

## 📡 COMUNICAÇÃO FRONTEND ↔ BACKEND

### **APIs Utilizadas:**

#### **AutoPilot:**
```javascript
GET  /api/trading/autopilot/status    // Status do motor
POST /api/trading/autopilot/start     // Iniciar motor
POST /api/trading/autopilot/stop      // Parar motor
GET  /api/trading/autopilot/config    // Configuração global
POST /api/trading/autopilot/config    // Atualizar config
```

#### **Pools:**
```javascript
GET    /api/trading/pools             // Listar pools
POST   /api/trading/pools             // Criar pool
GET    /api/trading/pools/{id}        // Detalhes do pool
PUT    /api/trading/pools/{id}        // Atualizar pool
DELETE /api/trading/pools/{id}        // Deletar pool
POST   /api/trading/pools/{id}/start  // Ativar pool
POST   /api/trading/pools/{id}/stop   // Desativar pool
```

#### **Posições e Ordens:**
```javascript
GET /api/trading/positions            // Posições abertas
GET /api/trading/orders               // Ordens
GET /api/trading/portfolio            // Portfólio
GET /api/trading/performance          // Performance
GET /api/trading/risk/alerts          // Alertas de risco
```

#### **Emergência:**
```javascript
POST /api/trading/emergency/panic-close-all  // Fechar tudo
```

---

## 🔄 ATUALIZAÇÃO AUTOMÁTICA

### **Polling (Atualização Periódica):**

```javascript
// AutomatedTrading.vue - onMounted
updateInterval = setInterval(async () => {
  await Promise.all([
    tradingStore.fetchPositions(),
    tradingStore.fetchOrders(),
    tradingStore.fetchPortfolio(),
    tradingStore.fetchRiskAlerts()
  ])
}, 10000)  // A cada 10 segundos
```

---

## 🎯 ESTADOS E STATUS

### **Status do Motor:**
- `running` - Motor rodando (🟢)
- `paused` - Motor pausado (⏸️)
- `stopped` - Motor parado (🔴)

### **Status dos Pools:**
- `active` - Pool ativo (🟢)
- `inactive` - Pool inativo (⚪)
- `paused` - Pool pausado (⏸️)
- `stopped` - Pool parado (🔴)

### **Status das Ordens:**
- `pending` - Aguardando execução
- `filled` - Executada
- `cancelled` - Cancelada
- `rejected` - Rejeitada

---

## 🛡️ VALIDAÇÕES E SEGURANÇA

### **Validações Antes de Executar Trade:**

1. **Confluência Mínima:**
   - Verifica se confluência >= mínimo (global ou do pool)

2. **Risco por Trade:**
   - Verifica se risco <= máximo configurado

3. **Capital Disponível:**
   - Verifica se pool tem capital suficiente

4. **Máximo de Posições:**
   - Verifica se pool não excedeu limite de posições

5. **Horário de Operação:**
   - Verifica se está dentro do horário permitido

---

## 📊 DADOS EXIBIDOS

### **Informações em Tempo Real:**

1. **Status do Motor:**
   - Rodando/Parado
   - Pares monitorados
   - Última análise

2. **Pools:**
   - Capital alocado/usado/disponível
   - Símbolos configurados
   - Risco por trade
   - Status

3. **Posições:**
   - Símbolo, lado, quantidade
   - Preço de entrada vs atual
   - P&L realizado e não realizado

4. **Portfólio:**
   - Capital total
   - P&L total
   - ROI
   - Exposição

---

## 🎮 AÇÕES DO USUÁRIO

### **1. Criar Pool:**
```
1. Clicar em "+ Novo Pool"
2. Preencher formulário:
   - Nome
   - Capital alocado
   - Símbolos (separados por vírgula)
   - Risco por trade (%)
   - Máximo de posições
3. Clicar em "Criar Pool"
```

### **2. Ativar Motor:**
```
1. Verificar configuração global
2. Clicar no toggle do Motor SNE
3. Motor inicia loop de análise
```

### **3. Monitorar:**
```
- Terminal de log mostra ações em tempo real
- Posições aparecem quando abertas
- Ordens aparecem quando criadas
- P&L atualiza automaticamente
```

---

## 🔧 ARQUIVOS PRINCIPAIS

### **Frontend:**
- `frontend/src/views/AutomatedTrading.vue` - View principal
- `frontend/src/stores/trading.js` - Store Pinia (estado)
- `frontend/src/services/tradingApi.js` - Cliente API
- `frontend/src/components/trading/*` - Componentes

### **Backend:**
- `app/api/trading/routes.py` - Rotas da API
- `app/api/trading/autopilot.py` - Rotas do AutoPilot
- `app/api/trading/pools.py` - Rotas dos Pools
- `app/services/autopilot_engine.py` - Motor autônomo
- `app/models/trading_models.py` - Modelos (Pool, Config, etc.)

---

## 📋 RESUMO

### **O que a aba faz:**

1. ✅ **Gerencia Pools de Capital** - Cria, edita, ativa pools
2. ✅ **Controla Motor Autônomo** - Liga/desliga análise automática
3. ✅ **Monitora Execução** - Logs, ordens, posições em tempo real
4. ✅ **Exibe Financeiro** - Portfólio, P&L, performance
5. ✅ **Alertas de Risco** - Notificações de situações críticas

### **Como funciona:**

1. **Motor analisa mercado** (loop contínuo)
2. **Gera sinais** (BUY/SELL/HOLD)
3. **Distribui para pools** interessados
4. **Cada pool executa** proporcionalmente ao capital
5. **Frontend atualiza** a cada 10 segundos

### **Vantagens:**

- ✅ **Eficiente:** Analisa cada par UMA VEZ
- ✅ **Flexível:** Múltiplos pools com perfis diferentes
- ✅ **Seguro:** Validações antes de executar
- ✅ **Transparente:** Logs detalhados de tudo
- ✅ **Profissional:** Arquitetura estilo hedge fund

---

**Documento criado em:** 02 de Janeiro de 2025

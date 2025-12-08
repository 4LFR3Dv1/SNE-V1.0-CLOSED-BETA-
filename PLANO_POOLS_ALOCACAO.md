# 🎯 PLANO: POOLS DE ALOCAÇÃO - ARQUITETURA HEDGE FUND

**Data:** 02 de Janeiro de 2025  
**Status:** 📋 Plano de Implementação

---

## 💡 NOVO PARADIGMA

### **ANTES (Redundante):**
```
Estratégia 1 → Analisa BTCUSDT → Executa
Estratégia 2 → Analisa BTCUSDT → Executa (mesma análise!)
Estratégia 3 → Analisa BTCUSDT → Executa (mesma análise!)
```

### **DEPOIS (Eficiente):**
```
Motor SNE → Analisa BTCUSDT UMA VEZ
    ↓
Verifica Pools interessados em BTCUSDT
    ↓
Distribui ordem proporcionalmente para cada Pool
```

---

## 🏗️ ARQUITETURA PROPOSTA

### **1. Motor SNE (Gestor Universal)**
- Analisa todos os pares configurados
- Gera sinais automaticamente
- Não precisa de "estratégias" - ele É a estratégia

### **2. Pools de Alocação**
- Usuário define: capital, pares, perfil de risco
- Sistema distribui trades baseado nos pools
- Foco em gestão de capital, não em lógica de trading

### **3. Filtros Globais**
- Confluência mínima
- Risco máximo por trade
- Horário de operação
- Aplicados a TODOS os pools

---

## 📊 NOVO MODELO DE DADOS

### **Pool (substitui Strategy):**

```python
class CapitalPool(db.Model):
    """
    Pool de Alocação de Capital
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(100))  # "Scalper BTC", "Swing Alts"
    description = Column(Text)
    
    # Alocação
    capital_allocated = Column(NUMERIC(...))  # $5,000
    capital_used = Column(NUMERIC(...))       # $2,000 (em posições)
    capital_available = Column(NUMERIC(...))  # $3,000
    
    # Pares de interesse
    symbols = Column(JSON)  # ["BTCUSDT", "ETHUSDT"]
    
    # Perfil de risco
    risk_per_trade_pct = Column(NUMERIC(...))  # 1.5%
    max_positions = Column(Integer)  # 5
    min_confluencia = Column(NUMERIC(...))  # 75% (override do global)
    
    # Status
    status = Column(String(20))  # 'active', 'paused', 'stopped'
    
    # Timestamps
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    user_id = Column(Integer, ForeignKey('user.id'))
```

### **GlobalConfig (novo):**

```python
class TradingGlobalConfig(db.Model):
    """
    Configurações Globais do Motor SNE
    """
    id = Column(Integer, primary_key=True)
    
    # Filtros de segurança
    min_confluencia_global = Column(NUMERIC(...), default=75.0)
    max_risk_per_trade_pct = Column(NUMERIC(...), default=1.5)
    
    # Pares para monitorar
    monitored_symbols = Column(JSON)  # ["BTCUSDT", "ETHUSDT", ...]
    default_timeframe = Column(String(10), default='1h')
    
    # Horário de operação
    trading_hours_start = Column(Time)
    trading_hours_end = Column(Time)
    trade_24_7 = Column(Boolean, default=True)
    
    # Status do motor
    motor_enabled = Column(Boolean, default=False)
    
    user_id = Column(Integer, ForeignKey('user.id'))
```

---

## 🔄 NOVO FLUXO DE EXECUÇÃO

### **AutoPilotEngine (substitui StrategyEngine):**

```python
class AutoPilotEngine:
    """
    Motor Autônomo - Analisa mercado e distribui para pools
    """
    
    def __init__(self):
        self.global_config = TradingGlobalConfig.query.first()
        self.running = False
    
    def start(self):
        """Inicia o motor autônomo"""
        self.running = True
        thread = threading.Thread(target=self._main_loop)
        thread.start()
    
    def _main_loop(self):
        """Loop principal - analisa mercado continuamente"""
        while self.running:
            # 1. Buscar configuração global
            config = self.global_config
            
            # 2. Para cada par monitorado
            for symbol in config.monitored_symbols:
                # 3. Analisar UMA VEZ com motor_renan
                analise = motor_renan.analise_completa(
                    symbol, 
                    config.default_timeframe
                )
                
                # 4. Extrair sinal
                signal = self._extract_signal(analise)
                
                # 5. Se sinal válido, verificar pools interessados
                if signal and signal['action'] != 'HOLD':
                    pools = self._get_interested_pools(symbol)
                    
                    # 6. Para cada pool, calcular alocação e executar
                    for pool in pools:
                        if self._validate_pool_trade(pool, signal):
                            self._execute_pool_trade(pool, signal)
            
            # Aguardar antes da próxima análise
            time.sleep(60)  # 1 minuto
    
    def _get_interested_pools(self, symbol):
        """Retorna pools que querem operar este símbolo"""
        return CapitalPool.query.filter(
            CapitalPool.status == 'active',
            CapitalPool.symbols.contains([symbol])
        ).all()
    
    def _execute_pool_trade(self, pool, signal):
        """Executa trade para um pool específico"""
        # Calcular quantidade baseado no capital do pool
        quantity = self._calculate_pool_quantity(pool, signal)
        
        # Criar ordem proporcional ao pool
        order = OrderManager.create_order({
            'symbol': signal['symbol'],
            'side': signal['action'],
            'quantity': quantity,
            'pool_id': pool.id,  # ← Novo campo
            'user_id': pool.user_id
        })
```

---

## 🎨 NOVA INTERFACE (UX)

### **Layout Proposto:**

```
┌─────────────────────────────────────────────────────────┐
│  🏦 TRADING AUTOMATIZADO - MOTOR SNE 3.0                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [ MESTRE: MOTOR SNE ]  🟢 ON  |  🔴 OFF                │
│                                                          │
│  Status: Analisando 12 Pares em Tempo Real...           │
│  Última Análise: BTCUSDT @ 42,500 (Confluência: 85%)    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 ALOCAÇÃO DE CAPITAL                                 │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ PERFIL      │ PARES          │ CAPITAL  │ STATUS │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Scalper BTC │ BTCUSDT        │ $5,000   │ 🟢 ON  │  │
│  │ Swing Alts  │ ETH, SOL, ADA  │ $2,000   │ 🟢 ON  │  │
│  │ Conservative│ Top 10         │ $10,000  │ 🔴 OFF │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  [ + Adicionar Pool ]                                   │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ⚙️ FILTROS GLOBAIS DE SEGURANÇA                        │
│                                                          │
│  Confluência Mínima: [75%] ────────────────            │
│  Risco Máximo por Trade: [1.5%] ───────────            │
│  Horário: [24/7] ☑️  [Custom] ☐                        │
│                                                          │
│  Pares Monitorados:                                     │
│  [BTCUSDT] [ETHUSDT] [BNBUSDT] [SOLUSDT] ...           │
│  [ + Adicionar Par ]                                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 MIGRAÇÃO DO CÓDIGO

### **Fase 1: Criar Novos Modelos**
1. ✅ Criar `CapitalPool` model
2. ✅ Criar `TradingGlobalConfig` model
3. ✅ Migration para criar tabelas

### **Fase 2: Criar AutoPilotEngine**
1. ✅ Substituir `StrategyEngine` por `AutoPilotEngine`
2. ✅ Implementar loop principal
3. ✅ Implementar distribuição para pools

### **Fase 3: Atualizar API**
1. ✅ Rotas para pools (CRUD)
2. ✅ Rota para config global
3. ✅ Rota para start/stop motor

### **Fase 4: Atualizar Frontend**
1. ✅ Nova interface de pools
2. ✅ Painel de config global
3. ✅ Remover interface de "estratégias"

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### **Backend:**
- [ ] Criar model `CapitalPool`
- [ ] Criar model `TradingGlobalConfig`
- [ ] Migration para novas tabelas
- [ ] Criar `AutoPilotEngine` (substituir `StrategyEngine`)
- [ ] Atualizar `Order` model (adicionar `pool_id`)
- [ ] Criar rotas API para pools
- [ ] Criar rotas API para config global
- [ ] Atualizar `OrderManager` para suportar pools

### **Frontend:**
- [ ] Criar componente `PoolManager`
- [ ] Criar componente `GlobalConfigPanel`
- [ ] Atualizar `AutomatedTrading.vue`
- [ ] Remover componentes de "estratégias"
- [ ] Atualizar store (trading.js)

### **Testes:**
- [ ] Testar criação de pools
- [ ] Testar motor autônomo
- [ ] Testar distribuição de trades
- [ ] Testar filtros globais

---

## 🎯 VANTAGENS DA NOVA ARQUITETURA

1. **Eficiência Computacional**
   - Analisa cada par UMA VEZ
   - Distribui para múltiplos pools
   - Reduz carga do sistema

2. **Intuitividade**
   - Foco em alocação de capital
   - Não precisa "ensinar" o robô
   - Mentalidade de hedge fund

3. **Flexibilidade**
   - Múltiplos pools com perfis diferentes
   - Configuração global centralizada
   - Fácil adicionar/remover pools

4. **Escalabilidade**
   - Fácil adicionar novos pares
   - Fácil criar novos pools
   - Sistema cresce naturalmente

---

## 🚀 PRÓXIMOS PASSOS

1. **Aprovar arquitetura** ✅
2. **Implementar modelos** (CapitalPool, TradingGlobalConfig)
3. **Criar AutoPilotEngine**
4. **Atualizar API**
5. **Atualizar Frontend**
6. **Testar sistema completo**

---

**Status:** 📋 Plano Aprovado - Pronto para Implementação



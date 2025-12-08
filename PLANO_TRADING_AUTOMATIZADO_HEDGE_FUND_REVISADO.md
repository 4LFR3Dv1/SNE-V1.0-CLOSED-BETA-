# 🏦 PLANO DE IMPLEMENTAÇÃO: TRADING AUTOMATIZADO PARA HEDGE FUND
## 📋 REVISÃO TÉCNICA CTO - VERSÃO CRÍTICA

**Data:** 02 de Janeiro de 2025  
**Revisão:** CTO Technical Review - Infraestrutura Crítica  
**Status:** ✅ Revisado com 4 Considerações Técnicas Vitais

---

## 🚨 CONSIDERAÇÕES TÉCNICAS CRÍTICAS

### **1. O Problema do Float (CRÍTICO)**

**Risco:** Float em computação tem problemas de precisão. Em um fundo auditado, um centavo sumindo quebra o compliance.

**Solução:** Usar `db.Numeric` ou `db.Decimal` com precisão fixa.

```python
# ❌ ERRADO para dinheiro
price = db.Column(db.Float)

# ✅ CORRETO para Hedge Fund
price = db.Column(db.Numeric(precision=20, scale=8))
```

**Aplicação:**
- Todos os campos monetários: `price`, `quantity`, `pnl`, `balance`, `commission`
- Precisão: 20 dígitos totais, 8 casas decimais (padrão cripto)
- Exceção: Percentuais podem usar `scale=4` (4 casas decimais)

---

### **2. Reconciliação (Source of Truth)**

**Problema:** Banco de Dados e Binance podem dessincronizar (internet cai, API falha, etc.)

**Solução:** Serviço de Reconciliação que roda periodicamente.

**Novo Serviço:** `/app/services/reconciliation_engine.py`

**Funcionalidades:**
- Roda a cada 1 minuto (configurável)
- Baixa todas as posições reais da Binance
- Compara com Banco de Dados local
- Detecta discrepâncias:
  - Posições na Binance que não estão no DB
  - Posições no DB que não estão na Binance
  - Quantidades diferentes
  - Preços diferentes
- Ações:
  - **Alerta Crítico** (padrão): Notifica operador
  - **Auto-correção** (opcional): Sincroniza automaticamente
  - **Log de Auditoria**: Registra todas as discrepâncias

**Fluxo:**
```
1. ReconciliationEngine.run()
   ↓
2. BinanceExecutor.get_all_positions()
   ↓
3. Comparar com Position.query.all()
   ↓
4. Se discrepância:
   - ComplianceEngine.log_discrepancy()
   - RiskManager.alert_critical()
   - Opcional: auto_correct()
```

---

### **3. Latência e Assincronicidade (Fila de Ordens)**

**Problema:** Execução síncrona trava o servidor Flask.

**Solução:** Fila de mensagens (Redis + Celery).

**Arquitetura:**
```
Estratégia → Fila (Redis) → Worker (Celery) → Binance
```

**Componentes:**
- **Redis**: Fila de mensagens
- **Celery**: Workers assíncronos
- **Fila de Prioridades:**
  - `high_priority`: Ordens críticas (execução imediata)
  - `normal`: Ordens normais
  - `low_priority`: Reconciliação, relatórios

**Fluxo Atualizado:**
```
1. StrategyEngine gera sinal
   ↓
2. RiskManager valida (síncrono, rápido)
   ↓
3. OrderManager.create_order() → Retorna imediatamente
   ↓
4. Adiciona à fila Redis (high_priority)
   ↓
5. API retorna "Ordem Aceita" (status: pending)
   ↓
6. Worker Celery processa em background:
   - BinanceExecutor.place_order()
   - Atualiza status no DB
   - Notifica via WebSocket
```

**Novos Arquivos:**
- `/app/services/celery_app.py` - Configuração Celery
- `/app/tasks/order_tasks.py` - Tasks de execução
- `/app/tasks/reconciliation_tasks.py` - Tasks de reconciliação

---

### **4. Kill Switch de Hardware (Pânico)**

**Problema:** Software pode enlouquecer. Precisa de botão que não depende da lógica falha.

**Solução:** Rota de API separada e simplificada.

**Implementação:**

**Backend:**
```python
# /app/api/trading/emergency.py
@app.route('/api/trading/emergency/panic-close-all', methods=['POST'])
@require_emergency_permission
def panic_close_all():
    """
    FECHA TODAS AS POSIÇÕES IMEDIATAMENTE
    IGNORA VERIFICAÇÕES DE RISCO
    USA APENAS ORDENS MARKET SELL
    """
    # 1. Buscar todas as posições abertas
    # 2. Para cada posição: MARKET SELL
    # 3. Log crítico de auditoria
    # 4. Notificar todos os usuários
```

**Frontend:**
```vue
<!-- ExecutionControl.vue -->
<button 
  class="panic-button"
  @click="triggerPanicClose"
  :disabled="!canPanic"
>
  🚨 PANIC CLOSE ALL
</button>
```

**Características:**
- Rota separada (`/emergency/`)
- Ignora RiskManager
- Ignora validações
- Apenas MARKET SELL
- Log de auditoria obrigatório
- Requer permissão especial (`emergency.panic`)
- Confirmação dupla no frontend

---

## 🎨 REFINAMENTO VISUAL: COCKPIT DE AVIÃO

### **Layout Atualizado: `AutomatedTrading.vue`**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER: Trading Automatizado                                           │
│  [Status: 🟢 Running] [Total P&L: +$1,234.56] [🚨 PANIC CLOSE ALL]    │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────┬──────────────────────┐
│  COLUNA ESQUERDA     │  COLUNA CENTRO           │  COLUNA DIREITA      │
│  (Estratégia)        │  (Execução)              │  (Financeiro)        │
├──────────────────────┼──────────────────────────┼──────────────────────┤
│                      │                          │                      │
│  📊 ESTRATÉGIAS      │  📺 TERMINAL DE LOG      │  📈 EQUITY CURVE     │
│                      │  (Tempo Real)            │                      │
│  ┌────────────────┐  │  ┌────────────────────┐ │  ┌────────────────┐  │
│  │ Strategy 1     │  │  │ [14:00:01] ANALIS. │ │  │   [Gráfico]    │  │
│  │ 🟢 Running     │  │  │ [14:00:02] CONFLU. │ │  │                │  │
│  │ P&L: +$123.45  │  │  │ [14:00:03] RISCO   │ │  │                │  │
│  │ Health: ✅     │  │  │ [14:00:04] ORDEM   │ │  │                │  │
│  └────────────────┘  │  │ [14:00:05] FILLED  │ │  └────────────────┘  │
│                      │  └────────────────────┘ │                      │
│  ┌────────────────┐  │                          │  💰 EXPOSIÇÃO       │
│  │ Strategy 2     │  │  📋 ORDENS PENDENTES   │  ┌────────────────┐  │
│  │ 🟡 Paused      │  │  ┌────────────────────┐ │  │ Total: $50,000 │  │
│  │ P&L: +$45.67   │  │  │ BTCUSDT BUY 0.1    │ │  │ Used: $30,000  │  │
│  │ Health: ⚠️     │  │  │ Status: Pending    │ │  │ Free: $20,000  │  │
│  └────────────────┘  │  └────────────────────┘ │  └────────────────┘  │
│                      │                          │                      │
│  ┌────────────────┐  │  📊 POSIÇÕES ABERTAS   │  ⚠️  ALERTAS RISCO   │
│  │ Strategy 3     │  │  ┌────────────────────┐ │  ┌────────────────┐  │
│  │ 🔴 Stopped     │  │  │ BTCUSDT LONG 0.5   │ │  │ Max Drawdown   │  │
│  │ P&L: -$12.34   │  │  │ Entry: $50,000     │ │  │ 12.5% / 15%    │  │
│  │ Health: ❌     │  │  │ Current: $51,000   │ │  │                │  │
│  └────────────────┘  │  │ P&L: +$500 (+1%)   │ │  │ Daily Loss     │  │
│                      │  └────────────────────┘ │  │ 3.2% / 5%       │  │
│  [Nova Estratégia]   │                          │  └────────────────┘  │
│                      │                          │                      │
└──────────────────────┴──────────────────────────┴──────────────────────┘
```

### **Componentes Novos:**

#### **1. TerminalLog.vue**
- Console de log em tempo real
- Cores por tipo (INFO, WARNING, ERROR, SUCCESS)
- Auto-scroll
- Filtros (por estratégia, tipo, etc.)
- Exportar log

#### **2. StrategyHealthIndicator.vue**
- Luzes verde/amarela/vermelha
- Métricas de saúde:
  - Última execução
  - Taxa de erro
  - Latência
  - Conectividade

#### **3. ExposureMeter.vue**
- Gauge visual de exposição
- Cores: Verde (seguro) → Amarelo (atenção) → Vermelho (crítico)
- Breakdown por estratégia

---

## 📊 MODELOS DE BANCO DE DADOS CORRIGIDOS

### **Importações Necessárias:**

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import NUMERIC, DECIMAL
from sqlalchemy.orm import relationship
from decimal import Decimal
import datetime
```

### **Configuração de Precisão:**

```python
# Constantes de precisão
PRECISION_PRICE = 20  # Total de dígitos
SCALE_PRICE = 8       # Casas decimais (padrão cripto)
PRECISION_QUANTITY = 20
SCALE_QUANTITY = 8
PRECISION_PERCENT = 10
SCALE_PERCENT = 4     # 4 casas decimais para percentuais
PRECISION_PNL = 20
SCALE_PNL = 8
```

### **Modelos Corrigidos:**

#### **1. Strategy**

```python
class Strategy(db.Model):
    __tablename__ = 'strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))  # 'momentum', 'mean_reversion', 'breakout', etc.
    status = db.Column(db.String(20), default='inactive')  # 'active', 'paused', 'stopped', 'inactive'
    config = db.Column(db.JSON)  # Configurações da estratégia
    
    # Capital alocado (usar Numeric)
    capital_allocation = db.Column(
        db.Numeric(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False,
        default=Decimal('0.00')
    )
    
    # Risco por trade (usar Numeric)
    risk_per_trade = db.Column(
        db.Numeric(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False,
        default=Decimal('1.00')
    )
    
    max_positions = db.Column(db.Integer, default=5)
    symbols = db.Column(db.JSON)  # Lista de símbolos
    timeframes = db.Column(db.JSON)  # Lista de timeframes
    
    # Health check
    last_execution = db.Column(db.DateTime)
    last_error = db.Column(db.DateTime)
    error_count = db.Column(db.Integer, default=0)
    health_status = db.Column(db.String(20), default='unknown')  # 'healthy', 'warning', 'critical'
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamentos
    positions = db.relationship('Position', backref='strategy', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='strategy', lazy=True, cascade='all, delete-orphan')
    trades = db.relationship('Trade', backref='strategy', lazy=True, cascade='all, delete-orphan')
    
    # Índices
    __table_args__ = (
        Index('idx_strategy_user_status', 'user_id', 'status'),
        Index('idx_strategy_health', 'health_status'),
    )
```

#### **2. Position**

```python
class Position(db.Model):
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    side = db.Column(db.String(10), nullable=False)  # 'long', 'short'
    
    # Quantidade (usar Numeric)
    quantity = db.Column(
        db.Numeric(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        nullable=False
    )
    
    # Preços (usar Numeric)
    entry_price = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE),
        nullable=False
    )
    
    current_price = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    stop_loss = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    take_profit = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    # P&L (usar Numeric)
    unrealized_pnl = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    unrealized_pnl_pct = db.Column(
        db.Numeric(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        default=Decimal('0.00')
    )
    
    # Alavancagem e margem
    leverage = db.Column(
        db.Numeric(precision=5, scale=2),
        default=Decimal('1.00')
    )
    
    margin = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL)
    )
    
    # Reconciliação
    last_reconciled = db.Column(db.DateTime)
    reconciliation_status = db.Column(db.String(20), default='pending')  # 'pending', 'synced', 'discrepancy'
    
    opened_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamentos
    orders = db.relationship('Order', backref='position', lazy=True)
    
    # Índices
    __table_args__ = (
        Index('idx_position_symbol', 'symbol'),
        Index('idx_position_strategy', 'strategy_id'),
        Index('idx_position_reconciliation', 'reconciliation_status'),
    )
```

#### **3. Order**

```python
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    binance_order_id = db.Column(db.String(50), unique=True, index=True)  # ID da ordem na Binance
    symbol = db.Column(db.String(20), nullable=False, index=True)
    side = db.Column(db.String(10), nullable=False)  # 'buy', 'sell'
    type = db.Column(db.String(20), nullable=False)  # 'market', 'limit', 'stop', 'stop_limit'
    
    # Quantidade (usar Numeric)
    quantity = db.Column(
        db.Numeric(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        nullable=False
    )
    
    # Preços (usar Numeric)
    price = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )  # Para ordens limit
    
    stop_price = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )  # Para ordens stop
    
    status = db.Column(db.String(20), default='pending', index=True)  # 'pending', 'filled', 'cancelled', 'rejected', 'partially_filled'
    
    # Quantidade e preço preenchidos (usar Numeric)
    filled_quantity = db.Column(
        db.Numeric(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        default=Decimal('0.00')
    )
    
    filled_price = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    # Comissão (usar Numeric)
    commission = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    # Reconciliação
    last_reconciled = db.Column(db.DateTime)
    reconciliation_status = db.Column(db.String(20), default='pending')
    
    # Fila
    queue_priority = db.Column(db.String(20), default='normal')  # 'high', 'normal', 'low'
    celery_task_id = db.Column(db.String(100))  # ID da task Celery
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    executed_at = db.Column(db.DateTime)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Índices
    __table_args__ = (
        Index('idx_order_status', 'status'),
        Index('idx_order_symbol', 'symbol'),
        Index('idx_order_reconciliation', 'reconciliation_status'),
        Index('idx_order_created', 'created_at'),
    )
```

#### **4. Trade**

```python
class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    side = db.Column(db.String(10), nullable=False)  # 'long', 'short'
    
    # Preços (usar Numeric)
    entry_price = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE),
        nullable=False
    )
    
    exit_price = db.Column(
        db.Numeric(precision=PRECISION_PRICE, scale=SCALE_PRICE),
        nullable=False
    )
    
    # Quantidade (usar Numeric)
    quantity = db.Column(
        db.Numeric(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        nullable=False
    )
    
    # P&L (usar Numeric)
    pnl = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    pnl_pct = db.Column(
        db.Numeric(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False
    )
    
    # Comissão (usar Numeric)
    commission = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    duration = db.Column(db.Integer)  # Duração em segundos
    
    entry_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    exit_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    
    opened_at = db.Column(db.DateTime, nullable=False, index=True)
    closed_at = db.Column(db.DateTime, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Índices
    __table_args__ = (
        Index('idx_trade_strategy', 'strategy_id', 'closed_at'),
        Index('idx_trade_symbol', 'symbol', 'closed_at'),
    )
```

#### **5. Portfolio**

```python
class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Balances (usar Numeric)
    total_balance = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    available_balance = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    margin_used = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    # P&L (usar Numeric)
    unrealized_pnl = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    realized_pnl = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    total_pnl = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    # Equity = Balance + Unrealized PnL (usar Numeric)
    equity = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Índices
    __table_args__ = (
        Index('idx_portfolio_timestamp', 'timestamp'),
    )
```

#### **6. ComplianceLog**

```python
class ComplianceLog(db.Model):
    __tablename__ = 'compliance_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False, index=True)  # 'trade_executed', 'order_placed', 'strategy_started', 'panic_close', 'reconciliation_discrepancy', etc.
    entity_type = db.Column(db.String(50))  # 'order', 'position', 'strategy', 'portfolio', etc.
    entity_id = db.Column(db.Integer, index=True)
    
    # Detalhes da ação (JSON)
    details = db.Column(db.JSON)
    
    # Valores monetários envolvidos (usar Numeric)
    amount = db.Column(
        db.Numeric(precision=PRECISION_PNL, scale=SCALE_PNL)
    )
    
    # Metadados
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Aprovação
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    
    # Índices
    __table_args__ = (
        Index('idx_compliance_action', 'action', 'timestamp'),
        Index('idx_compliance_user', 'user_id', 'timestamp'),
        Index('idx_compliance_entity', 'entity_type', 'entity_id'),
    )
```

#### **7. RiskAlert**

```python
class RiskAlert(db.Model):
    __tablename__ = 'risk_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, index=True)  # 'max_drawdown', 'max_position_size', 'max_daily_loss', 'reconciliation_failure', etc.
    severity = db.Column(db.String(20), nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON)
    
    # Valores (usar Numeric)
    threshold_value = db.Column(
        db.Numeric(precision=PRECISION_PERCENT, scale=SCALE_PERCENT)
    )
    
    current_value = db.Column(
        db.Numeric(precision=PRECISION_PERCENT, scale=SCALE_PERCENT)
    )
    
    resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Índices
    __table_args__ = (
        Index('idx_risk_alert_severity', 'severity', 'resolved'),
        Index('idx_risk_alert_type', 'type', 'resolved'),
    )
```

#### **8. ReconciliationLog (NOVO)**

```python
class ReconciliationLog(db.Model):
    __tablename__ = 'reconciliation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    reconciliation_type = db.Column(db.String(50), nullable=False)  # 'position', 'order', 'balance'
    status = db.Column(db.String(20), nullable=False)  # 'success', 'discrepancy', 'error'
    
    # Detalhes da reconciliação
    details = db.Column(db.JSON)  # { 'binance_data': {...}, 'local_data': {...}, 'differences': {...} }
    
    # Ações tomadas
    action_taken = db.Column(db.String(50))  # 'alerted', 'auto_corrected', 'manual_review'
    
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Índices
    __table_args__ = (
        Index('idx_reconciliation_status', 'status', 'timestamp'),
        Index('idx_reconciliation_type', 'reconciliation_type', 'timestamp'),
    )
```

---

## 🔧 NOVOS SERVIÇOS

### **1. ReconciliationEngine**

**Arquivo:** `/app/services/reconciliation_engine.py`

```python
class ReconciliationEngine:
    """
    Motor de reconciliação que sincroniza dados locais com Binance
    """
    
    def __init__(self, binance_executor, db_session):
        self.binance = binance_executor
        self.db = db_session
        self.compliance = ComplianceEngine(db_session)
        self.risk_manager = RiskManager()
    
    def run_full_reconciliation(self):
        """
        Executa reconciliação completa:
        1. Posições
        2. Ordens pendentes
        3. Balances
        """
        results = {
            'positions': self.reconcile_positions(),
            'orders': self.reconcile_orders(),
            'balance': self.reconcile_balance()
        }
        return results
    
    def reconcile_positions(self):
        """
        Reconcilia posições abertas
        """
        # 1. Buscar posições da Binance
        binance_positions = self.binance.get_all_positions()
        
        # 2. Buscar posições do DB
        db_positions = Position.query.filter_by(
            reconciliation_status='pending'
        ).all()
        
        # 3. Comparar
        discrepancies = []
        for binance_pos in binance_positions:
            db_pos = next((p for p in db_positions if p.symbol == binance_pos['symbol']), None)
            
            if not db_pos:
                # Posição na Binance que não está no DB
                discrepancies.append({
                    'type': 'missing_in_db',
                    'symbol': binance_pos['symbol'],
                    'binance_data': binance_pos
                })
            elif self._compare_positions(db_pos, binance_pos):
                # Discrepância encontrada
                discrepancies.append({
                    'type': 'discrepancy',
                    'symbol': binance_pos['symbol'],
                    'db_data': self._position_to_dict(db_pos),
                    'binance_data': binance_pos
                })
        
        # 4. Processar discrepâncias
        for disc in discrepancies:
            self._handle_discrepancy(disc, 'position')
        
        return {
            'checked': len(binance_positions),
            'discrepancies': len(discrepancies)
        }
    
    def _handle_discrepancy(self, discrepancy, entity_type):
        """
        Trata discrepância encontrada
        """
        # 1. Log de auditoria
        self.compliance.log_action(
            action='reconciliation_discrepancy',
            entity_type=entity_type,
            entity_id=discrepancy.get('id'),
            details=discrepancy
        )
        
        # 2. Criar alerta de risco
        self.risk_manager.generate_risk_alert(
            type='reconciliation_failure',
            severity='critical',
            message=f"Discrepância encontrada em {entity_type}: {discrepancy['symbol']}",
            details=discrepancy
        )
        
        # 3. Salvar log de reconciliação
        log = ReconciliationLog(
            reconciliation_type=entity_type,
            status='discrepancy',
            details=discrepancy,
            action_taken='alerted'
        )
        self.db.session.add(log)
        self.db.session.commit()
```

### **2. CeleryApp**

**Arquivo:** `/app/services/celery_app.py`

```python
from celery import Celery
from flask import current_app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_routes={
            'app.tasks.order_tasks.*': {'queue': 'high_priority'},
            'app.tasks.reconciliation_tasks.*': {'queue': 'low_priority'},
        }
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
```

### **3. OrderTasks (Celery)**

**Arquivo:** `/app/tasks/order_tasks.py`

```python
from app.services.celery_app import celery
from app.services.binance_executor import BinanceExecutor
from app.services.order_manager import OrderManager
from app.models.models import Order, db

@celery.task(bind=True, max_retries=3)
def execute_order_task(self, order_id):
    """
    Task Celery para executar ordem na Binance
    """
    try:
        # 1. Buscar ordem
        order = Order.query.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # 2. Executar na Binance
        executor = BinanceExecutor()
        result = executor.place_order(
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            quantity=float(order.quantity),
            price=float(order.price) if order.price else None,
            stop_price=float(order.stop_price) if order.stop_price else None
        )
        
        # 3. Atualizar ordem
        order.binance_order_id = result['orderId']
        order.status = result['status']
        order.filled_quantity = Decimal(str(result.get('executedQty', 0)))
        order.filled_price = Decimal(str(result.get('price', 0)))
        order.executed_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'status': 'success', 'order_id': order_id}
        
    except Exception as exc:
        # Retry em caso de erro
        raise self.retry(exc=exc, countdown=60)
```

---

## 📋 PLANO DE IMPLEMENTAÇÃO ATUALIZADO

### **FASE 1: Fundação + Risco (Semana 1-2)**

**Tarefas:**
1. ✅ Criar modelos de banco com `Numeric` (não `Float`)
2. ✅ Criar migrações Alembic
3. ✅ Implementar `RiskManager` básico
4. ✅ Criar estrutura de serviços
5. ✅ Configurar Redis + Celery

### **FASE 2: Execução + Reconciliação (Semana 3-4)**

**Tarefas:**
1. ✅ Implementar `BinanceExecutor`
2. ✅ Implementar `OrderManager` com fila
3. ✅ Implementar `ReconciliationEngine`
4. ✅ Tasks Celery para execução
5. ✅ Tasks Celery para reconciliação (a cada 1 min)

### **FASE 3: Estratégias (Semana 5-6)**

**Tarefas:**
1. ✅ Implementar `StrategyEngine`
2. ✅ Integrar com `motor_renan.py`
3. ✅ Sistema de sinais automáticos
4. ✅ Gestão de múltiplas estratégias

### **FASE 4: Risco e Compliance Completo (Semana 7-8)**

**Tarefas:**
1. ✅ `RiskManager` completo
2. ✅ Sistema de alertas
3. ✅ `ComplianceEngine`
4. ✅ Logs de auditoria
5. ✅ **Kill Switch (Panic Close)**

### **FASE 5: Interface Cockpit (Semana 9-10)**

**Tarefas:**
1. ✅ Layout 3 colunas (Cockpit)
2. ✅ Terminal de log em tempo real
3. ✅ Health indicators
4. ✅ Exposure meters
5. ✅ Botão Panic Close

### **FASE 6: Testes e Refinamento (Semana 11-12)**

**Tarefas:**
1. ✅ Testes end-to-end
2. ✅ Testes de reconciliação
3. ✅ Testes de kill switch
4. ✅ Testes de carga
5. ✅ Documentação

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **Modelos de Banco:**
- [ ] Todos os campos monetários usam `Numeric(precision=20, scale=8)`
- [ ] Percentuais usam `Numeric(precision=10, scale=4)`
- [ ] Índices criados para queries frequentes
- [ ] Campos de reconciliação adicionados
- [ ] Campos de fila (Celery) adicionados

### **Reconciliação:**
- [ ] `ReconciliationEngine` implementado
- [ ] Task Celery para reconciliação periódica
- [ ] Logs de reconciliação
- [ ] Alertas de discrepância
- [ ] Auto-correção (opcional)

### **Fila de Ordens:**
- [ ] Redis configurado
- [ ] Celery configurado
- [ ] Tasks de execução criadas
- [ ] Prioridades de fila definidas
- [ ] Retry logic implementado

### **Kill Switch:**
- [ ] Rota `/api/trading/emergency/panic-close-all`
- [ ] Permissão especial `emergency.panic`
- [ ] Botão no frontend
- [ ] Confirmação dupla
- [ ] Log de auditoria obrigatório

### **Frontend Cockpit:**
- [ ] Layout 3 colunas
- [ ] Terminal de log
- [ ] Health indicators
- [ ] Exposure meters
- [ ] Botão Panic Close

---

**Status:** ✅ Plano Revisado e Atualizado  
**Próxima Ação:** Aguardando aprovação para iniciar FASE 1



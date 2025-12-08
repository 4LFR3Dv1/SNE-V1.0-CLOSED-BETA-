# 📊 MODELOS SQLALCHEMY CORRIGIDOS - TRADING AUTOMATIZADO

**Data:** 02 de Janeiro de 2025  
**Revisão:** CTO Technical Review - Tipos Numéricos Corrigidos + Idempotência  
**Status:** ✅ Pronto para Implementação FASE 1 (Institucional/Auditável)

---

## 🎯 PRINCÍPIOS APLICADOS

### **1. Precisão Numérica (CRÍTICO)**
- ❌ **NUNCA** usar `db.Float` para valores monetários
- ✅ **SEMPRE** usar `db.Numeric(precision=X, scale=Y)` ou `db.Decimal`
- Precisão padrão cripto: 20 dígitos totais, 8 casas decimais
- Percentuais: 10 dígitos totais, 4 casas decimais

### **2. Índices Estratégicos**
- Índices em campos usados em queries frequentes
- Índices compostos para queries complexas
- Índices em campos de reconciliação

### **3. Relacionamentos e Cascatas**
- Relacionamentos bem definidos
- Cascatas apropriadas (delete-orphan onde necessário)

---

## 📦 CÓDIGO COMPLETO DOS MODELOS

### **Arquivo: `/app/models/trading_models.py`**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos de Banco de Dados para Trading Automatizado
Todos os valores monetários usam Numeric (não Float) para precisão
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import NUMERIC
from sqlalchemy.orm import relationship
from decimal import Decimal
import datetime

# Importar db do models.py principal
from app.models.models import db

# ============================================================================
# CONSTANTES DE PRECISÃO
# ============================================================================

# Precisão para preços (cripto padrão: 8 casas decimais)
PRECISION_PRICE = 20  # Total de dígitos
SCALE_PRICE = 8       # Casas decimais

# Precisão para quantidades
PRECISION_QUANTITY = 20
SCALE_QUANTITY = 8

# Precisão para percentuais (4 casas decimais suficientes)
PRECISION_PERCENT = 10
SCALE_PERCENT = 4

# Precisão para P&L e valores monetários
PRECISION_PNL = 20
SCALE_PNL = 8

# Precisão para alavancagem (2 casas decimais)
PRECISION_LEVERAGE = 5
SCALE_LEVERAGE = 2


# ============================================================================
# MODELO: Strategy (Estratégia)
# ============================================================================

class Strategy(db.Model):
    """
    Estratégia de trading automatizado
    """
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # 'momentum', 'mean_reversion', 'breakout', 'arbitrage', etc.
    status = Column(String(20), default='inactive', nullable=False, index=True)  # 'active', 'paused', 'stopped', 'inactive'
    config = Column(JSON)  # Configurações da estratégia em JSON
    
    # Capital alocado (% do portfólio) - USAR NUMERIC
    capital_allocation = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False,
        default=Decimal('0.00')
    )
    
    # Risco por trade (% do capital) - USAR NUMERIC
    risk_per_trade = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False,
        default=Decimal('1.00')
    )
    
    max_positions = Column(Integer, default=5)
    symbols = Column(JSON)  # Lista de símbolos: ["BTCUSDT", "ETHUSDT", ...]
    timeframes = Column(JSON)  # Lista de timeframes: ["1m", "5m", "15m", ...]
    
    # Health check
    last_execution = Column(DateTime)
    last_error = Column(DateTime)
    error_count = Column(Integer, default=0)
    health_status = Column(String(20), default='unknown', index=True)  # 'healthy', 'warning', 'critical'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    # Relacionamentos
    positions = relationship(
        'Position',
        backref='strategy',
        lazy=True,
        cascade='all, delete-orphan'
    )
    orders = relationship(
        'Order',
        backref='strategy',
        lazy=True,
        cascade='all, delete-orphan'
    )
    trades = relationship(
        'Trade',
        backref='strategy',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # Índices compostos
    __table_args__ = (
        Index('idx_strategy_user_status', 'user_id', 'status'),
        Index('idx_strategy_health', 'health_status', 'last_execution'),
    )
    
    def __repr__(self):
        return f'<Strategy {self.name} ({self.status})>'


# ============================================================================
# MODELO: Position (Posição Aberta)
# ============================================================================

class Position(db.Model):
    """
    Posição aberta no mercado
    """
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'long', 'short'
    
    # Quantidade - USAR NUMERIC
    quantity = Column(
        NUMERIC(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        nullable=False
    )
    
    # Preços - USAR NUMERIC
    entry_price = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE),
        nullable=False
    )
    
    current_price = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    stop_loss = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    take_profit = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    # P&L - USAR NUMERIC
    unrealized_pnl = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    unrealized_pnl_pct = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        default=Decimal('0.00')
    )
    
    # Alavancagem e margem - USAR NUMERIC
    leverage = Column(
        NUMERIC(precision=PRECISION_LEVERAGE, scale=SCALE_LEVERAGE),
        default=Decimal('1.00')
    )
    
    margin = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL)
    )
    
    # Reconciliação
    last_reconciled = Column(DateTime)
    reconciliation_status = Column(
        String(20),
        default='pending',
        index=True
    )  # 'pending', 'synced', 'discrepancy'
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Foreign Keys
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    # Relacionamentos
    orders = relationship('Order', backref='position', lazy=True)
    
    # Índices
    __table_args__ = (
        Index('idx_position_symbol', 'symbol', 'opened_at'),
        Index('idx_position_strategy', 'strategy_id', 'opened_at'),
        Index('idx_position_reconciliation', 'reconciliation_status', 'last_reconciled'),
    )
    
    def __repr__(self):
        return f'<Position {self.symbol} {self.side} {self.quantity}>'


# ============================================================================
# MODELO: Order (Ordem)
# ============================================================================

class Order(db.Model):
    """
    Ordem de compra/venda
    """
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    
    # --- IDEMPOTÊNCIA (CRÍTICO) ---
    # ID interno único gerado pelo SNE ANTES de enviar para Binance (newClientOrderId)
    # Permite rastrear ordem mesmo se rede cair entre envio e resposta
    client_order_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # ID retornado pela Binance (orderId) - Pode ser Null se ordem falhar no envio
    binance_order_id = Column(String(50), unique=True, index=True, nullable=True)
    # -------------------------------
    
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'buy', 'sell'
    type = Column(String(20), nullable=False)  # 'market', 'limit', 'stop', 'stop_limit'
    
    # Quantidade - USAR NUMERIC
    quantity = Column(
        NUMERIC(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        nullable=False
    )
    
    # Preços - USAR NUMERIC
    price = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )  # Para ordens limit
    
    stop_price = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )  # Para ordens stop
    
    status = Column(
        String(20),
        default='pending',
        nullable=False,
        index=True
    )  # 'pending', 'filled', 'cancelled', 'rejected', 'partially_filled', 'expired'
    
    # Quantidade e preço preenchidos - USAR NUMERIC
    filled_quantity = Column(
        NUMERIC(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        default=Decimal('0.00')
    )
    
    filled_price = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE)
    )
    
    # Comissão - USAR NUMERIC
    commission = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    # Reconciliação
    last_reconciled = Column(DateTime)
    reconciliation_status = Column(
        String(20),
        default='pending',
        index=True
    )  # 'pending', 'synced', 'discrepancy'
    
    # Fila (Celery)
    queue_priority = Column(String(20), default='normal')  # 'high', 'normal', 'low'
    celery_task_id = Column(String(100), index=True)  # ID da task Celery
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    executed_at = Column(DateTime)
    
    # Foreign Keys
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False, index=True)
    position_id = Column(Integer, ForeignKey('positions.id'))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    # Índices
    __table_args__ = (
        Index('idx_order_status', 'status', 'created_at'),
        Index('idx_order_symbol', 'symbol', 'created_at'),
        Index('idx_order_reconciliation', 'reconciliation_status', 'last_reconciled'),
        Index('idx_order_celery', 'celery_task_id'),
        Index('idx_order_client_id', 'client_order_id'),  # Para reconciliação
    )
    
    def __repr__(self):
        return f'<Order {self.symbol} {self.side} {self.quantity} ({self.status})>'


# ============================================================================
# MODELO: Trade (Trade Completo)
# ============================================================================

class Trade(db.Model):
    """
    Trade completo (entrada + saída)
    """
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # 'long', 'short'
    
    # Preços - USAR NUMERIC
    entry_price = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE),
        nullable=False
    )
    
    exit_price = Column(
        NUMERIC(precision=PRECISION_PRICE, scale=SCALE_PRICE),
        nullable=False
    )
    
    # Quantidade - USAR NUMERIC
    quantity = Column(
        NUMERIC(precision=PRECISION_QUANTITY, scale=SCALE_QUANTITY),
        nullable=False
    )
    
    # P&L - USAR NUMERIC
    pnl = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    pnl_pct = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False
    )
    
    # Comissão - USAR NUMERIC
    commission = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    duration = Column(Integer)  # Duração em segundos
    
    # Foreign Keys
    entry_order_id = Column(Integer, ForeignKey('orders.id'))
    exit_order_id = Column(Integer, ForeignKey('orders.id'))
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False, index=True)
    
    # Timestamps
    opened_at = Column(DateTime, nullable=False, index=True)
    closed_at = Column(DateTime, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    # Índices
    __table_args__ = (
        Index('idx_trade_strategy', 'strategy_id', 'closed_at'),
        Index('idx_trade_symbol', 'symbol', 'closed_at'),
        Index('idx_trade_pnl', 'pnl', 'closed_at'),
    )
    
    def __repr__(self):
        return f'<Trade {self.symbol} {self.side} P&L: {self.pnl}>'


# ============================================================================
# MODELO: Portfolio (Portfólio)
# ============================================================================

class Portfolio(db.Model):
    """
    Snapshot do portfólio em um momento específico
    """
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    
    # Balances - USAR NUMERIC
    total_balance = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    available_balance = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    margin_used = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    # P&L - USAR NUMERIC
    unrealized_pnl = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    realized_pnl = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    total_pnl = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        default=Decimal('0.00')
    )
    
    # Equity = Balance + Unrealized PnL - USAR NUMERIC
    equity = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False
    )
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Foreign Key (um portfólio por usuário)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True, index=True)
    
    # Índices
    __table_args__ = (
        Index('idx_portfolio_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<Portfolio User {self.user_id} Equity: {self.equity}>'


# ============================================================================
# MODELO: ComplianceLog (Log de Compliance)
# ============================================================================

class ComplianceLog(db.Model):
    """
    Log de auditoria para compliance
    Todas as ações críticas são registradas aqui
    """
    __tablename__ = 'compliance_logs'
    
    id = Column(Integer, primary_key=True)
    action = Column(String(50), nullable=False, index=True)  # 'trade_executed', 'order_placed', 'strategy_started', 'panic_close', 'reconciliation_discrepancy', etc.
    entity_type = Column(String(50), index=True)  # 'order', 'position', 'strategy', 'portfolio', etc.
    entity_id = Column(Integer, index=True)
    
    # Detalhes da ação (JSON)
    details = Column(JSON)
    
    # Valor monetário envolvido (se aplicável) - USAR NUMERIC
    amount = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL)
    )
    
    # Metadados
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    
    # Aprovação
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey('user.id'))
    approved_at = Column(DateTime)
    
    # Índices
    __table_args__ = (
        Index('idx_compliance_action', 'action', 'timestamp'),
        Index('idx_compliance_user', 'user_id', 'timestamp'),
        Index('idx_compliance_entity', 'entity_type', 'entity_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<ComplianceLog {self.action} by User {self.user_id} at {self.timestamp}>'


# ============================================================================
# MODELO: RiskAlert (Alerta de Risco)
# ============================================================================

class RiskAlert(db.Model):
    """
    Alertas de risco gerados pelo RiskManager
    """
    __tablename__ = 'risk_alerts'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False, index=True)  # 'max_drawdown', 'max_position_size', 'max_daily_loss', 'reconciliation_failure', etc.
    severity = Column(String(20), nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'
    message = Column(Text, nullable=False)
    details = Column(JSON)
    
    # Valores (threshold e atual) - USAR NUMERIC
    threshold_value = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT)
    )
    
    current_value = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT)
    )
    
    # Resolução
    resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('user.id'))
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    # Índices
    __table_args__ = (
        Index('idx_risk_alert_severity', 'severity', 'resolved', 'created_at'),
        Index('idx_risk_alert_type', 'type', 'resolved', 'created_at'),
    )
    
    def __repr__(self):
        return f'<RiskAlert {self.type} ({self.severity}) - Resolved: {self.resolved}>'


# ============================================================================
# MODELO: ReconciliationLog (Log de Reconciliação) - NOVO
# ============================================================================

class ReconciliationLog(db.Model):
    """
    Log de reconciliação entre dados locais e Binance
    """
    __tablename__ = 'reconciliation_logs'
    
    id = Column(Integer, primary_key=True)
    reconciliation_type = Column(String(50), nullable=False, index=True)  # 'position', 'order', 'balance'
    status = Column(String(20), nullable=False, index=True)  # 'success', 'discrepancy', 'error'
    
    # Detalhes da reconciliação (JSON)
    # Estrutura: { 'binance_data': {...}, 'local_data': {...}, 'differences': {...} }
    details = Column(JSON)
    
    # Ação tomada
    action_taken = Column(String(50))  # 'alerted', 'auto_corrected', 'manual_review', 'none'
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    # Índices
    __table_args__ = (
        Index('idx_reconciliation_status', 'status', 'timestamp'),
        Index('idx_reconciliation_type', 'reconciliation_type', 'timestamp'),
        Index('idx_reconciliation_user', 'user_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<ReconciliationLog {self.reconciliation_type} - {self.status} at {self.timestamp}>'


# ============================================================================
# EXPORTAR TODOS OS MODELOS
# ============================================================================

__all__ = [
    'Strategy',
    'Position',
    'Order',
    'Trade',
    'Portfolio',
    'ComplianceLog',
    'RiskAlert',
    'ReconciliationLog',
    # Constantes
    'PRECISION_PRICE',
    'SCALE_PRICE',
    'PRECISION_QUANTITY',
    'SCALE_QUANTITY',
    'PRECISION_PERCENT',
    'SCALE_PERCENT',
    'PRECISION_PNL',
    'SCALE_PNL',
    'PRECISION_LEVERAGE',
    'SCALE_LEVERAGE',
]
```

---

## 📝 MIGRAÇÃO ALEMBIC

### **Arquivo: `/alembic/versions/0003_add_trading_models.py`**

```python
"""Add trading models

Revision ID: 0003_add_trading_models
Revises: 0002_add_performance_indexes
Create Date: 2025-01-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003_add_trading_models'
down_revision = '0002_add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela strategies
    op.create_table(
        'strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='inactive'),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('capital_allocation', sa.Numeric(precision=10, scale=4), nullable=False, server_default='0.00'),
        sa.Column('risk_per_trade', sa.Numeric(precision=10, scale=4), nullable=False, server_default='1.00'),
        sa.Column('max_positions', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('symbols', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('timeframes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_execution', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.DateTime(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('health_status', sa.String(length=20), nullable=True, server_default='unknown'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_strategy_user_status', 'strategies', ['user_id', 'status'])
    op.create_index('idx_strategy_health', 'strategies', ['health_status', 'last_execution'])
    op.create_index(op.f('ix_strategies_status'), 'strategies', ['status'])
    op.create_index(op.f('ix_strategies_health_status'), 'strategies', ['health_status'])
    op.create_index(op.f('ix_strategies_user_id'), 'strategies', ['user_id'])
    
    # Criar tabela positions
    op.create_table(
        'positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('entry_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('current_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('stop_loss', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('take_profit', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('unrealized_pnl_pct', sa.Numeric(precision=10, scale=4), nullable=True, server_default='0.00'),
        sa.Column('leverage', sa.Numeric(precision=5, scale=2), nullable=True, server_default='1.00'),
        sa.Column('margin', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('last_reconciled', sa.DateTime(), nullable=True),
        sa.Column('reconciliation_status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('opened_at', sa.DateTime(), nullable=False),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_position_symbol', 'positions', ['symbol', 'opened_at'])
    op.create_index('idx_position_strategy', 'positions', ['strategy_id', 'opened_at'])
    op.create_index('idx_position_reconciliation', 'positions', ['reconciliation_status', 'last_reconciled'])
    op.create_index(op.f('ix_positions_symbol'), 'positions', ['symbol'])
    op.create_index(op.f('ix_positions_strategy_id'), 'positions', ['strategy_id'])
    op.create_index(op.f('ix_positions_reconciliation_status'), 'positions', ['reconciliation_status'])
    op.create_index(op.f('ix_positions_opened_at'), 'positions', ['opened_at'])
    op.create_index(op.f('ix_positions_user_id'), 'positions', ['user_id'])
    
    # Criar tabela orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        # --- IDEMPOTÊNCIA (CRÍTICO) ---
        sa.Column('client_order_id', sa.String(length=50), nullable=False),  # ID gerado pelo SNE
        sa.Column('binance_order_id', sa.String(length=50), nullable=True),  # ID retornado pela Binance
        # -------------------------------
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('stop_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('filled_quantity', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('filled_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('last_reconciled', sa.DateTime(), nullable=True),
        sa.Column('reconciliation_status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('queue_priority', sa.String(length=20), nullable=True, server_default='normal'),
        sa.Column('celery_task_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['position_id'], ['positions.id'], ),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_order_id'),  # ID único gerado pelo SNE
        sa.UniqueConstraint('binance_order_id')  # ID único retornado pela Binance
    )
    op.create_index('idx_order_status', 'orders', ['status', 'created_at'])
    op.create_index('idx_order_symbol', 'orders', ['symbol', 'created_at'])
    op.create_index('idx_order_reconciliation', 'orders', ['reconciliation_status', 'last_reconciled'])
    op.create_index(op.f('ix_orders_client_order_id'), 'orders', ['client_order_id'], unique=True)
    op.create_index(op.f('ix_orders_binance_order_id'), 'orders', ['binance_order_id'], unique=True)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'])
    op.create_index(op.f('ix_orders_symbol'), 'orders', ['symbol'])
    op.create_index(op.f('ix_orders_reconciliation_status'), 'orders', ['reconciliation_status'])
    op.create_index(op.f('ix_orders_created_at'), 'orders', ['created_at'])
    op.create_index(op.f('ix_orders_strategy_id'), 'orders', ['strategy_id'])
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'])
    op.create_index(op.f('ix_orders_celery_task_id'), 'orders', ['celery_task_id'])
    
    # Criar tabela trades
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('entry_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('exit_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('pnl', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('pnl_pct', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('entry_order_id', sa.Integer(), nullable=True),
        sa.Column('exit_order_id', sa.Integer(), nullable=True),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('opened_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['entry_order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['exit_order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_trade_strategy', 'trades', ['strategy_id', 'closed_at'])
    op.create_index('idx_trade_symbol', 'trades', ['symbol', 'closed_at'])
    op.create_index('idx_trade_pnl', 'trades', ['pnl', 'closed_at'])
    op.create_index(op.f('ix_trades_symbol'), 'trades', ['symbol'])
    op.create_index(op.f('ix_trades_strategy_id'), 'trades', ['strategy_id'])
    op.create_index(op.f('ix_trades_opened_at'), 'trades', ['opened_at'])
    op.create_index(op.f('ix_trades_closed_at'), 'trades', ['closed_at'])
    op.create_index(op.f('ix_trades_user_id'), 'trades', ['user_id'])
    
    # Criar tabela portfolios
    op.create_table(
        'portfolios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('total_balance', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('available_balance', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('margin_used', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('realized_pnl', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('total_pnl', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0.00'),
        sa.Column('equity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_portfolio_timestamp', 'portfolios', ['timestamp'])
    op.create_index(op.f('ix_portfolios_user_id'), 'portfolios', ['user_id'])
    
    # Criar tabela compliance_logs
    op.create_table(
        'compliance_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('amount', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_compliance_action', 'compliance_logs', ['action', 'timestamp'])
    op.create_index('idx_compliance_user', 'compliance_logs', ['user_id', 'timestamp'])
    op.create_index('idx_compliance_entity', 'compliance_logs', ['entity_type', 'entity_id', 'timestamp'])
    op.create_index(op.f('ix_compliance_logs_action'), 'compliance_logs', ['action'])
    op.create_index(op.f('ix_compliance_logs_entity_type'), 'compliance_logs', ['entity_type'])
    op.create_index(op.f('ix_compliance_logs_entity_id'), 'compliance_logs', ['entity_id'])
    op.create_index(op.f('ix_compliance_logs_timestamp'), 'compliance_logs', ['timestamp'])
    op.create_index(op.f('ix_compliance_logs_user_id'), 'compliance_logs', ['user_id'])
    
    # Criar tabela risk_alerts
    op.create_table(
        'risk_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('threshold_value', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('current_value', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['resolved_by'], ['user.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_risk_alert_severity', 'risk_alerts', ['severity', 'resolved', 'created_at'])
    op.create_index('idx_risk_alert_type', 'risk_alerts', ['type', 'resolved', 'created_at'])
    op.create_index(op.f('ix_risk_alerts_type'), 'risk_alerts', ['type'])
    op.create_index(op.f('ix_risk_alerts_severity'), 'risk_alerts', ['severity'])
    op.create_index(op.f('ix_risk_alerts_resolved'), 'risk_alerts', ['resolved'])
    op.create_index(op.f('ix_risk_alerts_created_at'), 'risk_alerts', ['created_at'])
    op.create_index(op.f('ix_risk_alerts_user_id'), 'risk_alerts', ['user_id'])
    
    # Criar tabela reconciliation_logs
    op.create_table(
        'reconciliation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reconciliation_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('action_taken', sa.String(length=50), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_reconciliation_status', 'reconciliation_logs', ['status', 'timestamp'])
    op.create_index('idx_reconciliation_type', 'reconciliation_logs', ['reconciliation_type', 'timestamp'])
    op.create_index('idx_reconciliation_user', 'reconciliation_logs', ['user_id', 'timestamp'])
    op.create_index(op.f('ix_reconciliation_logs_reconciliation_type'), 'reconciliation_logs', ['reconciliation_type'])
    op.create_index(op.f('ix_reconciliation_logs_status'), 'reconciliation_logs', ['status'])
    op.create_index(op.f('ix_reconciliation_logs_timestamp'), 'reconciliation_logs', ['timestamp'])
    op.create_index(op.f('ix_reconciliation_logs_user_id'), 'reconciliation_logs', ['user_id'])


def downgrade():
    # Remover tabelas na ordem inversa (devido a foreign keys)
    op.drop_table('reconciliation_logs')
    op.drop_table('risk_alerts')
    op.drop_table('compliance_logs')
    op.drop_table('portfolios')
    op.drop_table('trades')
    op.drop_table('orders')
    op.drop_table('positions')
    op.drop_table('strategies')
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **Antes de Aplicar:**
- [ ] Revisar todos os tipos `Numeric` (não há `Float`)
- [ ] Verificar precisões (20,8 para preços/quantidades, 10,4 para percentuais)
- [ ] Confirmar índices necessários
- [ ] Testar migration em ambiente de desenvolvimento

### **Aplicar Migration:**
```bash
# Criar migration
alembic revision --autogenerate -m "Add trading models"

# Revisar migration gerada
# (comparar com a migration acima)

# Aplicar migration
alembic upgrade head
```

### **Após Aplicar:**
- [ ] Verificar tabelas criadas no banco
- [ ] Testar criação de registros
- [ ] Verificar precisão numérica
- [ ] Testar queries com índices

---

**Status:** ✅ Modelos Prontos para FASE 1  
**Próxima Ação:** Aplicar migration e testar


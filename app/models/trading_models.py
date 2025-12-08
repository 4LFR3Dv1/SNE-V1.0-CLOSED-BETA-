#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos de Banco de Dados para Trading Automatizado
Todos os valores monetários usam Numeric (não Float) para precisão
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text, Index, Time, Time
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
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=True, index=True)  # Deprecated - usar pool_id
    pool_id = Column(Integer, ForeignKey('capital_pools.id'), nullable=True, index=True)  # Novo - Pool de Alocação
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
    # ID interno único gerado pelo SNE ANTES de enviar para exchange
    # Permite rastrear ordem mesmo se rede cair entre envio e resposta
    client_order_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # ID retornado pela exchange (orderId) - Pode ser Null se ordem falhar no envio
    exchange_order_id = Column(String(50), unique=True, index=True, nullable=True)
    
    # Nome da exchange onde a ordem foi executada (bybit, binance, etc.)
    exchange_name = Column(String(20), default='bybit', nullable=False, index=True)
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
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=True, index=True)  # Deprecated - usar pool_id
    pool_id = Column(Integer, ForeignKey('capital_pools.id'), nullable=True, index=True)  # Novo - Pool de Alocação
    position_id = Column(Integer, ForeignKey('positions.id'), nullable=True)
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
# MODELO: CapitalPool (Pool de Alocação de Capital)
# ============================================================================

class CapitalPool(db.Model):
    """
    Pool de Alocação de Capital
    Substitui o conceito de "Estratégia" por alocação de capital
    """
    __tablename__ = 'capital_pools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Alocação de Capital
    capital_allocated = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False,
        default=Decimal('0.00')
    )
    capital_used = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False,
        default=Decimal('0.00')
    )
    capital_available = Column(
        NUMERIC(precision=PRECISION_PNL, scale=SCALE_PNL),
        nullable=False,
        default=Decimal('0.00')
    )
    
    # Pares de interesse
    symbols = Column(JSON, nullable=False)  # ["BTCUSDT", "ETHUSDT"]
    
    # Perfil de Risco
    risk_per_trade_pct = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False,
        default=Decimal('1.00')
    )
    max_positions = Column(Integer, default=5)
    min_confluencia = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=True  # Se None, usa o global
    )
    
    # Status
    status = Column(String(20), default='inactive', nullable=False, index=True)  # 'active', 'paused', 'stopped', 'inactive'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    # Relacionamentos
    orders = relationship(
        'Order',
        backref='pool',
        lazy=True,
        cascade='all, delete-orphan'
    )
    positions = relationship(
        'Position',
        backref='pool',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # Índices
    __table_args__ = (
        Index('idx_pool_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self):
        return f'<CapitalPool {self.name} (${self.capital_allocated})>'


# ============================================================================
# MODELO: TradingGlobalConfig (Configuração Global do Motor)
# ============================================================================

class TradingGlobalConfig(db.Model):
    """
    Configurações Globais do Motor SNE
    Define como o motor autônomo opera
    """
    __tablename__ = 'trading_global_config'
    
    id = Column(Integer, primary_key=True)
    
    # Filtros de Segurança Globais
    min_confluencia_global = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False,
        default=Decimal('75.00')
    )
    max_risk_per_trade_pct = Column(
        NUMERIC(precision=PRECISION_PERCENT, scale=SCALE_PERCENT),
        nullable=False,
        default=Decimal('1.50')
    )
    
    # Pares para Monitorar
    monitored_symbols = Column(JSON, nullable=False, default=list)  # ["BTCUSDT", "ETHUSDT", ...]
    default_timeframe = Column(String(10), nullable=False, default='1h')
    
    # Horário de Operação
    trading_hours_start = Column(Time, nullable=True)
    trading_hours_end = Column(Time, nullable=True)
    trade_24_7 = Column(Boolean, nullable=False, default=True)
    
    # Status do Motor
    motor_enabled = Column(Boolean, nullable=False, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True, unique=True)
    
    def __repr__(self):
        return f'<TradingGlobalConfig user:{self.user_id} enabled:{self.motor_enabled}>'


# ============================================================================
# EXPORTAR TODOS OS MODELOS
# ============================================================================

__all__ = [
    'Strategy',  # Deprecated - usar CapitalPool
    'CapitalPool',  # Novo
    'TradingGlobalConfig',  # Novo
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


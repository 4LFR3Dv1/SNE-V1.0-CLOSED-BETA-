"""Add trading models

Revision ID: 0003_add_trading_models
Revises: 0002
Create Date: 2025-01-02 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0003_add_trading_models'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Verifica se tabela existe"""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    return table_name in inspector.get_table_names()


def _index_exists(index_name: str, table_name: str) -> bool:
    """Verifica se índice existe"""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = inspector.get_indexes(table_name)
    return any(idx['name'] == index_name for idx in indexes)


def upgrade() -> None:
    # Verificar tabelas existentes
    existing_tables = set()
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())
    
    # Criar tabela strategies
    if 'strategies' not in existing_tables:
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
    
    # Criar índices de strategies (se tabela existe)
    if 'strategies' in existing_tables or 'strategies' not in existing_tables:
        if 'strategies' not in existing_tables:
            existing_tables.add('strategies')
        
        try:
            if not _index_exists('idx_strategy_user_status', 'strategies'):
                op.create_index('idx_strategy_user_status', 'strategies', ['user_id', 'status'])
        except:
            pass
        
        try:
            if not _index_exists('idx_strategy_health', 'strategies'):
                op.create_index('idx_strategy_health', 'strategies', ['health_status', 'last_execution'])
        except:
            pass
        
        try:
            op.create_index(op.f('ix_strategies_status'), 'strategies', ['status'], unique=False, if_not_exists=True)
        except:
            pass
        
        try:
            op.create_index(op.f('ix_strategies_health_status'), 'strategies', ['health_status'], unique=False, if_not_exists=True)
        except:
            pass
        
        try:
            op.create_index(op.f('ix_strategies_user_id'), 'strategies', ['user_id'], unique=False, if_not_exists=True)
        except:
            pass
    
    # Criar tabela positions
    if 'positions' not in existing_tables:
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
    
    # Criar índices de positions
    if 'positions' in existing_tables or 'positions' not in existing_tables:
        if 'positions' not in existing_tables:
            existing_tables.add('positions')
        
        for idx_name, cols in [
            ('idx_position_symbol', ['symbol', 'opened_at']),
            ('idx_position_strategy', ['strategy_id', 'opened_at']),
            ('idx_position_reconciliation', ['reconciliation_status', 'last_reconciled']),
        ]:
            try:
                if not _index_exists(idx_name, 'positions'):
                    op.create_index(idx_name, 'positions', cols)
            except:
                pass
        
        for idx_name in ['ix_positions_symbol', 'ix_positions_strategy_id', 'ix_positions_reconciliation_status', 'ix_positions_opened_at', 'ix_positions_user_id']:
            try:
                op.create_index(op.f(idx_name), 'positions', [idx_name.replace('ix_positions_', '').replace('_', '')], unique=False, if_not_exists=True)
            except:
                pass
    
    # Criar tabela orders
    if 'orders' not in existing_tables:
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
    else:
        # Se tabela já existe, adicionar coluna client_order_id se não existir
        try:
            conn = op.get_bind()
            inspector = sa.inspect(conn)
            columns = [col['name'] for col in inspector.get_columns('orders')]
            
            if 'client_order_id' not in columns:
                op.add_column('orders', sa.Column('client_order_id', sa.String(length=50), nullable=True))
                # Preencher com valores temporários
                op.execute("UPDATE orders SET client_order_id = 'TEMP-' || id WHERE client_order_id IS NULL")
                # Tornar NOT NULL
                op.alter_column('orders', 'client_order_id', nullable=False)
                # Criar índice único
                op.create_index('ix_orders_client_order_id', 'orders', ['client_order_id'], unique=True)
        except Exception as e:
            print(f"Warning: Could not add client_order_id column: {e}")
    
    # Criar índices de orders
    if 'orders' in existing_tables or 'orders' not in existing_tables:
        if 'orders' not in existing_tables:
            existing_tables.add('orders')
        
        for idx_name, cols in [
            ('idx_order_status', ['status', 'created_at']),
            ('idx_order_symbol', ['symbol', 'created_at']),
            ('idx_order_reconciliation', ['reconciliation_status', 'last_reconciled']),
            ('idx_order_celery', ['celery_task_id']),
            ('idx_order_client_id', ['client_order_id']),
        ]:
            try:
                if not _index_exists(idx_name, 'orders'):
                    op.create_index(idx_name, 'orders', cols)
            except:
                pass
        
        for idx_name in ['ix_orders_client_order_id', 'ix_orders_binance_order_id', 'ix_orders_status', 'ix_orders_symbol', 'ix_orders_reconciliation_status', 'ix_orders_created_at', 'ix_orders_strategy_id', 'ix_orders_user_id', 'ix_orders_celery_task_id']:
            try:
                col_name = idx_name.replace('ix_orders_', '')
                op.create_index(op.f(idx_name), 'orders', [col_name], unique=('client_order_id' in idx_name or 'binance_order_id' in idx_name), if_not_exists=True)
            except:
                pass
    
    # Criar tabela trades
    if 'trades' not in existing_tables:
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
    
    # Criar índices de trades
    if 'trades' in existing_tables or 'trades' not in existing_tables:
        if 'trades' not in existing_tables:
            existing_tables.add('trades')
        
        for idx_name, cols in [
            ('idx_trade_strategy', ['strategy_id', 'closed_at']),
            ('idx_trade_symbol', ['symbol', 'closed_at']),
            ('idx_trade_pnl', ['pnl', 'closed_at']),
        ]:
            try:
                if not _index_exists(idx_name, 'trades'):
                    op.create_index(idx_name, 'trades', cols)
            except:
                pass
        
        for idx_name in ['ix_trades_symbol', 'ix_trades_strategy_id', 'ix_trades_opened_at', 'ix_trades_closed_at', 'ix_trades_user_id']:
            try:
                col_name = idx_name.replace('ix_trades_', '')
                op.create_index(op.f(idx_name), 'trades', [col_name], unique=False, if_not_exists=True)
            except:
                pass
    
    # Criar tabela portfolios
    if 'portfolios' not in existing_tables:
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
    
    # Criar índices de portfolios
    if 'portfolios' in existing_tables or 'portfolios' not in existing_tables:
        if 'portfolios' not in existing_tables:
            existing_tables.add('portfolios')
        
        try:
            if not _index_exists('idx_portfolio_timestamp', 'portfolios'):
                op.create_index('idx_portfolio_timestamp', 'portfolios', ['timestamp'])
        except:
            pass
        
        try:
            op.create_index(op.f('ix_portfolios_user_id'), 'portfolios', ['user_id'], unique=False, if_not_exists=True)
        except:
            pass
    
    # Criar tabela compliance_logs
    if 'compliance_logs' not in existing_tables:
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
    
    # Criar índices de compliance_logs
    if 'compliance_logs' in existing_tables or 'compliance_logs' not in existing_tables:
        if 'compliance_logs' not in existing_tables:
            existing_tables.add('compliance_logs')
        
        for idx_name, cols in [
            ('idx_compliance_action', ['action', 'timestamp']),
            ('idx_compliance_user', ['user_id', 'timestamp']),
            ('idx_compliance_entity', ['entity_type', 'entity_id', 'timestamp']),
        ]:
            try:
                if not _index_exists(idx_name, 'compliance_logs'):
                    op.create_index(idx_name, 'compliance_logs', cols)
            except:
                pass
        
        for idx_name in ['ix_compliance_logs_action', 'ix_compliance_logs_entity_type', 'ix_compliance_logs_entity_id', 'ix_compliance_logs_timestamp', 'ix_compliance_logs_user_id']:
            try:
                col_name = idx_name.replace('ix_compliance_logs_', '')
                op.create_index(op.f(idx_name), 'compliance_logs', [col_name], unique=False, if_not_exists=True)
            except:
                pass
    
    # Criar tabela risk_alerts
    if 'risk_alerts' not in existing_tables:
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
    
    # Criar índices de risk_alerts
    if 'risk_alerts' in existing_tables or 'risk_alerts' not in existing_tables:
        if 'risk_alerts' not in existing_tables:
            existing_tables.add('risk_alerts')
        
        for idx_name, cols in [
            ('idx_risk_alert_severity', ['severity', 'resolved', 'created_at']),
            ('idx_risk_alert_type', ['type', 'resolved', 'created_at']),
        ]:
            try:
                if not _index_exists(idx_name, 'risk_alerts'):
                    op.create_index(idx_name, 'risk_alerts', cols)
            except:
                pass
        
        for idx_name in ['ix_risk_alerts_type', 'ix_risk_alerts_severity', 'ix_risk_alerts_resolved', 'ix_risk_alerts_created_at', 'ix_risk_alerts_user_id']:
            try:
                col_name = idx_name.replace('ix_risk_alerts_', '')
                op.create_index(op.f(idx_name), 'risk_alerts', [col_name], unique=False, if_not_exists=True)
            except:
                pass
    
    # Criar tabela reconciliation_logs
    if 'reconciliation_logs' not in existing_tables:
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
    
    # Criar índices de reconciliation_logs
    if 'reconciliation_logs' in existing_tables or 'reconciliation_logs' not in existing_tables:
        if 'reconciliation_logs' not in existing_tables:
            existing_tables.add('reconciliation_logs')
        
        for idx_name, cols in [
            ('idx_reconciliation_status', ['status', 'timestamp']),
            ('idx_reconciliation_type', ['reconciliation_type', 'timestamp']),
            ('idx_reconciliation_user', ['user_id', 'timestamp']),
        ]:
            try:
                if not _index_exists(idx_name, 'reconciliation_logs'):
                    op.create_index(idx_name, 'reconciliation_logs', cols)
            except:
                pass
        
        for idx_name in ['ix_reconciliation_logs_reconciliation_type', 'ix_reconciliation_logs_status', 'ix_reconciliation_logs_timestamp', 'ix_reconciliation_logs_user_id']:
            try:
                col_name = idx_name.replace('ix_reconciliation_logs_', '')
                op.create_index(op.f(idx_name), 'reconciliation_logs', [col_name], unique=False, if_not_exists=True)
            except:
                pass


def downgrade() -> None:
    # Remover tabelas na ordem inversa (devido a foreign keys)
    try:
        op.drop_table('reconciliation_logs')
    except:
        pass
    
    try:
        op.drop_table('risk_alerts')
    except:
        pass
    
    try:
        op.drop_table('compliance_logs')
    except:
        pass
    
    try:
        op.drop_table('portfolios')
    except:
        pass
    
    try:
        op.drop_table('trades')
    except:
        pass
    
    try:
        op.drop_table('orders')
    except:
        pass
    
    try:
        op.drop_table('positions')
    except:
        pass
    
    try:
        op.drop_table('strategies')
    except:
        pass

"""Add CapitalPool and TradingGlobalConfig

Revision ID: 0005_add_capital_pools
Revises: 0004_rename_binance_to_exchange
Create Date: 2025-01-02 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from decimal import Decimal

# revision identifiers, used by Alembic.
revision = '0005_add_capital_pools'
down_revision = '0004_rename_binance_to_exchange'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela capital_pools
    op.create_table(
        'capital_pools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('capital_allocated', sa.NUMERIC(precision=20, scale=8), nullable=False, server_default='0.00'),
        sa.Column('capital_used', sa.NUMERIC(precision=20, scale=8), nullable=False, server_default='0.00'),
        sa.Column('capital_available', sa.NUMERIC(precision=20, scale=8), nullable=False, server_default='0.00'),
        sa.Column('symbols', sa.JSON(), nullable=False),
        sa.Column('risk_per_trade_pct', sa.NUMERIC(precision=10, scale=4), nullable=False, server_default='1.00'),
        sa.Column('max_positions', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('min_confluencia', sa.NUMERIC(precision=10, scale=4), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='inactive'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_pool_user_status', 'capital_pools', ['user_id', 'status'], unique=False)
    op.create_index(op.f('ix_capital_pools_status'), 'capital_pools', ['status'], unique=False)
    op.create_index(op.f('ix_capital_pools_user_id'), 'capital_pools', ['user_id'], unique=False)
    
    # Criar tabela trading_global_config
    op.create_table(
        'trading_global_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('min_confluencia_global', sa.NUMERIC(precision=10, scale=4), nullable=False, server_default='75.00'),
        sa.Column('max_risk_per_trade_pct', sa.NUMERIC(precision=10, scale=4), nullable=False, server_default='1.50'),
        sa.Column('monitored_symbols', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('default_timeframe', sa.String(length=10), nullable=False, server_default='1h'),
        sa.Column('trading_hours_start', sa.Time(), nullable=True),
        sa.Column('trading_hours_end', sa.Time(), nullable=True),
        sa.Column('trade_24_7', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('motor_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_trading_global_config_motor_enabled'), 'trading_global_config', ['motor_enabled'], unique=False)
    op.create_index(op.f('ix_trading_global_config_user_id'), 'trading_global_config', ['user_id'], unique=False)
    
    # Adicionar pool_id nas tabelas orders e positions
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pool_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_orders_pool_id', 'capital_pools', ['pool_id'], ['id'])
        batch_op.create_index(op.f('ix_orders_pool_id'), ['pool_id'], unique=False)
    
    with op.batch_alter_table('positions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pool_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_positions_pool_id', 'capital_pools', ['pool_id'], ['id'])
        batch_op.create_index(op.f('ix_positions_pool_id'), ['pool_id'], unique=False)


def downgrade() -> None:
    # Remover pool_id das tabelas orders e positions
    with op.batch_alter_table('positions', schema=None) as batch_op:
        batch_op.drop_index(op.f('ix_positions_pool_id'))
        batch_op.drop_constraint('fk_positions_pool_id', type_='foreignkey')
        batch_op.drop_column('pool_id')
    
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_index(op.f('ix_orders_pool_id'))
        batch_op.drop_constraint('fk_orders_pool_id', type_='foreignkey')
        batch_op.drop_column('pool_id')
    
    # Remover tabelas
    op.drop_index(op.f('ix_trading_global_config_user_id'), table_name='trading_global_config')
    op.drop_index(op.f('ix_trading_global_config_motor_enabled'), table_name='trading_global_config')
    op.drop_table('trading_global_config')
    
    op.drop_index(op.f('ix_capital_pools_user_id'), table_name='capital_pools')
    op.drop_index(op.f('ix_capital_pools_status'), table_name='capital_pools')
    op.drop_index('idx_pool_user_status', table_name='capital_pools')
    op.drop_table('capital_pools')



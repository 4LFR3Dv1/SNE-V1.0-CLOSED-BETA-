"""Initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Signals table
    op.create_table(
        'signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('signal_type', sa.String(length=10), nullable=False),  # LONG, SHORT
        sa.Column('confluence_score', sa.Float(), nullable=True),
        sa.Column('entry_price', sa.Float(), nullable=True),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_signals_symbol_timeframe', 'signals', ['symbol', 'timeframe'])
    op.create_index('idx_signals_created_at', 'signals', ['created_at'])

    # Trades table
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('signal_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('trade_type', sa.String(length=10), nullable=False),  # LONG, SHORT
        sa.Column('entry_price', sa.Float(), nullable=False),
        sa.Column('exit_price', sa.Float(), nullable=True),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),  # OPEN, CLOSED, CANCELLED
        sa.Column('pnl', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_trades_user_id', 'trades', ['user_id'])
    op.create_index('idx_trades_status', 'trades', ['status'])


def downgrade() -> None:
    op.drop_index('idx_trades_status', table_name='trades')
    op.drop_index('idx_trades_user_id', table_name='trades')
    op.drop_table('trades')
    op.drop_index('idx_signals_created_at', table_name='signals')
    op.drop_index('idx_signals_symbol_timeframe', table_name='signals')
    op.drop_table('signals')
    op.drop_table('users')




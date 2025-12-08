"""add performance indexes

Revision ID: 0002
Revises: 0001_initial
Create Date: 2025-01-XX

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona índices para otimização de performance"""
    
    # Verificar se as tabelas existem antes de criar índices
    # Índices para tabela market_data (se existir)
    try:
        op.create_index(
            'idx_market_data_symbol_timestamp',
            'market_data',
            ['symbol', sa.text('timestamp DESC')],
            if_not_exists=True
        )
        
        op.create_index(
            'idx_market_data_timestamp',
            'market_data',
            [sa.text('timestamp DESC')],
            if_not_exists=True
        )
    except Exception:
        pass  # Tabela pode não existir
    
    # Índices para tabela alert (se existir)
    try:
        op.create_index(
            'idx_alerts_symbol_tipo',
            'alert',
            ['symbol', 'tipo'],
            if_not_exists=True
        )
        
        op.create_index(
            'idx_alerts_timestamp',
            'alert',
            [sa.text('timestamp DESC')],
            if_not_exists=True
        )
    except Exception:
        pass  # Tabela pode não existir
    
    # Índice para tabela user (se existir e tiver campo is_admin)
    try:
        op.create_index(
            'idx_users_is_admin',
            'user',
            ['is_admin'],
            if_not_exists=True
        )
    except Exception:
        pass  # Campo pode não existir


def downgrade() -> None:
    """Remove índices"""
    
    try:
        op.drop_index('idx_market_data_symbol_timestamp', table_name='market_data', if_exists=True)
        op.drop_index('idx_market_data_timestamp', table_name='market_data', if_exists=True)
    except Exception:
        pass
    
    try:
        op.drop_index('idx_alerts_symbol_tipo', table_name='alert', if_exists=True)
        op.drop_index('idx_alerts_timestamp', table_name='alert', if_exists=True)
    except Exception:
        pass
    
    try:
        op.drop_index('idx_users_is_admin', table_name='user', if_exists=True)
    except Exception:
        pass


"""Rename binance_order_id to exchange_order_id

Revision ID: 0004_rename_binance_to_exchange
Revises: 0003_add_trading_models
Create Date: 2025-01-02 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_rename_binance_to_exchange'
down_revision: Union[str, None] = '0003_add_trading_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renomear coluna binance_order_id para exchange_order_id
    try:
        op.alter_column('orders', 'binance_order_id', new_column_name='exchange_order_id')
        print("✅ Coluna binance_order_id renomeada para exchange_order_id")
    except Exception as e:
        # Se a coluna não existir ou já foi renomeada, tentar adicionar
        print(f"⚠️ Tentando adicionar coluna exchange_order_id: {e}")
        try:
            op.add_column('orders', sa.Column('exchange_order_id', sa.String(length=50), nullable=True))
            # Copiar dados se binance_order_id existir
            op.execute("""
                UPDATE orders 
                SET exchange_order_id = binance_order_id 
                WHERE binance_order_id IS NOT NULL
            """)
        except:
            pass
    
    # Adicionar coluna exchange_name se não existir
    try:
        op.add_column('orders', sa.Column('exchange_name', sa.String(length=20), nullable=True, server_default='bybit'))
        # Atualizar registros existentes
        op.execute("UPDATE orders SET exchange_name = 'binance' WHERE exchange_name IS NULL")
        # Tornar NOT NULL após atualizar
        op.alter_column('orders', 'exchange_name', nullable=False)
        print("✅ Coluna exchange_name adicionada")
    except Exception as e:
        print(f"⚠️ Coluna exchange_name pode já existir: {e}")
    
    # Criar índice se não existir
    try:
        op.create_index('ix_orders_exchange_name', 'orders', ['exchange_name'], unique=False)
        print("✅ Índice ix_orders_exchange_name criado")
    except:
        pass


def downgrade() -> None:
    # Reverter: renomear exchange_order_id para binance_order_id
    try:
        op.alter_column('orders', 'exchange_order_id', new_column_name='binance_order_id')
    except:
        pass
    
    # Remover coluna exchange_name
    try:
        op.drop_index('ix_orders_exchange_name', table_name='orders')
        op.drop_column('orders', 'exchange_name')
    except:
        pass



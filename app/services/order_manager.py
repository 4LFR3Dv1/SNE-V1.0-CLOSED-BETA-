#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Ordens
Cria e gerencia o ciclo de vida de ordens
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
from app.models.trading_models import Order, db
from app.models.trading_models import PRECISION_QUANTITY, SCALE_QUANTITY, PRECISION_PRICE, SCALE_PRICE


class OrderManager:
    """
    Gerenciador de ordens para trading automatizado
    """
    
    def __init__(self, db_session=None):
        self.db = db_session or db
    
    def create_order(self, order_data: Dict) -> Order:
        """
        Cria ordem com client_order_id único
        
        Args:
            order_data: Dicionário com dados da ordem
                - symbol: str
                - side: str ('buy' ou 'sell')
                - type: str ('market', 'limit', 'stop', etc)
                - quantity: Decimal ou float
                - price: Decimal ou float (opcional, para ordens limit)
                - stop_price: Decimal ou float (opcional, para ordens stop)
                - strategy_id: int (opcional, deprecated - usar pool_id)
                - pool_id: int (opcional, novo - Pool de Alocação)
                - user_id: int
                - position_id: int (opcional)
                - queue_priority: str ('high', 'normal', 'low')
        
        Returns:
            Order: Ordem criada
        """
        # Gerar UUID único ANTES de enviar para exchange
        client_order_id = f"SNE-{uuid.uuid4().hex[:16].upper()}-{int(datetime.utcnow().timestamp())}"
        
        # Obter nome da exchange (padrão: bybit)
        import os
        exchange_name = os.environ.get('EXCHANGE_NAME', 'bybit').lower()
        
        # Criar ordem no banco
        order = Order(
            client_order_id=client_order_id,  # ← ID gerado pelo SNE
            symbol=order_data['symbol'],
            side=order_data['side'].lower(),
            type=order_data['type'].lower(),
            quantity=Decimal(str(order_data['quantity'])),
            price=Decimal(str(order_data.get('price', 0))) if order_data.get('price') else None,
            stop_price=Decimal(str(order_data.get('stop_price', 0))) if order_data.get('stop_price') else None,
            status='pending',
            strategy_id=order_data.get('strategy_id'),  # Deprecated
            pool_id=order_data.get('pool_id'),  # Novo
            user_id=order_data['user_id'],
            position_id=order_data.get('position_id'),
            queue_priority=order_data.get('queue_priority', 'normal'),
            exchange_name=exchange_name,  # ← Nome da exchange
            # exchange_order_id será preenchido APÓS resposta da exchange
        )
        
        self.db.session.add(order)
        self.db.session.commit()
        
        return order
    
    def get_order(self, order_id: int) -> Optional[Order]:
        """Busca ordem por ID"""
        return Order.query.get(order_id)
    
    def get_order_by_client_id(self, client_order_id: str) -> Optional[Order]:
        """Busca ordem por client_order_id"""
        return Order.query.filter_by(client_order_id=client_order_id).first()
    
    def update_order_status(self, order_id: int, status: str, **kwargs) -> Optional[Order]:
        """
        Atualiza status da ordem
        
        Args:
            order_id: ID da ordem
            status: Novo status
            **kwargs: Outros campos para atualizar (exchange_order_id, filled_quantity, etc)
        """
        order = self.get_order(order_id)
        if not order:
            return None
        
        order.status = status
        order.updated_at = datetime.utcnow()
        
        # Atualizar campos adicionais
        for key, value in kwargs.items():
            if hasattr(order, key):
                if isinstance(value, (int, float)):
                    # Converter para Decimal se for campo numérico
                    if key in ['filled_quantity', 'quantity']:
                        setattr(order, key, Decimal(str(value)))
                    elif key in ['filled_price', 'price', 'stop_price', 'commission']:
                        setattr(order, key, Decimal(str(value)))
                    else:
                        setattr(order, key, value)
                else:
                    setattr(order, key, value)
        
        self.db.session.commit()
        return order
    
    def get_pending_orders(self, user_id: Optional[int] = None) -> list:
        """Busca ordens pendentes"""
        query = Order.query.filter_by(status='pending')
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.all()
    
    def cancel_order(self, order_id: int) -> bool:
        """Cancela ordem"""
        order = self.get_order(order_id)
        if not order:
            return False
        
        order.status = 'cancelled'
        self.db.session.commit()
        return True


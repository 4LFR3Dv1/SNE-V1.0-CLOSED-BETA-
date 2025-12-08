#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tasks Celery para execução de ordens
"""

from datetime import datetime
from decimal import Decimal
from app.models.trading_models import Order, db


# Celery será inicializado quando app Flask estiver disponível
celery = None


def init_celery(app):
    """Inicializa Celery com Flask app"""
    global celery
    from app.services.celery_app import make_celery
    celery = make_celery(app)
    
    # Registrar tasks após inicializar
    register_tasks()
    
    return celery


def execute_order_task_internal(order_id: int):
    """Função interna para executar ordem (chamada pela task)"""
    from app.services.executors.exchange_adapter import get_exchange_adapter
    from app.services.compliance_engine import ComplianceEngine
    
    # 1. Buscar ordem
    order = Order.query.get(order_id)
    if not order:
        raise ValueError(f"Order {order_id} not found")
    
    # 2. Obter adapter (usa exchange configurada)
    adapter = get_exchange_adapter()
    
    # 3. Mapear tipo de ordem para formato da exchange
    order_type_map = {
        'market': 'Market',
        'limit': 'Limit',
        'stop': 'Stop',
        'stop_limit': 'StopLimit'
    }
    exchange_order_type = order_type_map.get(order.type.lower(), 'Market')
    
    # 4. Mapear side (Bybit usa capitalizado, Binance usa uppercase)
    side_map = {
        'buy': 'Buy' if order.exchange_name == 'bybit' else 'BUY',
        'sell': 'Sell' if order.exchange_name == 'bybit' else 'SELL'
    }
    exchange_side = side_map.get(order.side.lower(), order.side)
    
    # 5. Executar na exchange
    result = adapter.place_order(
        symbol=order.symbol,
        side=exchange_side,
        qty=float(order.quantity),
        order_type=exchange_order_type,
        price=float(order.price) if order.price else None,
        client_order_id=order.client_order_id
    )
    
    # 6. Atualizar ordem
    order.exchange_order_id = str(result.get('order_id', ''))
    order.status = result.get('status', 'pending').lower()
    order.filled_quantity = Decimal(str(result.get('filled_qty', 0)))
    order.filled_price = Decimal(str(result.get('price', 0))) if result.get('price') else None
    order.executed_at = datetime.utcnow()
    order.reconciliation_status = 'synced'
    
    db.session.commit()
    
    # 7. Log de compliance
    compliance = ComplianceEngine(db.session)
    compliance.log_action(
        action='order_executed',
        entity_type='order',
        entity_id=order.id,
        user_id=order.user_id,
        details={
            'exchange_order_id': order.exchange_order_id,
            'exchange_name': order.exchange_name
        }
    )
    
    return {
        'status': 'success',
        'order_id': order_id,
        'exchange_order_id': order.exchange_order_id,
        'exchange_name': order.exchange_name
    }


def register_tasks():
    """Registra tasks Celery"""
    global celery
    if not celery:
        return
    
    @celery.task(bind=True, max_retries=3)
    def execute_order_task(self, order_id: int):
        """
        Task Celery para executar ordem na Binance
        
        Args:
            order_id: ID da ordem no banco de dados
        
        Returns:
            Dict: Resultado da execução
        """
        try:
            return execute_order_task_internal(order_id)
        except Exception as exc:
            # Atualizar ordem com erro
            order = Order.query.get(order_id)
            if order:
                order.status = 'rejected'
                order.reconciliation_status = 'discrepancy'
                db.session.commit()
            
            # Retry em caso de erro
            raise self.retry(exc=exc, countdown=60)
    
    @celery.task
    def cancel_order_task(order_id: int):
        """
        Task para cancelar ordem na exchange
        
        Args:
            order_id: ID da ordem
        """
        try:
            from app.services.executors.exchange_adapter import get_exchange_adapter
            
            order = Order.query.get(order_id)
            if not order:
                return {'status': 'error', 'message': 'Order not found'}
            
            adapter = get_exchange_adapter()
            
            if order.exchange_order_id:
                adapter.cancel_order(order.symbol, order_id=order.exchange_order_id)
            else:
                adapter.cancel_order(order.symbol, client_order_id=order.client_order_id)
            
            order.status = 'cancelled'
            db.session.commit()
            
            return {'status': 'success', 'order_id': order_id}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # Exportar tasks
    globals()['execute_order_task'] = execute_order_task
    globals()['cancel_order_task'] = cancel_order_task


# Fallback síncrono se Celery não estiver disponível
def execute_order_task_sync(order_id: int):
    """Execução síncrona se Celery não estiver disponível"""
    return execute_order_task_internal(order_id)

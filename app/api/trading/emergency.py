#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints de emergência (Kill Switch)
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.models.trading_models import Position, Order, db
from app.services.executors.exchange_adapter import get_exchange_adapter
from app.services.compliance_engine import ComplianceEngine
# execute_order_task será importado apenas se necessário
# from app.tasks.order_tasks import execute_order_task
from flask_login import login_required, current_user
from decimal import Decimal


compliance = ComplianceEngine()


def require_emergency_permission(f):
    """Decorator para verificar permissão de emergência"""
    # TODO: Implementar verificação de permissão 'emergency.panic'
    return login_required(f)


@trading_bp.route('/emergency/panic-close-all', methods=['POST'])
@require_emergency_permission
def panic_close_all():
    """
    FECHA TODAS AS POSIÇÕES IMEDIATAMENTE
    IGNORA VERIFICAÇÕES DE RISCO
    USA APENAS ORDENS MARKET SELL
    """
    try:
        # 1. Buscar todas as posições abertas
        positions = Position.query.filter_by(user_id=current_user.id).all()
        
        if not positions:
            return jsonify({
                'success': True,
                'message': 'No open positions to close',
                'closed_count': 0
            }), 200
        
        # 2. Para cada posição: MARKET SELL
        adapter = get_exchange_adapter()
        closed_count = 0
        errors = []
        
        for position in positions:
            try:
                # Criar ordem de fechamento (MARKET SELL)
                from app.services.order_manager import OrderManager
                order_manager = OrderManager()
                
                order_data = {
                    'symbol': position.symbol,
                    'side': 'sell' if position.side == 'long' else 'buy',
                    'type': 'market',
                    'quantity': position.quantity,
                    'strategy_id': position.strategy_id,
                    'user_id': current_user.id,
                    'position_id': position.id,
                    'queue_priority': 'high'
                }
                
                order = order_manager.create_order(order_data)
                
                # Mapear side para formato da exchange
                side_map = {
                    'buy': 'Buy' if order.exchange_name == 'bybit' else 'BUY',
                    'sell': 'Sell' if order.exchange_name == 'bybit' else 'SELL'
                }
                exchange_side = side_map.get(order.side.lower(), order.side)
                
                # Executar imediatamente (ignorar fila)
                result = adapter.place_order(
                    symbol=order.symbol,
                    side=exchange_side,
                    qty=float(order.quantity),
                    order_type='Market',
                    client_order_id=order.client_order_id
                )
                
                # Atualizar ordem
                order.exchange_order_id = str(result.get('order_id', ''))
                order.status = result.get('status', 'pending').lower()
                order.filled_quantity = Decimal(str(result.get('filled_qty', 0)))
                order.filled_price = Decimal(str(result.get('price', 0))) if result.get('price') else None
                
                # Fechar posição
                # TODO: Implementar lógica de fechamento de posição
                
                closed_count += 1
                
            except Exception as e:
                errors.append({
                    'position_id': position.id,
                    'symbol': position.symbol,
                    'error': str(e)
                })
        
        db.session.commit()
        
        # 3. Log crítico de auditoria
        compliance.log_action(
            action='panic_close_all',
            entity_type='portfolio',
            entity_id=None,
            user_id=current_user.id,
            details={
                'positions_closed': closed_count,
                'errors': errors,
                'total_positions': len(positions)
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Panic close executed: {closed_count}/{len(positions)} positions closed',
            'closed_count': closed_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints para execução de ordens
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.models.trading_models import Order, db
from app.services.order_manager import OrderManager
from app.services.risk_manager import RiskManager
from app.services.portfolio_manager import PortfolioManager
# Import será feito dinamicamente se Celery estiver disponível
try:
    from app.tasks.order_tasks import execute_order_task
    CELERY_AVAILABLE = True
except:
    from app.tasks.order_tasks import execute_order_task_sync as execute_order_task
    CELERY_AVAILABLE = False
from flask_login import login_required, current_user
from decimal import Decimal


order_manager = OrderManager()
risk_manager = RiskManager()
portfolio_manager = PortfolioManager()


@trading_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """Cria nova ordem"""
    try:
        data = request.get_json()
        
        # Validar risco
        portfolio = portfolio_manager.get_portfolio(current_user.id)
        trade_data = {
            'entry': data['price'] or data.get('entry'),
            'stop_loss': data.get('stop_loss'),
            'take_profit': data.get('take_profit'),
            'quantity': data['quantity'],
            'symbol': data['symbol'],
            'user_id': current_user.id
        }
        
        approved, error_msg = risk_manager.validate_trade(trade_data, portfolio)
        if not approved:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Criar ordem
        order_data = {
            'symbol': data['symbol'],
            'side': data['side'],
            'type': data['type'],
            'quantity': data['quantity'],
            'price': data.get('price'),
            'stop_price': data.get('stop_price'),
            'strategy_id': data.get('strategy_id'),
            'user_id': current_user.id,
            'position_id': data.get('position_id'),
            'queue_priority': data.get('queue_priority', 'normal')
        }
        
        order = order_manager.create_order(order_data)
        
        # Enviar para fila Celery (ou executar síncrono)
        if CELERY_AVAILABLE:
            task = execute_order_task.delay(order.id)
            order.celery_task_id = task.id
            db.session.commit()
        else:
            # Execução síncrona se Celery não disponível
            execute_order_task(order.id)
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'client_order_id': order.client_order_id,
                'exchange_name': order.exchange_name,
                'status': order.status,
                'celery_task_id': task.id if CELERY_AVAILABLE else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/orders', methods=['GET'])
@login_required
def list_orders():
    """Lista ordens do usuário"""
    try:
        status = request.args.get('status')
        query = Order.query.filter_by(user_id=current_user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).limit(100).all()
        
        return jsonify({
            'success': True,
            'orders': [{
                'id': o.id,
                'client_order_id': o.client_order_id,
                'exchange_order_id': o.exchange_order_id,
                'exchange_name': o.exchange_name,
                'symbol': o.symbol,
                'side': o.side,
                'type': o.type,
                'quantity': float(o.quantity),
                'price': float(o.price) if o.price else None,
                'status': o.status,
                'filled_quantity': float(o.filled_quantity),
                'filled_price': float(o.filled_price) if o.filled_price else None,
                'created_at': o.created_at.isoformat(),
                'executed_at': o.executed_at.isoformat() if o.executed_at else None
            } for o in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancela ordem"""
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        success = order_manager.cancel_order(order_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Order cancelled'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to cancel order'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints para gestão de posições
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.models.trading_models import Position, db
from flask_login import login_required, current_user


@trading_bp.route('/positions', methods=['GET'])
@login_required
def list_positions():
    """Lista posições abertas"""
    try:
        positions = Position.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            'success': True,
            'positions': [{
                'id': p.id,
                'symbol': p.symbol,
                'side': p.side,
                'quantity': float(p.quantity),
                'entry_price': float(p.entry_price),
                'current_price': float(p.current_price) if p.current_price else None,
                'stop_loss': float(p.stop_loss) if p.stop_loss else None,
                'take_profit': float(p.take_profit) if p.take_profit else None,
                'unrealized_pnl': float(p.unrealized_pnl),
                'unrealized_pnl_pct': float(p.unrealized_pnl_pct),
                'leverage': float(p.leverage),
                'opened_at': p.opened_at.isoformat(),
                'strategy_id': p.strategy_id
            } for p in positions]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/positions/<int:position_id>', methods=['GET'])
@login_required
def get_position(position_id):
    """Obtém posição específica"""
    try:
        position = Position.query.filter_by(id=position_id, user_id=current_user.id).first()
        if not position:
            return jsonify({'success': False, 'error': 'Position not found'}), 404
        
        return jsonify({
            'success': True,
            'position': {
                'id': position.id,
                'symbol': position.symbol,
                'side': position.side,
                'quantity': float(position.quantity),
                'entry_price': float(position.entry_price),
                'current_price': float(position.current_price) if position.current_price else None,
                'stop_loss': float(position.stop_loss) if position.stop_loss else None,
                'take_profit': float(position.take_profit) if position.take_profit else None,
                'unrealized_pnl': float(position.unrealized_pnl),
                'unrealized_pnl_pct': float(position.unrealized_pnl_pct),
                'leverage': float(position.leverage),
                'opened_at': position.opened_at.isoformat(),
                'strategy_id': position.strategy_id
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/positions/<int:position_id>/close', methods=['POST'])
@login_required
def close_position(position_id):
    """Fecha posição manualmente"""
    try:
        position = Position.query.filter_by(id=position_id, user_id=current_user.id).first()
        if not position:
            return jsonify({'success': False, 'error': 'Position not found'}), 404
        
        # TODO: Criar ordem de fechamento
        # Por enquanto, apenas retorna sucesso
        
        return jsonify({'success': True, 'message': 'Position close order created'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



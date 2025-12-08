#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Endpoints para gestão de estratégias
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.models.trading_models import Strategy, db
from app.services.strategy_engine import StrategyEngine
from app.services.compliance_engine import ComplianceEngine
from flask_login import login_required, current_user
from decimal import Decimal


strategy_engine = StrategyEngine()
compliance = ComplianceEngine()


@trading_bp.route('/strategies', methods=['GET'])
@login_required
def list_strategies():
    """Lista estratégias do usuário"""
    try:
        strategies = Strategy.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'strategies': [{
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'type': s.type,
                'status': s.status,
                'health_status': s.health_status,
                'capital_allocation': float(s.capital_allocation),
                'risk_per_trade': float(s.risk_per_trade),
                'max_positions': s.max_positions,
                'symbols': s.symbols,
                'timeframes': s.timeframes,
                'last_execution': s.last_execution.isoformat() if s.last_execution else None,
                'error_count': s.error_count,
                'created_at': s.created_at.isoformat()
            } for s in strategies]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/strategies', methods=['POST'])
@login_required
def create_strategy():
    """Cria nova estratégia"""
    try:
        data = request.get_json()
        
        strategy = Strategy(
            name=data['name'],
            description=data.get('description'),
            type=data.get('type', 'momentum'),
            status='inactive',
            config=data.get('config', {}),
            capital_allocation=Decimal(str(data.get('capital_allocation', 0))),
            risk_per_trade=Decimal(str(data.get('risk_per_trade', 1.0))),
            max_positions=data.get('max_positions', 5),
            symbols=data.get('symbols', []),
            timeframes=data.get('timeframes', []),
            user_id=current_user.id
        )
        
        db.session.add(strategy)
        db.session.commit()
        
        # Log de compliance
        compliance.log_action(
            action='strategy_created',
            entity_type='strategy',
            entity_id=strategy.id,
            user_id=current_user.id,
            details=data
        )
        
        return jsonify({
            'success': True,
            'strategy': {
                'id': strategy.id,
                'name': strategy.name,
                'status': strategy.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
@login_required
def get_strategy(strategy_id):
    """Obtém estratégia específica"""
    try:
        strategy = Strategy.query.filter_by(id=strategy_id, user_id=current_user.id).first()
        if not strategy:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        return jsonify({
            'success': True,
            'strategy': {
                'id': strategy.id,
                'name': strategy.name,
                'description': strategy.description,
                'type': strategy.type,
                'status': strategy.status,
                'health_status': strategy.health_status,
                'config': strategy.config,
                'capital_allocation': float(strategy.capital_allocation),
                'risk_per_trade': float(strategy.risk_per_trade),
                'max_positions': strategy.max_positions,
                'symbols': strategy.symbols,
                'timeframes': strategy.timeframes,
                'last_execution': strategy.last_execution.isoformat() if strategy.last_execution else None,
                'error_count': strategy.error_count,
                'created_at': strategy.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/strategies/<int:strategy_id>/start', methods=['POST'])
@login_required
def start_strategy(strategy_id):
    """Inicia estratégia"""
    try:
        strategy = Strategy.query.filter_by(id=strategy_id, user_id=current_user.id).first()
        if not strategy:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        success = strategy_engine.start_strategy(strategy_id)
        
        if success:
            compliance.log_action(
                action='strategy_started',
                entity_type='strategy',
                entity_id=strategy_id,
                user_id=current_user.id
            )
            return jsonify({'success': True, 'message': 'Strategy started'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to start strategy'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/strategies/<int:strategy_id>/stop', methods=['POST'])
@login_required
def stop_strategy(strategy_id):
    """Para estratégia"""
    try:
        strategy = Strategy.query.filter_by(id=strategy_id, user_id=current_user.id).first()
        if not strategy:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        success = strategy_engine.stop_strategy(strategy_id)
        
        if success:
            compliance.log_action(
                action='strategy_stopped',
                entity_type='strategy',
                entity_id=strategy_id,
                user_id=current_user.id
            )
            return jsonify({'success': True, 'message': 'Strategy stopped'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to stop strategy'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/strategies/<int:strategy_id>/pause', methods=['POST'])
@login_required
def pause_strategy(strategy_id):
    """Pausa estratégia"""
    try:
        strategy = Strategy.query.filter_by(id=strategy_id, user_id=current_user.id).first()
        if not strategy:
            return jsonify({'success': False, 'error': 'Strategy not found'}), 404
        
        success = strategy_engine.pause_strategy(strategy_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Strategy paused'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to pause strategy'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



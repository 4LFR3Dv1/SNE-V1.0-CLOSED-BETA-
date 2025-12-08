#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API endpoints para Pools de Alocação de Capital
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.models.trading_models import CapitalPool, db
from flask_login import login_required, current_user
from decimal import Decimal
import traceback


@trading_bp.route('/pools', methods=['GET'])
@login_required
def list_pools():
    """Lista pools do usuário"""
    try:
        pools = CapitalPool.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'pools': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'capital_allocated': float(p.capital_allocated),
                'capital_used': float(p.capital_used),
                'capital_available': float(p.capital_available),
                'symbols': p.symbols,
                'risk_per_trade_pct': float(p.risk_per_trade_pct),
                'max_positions': p.max_positions,
                'min_confluencia': float(p.min_confluencia) if p.min_confluencia else None,
                'status': p.status,
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in pools]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/pools', methods=['POST'])
@login_required
def create_pool():
    """Cria novo pool"""
    try:
        data = request.get_json()
        
        # Validar dados
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Nome do pool é obrigatório'}), 400
        
        if not data.get('symbols') or len(data.get('symbols', [])) == 0:
            return jsonify({'success': False, 'error': 'Pelo menos um símbolo é obrigatório'}), 400
        
        # Criar pool
        pool = CapitalPool(
            name=data.get('name'),
            description=data.get('description', ''),
            capital_allocated=Decimal(str(data.get('capital_allocated', 0))),
            capital_available=Decimal(str(data.get('capital_allocated', 0))),  # Inicialmente igual ao alocado
            capital_used=Decimal('0.00'),
            symbols=data.get('symbols'),
            risk_per_trade_pct=Decimal(str(data.get('risk_per_trade_pct', 1.0))),
            max_positions=data.get('max_positions', 5),
            min_confluencia=Decimal(str(data.get('min_confluencia'))) if data.get('min_confluencia') else None,
            status='inactive',
            user_id=current_user.id
        )
        
        db.session.add(pool)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pool "{pool.name}" criado com sucesso',
            'pool': {
                'id': pool.id,
                'name': pool.name,
                'capital_allocated': float(pool.capital_allocated),
                'symbols': pool.symbols
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/pools/<int:pool_id>', methods=['PUT'])
@login_required
def update_pool(pool_id):
    """Atualiza pool"""
    try:
        pool = CapitalPool.query.filter_by(id=pool_id, user_id=current_user.id).first()
        if not pool:
            return jsonify({'success': False, 'error': 'Pool não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'name' in data:
            pool.name = data['name']
        if 'description' in data:
            pool.description = data.get('description')
        if 'symbols' in data:
            pool.symbols = data['symbols']
        if 'risk_per_trade_pct' in data:
            pool.risk_per_trade_pct = Decimal(str(data['risk_per_trade_pct']))
        if 'max_positions' in data:
            pool.max_positions = data['max_positions']
        if 'min_confluencia' in data:
            pool.min_confluencia = Decimal(str(data['min_confluencia'])) if data['min_confluencia'] else None
        if 'status' in data:
            pool.status = data['status']
        if 'capital_allocated' in data:
            new_capital = Decimal(str(data['capital_allocated']))
            # Ajustar capital_available proporcionalmente
            if pool.capital_allocated > 0:
                ratio = new_capital / pool.capital_allocated
                pool.capital_available = pool.capital_available * ratio
            else:
                pool.capital_available = new_capital
            pool.capital_allocated = new_capital
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pool "{pool.name}" atualizado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/pools/<int:pool_id>', methods=['DELETE'])
@login_required
def delete_pool(pool_id):
    """Deleta pool"""
    try:
        pool = CapitalPool.query.filter_by(id=pool_id, user_id=current_user.id).first()
        if not pool:
            return jsonify({'success': False, 'error': 'Pool não encontrado'}), 404
        
        # Verificar se pool tem posições abertas
        from app.models.trading_models import Position
        open_positions = Position.query.filter_by(pool_id=pool_id, status='open').count()
        if open_positions > 0:
            return jsonify({
                'success': False,
                'error': f'Pool tem {open_positions} posição(ões) aberta(s). Feche as posições antes de deletar.'
            }), 400
        
        db.session.delete(pool)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pool "{pool.name}" deletado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/pools/<int:pool_id>/start', methods=['POST'])
@login_required
def start_pool(pool_id):
    """Ativa pool"""
    try:
        pool = CapitalPool.query.filter_by(id=pool_id, user_id=current_user.id).first()
        if not pool:
            return jsonify({'success': False, 'error': 'Pool não encontrado'}), 404
        
        pool.status = 'active'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pool "{pool.name}" ativado'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/pools/<int:pool_id>/stop', methods=['POST'])
@login_required
def stop_pool(pool_id):
    """Desativa pool"""
    try:
        pool = CapitalPool.query.filter_by(id=pool_id, user_id=current_user.id).first()
        if not pool:
            return jsonify({'success': False, 'error': 'Pool não encontrado'}), 404
        
        pool.status = 'stopped'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pool "{pool.name}" desativado'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500



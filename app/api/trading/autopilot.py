#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API endpoints para Motor Autônomo (AutoPilot)
"""

from flask import request, jsonify
from app.api.trading import trading_bp
from app.models.trading_models import TradingGlobalConfig, db
from app.services.autopilot_engine import AutoPilotEngine
from flask_login import login_required, current_user
from decimal import Decimal
import traceback

# Instância global do motor (singleton)
_autopilot_engine = None

def get_autopilot_engine():
    """Retorna instância singleton do AutoPilotEngine"""
    global _autopilot_engine
    if _autopilot_engine is None:
        _autopilot_engine = AutoPilotEngine()
    return _autopilot_engine


@trading_bp.route('/autopilot/status', methods=['GET'])
@login_required
def autopilot_status():
    """Retorna status do motor autônomo"""
    try:
        config = TradingGlobalConfig.query.filter_by(user_id=current_user.id).first()
        
        if not config:
            return jsonify({
                'success': True,
                'motor_enabled': False,
                'message': 'Configuração não encontrada. Configure o motor primeiro.'
            }), 200
        
        engine = get_autopilot_engine()
        
        return jsonify({
            'success': True,
            'motor_enabled': config.motor_enabled,
            'running': engine.running,
            'monitored_symbols': config.monitored_symbols,
            'default_timeframe': config.default_timeframe,
            'min_confluencia_global': float(config.min_confluencia_global),
            'max_risk_per_trade_pct': float(config.max_risk_per_trade_pct),
            'trade_24_7': config.trade_24_7
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/autopilot/config', methods=['GET'])
@login_required
def get_autopilot_config():
    """Retorna configuração global"""
    try:
        config = TradingGlobalConfig.query.filter_by(user_id=current_user.id).first()
        
        if not config:
            # Criar configuração padrão se não existir
            config = TradingGlobalConfig(
                user_id=current_user.id,
                monitored_symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
                default_timeframe='1h',
                min_confluencia_global=Decimal('75.00'),
                max_risk_per_trade_pct=Decimal('1.50'),
                trade_24_7=True,
                motor_enabled=False
            )
            db.session.add(config)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'config': {
                'min_confluencia_global': float(config.min_confluencia_global),
                'max_risk_per_trade_pct': float(config.max_risk_per_trade_pct),
                'monitored_symbols': config.monitored_symbols,
                'default_timeframe': config.default_timeframe,
                'trade_24_7': config.trade_24_7,
                'trading_hours_start': config.trading_hours_start.isoformat() if config.trading_hours_start else None,
                'trading_hours_end': config.trading_hours_end.isoformat() if config.trading_hours_end else None,
                'motor_enabled': config.motor_enabled
            }
        }), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/autopilot/config', methods=['PUT'])
@login_required
def update_autopilot_config():
    """Atualiza configuração global"""
    try:
        config = TradingGlobalConfig.query.filter_by(user_id=current_user.id).first()
        
        if not config:
            # Criar se não existir
            config = TradingGlobalConfig(user_id=current_user.id)
            db.session.add(config)
        
        data = request.get_json()
        
        # Atualizar campos
        if 'min_confluencia_global' in data:
            config.min_confluencia_global = Decimal(str(data['min_confluencia_global']))
        if 'max_risk_per_trade_pct' in data:
            config.max_risk_per_trade_pct = Decimal(str(data['max_risk_per_trade_pct']))
        if 'monitored_symbols' in data:
            config.monitored_symbols = data['monitored_symbols']
        if 'default_timeframe' in data:
            config.default_timeframe = data['default_timeframe']
        if 'trade_24_7' in data:
            config.trade_24_7 = data['trade_24_7']
        if 'trading_hours_start' in data:
            from datetime import time as dt_time
            if data['trading_hours_start']:
                config.trading_hours_start = dt_time.fromisoformat(data['trading_hours_start'])
            else:
                config.trading_hours_start = None
        if 'trading_hours_end' in data:
            from datetime import time as dt_time
            if data['trading_hours_end']:
                config.trading_hours_end = dt_time.fromisoformat(data['trading_hours_end'])
            else:
                config.trading_hours_end = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Configuração atualizada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/autopilot/start', methods=['POST'])
@login_required
def start_autopilot():
    """Inicia motor autônomo"""
    try:
        config = TradingGlobalConfig.query.filter_by(user_id=current_user.id).first()
        
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuração não encontrada. Configure o motor primeiro.'
            }), 400
        
        if not config.monitored_symbols or len(config.monitored_symbols) == 0:
            return jsonify({
                'success': False,
                'error': 'Nenhum símbolo configurado para monitorar. Configure símbolos primeiro.'
            }), 400
        
        engine = get_autopilot_engine()
        success = engine.start(current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Motor autônomo iniciado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Falha ao iniciar motor autônomo'
            }), 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@trading_bp.route('/autopilot/stop', methods=['POST'])
@login_required
def stop_autopilot():
    """Para motor autônomo"""
    try:
        engine = get_autopilot_engine()
        success = engine.stop(current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Motor autônomo parado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Falha ao parar motor autônomo'
            }), 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Cloud - Versão pura REST para Electron
Todas as rotas retornam JSON, nunca HTML
Proteção total de IP: código nunca sai do servidor
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from functools import wraps
import os

cloud_api = Blueprint('cloud_api', __name__, url_prefix='/api/v1')

# Importar serviços (lazy loading para evitar erros circulares)
def get_autopilot_engine():
    """Lazy import do AutoPilotEngine"""
    from app.services.autopilot_engine import AutoPilotEngine
    return AutoPilotEngine

def get_motor_renan():
    """Lazy import do motor_renan"""
    try:
        from motor_renan import analise_completa
        return analise_completa
    except ImportError:
        # Fallback para services/sne-web se não encontrar na raiz
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../services/sne-web'))
        from motor_renan import analise_completa
        return analise_completa


# ============================================================================
# HEALTH CHECK
# ============================================================================

@cloud_api.route('/health', methods=['GET'])
def health():
    """Health check - não requer autenticação"""
    return jsonify({
        'status': 'ok',
        'service': 'SNE Radar API',
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'production')
    })


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

@cloud_api.route('/auth/login', methods=['POST'])
def login():
    """Login e obtenção de token JWT"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username e password são obrigatórios'
            }), 400
        
        # Importar User aqui para evitar import circular
        from app.models.models import User, db
        import bcrypt
        
        # Buscar usuário
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Credenciais inválidas'
            }), 401
        
        # Verificar senha
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({
                'success': False,
                'error': 'Credenciais inválidas'
            }), 401
        
        # Criar token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'tier': user.tier
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cloud_api.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verificar se token é válido"""
    user_id = get_jwt_identity()
    
    from app.models.models import User
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'error': 'Usuário não encontrado'
        }), 404
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'tier': user.tier
        }
    })


# ============================================================================
# ANÁLISE
# ============================================================================

@cloud_api.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    """Análise completa de um símbolo"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        
        # Importar motor de análise
        analise_completa = get_motor_renan()
        
        # Executar análise
        resultado = analise_completa(symbol, timeframe)
        
        return jsonify({
            'success': True,
            'data': resultado,
            'symbol': symbol,
            'timeframe': timeframe
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# TRADING - AUTOPILOT
# ============================================================================

@cloud_api.route('/trading/autopilot/status', methods=['GET'])
@jwt_required()
def autopilot_status():
    """Status do AutoPilot do usuário"""
    try:
        user_id = get_jwt_identity()
        
        from app.models.trading_models import TradingGlobalConfig, CapitalPool, db
        
        # Buscar configuração global
        config = TradingGlobalConfig.query.filter_by(user_id=user_id).first()
        
        # Buscar pools
        pools = CapitalPool.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'running': config.motor_enabled if config else False,
            'config': {
                'min_confluencia': config.min_confluencia_global if config else 75.0,
                'max_risk_per_trade': config.max_risk_per_trade_pct if config else 1.5,
                'monitored_symbols': config.monitored_symbols if config else []
            },
            'pools': [
                {
                    'id': pool.id,
                    'name': pool.name,
                    'capital_allocated': float(pool.capital_allocated),
                    'capital_used': float(pool.capital_used),
                    'capital_available': float(pool.capital_available),
                    'status': pool.status,
                    'symbols': pool.symbols
                }
                for pool in pools
            ]
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cloud_api.route('/trading/autopilot/start', methods=['POST'])
@jwt_required()
def autopilot_start():
    """Iniciar AutoPilot"""
    try:
        user_id = get_jwt_identity()
        
        # Importar engine
        AutoPilotEngine = get_autopilot_engine()
        engine = AutoPilotEngine()
        engine.start()
        
        return jsonify({
            'success': True,
            'message': 'AutoPilot iniciado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cloud_api.route('/trading/autopilot/stop', methods=['POST'])
@jwt_required()
def autopilot_stop():
    """Parar AutoPilot"""
    try:
        user_id = get_jwt_identity()
        
        # Importar engine
        AutoPilotEngine = get_autopilot_engine()
        engine = AutoPilotEngine()
        engine.stop()
        
        return jsonify({
            'success': True,
            'message': 'AutoPilot parado'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# TRADING - POSIÇÕES
# ============================================================================

@cloud_api.route('/trading/positions', methods=['GET'])
@jwt_required()
def get_positions():
    """Lista posições abertas do usuário"""
    try:
        user_id = get_jwt_identity()
        
        from app.models.trading_models import Position, db
        
        positions = Position.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'positions': [
                {
                    'id': pos.id,
                    'symbol': pos.symbol,
                    'side': pos.side,
                    'quantity': float(pos.quantity),
                    'entry_price': float(pos.entry_price),
                    'current_price': float(pos.current_price) if pos.current_price else None,
                    'pnl': float(pos.pnl) if pos.pnl else 0.0,
                    'pnl_pct': float(pos.pnl_pct) if pos.pnl_pct else 0.0,
                    'leverage': float(pos.leverage) if pos.leverage else 1.0,
                    'opened_at': pos.opened_at.isoformat() if pos.opened_at else None
                }
                for pos in positions
            ]
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# TRADING - PORTFÓLIO
# ============================================================================

@cloud_api.route('/trading/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    """Informações do portfólio do usuário"""
    try:
        user_id = get_jwt_identity()
        
        from app.models.trading_models import Portfolio, db
        
        portfolio = Portfolio.query.filter_by(user_id=user_id).first()
        
        if not portfolio:
            return jsonify({
                'success': True,
                'portfolio': {
                    'total_capital': 0.0,
                    'used_capital': 0.0,
                    'available_capital': 0.0,
                    'total_pnl': 0.0,
                    'roi': 0.0
                }
            })
        
        return jsonify({
            'success': True,
            'portfolio': {
                'total_capital': float(portfolio.total_capital),
                'used_capital': float(portfolio.used_capital),
                'available_capital': float(portfolio.available_capital),
                'total_pnl': float(portfolio.total_pnl) if portfolio.total_pnl else 0.0,
                'roi': float(portfolio.roi) if portfolio.roi else 0.0,
                'updated_at': portfolio.updated_at.isoformat() if portfolio.updated_at else None
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# MARKET DATA
# ============================================================================

@cloud_api.route('/market/symbols', methods=['GET'])
@jwt_required()
def get_symbols():
    """Lista símbolos disponíveis"""
    # Lista padrão de símbolos
    symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT',
        'XRPUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT'
    ]
    
    return jsonify({
        'success': True,
        'symbols': symbols
    })


@cloud_api.route('/market/price/<symbol>', methods=['GET'])
@jwt_required()
def get_price(symbol):
    """Preço atual de um símbolo"""
    try:
        # Importar cliente Binance
        from binance.client import Client
        import os
        
        client = Client(
            api_key=os.environ.get('BINANCE_API_KEY'),
            api_secret=os.environ.get('BINANCE_SECRET_KEY')
        )
        
        ticker = client.get_symbol_ticker(symbol=symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'price': float(ticker['price'])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



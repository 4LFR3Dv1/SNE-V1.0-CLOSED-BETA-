"""
API endpoints for SNE Web
"""
from flask import request, jsonify
from . import app
from .motor import analisar_par, obter_sinal
import logging
import os

logger = logging.getLogger(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze endpoint - Usa motor_renan.py real
    Expected payload: { "symbol": "BTCUSDT", "timeframe": "15m" }
    """
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol') or data.get('pair', 'BTCUSDT')
        timeframe = data.get('timeframe', '15m')
        
        logger.info(f"Analysis requested for {symbol} on {timeframe}")
        
        # Usar motor real
        resultado = analisar_par(symbol, timeframe)
        
        if resultado.get('status') == 'error':
            return jsonify(resultado), 500
        
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Error in analyze: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/signal', methods=['GET'])
def get_signal():
    """
    Get latest signal - Usa motor_renan.py real
    Query params: ?symbol=BTCUSDT&timeframe=15m
    """
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '15m')
        
        logger.info(f"Signal requested for {symbol} on {timeframe}")
        
        # Usar motor real
        resultado = obter_sinal(symbol, timeframe)
        
        if resultado.get('status') == 'error':
            return jsonify(resultado), 500
        
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"Error in get_signal: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


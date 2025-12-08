#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask SIMPLES apenas para APIs básicas
Use este se sne_radar_web.py tiver muitas dependências
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)  # Permitir CORS para desenvolvimento
socketio = SocketIO(app, cors_allowed_origins="*")

# Health check
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'sne-web-simple',
        'version': '1.0.0'
    })

# API de análise (mock - retorna dados de exemplo)
@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Análise técnica (mock)"""
    return jsonify({
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'signal': 'BUY',
        'confluence_score': 8.5,
        'message': 'API mock - Use sne_radar_web.py para análise real'
    })

# API de sinal (mock)
@app.route('/api/signal')
def signal():
    """Obter sinal (mock)"""
    symbol = request.args.get('symbol', 'BTCUSDT')
    timeframe = request.args.get('timeframe', '1h')
    
    return jsonify({
        'symbol': symbol,
        'timeframe': timeframe,
        'signal': 'BUY',
        'score': 8.5,
        'message': 'API mock - Use sne_radar_web.py para análise real'
    })

# WebSocket básico
@socketio.on('connect')
def handle_connect():
    print('✅ Cliente conectado')
    socketio.emit('status', {'message': 'Conectado ao SNE Web'})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Cliente desconectado')

if __name__ == '__main__':
    print("🚀 Servidor Flask SIMPLES iniciado!")
    print("🌐 Frontend: http://localhost:5173")
    print("🌐 Backend:  http://localhost:9999")
    print("")
    print("⚠️  Este é um servidor MOCK - use sne_radar_web.py para funcionalidades completas")
    print("")
    socketio.run(app, host='0.0.0.0', port=9999, debug=True)


#!/usr/bin/env python3
"""
Servidor Flask para receber webhooks do Telegram
"""

import sys
import os
import json
from flask import Flask, request, jsonify

# Adicionar o diretório atual ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint para receber webhooks do Telegram
    """
    try:
        # Obter dados do webhook
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        print(f"📨 Webhook recebido: {json.dumps(update_data, indent=2)}")
        
        # Processar update
        from xenos_bot import processar_webhook_update
        processar_webhook_update(update_data)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de health check
    """
    return jsonify({'status': 'ok', 'message': 'SNE Radar Bot Webhook Server'}), 200

@app.route('/', methods=['GET'])
def index():
    """
    Página inicial
    """
    return """
    <h1>🤖 SNE Radar Bot - Webhook Server</h1>
    <p>Servidor ativo e funcionando!</p>
    <p>Webhook endpoint: <code>/webhook</code></p>
    <p>Health check: <code>/health</code></p>
    """

def main():
    print("🚀 INICIANDO SERVIDOR WEBHOOK")
    print("=" * 40)
    
    try:
        print("✅ Servidor Flask configurado")
        print("🌐 Endpoints disponíveis:")
        print("   • /webhook - Receber webhooks do Telegram")
        print("   • /health - Health check")
        print("   • / - Página inicial")
        print("\n🔄 Iniciando servidor...")
        print("⚠️  Pressione Ctrl+C para parar")
        
        # Executar servidor
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
        
    except KeyboardInterrupt:
        print("\n✅ Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

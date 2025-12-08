"""
API endpoints para Trading Automatizado
"""

# Usar routes.py como blueprint principal (com mocks funcionais)
# Os outros arquivos (strategies.py, execution.py, etc) serão integrados depois
try:
    from app.api.trading.routes import trading_bp
    
    # Importar rotas de pools e autopilot
    try:
        from app.api.trading import pools
        from app.api.trading import autopilot
    except ImportError as e:
        print(f"⚠️ Algumas rotas de trading não puderam ser importadas: {e}")
        
except ImportError:
    # Fallback: criar blueprint básico se routes.py não existir
    from flask import Blueprint
    trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')
    
    @trading_bp.route('/status', methods=['GET'])
    def status():
        from flask import jsonify
        return jsonify({"status": "online"})


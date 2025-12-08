"""
API Blueprints
"""

from app.api.trading import trading_bp


def register_blueprints(app):
    """Registra todos os blueprints"""
    app.register_blueprint(trading_bp)



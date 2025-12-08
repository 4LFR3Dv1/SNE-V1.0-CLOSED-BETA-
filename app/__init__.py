"""
SNE Radar - Backend Application
Estrutura modular para separação gradual do código
"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

__version__ = "1.0.0"

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

# JWT (opcional, para API cloud)
jwt = None
try:
    from flask_jwt_extended import JWTManager
    jwt = JWTManager()
except ImportError:
    pass


def create_app(config_name='default'):
    """
    Factory function para criar Flask app
    Suporta tanto modo web tradicional quanto API cloud pura
    """
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sne_radar.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT para API cloud
    if jwt:
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
        jwt.init_app(app)
    
    # CORS - permitir requisições do Electron
    CORS(app, origins=['*'], supports_credentials=True)
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # Importar modelos
    from app.models import models
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar user loader
    from app.models.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app


def register_blueprints(app):
    """Registra todos os blueprints"""
    
    # API Cloud (para Electron)
    try:
        from app.api.cloud_api import cloud_api
        app.register_blueprint(cloud_api)
        print("✅ Cloud API registrada")
    except ImportError as e:
        print(f"⚠️ Cloud API não disponível: {e}")
    
    # APIs tradicionais (se existirem)
    try:
        from app.api.trading import trading_bp
        app.register_blueprint(trading_bp)
    except ImportError:
        pass
    
    try:
        from app.routes.pages import pages_bp
        app.register_blueprint(pages_bp)
    except ImportError:
        pass
    
    try:
        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        pass

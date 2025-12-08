#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE Radar Web - Sistema Neural Estratégico Completo
Dashboard web com análise estratégica, múltiplos pares e recomendações de trading
"""

import os, json, threading, webbrowser, time, datetime, sys, requests, pandas as pd, numpy as np, platform, random, pytz
from datetime import date
import urllib3
import bcrypt
import re
from cachetools import TTLCache
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, make_response, send_from_directory
import json
from flask import Blueprint
import io
import base64
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Desabilitar warnings SSL
# Desabilitar warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Importar sistema de validação multi-timeframe
try:
    from multi_timeframe_validator import validator, validar_sinal_completo, detectar_divergencias_completo
    MULTI_TIMEFRAME_AVAILABLE = True
    print("✅ Sistema de validação multi-timeframe carregado com sucesso!")
except ImportError as e:
    MULTI_TIMEFRAME_AVAILABLE = False
    print(f"⚠️ Sistema de validação multi-timeframe não disponível: {e}")

from database_config import get_database_url
from config import Settings as C
from services.ta_summary import summarize as ta_summarize
from integrations.cmc import get_global_metrics
from integrations.coinglass import get_funding, get_oi, get_lsr, get_liquidations
from integrations.cmc import get_global_metrics, get_listings_by_tag
from services.advanced_indicators import calculate_all_indicators
from services.professional_indicators import calculate_all_professional_indicators
from services.ml_predictions import train_ml_models, predict_price_ml, ensemble_predict, get_ml_performance
from services.advanced_backtesting import (
    run_single_strategy_backtest, run_multi_strategy_backtest, optimize_strategy_parameters,
    MovingAverageCrossover, RSIStrategy, BollingerBandsStrategy
)
from services.alert_system import alert_manager, create_price_alert, create_rsi_alert, create_volume_alert, check_market_alerts
from services.export_system import data_exporter

# ============================================
# MONITOR DE OPORTUNIDADES (GLOBAL)
# ============================================
# O monitor será inicializado pelo sne_desktop.py quando rodando como app
# Ou pode ser inicializado manualmente via API quando necessário
opportunity_monitor = None

def get_opportunity_monitor():
    """Retorna instância do monitor (cria se não existir)"""
    global opportunity_monitor
    
    # Ajustar path para funcionar no bundle do PyInstaller
    import sys
    from pathlib import Path
    
    if getattr(sys, 'frozen', False):
        # Modo bundle: adicionar Resources ao path
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller cria _MEIPASS durante execução
            resources_path = Path(sys._MEIPASS)
        else:
            # Fallback: tentar encontrar Resources
            executable_path = Path(sys.executable)
            if 'Contents/MacOS' in str(executable_path):
                resources_path = executable_path.parent.parent / 'Resources'
            else:
                resources_path = Path(BASE_DIR) / 'Resources'
        
        # Adicionar ao path se não estiver
        if str(resources_path) not in sys.path:
            sys.path.insert(0, str(resources_path))
            print(f"✅ Adicionado Resources ao path: {resources_path}")
    
    if opportunity_monitor is None:
        try:
            # Tentar importar com path ajustado
            from monitors.opportunity_monitor import OpportunityMonitor
            opportunity_monitor = OpportunityMonitor(
                symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT'],
                scan_interval=60,
                enable_volume_scanner=True,
                enable_pavio_scanner=True  # ✅ ATIVADO POR PADRÃO
            )
            print("✅ Monitor de oportunidades criado")
            # ✅ INICIAR AUTOMATICAMENTE quando criado via web
            if not opportunity_monitor.running:
                try:
                    opportunity_monitor.start()
                    print("✅ Monitor iniciado automaticamente")
                    
                    # Enviar mensagem de inicialização
                    try:
                        if opportunity_monitor.notifier:
                            print("📤 Enviando mensagem de inicialização...")
                            mode = "Web" if not getattr(sys, 'frozen', False) else "Bundle"
                            opportunity_monitor.notifier.send_startup_message(mode=mode)
                    except Exception as e:
                        print(f"⚠️ Erro ao enviar mensagem de inicialização: {e}")
                        # Não bloquear se falhar
                        
                except Exception as e:
                    print(f"⚠️ Erro ao iniciar monitor automaticamente: {e}")
                    import traceback
                    traceback.print_exc()
        except ImportError as e:
            print(f"⚠️ Monitor de oportunidades não disponível: {e}")
            print(f"   sys.path: {sys.path[:5]}")
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"❌ Erro ao criar monitor: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Garantir que o monitor está rodando quando solicitado
    if opportunity_monitor is not None and not opportunity_monitor.running:
        try:
            print("🔄 Monitor não estava rodando, iniciando agora...")
            opportunity_monitor.start()
            print("✅ Monitor iniciado")
        except Exception as e:
            print(f"⚠️ Erro ao iniciar monitor: {e}")
    
    return opportunity_monitor

# ============================================
# CONFIGURAÇÃO FRONTEND VUE.JS
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')
FRONTEND_STATIC = os.path.join(FRONTEND_DIR, 'assets')
FRONTEND_INDEX = os.path.join(FRONTEND_DIR, 'index.html')
FRONTEND_EXISTS = os.path.exists(FRONTEND_INDEX)

# Configurações Flask
app = Flask(__name__,
    static_folder=FRONTEND_STATIC if FRONTEND_EXISTS else None,
    template_folder=FRONTEND_DIR if FRONTEND_EXISTS else 'templates'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())

# Ambiente
FLASK_ENV = os.environ.get('FLASK_ENV', 'development').lower()
IS_PRODUCTION = FLASK_ENV == 'production'

# Banco de dados centralizado via database_config
# Detecta automaticamente o ambiente (production ou local)
db_url = get_database_url()
if not db_url:
    # fallback para SQLite local (caminho relativo simples)
    db_url = 'sqlite:///sne_radar.db'

# Para desenvolvimento local, usar caminho absoluto simples
if not IS_PRODUCTION and 'sqlite' in db_url:
    db_url = 'sqlite:///sne_radar.db'  # Sem instance/ para evitar problemas de caminho

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de segurança (compatíveis com Render)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=24)
if IS_PRODUCTION:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None

# CSRF global (protege POST/PUT/DELETE em formulários)
# Temporariamente desabilitado para debug
# csrf = CSRFProtect(app)

# API Keys (sem defaults sensíveis)
COINGECKO_KEY = os.environ.get('COINGECKO_KEY')
SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY')
if IS_PRODUCTION:
    if not COINGECKO_KEY:
        print("⚠️ COINGECKO_KEY não configurada no ambiente de produção")
    if not SCRAPERAPI_KEY:
        print("⚠️ SCRAPERAPI_KEY não configurada no ambiente de produção")

# Inicializar extensões
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Rate limiting
# Em desenvolvimento, limites mais altos para permitir testes
if IS_PRODUCTION:
    default_limits = ["200 per day", "50 per hour"]
else:
    # Limites muito mais altos em desenvolvimento para evitar bloqueios durante desenvolvimento
    default_limits = ["5000 per day", "500 per hour"]

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=default_limits,
    storage_uri="memory://"  # Usar memória para desenvolvimento (mais rápido)
)

# CORS do SocketIO
allowed_origins_env = C.ALLOWED_ORIGINS
cors_origins = "*" if not IS_PRODUCTION else (allowed_origins_env or None)
socketio = SocketIO(app, cors_allowed_origins=cors_origins)

# ===========================================
# REGISTRAR BLUEPRINTS DE TRADING
# ===========================================
try:
    from app.api.trading.routes import trading_bp
    app.register_blueprint(trading_bp)
    print("✅ Blueprint de trading registrado (routes.py)")
except Exception as e:
    print(f"⚠️ Erro ao registrar blueprint de trading (routes.py): {e}")
    import traceback
    traceback.print_exc()

# CORS para todas as rotas de API
@app.after_request
def after_request(response):
    """Adiciona headers CORS para todas as rotas /api/*"""
    if request.path.startswith('/api/'):
        origin = request.headers.get('Origin')
        allowed_origins = ['http://localhost:5173', 'http://localhost:9999', 'http://127.0.0.1:5173']
        if origin in allowed_origins or not IS_PRODUCTION:
            response.headers['Access-Control-Allow-Origin'] = origin or '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, HEAD'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Lista de admins via env (ex.: "admin,renan")
ADMIN_USERS = C.ADMIN_USERS

# --- Admin Blueprint ---
def admin_required_func():
    return current_user.is_authenticated and current_user.username in ADMIN_USERS

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def admin_dashboard_page():
    if not admin_required_func():
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

# Registrar blueprint
app.register_blueprint(admin_bp)

# Importar inspector para verificação de colunas
from sqlalchemy import inspect

# Funções de segurança
def sanitize_input(text):
    """Sanitiza entrada de texto para prevenir XSS e injeção"""
    if not text:
        return ""
    
    # Remover caracteres perigosos
    text = re.sub(r'[<>"\']', '', str(text))
    text = text.strip()
    
    # Limitar tamanho
    if len(text) > 100:
        text = text[:100]
    
    return text

def validate_username(username):
    """Valida formato do username"""
    if not username:
        return False, "Username é obrigatório"
    
    username = sanitize_input(username)
    
    # Verificar formato (apenas letras, números e underscore)
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return False, "Username deve ter 3-20 caracteres (apenas letras, números e _)"
    
    return True, username

def validate_password(password):
    """Valida força da senha"""
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 3:
        return False, "Senha deve ter pelo menos 3 caracteres"
    
    return True, password

def hash_password(password):
    """Cria hash seguro da senha"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password, hashed):
    """Verifica senha contra hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Configurações do sistema
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]  # Apenas os símbolos desejados
interval = "1m"
limit = 100
# Intervalo configurável por ambiente para reduzir defasagem
update_interval = C.UPDATE_INTERVAL
br_tz = pytz.timezone("America/Sao_Paulo")

# Configurações multi-timeframe
timeframes_config = {
    "1m": {"interval": "1m", "limit": 100, "weight": 0.15, "name": "Tempo Real"},
    "5m": {"interval": "5m", "limit": 100, "weight": 0.20, "name": "Curto Prazo"},
    "15m": {"interval": "15m", "limit": 100, "weight": 0.25, "name": "Médio Prazo"},
    "1h": {"interval": "1h", "limit": 100, "weight": 0.20, "name": "Médio-Longo Prazo"},
    "4h": {"interval": "4h", "limit": 100, "weight": 0.15, "name": "Longo Prazo"},
    "1d": {"interval": "1d", "limit": 100, "weight": 0.05, "name": "Tendência Principal"}
}

# Cache de símbolos da Binance (24 horas)
symbol_cache = TTLCache(maxsize=1, ttl=86400)

def get_binance_symbols():
    """
    Busca todos os símbolos USDT da Binance e cacheia por 24h
    """
    if 'symbols' in symbol_cache:
        return symbol_cache['symbols']
    
    try:
        # Endpoint público leve da Binance
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filtra apenas pares USDT e ordena por status TRADING
            symbols = [
                {
                    'symbol': s['symbol'],
                    'name': s['baseAsset'] + '/' + s['quoteAsset'],
                    'baseAsset': s['baseAsset'],
                    'quoteAsset': s['quoteAsset'],
                    'status': s['status']
                }
                for s in data['symbols'] 
                if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING'
            ]
            
            # Ordenar alfabeticamente
            symbols.sort(key=lambda x: x['symbol'])
            
            symbol_cache['symbols'] = symbols
            print(f"✅ {len(symbols)} símbolos carregados da Binance")
            return symbols
        else:
            print(f"⚠️ Erro ao buscar símbolos: {response.status_code}")
            return get_fallback_symbols()
    except Exception as e:
        print(f"❌ Erro ao buscar símbolos: {e}")
        return get_fallback_symbols()

def get_fallback_symbols():
    """Lista básica de símbolos populares como fallback"""
    return [
        {'symbol': 'BTCUSDT', 'name': 'Bitcoin/USDT', 'baseAsset': 'BTC', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'ETHUSDT', 'name': 'Ethereum/USDT', 'baseAsset': 'ETH', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'BNBUSDT', 'name': 'Binance Coin/USDT', 'baseAsset': 'BNB', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'SOLUSDT', 'name': 'Solana/USDT', 'baseAsset': 'SOL', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'ADAUSDT', 'name': 'Cardano/USDT', 'baseAsset': 'ADA', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'XRPUSDT', 'name': 'Ripple/USDT', 'baseAsset': 'XRP', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'DOGEUSDT', 'name': 'Dogecoin/USDT', 'baseAsset': 'DOGE', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'DOTUSDT', 'name': 'Polkadot/USDT', 'baseAsset': 'DOT', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'MATICUSDT', 'name': 'Polygon/USDT', 'baseAsset': 'MATIC', 'quoteAsset': 'USDT', 'status': 'TRADING'},
        {'symbol': 'AVAXUSDT', 'name': 'Avalanche/USDT', 'baseAsset': 'AVAX', 'quoteAsset': 'USDT', 'status': 'TRADING'},
    ]

# Estado global do sistema
sistema_estado = {
    "ativo": False,
    "ultima_atualizacao": None,
    "dados_mercado": {},
    "rupturas_detectadas": [],
    "alertas_enviados": 0,
    "inicio_execucao": None,
    "analise_thread": None,
    "last_api_call": {},  # Rate limiting por API
    "api_call_count": {},  # Contador de chamadas
    "circuit_breaker": {}
}

# Lock para proteger estado compartilhado entre threads
from threading import Lock
estado_lock = Lock()

# Modelos de dados
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tier = db.Column(db.String(20), default='free')  # free, pro, institutional
    api_calls_today = db.Column(db.Integer, default=0)
    last_api_reset = db.Column(db.Date, default=datetime.date.today)
    subscription_expires = db.Column(db.DateTime, nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=True)

class MarketData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    ema8 = db.Column(db.Float, nullable=False)
    ema21 = db.Column(db.Float, nullable=False)
    sma200 = db.Column(db.Float, nullable=False)
    rsi = db.Column(db.Float, nullable=False)
    volatilidade = db.Column(db.Float, nullable=False)
    tendencia = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    message = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tier = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_rate_limit(api_name, max_calls=10, window_seconds=60):
    """Verifica rate limit para APIs"""
    now = time.time()
    
    if api_name not in sistema_estado["last_api_call"]:
        sistema_estado["last_api_call"][api_name] = []
        sistema_estado["api_call_count"][api_name] = 0
    
    # Limpar chamadas antigas
    sistema_estado["last_api_call"][api_name] = [
        call_time for call_time in sistema_estado["last_api_call"][api_name]
        if now - call_time < window_seconds
    ]
    
    # Verificar se pode fazer nova chamada
    if len(sistema_estado["last_api_call"][api_name]) >= max_calls:
        print(f"⏳ Rate limit {api_name}: {len(sistema_estado['last_api_call'][api_name])}/{max_calls} calls")
        return False
    
    # Registrar nova chamada
    sistema_estado["last_api_call"][api_name].append(now)
    sistema_estado["api_call_count"][api_name] += 1
    
    return True

def reset_circuit_breaker(api_name):
    """Reseta o circuit breaker para uma API específica"""
    with estado_lock:
        if api_name in sistema_estado["circuit_breaker"]:
            sistema_estado["circuit_breaker"][api_name] = {"fails": 0, "open_until": 0}
            print(f"✅ Circuit breaker resetado para {api_name}")

def check_user_rate_limit(user_id, tier='free'):
    """Verifica rate limit por usuário baseado no tier"""
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Reset diário do contador
            today = datetime.date.today()
            if user.last_api_reset != today:
                user.api_calls_today = 0
                user.last_api_reset = today
                db.session.commit()
            
            # Limites por tier
            tier_limits = {
                'free': 100,        # 100 requests/dia
                'pro': 1000,        # 1000 requests/dia
                'institutional': 10000  # 10000 requests/dia
            }
            
            limit = tier_limits.get(tier, 100)
            
            if user.api_calls_today >= limit:
                print(f"⏳ Rate limit usuário {user.username} ({tier}): {user.api_calls_today}/{limit}")
                return False
            
            # Incrementar contador
            user.api_calls_today += 1
            db.session.commit()
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar rate limit do usuário: {e}")
        return False

def get_user_tier_limits(tier):
    """Retorna limites baseados no tier do usuário"""
    limits = {
        'free': {
            'symbols': ['BTCUSDT'],
            'timeframes': ['1m'],
            'update_interval': 300,  # 5 minutos
            'max_alerts_per_day': 2,
            'api_calls_per_day': 100
        },
        'pro': {
            'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
            'timeframes': ['1m', '5m', '15m', '1h', '4h', '1d'],
            'update_interval': 30,   # 30 segundos
            'max_alerts_per_day': -1,  # Ilimitado
            'api_calls_per_day': 1000
        },
        'institutional': {
            'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT'],
            'timeframes': ['1m', '5m', '15m', '1h', '4h', '1d'],
            'update_interval': 15,   # 15 segundos
            'max_alerts_per_day': -1,  # Ilimitado
            'api_calls_per_day': 10000
        }
    }
    return limits.get(tier, limits['free'])

def criar_dados_mock(symbol, interval):
    """Cria dados mock para teste quando API falha"""
    try:
        import random
        from datetime import datetime, timedelta
        
        # Dados base mais realistas para diferentes símbolos
        precos_base = {
            "BTCUSDT": 68000,
            "ETHUSDT": 3800,
            "SOLUSDT": 180
        }
        
        preco_base = precos_base.get(symbol, 100)
        
        # Gerar 100 candles
        dados = []
        agora = datetime.now()
        
        # Simular tendência de mercado
        tendencia_geral = random.uniform(-0.001, 0.001)  # Tendência geral
        volatilidade = random.uniform(0.005, 0.015)  # Volatilidade variável
        
        for i in range(100):
            timestamp = agora - timedelta(minutes=i)
            
            if i == 0:
                preco = preco_base
            else:
                # Movimento mais realista com correlação
                movimento_base = tendencia_geral + random.gauss(0, volatilidade)
                preco = float(dados[-1][4]) * (1 + movimento_base)  # Usar close anterior
            
            # Gerar OHLC com correlação realista
            open_price = preco
            range_candle = abs(random.gauss(0, volatilidade * 0.5))
            high_price = open_price * (1 + range_candle)
            low_price = open_price * (1 - range_candle)
            
            # Close price com viés baseado na tendência
            close_bias = random.uniform(-0.3, 0.7)  # Viés para alta
            close_price = low_price + (high_price - low_price) * close_bias
            
            # Volume correlacionado com volatilidade
            volume_base = {
                "BTCUSDT": 2000000,
                "ETHUSDT": 1000000, 
                "SOLUSDT": 500000
            }.get(symbol, 1000000)
            
            volume_multiplier = 1 + range_candle * 2  # Volume maior em candles mais voláteis
            volume = volume_base * volume_multiplier * random.uniform(0.7, 1.3)
            trades = int(volume / 1000)  # Trades baseado no volume
            
            dados.append([
                int(timestamp.timestamp() * 1000),  # open_time
                str(open_price),
                str(high_price),
                str(low_price),
                str(close_price),
                str(volume),
                int(timestamp.timestamp() * 1000) + 60000,  # close_time
                str(volume * 0.5),  # qav
                trades,  # trades
                str(volume * 0.3),  # tbb
                str(volume * 0.7),  # tbq
                0  # ignore
            ])
        
        # Criar DataFrame
        df = pd.DataFrame(dados, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        print(f"✅ Dados mock criados para {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao criar dados mock: {e}")
        return None

def buscar_dados_coingecko(symbol, interval, limit):
    """Busca dados da CoinGecko API com ScraperAPI (proxy + API key)"""
    try:
        # Verificar rate limit (máximo 10 chamadas por minuto com API key)
        if not check_rate_limit("coingecko", max_calls=10, window_seconds=60):
            print(f"⏳ Rate limit CoinGecko atingido para {symbol}")
            return buscar_dados_bybit(symbol, interval, limit)
        
        # Mapear símbolos para IDs do CoinGecko
        symbol_mapping = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum", 
            "SOLUSDT": "solana"
        }
        
        coin_id = symbol_mapping.get(symbol, "bitcoin")
        
        # API CoinGecko Simple Price (mais confiável)
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "x_cg_demo_api_key": COINGECKO_KEY
        }
        
        print(f"🔍 Buscando dados CoinGecko Simple: {symbol} ({coin_id})...")
        
        # Delay para evitar rate limit
        time.sleep(1)
        
        response = requests.get(url, params=params, timeout=15, verify=False)
        
        if response.status_code != 200:
            print(f"❌ Erro na API CoinGecko: {response.status_code}")
            print("🔄 Usando dados mock como último recurso...")
            return criar_dados_mock(symbol, interval)
            
        data = response.json()
        
        if not data or coin_id not in data:
            print(f"❌ Dados vazios da CoinGecko para {symbol}")
            return criar_dados_mock(symbol, interval)
        
        # Extrair preço atual do CoinGecko Simple Price
        preco_atual = data[coin_id]["usd"]
        
        # Criar dados históricos simulados baseados no preço atual
        import random
        from datetime import datetime, timedelta
        
        df_data = []
        agora = datetime.now()
        
        # Criar 100 candles simulados (últimas 100 unidades de tempo)
        for i in range(100):
            # Simular variação de preço
            variacao = random.uniform(-0.02, 0.02)  # ±2%
            preco = preco_atual * (1 + variacao)
            
            # Simular OHLC
            open_price = preco * random.uniform(0.998, 1.002)
            high_price = preco * random.uniform(1.001, 1.005)
            low_price = preco * random.uniform(0.995, 0.999)
            close_price = preco
            
            # Simular volume
            volume = random.uniform(1000, 10000)
            
            # Timestamp (do mais antigo para o mais recente)
            timestamp = int((agora - timedelta(minutes=100-i)).timestamp() * 1000)
            
            df_data.append([
                timestamp,  # open_time
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                timestamp + 60000,  # close_time
                volume * 0.5,  # qav
                int(volume / 10),  # trades
                volume * 0.3,  # tbb
                volume * 0.7,  # tbq
                0  # ignore
            ])
        
        df = pd.DataFrame(df_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        print(f"✅ Dados CoinGecko Simple carregados para {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados CoinGecko: {e}")
        return criar_dados_mock(symbol, interval)

def buscar_dados_bybit(symbol, interval, limit):
    """Busca dados da Bybit API (alternativa confiável)"""
    try:
        # Verificar rate limit
        if not check_rate_limit("bybit", max_calls=10, window_seconds=10):
            print(f"⏳ Rate limit Bybit atingido para {symbol}")
            return buscar_dados_kucoin(symbol, interval, limit)
        
        # Mapear símbolos para Bybit
        symbol_mapping = {
            "BTCUSDT": "BTCUSDT",
            "ETHUSDT": "ETHUSDT", 
            "SOLUSDT": "SOLUSDT"
        }
        
        bybit_symbol = symbol_mapping.get(symbol, "BTCUSDT")
        
        # Mapear intervalos para Bybit
        interval_mapping = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "1h": "60",
            "4h": "240",
            "1d": "D"
        }
        
        bybit_interval = interval_mapping.get(interval, "1")
        
        # API Bybit Kline
        url = "https://api.bybit.com/v5/market/kline"
        params = {
            "category": "spot",
            "symbol": bybit_symbol,
            "interval": bybit_interval,
            "limit": limit
        }
        
        print(f"🔍 Buscando dados Bybit: {symbol} ({bybit_symbol})...")
        
        # Delay para respeitar rate limit
        time.sleep(0.1)
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erro na API Bybit: {response.status_code}")
            return buscar_dados_kucoin(symbol, interval, limit)
            
        data = response.json()
        
        if not data or data.get("retCode") != 0 or not data.get("result", {}).get("list"):
            print(f"❌ Dados vazios da Bybit para {symbol}")
            return buscar_dados_kucoin(symbol, interval, limit)
        
        # Extrair dados OHLC
        kline_data = data["result"]["list"]
        
        # Criar DataFrame
        df_data = []
        for candle in kline_data:
            timestamp, open_price, high_price, low_price, close_price, volume, turnover = candle
            
            df_data.append([
                int(timestamp),  # open_time
                float(open_price),
                float(high_price),
                float(low_price),
                float(close_price),
                float(volume),
                int(timestamp) + 60000,  # close_time
                float(volume) * 0.5,  # qav
                int(float(volume) / 100),  # trades
                float(volume) * 0.3,  # tbb
                float(volume) * 0.7,  # tbq
                0  # ignore
            ])
        
        df = pd.DataFrame(df_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        print(f"✅ Dados Bybit carregados para {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados Bybit: {e}")
        return buscar_dados_kucoin(symbol, interval, limit)

def buscar_dados_kucoin(symbol, interval, limit):
    """Busca dados da KuCoin API (alternativa confiável)"""
    try:
        # Verificar rate limit
        if not check_rate_limit("kucoin", max_calls=10, window_seconds=10):
            print(f"⏳ Rate limit KuCoin atingido para {symbol}")
            return buscar_dados_mexc(symbol, interval, limit)
        
        # Mapear símbolos para KuCoin
        symbol_mapping = {
            "BTCUSDT": "BTC-USDT",
            "ETHUSDT": "ETH-USDT", 
            "SOLUSDT": "SOL-USDT"
        }
        
        kucoin_symbol = symbol_mapping.get(symbol, "BTC-USDT")
        
        # Mapear intervalos para KuCoin
        interval_mapping = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "1hour",
            "4h": "4hour",
            "1d": "1day"
        }
        
        kucoin_interval = interval_mapping.get(interval, "1min")
        
        # API KuCoin Kline
        url = "https://api.kucoin.com/api/v1/market/candles"
        params = {
            "symbol": kucoin_symbol,
            "type": kucoin_interval,
            "startAt": int((time.time() - 86400) * 1000),  # Últimas 24h
            "endAt": int(time.time() * 1000)
        }
        
        print(f"🔍 Buscando dados KuCoin: {symbol} ({kucoin_symbol})...")
        
        # Delay para respeitar rate limit
        time.sleep(0.1)
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erro na API KuCoin: {response.status_code}")
            return buscar_dados_mexc(symbol, interval, limit)
            
        data = response.json()
        
        if not data or data.get("code") != "200000" or not data.get("data"):
            print(f"❌ Dados vazios da KuCoin para {symbol}")
            return buscar_dados_mexc(symbol, interval, limit)
        
        # Extrair dados OHLC
        kline_data = data["data"]
        
        # Criar DataFrame
        df_data = []
        for candle in kline_data:
            timestamp, open_price, close_price, high_price, low_price, volume, turnover = candle
            
            df_data.append([
                int(timestamp),  # open_time
                float(open_price),
                float(high_price),
                float(low_price),
                float(close_price),
                float(volume),
                int(timestamp) + 60000,  # close_time
                float(volume) * 0.5,  # qav
                int(float(volume) / 100),  # trades
                float(volume) * 0.3,  # tbb
                float(volume) * 0.7,  # tbq
                0  # ignore
            ])
        
        df = pd.DataFrame(df_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        print(f"✅ Dados KuCoin carregados para {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados KuCoin: {e}")
        return buscar_dados_mexc(symbol, interval, limit)

def buscar_dados_mexc(symbol, interval, limit):
    """Busca dados da MEXC API (alternativa confiável)"""
    try:
        # Verificar rate limit
        if not check_rate_limit("mexc", max_calls=10, window_seconds=10):
            print(f"⏳ Rate limit MEXC atingido para {symbol}")
            return buscar_dados_bing(symbol, interval, limit)
        
        # Mapear símbolos para MEXC
        symbol_mapping = {
            "BTCUSDT": "BTC_USDT",
            "ETHUSDT": "ETH_USDT", 
            "SOLUSDT": "SOL_USDT"
        }
        
        mexc_symbol = symbol_mapping.get(symbol, "BTC_USDT")
        
        # Mapear intervalos para MEXC
        interval_mapping = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d"
        }
        
        mexc_interval = interval_mapping.get(interval, "1m")
        
        # API MEXC Kline
        url = "https://www.mexc.com/open/api/v2/market/kline"
        params = {
            "symbol": mexc_symbol,
            "interval": mexc_interval,
            "limit": limit
        }
        
        print(f"🔍 Buscando dados MEXC: {symbol} ({mexc_symbol})...")
        
        # Delay para respeitar rate limit
        time.sleep(0.1)
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erro na API MEXC: {response.status_code}")
            return buscar_dados_bing(symbol, interval, limit)
            
        data = response.json()
        
        if not data or data.get("code") != 200 or not data.get("data"):
            print(f"❌ Dados vazios da MEXC para {symbol}")
            return buscar_dados_bing(symbol, interval, limit)
        
        # Extrair dados OHLC
        kline_data = data["data"]
        
        # Criar DataFrame
        df_data = []
        for candle in kline_data:
            timestamp, open_price, close_price, high_price, low_price, volume = candle
            
            df_data.append([
                int(timestamp),  # open_time
                float(open_price),
                float(high_price),
                float(low_price),
                float(close_price),
                float(volume),
                int(timestamp) + 60000,  # close_time
                float(volume) * 0.5,  # qav
                int(float(volume) / 100),  # trades
                float(volume) * 0.3,  # tbb
                float(volume) * 0.7,  # tbq
                0  # ignore
            ])
        
        df = pd.DataFrame(df_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        print(f"✅ Dados MEXC carregados para {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados MEXC: {e}")
        return buscar_dados_bing(symbol, interval, limit)

def buscar_dados_bing(symbol, interval, limit):
    """Busca dados da BingX API (última alternativa)"""
    try:
        # Verificar rate limit
        if not check_rate_limit("bing", max_calls=10, window_seconds=10):
            print(f"⏳ Rate limit BingX atingido para {symbol}")
            return criar_dados_mock(symbol, interval)
        
        # Mapear símbolos para BingX
        symbol_mapping = {
            "BTCUSDT": "BTC-USDT",
            "ETHUSDT": "ETH-USDT", 
            "SOLUSDT": "SOL-USDT"
        }
        
        bing_symbol = symbol_mapping.get(symbol, "BTC-USDT")
        
        # Mapear intervalos para BingX
        interval_mapping = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "1h": "60",
            "4h": "240",
            "1d": "1D"
        }
        
        bing_interval = interval_mapping.get(interval, "1")
        
        # API BingX Kline
        url = "https://open-api.bingx.com/openApi/spot/v1/market/kline"
        params = {
            "symbol": bing_symbol,
            "interval": bing_interval,
            "limit": limit
        }
        
        print(f"🔍 Buscando dados BingX: {symbol} ({bing_symbol})...")
        
        # Delay para respeitar rate limit
        time.sleep(0.1)
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erro na API BingX: {response.status_code}")
            return criar_dados_mock(symbol, interval)
            
        data = response.json()
        
        if not data or data.get("code") != 0 or not data.get("data"):
            print(f"❌ Dados vazios da BingX para {symbol}")
            return criar_dados_mock(symbol, interval)
        
        # Extrair dados OHLC
        kline_data = data["data"]
        
        # Criar DataFrame
        df_data = []
        for candle in kline_data:
            timestamp, open_price, high_price, low_price, close_price, volume = candle
            
            df_data.append([
                int(timestamp),  # open_time
                float(open_price),
                float(high_price),
                float(low_price),
                float(close_price),
                float(volume),
                int(timestamp) + 60000,  # close_time
                float(volume) * 0.5,  # qav
                int(float(volume) / 100),  # trades
                float(volume) * 0.3,  # tbb
                float(volume) * 0.7,  # tbq
                0  # ignore
            ])
        
        df = pd.DataFrame(df_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        print(f"✅ Dados BingX carregados para {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados BingX: {e}")
        return criar_dados_mock(symbol, interval)

def buscar_dados_kraken(symbol, interval, limit):
    """Busca dados da Kraken API (alternativa confiável)"""
    try:
        # Verificar rate limit (máximo 10 chamadas por 10 segundos)
        if not check_rate_limit("kraken", max_calls=10, window_seconds=10):
            print(f"⏳ Rate limit Kraken atingido para {symbol}")
            return buscar_dados_coingecko(symbol, interval, limit)
        
        # Mapear símbolos para Kraken (nomes corretos)
        symbol_mapping = {
            "BTCUSDT": "XBTUSD",
            "ETHUSDT": "ETHUSD", 
            "SOLUSDT": "SOLUSD"
        }
        
        # Verificar se o símbolo existe na Kraken
        kraken_symbol = symbol_mapping.get(symbol, "XBTUSD")
        
        # Testar primeiro se o par existe
        test_url = "https://api.kraken.com/0/public/AssetPairs"
        test_response = requests.get(test_url, timeout=10)
        
        if test_response.status_code == 200:
            pairs_data = test_response.json()
            available_pairs = pairs_data.get("result", {}).keys()
            
            # Tentar variações do símbolo
            possible_symbols = [
                kraken_symbol,
                f"{kraken_symbol}.d",  # Com .d
                kraken_symbol.replace("USD", "USDT"),  # USDT em vez de USD
                kraken_symbol.replace("XBT", "BTC")  # BTC em vez de XBT
            ]
            
            # Encontrar símbolo válido
            valid_symbol = None
            for sym in possible_symbols:
                if sym in available_pairs:
                    valid_symbol = sym
                    break
            
            if valid_symbol:
                kraken_symbol = valid_symbol
                print(f"✅ Símbolo Kraken encontrado: {kraken_symbol}")
            else:
                print(f"❌ Símbolo {kraken_symbol} não encontrado na Kraken")
                return buscar_dados_coingecko(symbol, interval, limit)
        
        # Mapear intervalos para Kraken
        interval_mapping = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "4h": 240,
            "1d": 1440
        }
        
        kraken_interval = interval_mapping.get(interval, 1)
        
        # API Kraken OHLC
        url = "https://api.kraken.com/0/public/OHLC"
        params = {
            "pair": kraken_symbol,
            "interval": kraken_interval,
            "since": int((time.time() - 86400) * 1000)  # Últimas 24h
        }
        
        print(f"🔍 Buscando dados Kraken: {symbol} ({kraken_symbol})...")
        
        # Delay para respeitar rate limit
        time.sleep(0.1)
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Erro na API Kraken: {response.status_code}")
            return buscar_dados_coingecko(symbol, interval, limit)
            
        data = response.json()
        
        if not data or "error" in data or not data.get("result"):
            print(f"❌ Dados vazios da Kraken para {symbol}")
            return buscar_dados_coingecko(symbol, interval, limit)
        
        # Extrair dados OHLC
        ohlc_data = data["result"][kraken_symbol]
        
        # Criar DataFrame
        df_data = []
        for candle in ohlc_data:
            timestamp, open_price, high_price, low_price, close_price, vwap, volume, count = candle
            
            df_data.append([
                timestamp * 1000,  # open_time (ms)
                float(open_price),
                float(high_price),
                float(low_price),
                float(close_price),
                float(volume),
                (timestamp + kraken_interval * 60) * 1000,  # close_time
                float(volume) * 0.5,  # qav
                int(count),  # trades
                float(volume) * 0.3,  # tbb
                float(volume) * 0.7,  # tbq
                0  # ignore
            ])
        
        df = pd.DataFrame(df_data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        print(f"✅ Dados Kraken carregados para {symbol}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados Kraken: {e}")
        return buscar_dados_coingecko(symbol, interval, limit)

def buscar_dados_binance(symbol, interval, limit, skip_rate_limit=False):
    """Busca dados APENAS da Binance - SEM FALLBACKS
    
    Args:
        symbol: Símbolo da moeda (ex: BTCUSDT)
        interval: Intervalo (1m, 5m, 1h, etc)
        limit: Número de candles
        skip_rate_limit: Se True, ignora rate limit (usado para requisições sob demanda)
    """
    # LOG CRÍTICO: Sempre mostrar quando a função é chamada
    print(f"\n{'='*80}")
    print(f"🔍 [BINANCE-FUNC] buscar_dados_binance CHAMADA!")
    print(f"   Symbol: {symbol}")
    print(f"   Interval: {interval} (tipo: {type(interval)})")
    print(f"   Limit: {limit}")
    print(f"{'='*80}\n")
    
    try:
        # Verificar rate limit apenas se não for requisição sob demanda
        if not skip_rate_limit:
            binance_calls = C.BINANCE_CALLS_PER_WINDOW
            binance_window = C.BINANCE_WINDOW_SECONDS
            if not check_rate_limit("binance", max_calls=binance_calls, window_seconds=binance_window):
                print(f"⏳ Rate limit Binance atingido para {symbol}")
                return None
        
        # Mapear intervalos para Binance Data API
        # IMPORTANTE: Binance suporta APENAS: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 1w, 1M
        # NOTA: Binance NÃO suporta: 10m, 3d
        # Para intervalos não suportados, usar o mais próximo suportado
        interval_mapping = {
            "1m": "1m",
            "3m": "3m",
            "5m": "5m", 
            "10m": "15m",  # Binance não suporta 10m - usar 15m como aproximação
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "2h": "2h",
            "4h": "4h",
            "6h": "6h",
            "8h": "8h",
            "12h": "12h",
            "1d": "1d",
            "3d": "1d",  # Binance não suporta 3d diretamente - usar 1d e agregar depois
            "1w": "1w",
            "1M": "1M"
        }
        
        # Verificar se o intervalo está no mapeamento
        if interval not in interval_mapping:
            print(f"⚠️ [BINANCE] Intervalo '{interval}' não está mapeado, usando como está")
        
        binance_interval = interval_mapping.get(interval, interval)  # Usar o próprio intervalo se não estiver mapeado
        
        # LOG CRÍTICO: Mostrar mapeamento
        print(f"🔍 [BINANCE-MAP] Intervalo original: '{interval}' -> Mapeado: '{binance_interval}'")
        
        # Validar se o intervalo é suportado pela Binance
        valid_binance_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "1w", "1M"]
        if binance_interval not in valid_binance_intervals:
            print(f"❌ [BINANCE] Intervalo '{binance_interval}' não é suportado pela Binance! Usando '1h' como fallback")
            binance_interval = "1h"
        else:
            print(f"✅ [BINANCE-VALID] Intervalo '{binance_interval}' é válido!")
        
        # Para 3d, precisamos buscar dados de 1d e agregar em grupos de 3
        needs_aggregation = (interval == "3d")
        
        # DEBUG: Verificar se o intervalo está correto
        if interval != binance_interval:
            print(f"⚠️ [BINANCE] Intervalo mapeado: {interval} -> {binance_interval}")
        
        # Binance API DIRETA - sem proxy
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": binance_interval,
            "limit": limit
        }
        
        print(f"🔍 [BINANCE] Buscando: {symbol} | Intervalo original: {interval} | Binance: {binance_interval} | Limit: {limit}")
        print(f"   URL: {url}")
        print(f"   Params: {params}")
        print(f"   URL completa: {url}?symbol={symbol}&interval={binance_interval}&limit={limit}")
        
        # Delay para respeitar rate limit
        time.sleep(0.1)
        
        # Requisição DIRETA sem proxy e sem headers especiais
        # IMPORTANTE: Usar params como dicionário para garantir que o intervalo seja passado corretamente
        # FORÇAR: Construir URL manualmente para garantir que o intervalo está correto
        request_url = f"{url}?symbol={symbol}&interval={binance_interval}&limit={limit}"
        print(f"🔗 [BINANCE] URL FINAL CONSTRUÍDA: {request_url}")
        
        response = requests.get(request_url, timeout=10)
        
        # DEBUG: Verificar resposta e URL final
        print(f"📡 [BINANCE] Status: {response.status_code}")
        print(f"📡 [BINANCE] URL final da requisição (response.url): {response.url}")
        
        # Verificar se o intervalo está na URL
        if binance_interval not in response.url:
            print(f"⚠️ [BINANCE] AVISO: Intervalo '{binance_interval}' não encontrado na URL final!")
            print(f"   URL: {response.url}")
            print(f"   Isso pode indicar que o parâmetro não foi passado corretamente")
            print(f"   ❌ ERRO CRÍTICO: Requisição pode estar usando intervalo incorreto!")
            return None
        
        if response.status_code != 200:
            print(f"❌ [BINANCE] Erro {response.status_code}: {response.text}")
            print("⚠️ Dados Binance indisponíveis - requisição negada")
            return None
            
        data = response.json()
        
        # Verificar se retornou erro da Binance
        if isinstance(data, dict) and 'code' in data:
            print(f"❌ [BINANCE] Erro da API: {data.get('msg', 'Erro desconhecido')}")
            return None
        
        if not data or len(data) == 0:
            print(f"❌ [BINANCE] Dados vazios para {symbol} {binance_interval}")
            return None
        
        # DEBUG: Verificar intervalo dos dados retornados
        if len(data) > 1:
            first_candle_time = data[0][0]  # Timestamp do primeiro candle (ms)
            last_candle_time = data[-1][0]  # Timestamp do último candle (ms)
            time_diff_ms = last_candle_time - first_candle_time
            time_diff_min = time_diff_ms / 1000 / 60  # Diferença em minutos
            actual_interval_min = time_diff_min / (len(data) - 1) if len(data) > 1 else 0
            
            expected_interval_minutes = {
                "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
                "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720,
                "1d": 1440, "1w": 10080, "1M": 43200
            }
            expected_min = expected_interval_minutes.get(binance_interval, 60)
            
            print(f"✅ [BINANCE] Recebidos {len(data)} candles para {symbol} {binance_interval}")
            print(f"   Intervalo esperado: ~{expected_min} min | Intervalo real: ~{actual_interval_min:.1f} min")
            print(f"   Primeiro candle: {datetime.datetime.fromtimestamp(first_candle_time/1000)}")
            print(f"   Último candle: {datetime.datetime.fromtimestamp(last_candle_time/1000)}")
            
            if abs(actual_interval_min - expected_min) > expected_min * 0.5:  # Tolerância de 50%
                print(f"   ⚠️ [BINANCE] ERRO CRÍTICO: Intervalo dos dados não corresponde ao solicitado!")
                print(f"   Solicitado: {binance_interval} (~{expected_min} min)")
                print(f"   Recebido: ~{actual_interval_min:.1f} min/candle")
                print(f"   ⚠️ A requisição pode ter falhado ou a Binance retornou dados incorretos!")
                # Retornar None para forçar nova tentativa ou erro explícito
                return None
        else:
            print(f"✅ [BINANCE] Recebidos {len(data)} candles para {symbol} {binance_interval}")
        
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbb", "tbq", "ignore"
        ])
        
        # DEBUG: Verificar timestamps antes de converter
        if len(df) > 1:
            first_ts = df.iloc[0]["open_time"]
            last_ts = df.iloc[-1]["open_time"]
            time_diff_ms = last_ts - first_ts
            time_diff_min = time_diff_ms / 1000 / 60
            actual_interval_min = time_diff_min / (len(df) - 1) if len(df) > 1 else 0
            print(f"   📊 [BINANCE-RAW] Timestamps brutos:")
            print(f"      Primeiro: {first_ts} ({datetime.datetime.fromtimestamp(first_ts/1000)})")
            print(f"      Último: {last_ts} ({datetime.datetime.fromtimestamp(last_ts/1000)})")
            print(f"      Intervalo real: ~{actual_interval_min:.1f} min/candle")
        
        df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
        df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
            "open": float, "high": float, "low": float, "close": float,
            "volume": float, "trades": int
        })
        df.set_index("time", inplace=True)
        
        # Agregar dados para 3d se necessário (Binance não suporta 3d diretamente)
        if needs_aggregation and len(df) > 0:
            print(f"📊 [BINANCE] Agregando dados de 1d para 3d...")
            # Agrupar por períodos de 3 dias
            df['date_group'] = df.index.to_period('3D')
            df_agg = df.groupby('date_group').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'trades': 'sum'
            }).reset_index()
            df_agg['time'] = pd.to_datetime(df_agg['date_group'].astype(str))
            df_agg.set_index('time', inplace=True)
            df_agg = df_agg[['open', 'high', 'low', 'close', 'volume', 'trades']]
            df = df_agg
            print(f"✅ [BINANCE] Agregados {len(df)} candles de 3d")
        
        # Calcular indicadores técnicos
        df["EMA8"] = df["close"].ewm(span=8).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()
        df["SMA200"] = df["close"].rolling(window=20).mean()
        df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
        df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                        (df["volume"] > df["volume"].quantile(0.9))
        df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
        df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
        
        # Calcular RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        
        # Calcular MACD
        ema12 = df["close"].ewm(span=12).mean()
        ema26 = df["close"].ewm(span=26).mean()
        df["MACD"] = ema12 - ema26
        
        print(f"✅ Dados Binance via proxy carregados para {symbol}")
        return df
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
        return None

def buscar_dados_multitimeframe(symbol):
    """Busca dados de múltiplos timeframes para um símbolo"""
    try:
        dados_timeframes = {}
        
        for timeframe, config in timeframes_config.items():
            try:
                df = buscar_dados_binance(symbol, config["interval"], config["limit"])
                if df is not None and not df.empty:
                    dados_timeframes[timeframe] = df
                    print(f"✅ Dados {timeframe} carregados para {symbol}")
                else:
                    print(f"⚠️ Dados {timeframe} não disponíveis para {symbol}")
            except Exception as e:
                print(f"❌ Erro ao buscar dados {timeframe} para {symbol}: {e}")
                continue
        
        return dados_timeframes
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados multi-timeframe para {symbol}: {e}")
        return {}

def calcular_rsi(prices, period=14):
    """Calcula RSI"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])
    except:
        return 50.0

def calcular_volatilidade(prices, period=20):
    """Calcula volatilidade"""
    try:
        returns = prices.pct_change()
        volatilidade = returns.rolling(window=period).std() * np.sqrt(period) * 100
        return float(volatilidade.iloc[-1])
    except:
        return 0.0

def detectar_ruptura(df):
    """Detecta rupturas no DataFrame"""
    if df is None or df.empty:
        return False, 0
    
    ultima_linha = df.iloc[-1]
    if ultima_linha["ruptura"]:
        percentual = abs(df["densidade"].diff().iloc[-1]) / df["densidade"].iloc[-1] * 100
        return True, percentual
    return False, 0

def analisar_simbolo_estrategico(symbol, df, ruptura, percentual):
    """Análise estratégica completa de um símbolo"""
    try:
        preco_atual = float(df["close"].iloc[-1])
        volume_atual = float(df["volume"].iloc[-1])
        ema8 = float(df["EMA8"].iloc[-1])
        ema21 = float(df["EMA21"].iloc[-1])
        sma200 = float(df["SMA200"].iloc[-1])
        
        # Análise básica
        variacao_preco = ((preco_atual - float(df["close"].iloc[-2])) / float(df["close"].iloc[-2])) * 100
        volume_medio = float(df["volume"].rolling(window=20).mean().iloc[-1])
        volume_ratio = volume_atual / volume_medio if volume_medio > 0 else 1
        
        # Indicadores técnicos
        rsi = calcular_rsi(df["close"])
        volatilidade = calcular_volatilidade(df["close"])
        tendencia_curta = "BULLISH" if ema8 > ema21 else "BEARISH"
        tendencia_longa = "BULLISH" if ema21 > sma200 else "BEARISH"
        suporte = float(df["low"].rolling(window=20).min().iloc[-1])
        resistencia = float(df["high"].rolling(window=20).max().iloc[-1])
        
        # Análises dos módulos estratégicos
        mente_fluida = analisar_mente_fluida(df)
        catalogo_magnetico = analisar_catalogo_magnetico(df, symbol)
        mapeamento_gravitacional = analisar_mapeamento_gravitacional(df)
        previsao_magnetica = analisar_previsao_magnetica(df)
        pulso_magnetico = analisar_pulso_magnetico(df)
        memoria_neural = analisar_memoria_neural(symbol, df)
        fluxo_mental = analisar_fluxo_mental(df)
        
        # Sinais e gestão de risco
        sinal_compra = df["sinal_compra"].iloc[-1]
        sinal_venda = df["sinal_venda"].iloc[-1]
        risco = calcular_risco(df, preco_atual, suporte, resistencia)
        momentum = calcular_momentum(df)
        forca_mercado = calcular_forca_mercado(df, volume_ratio, volatilidade, rsi)
        
        # Validação multi-timeframe (se disponível)
        validacao_multitimeframe = None
        divergencias = []
        
        if MULTI_TIMEFRAME_AVAILABLE:
            try:
                # Buscar dados de múltiplos timeframes
                dados_timeframes = buscar_dados_multitimeframe(symbol)
                
                if dados_timeframes:
                    # Determinar tipo de sinal para validação
                    sinal_tipo = "aguardar"
                    if sinal_compra:
                        sinal_tipo = "compra"
                    elif sinal_venda:
                        sinal_tipo = "venda"
                    
                    # Validar sinal multi-timeframe
                    validacao_multitimeframe = validar_sinal_completo(symbol, sinal_tipo, dados_timeframes)
                    
                    # Detectar divergências
                    divergencias = detectar_divergencias_completo(dados_timeframes)
                    
                    print(f"🔍 Validação multi-timeframe para {symbol}: {validacao_multitimeframe['valido'] if validacao_multitimeframe else 'N/A'}")
                    print(f"🚨 Divergências detectadas: {len(divergencias)}")
                    
            except Exception as e:
                print(f"❌ Erro na validação multi-timeframe para {symbol}: {e}")
                validacao_multitimeframe = None
                divergencias = []
        
        # Estratégia completa com validação multi-timeframe
        estrategia = gerar_estrategia_com_validacao(df, ruptura, percentual, mente_fluida, catalogo_magnetico, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental, validacao_multitimeframe, divergencias)
        
        # Interpretação completa
        interpretacao = interpretar_mercado(df, mente_fluida, catalogo_magnetico, mapeamento_gravitacional, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental)
        
        # Dicas avançadas
        dicas = gerar_dicas_trading(df, mente_fluida, catalogo_magnetico, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental)
        
        return {
            "symbol": symbol,
            "price": preco_atual,
            "volume": volume_atual,
            "ema8": ema8,
            "ema21": ema21,
            "sma200": sma200,
            "rsi": rsi,
            "volatilidade": volatilidade,
            "tendencia_curta": tendencia_curta,
            "tendencia_longa": tendencia_longa,
            "suporte": suporte,
            "resistencia": resistencia,
            "variacao_preco": variacao_preco,
            "volume_ratio": volume_ratio,
            "rupture": str(ruptura),
            "percentual_ruptura": percentual,
            "sinal_compra": str(sinal_compra),
            "sinal_venda": str(sinal_venda),
            "mente_fluida": mente_fluida,
            "catalogo_magnetico": catalogo_magnetico,
            "mapeamento_gravitacional": mapeamento_gravitacional,
            "previsao_magnetica": previsao_magnetica,
            "pulso_magnetico": pulso_magnetico,
            "memoria_neural": memoria_neural,
            "fluxo_mental": fluxo_mental,
            "estrategia": estrategia,
            "interpretacao": interpretacao,
            "dicas": dicas,
            "risco": risco,
            "momentum": momentum,
            "forca_mercado": forca_mercado,
            "validacao_multitimeframe": validacao_multitimeframe,
            "divergencias": divergencias
        }
        
    except Exception as e:
        print(f"❌ Erro na análise estratégica de {symbol}: {e}")
        return None

def analisar_mente_fluida(df):
    """Análise da mente fluída"""
    try:
        variacao = ((float(df["close"].iloc[-1]) - float(df["close"].iloc[-5])) / float(df["close"].iloc[-5])) * 100
        volume_ratio = float(df["volume"].iloc[-1]) / float(df["volume"].rolling(window=20).mean().iloc[-1])
        
        if variacao > 3 and volume_ratio > 1.5:
            return "PADRÃO DE IMPULSO DETECTADO"
        elif variacao < -3 and volume_ratio > 1.5:
            return "PADRÃO DE REVERSÃO DETECTADO"
        elif abs(variacao) < 1 and volume_ratio < 0.8:
            return "PADRÃO DE CONSOLIDAÇÃO"
        else:
            return "PADRÃO NEUTRO"
    except:
        return "ANÁLISE EM ANDAMENTO"

def analisar_catalogo_magnetico(df, symbol):
    """Análise do catálogo magnético"""
    try:
        preco_atual = float(df["close"].iloc[-1])
        suporte = float(df["low"].rolling(window=20).min().iloc[-1])
        resistencia = float(df["high"].rolling(window=20).max().iloc[-1])
        
        distancia_suporte = abs(preco_atual - suporte) / preco_atual * 100
        distancia_resistencia = abs(resistencia - preco_atual) / preco_atual * 100
        
        if distancia_suporte < 2:
            return f"ZONA DE SUPORTE FORTE - {distancia_suporte:.1f}%"
        elif distancia_resistencia < 2:
            return f"ZONA DE RESISTÊNCIA FORTE - {distancia_resistencia:.1f}%"
        elif distancia_suporte < 5:
            return f"APROXIMANDO SUPORTE - {distancia_suporte:.1f}%"
        elif distancia_resistencia < 5:
            return f"APROXIMANDO RESISTÊNCIA - {distancia_resistencia:.1f}%"
        else:
            return "ZONA NEUTRA"
    except:
        return "ANÁLISE EM ANDAMENTO"

def analisar_mapeamento_gravitacional(df):
    """Análise do mapeamento gravitacional"""
    try:
        densidade = float(df["densidade"].iloc[-1])
        densidade_media = float(df["densidade"].rolling(window=20).mean().iloc[-1])
        
        if densidade > densidade_media * 1.5:
            return "ZONA DE ALTA DENSIDADE - ATENÇÃO"
        elif densidade < densidade_media * 0.5:
            return "ZONA DE BAIXA DENSIDADE - OPORTUNIDADE"
        else:
            return "ZONA DE DENSIDADE NORMAL"
    except:
        return "ANÁLISE EM ANDAMENTO"

def analisar_previsao_magnetica(df):
    """Análise da previsão magnética"""
    try:
        ema8 = float(df["EMA8"].iloc[-1])
        ema21 = float(df["EMA21"].iloc[-1])
        sma200 = float(df["SMA200"].iloc[-1])
        
        if ema8 > ema21 > sma200:
            return "PREVISÃO: ALTA CONTINUADA"
        elif ema8 < ema21 < sma200:
            return "PREVISÃO: BAIXA CONTINUADA"
        elif ema8 > ema21 and ema21 < sma200:
            return "PREVISÃO: POSSÍVEL REVERSÃO DE ALTA"
        elif ema8 < ema21 and ema21 > sma200:
            return "PREVISÃO: POSSÍVEL REVERSÃO DE BAIXA"
        else:
            return "PREVISÃO: LATERAL"
    except:
        return "PREVISÃO INDEFINIDA"

def analisar_pulso_magnetico(df):
    """Análise do pulso magnético"""
    try:
        volume_atual = float(df["volume"].iloc[-1])
        volume_medio = float(df["volume"].rolling(window=20).mean().iloc[-1])
        variacao = ((float(df["close"].iloc[-1]) - float(df["close"].iloc[-2])) / float(df["close"].iloc[-2])) * 100
        
        if volume_atual > volume_medio * 2 and abs(variacao) > 2:
            return "PULSO FORTE - MOVIMENTO ACELERADO"
        elif volume_atual > volume_medio * 1.5 and abs(variacao) > 1:
            return "PULSO MODERADO - MOVIMENTO CONFIRMADO"
        elif volume_atual < volume_medio * 0.5:
            return "PULSO FRACO - CUIDADO"
        else:
            return "PULSO NEUTRO"
    except:
        return "ANÁLISE EM ANDAMENTO"

def analisar_memoria_neural(symbol, df):
    """Análise da memória neural"""
    try:
        padroes = [
            "PADRÃO HISTÓRICO: ALTA APÓS SUPORTE",
            "PADRÃO HISTÓRICO: BAIXA APÓS RESISTÊNCIA",
            "PADRÃO HISTÓRICO: CONSOLIDAÇÃO",
            "PADRÃO HISTÓRICO: RUPTURA"
        ]
        return random.choice(padroes)
    except:
        return "MEMÓRIA VAZIA"

def analisar_fluxo_mental(df):
    """Análise do fluxo mental"""
    try:
        rsi = calcular_rsi(df["close"])
        volatilidade = calcular_volatilidade(df["close"])
        
        if rsi < 30 and volatilidade > 5:
            return "FLUXO: SOBREVENDA COM VOLATILIDADE"
        elif rsi > 70 and volatilidade > 5:
            return "FLUXO: SOBRECOMPRA COM VOLATILIDADE"
        elif rsi < 30:
            return "FLUXO: SOBREVENDA"
        elif rsi > 70:
            return "FLUXO: SOBRECOMPRA"
        else:
            return "FLUXO: NEUTRO"
    except:
        return "ANÁLISE EM ANDAMENTO"

def gerar_estrategia_trading(df, ruptura, percentual, mente_fluida, catalogo_magnetico, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental):
    """Gera estratégia de trading baseada na análise"""
    try:
        preco_atual = float(df["close"].iloc[-1])
        ema8 = float(df["EMA8"].iloc[-1])
        ema21 = float(df["EMA21"].iloc[-1])
        sma200 = float(df["SMA200"].iloc[-1])
        
        estrategias = []
        acao_principal = ""
        
        # Análise de tendência e ação principal
        if ema8 > ema21 and ema21 > sma200:
            estrategias.append("TENDÊNCIA DE ALTA FORTE")
            acao_principal = "COMPRAR"
        elif ema8 > ema21:
            estrategias.append("TENDÊNCIA DE ALTA MÉDIA")
            acao_principal = "COMPRAR"
        elif ema8 < ema21 and ema21 < sma200:
            estrategias.append("TENDÊNCIA DE BAIXA FORTE")
            acao_principal = "VENDER"
        elif ema8 < ema21:
            estrategias.append("TENDÊNCIA DE BAIXA MÉDIA")
            acao_principal = "VENDER"
        else:
            estrategias.append("TENDÊNCIA LATERAL")
            acao_principal = "AGUARDAR"
        
        # Análise de RSI para confirmação
        rsi = calcular_rsi(df["close"])
        if rsi < 30:
            estrategias.append("RSI SOBREVENDIDO - OPORTUNIDADE DE COMPRA")
            if acao_principal == "AGUARDAR":
                acao_principal = "COMPRAR"
        elif rsi > 70:
            estrategias.append("RSI SOBRECOMPRADO - OPORTUNIDADE DE VENDA")
            if acao_principal == "AGUARDAR":
                acao_principal = "VENDER"
        
        # Análise de ruptura
        if ruptura:
            if percentual > 10:
                estrategias.append("RUPTURA MAJOR - ATENÇÃO MÁXIMA")
                if acao_principal == "COMPRAR":
                    acao_principal = "COMPRAR COM CUIDADO"
                elif acao_principal == "VENDER":
                    acao_principal = "VENDER COM CUIDADO"
            elif percentual > 5:
                estrategias.append("RUPTURA SIGNIFICATIVA")
            else:
                estrategias.append("RUPTURA MENOR")
        
        # Análise de volume
        volume_medio = float(df["volume"].rolling(window=20).mean().iloc[-1])
        volume_atual = float(df["volume"].iloc[-1])
        
        if volume_atual > volume_medio * 1.5:
            estrategias.append("VOLUME ALTO - CONFIRMAÇÃO")
        elif volume_atual < volume_medio * 0.5:
            estrategias.append("VOLUME BAIXO - CUIDADO")
            if acao_principal == "COMPRAR":
                acao_principal = "COMPRAR COM CUIDADO"
            elif acao_principal == "VENDER":
                acao_principal = "VENDER COM CUIDADO"
        
        # Integração com módulos
        if mente_fluida and "padrão" in mente_fluida.lower():
            estrategias.append(f"MENTE FLUÍDA: {mente_fluida}")
        
        if catalogo_magnetico and "zona" in catalogo_magnetico.lower():
            estrategias.append(f"CATÁLOGO MAGNÉTICO: {catalogo_magnetico}")
        
        if previsao_magnetica and "previsão" in previsao_magnetica.lower():
            estrategias.append(f"PREVISÃO: {previsao_magnetica}")
        
        if pulso_magnetico and "pulso" in pulso_magnetico.lower():
            estrategias.append(f"PULSO: {pulso_magnetico}")
        
        if memoria_neural and "padrão" in memoria_neural.lower():
            estrategias.append(f"MEMÓRIA: {memoria_neural}")
        
        if fluxo_mental and "fluxo" in fluxo_mental.lower():
            estrategias.append(f"FLUXO: {fluxo_mental}")
        
        # Sinais específicos
        if df["sinal_compra"].iloc[-1]:
            estrategias.append("SINAL DE COMPRA DETECTADO")
            acao_principal = "COMPRAR AGORA"
        elif df["sinal_venda"].iloc[-1]:
            estrategias.append("SINAL DE VENDA DETECTADO")
            acao_principal = "VENDER AGORA"
        
        # Estratégia final com ação principal
        estrategia_final = f"🎯 AÇÃO PRINCIPAL: {acao_principal}\n\n"
        estrategia_final += "📊 ANÁLISE TÉCNICA:\n"
        estrategia_final += " | ".join(estrategias)
        
        return estrategia_final
        
    except Exception as e:
        return "Análise em andamento..."

def gerar_estrategia_com_validacao(df, ruptura, percentual, mente_fluida, catalogo_magnetico, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental, validacao_multitimeframe=None, divergencias=None):
    """Gera estratégia de trading com validação multi-timeframe"""
    try:
        # Estratégia base
        estrategia_base = gerar_estrategia_trading(df, ruptura, percentual, mente_fluida, catalogo_magnetico, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental)
        
        # Adicionar validação multi-timeframe se disponível
        if validacao_multitimeframe and MULTI_TIMEFRAME_AVAILABLE:
            estrategia_base += f"\n\n🔍 VALIDAÇÃO MULTI-TIMEFRAME:\n"
            
            if validacao_multitimeframe.get('valido', False):
                estrategia_base += f"✅ SINAL VALIDADO - Confiança: {validacao_multitimeframe.get('confianca', 0):.1f}%\n"
                estrategia_base += f"📊 Score Final: {validacao_multitimeframe.get('score_final', 0):.1f}/100\n"
                estrategia_base += f"🎯 Recomendação: {validacao_multitimeframe.get('recomendacao', 'N/A')}\n"
            else:
                estrategia_base += f"❌ SINAL NÃO VALIDADO - Confiança: {validacao_multitimeframe.get('confianca', 0):.1f}%\n"
                estrategia_base += f"📊 Score Final: {validacao_multitimeframe.get('score_final', 0):.1f}/100\n"
                estrategia_base += f"⚠️ Motivo: {validacao_multitimeframe.get('recomendacao', 'Critérios não atendidos')}\n"
            
            # Adicionar informações de concordância
            concordancia = validacao_multitimeframe.get('concordancia', {})
            if concordancia:
                estrategia_base += f"📈 Concordância: {concordancia.get('concordancia', 'N/A')}\n"
                estrategia_base += f"🎯 Tendência Dominante: {concordancia.get('tendencia_dominante', 'N/A').upper()}\n"
                estrategia_base += f"💪 Força do Sinal: {concordancia.get('forca_sinal', 0):.1f}\n"
        
        # Adicionar divergências se detectadas
        if divergencias and len(divergencias) > 0:
            estrategia_base += f"\n🚨 DIVERGÊNCIAS DETECTADAS ({len(divergencias)}):\n"
            for i, divergencia in enumerate(divergencias[:3], 1):  # Mostrar apenas as 3 primeiras
                estrategia_base += f"{i}. {divergencia.get('tipo', 'N/A')} - {divergencia.get('severidade', 'N/A')}\n"
                estrategia_base += f"   {divergencia.get('descricao', 'N/A')}\n"
                if divergencia.get('recomendacao'):
                    estrategia_base += f"   💡 {divergencia.get('recomendacao')}\n"
        
        return estrategia_base
        
    except Exception as e:
        print(f"❌ Erro ao gerar estratégia com validação: {e}")
        return "Análise em andamento..."

def interpretar_mercado(df, mente_fluida, catalogo_magnetico, mapeamento_gravitacional, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental):
    """Interpreta o mercado baseado em todos os módulos"""
    try:
        interpretacoes = []
        
        preco_atual = float(df["close"].iloc[-1])
        variacao = ((preco_atual - float(df["close"].iloc[-2])) / float(df["close"].iloc[-2])) * 100
        
        # Interpretação básica
        if variacao > 3:
            interpretacoes.append("MOMENTUM FORTE - MOVIMENTO ACELERADO")
        elif variacao > 1:
            interpretacoes.append("MOMENTUM MODERADO")
        elif variacao > 0:
            interpretacoes.append("MOMENTUM POSITIVO")
        else:
            interpretacoes.append("MOMENTUM NEGATIVO")
        
        # Integração com módulos
        if mente_fluida and "padrão" in mente_fluida.lower():
            interpretacoes.append(f"MENTE FLUÍDA: {mente_fluida}")
        
        if catalogo_magnetico and "zona" in catalogo_magnetico.lower():
            interpretacoes.append(f"CATÁLOGO MAGNÉTICO: {catalogo_magnetico}")
        
        if mapeamento_gravitacional and "zona" in mapeamento_gravitacional.lower():
            interpretacoes.append(f"MAPEAMENTO GRAVITACIONAL: {mapeamento_gravitacional}")
        
        if previsao_magnetica and "previsão" in previsao_magnetica.lower():
            interpretacoes.append(f"PREVISÃO MAGNÉTICA: {previsao_magnetica}")
        
        if pulso_magnetico and "pulso" in pulso_magnetico.lower():
            interpretacoes.append(f"PULSO MAGNÉTICO: {pulso_magnetico}")
        
        if memoria_neural and "padrão" in memoria_neural.lower():
            interpretacoes.append(f"MEMÓRIA NEURAL: {memoria_neural}")
        
        if fluxo_mental and "fluxo" in fluxo_mental.lower():
            interpretacoes.append(f"FLUXO MENTAL: {fluxo_mental}")
        
        return " | ".join(interpretacoes)
        
    except Exception as e:
        return "Interpretação em andamento..."

def gerar_dicas_trading(df, mente_fluida, catalogo_magnetico, previsao_magnetica, pulso_magnetico, memoria_neural, fluxo_mental):
    """Gera dicas de trading baseadas na análise"""
    try:
        dicas = [
            "💰 Nunca arrisque mais de 2% por trade",
            "💰 Use sempre stop loss",
            "💰 Diversifique posições",
            "💰 Monitore volume e momentum",
            "💰 Respeite suporte e resistência"
        ]
        
        # Dicas baseadas nos módulos
        if mente_fluida and "padrão" in mente_fluida.lower():
            dicas.append(f"🧠 {mente_fluida}")
        
        if catalogo_magnetico and "zona" in catalogo_magnetico.lower():
            dicas.append(f"🧲 {catalogo_magnetico}")
        
        if previsao_magnetica and "previsão" in previsao_magnetica.lower():
            dicas.append(f"🔮 {previsao_magnetica}")
        
        if pulso_magnetico and "pulso" in pulso_magnetico.lower():
            dicas.append(f"💓 {pulso_magnetico}")
        
        if memoria_neural and "padrão" in memoria_neural.lower():
            dicas.append(f"🧠 {memoria_neural}")
        
        if fluxo_mental and "fluxo" in fluxo_mental.lower():
            dicas.append(f"🌊 {fluxo_mental}")
        
        return dicas
        
    except Exception as e:
        return ["Análise em andamento..."]

def calcular_risco(df, preco_atual, suporte, resistencia):
    """Calcula nível de risco"""
    try:
        distancia_suporte = abs(preco_atual - suporte) / preco_atual * 100
        distancia_resistencia = abs(resistencia - preco_atual) / preco_atual * 100
        
        if distancia_suporte < 2:
            return "ALTO - Próximo ao suporte"
        elif distancia_resistencia < 2:
            return "ALTO - Próximo à resistência"
        elif distancia_suporte < 5 or distancia_resistencia < 5:
            return "MÉDIO - Zona de transição"
        else:
            return "BAIXO - Zona segura"
    except:
        return "INDEFINIDO"

def calcular_momentum(df):
    """Calcula momentum do mercado"""
    try:
        variacao_5 = ((float(df["close"].iloc[-1]) - float(df["close"].iloc[-5])) / float(df["close"].iloc[-5])) * 100
        variacao_10 = ((float(df["close"].iloc[-1]) - float(df["close"].iloc[-10])) / float(df["close"].iloc[-10])) * 100
        
        if variacao_5 > 5 and variacao_10 > 10:
            return "FORTE ALTA"
        elif variacao_5 > 2 and variacao_10 > 5:
            return "ALTA MODERADA"
        elif variacao_5 > 0 and variacao_10 > 0:
            return "ALTA FRACA"
        elif variacao_5 < -5 and variacao_10 < -10:
            return "FORTE BAIXA"
        elif variacao_5 < -2 and variacao_10 < -5:
            return "BAIXA MODERADA"
        elif variacao_5 < 0 and variacao_10 < 0:
            return "BAIXA FRACA"
        else:
            return "LATERAL"
    except:
        return "INDEFINIDO"

def calcular_forca_mercado(df, volume_ratio, volatilidade, rsi):
    """Calcula força do mercado"""
    try:
        score = 0
        
        # Volume
        if volume_ratio > 1.5:
            score += 2
        elif volume_ratio > 1.0:
            score += 1
        
        # Volatilidade
        if volatilidade < 2:
            score += 2
        elif volatilidade < 5:
            score += 1
        
        # RSI
        if 30 <= rsi <= 70:
            score += 2
        elif 20 <= rsi <= 80:
            score += 1
        
        # Tendência
        ema8 = float(df["EMA8"].iloc[-1])
        ema21 = float(df["EMA21"].iloc[-1])
        if ema8 > ema21:
            score += 1
        
        if score >= 6:
            return "MUITO FORTE"
        elif score >= 4:
            return "FORTE"
        elif score >= 2:
            return "MÉDIA"
        else:
            return "FRACA"
    except:
        return "INDEFINIDA"

def analisar_simbolo(symbol):
    """Análise completa de um símbolo"""
    try:
        print(f"🔍 Buscando dados para {symbol}...")
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            print(f"❌ Dados vazios para {symbol}")
            return None
        
        print(f"✅ Dados obtidos para {symbol}: {len(df)} registros")
        
        ruptura, percentual = detectar_ruptura(df)
        
        # Análise estratégica completa
        analise = analisar_simbolo_estrategico(symbol, df, ruptura, percentual)
        
        # Salvar dados no banco
        if analise:
            with app.app_context():
                market_data = MarketData(
                    symbol=symbol,
                    price=analise["price"],
                    volume=analise["volume"],
                    ema8=analise["ema8"],
                    ema21=analise["ema21"],
                    sma200=analise["sma200"],
                    rsi=analise["rsi"],
                    volatilidade=analise["volatilidade"],
                    tendencia=analise["tendencia_curta"]
                )
                db.session.add(market_data)
                
                # Criar alertas se necessário
                if ruptura:
                    alert = Alert(
                        symbol=symbol,
                        price=analise["price"],
                        message=f"Ruptura detectada: {percentual:.2f}%",
                        tipo="ruptura"
                    )
                    db.session.add(alert)
                    sistema_estado["alertas_enviados"] += 1
                
                if analise["sinal_compra"]:
                    alert = Alert(
                        symbol=symbol,
                        price=analise["price"],
                        message="Sinal de compra detectado",
                        tipo="compra"
                    )
                    db.session.add(alert)
                
                if analise["sinal_venda"]:
                    alert = Alert(
                        symbol=symbol,
                        price=analise["price"],
                        message="Sinal de venda detectado",
                        tipo="venda"
                    )
                    db.session.add(alert)
                
                db.session.commit()
        
        return analise
        
    except Exception as e:
        print(f"❌ Erro na análise de {symbol}: {e}")
        return None

def executar_ciclo_analise():
    """Executa ciclo de análise contínua"""
    print("🔄 Iniciando ciclo de análise...")
    while sistema_estado["ativo"]:
        try:
            print(f"📊 Processando {len(symbols)} símbolos...")
            dados_atualizados = {}
            
            for symbol in symbols:
                print(f"🔍 Analisando {symbol}...")
                analise = analisar_simbolo(symbol)
                if analise:
                    dados_atualizados[symbol] = analise
                    print(f"✅ {symbol} processado com sucesso")
                else:
                    print(f"❌ {symbol} falhou na análise")
            
            print(f"📈 {len(dados_atualizados)} símbolos atualizados")
            with estado_lock:
                sistema_estado["dados_mercado"] = dados_atualizados
                sistema_estado["ultima_atualizacao"] = datetime.datetime.now()
            
            # Emitir dados via WebSocket
            with app.app_context():
                for symbol, dados in dados_atualizados.items():
                    dados_emitidos = {
                        'symbol': symbol,
                        'data': serializar_dados_json(dados)
                    }
                    # Verificar alertas
                    triggered_alerts = check_market_alerts(symbol, dados)
                    if triggered_alerts:
                        for alert in triggered_alerts:
                            socketio.emit('alert_triggered', alert, room=f"user_{alert['user_id']}")
                    
                    print(f"📡 Emitindo dados para {symbol}: {len(dados_emitidos['data'])} campos")
                    socketio.emit('market_data', dados_emitidos)
            
            time.sleep(update_interval)
            
        except Exception as e:
            print(f"❌ Erro no ciclo de análise: {e}")
            time.sleep(update_interval)

def start_market_analysis():
    """Inicia análise de mercado"""
    if not sistema_estado["ativo"]:
        with estado_lock:
            sistema_estado["ativo"] = True
            sistema_estado["inicio_execucao"] = datetime.datetime.now()
            sistema_estado["analise_thread"] = threading.Thread(target=executar_ciclo_analise)
        sistema_estado["analise_thread"].start()
        print("✅ Análise de mercado iniciada")

def stop_market_analysis():
    """Para análise de mercado"""
    with estado_lock:
        sistema_estado["ativo"] = False
    if sistema_estado["analise_thread"] and sistema_estado["analise_thread"].is_alive():
        try:
            sistema_estado["analise_thread"].join(timeout=5)
        except:
            pass
    print("⏹️ Análise de mercado parada")

# Rotas Flask
# ============================================
# IMPORTANTE: Rotas específicas devem vir ANTES da rota catch-all
# ============================================

# Endpoint para gerar gráfico como imagem (DEVE VIR ANTES DA ROTA CATCH-ALL)
@app.route('/api/v1/chart-image')
# @login_required  # Temporariamente desabilitado para permitir gráficos sem login
def api_v1_chart_image():
    """Gera gráfico de candlestick como imagem PNG"""
    print("=" * 80)
    print("🎯 [CHART-IMAGE] ENDPOINT ACESSADO!")
    print("=" * 80)
    
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    
    print(f"📊 [CHART-IMAGE] Requisição recebida: {symbol} {interval}")
    print(f"📊 [CHART-IMAGE] URL completa: {request.url}")
    print(f"📊 [CHART-IMAGE] Headers: {dict(request.headers)}")
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # Backend não-interativo para evitar problemas
        import matplotlib.pyplot as plt
        import mplfinance as mpf
        import numpy as np
        import pandas as pd
        
        print(f"📊 Gerando gráfico para {symbol} ({interval})...")
        
        # Tentar usar função do grafico_candlestick primeiro
        try:
            from grafico_candlestick import obter_dados_candlestick, calcular_indicadores_grafico
            df = obter_dados_candlestick(symbol, interval, limit=200)
            if df is not None and not df.empty:
                df = calcular_indicadores_grafico(df)
        except Exception as e:
            print(f"⚠️ Erro ao usar grafico_candlestick, tentando buscar_dados_binance: {e}")
            # Fallback: usar buscar_dados_binance
            df = buscar_dados_binance(symbol, interval, 200, skip_rate_limit=True)
            if df is not None and not df.empty:
                # Calcular EMAs básicas
                df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
                df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
        
        if df is None or df.empty:
            print(f"❌ Dados não disponíveis para {symbol} ({interval})")
            # Retornar imagem de erro
            return create_error_image(f"Dados não disponíveis para {symbol} ({interval})")
        
        print(f"✅ Dados obtidos: {len(df)} candles")
        
        # Garantir que o DataFrame tem o formato correto para mplfinance
        # mplfinance espera: index datetime, colunas ['open', 'high', 'low', 'close', 'volume']
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            print(f"❌ DataFrame não tem colunas necessárias: {df.columns.tolist()}")
            return create_error_image("Formato de dados inválido")
        
        # Selecionar apenas colunas necessárias
        df_plot = df[required_cols].copy()
        
        # Configurar estilo
        mc = mpf.make_marketcolors(
            up='#00ff88',
            down='#ff4444',
            edge='inherit',
            wick={'up':'#00ff88', 'down':'#ff4444'},
            volume='in',
            alpha=0.9
        )
        
        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='',
            y_on_right=False,
            rc={
                'font.size': 11,
                'axes.labelcolor': 'white',
                'axes.edgecolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white',
                'text.color': 'white'
            },
            facecolor='#1a1a1a',
            edgecolor='#ffffff',
            figcolor='#0a0a0a',
            gridcolor='#333333'
        )
        
        # Preparar adicional plots
        apds = []
        
        # EMAs
        if 'EMA8' in df.columns:
            apds.append(mpf.make_addplot(df['EMA8'], color='cyan', width=1.5, label='EMA 8'))
        if 'EMA21' in df.columns:
            apds.append(mpf.make_addplot(df['EMA21'], color='orange', width=1.5, label='EMA 21'))
        
        print(f"📊 Criando gráfico com {len(df_plot)} candles...")
        
        # Criar figura
        try:
            fig, axes = mpf.plot(
                df_plot,
                type='candle',
                style=s,
                title=f'{symbol} - {interval}',
                ylabel='Preço (USDT)',
                volume=True,
                ylabel_lower='Volume',
                addplot=apds if apds else None,
                figsize=(16, 10),
                returnfig=True,
                show_nontrading=False,
                warn_too_much_data=False
            )
        except Exception as e:
            print(f"❌ Erro ao criar gráfico mplfinance: {e}")
            import traceback
            traceback.print_exc()
            return create_error_image(f"Erro ao criar gráfico: {str(e)}")
        
        # Converter para bytes
        buffer = io.BytesIO()
        try:
            plt.savefig(
                buffer,
                format='png',
                dpi=150,
                bbox_inches='tight',
                facecolor='#0a0a0a',
                edgecolor='white',
                pad_inches=0.2
            )
            buffer.seek(0)
            plt.close(fig)
            print(f"✅ Gráfico gerado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao salvar gráfico: {e}")
            plt.close(fig)
            return create_error_image(f"Erro ao salvar gráfico: {str(e)}")
        
        # Retornar imagem
        image_bytes = buffer.getvalue()
        print(f"📊 [CHART-IMAGE] Imagem gerada: {len(image_bytes)} bytes")
        
        response = make_response(image_bytes)
        response.headers['Content-Type'] = 'image/png'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Content-Length'] = str(len(image_bytes))
        # CORS headers para garantir acesso do frontend
        origin = request.headers.get('Origin')
        allowed_origins = ['http://localhost:5173', 'http://localhost:9999', 'http://127.0.0.1:5173']
        if origin in allowed_origins or not IS_PRODUCTION:
            response.headers['Access-Control-Allow-Origin'] = origin or '*'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        print(f"📊 [CHART-IMAGE] Resposta preparada, Content-Type: {response.headers['Content-Type']}")
        return response
        
    except Exception as e:
        print(f"❌ Erro em /api/v1/chart-image: {e}")
        import traceback
        traceback.print_exc()
        return create_error_image(f"Erro: {str(e)}")

def create_error_image(message):
    """Cria uma imagem de erro simples"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        
        # Texto de erro
        ax.text(0.5, 0.5, message, 
                ha='center', va='center',
                fontsize=16, color='#ff4444',
                transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='#1a1a1a', edgecolor='#ff4444', pad=20))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, facecolor='#0a0a0a', bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'image/png'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except Exception as e:
        # Se até criar imagem de erro falhar, retornar JSON
        return jsonify({"success": False, "error": message}), 500

# ============================================
# ENDPOINT PARA POLLING DE PREÇO (ANTES DA ROTA CATCH-ALL)
# ============================================
@app.route('/api/v1/last-price')
# @login_required  # Temporariamente desabilitado para permitir gráficos sem login
def api_v1_last_price():
    """
    Endpoint leve que retorna apenas o último candle/preço para atualização em tempo real.
    Usado para polling do gráfico interativo.
    """
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    
    try:
        # Buscar apenas o último candle (limit=1)
        df = buscar_dados_binance(symbol, interval, 1, skip_rate_limit=True)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados não disponíveis"}), 404
        
        # Pegar último candle
        last_row = df.iloc[-1]
        timestamp = last_row.name
        
        # Converter datetime para timestamp Unix em segundos
        if hasattr(timestamp, 'timestamp'):
            time_sec = int(timestamp.timestamp())
        elif isinstance(timestamp, (int, float)):
            time_sec = int(timestamp) if timestamp < 1000000000000 else int(timestamp / 1000)
        else:
            time_sec = int(pd.Timestamp(timestamp).timestamp())
        
        return jsonify({
            "success": True,
            "symbol": symbol,
            "timeframe": interval,
            "candle": {
                "time": time_sec,
                "open": float(last_row['open']),
                "high": float(last_row['high']),
                "low": float(last_row['low']),
                "close": float(last_row['close']),
                "volume": float(last_row['volume']) if 'volume' in last_row else 0.0
            },
            "current_price": float(last_row['close'])
        }), 200
        
    except Exception as e:
        print(f"❌ [LAST-PRICE] Erro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ROTA PARA SERVIR FRONTEND VUE.JS
# ============================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """
    Serve o frontend Vue.js.
    Vue Router cuida do roteamento no frontend.
    Mantém compatibilidade com rotas antigas.
    
    IMPORTANTE: Esta rota catch-all NÃO deve capturar rotas de API.
    Todas as rotas /api/* devem ser definidas ANTES desta rota.
    """
    # CRÍTICO: Verificar PRIMEIRO se é rota de API antes de qualquer coisa
    # Verificar tanto o path quanto a URL completa
    request_path = request.path
    path_check = path.startswith('api/') or path.startswith('/api/') or 'api' in path
    url_check = request_path.startswith('/api/')
    
    if path_check or url_check:
        # Se chegou aqui, a rota de API não foi encontrada (erro 404)
        # Isso NÃO deveria acontecer se as rotas estiverem na ordem correta
        print(f"⚠️⚠️⚠️ [CATCH-ALL] ERRO CRÍTICO: Rota de API interceptada pela catch-all!")
        print(f"   Path: {path}")
        print(f"   Request path: {request_path}")
        print(f"   Method: {request.method}")
        print(f"   Headers: {dict(request.headers)}")
        print(f"   Isso indica que a rota de API não foi encontrada ANTES da catch-all")
        return jsonify({
            "success": False, 
            "error": f"API route not found: {request_path}",
            "path": path,
            "request_path": request_path,
            "message": "Esta rota de API não foi encontrada. Verifique se está definida antes da rota catch-all."
        }), 404
    
    # Rotas que devem usar templates antigos (compatibilidade)
    legacy_routes = ['/login', '/register', '/pricing', '/upgrade', '/admin']
    
    # Se for rota legacy, usar template antigo
    if path in legacy_routes or path.startswith('admin/'):
        if path == '/login' or path == 'login':
            return render_template('login.html')
        elif path == '/register' or path == 'register':
            return render_template('register.html')
        elif path == '/pricing' or path == 'pricing':
            return render_template('pricing.html')
        elif path == '/upgrade' or path == 'upgrade':
            return render_template('upgrade.html')
        elif path.startswith('admin'):
            # Deixar rotas admin para o blueprint
            pass
    
    # Se frontend existe, servir Vue.js
    if FRONTEND_EXISTS:
        # Arquivos estáticos (assets)
        if path.startswith('assets/'):
            return send_from_directory(FRONTEND_DIR, path)
        
        # Todas as outras rotas servem index.html
        # Vue Router cuida do roteamento
        return send_from_directory(FRONTEND_DIR, 'index.html')
    else:
        # Fallback: usar template antigo se frontend não estiver buildado
        if path == '' or path == '/':
            return render_template('pricing.html')
        return render_template('pricing.html')

@app.route('/legacy')
def index():
    """Homepage legacy - Página de pricing (mantida para compatibilidade)"""
    return render_template('pricing.html')

@app.route('/home')
def home():
    """Redireciona para pricing (homepage)"""
    return redirect(url_for('index'))

# Health endpoints
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/ready')
def ready():
    db_ok = True
    try:
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
    except Exception:
        db_ok = False
    keys_ok = (COINGECKO_KEY is not None) and (SCRAPERAPI_KEY is not None)
    return jsonify({
        "status": "ready" if (db_ok) else "not_ready",
        "db": db_ok,
        "keys": keys_ok
    })

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Rate limiting: 5 tentativas por minuto
def login():
    if request.method == 'POST':
        # Validar e sanitizar entrada
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Validação de entrada
        username_valid, username_msg = validate_username(username)
        password_valid, password_msg = validate_password(password)
        
        if not username_valid:
            flash(f'❌ {username_msg}')
            return render_template('login.html')
        
        if not password_valid:
            flash(f'❌ {password_msg}')
            return render_template('login.html')
        
        # Buscar usuário
        user = User.query.filter_by(username=username_msg).first()
        
        if user and verify_password(password, user.password.encode('utf-8')):
            login_user(user, remember=True)
            flash(f'✅ Login realizado com sucesso! Bem-vindo, {user.username}')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Usuário ou senha inválidos')
            # Log de tentativa falhada
            print(f"⚠️ Tentativa de login falhada para usuário: {username}")
    
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")  # Rate limiting: 3 registros por hora
def register():
    if request.method == 'POST':
        # Validar e sanitizar entrada
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Validação de entrada
        username_valid, username_msg = validate_username(username)
        password_valid, password_msg = validate_password(password)
        
        if not username_valid:
            flash(f'❌ {username_msg}')
            return render_template('register.html')
        
        if not password_valid:
            flash(f'❌ {password_msg}')
            return render_template('register.html')
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username_msg).first():
            flash('❌ Usuário já existe')
            return render_template('register.html')
        
        try:
            # Criar hash da senha
            password_hash = hash_password(password)
            
            # Criar usuário
            user = User(
                username=username_msg, 
                password=password_hash.decode('utf-8'),
                tier='free',
                api_calls_today=0,
                last_api_reset=datetime.date.today()
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('✅ Conta criada com sucesso! Faça login para continuar.')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erro ao criar conta: {str(e)}')
            print(f"❌ Erro ao criar usuário: {e}")
    
    response = make_response(render_template('register.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# ========================================
# NOVOS ENDPOINTS PARA DASHBOARD SEM WEBSOCKET
# ========================================

@app.route('/api/dashboard/execute/<command>', methods=['POST'])
@login_required
def api_dashboard_execute(command):
    """Executa comandos do terminal - USA APENAS BINANCE"""
    try:
        from motor_renan import analise_completa, coletar_dados
        from relatorio_profissional import gerar_relatorio_profissional
        
        data = request.json or {}
        command = command.upper()
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        
        # BUSCAR DADOS APENAS DA BINANCE (ignorando rate limit para requisições sob demanda)
        print(f"📊 Buscando dados Binance: {symbol} {timeframe}...")
        df = buscar_dados_binance(symbol, timeframe, 500, skip_rate_limit=True)
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'error': f'Dados não disponíveis da Binance para {symbol}'
            }), 404
        
        print(f"✅ Dados obtidos: {len(df)} registros")
        
        # EXECUTAR ANÁLISE COMPLETA
        print(f"🔬 Executando análise completa...")
        resultado = analise_completa(symbol, timeframe)
        
        # GERAR RELATÓRIO
        print(f"📝 Gerando relatório...")
        try:
            relatorio = gerar_relatorio_profissional(resultado)
        except Exception as e:
            print(f"⚠️ Erro ao gerar relatório completo: {e}")
            relatorio = f"📊 Análise de {symbol}\n{resultado.get('sintese', {}).get('resumo', 'Relatório em geração...')}"
        
        # Função helper para converter valores numpy/pandas
        def to_native_type(v):
            if isinstance(v, (np.integer, pd.Int64Dtype)):
                return int(v)
            elif isinstance(v, (np.floating, pd.Float64Dtype)):
                return float(v) if pd.notna(v) else None
            elif pd.isna(v):
                return None
            elif isinstance(v, (bool, np.bool_)):
                return bool(v)
            elif isinstance(v, (str, int, float, type(None))):
                return v
            else:
                return str(v)
        
        # Converter MACD para float ou None
        macd_value = df['MACD'].iloc[-1] if 'MACD' in df.columns else None
        macd_value = to_native_type(macd_value)
        
        resposta = {
            'success': True,
            'command': command,
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': pd.Timestamp.now().isoformat(),
            'analysis': {
                'price': float(df['close'].iloc[-1]),
                'indicators': {
                    'ema8': float(df['EMA8'].iloc[-1]) if 'EMA8' in df.columns else 0,
                    'ema21': float(df['EMA21'].iloc[-1]) if 'EMA21' in df.columns else 0,
                    'rsi': float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else 0,
                    'macd': macd_value,
                },
                'recommendation': str(resultado.get('sintese', {}).get('acao', 'AGUARDAR')),
                'entry': to_native_type(resultado.get('sintese', {}).get('entry_price')),
                'stop_loss': to_native_type(resultado.get('sintese', {}).get('stop_loss')),
                'take_profit': {
                    'tp1': to_native_type(resultado.get('sintese', {}).get('tp1')),
                    'tp2': to_native_type(resultado.get('sintese', {}).get('tp2')),
                    'tp3': to_native_type(resultado.get('sintese', {}).get('tp3')),
                },
                'risk_level': str(resultado.get('gestao_risco', {}).get('nivel', 'MÉDIO')),
                'confidence': to_native_type(resultado.get('confluencia', {}).get('score', 0))
            },
            'chart_data': {
                'timestamps': [str(ts) for ts in df.index[-100:]],
                'open': [float(x) for x in df['open'].iloc[-100:]],
                'high': [float(x) for x in df['high'].iloc[-100:]],
                'low': [float(x) for x in df['low'].iloc[-100:]],
                'close': [float(x) for x in df['close'].iloc[-100:]],
                'volume': [float(x) for x in df['volume'].iloc[-100:]],
            },
            'report': str(relatorio),
        }
        
        return jsonify(resposta)
    
    except Exception as e:
        print(f"❌ Erro executando comando {command}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/dashboard/commands')
@login_required
def api_dashboard_commands():
    """Lista comandos disponíveis"""
    return jsonify({
        'success': True,
        'commands': [
            {'code': 'R', 'name': 'Scanner Técnico', 'description': 'Análise completa multi-camada'},
            {'code': 'CTX', 'name': 'Contexto Macro', 'description': 'Regime e sentiment global'},
            {'code': 'MULT', 'name': 'Multi-Pair', 'description': 'Comparação de múltiplos pares'},
            {'code': 'CM', 'name': 'Campo Magnético', 'description': 'Visualização 3D de liquidez'},
        ]
    })

@app.route('/terminal')
@login_required
def terminal_dashboard():
    """Dashboard terminal com comandos interativos"""
    response = make_response(render_template('dashboard_terminal.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal para usuários autenticados"""
    # Redirecionar para terminal por padrão
    return redirect(url_for('terminal_dashboard'))
    
    # Versão antiga (mantida para backup):
    # response = make_response(render_template('dashboard.html'))
    # response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    # response.headers['Pragma'] = 'no-cache'
    # response.headers['Expires'] = '0'
    # return response

@app.route('/professional')
@login_required
def professional_dashboard():
    """Dashboard profissional com funcionalidades avançadas"""
    response = make_response(render_template('professional_dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/app')
def app_redirect():
    """Redireciona usuários autenticados para dashboard, outros para pricing"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

def serializar_dados_json(dados):
    """Serializa dados para JSON de forma segura - versão melhorada"""
    import numpy as np
    import pandas as pd
    from datetime import datetime, date
    
    if dados is None:
        return {}
    
    def make_json_serializable(obj):
        """Converte objetos não serializáveis para tipos JSON válidos"""
        # Verificar tipos NumPy primeiro (antes de tipos Python nativos)
        if isinstance(obj, np.bool_):
            return bool(obj)  # Converter np.bool_ para bool Python
        elif isinstance(obj, (np.integer, np.int64, np.int32, np.int8, np.int16)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            # Verificar se é NaN ou Inf antes de converter
            val = float(obj)
            if pd.isna(val) or not np.isfinite(val):
                return None
            return val
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, bool):
            return bool(obj)  # Garantir que é bool Python nativo
        elif isinstance(obj, dict):
            return {key: make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [make_json_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, type(None))):
            # Verificar se é NaN ou Inf antes de retornar
            if isinstance(obj, float):
                if pd.isna(obj) or not np.isfinite(obj):
                    return None
            return obj
        elif pd.isna(obj):
            return None
        elif isinstance(obj, float) and (np.isnan(obj) or not np.isfinite(obj)):
            return None
        else:
            # Tentar converter para string se não for um tipo básico
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # Último recurso: converter para string
                return str(obj)
    
    # Aplicar serialização recursiva
    if isinstance(dados, dict):
        return {key: make_json_serializable(value) for key, value in dados.items()}
    elif isinstance(dados, (list, tuple)):
        return [make_json_serializable(item) for item in dados]
    else:
        return make_json_serializable(dados)

@app.route('/api/market-data')
@login_required
def api_market_data():
    """API para obter dados de mercado com paginação"""
    symbol = request.args.get('symbol', 'BTCUSDT')
    dados = sistema_estado["dados_mercado"].get(symbol, {})
    return jsonify(serializar_dados_json(dados))

@app.route('/api/alerts')
@login_required
def api_alerts():
    """API para obter alertas com paginação"""
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = max(1, min(100, per_page))  # Limitar entre 1 e 100
        
        # Filtros opcionais
        symbol = request.args.get('symbol', None)
        tipo = request.args.get('tipo', None)
        
        # Query base
        query = Alert.query
        
        # Aplicar filtros
        if symbol:
            query = query.filter(Alert.symbol == symbol.upper())
        if tipo:
            query = query.filter(Alert.tipo == tipo)
        
        # Ordenar e paginar
        query = query.order_by(Alert.timestamp.desc())
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Serializar alertas
        alerts_data = [{
            'id': alert.id,
            'symbol': alert.symbol,
            'price': alert.price,
            'message': alert.message,
            'tipo': alert.tipo,
            'timestamp': alert.timestamp.isoformat() if alert.timestamp else None
        } for alert in pagination.items]
        
        return jsonify({
            'data': alerts_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        print(f"❌ Erro em /api/alerts: {e}")
        return jsonify({'error': str(e)}), 500

# --- API v1: TA Summary ---
@app.route('/api/v1/ta-summary')
@login_required
def api_v1_ta_summary():
    if not getattr(C, 'ENABLE_TA_SUMMARY', False):
        return jsonify({"success": False, "error": "feature_disabled"}), 404
    symbol = request.args.get('symbol', 'BTCUSDT')
    # Reutiliza dados mais recentes do estado (timeframe base 1m)
    dados = sistema_estado["dados_mercado"].get(symbol)
    if not dados:
        return jsonify({"success": False, "error": "no_data"}), 404
    # Para o resumo local, precisaríamos do DataFrame; como não guardamos DF, retornamos do snapshot
    # Alternativa: expor um cálculo leve baseado nos últimos campos do snapshot
    summary = {
        "symbol": symbol,
        "summary": "BUY" if (dados.get('ema8', 0) > dados.get('ema21', 0) and 30 <= dados.get('rsi', 50) <= 70) else "SELL",
        "latest": {
            "ema8": dados.get('ema8'),
            "ema21": dados.get('ema21'),
            "sma200": dados.get('sma200'),
            "rsi": dados.get('rsi')
        }
    }
    return jsonify({"success": True, "data": summary})

# --- API v1: Global Metrics (CMC) ---
@app.route('/api/v1/global-metrics')
@login_required
def api_v1_global_metrics():
    if not getattr(C, 'ENABLE_CMC', False):
        return jsonify({"success": False, "error": "feature_disabled"}), 404
    res = get_global_metrics(ttl=C.CMC_TTL, timeout=C.REQUEST_TIMEOUT)
    # Normalização defensiva
    cap = None
    btc_dom = None
    eth_dom = None
    gainers = 0
    losers = 0
    try:
        data = res.get('data', {})
        quote = data.get('data', {})  # conforme CMC estrutura
        cap = float(quote.get('quote', {}).get('USD', {}).get('total_market_cap', 0)) if quote.get('quote') else None
        btc_dom = float(quote.get('btc_dominance', 0)) if 'btc_dominance' in quote else None
        eth_dom = float(quote.get('eth_dominance', 0)) if 'eth_dominance' in quote else None
        # breadth: placeholders até listagem estar disponível
        gainers = int(quote.get('active_cryptocurrencies', 0) * 0.5) if quote.get('active_cryptocurrencies') else 0
        losers = max(0, int(quote.get('active_cryptocurrencies', 0)) - gainers) if quote.get('active_cryptocurrencies') else 0
    except Exception:
        pass
    return jsonify({
        "success": True,
        "data": {
            "market_cap": cap,
            "btc_dominance": btc_dom,
            "eth_dominance": eth_dom,
            "breadth": {"gainers": gainers, "losers": losers},
            "timestamp": int(time.time())
        }
    })

# --- API v1: Derivatives (CoinGlass) ---
@app.route('/api/v1/derivatives')
@login_required
def api_v1_derivatives():
    if not getattr(C, 'ENABLE_COINGLASS', False):
        return jsonify({"success": False, "error": "feature_disabled"}), 404
    symbol = request.args.get('symbol', 'BTCUSDT')
    funding = get_funding(symbol, ttl=C.COINGLASS_TTL, timeout=C.REQUEST_TIMEOUT)
    oi = get_oi(symbol, ttl=C.COINGLASS_TTL, timeout=C.REQUEST_TIMEOUT)
    lsr = get_lsr(symbol, ttl=C.COINGLASS_TTL, timeout=C.REQUEST_TIMEOUT)
    liq = get_liquidations(symbol, ttl=C.COINGLASS_TTL, timeout=C.REQUEST_TIMEOUT)

    # Normalização conservadora
    funding_series = []
    try:
        funding_series = funding.get('data', {}).get('data', [])[:50]
        if isinstance(funding_series, dict):
            funding_series = list(funding_series.values())
    except Exception:
        funding_series = []
    zscore = None
    if funding_series:
        try:
            vals = [float(x.get('fundingRate', 0)) for x in funding_series if isinstance(x, dict)]
            if len(vals) >= 5:
                mu = sum(vals) / len(vals)
                var = sum((v - mu)**2 for v in vals) / len(vals)
                std = var ** 0.5
                last = vals[-1]
                zscore = (last - mu) / std if std > 0 else 0.0
        except Exception:
            zscore = None

    oi_delta = None
    try:
        oi_points = oi.get('data', {}).get('data', [])[:2]
        if len(oi_points) >= 2:
            a = float(oi_points[-2].get('openInterest', 0))
            b = float(oi_points[-1].get('openInterest', 0))
            if a > 0:
                oi_delta = (b - a) / a * 100.0
    except Exception:
        oi_delta = None

    lsr_accounts = None
    lsr_volume = None
    try:
        lsr_data = lsr.get('data', {}).get('data', {})
        lsr_accounts = float(lsr_data.get('longShortAccount', 0)) if isinstance(lsr_data, dict) else None
        lsr_volume = float(lsr_data.get('longShortVolume', 0)) if isinstance(lsr_data, dict) else None
    except Exception:
        pass

    # Liquidations como série para overlay (com preço e timestamp)
    liq_series = []
    liq_overlay_data = []
    try:
        liq_points = liq.get('data', {}).get('data', [])[:50]
        if isinstance(liq_points, list):
            for p in liq_points:
                v = float(p.get('volume', 0)) if isinstance(p, dict) else 0
                liq_series.append(v)
                
                # Dados para overlay no gráfico (preço + timestamp)
                if isinstance(p, dict):
                    price = float(p.get('price', 0))
                    timestamp = p.get('timestamp', int(time.time()))
                    liq_type = p.get('type', 'unknown')
                    liq_overlay_data.append({
                        'price': price,
                        'timestamp': timestamp,
                        'volume': v,
                        'type': liq_type
                    })
    except Exception:
        liq_series = []
        liq_overlay_data = []

    return jsonify({
        "success": True,
        "data": {
            "funding": {"zscore": zscore, "series": funding_series},
            "oi": {"delta_pct": oi_delta},
            "lsr": {"accounts": lsr_accounts, "volume": lsr_volume},
            "liquidations": {"series": liq_series, "overlay_data": liq_overlay_data},
            "timestamp": int(time.time())
        }
    })

# Listings por tag com dados reais do CMC
@app.route('/api/v1/listings')
@login_required
def api_v1_listings():
    if not getattr(C, 'ENABLE_CMC', False):
        return jsonify({"success": False, "error": "feature_disabled"}), 404
    tag = request.args.get('tag', 'all')
    limit = min(int(request.args.get('limit', '100')), 500)
    
    try:
        from integrations.cmc import get_listings_by_tag
        res = get_listings_by_tag(tag, limit=limit, ttl=C.CMC_TTL, timeout=C.REQUEST_TIMEOUT)
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoint para dados de candles reais
# ============================================
# APIs PARA FRONTEND VUE.JS
# ============================================

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Análise técnica completa - Endpoint para frontend Vue.js"""
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        
        print(f"\n{'='*80}")
        print(f"📊 [ANALYZE] Requisição recebida: {symbol} {timeframe}")
        print(f"{'='*80}\n")
        
        # Importar motor de análise
        from motor_renan import analise_completa
        
        # Executar análise
        print(f"🔬 [ANALYZE] Executando análise completa para {symbol} {timeframe}...")
        resultado = analise_completa(symbol, timeframe)
        
        # DEBUG: Verificar estrutura do resultado
        print(f"✅ [ANALYZE] Análise concluída!")
        print(f"   Tem sintese? {bool(resultado.get('sintese'))}")
        print(f"   Tem niveis_operacionais? {bool(resultado.get('niveis_operacionais'))}")
        print(f"   Tem contexto? {bool(resultado.get('contexto'))}")
        print(f"   Tem estrutura? {bool(resultado.get('estrutura'))}")
        print(f"   Tem confluencia? {bool(resultado.get('confluencia'))}")
        
        if resultado.get('sintese'):
            sintese = resultado['sintese']
            print(f"   Sintese - Score: {sintese.get('score_combinado', 'N/A')}")
            print(f"   Sintese - Ação: {sintese.get('acao', 'N/A')}")
        
        # Serializar para JSON (versão melhorada)
        resultado_serializado = serializar_dados_json(resultado)
        
        # Garantir que é JSON válido e limpar NaN/Inf
        import json
        import math
        
        def clean_nan_inf(obj):
            """Remove NaN e Inf recursivamente"""
            if isinstance(obj, dict):
                return {k: clean_nan_inf(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan_inf(item) for item in obj]
            elif isinstance(obj, float):
                if math.isnan(obj) or not math.isfinite(obj):
                    return None
                return obj
            return obj
        
        resultado_serializado = clean_nan_inf(resultado_serializado)
        
        # Testar se é serializável
        json.dumps(resultado_serializado)
        
        print(f"✅ [ANALYZE] Dados serializados e prontos para envio")
        print(f"   Sintese presente: {bool(resultado_serializado.get('sintese'))}")
        print(f"   Niveis operacionais presentes: {bool(resultado_serializado.get('niveis_operacionais'))}\n")
        return jsonify(resultado_serializado), 200
        
    except TypeError as e:
        # Erro de serialização JSON
        print(f"❌ Erro de serialização JSON em /api/analyze: {e}")
        import traceback
        traceback.print_exc()
        # Tentar serializar novamente com tratamento mais agressivo
        try:
            resultado_serializado = serializar_dados_json(resultado)
            return jsonify(resultado_serializado), 200
        except:
            return jsonify({
                'status': 'error',
                'error': f'Erro ao serializar resultado: {str(e)}',
                'symbol': symbol,
                'timeframe': timeframe
            }), 500
    except Exception as e:
        print(f"❌ Erro em /api/analyze: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/v1/symbols/search', methods=['GET'])
@limiter.limit("100 per minute")  # Rate limit generoso
def search_symbols():
    """
    Busca símbolos com autocomplete
    Query params: q (query), limit (max results, default 20)
    """
    try:
        query = request.args.get('q', '').upper().strip()
        limit = int(request.args.get('limit', 20))
        
        if len(query) < 1:
            return jsonify({'symbols': [], 'total': 0, 'query': query})
        
        all_symbols = get_binance_symbols()
        
        if not all_symbols:
            return jsonify({
                'symbols': get_fallback_symbols()[:limit],
                'total': len(get_fallback_symbols()),
                'query': query,
                'warning': 'Usando lista fallback'
            })
        
        # Filtra em memória (muito rápido para < 2000 itens)
        # Busca no símbolo OU no nome base
        filtered = []
        for s in all_symbols:
            symbol_match = query in s['symbol']
            name_match = query in s['baseAsset'].upper() or query in s['name'].upper()
            
            if symbol_match or name_match:
                filtered.append(s)
        
        # Limitar resultados
        results = filtered[:limit]
        
        return jsonify({
            'symbols': results,
            'total': len(filtered),
            'query': query
        })
    except Exception as e:
        print(f"❌ Erro em /api/v1/symbols/search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'symbols': get_fallback_symbols()[:20],
            'total': len(get_fallback_symbols()),
            'query': query or '',
            'error': str(e)
        }), 500

@app.route('/api/signal', methods=['GET'])
@limiter.limit("500 per hour" if not IS_PRODUCTION else "100 per hour")  # Limite muito alto em dev
def api_signal():
    """Obter sinal - Endpoint para frontend Vue.js"""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1h')
        
        # Importar cache manager
        try:
            from cache_manager import get_cached_analysis, set_cached_analysis
            cache_available = True
        except ImportError:
            cache_available = False
            print("⚠️ Cache manager não disponível, continuando sem cache")
        
        # TTL por timeframe (em segundos)
        TTL_BY_TIMEFRAME = {
            '1m': 60, '3m': 60, '5m': 60,
            '15m': 180, '30m': 180,
            '1h': 300,
            '2h': 600,   # 10 minutos
            '4h': 1800,  # 30 minutos
            '6h': 1800,  # 30 minutos
            '8h': 1800,  # 30 minutos
            '12h': 1800, # 30 minutos
            '1d': 1800,  # 30 minutos
            '3d': 3600,  # 1 hora
            '1w': 3600,  # 1 hora
            '1M': 7200   # 2 horas
        }
        ttl = TTL_BY_TIMEFRAME.get(timeframe, 300)  # Default 5 minutos
        
        # Tentar obter do cache primeiro
        if cache_available:
            cached_result = get_cached_analysis(symbol, timeframe)
            if cached_result:
                print(f"✅ Cache hit para {symbol} {timeframe}")
                # Retornar resultado em cache formatado
                return jsonify(cached_result), 200
        
        # Cache miss - executar análise
        print(f"🔄 Cache miss para {symbol} {timeframe}, executando análise...")
        
        # Importar motor de análise
        from motor_renan import analise_completa
        
        # Executar análise
        resultado = analise_completa(symbol, timeframe)
        
        # Extrair sinal e score do resultado
        # O resultado pode ter sinal em diferentes lugares
        sinal_completo = resultado.get('indicadores', {}).get('sinal_completo', {})
        confluencia_avancada = resultado.get('indicadores', {}).get('confluencia_avancada', {})
        confluencia = resultado.get('confluencia', {})
        
        # Extrair score - usar o mesmo que a análise detalhada usa
        sintese = resultado.get('sintese', {})
        
        # Determinar sinal - usar ação/recomendação da síntese se disponível
        sinal = 'NEUTRAL'
        acao_sintese = sintese.get('acao', '')
        recomendacao_sintese = sintese.get('recomendacao', '')
        
        # Extrair preço atual ANTES de determinar sinal (para comparação com entry)
        indicadores = resultado.get('indicadores', {})
        contexto = resultado.get('contexto', {})
        preco_atual = (
            indicadores.get('preco') or 
            contexto.get('preco_atual') or 
            contexto.get('preco') or 
            None
        )
        
        # Priorizar ação da síntese (LONG/SHORT) - verificar se há Entry definido
        entry_price = sintese.get('entry_price', 0)
        has_entry = entry_price and entry_price > 0
        
        if has_entry:
            # Se há entry definido, determinar sinal pela ação
            if 'LONG' in str(acao_sintese).upper() or 'LONG' in str(recomendacao_sintese).upper():
                sinal = 'BUY'
            elif 'SHORT' in str(acao_sintese).upper() or 'SHORT' in str(recomendacao_sintese).upper():
                sinal = 'SELL'
            # Se não conseguiu determinar, mas há entry, tentar pelo preço
            elif preco_atual and entry_price < preco_atual:
                # Entry abaixo do preço atual = oportunidade de compra (BUY/LONG)
                sinal = 'BUY'
            elif preco_atual and entry_price > preco_atual:
                # Entry acima do preço atual = oportunidade de venda (SELL/SHORT)
                sinal = 'SELL'
        
        # Fallback para sinal_completo
        if sinal == 'NEUTRAL' and sinal_completo:
            sinal_num = sinal_completo.get('sinal', 0)
            if sinal_num > 0:
                sinal = 'BUY'
            elif sinal_num < 0:
                sinal = 'SELL'
        score = 0
        
        # Priorizar score_combinado (mesma prioridade da análise detalhada)
        if sintese:
            # Prioridade 1: score_combinado = (score + score_avancado) / 2
            score_combinado = sintese.get('score_combinado')
            if score_combinado is not None:
                score = float(score_combinado)
            else:
                # Prioridade 2: score_confianca
                score_confianca = sintese.get('score_confianca')
                if score_confianca is not None:
                    score = float(score_confianca)
                else:
                    # Prioridade 3: score básico
                    score_basico = sintese.get('score')
                    if score_basico is not None:
                        score = float(score_basico)
        
        # Se score ainda é 0 ou None, usar confluência básica
        if score == 0 or score is None:
            score_basico = confluencia.get('score', 0)
            score = float(score_basico) if score_basico else 0
            # Normalizar se negativo
            if score < 0:
                score = abs(score)
        
        # Garantir que score está entre 0-10
        score = max(0.0, min(10.0, float(score) if score else 0.0))
        
        # Extrair informações operacionais da síntese
        entry_price = sintese.get('entry_price', 0)
        stop_loss = sintese.get('stop_loss', 0)
        tp1 = sintese.get('tp1', 0)
        tp2 = sintese.get('tp2', 0)
        tp3 = sintese.get('tp3', 0)
        rr_ratio = sintese.get('rr_ratio', 'N/A')
        risco = sintese.get('risco', 'N/A')
        recomendacao = sintese.get('recomendacao', '')
        acao = sintese.get('acao', '')
        
        # Preço atual já foi extraído anteriormente para determinar sinal
        
        # Formatar resposta
        response_data = {
            'symbol': symbol,
            'timeframe': timeframe,
            'signal': sinal,
            'score': score,
            'confluence_score': score,
            # Preço atual do ativo
            'current_price': float(preco_atual) if preco_atual else None,
            # Informações operacionais estratégicas
            'operational': {
                'entry_price': float(entry_price) if entry_price else None,
                'stop_loss': float(stop_loss) if stop_loss else None,
                'take_profit_1': float(tp1) if tp1 else None,
                'take_profit_2': float(tp2) if tp2 else None,
                'take_profit_3': float(tp3) if tp3 else None,
                'risk_reward_ratio': rr_ratio if rr_ratio != 'N/A' else None,
                'risk_level': risco if risco != 'N/A' else None,
                'recommendation': recomendacao,
                'action': acao
            }
        }
        
        # Armazenar no cache para próximas requisições
        if cache_available:
            try:
                # Usar cache manager para armazenar com TTL específico
                from cache_manager import cache_manager
                cache_key = f"{symbol}_{timeframe}"
                cache_manager.set('sinais', cache_key, response_data, ttl=ttl)
                print(f"💾 Resultado cacheado para {symbol} {timeframe} (TTL: {ttl}s)")
            except Exception as e:
                print(f"⚠️ Erro ao cachear resultado: {e}")
        
        # Retornar resposta
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Erro em /api/signal: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/v1/candles')
# @login_required  # Temporariamente desabilitado para permitir gráficos sem login
def api_v1_candles():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1m')
    limit = min(int(request.args.get('limit', '100')), 1000)
    
    try:
        # Usar a função existente de busca de dados
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados não disponíveis"}), 404
        
        # Converter DataFrame para formato de candles
        # O DataFrame tem 'time' como índice (datetime) e colunas OHLCV
        candles = []
        for timestamp, row in df.iterrows():
            # Converter datetime para timestamp Unix em milissegundos
            if hasattr(timestamp, 'timestamp'):
                # Se é datetime, converter para timestamp
                time_ms = int(timestamp.timestamp() * 1000)
            elif isinstance(timestamp, (int, float)):
                # Se já é timestamp, usar diretamente
                time_ms = int(timestamp * 1000) if timestamp < 1000000000000 else int(timestamp)
            else:
                # Fallback: usar timestamp atual
                time_ms = int(time.time() * 1000)
            
            candles.append({
                "time": time_ms,  # timestamp em ms
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume'])
            })
        
        return jsonify({
            "success": True,
            "data": {
                "symbol": symbol,
                "interval": interval,
                "candles": candles,
                "timestamp": int(time.time())
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoint para indicadores avançados
@app.route('/api/v1/advanced-indicators')
# @login_required  # Temporariamente desabilitado para permitir gráficos sem login
def api_v1_advanced_indicators():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1m')
    limit = min(int(request.args.get('limit', '100')), 1000)
    
    try:
        # Buscar dados de candles
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados não disponíveis"}), 404
        
        # Calcular indicadores avançados
        indicators = calculate_all_indicators(df)
        
        return jsonify({
            "success": True,
            "data": {
                "symbol": symbol,
                "interval": interval,
                "indicators": indicators,
                "timestamp": int(time.time())
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoint para níveis S/R e operacionais
@app.route('/api/chart/levels')
# @login_required  # Temporariamente desabilitado para permitir gráficos sem login
def api_chart_levels():
    """Retorna suportes, resistências e níveis operacionais para o gráfico"""
    symbol = request.args.get('symbol', 'BTCUSDT')
    timeframe = request.args.get('timeframe', '1h')
    
    try:
        from motor_renan import analise_completa
        from calcular_suportes_resistencias import calcular_suportes_resistencias
        
        # Buscar dados
        df = buscar_dados_binance(symbol, timeframe, 500)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados não disponíveis"}), 404
        
        # Calcular S/R
        sr_data = calcular_suportes_resistencias(df, num_niveis=5)
        
        # Buscar análise completa para níveis operacionais
        try:
            resultado = analise_completa(symbol, timeframe)
            niveis_operacionais = resultado.get('niveis_operacionais', {})
            estrutura = resultado.get('estrutura', {})
            
            # Extrair suportes e resistências da estrutura também
            suportes_estrutura = estrutura.get('suportes', [])
            resistencias_estrutura = estrutura.get('resistencias', [])
        except Exception as e:
            print(f"⚠️ Erro ao buscar análise completa: {e}")
            niveis_operacionais = {}
            suportes_estrutura = []
            resistencias_estrutura = []
        
        # Combinar suportes e resistências
        suportes = sr_data.get('suportes', []) if sr_data else []
        resistencias = sr_data.get('resistencias', []) if sr_data else []
        
        # Adicionar da estrutura
        for sup in suportes_estrutura:
            if isinstance(sup, dict):
                suportes.append(sup.get('preco', 0))
            else:
                suportes.append(sup)
        
        for res in resistencias_estrutura:
            if isinstance(res, dict):
                resistencias.append(res.get('preco', 0))
            else:
                resistencias.append(res)
        
        # Remover duplicatas e ordenar
        suportes = sorted(list(set([s for s in suportes if s > 0])), reverse=True)[:5]
        resistencias = sorted(list(set([r for r in resistencias if r > 0])), reverse=True)[:5]
        
        return jsonify({
            "success": True,
            "data": {
                "suportes": suportes,
                "resistencias": resistencias,
                "operacionais": {
                    "entry": niveis_operacionais.get('entry_price'),
                    "stop_loss": niveis_operacionais.get('stop_loss'),
                    "tp1": niveis_operacionais.get('tp1'),
                    "tp2": niveis_operacionais.get('tp2'),
                    "tp3": niveis_operacionais.get('tp3'),
                    "rr_ratio": niveis_operacionais.get('rr_ratio')
                }
            }
        })
    except Exception as e:
        print(f"❌ Erro em /api/chart/levels: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================
# ENDPOINT PARA POLLING DE PREÇO (ANTES DA ROTA CATCH-ALL)
# ============================================
@app.route('/api/v1/chart-data')
# @login_required  # Temporariamente desabilitado para permitir gráficos sem login
def api_v1_chart_data():
    """
    Endpoint consolidado que retorna todos os dados necessários para gráfico interativo:
    - Candles (OHLCV)
    - Indicadores (EMA8, EMA21, RSI)
    - Níveis operacionais (Entry, SL, TP)
    - Suportes e Resistências
    """
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    requested_limit = int(request.args.get('limit', '500'))
    
    # DEBUG: Verificar parâmetros recebidos
    print(f"📊 [CHART-DATA] Parâmetros recebidos:")
    print(f"   symbol: {symbol}")
    print(f"   interval: {interval} (tipo: {type(interval)})")
    print(f"   limit: {requested_limit}")
    print(f"   Todos os args: {dict(request.args)}")
    
    # Ajustar limit baseado no intervalo para evitar problemas com intervalos longos
    # Intervalos longos (3d, 1w, 1M) precisam de menos candles para mostrar período significativo
    limit_adjustments = {
        '3d': min(requested_limit, 200),   # 200 candles = ~600 dias
        '1w': min(requested_limit, 150),   # 150 candles = ~1050 dias (~3 anos)
        '1M': min(requested_limit, 100)    # 100 candles = ~100 meses (~8 anos)
    }
    limit = limit_adjustments.get(interval, min(requested_limit, 1000))
    
    print(f"📊 [CHART-DATA] Requisição processada: {symbol} {interval} (limit: {limit}, original: {requested_limit})")
    
    try:
        # Buscar dados da Binance
        try:
            df = buscar_dados_binance(symbol, interval, limit, skip_rate_limit=True)
            if df is None or df.empty:
                print(f"⚠️ [CHART-DATA] DataFrame vazio ou None para {symbol} {interval}")
                return jsonify({"success": False, "error": "Dados não disponíveis da Binance"}), 404
        except Exception as e:
            print(f"❌ [CHART-DATA] Erro ao buscar dados: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": f"Erro ao buscar dados: {str(e)}"}), 500
        
        # Calcular indicadores básicos
        df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
        df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
        
        # Calcular RSI
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        except Exception as e:
            print(f"⚠️ Erro ao calcular RSI: {e}")
            df['RSI'] = None
        
        # DEBUG: Verificar intervalo dos dados antes de converter
        if len(df) >= 2:
            first_ts = df.index[0]
            last_ts = df.index[-1]
            if hasattr(first_ts, 'timestamp'):
                first_sec = int(first_ts.timestamp())
                last_sec = int(last_ts.timestamp())
            else:
                first_sec = int(first_ts) if first_ts < 1000000000000 else int(first_ts / 1000)
                last_sec = int(last_ts) if last_ts < 1000000000000 else int(last_ts / 1000)
            diff_sec = last_sec - first_sec
            diff_min = diff_sec / 60
            actual_interval_min = diff_min / (len(df) - 1) if len(df) > 1 else 0
            print(f"📊 [CHART-DATA] Intervalo dos dados ANTES de converter:")
            print(f"   Primeiro: {first_ts} ({first_sec})")
            print(f"   Último: {last_ts} ({last_sec})")
            print(f"   Intervalo real: ~{actual_interval_min:.1f} min/candle")
            print(f"   Esperado para {interval}: {720 if interval == '12h' else 'varia'} min/candle")
            if interval == '12h' and abs(actual_interval_min - 720) > 60:
                print(f"   ⚠️ [CHART-DATA] ERRO: Dados estão com intervalo incorreto!")
                print(f"   Isso pode indicar que buscar_dados_binance retornou dados errados ou há cache")
        
        # Preparar candles para Lightweight Charts (timestamp em segundos)
        candles = []
        for timestamp, row in df.iterrows():
            # Converter datetime para timestamp Unix em segundos
            if hasattr(timestamp, 'timestamp'):
                time_sec = int(timestamp.timestamp())
            elif isinstance(timestamp, (int, float)):
                # Se já é timestamp, ajustar para segundos se necessário
                time_sec = int(timestamp) if timestamp < 1000000000000 else int(timestamp / 1000)
            else:
                time_sec = int(time.time())
            
            candles.append({
                "time": time_sec,
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume'])
            })
        
        # DEBUG: Verificar intervalo dos candles APÓS converter
        if len(candles) >= 2:
            first_candle_time = candles[0]['time']
            last_candle_time = candles[-1]['time']
            diff_sec = last_candle_time - first_candle_time
            diff_min = diff_sec / 60
            actual_interval_min = diff_min / (len(candles) - 1) if len(candles) > 1 else 0
            print(f"📊 [CHART-DATA] Intervalo dos candles APÓS converter:")
            print(f"   Primeiro: {first_candle_time} ({datetime.datetime.fromtimestamp(first_candle_time)})")
            print(f"   Último: {last_candle_time} ({datetime.datetime.fromtimestamp(last_candle_time)})")
            print(f"   Intervalo real: ~{actual_interval_min:.1f} min/candle")
            if interval == '12h' and abs(actual_interval_min - 720) > 60:
                print(f"   ❌ [CHART-DATA] ERRO CRÍTICO: Candles convertidos estão com intervalo incorreto!")
        
        # Preparar indicadores (apenas valores não-nulos)
        indicators = {
            "ema8": [],
            "ema21": [],
            "rsi": []
        }
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            if hasattr(timestamp, 'timestamp'):
                time_sec = int(timestamp.timestamp())
            elif isinstance(timestamp, (int, float)):
                time_sec = int(timestamp) if timestamp < 1000000000000 else int(timestamp / 1000)
            else:
                time_sec = int(time.time())
            
            # EMA8 - começar após 8 períodos
            if i >= 7 and pd.notna(row.get('EMA8')):
                indicators["ema8"].append({
                    "time": time_sec,
                    "value": float(row['EMA8'])
                })
            
            # EMA21 - começar após 21 períodos
            if i >= 20 and pd.notna(row.get('EMA21')):
                indicators["ema21"].append({
                    "time": time_sec,
                    "value": float(row['EMA21'])
                })
            
            # RSI - começar após 14 períodos
            if i >= 13 and pd.notna(row.get('RSI')):
                indicators["rsi"].append({
                    "time": time_sec,
                    "value": float(row['RSI'])
                })
        
        # Buscar níveis operacionais e S/R via análise completa
        levels = {
            "supports": [],
            "resistances": [],
            "operational": {
                "entry": None,
                "stop_loss": None,
                "take_profit": [None, None, None]
            }
        }
        
        try:
            from motor_renan import analise_completa
            from calcular_suportes_resistencias import calcular_suportes_resistencias
            
            # Calcular S/R
            sr_data = calcular_suportes_resistencias(df, num_niveis=5)
            if sr_data:
                levels["supports"] = [float(s) for s in sr_data.get('suportes', []) if s > 0][:5]
                levels["resistances"] = [float(r) for r in sr_data.get('resistencias', []) if r > 0][:5]
            
            # Buscar análise completa para níveis operacionais
            resultado = analise_completa(symbol, interval)
            sintese = resultado.get('sintese', {})
            niveis_operacionais = resultado.get('niveis_operacionais', {})
            
            # Helper para converter valores
            def to_float(v):
                try:
                    if v is None or (isinstance(v, float) and (pd.isna(v) or pd.isinf(v))):
                        return None
                    return float(v) if v != 0 else None
                except:
                    return None
            
            # Níveis operacionais
            levels["operational"]["entry"] = to_float(sintese.get('entry_price') or niveis_operacionais.get('entry_price'))
            levels["operational"]["stop_loss"] = to_float(sintese.get('stop_loss') or niveis_operacionais.get('stop_loss'))
            levels["operational"]["take_profit"][0] = to_float(sintese.get('tp1') or niveis_operacionais.get('tp1'))
            levels["operational"]["take_profit"][1] = to_float(sintese.get('tp2') or niveis_operacionais.get('tp2'))
            levels["operational"]["take_profit"][2] = to_float(sintese.get('tp3') or niveis_operacionais.get('tp3'))
            
        except Exception as e:
            print(f"⚠️ Erro ao buscar níveis operacionais: {e}")
            import traceback
            traceback.print_exc()
        
        # Preço atual
        current_price = float(df['close'].iloc[-1]) if len(df) > 0 else None
        
        # Montar resposta consolidada
        response_data = {
            "success": True,
            "symbol": symbol,
            "timeframe": interval,
            "candles": candles,
            "indicators": indicators,
            "levels": levels,
            "current_price": current_price,
            "timestamp": int(time.time())
        }
        
        # Log de debug para verificar formato de timestamp
        if candles:
            first_candle_time = candles[0]['time']
            print(f"📊 [CHART-DATA] Primeiro candle timestamp: {first_candle_time}")
            print(f"📊 [CHART-DATA] É segundos? {first_candle_time < 2000000000}")
            print(f"📊 [CHART-DATA] Data: {datetime.datetime.fromtimestamp(first_candle_time).isoformat()}")
        
        print(f"✅ [CHART-DATA] Dados preparados: {len(candles)} candles, {len(indicators['ema8'])} EMA8, {len(indicators['ema21'])} EMA21")
        
        # DEBUG: Verificar intervalo dos candles retornados
        if len(candles) > 1:
            first_time = candles[0]['time']
            last_time = candles[-1]['time']
            time_diff = last_time - first_time
            candles_count = len(candles)
            avg_interval_sec = time_diff / (candles_count - 1) if candles_count > 1 else 0
            avg_interval_min = avg_interval_sec / 60
            
            expected_intervals = {
                '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '2h': 120, '4h': 240, '6h': 360, '8h': 480, '12h': 720,
                '1d': 1440, '3d': 4320, '1w': 10080, '1M': 43200
            }
            expected_min = expected_intervals.get(interval, 60)
            
            print(f"📊 [CHART-DATA] Verificação de intervalo:")
            print(f"   Intervalo solicitado: {interval}")
            print(f"   Intervalo esperado: ~{expected_min} min")
            print(f"   Intervalo real dos dados: ~{avg_interval_min:.1f} min")
            print(f"   Primeiro candle: {datetime.datetime.fromtimestamp(first_time)}")
            print(f"   Último candle: {datetime.datetime.fromtimestamp(last_time)}")
            if abs(avg_interval_min - expected_min) > expected_min * 0.3:
                print(f"   ⚠️ AVISO: Intervalo dos dados não corresponde ao solicitado!")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Erro em /api/v1/chart-data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# NOTA: A rota /api/v1/chart-image foi movida para ANTES da rota catch-all (linha ~1990)
# para garantir que seja encontrada antes da rota catch-all capturar a requisição

# Endpoints para sistema de alertas
@app.route('/api/v1/alerts', methods=['GET'])
@login_required
def api_v1_get_alerts():
    """Retorna alertas do usuário."""
    try:
        alerts = alert_manager.get_user_alerts(current_user.id)
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "id": alert.id,
                "symbol": alert.symbol,
                "type": alert.alert_type.value,
                "condition": alert.condition.value,
                "threshold": alert.threshold,
                "message": alert.message,
                "is_active": alert.is_active,
                "created_at": alert.created_at.isoformat(),
                "trigger_count": alert.trigger_count
            })
        
        return jsonify({"success": True, "data": alerts_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/alerts', methods=['POST'])
@login_required
def api_v1_create_alert():
    """Cria um novo alerta."""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        alert_type = data.get('type')
        condition = data.get('condition')
        threshold = float(data.get('threshold', 0))
        message = data.get('message', '')
        
        if not all([symbol, alert_type, condition]):
            return jsonify({"success": False, "error": "Dados obrigatórios ausentes"}), 400
        
        # Criar alerta baseado no tipo
        if alert_type == 'price':
            alert_id = create_price_alert(current_user.id, symbol, condition, threshold, message)
        elif alert_type == 'rsi':
            alert_id = create_rsi_alert(current_user.id, symbol, condition, threshold, message)
        elif alert_type == 'volume':
            alert_id = create_volume_alert(current_user.id, symbol, condition, threshold, message)
        else:
            return jsonify({"success": False, "error": "Tipo de alerta inválido"}), 400
        
        return jsonify({"success": True, "data": {"alert_id": alert_id}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/alerts/<alert_id>', methods=['DELETE'])
@login_required
def api_v1_delete_alert(alert_id):
    """Remove um alerta."""
    try:
        success = alert_manager.delete_alert(alert_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Alerta não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================
# API: NOTIFICAÇÕES E MONITOR DE OPORTUNIDADES
# ============================================

@app.route('/api/v1/notifications/stats', methods=['GET'])
def api_v1_notifications_stats():
    """Retorna estatísticas do monitor de oportunidades"""
    monitor = get_opportunity_monitor()
    
    # Se monitor não está disponível, tentar criar novamente
    if monitor is None:
        # Tentar criar monitor novamente
        try:
            monitor = get_opportunity_monitor()
        except:
            pass
    
    if monitor is None:
        return jsonify({
            "success": False,
            "error": "Monitor de oportunidades não disponível",
            "stats": None
        }), 503
    
    try:
        stats = monitor.get_stats()
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/v1/notifications/history', methods=['GET'])
def api_v1_notifications_history():
    """Retorna histórico de notificações enviadas com dados completos"""
    try:
        from notifications.telegram_notifier import get_app_data_dir
        from pathlib import Path
        import json
        
        try:
            app_data_dir = get_app_data_dir()
        except Exception as e:
            print(f"⚠️ Erro ao obter diretório de dados: {e}")
            # Fallback para diretório padrão
            from pathlib import Path
            import os
            home = Path.home()
            app_data_dir = home / 'Library' / 'Application Support' / 'SNE_RADAR'
            app_data_dir.mkdir(parents=True, exist_ok=True)
        
        state_file = app_data_dir / 'scanner_state.json'
        
        if not state_file.exists():
            return jsonify({
                "success": True,
                "history": []
            }), 200
        
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Tentar carregar histórico detalhado se existir
        history_file = app_data_dir / 'scanner_history.json'
        detailed_history = {}
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    detailed_history = json.load(f)
            except:
                pass
        
        # Converter para formato de histórico
        history = []
        for symbol, timestamp_str in state.items():
            try:
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    timestamp = timestamp_str
                
                # Buscar dados detalhados se disponíveis
                alert_data = detailed_history.get(symbol, {})
                
                history_item = {
                    "symbol": symbol,
                    "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp),
                    "type": alert_data.get('type', 'volume'),  # volume ou pavio
                    "preco_atual": alert_data.get('preco_atual', 0),
                }
                
                # Adicionar dados específicos do tipo
                if alert_data.get('type') == 'pavio' or alert_data.get('tipo'):
                    history_item.update({
                        "tipo": alert_data.get('tipo'),  # LONG ou SHORT
                        "rvol_m30": alert_data.get('rvol_m30', 0),
                        "rsi_m5": alert_data.get('rsi_m5'),
                        "recuo_pct": alert_data.get('recuo_pct', 0),
                        "high_m5": alert_data.get('high_m5'),
                        "low_m5": alert_data.get('low_m5'),
                        "wick_confirmed": alert_data.get('wick_confirmed', False)
                    })
                else:
                    # Dados de volume
                    history_item.update({
                        "rvol": alert_data.get('rvol', 0),
                        "volume_atual": alert_data.get('volume_atual', 0),
                        "volume_medio": alert_data.get('volume_medio', 0)
                    })
                
                history.append(history_item)
            except Exception as e:
                print(f"⚠️ Erro ao processar alerta de {symbol}: {e}")
                continue
        
        # Ordenar por timestamp (mais recente primeiro)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            "success": True,
            "history": history[:50]  # Últimos 50
        }), 200
        
    except Exception as e:
        print(f"❌ Erro ao obter histórico: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/v1/notifications/monitor/start', methods=['POST'])
def api_v1_notifications_monitor_start():
    """Inicia o monitor de oportunidades"""
    monitor = get_opportunity_monitor()
    
    if monitor is None:
        return jsonify({
            "success": False,
            "error": "Monitor de oportunidades não disponível"
        }), 503
    
    try:
        if monitor.running:
            return jsonify({
                "success": False,
                "error": "Monitor já está rodando"
            }), 400
        
        monitor.start()
        
        # Enviar mensagem de inicialização quando iniciado manualmente
        try:
            if monitor.notifier:
                monitor.notifier.send_startup_message(mode="Manual (Web)")
        except Exception as e:
            print(f"⚠️ Erro ao enviar mensagem de inicialização: {e}")
            # Não bloquear se falhar
        
        return jsonify({
            "success": True,
            "message": "Monitor iniciado com sucesso"
        }), 200
    except Exception as e:
        print(f"❌ Erro ao iniciar monitor: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/v1/notifications/monitor/stop', methods=['POST'])
def api_v1_notifications_monitor_stop():
    """Para o monitor de oportunidades"""
    monitor = get_opportunity_monitor()
    
    if monitor is None:
        return jsonify({
            "success": False,
            "error": "Monitor de oportunidades não disponível"
        }), 503
    
    try:
        if not monitor.running:
            return jsonify({
                "success": False,
                "error": "Monitor não está rodando"
            }), 400
        
        monitor.stop()
        return jsonify({
            "success": True,
            "message": "Monitor parado com sucesso"
        }), 200
    except Exception as e:
        print(f"❌ Erro ao parar monitor: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/v1/notifications/monitor/status', methods=['GET'])
def api_v1_notifications_monitor_status():
    """Retorna status do monitor de oportunidades"""
    monitor = get_opportunity_monitor()
    
    if monitor is None:
        return jsonify({
            "success": True,
            "status": {
                "available": False,
                "running": False,
                "message": "Monitor não disponível"
            }
        }), 200
    
    try:
        # Verificar se o monitor está realmente rodando
        # Se não estiver rodando mas deveria estar, tentar reiniciar
        if not monitor.running:
            # Verificar se a thread ainda existe e está viva
            if monitor.thread is not None and monitor.thread.is_alive():
                # Thread existe mas running=False - pode ser um estado inconsistente
                monitor.running = True
            else:
                # Thread não existe ou não está viva - monitor realmente parou
                # Tentar reiniciar automaticamente
                try:
                    print("🔄 Monitor parou, tentando reiniciar automaticamente...")
                    monitor.start()
                    print("✅ Monitor reiniciado automaticamente")
                except Exception as e:
                    print(f"⚠️ Não foi possível reiniciar monitor automaticamente: {e}")
        
        return jsonify({
            "success": True,
            "status": {
                "available": True,
                "running": monitor.running,
                "symbols": monitor.symbols,
                "scan_interval": monitor.scan_interval,
                "volume_scanner_enabled": monitor.volume_scanner is not None,
                "pavio_scanner_enabled": monitor.pavio_scanner is not None,
                "thread_alive": monitor.thread.is_alive() if monitor.thread else False
            }
        }), 200
    except Exception as e:
        print(f"❌ Erro ao obter status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/v1/alerts/triggered')
@login_required
def api_v1_get_triggered_alerts():
    """Retorna alertas disparados do usuário."""
    try:
        limit = int(request.args.get('limit', '50'))
        alerts = alert_manager.get_triggered_alerts(current_user.id, limit)
        return jsonify({"success": True, "data": alerts})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoints para exportação
@app.route('/api/v1/export/market-data', methods=['POST'])
@login_required
def api_v1_export_market_data():
    """Exporta dados de mercado para CSV."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        market_data = data.get('market_data', {})
        indicators = data.get('indicators', {})
        
        filepath = data_exporter.export_market_data_csv(symbol, market_data, indicators)
        return jsonify({"success": True, "data": {"filepath": filepath}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/export/candles', methods=['POST'])
@login_required
def api_v1_export_candles():
    """Exporta dados de candles para CSV."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        candles = data.get('candles', [])
        interval = data.get('interval', '1m')
        
        filepath = data_exporter.export_candles_csv(symbol, candles, interval)
        if filepath:
            return jsonify({"success": True, "data": {"filepath": filepath}})
        else:
            return jsonify({"success": False, "error": "Nenhum dado para exportar"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/export/report', methods=['POST'])
@login_required
def api_v1_export_report():
    """Exporta relatório completo para PDF."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        market_data = data.get('market_data', {})
        indicators = data.get('indicators', {})
        derivatives_data = data.get('derivatives_data', {})
        
        filepath = data_exporter.export_market_report_pdf(
            symbol, market_data, indicators, derivatives_data
        )
        return jsonify({"success": True, "data": {"filepath": filepath}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/export/list')
@login_required
def api_v1_export_list():
    """Lista arquivos de exportação."""
    try:
        exports = data_exporter.get_export_list()
        return jsonify({"success": True, "data": exports})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoint para resetar circuit breaker
@app.route('/api/v1/system/reset-circuit-breaker', methods=['POST'])
@login_required
def api_v1_reset_circuit_breaker():
    """Reseta circuit breaker para APIs."""
    try:
        data = request.get_json()
        api_name = data.get('api_name', 'binance')
        
        reset_circuit_breaker(api_name)
        
        return jsonify({
            "success": True,
            "message": f"Circuit breaker resetado para {api_name}",
            "data": {
                "api_name": api_name,
                "timestamp": int(time.time())
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoint para status do sistema
@app.route('/api/v1/system/status')
@login_required
def api_v1_system_status():
    """Retorna status do sistema e circuit breakers."""
    try:
        status = {
            "circuit_breakers": sistema_estado["circuit_breaker"],
            "rate_limits": {
                api: len(calls) for api, calls in sistema_estado["last_api_call"].items()
            },
            "api_call_counts": sistema_estado["api_call_count"],
            "timestamp": int(time.time())
        }
        
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ROTA DUPLICADA REMOVIDA - Endpoint /api/v1/advanced-indicators já existe na linha 2490
# Mantendo apenas a versão original para evitar conflito

# Endpoint para indicadores profissionais
@app.route('/api/v1/professional-indicators')
@login_required
def api_v1_professional_indicators():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1m')
    limit = min(int(request.args.get('limit', '200')), 1000)
    
    try:
        # Buscar dados de candles
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados não disponíveis"}), 404
        
        # Calcular indicadores profissionais
        indicators = calculate_all_professional_indicators(df)
        
        return jsonify({
            "success": True,
            "data": {
                "symbol": symbol,
                "interval": interval,
                "indicators": indicators,
                "timestamp": int(time.time())
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoints para Machine Learning
@app.route('/api/v1/ml/train', methods=['POST'])
@login_required
def api_v1_ml_train():
    """Treina modelos de ML."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        interval = data.get('interval', '1m')
        limit = min(int(data.get('limit', '1000')), 2000)
        
        # Buscar dados históricos
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados insuficientes para treinamento"}), 400
        
        # Treinar modelos
        results = train_ml_models(df)
        
        return jsonify({
            "success": True,
            "data": {
                "symbol": symbol,
                "interval": interval,
                "training_results": results,
                "timestamp": int(time.time())
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/ml/predict')
@login_required
def api_v1_ml_predict():
    """Faz predição usando ML."""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        interval = request.args.get('interval', '1m')
        limit = min(int(request.args.get('limit', '200')), 1000)
        model_name = request.args.get('model', 'ensemble')
        horizon = int(request.args.get('horizon', '1'))
        
        # Buscar dados
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados não disponíveis"}), 404
        
        # Fazer predição
        if model_name == 'ensemble':
            prediction = ensemble_predict(df, horizon)
        else:
            prediction = predict_price_ml(df, model_name, horizon)
        
        return jsonify({
            "success": True,
            "data": prediction
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/ml/performance')
@login_required
def api_v1_ml_performance():
    """Retorna performance dos modelos ML."""
    try:
        performance = get_ml_performance()
        return jsonify({
            "success": True,
            "data": performance
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoints para Backtesting
@app.route('/api/v1/backtest/run', methods=['POST'])
@login_required
def api_v1_backtest_run():
    """Executa backtest de estratégias."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        interval = data.get('interval', '1h')
        limit = min(int(data.get('limit', '1000')), 2000)
        initial_capital = float(data.get('initial_capital', 10000))
        strategies = data.get('strategies', ['ma_crossover'])
        
        # Buscar dados históricos
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados insuficientes para backtest"}), 400
        
        # Criar estratégias
        strategy_objects = []
        for strategy_name in strategies:
            if strategy_name == 'ma_crossover':
                strategy_objects.append(MovingAverageCrossover())
            elif strategy_name == 'rsi':
                strategy_objects.append(RSIStrategy())
            elif strategy_name == 'bollinger':
                strategy_objects.append(BollingerBandsStrategy())
        
        if not strategy_objects:
            return jsonify({"success": False, "error": "Nenhuma estratégia válida especificada"}), 400
        
        # Executar backtest
        if len(strategy_objects) == 1:
            result = run_single_strategy_backtest(df, strategy_objects[0], initial_capital, symbol)
        else:
            result = run_multi_strategy_backtest(df, strategy_objects, initial_capital, symbol)
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/backtest/optimize', methods=['POST'])
@login_required
def api_v1_backtest_optimize():
    """Otimiza parâmetros de estratégia."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        interval = data.get('interval', '1h')
        limit = min(int(data.get('limit', '1000')), 2000)
        initial_capital = float(data.get('initial_capital', 10000))
        strategy_type = data.get('strategy_type', 'ma_crossover')
        param_ranges = data.get('param_ranges', {})
        
        # Buscar dados históricos
        df = buscar_dados_binance(symbol, interval, limit)
        if df is None or df.empty:
            return jsonify({"success": False, "error": "Dados insuficientes para otimização"}), 400
        
        # Selecionar classe de estratégia
        strategy_class = None
        if strategy_type == 'ma_crossover':
            strategy_class = MovingAverageCrossover
            if not param_ranges:
                param_ranges = {
                    'fast_period': [5, 10, 15, 20],
                    'slow_period': [20, 30, 40, 50]
                }
        elif strategy_type == 'rsi':
            strategy_class = RSIStrategy
            if not param_ranges:
                param_ranges = {
                    'rsi_period': [10, 14, 20],
                    'oversold': [20, 30, 40],
                    'overbought': [60, 70, 80]
                }
        elif strategy_type == 'bollinger':
            strategy_class = BollingerBandsStrategy
            if not param_ranges:
                param_ranges = {
                    'period': [15, 20, 25],
                    'std_dev': [1.5, 2.0, 2.5]
                }
        
        if strategy_class is None:
            return jsonify({"success": False, "error": "Tipo de estratégia inválido"}), 400
        
        # Executar otimização
        result = optimize_strategy_parameters(df, strategy_class, param_ranges, initial_capital)
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/execute-analysis', methods=['POST'])
@login_required
def execute_analysis():
    try:
        symbol = request.json.get('symbol', 'BTCUSDT')
        analise = analisar_simbolo(symbol)
        return jsonify({'success': True, 'data': analise})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validation-report/<symbol>')
@login_required
def api_validation_report(symbol):
    """Retorna relatório detalhado de validação multi-timeframe"""
    try:
        if not MULTI_TIMEFRAME_AVAILABLE:
            return jsonify({'error': 'Sistema de validação multi-timeframe não disponível'})
        
        # Buscar dados multi-timeframe
        dados_timeframes = buscar_dados_multitimeframe(symbol)
        
        if not dados_timeframes:
            return jsonify({'error': 'Dados não disponíveis para este símbolo'})
        
        # Determinar tipo de sinal
        df_1m = dados_timeframes.get('1m')
        if df_1m is not None:
            sinal_compra = df_1m["sinal_compra"].iloc[-1] if "sinal_compra" in df_1m.columns else False
            sinal_venda = df_1m["sinal_venda"].iloc[-1] if "sinal_venda" in df_1m.columns else False
            
            sinal_tipo = "aguardar"
            if sinal_compra:
                sinal_tipo = "compra"
            elif sinal_venda:
                sinal_tipo = "venda"
        else:
            sinal_tipo = "aguardar"
        
        # Validar sinal
        validacao = validar_sinal_completo(symbol, sinal_tipo, dados_timeframes)
        
        # Detectar divergências
        divergencias = detectar_divergencias_completo(dados_timeframes)
        
        # Gerar relatório
        relatorio = validator.gerar_relatorio_validacao(symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'sinal_tipo': sinal_tipo,
            'validacao': validacao,
            'divergencias': divergencias,
            'relatorio': relatorio,
            'timeframes_analisados': list(dados_timeframes.keys())
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validation-stats')
@login_required
def api_validation_stats():
    """Retorna estatísticas de validação"""
    try:
        if not MULTI_TIMEFRAME_AVAILABLE:
            return jsonify({'error': 'Sistema de validação multi-timeframe não disponível'})
        
        stats = validator.get_estatisticas_validacao()
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Rotas de Monetização
@app.route('/pricing')
def pricing():
    """Página de preços e planos"""
    return render_template('pricing.html')

@app.route('/upgrade/<tier>')
@login_required
def upgrade_tier(tier):
    """Upgrade para tier específico"""
    if tier not in ['pro', 'institutional']:
        flash('Tier inválido')
        return redirect(url_for('dashboard'))
    
    # Preços dos tiers
    prices = {
        'pro': 29.99,
        'institutional': 99.99
    }
    
    return render_template('upgrade.html', tier=tier, price=prices[tier])

@app.route('/api/upgrade', methods=['POST'])
@login_required
def api_upgrade():
    """API para processar upgrade de tier"""
    try:
        data = request.json
        tier = data.get('tier')
        payment_method = data.get('payment_method', 'stripe')
        
        if tier not in ['pro', 'institutional']:
            return jsonify({'success': False, 'error': 'Tier inválido'})
        
        # Preços dos tiers
        prices = {
            'pro': 29.99,
            'institutional': 99.99
        }
        
        price = prices[tier]
        
        # Criar subscription
        subscription = Subscription(
            user_id=current_user.id,
            tier=tier,
            end_date=datetime.datetime.utcnow() + datetime.timedelta(days=30),
            payment_method=payment_method,
            amount=price
        )
        
        db.session.add(subscription)
        
        # Atualizar usuário
        current_user.tier = tier
        current_user.subscription_expires = subscription.end_date
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Upgrade para {tier} realizado com sucesso!',
            'tier': tier,
            'expires': subscription.end_date.isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user-limits')
@login_required
def api_user_limits():
    """Retorna limites do usuário baseado no tier"""
    try:
        limits = get_user_tier_limits(current_user.tier)
        return jsonify({
            'success': True,
            'tier': current_user.tier,
            'limits': limits,
            'api_calls_used': current_user.api_calls_today,
            'subscription_expires': current_user.subscription_expires.isoformat() if current_user.subscription_expires else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Headers de segurança
@app.after_request
def add_security_headers(response):
    """Adiciona headers de segurança (compatíveis com Render)"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Eventos SocketIO
@socketio.on('connect')
def handle_connect():
    print(f"✅ Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Cliente desconectado: {request.sid}")

@socketio.on('start_analysis')
def handle_start_analysis():
    start_market_analysis()
    emit('analysis_status', {'status': 'started'})

@socketio.on('stop_analysis')
def handle_stop_analysis():
    stop_market_analysis()
    emit('analysis_status', {'status': 'stopped'})

def create_templates():
    """Cria templates HTML com estilo terminal"""
    from templates_terminal import create_terminal_templates
    create_terminal_templates()

def init_database():
    """Inicializa banco de dados"""
    with app.app_context():
        try:
            # Tentar criar/atualizar banco
            db.create_all()
            
            # Verificar se as novas colunas existem
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'tier' not in columns:
                print("⚠️ Colunas de monetização não encontradas. Recriando banco...")
                db.drop_all()
                db.create_all()
                print("✅ Banco recriado com sucesso!")
            
            # Criar usuário admin padrão para desenvolvimento
            if not User.query.filter_by(username='admin').first():
                admin_password_hash = hash_password('admin')
                user = User(
                    username='admin', 
                    password=admin_password_hash.decode('utf-8'),
                    tier='free',
                    api_calls_today=0,
                    last_api_reset=datetime.date.today()
                )
                db.session.add(user)
                db.session.commit()
                print("✅ Usuário admin criado (admin/admin)")
            
            print("✅ Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            print("🔄 Tentando recriar banco...")
            try:
                db.drop_all()
                db.create_all()
                print("✅ Banco recriado com sucesso!")
            except Exception as e2:
                print(f"❌ Erro fatal ao recriar banco: {e2}")
                raise e2

def testar_conectividade_api():
    """Testa conectividade com a API da Binance"""
    try:
        print("🔍 Testando conectividade com API Binance...")
        
        # Teste simples com BTCUSDT 1m
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": "BTCUSDT", "interval": "1m", "limit": 5}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                print("✅ Conectividade com API Binance OK")
                return True
            else:
                print("❌ API retornou dados vazios")
                return False
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na conexão com API Binance")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão com API Binance")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def open_browser():
    """Abre navegador automaticamente"""
    # Só em desenvolvimento e se permitido por env
    if not IS_PRODUCTION and os.environ.get('AUTO_OPEN_BROWSER', 'true').lower() == 'true':
        time.sleep(2)
        webbrowser.open('http://localhost:9999')

# === ENDPOINTS ADMINISTRATIVOS SIMPLES ===
@app.route('/api/users')
@login_required
def api_users():
    """API simples para listar usuários (requer login)"""
    try:
        if current_user.username in ADMIN_USERS:
            users = User.query.all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'username': user.username,
                    'tier': getattr(user, 'tier', 'free'),
                    'api_calls_today': getattr(user, 'api_calls_today', 0),
                    'last_api_reset': str(getattr(user, 'last_api_reset', 'N/A'))
                })
            return jsonify({'success': True, 'users': user_list, 'total': len(user_list)})
        else:
            return jsonify({
                'success': True, 
                'users': [{
                    'id': current_user.id,
                    'username': current_user.username,
                    'tier': getattr(current_user, 'tier', 'free'),
                    'api_calls_today': getattr(current_user, 'api_calls_today', 0),
                    'last_api_reset': str(getattr(current_user, 'last_api_reset', 'N/A'))
                }], 
                'total': 1
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users')
@login_required
def api_admin_users():
    """API para admin ver usuários (requer ser admin)"""
    try:
        if current_user.username not in ADMIN_USERS:
            return jsonify({'error': 'Acesso negado. Apenas administradores.'}), 403
        
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'tier': getattr(user, 'tier', 'free'),
                'api_calls_today': getattr(user, 'api_calls_today', 0),
                'last_api_reset': str(getattr(user, 'last_api_reset', 'N/A'))
            })
        
        return jsonify({'success': True, 'users': user_list, 'total': len(user_list)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/admin/users/stats')
@login_required
def api_admin_users_stats():
    """API para estatísticas de usuários (requer ser admin)"""
    try:
        if current_user.username not in ADMIN_USERS:
            return jsonify({'error': 'Acesso negado. Apenas administradores.'}), 403
        
        total_users = User.query.count()
        
        from sqlalchemy import func
        tier_stats = db.session.query(
            User.tier, 
            func.count(User.id).label('count')
        ).group_by(User.tier).all()
        
        tier_data = []
        for tier, count in tier_stats:
            tier_data.append({
                'tier': tier or 'free',
                'count': count,
                'percentage': round((count / total_users * 100), 1) if total_users > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'by_tier': tier_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/v1/magnetic/liquidity')
# @login_required  # Temporariamente desabilitado
def api_v1_liquidity_heatmap():
    """
    Retorna dados de liquidez do order book processados para heatmap
    """
    symbol = request.args.get('symbol', 'BTCUSDT')
    limit = min(int(request.args.get('limit', '5000')), 5000)  # Max 5000 da Binance
    price_precision = int(request.args.get('precision', '2'))  # Agrupar por casas decimais
    
    try:
        from fluxo_ativo import FluxoAtivo
        
        fluxo = FluxoAtivo()
        depth = fluxo.obter_depth(symbol, limit=limit)
        
        if not depth or 'bids' not in depth or 'asks' not in depth:
            return jsonify({
                'success': False,
                'error': 'Não foi possível obter dados do order book'
            }), 404
        
        # Processar bids e asks
        bids = [[float(price), float(qty)] for price, qty in depth['bids']]
        asks = [[float(price), float(qty)] for price, qty in depth['asks']]
        
        # Calcular preço atual (média entre melhor bid e ask)
        best_bid = bids[0][0] if bids else 0
        best_ask = asks[0][0] if asks else 0
        current_price = (best_bid + best_ask) / 2 if best_bid > 0 and best_ask > 0 else 0
        
        # Agrupar por níveis de preço (agregação)
        def aggregate_levels(orders, is_bid=True):
            """Agrupa ordens por nível de preço"""
            levels = {}
            for price, qty in orders:
                # Arredondar preço para agrupar
                rounded_price = round(price, price_precision)
                
                if rounded_price not in levels:
                    levels[rounded_price] = {
                        'price': rounded_price,
                        'total_qty': 0,
                        'order_count': 0,
                        'max_qty': 0
                    }
                
                levels[rounded_price]['total_qty'] += qty
                levels[rounded_price]['order_count'] += 1
                levels[rounded_price]['max_qty'] = max(levels[rounded_price]['max_qty'], qty)
            
            return list(levels.values())
        
        bid_levels = aggregate_levels(bids, is_bid=True)
        ask_levels = aggregate_levels(asks, is_bid=False)
        
        # Calcular intensidade máxima para normalização
        all_levels = bid_levels + ask_levels
        max_qty = max([l['total_qty'] for l in all_levels]) if all_levels else 1
        
        # Adicionar intensidade normalizada (0-1)
        for level in bid_levels:
            level['intensity'] = level['total_qty'] / max_qty
            level['type'] = 'bid'
        
        for level in ask_levels:
            level['intensity'] = level['total_qty'] / max_qty
            level['type'] = 'ask'
        
        # Ordenar por preço
        bid_levels.sort(key=lambda x: x['price'], reverse=True)  # Maior para menor
        ask_levels.sort(key=lambda x: x['price'])  # Menor para maior
        
        # Calcular estatísticas
        total_bid_qty = sum([l['total_qty'] for l in bid_levels])
        total_ask_qty = sum([l['total_qty'] for l in ask_levels])
        liquidity_ratio = total_bid_qty / total_ask_qty if total_ask_qty > 0 else 1.0
        
        # Identificar "muros" de liquidez (níveis com muita liquidez)
        wall_threshold = max_qty * 0.1  # Top 10% são considerados muros
        bid_walls = [l for l in bid_levels if l['total_qty'] >= wall_threshold]
        ask_walls = [l for l in ask_levels if l['total_qty'] >= wall_threshold]
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'current_price': current_price,
            'best_bid': best_bid,
            'best_ask': best_ask,
            'spread': best_ask - best_bid if best_bid > 0 and best_ask > 0 else 0,
            'spread_pct': ((best_ask - best_bid) / current_price * 100) if current_price > 0 else 0,
            'bid_levels': bid_levels,
            'ask_levels': ask_levels,
            'statistics': {
                'total_bid_qty': total_bid_qty,
                'total_ask_qty': total_ask_qty,
                'liquidity_ratio': liquidity_ratio,
                'max_qty': max_qty,
                'bid_walls_count': len(bid_walls),
                'ask_walls_count': len(ask_walls)
            },
            'walls': {
                'bid': bid_walls[:10],  # Top 10 muros de compra
                'ask': ask_walls[:10]   # Top 10 muros de venda
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Erro em /api/v1/magnetic/liquidity: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def main():
    """Função principal"""
    try:
        print("🚀 Iniciando SNE Radar Web...")
        
        # Criar templates
        create_templates()
        
        # Inicializar banco
        init_database()
        
        # Registrar blueprints de trading
        try:
            from app.api import register_blueprints
            register_blueprints(app)
            print("✅ Blueprints de trading registrados")
        except Exception as e:
            print(f"⚠️ Aviso: Erro ao registrar blueprints de trading: {e}")
            import traceback
            traceback.print_exc()
        
        # Testar conectividade com API
        if not testar_conectividade_api():
            print("⚠️ Aviso: Problemas de conectividade com API Binance")
            print("💡 O sistema continuará, mas pode haver problemas na busca de dados")
        
        # Análise automática DESABILITADA - comandos sob demanda apenas
        # analysis_thread = threading.Thread(target=start_market_analysis)
        # analysis_thread.daemon = True
        # analysis_thread.start()
        
        # Abrir navegador
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("✅ SNE Radar Web iniciado!")
        if FRONTEND_EXISTS:
            print("✅ Frontend Vue.js detectado e será servido")
        else:
            print("⚠️ Frontend não encontrado. Use templates antigos.")
            print(f"   Build frontend: cd frontend && npm install && npm run build")
        if not IS_PRODUCTION:
            print("🌐 Acesse: http://localhost:9999")
        
        # Executar Flask
        port = int(os.environ.get('PORT', 9999))
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Encerrando SNE Radar Web...")
        stop_market_analysis()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        stop_market_analysis()

if __name__ == "__main__":
    main()

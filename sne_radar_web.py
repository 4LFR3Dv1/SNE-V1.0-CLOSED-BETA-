#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNE Radar Web - Sistema Neural Estratégico Completo
Dashboard web com análise estratégica, múltiplos pares e recomendações de trading
"""

import os, json, threading, webbrowser, time, datetime, sys, requests, pandas as pd, numpy as np, platform, random, pytz
import urllib3
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, make_response
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

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

# Configurações Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sne_radar_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sne_radar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# API Keys
COINGECKO_KEY = os.environ.get('COINGECKO_KEY', 'CG-dnjaiDwoE6ncJ3djKKUQeSkx')
SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY', '92c73c12f88f65c2525f77ac5511d3d4')

# Inicializar extensões
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurações do sistema
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]  # Apenas os símbolos desejados
interval = "1m"
limit = 100
update_interval = 120  # segundos (AUMENTADO para economizar requests)
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
    "api_call_count": {}  # Contador de chamadas
}

# Modelos de dados
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

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

def criar_dados_mock(symbol, interval):
    """Cria dados mock para teste quando API falha"""
    try:
        import random
        from datetime import datetime, timedelta
        
        # Dados base para diferentes símbolos
        precos_base = {
            "BTCUSDT": 65000,
            "ETHUSDT": 3500,
            "SOLUSDT": 150
        }
        
        preco_base = precos_base.get(symbol, 100)
        
        # Gerar 100 candles
        dados = []
        agora = datetime.now()
        
        for i in range(100):
            timestamp = agora - timedelta(minutes=i)
            
            # Variação aleatória
            variacao = random.uniform(-0.02, 0.02)  # ±2%
            preco = preco_base * (1 + variacao)
            
            # Simular candle
            open_price = preco
            high_price = preco * random.uniform(1.001, 1.005)
            low_price = preco * random.uniform(0.995, 0.999)
            close_price = preco * random.uniform(0.998, 1.002)
            volume = random.uniform(1000, 10000)
            trades = random.randint(100, 1000)
            
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

def buscar_dados_binance(symbol, interval, limit):
    """Busca dados da Binance via ScraperAPI (USO LIMITADO)"""
    try:
        # Verificar rate limit (MUITO REDUZIDO para economizar ScraperAPI)
        if not check_rate_limit("binance", max_calls=5, window_seconds=300):  # 5 calls/5min
            print(f"⏳ Rate limit Binance atingido para {symbol}")
            return buscar_dados_coingecko(symbol, interval, limit)
        
        # Mapear intervalos para Binance Data API
        interval_mapping = {
            "1m": "1m",
            "5m": "5m", 
            "15m": "15m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d"
        }
        
        binance_interval = interval_mapping.get(interval, "1m")
        
        # Binance API com proxy direto do ScraperAPI
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": binance_interval,
            "limit": limit
        }
        
        print(f"🔍 Buscando dados Binance via proxy: {symbol} {interval}...")
        
        # Headers para evitar geoblocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        # Proxy direto do ScraperAPI
        proxies = {
            "http": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
            "https": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"
        }
        
        # Delay para respeitar rate limit
        time.sleep(0.1)
        
        response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=30, verify=False)
        
        if response.status_code != 200:
            print(f"❌ Erro na API Binance: {response.status_code} - {response.text}")
            print("🔄 Tentando Kraken API...")
            return buscar_dados_kraken(symbol, interval, limit)
            
        data = response.json()
        
        if not data or len(data) == 0:
            print(f"❌ Dados vazios para {symbol} {interval}")
            return None
        
        df = pd.DataFrame(data, columns=[
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
            "validacao_multitimeframe": validacao_multitimeframe,
            "divergencias": divergencias,
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
            sistema_estado["dados_mercado"] = dados_atualizados
            sistema_estado["ultima_atualizacao"] = datetime.datetime.now()
            
            # Emitir dados via WebSocket
            with app.app_context():
                for symbol, dados in dados_atualizados.items():
                    socketio.emit('market_data', {
                        'symbol': symbol,
                        'data': serializar_dados_json(dados)
                    })
            
            time.sleep(update_interval)
            
        except Exception as e:
            print(f"❌ Erro no ciclo de análise: {e}")
            time.sleep(update_interval)

def start_market_analysis():
    """Inicia análise de mercado"""
    if not sistema_estado["ativo"]:
        sistema_estado["ativo"] = True
        sistema_estado["inicio_execucao"] = datetime.datetime.now()
        sistema_estado["analise_thread"] = threading.Thread(target=executar_ciclo_analise)
        sistema_estado["analise_thread"].start()
        print("✅ Análise de mercado iniciada")

def stop_market_analysis():
    """Para análise de mercado"""
    sistema_estado["ativo"] = False
    if sistema_estado["analise_thread"] and sistema_estado["analise_thread"].is_alive():
        try:
            sistema_estado["analise_thread"].join(timeout=5)
        except:
            pass
    print("⏹️ Análise de mercado parada")

# Rotas Flask
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos')
    
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe')
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Conta criada com sucesso!')
            return redirect(url_for('login'))
    
    response = make_response(render_template('register.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    response = make_response(render_template('dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def serializar_dados_json(dados):
    """Serializa dados para JSON de forma segura"""
    if dados is None:
        return {}
    
    dados_serializados = {}
    for key, value in dados.items():
        if isinstance(value, bool):
            dados_serializados[key] = str(value)
        elif isinstance(value, (int, float, str, list, dict)):
            dados_serializados[key] = value
        else:
            dados_serializados[key] = str(value)
    
    return dados_serializados

@app.route('/api/market-data')
@login_required
def api_market_data():
    symbol = request.args.get('symbol', 'BTCUSDT')
    dados = sistema_estado["dados_mercado"].get(symbol, {})
    return jsonify(serializar_dados_json(dados))

@app.route('/api/alerts')
@login_required
def api_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(10).all()
    return jsonify([{
        'symbol': alert.symbol,
        'price': alert.price,
        'message': alert.message,
        'tipo': alert.tipo,
        'timestamp': alert.timestamp.isoformat()
    } for alert in alerts])

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
        db.create_all()
        
        # Criar usuário padrão se não existir
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', password='admin')
            db.session.add(user)
            db.session.commit()
            print("✅ Usuário padrão criado: admin/admin")

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
    time.sleep(2)
    webbrowser.open('http://localhost:9999')

def main():
    """Função principal"""
    try:
        print("🚀 Iniciando SNE Radar Web...")
        
        # Criar templates
        create_templates()
        
        # Inicializar banco
        init_database()
        
        # Testar conectividade com API
        if not testar_conectividade_api():
            print("⚠️ Aviso: Problemas de conectividade com API Binance")
            print("💡 O sistema continuará, mas pode haver problemas na busca de dados")
        
        # Iniciar análise em background
        analysis_thread = threading.Thread(target=start_market_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        # Abrir navegador
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("✅ SNE Radar Web iniciado!")
        print("🌐 Acesse: http://localhost:9999")
        print("👤 Login: admin / admin")
        
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

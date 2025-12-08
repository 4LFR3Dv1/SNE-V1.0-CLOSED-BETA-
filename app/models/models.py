"""
Modelos de dados do SNE Radar
Extraídos do sne_radar_web.py para organização modular
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

# Será inicializado no app factory
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Modelo de usuário"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tier = db.Column(db.String(20), default='free')  # free, pro, institutional
    api_calls_today = db.Column(db.Integer, default=0)
    last_api_reset = db.Column(db.Date, default=datetime.date.today)
    subscription_expires = db.Column(db.DateTime, nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=True)


class MarketData(db.Model):
    """Modelo de dados de mercado"""
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
    """Modelo de alerta"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    message = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Subscription(db.Model):
    """Modelo de assinatura"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tier = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired


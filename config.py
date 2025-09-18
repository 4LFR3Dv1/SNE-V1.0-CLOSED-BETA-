#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração centralizada de ENV e feature flags do SNE Radar Web
"""

import os


def get_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return str(value).lower() in ("1", "true", "yes", "on")


class Settings:
    # Ambiente
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development').lower()
    IS_PRODUCTION = FLASK_ENV == 'production'

    # App
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS')

    # Atualização/coleta
    UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', '30'))
    BINANCE_CALLS_PER_WINDOW = int(os.environ.get('BINANCE_CALLS_PER_WINDOW', '30'))
    BINANCE_WINDOW_SECONDS = int(os.environ.get('BINANCE_WINDOW_SECONDS', '60'))
    BINANCE_CB_THRESHOLD = int(os.environ.get('BINANCE_CB_THRESHOLD', '3'))
    BINANCE_CB_COOLDOWN = int(os.environ.get('BINANCE_CB_COOLDOWN', '60'))

    # APIs externas
    COINGECKO_KEY = os.environ.get('COINGECKO_KEY')
    SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY')
    COINMARKETCAP_API_KEY = os.environ.get('COINMARKETCAP_API_KEY')
    COINGLASS_API_KEY = os.environ.get('COINGLASS_API_KEY')

    # Feature flags
    ENABLE_COINGLASS = get_bool('ENABLE_COINGLASS', False)
    ENABLE_CMC = get_bool('ENABLE_CMC', False)
    ENABLE_TA_SUMMARY = get_bool('ENABLE_TA_SUMMARY', False)

    # TTLs/Timeouts
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '12'))
    COINGLASS_TTL = int(os.environ.get('COINGLASS_TTL', '60'))
    CMC_TTL = int(os.environ.get('CMC_TTL', '60'))

    # Admins
    ADMIN_USERS = set([u.strip() for u in os.environ.get('ADMIN_USERS', 'admin').split(',') if u.strip()])



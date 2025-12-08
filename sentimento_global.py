#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SENTIMENTO GLOBAL
Análise de sentiment, funding, correlações
"""

import requests


def analisar_sentiment(symbol='BTCUSDT'):
    """Análise de sentimento do mercado"""
    return {
        'fear_greed': obter_fear_greed(),
        'funding_rate': obter_funding_rate(symbol),
        'open_interest': obter_open_interest(symbol),
        'correlacoes': calcular_correlacoes()
    }


def obter_fear_greed():
    """Fear & Greed Index (simulado - API real requer chave)"""
    # Em produção, usar API real: alternative.me/crypto/fear-and-greed-index/
    return {
        'valor': 72,
        'classificacao': 'Greed',
        'interpretacao': 'Mercado otimista mas não extremo'
    }


def obter_funding_rate(symbol):
    """Funding rate da Binance Futures"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/fundingRate"
        params = {"symbol": symbol, "limit": 1}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                rate = float(data[0]['fundingRate']) * 100
                return {
                    'rate': round(rate, 4),
                    'viés': 'Bullish' if rate > 0.01 else 'Bearish' if rate < -0.01 else 'Neutro'
                }
        return {'rate': 0, 'viés': 'Indisponível'}
    except:
        return {'rate': 0, 'viés': 'Erro'}


def obter_open_interest(symbol):
    """Open Interest (simulado)"""
    return {
        'valor': '$18.2B',
        'variacao_24h': '+8%',
        'interpretacao': 'Crescente (bullish)'
    }


def calcular_correlacoes():
    """Correlações com outros ativos (simplificado)"""
    return {
        'BTC/ETH': 0.85,
        'BTC/S&P500': 0.42,
        'BTC/Gold': -0.15,
        'BTC/DXY': -0.68,
        'interpretacao': 'Risk-on ativo'
    }






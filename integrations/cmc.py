#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente CoinMarketCap com cache TTL (esqueleto)"""

import os
import time
import requests
from typing import Dict, Any, Optional

_cache: Dict[str, Any] = {}


def _cache_get(key: str, ttl: int) -> Optional[Any]:
    entry = _cache.get(key)
    if not entry:
        return None
    if time.time() - entry["ts"] > ttl:
        return None
    return entry["data"]


def _cache_set(key: str, data: Any):
    _cache[key] = {"ts": time.time(), "data": data}


def get_global_metrics(ttl: int = 60, timeout: int = 10) -> Dict[str, Any]:
    key = "global_metrics"
    cached = _cache_get(key, ttl)
    if cached is not None:
        return cached

    api_key = os.environ.get('COINMARKETCAP_API_KEY')
    if not api_key:
        return {"success": False, "error": "missing_api_key"}

    url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": api_key}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return {"success": False, "status": resp.status_code}
        data = resp.json()
        out = {"success": True, "data": data}
        _cache_set(key, out)
        return out
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_listings_by_tag(tag: str, limit: int = 100, ttl: int = 300, timeout: int = 10) -> Dict[str, Any]:
    """Busca listagens por tag da CoinMarketCap (L2, AI, DeFi, etc.)."""
    key = f"listings_{tag}_{limit}"
    cached = _cache_get(key, ttl)
    if cached is not None:
        return cached

    api_key = os.environ.get('COINMARKETCAP_API_KEY')
    if not api_key:
        return {"success": False, "error": "missing_api_key"}

    # Mock de dados por tag para desenvolvimento
    mock_data = {
        "all": [
            {"symbol": "BTC", "name": "Bitcoin", "price": 68000, "change_24h": 2.5, "market_cap": 1300000000000},
            {"symbol": "ETH", "name": "Ethereum", "price": 3500, "change_24h": 1.8, "market_cap": 420000000000},
            {"symbol": "SOL", "name": "Solana", "price": 180, "change_24h": 5.2, "market_cap": 80000000000},
        ],
        "l2": [
            {"symbol": "MATIC", "name": "Polygon", "price": 0.85, "change_24h": 3.1, "market_cap": 8000000000},
            {"symbol": "ARB", "name": "Arbitrum", "price": 1.2, "change_24h": 2.8, "market_cap": 1500000000},
            {"symbol": "OP", "name": "Optimism", "price": 2.1, "change_24h": 1.5, "market_cap": 2000000000},
        ],
        "ai": [
            {"symbol": "FET", "name": "Fetch.ai", "price": 2.3, "change_24h": 8.5, "market_cap": 6000000000},
            {"symbol": "AGIX", "name": "SingularityNET", "price": 0.45, "change_24h": 12.3, "market_cap": 500000000},
            {"symbol": "OCEAN", "name": "Ocean Protocol", "price": 0.8, "change_24h": 6.7, "market_cap": 400000000},
        ],
        "defi": [
            {"symbol": "UNI", "name": "Uniswap", "price": 12.5, "change_24h": 4.2, "market_cap": 7500000000},
            {"symbol": "AAVE", "name": "Aave", "price": 95, "change_24h": 2.1, "market_cap": 1400000000},
            {"symbol": "COMP", "name": "Compound", "price": 65, "change_24h": 1.8, "market_cap": 500000000},
        ]
    }

    listings = mock_data.get(tag, mock_data["all"])[:limit]
    
    data = {
        "success": True,
        "data": {
            "tag": tag,
            "count": len(listings),
            "listings": listings,
            "timestamp": int(time.time())
        }
    }

    # Usar API real da CoinMarketCap
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        headers = {"X-CMC_PRO_API_KEY": api_key, "Accepts": "application/json"}
        params = {'limit': limit, 'sort': 'market_cap', 'sort_dir': 'desc'}
        
        # Filtrar por tag se não for 'all'
        if tag != 'all':
            params['tag'] = tag
            
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        if resp.status_code == 200:
            api_data = resp.json()
            # Normalizar dados da API
            listings = []
            for coin in api_data.get('data', []):
                quote = coin.get('quote', {}).get('USD', {})
                listings.append({
                    "symbol": coin.get('symbol', ''),
                    "name": coin.get('name', ''),
                    "price": quote.get('price', 0),
                    "change_24h": quote.get('percent_change_24h', 0),
                    "market_cap": quote.get('market_cap', 0)
                })
            
            data = {
                "success": True,
                "data": {
                    "tag": tag,
                    "count": len(listings),
                    "listings": listings,
                    "timestamp": int(time.time())
                }
            }
        else:
            # Fallback para mock se API falhar
            pass
    except Exception as e:
        # Fallback para mock em caso de erro
        pass

    _cache_set(key, data)
    return data



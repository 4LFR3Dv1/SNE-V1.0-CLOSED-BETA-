#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente CoinGlass com cache TTL (esqueleto)"""

import time
import os
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


def get_funding(symbol: str, ttl: int = 60, timeout: int = 10) -> Dict[str, Any]:
    key = f"funding:{symbol}"
    cached = _cache_get(key, ttl)
    if cached is not None:
        return cached

    api_key = os.environ.get('COINGLASS_API_KEY')
    if not api_key:
        return {"success": False, "error": "missing_api_key"}

    # Endpoint real da CoinGlass
    url = "https://open-api.coinglass.com/api/pro/v1/futures/fundingRate"
    headers = {"accept": "application/json", "coinglassSecret": api_key}
    params = {"symbol": symbol, "limit": 50}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        if resp.status_code != 200:
            return {"success": False, "status": resp.status_code}
        data = resp.json()
        out = {"success": True, "data": data}
        _cache_set(key, out)
        return out
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_oi(symbol: str, ttl: int = 60, timeout: int = 10) -> Dict[str, Any]:
    key = f"oi:{symbol}"
    cached = _cache_get(key, ttl)
    if cached is not None:
        return cached
    api_key = os.environ.get('COINGLASS_API_KEY')
    if not api_key:
        return {"success": False, "error": "missing_api_key"}
    # Endpoint real da CoinGlass
    url = "https://open-api.coinglass.com/api/pro/v1/futures/openInterest"
    headers = {"accept": "application/json", "coinglassSecret": api_key}
    params = {"symbol": symbol, "limit": 50}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        if resp.status_code != 200:
            return {"success": False, "status": resp.status_code}
        data = resp.json()
        # Normalização placeholder
        out = {"success": True, "data": data}
        _cache_set(key, out)
        return out
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_lsr(symbol: str, ttl: int = 60, timeout: int = 10) -> Dict[str, Any]:
    key = f"lsr:{symbol}"
    cached = _cache_get(key, ttl)
    if cached is not None:
        return cached
    api_key = os.environ.get('COINGLASS_API_KEY')
    if not api_key:
        return {"success": False, "error": "missing_api_key"}
    url = "https://open-api.coinglass.com/api/pro/v1/futures/longShortRatio"
    headers = {"accept": "application/json", "coinglassSecret": api_key}
    params = {"symbol": symbol, "limit": 50}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        if resp.status_code != 200:
            return {"success": False, "status": resp.status_code}
        data = resp.json()
        out = {"success": True, "data": data}
        _cache_set(key, out)
        return out
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_liquidations(symbol: str, ttl: int = 60, timeout: int = 10) -> Dict[str, Any]:
    key = f"liq:{symbol}"
    cached = _cache_get(key, ttl)
    if cached is not None:
        return cached
    api_key = os.environ.get('COINGLASS_API_KEY')
    if not api_key:
        return {"success": False, "error": "missing_api_key"}
    url = "https://open-api.coinglass.com/api/pro/v1/futures/liquidation"
    headers = {"accept": "application/json", "coinglassSecret": api_key}
    params = {"symbol": symbol, "limit": 50}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        if resp.status_code != 200:
            return {"success": False, "status": resp.status_code}
        data = resp.json()
        out = {"success": True, "data": data}
        _cache_set(key, out)
        return out
    except Exception as e:
        return {"success": False, "error": str(e)}



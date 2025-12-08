#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner de Volume Explosivo
Detecta RVOL > 2.0 (Fase 1)
"""

import sys
import time
import requests
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

# Adicionar diretório raiz ao path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    from sne_radar_web import buscar_dados_binance
except ImportError:
    print("⚠️ sne_radar_web não encontrado. Usando busca direta.")
    buscar_dados_binance = None


class VolumeScanner:
    """Scanner de volume explosivo"""
    
    def __init__(self, rvol_threshold: float = 2.0):
        """
        Inicializa scanner de volume
        
        Args:
            rvol_threshold: Threshold de volume relativo (padrão: 2.0x)
        """
        self.rvol_threshold = rvol_threshold
        self.last_scans = {}  # Cache de últimos scans
    
    def scan_symbol(self, symbol: str, timeframe: str = '5m') -> Optional[Dict]:
        """
        Escaneia um símbolo para volume explosivo
        
        Args:
            symbol: Símbolo a escanear (ex: BTCUSDT)
            timeframe: Timeframe (padrão: 5m)
        
        Returns:
            Dict com dados do alerta ou None se não disparou
        """
        max_retries = 3
        retry_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                # Buscar dados com timeout
                if buscar_dados_binance:
                    df = buscar_dados_binance(
                        symbol, 
                        timeframe, 
                        limit=21, 
                        skip_rate_limit=True
                    )
                else:
                    # Fallback: busca direta (se necessário)
                    df = self._buscar_dados_direto(symbol, timeframe, 21)
                
                if df is None or len(df) < 21:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None
                
                # Calcular volume médio (excluindo última vela)
                volume_medio = df['volume'].iloc[:-1].mean()
                volume_atual = df['volume'].iloc[-1]
                
                # Calcular RVOL (Relative Volume)
                rvol = volume_atual / volume_medio if volume_medio > 0 else 0
                
                # Verificar condição
                if rvol >= self.rvol_threshold:
                    return {
                        'triggered': True,
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'rvol': float(rvol),
                        'volume_atual': float(volume_atual),
                        'volume_medio': float(volume_medio),
                        'preco_atual': float(df['close'].iloc[-1]),
                        'timestamp': datetime.now()
                    }
                
                return None
                
            except requests.exceptions.ConnectionError as e:
                print(f"⚠️ Erro de conexão ao escanear {symbol} (tentativa {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Backoff exponencial
                    continue
                return None
                
            except requests.exceptions.Timeout as e:
                print(f"⚠️ Timeout ao escanear {symbol} (tentativa {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
                
            except Exception as e:
                print(f"❌ Erro inesperado ao escanear {symbol}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
        
        return None
    
    def _buscar_dados_direto(self, symbol: str, interval: str, limit: int):
        """Fallback: busca direta da Binance (se necessário)"""
        try:
            import pandas as pd
            
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                # Converter tipos
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                # Converter timestamp
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                return df
        except Exception as e:
            print(f"❌ Erro na busca direta: {e}")
        
        return None
    
    def scan_multiple(self, symbols: List[str], timeframe: str = '5m') -> List[Dict]:
        """Escaneia múltiplos símbolos"""
        alerts = []
        
        for symbol in symbols:
            result = self.scan_symbol(symbol, timeframe)
            if result and result.get('triggered'):
                alerts.append(result)
        
        return alerts




#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner "Caçador de Pavio"
Detecta Volume M30 Explosivo + RSI M5 Extremo + Confirmação de Wick
"""

import sys
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

# Adicionar diretório raiz ao path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    from sne_radar_web import buscar_dados_binance
except ImportError:
    print("⚠️ sne_radar_web não encontrado. Usando busca direta.")
    buscar_dados_binance = None


class PavioScanner:
    """Scanner completo de agulhadas em formação"""
    
    def __init__(self, 
                 volume_threshold: float = 2.5,
                 rsi_long_threshold: float = 25,
                 rsi_short_threshold: float = 75,
                 wick_confirmation_pct: float = 0.3):
        """
        Inicializa scanner de pavio
        
        Args:
            volume_threshold: Threshold de volume M30 (padrão: 2.5x)
            rsi_long_threshold: RSI mínimo para LONG (padrão: 25)
            rsi_short_threshold: RSI máximo para SHORT (padrão: 75)
            wick_confirmation_pct: % mínimo de recuo para confirmar wick (padrão: 0.3%)
        """
        self.volume_threshold = volume_threshold
        self.rsi_long_threshold = rsi_long_threshold
        self.rsi_short_threshold = rsi_short_threshold
        self.wick_confirmation_pct = wick_confirmation_pct
    
    def calcular_rsi(self, closes: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcula RSI (Relative Strength Index)
        
        Args:
            closes: Série de preços de fechamento
            period: Período do RSI (padrão: 14)
        
        Returns:
            Série com valores de RSI
        """
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def scan_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Escaneia símbolo para agulhada em formação
        
        Args:
            symbol: Símbolo a escanear (ex: BTCUSDT)
        
        Returns:
            Dict com dados do alerta ou None
        """
        max_retries = 3
        retry_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                # 1. Buscar dados M30 (para volume)
                if buscar_dados_binance:
                    df_m30 = buscar_dados_binance(symbol, '30m', 21, skip_rate_limit=True)
                else:
                    df_m30 = self._buscar_dados_direto(symbol, '30m', 21)
                
                if df_m30 is None or len(df_m30) < 21:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None
                
                # 2. Buscar dados M5 (para RSI)
                if buscar_dados_binance:
                    df_m5 = buscar_dados_binance(symbol, '5m', 15, skip_rate_limit=True)
                else:
                    df_m5 = self._buscar_dados_direto(symbol, '5m', 15)
                
                if df_m5 is None or len(df_m5) < 15:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None
                
                # 3. Calcular Volume M30
                volume_medio_m30 = df_m30['volume'].iloc[:-1].mean()  # Excluir última vela
                volume_atual_m30 = df_m30['volume'].iloc[-1]
                rvol_m30 = volume_atual_m30 / volume_medio_m30 if volume_medio_m30 > 0 else 0
                
                # 4. Calcular RSI M5
                rsi_series = self.calcular_rsi(df_m5['close'], period=14)
                rsi_atual = rsi_series.iloc[-1]
                
                # 5. Verificar condições de volume
                volume_ok = rvol_m30 >= self.volume_threshold
                
                if not volume_ok:
                    return None  # Sem volume explosivo, não há agulhada
                
                # 6. Verificar RSI extremo e confirmação de wick
                triggered = False
                tipo = None
                wick_confirmed = False
                recuo_pct = 0.0
                
                # Dados da última vela M5
                last_candle_m5 = df_m5.iloc[-1]
                high_m5 = last_candle_m5['high']
                low_m5 = last_candle_m5['low']
                close_m5 = last_candle_m5['close']
                open_m5 = last_candle_m5['open']
                
                # Verificar SHORT: RSI > 75 E preço já recuou da máxima
                if rsi_atual >= self.rsi_short_threshold:
                    # Calcular recuo da máxima (wick superior)
                    recuo_pct = ((high_m5 - close_m5) / high_m5) * 100 if high_m5 > 0 else 0
                    
                    # Confirmação: Preço já recuou pelo menos X% da máxima
                    if recuo_pct >= self.wick_confirmation_pct:
                        triggered = True
                        tipo = 'SHORT'
                        wick_confirmed = True
                    # else: Ainda subindo sem freio - aguardar confirmação
                
                # Verificar LONG: RSI < 25 E preço já subiu do mínimo
                elif rsi_atual <= self.rsi_long_threshold:
                    # Calcular recuo do mínimo (wick inferior)
                    recuo_pct = ((close_m5 - low_m5) / low_m5) * 100 if low_m5 > 0 else 0
                    
                    # Confirmação: Preço já subiu pelo menos X% do mínimo
                    if recuo_pct >= self.wick_confirmation_pct:
                        triggered = True
                        tipo = 'LONG'
                        wick_confirmed = True
                    # else: Ainda caindo sem freio - aguardar confirmação
                
                if triggered:
                    return {
                        'triggered': True,
                        'symbol': symbol,
                        'tipo': tipo,
                        'rvol_m30': float(rvol_m30),
                        'rsi_m5': float(rsi_atual),
                        'preco_atual': float(close_m5),
                        'volume_atual_m30': float(volume_atual_m30),
                        'volume_medio_m30': float(volume_medio_m30),
                        'wick_confirmed': wick_confirmed,
                        'recuo_pct': float(recuo_pct),
                        'high_m5': float(high_m5),
                        'low_m5': float(low_m5),
                        'open_m5': float(open_m5),
                        'close_m5': float(close_m5),
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
                import traceback
                traceback.print_exc()
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
        
        return None
    
    def _buscar_dados_direto(self, symbol: str, interval: str, limit: int):
        """Fallback: busca direta da Binance (se necessário)"""
        try:
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


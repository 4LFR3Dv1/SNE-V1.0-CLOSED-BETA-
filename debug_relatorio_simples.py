#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG RELATÓRIO SIMPLES - Identifica onde está o erro 'close'
"""

import sys
import os
import traceback
import requests
import pandas as pd

def coletar_dados_simples(symbol, interval, limit=200):
    """Coleta dados da Binance sem dependências externas"""
    try:
        interval = interval.lower()
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if not data or len(data) == 0:
                return None
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype({
                'timestamp': 'datetime64[ms]',
                'open': float, 'high': float, 'low': float,
                'close': float, 'volume': float
            })
            
            return df
        return None
    except Exception as e:
        print(f"Erro ao coletar dados: {e}")
        return None

def calcular_indicadores_simples(df):
    """Calcula indicadores básicos"""
    try:
        # EMAs básicas
        df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
        df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
        
        # RSI básico
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    except Exception as e:
        print(f"Erro ao calcular indicadores: {e}")
        return df

def debug_relatorio_simples():
    """Debug simplificado para identificar o erro"""
    print("🔍 DEBUG RELATÓRIO SIMPLES - Identificando erro 'close'")
    
    try:
        # 1. Coletar dados
        print("\n1️⃣ Coletando dados...")
        dados = coletar_dados_simples("BTCUSDT", "1h")
        if dados is None:
            print("❌ Falha na coleta de dados")
            return
        
        print(f"✅ Dados coletados: {len(dados)} candles")
        print(f"📊 Colunas disponíveis: {list(dados.columns)}")
        
        # 2. Calcular indicadores
        print("\n2️⃣ Calculando indicadores...")
        dados = calcular_indicadores_simples(dados)
        print(f"✅ Indicadores calculados")
        print(f"📊 Colunas após indicadores: {list(dados.columns)}")
        
        # 3. Verificar se 'close' existe
        if 'close' not in dados.columns:
            print("❌ Coluna 'close' não encontrada!")
            return
        
        print(f"✅ Coluna 'close' encontrada: {dados['close'].iloc[-1]}")
        
        # 4. Testar acesso aos indicadores
        print("\n3️⃣ Testando acesso aos indicadores...")
        try:
            ema8 = dados['EMA8'].iloc[-1]
            ema21 = dados['EMA21'].iloc[-1]
            rsi = dados['RSI'].iloc[-1]
            print(f"✅ EMA8: {ema8}, EMA21: {ema21}, RSI: {rsi}")
        except Exception as e:
            print(f"❌ Erro ao acessar indicadores: {e}")
            traceback.print_exc()
            return
        
        # 5. Testar funções que podem causar erro
        print("\n4️⃣ Testando funções específicas...")
        
        # Teste confluencia
        try:
            print("   📊 Testando confluencia...")
            import confluencia
            # Criar dados mock para teste
            mtf_mock = {'score': 7.5}
            fluxo_mock = {'pressao': 0.6}
            zonas_mock = {'zona_proxima': 50000}
            sent_mock = {'score': 0.5}
            
            conf = confluencia.calcular_confluencia(mtf_mock, fluxo_mock, zonas_mock, sent_mock)
            print("   ✅ confluencia OK")
        except Exception as e:
            print(f"   ❌ Erro em confluencia: {e}")
            traceback.print_exc()
            return
        
        # Teste projecoes
        try:
            print("   📊 Testando projecoes...")
            import projecoes
            # Criar dados mock para teste
            est_mock = {'tendencia': 'BULLISH'}
            cen = projecoes.projetar_cenarios(dados, 7.5, est_mock, fluxo_mock)
            print("   ✅ projecoes OK")
        except Exception as e:
            print(f"   ❌ Erro em projecoes: {e}")
            traceback.print_exc()
            return
        
        print("\n✅ Todas as funções testadas funcionaram!")
        print("🎯 O erro deve estar em uma das funções que dependem de scipy")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_relatorio_simples()













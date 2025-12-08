#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODO AGRESSIVO
Sempre retorna um sinal, mesmo sem setup perfeito
Para traders que PRECISAM operar AGORA
"""

import pandas as pd
import numpy as np
import requests

def calcular_indicadores_basicos(df):
    """Calcula apenas indicadores essenciais"""
    # EMAs
    df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def analisar_par_agressivo(symbol, df):
    """Análise agressiva - sempre retorna algo"""
    try:
        preco = df['close'].iloc[-1]
        ema8 = df['EMA8'].iloc[-1]
        ema21 = df['EMA21'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        
        # Volume
        volume_atual = df['volume'].iloc[-1]
        volume_medio = df['volume'].rolling(20).mean().iloc[-1]
        volume_ratio = volume_atual / volume_medio if volume_medio > 0 else 1
        
        # Determinar direção (SEMPRE retorna algo)
        if ema8 > ema21:
            acao = 'COMPRAR'
            confianca = 50  # Base
            motivos = ["EMA8 > EMA21"]
            
            if rsi > 50:
                confianca += 15
                motivos.append("RSI acima de 50")
            if volume_ratio > 1:
                confianca += 15
                motivos.append(f"Volume {volume_ratio:.1f}x")
            
            entry = preco
            tp1 = preco * 1.005  # 0.5%
            tp2 = preco * 1.01   # 1%
            tp3 = preco * 1.015  # 1.5%
            sl = preco * 0.997   # -0.3%
            
        else:
            acao = 'VENDER'
            confianca = 50  # Base
            motivos = ["EMA8 < EMA21"]
            
            if rsi < 50:
                confianca += 15
                motivos.append("RSI abaixo de 50")
            if volume_ratio > 1:
                confianca += 15
                motivos.append(f"Volume {volume_ratio:.1f}x")
            
            entry = preco
            tp1 = preco * 0.995  # -0.5%
            tp2 = preco * 0.99   # -1%
            tp3 = preco * 0.985  # -1.5%
            sl = preco * 1.003   # +0.3%
        
        # Calcular R/R
        risco = abs(entry - sl)
        retorno = abs(entry - tp1)
        rr = retorno / risco if risco > 0 else 1
        
        return {
            'symbol': symbol,
            'acao': acao,
            'confianca': min(confianca, 80),  # Max 80%
            'preco': preco,
            'entry': entry,
            'tp1': tp1,
            'tp2': tp2,
            'tp3': tp3,
            'sl': sl,
            'rr': rr,
            'motivos': motivos,
            'rsi': rsi,
            'volume_ratio': volume_ratio
        }
    except:
        return None

def buscar_melhor_par_agressivo():
    """Busca melhor par - SEMPRE retorna algo"""
    pares = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    
    sinais = []
    
    for symbol in pares:
        try:
            # Buscar dados
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": symbol, "interval": "5m", "limit": 50}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            df = calcular_indicadores_basicos(df)
            sinal = analisar_par_agressivo(symbol, df)
            
            if sinal:
                sinais.append(sinal)
        except:
            continue
    
    # Ordenar por confiança
    sinais.sort(key=lambda x: x['confianca'], reverse=True)
    
    return sinais[0] if sinais else None

def exibir_sinal_agressivo(sinal):
    """Exibe sinal agressivo"""
    if not sinal:
        print("\n❌ Erro ao buscar dados")
        return
    
    acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
    
    print("\n" + "="*60)
    print(f"🔥 MODO AGRESSIVO - {acao_emoji} {sinal['acao']} {sinal['symbol']}")
    print("="*60)
    
    print(f"\n💰 PREÇO: ${sinal['preco']:.4f}")
    print(f"⚡ CONFIANÇA: {sinal['confianca']:.0f}% (Agressivo)")
    
    print(f"\n📍 ENTRY: ${sinal['entry']:.4f}")
    
    tp1_pct = abs((sinal['tp1'] - sinal['entry']) / sinal['entry'] * 100)
    tp2_pct = abs((sinal['tp2'] - sinal['entry']) / sinal['entry'] * 100)
    tp3_pct = abs((sinal['tp3'] - sinal['entry']) / sinal['entry'] * 100)
    
    print(f"\n🎯 TAKE PROFIT:")
    print(f"   TP1: ${sinal['tp1']:.4f} ({tp1_pct:+.2f}%)")
    print(f"   TP2: ${sinal['tp2']:.4f} ({tp2_pct:+.2f}%)")
    print(f"   TP3: ${sinal['tp3']:.4f} ({tp3_pct:+.2f}%)")
    
    sl_pct = abs((sinal['entry'] - sinal['sl']) / sinal['entry'] * 100)
    print(f"\n🛡️  STOP LOSS: ${sinal['sl']:.4f} ({sl_pct:.2f}%)")
    
    print(f"\n📊 R/R: 1:{sinal['rr']:.1f}")
    
    print(f"\n💡 ANÁLISE:")
    for motivo in sinal['motivos']:
        print(f"   • {motivo}")
    
    print(f"\n📈 RSI: {sinal['rsi']:.1f}")
    print(f"📊 Volume: {sinal['volume_ratio']:.1f}x média")
    
    print("\n⚠️  AVISO: Modo agressivo - setup não perfeito!")
    print("💡 Use stop loss rigoroso e posição reduzida")
    
    print("="*60)






#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODO TRADER DIRETO
Análise simplificada e direta para day-trading
Sem enrolação, só ação!
"""

import pandas as pd
import numpy as np
import requests

def calcular_indicadores_simples(df):
    """Calcula indicadores básicos necessários"""
    # EMAs
    df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Mid'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Mid'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Mid'] - (bb_std * 2)
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    return df

class TraderDireto:
    """
    Modo ultra simplificado para traders
    Responde: COMPRAR, VENDER ou AGUARDAR
    """
    
    def __init__(self):
        self.pares_principais = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
            'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT', 'MATICUSDT'
        ]
    
    def analisar_agora(self):
        """
        Análise DIRETA do mercado
        Retorna melhor oportunidade com ação clara
        """
        print("\n🔍 ANALISANDO MERCADO...")
        
        oportunidades = []
        
        for symbol in self.pares_principais:
            try:
                # Buscar dados diretamente da Binance
                url = "https://api.binance.com/api/v3/klines"
                params = {
                    "symbol": symbol,
                    "interval": "5m",
                    "limit": 100
                }
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])
                
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype({
                    'open': float,
                    'high': float,
                    'low': float,
                    'close': float,
                    'volume': float
                })
                
                if df.empty:
                    continue
                
                # Calcular indicadores
                df = calcular_indicadores_simples(df)
                
                # Análise direta
                sinal = self._analisar_par(symbol, df)
                
                if sinal and sinal['acao'] != 'AGUARDAR':
                    oportunidades.append(sinal)
                    
            except Exception as e:
                continue
        
        # Ordenar por força do sinal
        oportunidades.sort(key=lambda x: x['forca'], reverse=True)
        
        return oportunidades[:3] if oportunidades else []
    
    def _analisar_par(self, symbol, df):
        """
        Análise direta de um par
        """
        try:
            # Dados atuais
            preco = df['close'].iloc[-1]
            ema8 = df['EMA8'].iloc[-1]
            ema21 = df['EMA21'].iloc[-1]
            rsi = df['RSI'].iloc[-1]
            
            # Bollinger Bands
            bb_upper = df['BB_Upper'].iloc[-1]
            bb_lower = df['BB_Lower'].iloc[-1]
            bb_mid = df['BB_Mid'].iloc[-1]
            
            # Volume
            volume_atual = df['volume'].iloc[-1]
            volume_medio = df['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume_atual / volume_medio
            
            # MACD
            macd = df['MACD'].iloc[-1]
            macd_signal = df['MACD_Signal'].iloc[-1]
            
            # === LÓGICA DIRETA ===
            
            forca = 0
            acao = 'AGUARDAR'
            motivo = []
            
            # SINAL DE COMPRA
            if (ema8 > ema21 and  # Tendência de alta
                rsi < 70 and rsi > 30 and  # RSI saudável
                preco > bb_mid and  # Acima da média
                macd > macd_signal and  # MACD positivo
                volume_ratio > 1.2):  # Volume confirmando
                
                acao = 'COMPRAR'
                forca = 0
                
                # Calcular força
                if rsi > 50:
                    forca += 25
                    motivo.append("RSI forte")
                if volume_ratio > 1.5:
                    forca += 25
                    motivo.append("Volume alto")
                if (ema8 - ema21) / ema21 > 0.01:
                    forca += 25
                    motivo.append("EMAs divergindo")
                if preco < bb_upper * 0.98:
                    forca += 25
                    motivo.append("Espaço para subir")
            
            # SINAL DE VENDA
            elif (ema8 < ema21 and  # Tendência de baixa
                  rsi > 30 and rsi < 70 and  # RSI saudável
                  preco < bb_mid and  # Abaixo da média
                  macd < macd_signal and  # MACD negativo
                  volume_ratio > 1.2):  # Volume confirmando
                
                acao = 'VENDER'
                forca = 0
                
                # Calcular força
                if rsi < 50:
                    forca += 25
                    motivo.append("RSI fraco")
                if volume_ratio > 1.5:
                    forca += 25
                    motivo.append("Volume alto")
                if (ema21 - ema8) / ema21 > 0.01:
                    forca += 25
                    motivo.append("EMAs divergindo")
                if preco > bb_lower * 1.02:
                    forca += 25
                    motivo.append("Espaço para cair")
            
            # Só retornar se força >= 40 (ajustado para ser mais brando)
            if forca < 40:
                return None
            
            # Calcular níveis
            if acao == 'COMPRAR':
                entry = preco
                tp1 = preco * 1.01  # +1%
                tp2 = preco * 1.02  # +2%
                tp3 = preco * 1.03  # +3%
                sl = preco * 0.995  # -0.5%
            elif acao == 'VENDER':
                entry = preco
                tp1 = preco * 0.99  # -1%
                tp2 = preco * 0.98  # -2%
                tp3 = preco * 0.97  # -3%
                sl = preco * 1.005  # +0.5%
            else:
                return None
            
            # Calcular R/R
            risco = abs(entry - sl)
            retorno = abs(entry - tp1)
            rr = retorno / risco if risco > 0 else 0
            
            return {
                'symbol': symbol,
                'acao': acao,
                'forca': forca,
                'preco': preco,
                'entry': entry,
                'tp1': tp1,
                'tp2': tp2,
                'tp3': tp3,
                'sl': sl,
                'rr': rr,
                'motivos': motivo,
                'rsi': rsi,
                'volume_ratio': volume_ratio
            }
            
        except Exception as e:
            return None

def exibir_sinal_direto(sinal):
    """
    Exibe sinal de forma DIRETA e CLARA
    """
    if not sinal:
        print("\n⏸️  AGUARDAR")
        print("💡 Nenhum setup claro no momento")
        return
    
    acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
    
    print("\n" + "="*60)
    print(f"{acao_emoji} {sinal['acao']} {sinal['symbol']}")
    print("="*60)
    
    print(f"\n💰 PREÇO ATUAL: ${sinal['preco']:.4f}")
    print(f"⚡ FORÇA DO SINAL: {sinal['forca']:.0f}%")
    
    print(f"\n📍 ENTRY: ${sinal['entry']:.4f}")
    
    print(f"\n🎯 TAKE PROFIT:")
    tp1_pct = abs((sinal['tp1'] - sinal['entry']) / sinal['entry'] * 100)
    tp2_pct = abs((sinal['tp2'] - sinal['entry']) / sinal['entry'] * 100)
    tp3_pct = abs((sinal['tp3'] - sinal['entry']) / sinal['entry'] * 100)
    
    print(f"   TP1: ${sinal['tp1']:.4f} ({tp1_pct:+.2f}%)")
    print(f"   TP2: ${sinal['tp2']:.4f} ({tp2_pct:+.2f}%)")
    print(f"   TP3: ${sinal['tp3']:.4f} ({tp3_pct:+.2f}%)")
    
    sl_pct = abs((sinal['entry'] - sinal['sl']) / sinal['entry'] * 100)
    print(f"\n🛡️  STOP LOSS: ${sinal['sl']:.4f} (-{sl_pct:.2f}%)")
    
    print(f"\n📊 RISCO/RETORNO: 1:{sinal['rr']:.1f}")
    
    print(f"\n💡 MOTIVOS:")
    for motivo in sinal['motivos']:
        print(f"   ✓ {motivo}")
    
    print(f"\n📈 RSI: {sinal['rsi']:.1f}")
    print(f"📊 Volume: {sinal['volume_ratio']:.1f}x média")
    
    print("\n" + "="*60)

def exibir_top_sinais_diretos(sinais):
    """
    Exibe top sinais de forma resumida
    """
    if not sinais:
        print("\n⏸️  AGUARDAR - Nenhum setup claro")
        return
    
    print(f"\n🏆 {len(sinais)} OPORTUNIDADES ENCONTRADAS:")
    print("-"*60)
    
    for i, sinal in enumerate(sinais, 1):
        acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
        print(f"\n{i}. {acao_emoji} {sinal['acao']} {sinal['symbol']}")
        print(f"   Força: {sinal['forca']:.0f}% | Entry: ${sinal['entry']:.4f}")
        print(f"   TP1: ${sinal['tp1']:.4f} | SL: ${sinal['sl']:.4f}")
        print(f"   R/R: 1:{sinal['rr']:.1f}")


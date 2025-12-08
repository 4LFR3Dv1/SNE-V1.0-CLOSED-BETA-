#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONTEXTO MACRO - Análise de mercado global
"""

from contexto_global import analisar_contexto
from sentimento_global import analisar_sentiment
import requests
import pandas as pd
from indicadores import calcular_indicadores


def analise_macro(pares=['BTCUSDT', 'ETHUSDT', 'BNBUSDT']):
    """Análise macro do mercado cripto"""
    
    print("\n🌍 ANALISANDO CONTEXTO MACRO...")
    
    resultados = {}
    
    # Usar motor_renan para análise mais robusta
    from motor_renan import analise_completa
    
    for par in pares:
        print(f"   🔄 {par}...", end=' ', flush=True)
        try:
            # Suprimir prints do motor_renan
            import sys
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            resultado = analise_completa(par, "1h")
            
            # Restaurar stdout
            sys.stdout = old_stdout
            
            if resultado and 'erro' not in resultado:
                ctx = resultado.get('contexto', {})
                
                # Buscar volume 24h real da API
                volume_24h = obter_volume_24h(par)
                
                resultados[par] = {
                    'regime': ctx.get('regime', 'N/A'),
                    'forca_regime': ctx.get('forca_regime', 0),
                    'volatilidade': ctx.get('volatilidade', 0),
                    'liquidez_score': ctx.get('liquidez_score', 0),
                    'volume_24h': volume_24h
                }
                print("✅")
            else:
                print("⚠️")
        except Exception as e:
            sys.stdout = old_stdout  # Garantir restauração
            print(f"❌ {str(e)}")
    
    # Sentiment global
    sentiment = analisar_sentiment('BTCUSDT')
    
    # Síntese
    regimes = [r['regime'] for r in resultados.values() if 'regime' in r]
    regime_dominante = max(set(regimes), key=regimes.count) if regimes else 'INDEFINIDO'
    
    return {
        'pares': resultados,
        'sentiment': sentiment,
        'regime_dominante': regime_dominante,
        'total_pares': len(pares)
    }


def obter_volume_24h(symbol):
    """Obtém volume 24h real em USD da API Binance"""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Volume em quote asset (USDT)
            volume_quote = float(data.get('quoteVolume', 0))
            return volume_quote
        return 0
    except:
        return 0


def coletar_dados(symbol, interval="1h", limit=100):
    """Coleta dados"""
    try:
        # Normalizar interval
        interval = interval.lower()
        
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            df = df[['close', 'volume']].astype(float)
            df = calcular_indicadores(df)
            return df
        return None
    except:
        return None


def exibir_macro(resultado):
    """Exibe contexto macro"""
    print("\n" + "="*60)
    print("🌍 CONTEXTO MACRO DE MERCADO")
    print("="*60)
    
    print(f"\n📊 Regime Dominante: {resultado['regime_dominante']}")
    
    if resultado['pares']:
        print(f"\n💹 Análise por Par:")
        for par, ctx in resultado['pares'].items():
            vol_24h = ctx.get('volume_24h', 0)
            vol_str = f"${vol_24h/1e9:.1f}B" if vol_24h > 0 else "N/A"
            
            print(f"\n   {par}:")
            print(f"   Regime:       {ctx.get('regime', 'N/A')} ({ctx.get('forca_regime', 0)}/10)")
            print(f"   Volatilidade: {ctx.get('volatilidade', 0):.2f}%")
            print(f"   Liquidez:     {ctx.get('liquidez_score', 0)}/10")
            print(f"   Volume 24h:   {vol_str}")
    else:
        print(f"\n⚠️  Nenhum dado disponível")
    
    print(f"\n😨 Sentiment:")
    s = resultado['sentiment']
    print(f"   Fear & Greed: {s['fear_greed']['valor']}/100 ({s['fear_greed']['classificacao']})")
    print(f"   Funding:      {s['funding_rate']['viés']}")
    
    print("\n" + "="*60)

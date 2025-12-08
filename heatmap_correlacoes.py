#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HEATMAP CORRELAÇÕES - Análise de correlações entre pares
"""

import requests
import pandas as pd
import numpy as np


PARES_ANALISE = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']


def gerar_heatmap_correlacoes(pares=None, intervalo="1h", limite=100):
    """Gera matriz de correlações"""
    
    if pares is None:
        pares = PARES_ANALISE
    
    print(f"\n🔥 CALCULANDO CORRELAÇÕES - {len(pares)} pares...")
    
    # Coletar preços
    dados = {}
    for par in pares:
        precos = coletar_precos(par, intervalo, limite)
        if precos is not None:
            dados[par] = precos
    
    if len(dados) < 2:
        return {'erro': 'Dados insuficientes'}
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Calcular correlações
    correlacoes = df.corr()
    
    return {
        'correlacoes': correlacoes,
        'pares': list(dados.keys())
    }


def coletar_precos(symbol, interval, limit):
    """Coleta série de preços"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            precos = [float(k[4]) for k in data]  # Close price
            return precos
        return None
    except:
        return None


def exibir_heatmap(resultado):
    """Exibe heatmap em formato texto"""
    
    if 'erro' in resultado:
        print(f"❌ {resultado['erro']}")
        return
    
    corr = resultado['correlacoes']
    pares = resultado['pares']
    
    print("\n" + "="*70)
    print("🔥 HEATMAP DE CORRELAÇÕES")
    print("="*70)
    
    # Cabeçalho
    print(f"\n{'':12}", end="")
    for par in pares:
        print(f"{par[:6]:>10}", end="")
    print()
    print("-" * 70)
    
    # Matriz
    for i, par1 in enumerate(pares):
        print(f"{par1[:10]:<12}", end="")
        for j, par2 in enumerate(pares):
            val = corr.iloc[i, j]
            
            # Colorir por valor
            if val >= 0.8:
                color = "🟢"
            elif val >= 0.5:
                color = "🟡"
            elif val >= 0:
                color = "⚪"
            else:
                color = "🔴"
            
            print(f"{color}{val:>8.2f}", end="")
        print()
    
    # Interpretação
    print("\n📊 INTERPRETAÇÃO:")
    print("   🟢 >= 0.80: Forte correlação positiva")
    print("   🟡 >= 0.50: Correlação moderada")
    print("   ⚪ >= 0.00: Correlação fraca")
    print("   🔴 <  0.00: Correlação negativa")
    
    # Pares mais correlacionados
    print("\n🔗 PARES MAIS CORRELACIONADOS:")
    for i in range(len(pares)):
        for j in range(i+1, len(pares)):
            val = corr.iloc[i, j]
            if val >= 0.8:
                print(f"   {pares[i]} ↔ {pares[j]}: {val:.3f}")
    
    print("\n" + "="*70)





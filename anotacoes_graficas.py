#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANOTAÇÕES GRÁFICAS - Identificação e marcação de padrões técnicos
"""

import pandas as pd
import numpy as np


def detectar_retestes(df, sr_levels):
    """
    Detecta retestes de suportes e resistências
    
    Args:
        df: DataFrame com OHLCV
        sr_levels: Dict com suportes e resistências
    
    Returns:
        Lista de retestes detectados
    """
    retestes = []
    
    suportes = sr_levels.get('suportes', [])
    resistencias = sr_levels.get('resistencias', [])
    
    for i in range(1, len(df)):
        preco_atual = df['close'].iloc[i]
        preco_anterior = df['close'].iloc[i-1]
        
        # Verificar reteste de suporte
        for suporte in suportes:
            tolerancia = suporte * 0.002  # 0.2% de tolerância
            
            # Preço tocou o suporte e voltou
            if (df['low'].iloc[i] <= suporte + tolerancia and 
                df['low'].iloc[i] >= suporte - tolerancia and
                preco_atual > suporte):
                
                retestes.append({
                    'tipo': 'RETESTE_SUPORTE',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': suporte,
                    'resultado': 'SUCESSO' if preco_atual > preco_anterior else 'FALHA'
                })
        
        # Verificar reteste de resistência
        for resistencia in resistencias:
            tolerancia = resistencia * 0.002
            
            # Preço tocou a resistência e voltou
            if (df['high'].iloc[i] >= resistencia - tolerancia and 
                df['high'].iloc[i] <= resistencia + tolerancia and
                preco_atual < resistencia):
                
                retestes.append({
                    'tipo': 'RETESTE_RESISTENCIA',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': resistencia,
                    'resultado': 'SUCESSO' if preco_atual < preco_anterior else 'FALHA'
                })
    
    return retestes


def detectar_rompimentos(df, sr_levels):
    """
    Detecta rompimentos de suportes e resistências
    
    Args:
        df: DataFrame com OHLCV
        sr_levels: Dict com suportes e resistências
    
    Returns:
        Lista de rompimentos detectados
    """
    rompimentos = []
    
    suportes = sr_levels.get('suportes', [])
    resistencias = sr_levels.get('resistencias', [])
    
    for i in range(1, len(df)):
        close_atual = df['close'].iloc[i]
        close_anterior = df['close'].iloc[i-1]
        
        # Rompimento de resistência (breakout)
        for resistencia in resistencias:
            if close_anterior < resistencia and close_atual > resistencia:
                # Verificar volume
                volume_medio = df['volume'].iloc[max(0, i-20):i].mean()
                volume_atual = df['volume'].iloc[i]
                
                rompimentos.append({
                    'tipo': 'BREAKOUT',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': resistencia,
                    'volume_relativo': volume_atual / volume_medio if volume_medio > 0 else 1,
                    'valido': volume_atual > volume_medio * 1.5
                })
        
        # Rompimento de suporte (breakdown)
        for suporte in suportes:
            if close_anterior > suporte and close_atual < suporte:
                volume_medio = df['volume'].iloc[max(0, i-20):i].mean()
                volume_atual = df['volume'].iloc[i]
                
                rompimentos.append({
                    'tipo': 'BREAKDOWN',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': suporte,
                    'volume_relativo': volume_atual / volume_medio if volume_medio > 0 else 1,
                    'valido': volume_atual > volume_medio * 1.5
                })
    
    return rompimentos


def detectar_pullbacks(df):
    """
    Detecta pullbacks em tendências
    
    Args:
        df: DataFrame com OHLCV
    
    Returns:
        Lista de pullbacks detectados
    """
    pullbacks = []
    
    # Calcular EMAs
    df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
    
    for i in range(21, len(df)):
        # Tendência de alta (EMA8 > EMA21)
        if df['EMA8'].iloc[i] > df['EMA21'].iloc[i]:
            # Pullback: preço tocou EMA21 e voltou
            if (df['low'].iloc[i] <= df['EMA21'].iloc[i] * 1.005 and
                df['close'].iloc[i] > df['EMA21'].iloc[i]):
                
                pullbacks.append({
                    'tipo': 'PULLBACK_ALTA',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': df['EMA21'].iloc[i],
                    'resultado': 'COMPRA'
                })
        
        # Tendência de baixa (EMA8 < EMA21)
        elif df['EMA8'].iloc[i] < df['EMA21'].iloc[i]:
            # Pullback: preço tocou EMA21 e voltou
            if (df['high'].iloc[i] >= df['EMA21'].iloc[i] * 0.995 and
                df['close'].iloc[i] < df['EMA21'].iloc[i]):
                
                pullbacks.append({
                    'tipo': 'PULLBACK_BAIXA',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': df['EMA21'].iloc[i],
                    'resultado': 'VENDA'
                })
    
    return pullbacks


def detectar_falhas(df, sr_levels):
    """
    Detecta falhas de rompimento (false breakouts)
    
    Args:
        df: DataFrame com OHLCV
        sr_levels: Dict com suportes e resistências
    
    Returns:
        Lista de falhas detectadas
    """
    falhas = []
    
    resistencias = sr_levels.get('resistencias', [])
    suportes = sr_levels.get('suportes', [])
    
    for i in range(2, len(df)):
        # Falha de breakout (rompeu resistência mas voltou)
        for resistencia in resistencias:
            if (df['high'].iloc[i-1] > resistencia and
                df['close'].iloc[i-1] > resistencia and
                df['close'].iloc[i] < resistencia):
                
                falhas.append({
                    'tipo': 'FALHA_BREAKOUT',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': resistencia,
                    'resultado': 'REVERSAO_BAIXA'
                })
        
        # Falha de breakdown (rompeu suporte mas voltou)
        for suporte in suportes:
            if (df['low'].iloc[i-1] < suporte and
                df['close'].iloc[i-1] < suporte and
                df['close'].iloc[i] > suporte):
                
                falhas.append({
                    'tipo': 'FALHA_BREAKDOWN',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': suporte,
                    'resultado': 'REVERSAO_ALTA'
                })
    
    return falhas


def detectar_pontos_entrada_saida(df):
    """
    Detecta pontos de entrada e saída passados baseados em sinais técnicos
    
    Args:
        df: DataFrame com OHLCV
    
    Returns:
        Lista de pontos de entrada/saída
    """
    pontos = []
    
    # Calcular indicadores
    df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['RSI'] = calcular_rsi(df['close'], 14)
    
    for i in range(21, len(df)):
        # SINAL DE COMPRA: EMA8 cruza acima de EMA21 + RSI < 70
        if (df['EMA8'].iloc[i-1] <= df['EMA21'].iloc[i-1] and
            df['EMA8'].iloc[i] > df['EMA21'].iloc[i] and
            df['RSI'].iloc[i] < 70):
            
            # Calcular resultado (olhar próximos 10 candles)
            preco_entrada = df['close'].iloc[i]
            max_preco = df['high'].iloc[i:min(i+10, len(df))].max()
            ganho_pct = ((max_preco - preco_entrada) / preco_entrada) * 100
            
            pontos.append({
                'tipo': 'ENTRADA_COMPRA',
                'index': i,
                'timestamp': df.index[i],
                'preco': preco_entrada,
                'resultado': f'+{ganho_pct:.1f}%' if ganho_pct > 0 else f'{ganho_pct:.1f}%',
                'sucesso': ganho_pct > 1
            })
        
        # SINAL DE VENDA: EMA8 cruza abaixo de EMA21 + RSI > 30
        elif (df['EMA8'].iloc[i-1] >= df['EMA21'].iloc[i-1] and
              df['EMA8'].iloc[i] < df['EMA21'].iloc[i] and
              df['RSI'].iloc[i] > 30):
            
            preco_entrada = df['close'].iloc[i]
            min_preco = df['low'].iloc[i:min(i+10, len(df))].min()
            ganho_pct = ((preco_entrada - min_preco) / preco_entrada) * 100
            
            pontos.append({
                'tipo': 'ENTRADA_VENDA',
                'index': i,
                'timestamp': df.index[i],
                'preco': preco_entrada,
                'resultado': f'+{ganho_pct:.1f}%' if ganho_pct > 0 else f'{ganho_pct:.1f}%',
                'sucesso': ganho_pct > 1
            })
    
    return pontos


def calcular_rsi(series, periodo=14):
    """Calcula RSI"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def analisar_padroes_tecnicos(df, sr_levels):
    """
    Análise completa de padrões técnicos
    
    Args:
        df: DataFrame com OHLCV
        sr_levels: Dict com suportes e resistências
    
    Returns:
        Dict com todos os padrões detectados
    """
    return {
        'retestes': detectar_retestes(df, sr_levels),
        'rompimentos': detectar_rompimentos(df, sr_levels),
        'pullbacks': detectar_pullbacks(df),
        'falhas': detectar_falhas(df, sr_levels),
        'pontos_entrada_saida': detectar_pontos_entrada_saida(df)
    }


if __name__ == "__main__":
    # Teste
    print("Módulo de anotações gráficas carregado!")





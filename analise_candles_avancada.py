#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE AVANÇADA DE CANDLES E PADRÕES
Módulo para leitura de candles passados e identificação de padrões
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Implementação própria de find_peaks para substituir scipy.signal
def find_peaks(data, distance=1):
    """Encontra picos em uma série de dados"""
    peaks = []
    for i in range(distance, len(data) - distance):
        is_peak = True
        for j in range(max(0, i-distance), min(len(data), i+distance+1)):
            if j != i and data[j] >= data[i]:
                is_peak = False
                break
        if is_peak:
            peaks.append(i)
    return np.array(peaks), {}

# Importação condicional do TA-Lib
try:
    import talib
    TALIB_AVAILABLE = True
    print("✅ TA-Lib disponível - usando padrões profissionais!")
except ImportError:
    TALIB_AVAILABLE = False
    print("⚠️ TA-Lib não disponível - usando implementações próprias avançadas!")

# Importação condicional do sklearn
try:
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn não disponível. Funcionalidades limitadas.")


class AnalisadorCandlesAvancado:
    """Analisador avançado de candles e padrões"""
    
    def __init__(self, df_candles):
        """
        Inicializa o analisador com dados de candles
        
        Args:
            df_candles: DataFrame com colunas OHLCV
        """
        self.df = df_candles.copy()
        self.padroes_detectados = []
        self.candles_significativos = []
        
    def analisar_candles_passados(self, lookback_periods=50):
        """
        Analisa candles passados para identificar padrões significativos
        
        Args:
            lookback_periods: Número de períodos para analisar
            
        Returns:
            dict com análise completa dos candles passados
        """
        try:
            if len(self.df) < lookback_periods:
                lookback_periods = len(self.df)
            
            # Pegar últimos N candles
            df_analise = self.df.tail(lookback_periods).copy()
            
            resultado = {
                'periodo_analisado': lookback_periods,
                'total_candles': len(df_analise),
                'candles_significativos': [],
                'padroes_candlestick': [],
                'padroes_graficos': [],
                'estatisticas': {},
                'momentum_historico': {},
                'volatilidade_historica': {}
            }
            
            # 1. ANÁLISE DE CANDLES SIGNIFICATIVOS
            resultado['candles_significativos'] = self._identificar_candles_significativos(df_analise)
            
            # 2. DETECÇÃO DE TODOS OS PADRÕES POSSÍVEIS
            todos_padroes = self._detectar_todos_padroes(df_analise)
            
            # Separar por categoria
            resultado['padroes_candlestick'] = [p for p in todos_padroes if p.get('categoria') == 'CANDLESTICK']
            resultado['padroes_graficos'] = [p for p in todos_padroes if p.get('categoria') == 'GRAFICO']
            resultado['padroes_volume'] = [p for p in todos_padroes if p.get('categoria') == 'VOLUME']
            resultado['padroes_preco'] = [p for p in todos_padroes if p.get('categoria') == 'PRECO']
            resultado['padroes_tempo'] = [p for p in todos_padroes if p.get('categoria') == 'TEMPO']
            resultado['padroes_momentum'] = [p for p in todos_padroes if p.get('categoria') == 'MOMENTUM']
            resultado['padroes_volatilidade'] = [p for p in todos_padroes if p.get('categoria') == 'VOLATILIDADE']
            
            # NOVAS CATEGORIAS AVANÇADAS
            resultado['padroes_sequencia'] = [p for p in todos_padroes if p.get('categoria') == 'SEQUENCIA']
            resultado['padroes_breakout'] = [p for p in todos_padroes if p.get('categoria') == 'BREAKOUT']
            resultado['padroes_divergencia'] = [p for p in todos_padroes if p.get('categoria') == 'DIVERGENCIA']
            resultado['padroes_liquidez'] = [p for p in todos_padroes if p.get('categoria') == 'LIQUIDEZ']
            resultado['padroes_sentimento'] = [p for p in todos_padroes if p.get('categoria') == 'SENTIMENTO']
            
            # Estatísticas de padrões
            resultado['estatisticas_padroes'] = {
                'total_padroes': len(todos_padroes),
                'por_categoria': {
                    'CANDLESTICK': len(resultado['padroes_candlestick']),
                    'GRAFICO': len(resultado['padroes_graficos']),
                    'VOLUME': len(resultado['padroes_volume']),
                    'PRECO': len(resultado['padroes_preco']),
                    'TEMPO': len(resultado['padroes_tempo']),
                    'MOMENTUM': len(resultado['padroes_momentum']),
                    'VOLATILIDADE': len(resultado['padroes_volatilidade']),
                    'SEQUENCIA': len(resultado['padroes_sequencia']),
                    'BREAKOUT': len(resultado['padroes_breakout']),
                    'DIVERGENCIA': len(resultado['padroes_divergencia']),
                    'LIQUIDEZ': len(resultado['padroes_liquidez']),
                    'SENTIMENTO': len(resultado['padroes_sentimento'])
                },
                'por_tipo': {
                    'BULLISH': len([p for p in todos_padroes if p.get('tipo') == 'BULLISH']),
                    'BEARISH': len([p for p in todos_padroes if p.get('tipo') == 'BEARISH']),
                    'NEUTRO': len([p for p in todos_padroes if p.get('tipo') == 'NEUTRO'])
                }
            }
            
            # 4. ESTATÍSTICAS HISTÓRICAS
            resultado['estatisticas'] = self._calcular_estatisticas_historicas(df_analise)
            
            # 5. MOMENTUM HISTÓRICO
            resultado['momentum_historico'] = self._analisar_momentum_historico(df_analise)
            
            # 6. VOLATILIDADE HISTÓRICA
            resultado['volatilidade_historica'] = self._analisar_volatilidade_historica(df_analise)
            
            return resultado
            
        except Exception as e:
            return {'erro': f'Erro na análise de candles passados: {str(e)}'}
    
    def _identificar_candles_significativos(self, df):
        """Identifica candles significativos baseado em múltiplos critérios"""
        try:
            candles_significativos = []
            
            # Calcular métricas para cada candle
            df['range'] = df['high'] - df['low']
            df['corpo'] = abs(df['close'] - df['open'])
            df['sombra_superior'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['sombra_inferior'] = df[['open', 'close']].min(axis=1) - df['low']
            df['range_pct'] = (df['range'] / df['open']) * 100
            df['corpo_pct'] = (df['corpo'] / df['open']) * 100
            
            # Calcular médias móveis para comparação
            df['range_ma'] = df['range'].rolling(window=20).mean()
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            
            for i, row in df.iterrows():
                significancia = 0
                caracteristicas = []
                
                # 1. CANDLE DE ALTA VOLATILIDADE
                if row['range_pct'] > df['range_pct'].quantile(0.9):
                    significancia += 3
                    caracteristicas.append('Alta Volatilidade')
                
                # 2. CANDLE DE ALTO VOLUME
                if row['volume'] > row['volume_ma'] * 2:
                    significancia += 2
                    caracteristicas.append('Alto Volume')
                
                # 3. CANDLE COM CORPO GRANDE
                if row['corpo_pct'] > df['corpo_pct'].quantile(0.8):
                    significancia += 2
                    caracteristicas.append('Corpo Grande')
                
                # 4. CANDLE COM SOMBRAS EXTREMAS
                if row['sombra_superior'] > row['range'] * 0.6:
                    significancia += 1
                    caracteristicas.append('Sombra Superior Extrema')
                
                if row['sombra_inferior'] > row['range'] * 0.6:
                    significancia += 1
                    caracteristicas.append('Sombra Inferior Extrema')
                
                # 5. CANDLE DE REJEIÇÃO
                if row['sombra_superior'] > row['corpo'] * 2 or row['sombra_inferior'] > row['corpo'] * 2:
                    significancia += 2
                    caracteristicas.append('Rejeição')
                
                # 6. CANDLE DE ABSORÇÃO
                if i > 0:
                    candle_anterior = df.iloc[i-1]
                    if row['corpo'] > candle_anterior['corpo'] * 1.5:
                        significancia += 2
                        caracteristicas.append('Absorção')
                
                # Se significativo, adicionar à lista
                if significancia >= 3:
                    candles_significativos.append({
                        'index': i,
                        'timestamp': i,
                        'significancia': significancia,
                        'caracteristicas': caracteristicas,
                        'preco_open': row['open'],
                        'preco_high': row['high'],
                        'preco_low': row['low'],
                        'preco_close': row['close'],
                        'volume': row['volume'],
                        'range_pct': row['range_pct'],
                        'corpo_pct': row['corpo_pct']
                    })
            
            return candles_significativos
            
        except Exception as e:
                return []
    
    def _detectar_todos_padroes(self, df):
        """Detecta TODOS os tipos de padrões possíveis"""
        try:
            todos_padroes = []
            
            # 1. PADRÕES DE CANDLESTICK (TA-Lib ou implementações próprias) - MANTIDO PARA ANÁLISE
            padroes_candlestick = self._detectar_padroes_candlestick_completos(df)
            todos_padroes.extend(padroes_candlestick)
            
            # 2. PADRÕES GRÁFICOS COMPLEXOS
            padroes_graficos = self._detectar_padroes_graficos_completos(df)
            todos_padroes.extend(padroes_graficos)
            
            # 3. PADRÕES DE VOLUME (EXPANDIDO)
            padroes_volume = self._detectar_padroes_volume(df)
            todos_padroes.extend(padroes_volume)
            
            # 4. PADRÕES DE PREÇO (EXPANDIDO)
            padroes_preco = self._detectar_padroes_preco(df)
            todos_padroes.extend(padroes_preco)
            
            # 5. PADRÕES DE TEMPO (EXPANDIDO)
            padroes_tempo = self._detectar_padroes_tempo(df)
            todos_padroes.extend(padroes_tempo)
            
            # 6. PADRÕES DE MOMENTUM (EXPANDIDO)
            padroes_momentum = self._detectar_padroes_momentum(df)
            todos_padroes.extend(padroes_momentum)
            
            # 7. PADRÕES DE VOLATILIDADE (EXPANDIDO)
            padroes_volatilidade = self._detectar_padroes_volatilidade(df)
            todos_padroes.extend(padroes_volatilidade)
            
            # 8. NOVOS PADRÕES AVANÇADOS
            padroes_sequencia = _detectar_padroes_sequencia(df)
            todos_padroes.extend(padroes_sequencia)
            
            padroes_breakout = _detectar_padroes_breakout(df)
            todos_padroes.extend(padroes_breakout)
            
            padroes_divergencia = _detectar_padroes_divergencia(df)
            todos_padroes.extend(padroes_divergencia)
            
            padroes_liquidez = _detectar_padroes_liquidez(df)
            todos_padroes.extend(padroes_liquidez)
            
            padroes_sentimento = _detectar_padroes_sentimento(df)
            todos_padroes.extend(padroes_sentimento)
            
            return todos_padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_candlestick_completos(self, df):
        """Detecta TODOS os padrões candlestick possíveis"""
        try:
            padroes = []
            
            if TALIB_AVAILABLE:
                # Usar TA-Lib se disponível
                padroes.extend(self._detectar_padroes_candlestick_talib(df))
            else:
                # Usar implementações próprias avançadas
                padroes.extend(self._detectar_padroes_candlestick_avancados(df))
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_candlestick_avancados(self, df):
        """Implementações próprias avançadas de padrões candlestick"""
        try:
            padroes = []
            
            for i in range(len(df)):
                if i < 3:  # Precisa de pelo menos 3 candles para comparação
                    continue
                
                # Dados dos candles
                candle_atual = df.iloc[i]
                candle_anterior = df.iloc[i-1]
                candle_anterior2 = df.iloc[i-2] if i >= 2 else None
                
                open_atual = candle_atual['open']
                high_atual = candle_atual['high']
                low_atual = candle_atual['low']
                close_atual = candle_atual['close']
                
                open_anterior = candle_anterior['open']
                high_anterior = candle_anterior['high']
                low_anterior = candle_anterior['low']
                close_anterior = candle_anterior['close']
                
                # Calcular métricas
                range_atual = high_atual - low_atual
                corpo_atual = abs(close_atual - open_atual)
                sombra_superior = high_atual - max(open_atual, close_atual)
                sombra_inferior = min(open_atual, close_atual) - low_atual
                
                range_anterior = high_anterior - low_anterior
                corpo_anterior = abs(close_anterior - open_anterior)
                
                # DOJI (corpo muito pequeno)
                if corpo_atual < range_atual * 0.1:
                    padroes.append({
                        'nome': 'DOJI',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': close_atual,
                        'confianca': 0.7,
                        'tipo': 'NEUTRO',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Corpo: {corpo_atual:.2f} ({corpo_atual/range_atual*100:.1f}%)'
                    })
                
                # HAMMER (sombra inferior longa, corpo pequeno)
                elif (sombra_inferior > corpo_atual * 2 and 
                      sombra_superior < corpo_atual * 0.5 and
                      close_atual > open_atual):
                    padroes.append({
                        'nome': 'HAMMER',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BULLISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Sombra: {sombra_inferior:.2f}, Corpo: {corpo_atual:.2f}'
                    })
                
                # HANGING MAN (mesmo que hammer mas bearish)
                elif (sombra_inferior > corpo_atual * 2 and 
                      sombra_superior < corpo_atual * 0.5 and
                      close_atual < open_atual):
                    padroes.append({
                        'nome': 'HANGING_MAN',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BEARISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Sombra: {sombra_inferior:.2f}, Corpo: {corpo_atual:.2f}'
                    })
                
                # SHOOTING STAR (sombra superior longa)
                elif (sombra_superior > corpo_atual * 2 and 
                      sombra_inferior < corpo_atual * 0.5 and
                      close_atual < open_atual):
                    padroes.append({
                        'nome': 'SHOOTING_STAR',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BEARISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Sombra: {sombra_superior:.2f}, Corpo: {corpo_atual:.2f}'
                    })
                
                # INVERTED HAMMER (shooting star bullish)
                elif (sombra_superior > corpo_atual * 2 and 
                      sombra_inferior < corpo_atual * 0.5 and
                      close_atual > open_atual):
                    padroes.append({
                        'nome': 'INVERTED_HAMMER',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BULLISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Sombra: {sombra_superior:.2f}, Corpo: {corpo_atual:.2f}'
                    })
                
                # ENGULFING BULLISH
                elif (close_atual > open_atual and  # Candle atual bullish
                      close_anterior < open_anterior and  # Candle anterior bearish
                      open_atual < close_anterior and  # Abertura abaixo do fechamento anterior
                      close_atual > open_anterior):  # Fechamento acima da abertura anterior
                    padroes.append({
                        'nome': 'ENGULFING_BULLISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 100,
                        'preco': close_atual,
                        'confianca': 0.9,
                        'tipo': 'BULLISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Engole: {corpo_atual:.2f} vs {corpo_anterior:.2f}'
                    })
                
                # ENGULFING BEARISH
                elif (close_atual < open_atual and  # Candle atual bearish
                      close_anterior > open_anterior and  # Candle anterior bullish
                      open_atual > close_anterior and  # Abertura acima do fechamento anterior
                      close_atual < open_anterior):  # Fechamento abaixo da abertura anterior
                    padroes.append({
                        'nome': 'ENGULFING_BEARISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.9,
                        'tipo': 'BEARISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Engole: {corpo_atual:.2f} vs {corpo_anterior:.2f}'
                    })
                
                # HARAMI BULLISH (corpo pequeno dentro do anterior)
                elif (close_atual > open_atual and  # Candle atual bullish
                      close_anterior < open_anterior and  # Candle anterior bearish
                      open_atual > close_anterior and  # Abertura dentro do corpo anterior
                      close_atual < open_anterior):  # Fechamento dentro do corpo anterior
                    padroes.append({
                        'nome': 'HARAMI_BULLISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 50,
                        'preco': close_atual,
                        'confianca': 0.6,
                        'tipo': 'BULLISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Corpo pequeno: {corpo_atual:.2f}'
                    })
                
                # HARAMI BEARISH
                elif (close_atual < open_atual and  # Candle atual bearish
                      close_anterior > open_anterior and  # Candle anterior bullish
                      open_atual < close_anterior and  # Abertura dentro do corpo anterior
                      close_atual > open_anterior):  # Fechamento dentro do corpo anterior
                    padroes.append({
                        'nome': 'HARAMI_BEARISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -50,
                        'preco': close_atual,
                        'confianca': 0.6,
                        'tipo': 'BEARISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Corpo pequeno: {corpo_atual:.2f}'
                    })
                
                # MARUBOZU BULLISH (corpo grande sem sombras)
                elif (close_atual > open_atual and  # Bullish
                      sombra_superior < range_atual * 0.1 and  # Sombra superior pequena
                      sombra_inferior < range_atual * 0.1):  # Sombra inferior pequena
                    padroes.append({
                        'nome': 'MARUBOZU_BULLISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BULLISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Corpo forte: {corpo_atual:.2f}'
                    })
                
                # MARUBOZU BEARISH
                elif (close_atual < open_atual and  # Bearish
                      sombra_superior < range_atual * 0.1 and  # Sombra superior pequena
                      sombra_inferior < range_atual * 0.1):  # Sombra inferior pequena
                    padroes.append({
                        'nome': 'MARUBOZU_BEARISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BEARISH',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Corpo forte: {corpo_atual:.2f}'
                    })
                
                # SPINNING TOP (corpo pequeno com sombras grandes)
                elif (corpo_atual < range_atual * 0.3 and  # Corpo pequeno
                      sombra_superior > range_atual * 0.2 and  # Sombras grandes
                      sombra_inferior > range_atual * 0.2):
                    padroes.append({
                        'nome': 'SPINNING_TOP',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': close_atual,
                        'confianca': 0.6,
                        'tipo': 'NEUTRO',
                        'categoria': 'CANDLESTICK',
                        'detalhes': f'Indecisão: Corpo {corpo_atual/range_atual*100:.1f}%'
                    })
                
                # MORNING STAR (3 candles)
                if candle_anterior2 is not None:
                    open_anterior2 = candle_anterior2['open']
                    close_anterior2 = candle_anterior2['close']
                    
                    # MORNING STAR: Bearish -> Doji -> Bullish
                    if (close_anterior2 < open_anterior2 and  # Primeiro bearish
                        abs(close_anterior - open_anterior) < range_anterior * 0.2 and  # Segundo doji
                        close_atual > open_atual and  # Terceiro bullish
                        close_atual > (open_anterior2 + close_anterior2) / 2):  # Quebra do meio
                        padroes.append({
                            'nome': 'MORNING_STAR',
                            'index': i,
                            'timestamp': df.index[i],
                            'sinal': 100,
                            'preco': close_atual,
                            'confianca': 0.9,
                            'tipo': 'BULLISH',
                            'categoria': 'CANDLESTICK',
                            'detalhes': 'Reversão de 3 candles'
                        })
                    
                    # EVENING STAR: Bullish -> Doji -> Bearish
                    if (close_anterior2 > open_anterior2 and  # Primeiro bullish
                        abs(close_anterior - open_anterior) < range_anterior * 0.2 and  # Segundo doji
                        close_atual < open_atual and  # Terceiro bearish
                        close_atual < (open_anterior2 + close_anterior2) / 2):  # Quebra do meio
                        padroes.append({
                            'nome': 'EVENING_STAR',
                            'index': i,
                            'timestamp': df.index[i],
                            'sinal': -100,
                            'preco': close_atual,
                            'confianca': 0.9,
                            'tipo': 'BEARISH',
                            'categoria': 'CANDLESTICK',
                            'detalhes': 'Reversão de 3 candles'
                        })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_talib(self, df):
        """Detecta padrões usando TA-Lib"""
        try:
            padroes = []
            
            # Converter para arrays numpy
            open_prices = df['open'].values
            high_prices = df['high'].values
            low_prices = df['low'].values
            close_prices = df['close'].values
            
            # Lista de padrões para detectar
            padroes_talib = [
                ('DOJI', talib.CDLDOJI),
                ('HAMMER', talib.CDLHAMMER),
                ('HANGING_MAN', talib.CDLHANGINGMAN),
                ('SHOOTING_STAR', talib.CDLSHOOTINGSTAR),
                ('ENGULFING_BULLISH', talib.CDLENGULFING),
                ('ENGULFING_BEARISH', talib.CDLENGULFING),
                ('MORNING_STAR', talib.CDLMORNINGSTAR),
                ('EVENING_STAR', talib.CDLEVENINGSTAR),
                ('HARAMI_BULLISH', talib.CDLHARAMI),
                ('HARAMI_BEARISH', talib.CDLHARAMI),
                ('PIERCING_LINE', talib.CDLPIERCING),
                ('DARK_CLOUD_COVER', talib.CDLDARKCLOUDCOVER),
                ('SPINNING_TOP', talib.CDLSPINNINGTOP),
                ('MARUBOZU_BULLISH', talib.CDLMARUBOZU),
                ('MARUBOZU_BEARISH', talib.CDLMARUBOZU)
            ]
            
            for nome, funcao in padroes_talib:
                try:
                    resultado = funcao(open_prices, high_prices, low_prices, close_prices)
                    
                    # Encontrar ocorrências do padrão
                    indices = np.where(resultado != 0)[0]
                    
                    for idx in indices:
                        if idx < len(df):
                            padroes.append({
                                'nome': nome,
                                'index': idx,
                                'timestamp': df.index[idx],
                                'sinal': resultado[idx],
                                'preco': close_prices[idx],
                                'confianca': abs(resultado[idx]) / 100.0,
                                'tipo': 'BULLISH' if resultado[idx] > 0 else 'BEARISH'
                            })
                except:
                    continue
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_proprios(self, df):
        """Detecta padrões usando implementações próprias"""
        try:
            padroes = []
            
            for i in range(len(df)):
                if i < 2:  # Precisa de pelo menos 2 candles para comparação
                    continue
                
                # Dados do candle atual e anterior
                candle_atual = df.iloc[i]
                candle_anterior = df.iloc[i-1]
                
                open_atual = candle_atual['open']
                high_atual = candle_atual['high']
                low_atual = candle_atual['low']
                close_atual = candle_atual['close']
                
                open_anterior = candle_anterior['open']
                high_anterior = candle_anterior['high']
                low_anterior = candle_anterior['low']
                close_anterior = candle_anterior['close']
                
                # Calcular métricas
                range_atual = high_atual - low_atual
                corpo_atual = abs(close_atual - open_atual)
                sombra_superior = high_atual - max(open_atual, close_atual)
                sombra_inferior = min(open_atual, close_atual) - low_atual
                
                range_anterior = high_anterior - low_anterior
                corpo_anterior = abs(close_anterior - open_anterior)
                
                # DOJI
                if corpo_atual < range_atual * 0.1:  # Corpo muito pequeno
                    padroes.append({
                        'nome': 'DOJI',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': close_atual,
                        'confianca': 0.7,
                        'tipo': 'NEUTRO'
                    })
                
                # HAMMER
                elif (sombra_inferior > corpo_atual * 2 and 
                      sombra_superior < corpo_atual * 0.5 and
                      close_atual > open_atual):
                    padroes.append({
                        'nome': 'HAMMER',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BULLISH'
                    })
                
                # HANGING MAN
                elif (sombra_inferior > corpo_atual * 2 and 
                      sombra_superior < corpo_atual * 0.5 and
                      close_atual < open_atual):
                    padroes.append({
                        'nome': 'HANGING_MAN',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BEARISH'
                    })
                
                # SHOOTING STAR
                elif (sombra_superior > corpo_atual * 2 and 
                      sombra_inferior < corpo_atual * 0.5 and
                      close_atual < open_atual):
                    padroes.append({
                        'nome': 'SHOOTING_STAR',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BEARISH'
                    })
                
                # ENGULFING BULLISH
                elif (close_atual > open_atual and  # Candle atual bullish
                      close_anterior < open_anterior and  # Candle anterior bearish
                      open_atual < close_anterior and  # Abertura abaixo do fechamento anterior
                      close_atual > open_anterior):  # Fechamento acima da abertura anterior
                    padroes.append({
                        'nome': 'ENGULFING_BULLISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 100,
                        'preco': close_atual,
                        'confianca': 0.9,
                        'tipo': 'BULLISH'
                    })
                
                # ENGULFING BEARISH
                elif (close_atual < open_atual and  # Candle atual bearish
                      close_anterior > open_anterior and  # Candle anterior bullish
                      open_atual > close_anterior and  # Abertura acima do fechamento anterior
                      close_atual < open_anterior):  # Fechamento abaixo da abertura anterior
                    padroes.append({
                        'nome': 'ENGULFING_BEARISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.9,
                        'tipo': 'BEARISH'
                    })
                
                # MARUBOZU BULLISH
                elif (close_atual > open_atual and  # Bullish
                      sombra_superior < range_atual * 0.1 and  # Sombra superior pequena
                      sombra_inferior < range_atual * 0.1):  # Sombra inferior pequena
                    padroes.append({
                        'nome': 'MARUBOZU_BULLISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BULLISH'
                    })
                
                # MARUBOZU BEARISH
                elif (close_atual < open_atual and  # Bearish
                      sombra_superior < range_atual * 0.1 and  # Sombra superior pequena
                      sombra_inferior < range_atual * 0.1):  # Sombra inferior pequena
                    padroes.append({
                        'nome': 'MARUBOZU_BEARISH',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -100,
                        'preco': close_atual,
                        'confianca': 0.8,
                        'tipo': 'BEARISH'
                    })
                
                # SPINNING TOP
                elif (corpo_atual < range_atual * 0.3 and  # Corpo pequeno
                      sombra_superior > range_atual * 0.2 and  # Sombras grandes
                      sombra_inferior > range_atual * 0.2):
                    padroes.append({
                        'nome': 'SPINNING_TOP',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': close_atual,
                        'confianca': 0.6,
                        'tipo': 'NEUTRO'
                    })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_graficos_completos(self, df):
        """Detecta TODOS os padrões gráficos complexos"""
        try:
            padroes = []
            
            # Padrões básicos
            padroes.extend(self._detectar_triangles(df))
            padroes.extend(self._detectar_head_shoulders(df))
            padroes.extend(self._detectar_flags_pennants(df))
            padroes.extend(self._detectar_double_top_bottom(df))
            padroes.extend(self._detectar_wedges(df))
            
            # Padrões avançados
            padroes.extend(self._detectar_canals(df))
            padroes.extend(self._detectar_rectangles(df))
            padroes.extend(self._detectar_diamonds(df))
            padroes.extend(self._detectar_cups_handles(df))
            padroes.extend(self._detectar_symmetrical_patterns(df))
            
            return padroes
            
        except Exception as e:
            return []
    
    def _detectar_padroes_volume(self, df):
        """Detecta padrões de volume"""
        try:
            padroes = []
            
            if 'volume' not in df.columns:
                    return padroes
            
            volume = df['volume'].values
            volume_ma = np.mean(volume[-20:])  # Média móvel de 20 períodos
            
            for i in range(len(df)):
                if i < 5:  # Precisa de histórico
                    continue
                
                vol_atual = volume[i]
                vol_anterior = volume[i-1]
                vol_medio = np.mean(volume[i-5:i])
                
                # Volume Spike (volume 3x maior que a média)
                if vol_atual > vol_medio * 3:
                    padroes.append({
                        'nome': 'VOLUME_SPIKE',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 1 if df.iloc[i]['close'] > df.iloc[i]['open'] else -1,
                        'preco': df.iloc[i]['close'],
                        'confianca': min(vol_atual / vol_medio / 3, 1.0),
                        'tipo': 'BULLISH' if df.iloc[i]['close'] > df.iloc[i]['open'] else 'BEARISH',
                        'categoria': 'VOLUME',
                        'detalhes': f'Volume: {vol_atual:,.0f} vs Média: {vol_medio:,.0f}'
                    })
                
                # Acumulação (volume crescente com preço lateral)
                if i >= 10:
                    vol_trend = np.polyfit(range(10), volume[i-9:i+1], 1)[0]
                    price_range = (df.iloc[i-9:i+1]['high'].max() - df.iloc[i-9:i+1]['low'].min()) / df.iloc[i]['close']
                    
                    if vol_trend > 0 and price_range < 0.02:  # Volume crescente, preço lateral
                        padroes.append({
                            'nome': 'ACUMULACAO',
                            'index': i,
                            'timestamp': df.index[i],
                            'sinal': 1,
                            'preco': df.iloc[i]['close'],
                            'confianca': min(abs(vol_trend) * 100, 1.0),
                            'tipo': 'BULLISH',
                            'categoria': 'VOLUME',
                            'detalhes': f'Tendência Volume: {vol_trend:.2f}'
                        })
                
                # Distribuição (volume crescente com preço caindo)
                if i >= 10:
                    vol_trend = np.polyfit(range(10), volume[i-9:i+1], 1)[0]
                    price_trend = np.polyfit(range(10), df.iloc[i-9:i+1]['close'].values, 1)[0]
                    
                    if vol_trend > 0 and price_trend < 0:  # Volume crescente, preço caindo
                        padroes.append({
                            'nome': 'DISTRIBUICAO',
                            'index': i,
                            'timestamp': df.index[i],
                            'sinal': -1,
                            'preco': df.iloc[i]['close'],
                            'confianca': min(abs(vol_trend) * 50, 1.0),
                            'tipo': 'BEARISH',
                            'categoria': 'VOLUME',
                            'detalhes': f'Vol: {vol_trend:.2f}, Preço: {price_trend:.2f}'
                        })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_preco(self, df):
        """Detecta padrões de preço"""
        try:
            padroes = []
            
            # Calcular suportes e resistências
            highs = df['high'].values
            lows = df['low'].values
            
            for i in range(20, len(df) - 20):
                # Resistência (máximo local)
                if highs[i] == np.max(highs[i-20:i+20]):
                    padroes.append({
                        'nome': 'RESISTENCIA',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -1,
                        'preco': highs[i],
                        'confianca': 0.8,
                        'tipo': 'BEARISH',
                        'categoria': 'PRECO',
                        'detalhes': f'Resistência em ${highs[i]:,.2f}'
                    })
                
                # Suporte (mínimo local)
                if lows[i] == np.min(lows[i-20:i+20]):
                    padroes.append({
                        'nome': 'SUPORTE',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 1,
                        'preco': lows[i],
                        'confianca': 0.8,
                        'tipo': 'BULLISH',
                        'categoria': 'PRECO',
                        'detalhes': f'Suporte em ${lows[i]:,.2f}'
                    })
                
                # Breakout de resistência
                if i > 0 and df.iloc[i]['close'] > highs[i-1] and highs[i-1] == np.max(highs[i-21:i]):
                    padroes.append({
                        'nome': 'BREAKOUT_RESISTENCIA',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 1,
                        'preco': df.iloc[i]['close'],
                        'confianca': 0.9,
                        'tipo': 'BULLISH',
                        'categoria': 'PRECO',
                        'detalhes': f'Quebra resistência ${highs[i-1]:,.2f}'
                    })
                
                # Breakdown de suporte
                if i > 0 and df.iloc[i]['close'] < lows[i-1] and lows[i-1] == np.min(lows[i-21:i]):
                    padroes.append({
                        'nome': 'BREAKDOWN_SUPORTE',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -1,
                        'preco': df.iloc[i]['close'],
                        'confianca': 0.9,
                        'tipo': 'BEARISH',
                        'categoria': 'PRECO',
                        'detalhes': f'Quebra suporte ${lows[i-1]:,.2f}'
                    })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_tempo(self, df):
        """Detecta padrões de tempo"""
        try:
            padroes = []
            
            # Converter timestamps para análise temporal
            timestamps = pd.to_datetime(df.index)
            horas = timestamps.hour
            dias_semana = timestamps.dayofweek
            
            for i in range(len(df)):
                hora_atual = horas[i]
                dia_atual = dias_semana[i]
                
                # Padrões de horário (mercados específicos)
                if hora_atual in [9, 10, 14, 15]:  # Horários de alta volatilidade
                    padroes.append({
                        'nome': 'HORARIO_ALTA_VOLATILIDADE',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': df.iloc[i]['close'],
                        'confianca': 0.7,
                        'tipo': 'NEUTRO',
                        'categoria': 'TEMPO',
                        'detalhes': f'Hora: {hora_atual}:00'
                    })
                
                # Padrões de dia da semana
                if dia_atual in [0, 4]:  # Segunda e sexta
                    padroes.append({
                        'nome': 'DIA_SEMANA_ESPECIAL',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': df.iloc[i]['close'],
                        'confianca': 0.6,
                        'tipo': 'NEUTRO',
                        'categoria': 'TEMPO',
                        'detalhes': f'Dia: {["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"][dia_atual]}'
                    })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_momentum(self, df):
        """Detecta padrões de momentum"""
        try:
            padroes = []
            
            # Calcular RSI
            closes = df['close'].values
            rsi = talib.RSI(closes, timeperiod=14)
            
            for i in range(len(df)):
                if i < 14 or np.isnan(rsi[i]):
                    continue
                
                rsi_atual = rsi[i]
                rsi_anterior = rsi[i-1] if i > 0 else rsi[i]
                
                # Divergência Bullish (preço caindo, RSI subindo)
                if i >= 10:
                    price_trend = np.polyfit(range(10), closes[i-9:i+1], 1)[0]
                    rsi_trend = np.polyfit(range(10), rsi[i-9:i+1], 1)[0]
                    
                    if price_trend < 0 and rsi_trend > 0 and rsi_atual < 30:
                        padroes.append({
                            'nome': 'DIVERGENCIA_BULLISH',
                            'index': i,
                            'timestamp': df.index[i],
                            'sinal': 1,
                            'preco': closes[i],
                            'confianca': 0.8,
                            'tipo': 'BULLISH',
                            'categoria': 'MOMENTUM',
                            'detalhes': f'RSI: {rsi_atual:.1f}, Preço: {price_trend:.4f}'
                        })
                    
                    # Divergência Bearish (preço subindo, RSI caindo)
                    if price_trend > 0 and rsi_trend < 0 and rsi_atual > 70:
                        padroes.append({
                            'nome': 'DIVERGENCIA_BEARISH',
                            'index': i,
                            'timestamp': df.index[i],
                            'sinal': -1,
                            'preco': closes[i],
                            'confianca': 0.8,
                            'tipo': 'BEARISH',
                            'categoria': 'MOMENTUM',
                            'detalhes': f'RSI: {rsi_atual:.1f}, Preço: {price_trend:.4f}'
                        })
                
                # RSI Oversold/Overbought
                if rsi_atual < 20:
                    padroes.append({
                        'nome': 'RSI_OVERSOLD',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 1,
                        'preco': closes[i],
                        'confianca': 0.7,
                        'tipo': 'BULLISH',
                        'categoria': 'MOMENTUM',
                        'detalhes': f'RSI: {rsi_atual:.1f}'
                    })
                
                if rsi_atual > 80:
                    padroes.append({
                        'nome': 'RSI_OVERBOUGHT',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': -1,
                        'preco': closes[i],
                        'confianca': 0.7,
                        'tipo': 'BEARISH',
                        'categoria': 'MOMENTUM',
                        'detalhes': f'RSI: {rsi_atual:.1f}'
                    })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_volatilidade(self, df):
        """Detecta padrões de volatilidade"""
        try:
            padroes = []
            
            # Calcular ATR
            highs = df['high'].values
            lows = df['low'].values
            closes = df['close'].values
            atr = talib.ATR(highs, lows, closes, timeperiod=14)
            
            for i in range(len(df)):
                if i < 14 or np.isnan(atr[i]):
                    continue
                
                atr_atual = atr[i]
                atr_medio = np.mean(atr[i-20:i]) if i >= 20 else atr_atual
                
                # Alta volatilidade
                if atr_atual > atr_medio * 1.5:
                    padroes.append({
                        'nome': 'ALTA_VOLATILIDADE',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': closes[i],
                        'confianca': min(atr_atual / atr_medio / 1.5, 1.0),
                        'tipo': 'NEUTRO',
                        'categoria': 'VOLATILIDADE',
                        'detalhes': f'ATR: {atr_atual:.2f} vs Média: {atr_medio:.2f}'
                    })
                
                # Baixa volatilidade
                if atr_atual < atr_medio * 0.5:
                    padroes.append({
                        'nome': 'BAIXA_VOLATILIDADE',
                        'index': i,
                        'timestamp': df.index[i],
                        'sinal': 0,
                        'preco': closes[i],
                        'confianca': 0.8,
                        'tipo': 'NEUTRO',
                        'categoria': 'VOLATILIDADE',
                        'detalhes': f'ATR: {atr_atual:.2f} vs Média: {atr_medio:.2f}'
                    })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_padroes_graficos(self, df):
        """Detecta padrões gráficos complexos"""
        try:
            padroes = []
            
            # 1. TRIÂNGULOS
            padroes.extend(self._detectar_triangulos(df))
            
            # 2. HEAD AND SHOULDERS
            padroes.extend(self._detectar_head_shoulders(df))
            
            # 3. FLAGS E PENNANTS
            padroes.extend(self._detectar_flags_pennants(df))
            
            # 4. DOUBLE TOP/BOTTOM
            padroes.extend(self._detectar_double_top_bottom(df))
            
            # 5. WEDGES
            padroes.extend(self._detectar_wedges(df))
            
            return padroes
            
        except Exception as e:
            return []
    
    def _detectar_triangulos(self, df):
        """Detecta padrões de triângulo"""
        try:
            padroes = []
            
            # Calcular máximos e mínimos locais
            highs = df['high'].values
            lows = df['low'].values
            
            # Encontrar picos e vales
            peaks, _ = find_peaks(highs, distance=5)
            valleys, _ = find_peaks(-lows, distance=5)
            
            if len(peaks) >= 3 and len(valleys) >= 3:
                # Analisar últimos 3 picos e vales
                ultimos_picos = peaks[-3:]
                ultimos_vales = valleys[-3:]
                
                # TRIÂNGULO ASCENDENTE: Máximos horizontais, mínimos ascendentes
                if len(ultimos_picos) >= 2 and len(ultimos_vales) >= 2:
                    max_diff = np.std([highs[p] for p in ultimos_picos[-2:]])
                    min_slope = np.polyfit(range(len(ultimos_vales[-2:])), [lows[v] for v in ultimos_vales[-2:]], 1)[0]
                    
                    if max_diff < np.mean(highs) * 0.01 and min_slope > 0:
                        padroes.append({
                            'nome': 'TRIANGULO_ASCENDENTE',
                            'tipo': 'CONTINUACAO',
                            'sinal': 'BULLISH',
                            'confianca': 0.7,
                            'picos': ultimos_picos.tolist(),
                            'vales': ultimos_vales.tolist(),
                            'alvo': highs[ultimos_picos[-1]] + (highs[ultimos_picos[-1]] - lows[ultimos_vales[-1]])
                        })
                
                # TRIÂNGULO DESCENDENTE: Mínimos horizontais, máximos descendentes
                if len(ultimos_picos) >= 2 and len(ultimos_vales) >= 2:
                    min_diff = np.std([lows[v] for v in ultimos_vales[-2:]])
                    max_slope = np.polyfit(range(len(ultimos_picos[-2:])), [highs[p] for p in ultimos_picos[-2:]], 1)[0]
                    
                    if min_diff < np.mean(lows) * 0.01 and max_slope < 0:
                        padroes.append({
                            'nome': 'TRIANGULO_DESCENDENTE',
                            'tipo': 'CONTINUACAO',
                            'sinal': 'BEARISH',
                            'confianca': 0.7,
                            'picos': ultimos_picos.tolist(),
                            'vales': ultimos_vales.tolist(),
                            'alvo': lows[ultimos_vales[-1]] - (highs[ultimos_picos[-1]] - lows[ultimos_vales[-1]])
                        })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_head_shoulders(self, df):
        """Detecta padrões Head and Shoulders"""
        try:
            padroes = []
            
            # Calcular máximos locais
            highs = df['high'].values
            peaks, _ = find_peaks(highs, distance=10)
            
            if len(peaks) >= 3:
                # Pegar últimos 3 picos
                ultimos_picos = peaks[-3:]
                pico_values = [highs[p] for p in ultimos_picos]
                
                # HEAD AND SHOULDERS: Pico do meio mais alto
                if len(pico_values) == 3:
                    left_shoulder, head, right_shoulder = pico_values
                    
                    # Verificar se o head é significativamente mais alto
                    if head > left_shoulder * 1.02 and head > right_shoulder * 1.02:
                        # Verificar se os ombros são similares
                        shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder
                        
                        if shoulder_diff < 0.03:  # 3% de diferença
                            padroes.append({
                                'nome': 'HEAD_AND_SHOULDERS',
                                'index': ultimos_picos[1],  # Usar índice do head
                                'timestamp': df.index[ultimos_picos[1]],
                                'preco': head,
                                'tipo': 'REVERSAO',
                                'sinal': 'BEARISH',
                                'confianca': 0.8,
                                'categoria': 'GRAFICO',
                                'picos': ultimos_picos.tolist(),
                                'neckline': (left_shoulder + right_shoulder) / 2,
                                'alvo': (left_shoulder + right_shoulder) / 2 - (head - (left_shoulder + right_shoulder) / 2)
                            })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_flags_pennants(self, df):
        """Detecta padrões Flag e Pennant"""
        try:
            padroes = []
            
            if len(df) < 50:
                    return padroes
            
            # Calcular médias móveis para identificar tendência
            df['ema_20'] = df['close'].ewm(span=20).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            
            # Identificar tendência
            tendencia_atual = 'ALTA' if df['ema_20'].iloc[-1] > df['ema_50'].iloc[-1] else 'BAIXA'
            
            # Analisar diferentes períodos para encontrar padrões
            for periodo in [10, 15, 20]:
                if len(df) < periodo + 20:
                    continue
                    
                df_recente = df.tail(periodo)
                
                # Calcular volatilidade
                volatilidade = df_recente['high'].max() - df_recente['low'].min()
                volatilidade_pct = (volatilidade / df_recente['close'].mean()) * 100
                
                # FLAG: Consolidação após movimento forte (mais permissivo)
                if volatilidade_pct < 3.0:  # Baixa volatilidade (mais permissivo)
                    # Verificar se houve movimento forte antes
                    df_antes = df.iloc[-(periodo+20):-periodo]
                    if len(df_antes) > 0:
                        movimento_antes = abs(df_antes['close'].iloc[-1] - df_antes['close'].iloc[0])
                        movimento_pct = (movimento_antes / df_antes['close'].iloc[0]) * 100
                        
                        if movimento_pct > 2.0:  # Movimento forte anterior (mais permissivo)
                            padroes.append({
                                'nome': f'FLAG_{periodo}D',
                                'index': len(df) - periodo // 2,  # Meio do período
                                'timestamp': df.index[len(df) - periodo // 2],
                                'preco': df['close'].iloc[len(df) - periodo // 2],
                                'tipo': 'CONTINUACAO',
                                'sinal': 'BULLISH' if tendencia_atual == 'ALTA' else 'BEARISH',
                                'confianca': 0.6,
                                'categoria': 'GRAFICO',
                                'volatilidade': volatilidade_pct,
                                'movimento_anterior': movimento_pct
                            })
                            break  # Encontrar apenas um padrão
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_double_top_bottom(self, df):
        """Detecta padrões Double Top e Double Bottom"""
        try:
            padroes = []
            
            # Calcular máximos e mínimos locais
            highs = df['high'].values
            lows = df['low'].values
            
            peaks, _ = find_peaks(highs, distance=10)
            valleys, _ = find_peaks(-lows, distance=10)
            
            # DOUBLE TOP: Dois máximos similares
            if len(peaks) >= 2:
                ultimos_picos = peaks[-2:]
                pico_values = [highs[p] for p in ultimos_picos]
                
                diff_pct = abs(pico_values[0] - pico_values[1]) / pico_values[0] * 100
                
                if diff_pct < 2.0:  # Máximos similares
                    padroes.append({
                        'nome': 'DOUBLE_TOP',
                        'tipo': 'REVERSAO',
                        'sinal': 'BEARISH',
                        'confianca': 0.7,
                        'picos': ultimos_picos.tolist(),
                        'nivel_resistencia': np.mean(pico_values)
                    })
            
            # DOUBLE BOTTOM: Dois mínimos similares
            if len(valleys) >= 2:
                ultimos_vales = valleys[-2:]
                vale_values = [lows[v] for v in ultimos_vales]
                
                diff_pct = abs(vale_values[0] - vale_values[1]) / vale_values[0] * 100
                
                if diff_pct < 2.0:  # Mínimos similares
                    padroes.append({
                        'nome': 'DOUBLE_BOTTOM',
                        'tipo': 'REVERSAO',
                        'sinal': 'BULLISH',
                        'confianca': 0.7,
                        'vales': ultimos_vales.tolist(),
                        'nivel_suporte': np.mean(vale_values)
                    })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _detectar_wedges(self, df):
        """Detecta padrões Wedge"""
        try:
            padroes = []
            
            # Calcular máximos e mínimos locais
            highs = df['high'].values
            lows = df['low'].values
            
            peaks, _ = find_peaks(highs, distance=5)
            valleys, _ = find_peaks(-lows, distance=5)
            
            if len(peaks) >= 3 and len(valleys) >= 3:
                # Analisar últimos 3 picos e vales
                ultimos_picos = peaks[-3:]
                ultimos_vales = valleys[-3:]
                
                # RISING WEDGE: Máximos e mínimos ascendentes, convergindo
                if len(ultimos_picos) >= 2 and len(ultimos_vales) >= 2:
                    max_slope = np.polyfit(range(len(ultimos_picos[-2:])), [highs[p] for p in ultimos_picos[-2:]], 1)[0]
                    min_slope = np.polyfit(range(len(ultimos_vales[-2:])), [lows[v] for v in ultimos_vales[-2:]], 1)[0]
                    
                    # Rising wedge: ambos ascendentes, mas máximos sobem mais devagar
                    if max_slope > 0 and min_slope > 0 and max_slope < min_slope:
                        padroes.append({
                            'nome': 'RISING_WEDGE',
                            'tipo': 'REVERSAO',
                            'sinal': 'BEARISH',
                            'confianca': 0.6,
                            'picos': ultimos_picos.tolist(),
                            'vales': ultimos_vales.tolist()
                        })
                
                # FALLING WEDGE: Máximos e mínimos descendentes, convergindo
                if len(ultimos_picos) >= 2 and len(ultimos_vales) >= 2:
                    max_slope = np.polyfit(range(len(ultimos_picos[-2:])), [highs[p] for p in ultimos_picos[-2:]], 1)[0]
                    min_slope = np.polyfit(range(len(ultimos_vales[-2:])), [lows[v] for v in ultimos_vales[-2:]], 1)[0]
                    
                    # Falling wedge: ambos descendentes, mas mínimos descem mais devagar
                    if max_slope < 0 and min_slope < 0 and min_slope > max_slope:
                        padroes.append({
                            'nome': 'FALLING_WEDGE',
                            'tipo': 'REVERSAO',
                            'sinal': 'BULLISH',
                            'confianca': 0.6,
                            'picos': ultimos_picos.tolist(),
                            'vales': ultimos_vales.tolist()
                        })
            
                return padroes
            
        except Exception as e:
                return []
    
    def _calcular_estatisticas_historicas(self, df):
        """Calcula estatísticas históricas dos candles"""
        try:
            stats = {
                'volatilidade_media': df['high'].sub(df['low']).mean(),
                'volatilidade_maxima': df['high'].sub(df['low']).max(),
                'volume_medio': df['volume'].mean(),
                'volume_maximo': df['volume'].max(),
                'corpo_medio': abs(df['close'] - df['open']).mean(),
                'corpo_maximo': abs(df['close'] - df['open']).max(),
                'tendencia_dominante': self._calcular_tendencia_dominante(df),
                'periodos_alta': len(df[df['close'] > df['open']]),
                'periodos_baixa': len(df[df['close'] < df['open']]),
                'periodos_neutros': len(df[df['close'] == df['open']])
            }
            
            return stats
            
        except Exception as e:
            return {}
    
    def _calcular_tendencia_dominante(self, df):
        """Calcula a tendência dominante no período"""
        try:
            # Calcular EMA 20 e 50
            df['ema_20'] = df['close'].ewm(span=20).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            
            # Contar períodos de alta e baixa
            periodos_alta = len(df[df['ema_20'] > df['ema_50']])
            periodos_baixa = len(df[df['ema_20'] < df['ema_50']])
            
            if periodos_alta > periodos_baixa:
                return 'ALTA'
            elif periodos_baixa > periodos_alta:
                return 'BAIXA'
            else:
                return 'LATERAL'
                
        except Exception as e:
            return 'INDEFINIDO'
    
    def _analisar_momentum_historico(self, df):
        """Analisa momentum histórico"""
        try:
            momentum = {
                'rsi_medio': df['close'].rolling(window=14).apply(lambda x: self._calcular_rsi(x)).mean(),
                'rsi_maximo': df['close'].rolling(window=14).apply(lambda x: self._calcular_rsi(x)).max(),
                'rsi_minimo': df['close'].rolling(window=14).apply(lambda x: self._calcular_rsi(x)).min(),
                'macd_tendencia': self._calcular_tendencia_macd(df),
                'momentum_atual': self._calcular_momentum_atual(df)
            }
            
            return momentum
            
        except Exception as e:
            return {}
    
    def _calcular_rsi(self, prices):
        """Calcula RSI para uma série de preços"""
        try:
            if len(prices) < 14:
                return 50
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).mean()
            loss = (-delta.where(delta < 0, 0)).mean()
            
            if loss == 0:
                return 100
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
            
        except Exception as e:
            return 50
    
    def _calcular_tendencia_macd(self, df):
        """Calcula tendência do MACD"""
        try:
            if len(df) < 26:
                return 'INDEFINIDO'
            
            # Calcular MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            
            # Analisar últimos valores
            macd_atual = macd.iloc[-1]
            signal_atual = signal.iloc[-1]
            
            if macd_atual > signal_atual:
                return 'BULLISH'
            elif macd_atual < signal_atual:
                return 'BEARISH'
            else:
                return 'NEUTRO'
                
        except Exception as e:
            return 'INDEFINIDO'
    
    def _calcular_momentum_atual(self, df):
        """Calcula momentum atual"""
        try:
            if len(df) < 10:
                return 0
            
            # Momentum baseado na diferença de preços
            momentum = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10] * 100
            
            return momentum
            
        except Exception as e:
            return 0
    
    def _analisar_volatilidade_historica(self, df):
        """Analisa volatilidade histórica"""
        try:
            volatilidade = {
                'atr_medio': df['high'].sub(df['low']).mean(),
                'atr_maximo': df['high'].sub(df['low']).max(),
                'volatilidade_percentual': (df['high'].sub(df['low']) / df['open'] * 100).mean(),
                'periodos_alta_volatilidade': len(df[(df['high'] - df['low']) / df['open'] * 100 > 3]),
                'periodos_baixa_volatilidade': len(df[(df['high'] - df['low']) / df['open'] * 100 < 1]),
                'tendencia_volatilidade': self._calcular_tendencia_volatilidade(df)
            }
            
            return volatilidade
            
        except Exception as e:
            return {}
    
    def _calcular_tendencia_volatilidade(self, df):
        """Calcula tendência da volatilidade"""
        try:
            if len(df) < 20:
                return 'INDEFINIDO'
            
            # Calcular volatilidade móvel
            df['volatilidade'] = (df['high'] - df['low']) / df['open'] * 100
            df['vol_ma'] = df['volatilidade'].rolling(window=10).mean()
            
            # Comparar primeira e segunda metade
            primeira_metade = df['vol_ma'].iloc[:len(df)//2].mean()
            segunda_metade = df['vol_ma'].iloc[len(df)//2:].mean()
            
            if segunda_metade > primeira_metade * 1.1:
                return 'CRESCENTE'
            elif segunda_metade < primeira_metade * 0.9:
                return 'DECRESCENTE'
            else:
                return 'ESTAVEL'
                
        except Exception as e:
            return 'INDEFINIDO'


def analisar_candles_avancado(df_candles, lookback_periods=50):
    """
    Função principal para análise avançada de candles
    
    Args:
        df_candles: DataFrame com dados OHLCV
        lookback_periods: Número de períodos para analisar
        
    Returns:
        dict com análise completa
    """
    try:
        analisador = AnalisadorCandlesAvancado(df_candles)
        resultado = analisador.analisar_candles_passados(lookback_periods)
        
        return resultado
        
    except Exception as e:
        return {'erro': f'Erro na análise avançada: {str(e)}'}


def _detectar_padroes_sequencia(df):
    """Detecta padrões de sequência de preços"""
    try:
        padroes = []
        
        if len(df) < 20:
            return padroes
        
        closes = df['close'].values
        
        # SEQUÊNCIA DE ALTA (3+ candles consecutivos de alta)
        for i in range(len(df) - 5):
            sequencia_alta = 0
            for j in range(5):
                if i + j + 1 < len(df) and closes[i + j + 1] > closes[i + j]:
                    sequencia_alta += 1
                else:
                    break
                
            if sequencia_alta >= 3:
                padroes.append({
                    'nome': f'SEQUENCIA_ALTA_{sequencia_alta}',
                    'index': i + sequencia_alta,
                    'timestamp': df.index[i + sequencia_alta],
                    'preco': closes[i + sequencia_alta],
                    'tipo': 'BULLISH',
                    'sinal': 'BULLISH',
                    'confianca': min(sequencia_alta / 5, 1.0),
                    'categoria': 'SEQUENCIA',
                    'detalhes': f'{sequencia_alta} candles consecutivos de alta'
                })
            
        # SEQUÊNCIA DE BAIXA (3+ candles consecutivos de baixa)
        for i in range(len(df) - 5):
            sequencia_baixa = 0
            for j in range(5):
                if i + j + 1 < len(df) and closes[i + j + 1] < closes[i + j]:
                    sequencia_baixa += 1
                else:
                    break
                
            if sequencia_baixa >= 3:
                padroes.append({
                    'nome': f'SEQUENCIA_BAIXA_{sequencia_baixa}',
                    'index': i + sequencia_baixa,
                    'timestamp': df.index[i + sequencia_baixa],
                    'preco': closes[i + sequencia_baixa],
                    'tipo': 'BEARISH',
                    'sinal': 'BEARISH',
                    'confianca': min(sequencia_baixa / 5, 1.0),
                    'categoria': 'SEQUENCIA',
                    'detalhes': f'{sequencia_baixa} candles consecutivos de baixa'
                })
        
            return padroes
        
    except Exception as e:
            return []
    
def _detectar_padroes_breakout(df):
    """Detecta padrões de breakout"""
    try:
        padroes = []
        
        if len(df) < 50:
            return padroes
        
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        
        for i in range(50, len(df)):
            # BREAKOUT DE ALTA (preço rompe resistência)
            resistencia = highs[i-20:i].max()
            if closes[i] > resistencia * 1.001:  # 0.1% acima da resistência
                padroes.append({
                    'nome': 'BREAKOUT_ALTA',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': closes[i],
                    'tipo': 'BREAKOUT',
                    'sinal': 'BULLISH',
                    'confianca': 0.8,
                    'categoria': 'BREAKOUT',
                    'detalhes': f'Rompeu resistência em ${resistencia:.2f}'
                })
            
            # BREAKOUT DE BAIXA (preço rompe suporte)
            suporte = lows[i-20:i].min()
            if closes[i] < suporte * 0.999:  # 0.1% abaixo do suporte
                padroes.append({
                    'nome': 'BREAKOUT_BAIXA',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': closes[i],
                    'tipo': 'BREAKOUT',
                    'sinal': 'BEARISH',
                    'confianca': 0.8,
                    'categoria': 'BREAKOUT',
                    'detalhes': f'Rompeu suporte em ${suporte:.2f}'
                })
        
        return padroes
        
    except Exception as e:
        return []
    
def _detectar_padroes_divergencia(df):
    """Detecta divergências entre preço e indicadores"""
    try:
        padroes = []
        
        if len(df) < 30:
            return padroes
        
        # Calcular RSI simples
        closes = df['close'].values
        rsi = _calcular_rsi_simples(closes)
        
        if len(rsi) < 20:
            return padroes
        
        # DIVERGÊNCIA BULLISH (preço faz mínima menor, RSI faz mínima maior)
        for i in range(20, len(df)):
            # Encontrar mínima recente no preço
            min_preco_idx = np.argmin(closes[i-10:i])
            min_preco_valor = closes[i-10+min_preco_idx]
            
            # Encontrar mínima recente no RSI
            min_rsi_idx = np.argmin(rsi[i-10:i])
            min_rsi_valor = rsi[i-10+min_rsi_idx]
            
            # Verificar divergência bullish
            if (min_preco_idx < min_rsi_idx and  # Preço fez mínima antes
                min_preco_valor < closes[i-15] and  # Preço caiu
                min_rsi_valor > rsi[i-15]):  # RSI subiu
                padroes.append({
                    'nome': 'DIVERGENCIA_BULLISH',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': closes[i],
                    'tipo': 'DIVERGENCIA',
                    'sinal': 'BULLISH',
                    'confianca': 0.7,
                    'categoria': 'DIVERGENCIA',
                    'detalhes': f'Preço: ${min_preco_valor:.2f}, RSI: {min_rsi_valor:.1f}'
                })
        
        return padroes
        
    except Exception as e:
        return []
    
def _detectar_padroes_liquidez(df):
    """Detecta padrões relacionados à liquidez"""
    try:
        padroes = []
            
        if len(df) < 20:
            return padroes
            
        # Calcular volume médio
        volumes = df['volume'].values
        volume_medio = np.mean(volumes[-20:])
            
        # LIQUIDEZ ALTA (volume muito acima da média)
        for i in range(len(df)):
            if volumes[i] > volume_medio * 2.5:  # 2.5x acima da média
                padroes.append({
                    'nome': 'LIQUIDEZ_ALTA',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': df['close'].iloc[i],
                    'tipo': 'LIQUIDEZ',
                    'sinal': 'BULLISH' if df['close'].iloc[i] > df['open'].iloc[i] else 'BEARISH',
                    'confianca': min(volumes[i] / volume_medio / 2.5, 1.0),
                    'categoria': 'LIQUIDEZ',
                    'detalhes': f'Volume: {volumes[i]:,.0f} vs Média: {volume_medio:,.0f}'
                })
            
            return padroes
            
    except Exception as e:
            return []
    
def _detectar_padroes_sentimento(df):
    """Detecta padrões de sentimento do mercado"""
    try:
        padroes = []
            
        if len(df) < 20:
            return padroes
            
        closes = df['close'].values
            
        # SENTIMENTO DE MEDO (queda rápida)
        for i in range(20, len(df)):
            queda_rapida = (closes[i-5] - closes[i]) / closes[i-5]
            if queda_rapida > 0.05:  # 5% de queda em 5 candles
                padroes.append({
                    'nome': 'SENTIMENTO_MEDO',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': closes[i],
                    'tipo': 'SENTIMENTO',
                    'sinal': 'BEARISH',
                    'confianca': min(queda_rapida * 10, 1.0),
                    'categoria': 'SENTIMENTO',
                    'detalhes': f'Queda: {queda_rapida*100:.1f}% em 5 candles'
                })
            
        # SENTIMENTO DE GANÂNCIA (alta rápida)
        for i in range(20, len(df)):
            alta_rapida = (closes[i] - closes[i-5]) / closes[i-5]
            if alta_rapida > 0.05:  # 5% de alta em 5 candles
                padroes.append({
                    'nome': 'SENTIMENTO_GANANCIA',
                    'index': i,
                    'timestamp': df.index[i],
                    'preco': closes[i],
                    'tipo': 'SENTIMENTO',
                    'sinal': 'BULLISH',
                    'confianca': min(alta_rapida * 10, 1.0),
                    'categoria': 'SENTIMENTO',
                    'detalhes': f'Alta: {alta_rapida*100:.1f}% em 5 candles'
                })
            
            return padroes
            
    except Exception as e:
            return []
    
def _calcular_rsi_simples(closes, periodo=14):
        """Calcula RSI de forma simples"""
        try:
            if len(closes) < periodo + 1:
                    return []
            
            rsi = []
            for i in range(periodo, len(closes)):
                ganhos = []
                perdas = []
                
                for j in range(periodo):
                    mudanca = closes[i-j] - closes[i-j-1]
                    if mudanca > 0:
                        ganhos.append(mudanca)
                        perdas.append(0)
                    else:
                        ganhos.append(0)
                        perdas.append(abs(mudanca))
                
                ganho_medio = np.mean(ganhos)
                perda_media = np.mean(perdas)
                
                if perda_media == 0:
                    rsi.append(100)
                else:
                    rs = ganho_medio / perda_media
                    rsi.append(100 - (100 / (1 + rs)))
            
            return rsi
            
        except Exception as e:
                return []

if __name__ == "__main__":
    # Teste com dados simulados
    import pandas as pd
    import numpy as np
    
    # Criar dados simulados
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    
    # Simular preços com padrões
    base_price = 100
    prices = [base_price]
    
    for i in range(99):
        # Adicionar alguns padrões específicos
        if i == 30:  # Hammer
            prices.append(prices[-1] * 0.98)
        elif i == 50:  # Doji
            prices.append(prices[-1])
        elif i == 70:  # Engulfing
            prices.append(prices[-1] * 1.03)
        else:
            change = np.random.normal(0, 0.02)
            prices.append(prices[-1] * (1 + change))
    
    # Criar DataFrame
    df = pd.DataFrame({
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices[1:] + [prices[-1]],
        'volume': np.random.uniform(1000, 10000, 100)
    }, index=dates)
    
    # Ajustar high/low para serem consistentes
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    # Executar análise
    resultado = analisar_candles_avancado(df, 50)
    
    print("="*60)
    print("ANÁLISE AVANÇADA DE CANDLES E PADRÕES")
    print("="*60)
    
    if 'erro' not in resultado:
        print(f"📊 Período analisado: {resultado['periodo_analisado']} candles")
        print(f"📊 Total de candles: {resultado['total_candles']}")
        
        print(f"\n🔍 CANDLES SIGNIFICATIVOS: {len(resultado['candles_significativos'])}")
        for candle in resultado['candles_significativos'][:5]:  # Mostrar apenas os 5 primeiros
            print(f"   • {candle['caracteristicas']} - Significância: {candle['significancia']}")
        
        print(f"\n📈 PADRÕES CANDLESTICK: {len(resultado['padroes_candlestick'])}")
        for padrao in resultado['padroes_candlestick'][:5]:
            print(f"   • {padrao['nome']} ({padrao['tipo']}) - Confiança: {padrao['confianca']:.2f}")
        
        print(f"\n🔺 PADRÕES GRÁFICOS: {len(resultado['padroes_graficos'])}")
        for padrao in resultado['padroes_graficos']:
            print(f"   • {padrao['nome']} ({padrao['sinal']}) - Confiança: {padrao['confianca']:.2f}")
        
        print(f"\n📊 ESTATÍSTICAS:")
        stats = resultado['estatisticas']
        print(f"   • Volatilidade média: {stats.get('volatilidade_media', 0):.2f}")
        print(f"   • Volume médio: {stats.get('volume_medio', 0):,.0f}")
        print(f"   • Tendência dominante: {stats.get('tendencia_dominante', 'N/A')}")
        
        print(f"\n⚡ MOMENTUM:")
        momentum = resultado['momentum_historico']
        print(f"   • RSI médio: {momentum.get('rsi_medio', 0):.1f}")
        print(f"   • MACD tendência: {momentum.get('macd_tendencia', 'N/A')}")
        print(f"   • Momentum atual: {momentum.get('momentum_atual', 0):.2f}%")
        
        print(f"\n📊 VOLATILIDADE:")
        vol = resultado['volatilidade_historica']
        print(f"   • ATR médio: {vol.get('atr_medio', 0):.2f}")
        print(f"   • Volatilidade %: {vol.get('volatilidade_percentual', 0):.2f}%")
        print(f"   • Tendência volatilidade: {vol.get('tendencia_volatilidade', 'N/A')}")
        
    else:
        print(f"❌ Erro: {resultado['erro']}")

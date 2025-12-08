#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Profissional de Sinais Multi-Timeframe
Análise validada em múltiplos timeframes para sinais de alta qualidade
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz

class MultiTimeframeSignal:
    """
    Gerador de sinais validados em múltiplos timeframes
    """
    
    def __init__(self):
        self.timeframes = ['1m', '5m', '15m', '1h']
        self.min_confirmations = 3  # Mínimo de 3 timeframes confirmando
        self.br_tz = pytz.timezone("America/Sao_Paulo")
    
    def analisar_multi_timeframe(self, symbol):
        """
        Analisa símbolo em todos os timeframes
        Retorna sinal apenas se houver confirmação em múltiplos TFs
        """
        try:
            print(f"   📊 Analisando {symbol}...", end=" ", flush=True)
            
            resultados = {}
            
            # Analisar cada timeframe
            for tf in self.timeframes:
                df = self._buscar_dados(symbol, interval=tf, limit=100)
                if df is not None and len(df) >= 50:
                    analise = self._analisar_timeframe(df, tf, symbol)
                    resultados[tf] = analise
            
            # Validação cruzada
            if len(resultados) >= 3:  # Mínimo de 3 timeframes analisados
                sinal_final = self._validar_cruzado(symbol, resultados)
                
                if sinal_final:
                    print(f"✅ Score: {sinal_final['score_confianca']:.0f}%")
                else:
                    print("⏸️")
                
                return sinal_final
            else:
                print("❌ Dados insuficientes")
                return None
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def _buscar_dados(self, symbol, interval='1m', limit=100):
        """
        Busca dados da Binance
        """
        try:
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df
        except:
            return None
    
    def _analisar_timeframe(self, df, timeframe, symbol):
        """
        Análise completa em um timeframe específico
        """
        preco_atual = df['close'].iloc[-1]
        
        # Calcular indicadores
        df['ema8'] = df['close'].ewm(span=8).mean()
        df['ema21'] = df['close'].ewm(span=21).mean()
        df['sma50'] = df['close'].rolling(50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Volume
        df['volume_ma'] = df['volume'].rolling(20).mean()
        volume_ratio = df['volume'].iloc[-1] / df['volume_ma'].iloc[-1] if df['volume_ma'].iloc[-1] > 0 else 1
        
        # Suporte e Resistência
        suporte = df['low'].rolling(20).min().iloc[-1]
        resistencia = df['high'].rolling(20).max().iloc[-1]
        
        # Detectar tendência
        tendencia = self._detectar_tendencia(df)
        
        # Momentum
        momentum = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1) * 100 if len(df) >= 5 else 0
        
        # Volatilidade
        volatilidade = df['close'].pct_change().tail(20).std() * 100
        
        # Score do timeframe
        score_tf = self._calcular_score_tf(df, tendencia, volume_ratio, volatilidade)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'preco_atual': preco_atual,
            'tendencia': tendencia,
            'momentum': momentum,
            'volume_ratio': volume_ratio,
            'volatilidade': volatilidade,
            'rsi': df['rsi'].iloc[-1],
            'ema8': df['ema8'].iloc[-1],
            'ema21': df['ema21'].iloc[-1],
            'sma50': df['sma50'].iloc[-1],
            'suporte': suporte,
            'resistencia': resistencia,
            'score': score_tf
        }
    
    def _detectar_tendencia(self, df):
        """
        Detecta tendência baseado em EMAs
        """
        ema8 = df['ema8'].iloc[-1]
        ema21 = df['ema21'].iloc[-1]
        sma50 = df['sma50'].iloc[-1]
        
        if ema8 > ema21 > sma50:
            return 'ALTA'
        elif ema8 < ema21 < sma50:
            return 'BAIXA'
        else:
            return 'LATERAL'
    
    def _calcular_score_tf(self, df, tendencia, volume_ratio, volatilidade):
        """
        Calcula score de qualidade do timeframe
        """
        score = 0
        
        # Tendência clara
        if tendencia in ['ALTA', 'BAIXA']:
            score += 30
        
        # Volume
        if volume_ratio > 1.3:
            score += 25
        elif volume_ratio > 1.0:
            score += 15
        
        # Volatilidade adequada
        if 0.5 < volatilidade < 3:
            score += 25
        elif volatilidade >= 3:
            score += 15
        
        # RSI não extremo
        rsi = df['rsi'].iloc[-1]
        if 30 < rsi < 70:
            score += 20
        elif 25 < rsi < 75:
            score += 10
        
        return score
    
    def _validar_cruzado(self, symbol, resultados):
        """
        Valida se múltiplos timeframes confirmam a mesma direção
        """
        # Contar confirmações
        confirmacoes_long = 0
        confirmacoes_short = 0
        
        for tf, analise in resultados.items():
            if analise['tendencia'] == 'ALTA':
                confirmacoes_long += 1
            elif analise['tendencia'] == 'BAIXA':
                confirmacoes_short += 1
        
        # Decisão
        if confirmacoes_long >= self.min_confirmations:
            return self._gerar_sinal_long(symbol, resultados)
        elif confirmacoes_short >= self.min_confirmations:
            return self._gerar_sinal_short(symbol, resultados)
        else:
            return None  # Sem consenso
    
    def _gerar_sinal_long(self, symbol, resultados):
        """
        Gera sinal de compra com níveis precisos
        """
        # Usar timeframe menor para entry, maiores para TP
        tf_1m = resultados.get('1m')
        tf_5m = resultados.get('5m')
        tf_15m = resultados.get('15m')
        tf_1h = resultados.get('1h')
        
        preco_atual = tf_1m['preco_atual']
        
        # Entry: Preço atual (ou próximo ao suporte do 1m)
        entry = preco_atual
        
        # TP: Resistências dos timeframes maiores
        tp1 = tf_5m['resistencia'] if tf_5m else preco_atual * 1.015
        tp2 = tf_15m['resistencia'] if tf_15m else preco_atual * 1.025
        tp3 = tf_1h['resistencia'] if tf_1h else preco_atual * 1.04
        
        # SL: Abaixo do suporte do 5m (mais seguro)
        sl = (tf_5m['suporte'] if tf_5m else preco_atual * 0.99) * 0.995
        
        # Calcular R/R
        risco = abs(entry - sl)
        retorno1 = abs(tp1 - entry)
        retorno2 = abs(tp2 - entry)
        retorno3 = abs(tp3 - entry)
        
        # Validar R/R mínimo
        if risco == 0 or retorno1 / risco < 1.5:
            return None
        
        # Listar confirmações
        confirmacoes = self._listar_confirmacoes(resultados, 'LONG')
        
        # Calcular score de confiança
        score_confianca = self._calcular_confianca(resultados, 'LONG')
        
        return {
            'tipo': 'LONG',
            'symbol': symbol,
            'entry': entry,
            'tp': [tp1, tp2, tp3],
            'sl': sl,
            'risco_retorno': [
                retorno1 / risco if risco > 0 else 0,
                retorno2 / risco if risco > 0 else 0,
                retorno3 / risco if risco > 0 else 0
            ],
            'confirmacoes': confirmacoes,
            'timeframe_principal': '1m',
            'timeframe_target': '1h',
            'validade': '30 minutos',
            'score_confianca': score_confianca,
            'timestamp': datetime.now(self.br_tz)
        }
    
    def _gerar_sinal_short(self, symbol, resultados):
        """
        Gera sinal de venda com níveis precisos
        """
        # Usar timeframe menor para entry, maiores para TP
        tf_1m = resultados.get('1m')
        tf_5m = resultados.get('5m')
        tf_15m = resultados.get('15m')
        tf_1h = resultados.get('1h')
        
        preco_atual = tf_1m['preco_atual']
        
        # Entry: Preço atual (ou próximo à resistência do 1m)
        entry = preco_atual
        
        # TP: Suportes dos timeframes maiores
        tp1 = tf_5m['suporte'] if tf_5m else preco_atual * 0.985
        tp2 = tf_15m['suporte'] if tf_15m else preco_atual * 0.975
        tp3 = tf_1h['suporte'] if tf_1h else preco_atual * 0.96
        
        # SL: Acima da resistência do 5m (mais seguro)
        sl = (tf_5m['resistencia'] if tf_5m else preco_atual * 1.01) * 1.005
        
        # Calcular R/R
        risco = abs(sl - entry)
        retorno1 = abs(entry - tp1)
        retorno2 = abs(entry - tp2)
        retorno3 = abs(entry - tp3)
        
        # Validar R/R mínimo
        if risco == 0 or retorno1 / risco < 1.5:
            return None
        
        # Listar confirmações
        confirmacoes = self._listar_confirmacoes(resultados, 'SHORT')
        
        # Calcular score de confiança
        score_confianca = self._calcular_confianca(resultados, 'SHORT')
        
        return {
            'tipo': 'SHORT',
            'symbol': symbol,
            'entry': entry,
            'tp': [tp1, tp2, tp3],
            'sl': sl,
            'risco_retorno': [
                retorno1 / risco if risco > 0 else 0,
                retorno2 / risco if risco > 0 else 0,
                retorno3 / risco if risco > 0 else 0
            ],
            'confirmacoes': confirmacoes,
            'timeframe_principal': '1m',
            'timeframe_target': '1h',
            'validade': '30 minutos',
            'score_confianca': score_confianca,
            'timestamp': datetime.now(self.br_tz)
        }
    
    def _listar_confirmacoes(self, resultados, tipo):
        """
        Lista confirmações de cada timeframe
        """
        confirmacoes = []
        
        for tf, analise in resultados.items():
            if tipo == 'LONG' and analise['tendencia'] == 'ALTA':
                confirmacoes.append(f"{tf}: Tendência de alta confirmada")
                
                if analise['volume_ratio'] > 1.3:
                    confirmacoes.append(f"{tf}: Volume {(analise['volume_ratio']-1)*100:.0f}% acima da média")
                
                if analise['rsi'] < 50:
                    confirmacoes.append(f"{tf}: RSI em {analise['rsi']:.0f} (espaço para subir)")
            
            elif tipo == 'SHORT' and analise['tendencia'] == 'BAIXA':
                confirmacoes.append(f"{tf}: Tendência de baixa confirmada")
                
                if analise['volume_ratio'] > 1.3:
                    confirmacoes.append(f"{tf}: Volume {(analise['volume_ratio']-1)*100:.0f}% acima da média")
                
                if analise['rsi'] > 50:
                    confirmacoes.append(f"{tf}: RSI em {analise['rsi']:.0f} (espaço para cair)")
        
        return confirmacoes
    
    def _calcular_confianca(self, resultados, tipo):
        """
        Calcula score de confiança baseado em múltiplos fatores
        """
        score = 0
        
        # Número de timeframes confirmando
        confirmacoes = sum(1 for r in resultados.values() 
                          if (tipo == 'LONG' and r['tendencia'] == 'ALTA') or 
                             (tipo == 'SHORT' and r['tendencia'] == 'BAIXA'))
        
        score += confirmacoes * 15  # 15 pontos por confirmação
        
        # Score médio dos timeframes
        score_medio = np.mean([r['score'] for r in resultados.values()])
        score += score_medio * 0.4  # 40% do score médio
        
        # Volume consistente
        volumes_altos = sum(1 for r in resultados.values() if r['volume_ratio'] > 1.3)
        score += volumes_altos * 5
        
        return min(score, 100)






#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST SNE RADAR - SISTEMA MTF CANDLE POR CANDLE
Sistema de backtest que opera candle por candle com análise MTF contínua
"""

import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ColetorDadosHistoricosMTF:
    """Coletor de dados históricos para múltiplos timeframes"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SNE-Radar-MTF/1.0'
        })
    
    def coletar_dados_mtf(self, symbol: str, timeframes: List[str], start_date: str, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados históricos para múltiplos timeframes
        
        Args:
            symbol: Par (ex: 'BTCUSDT')
            timeframes: Lista de timeframes ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
            start_date: Data início (YYYY-MM-DD)
            end_date: Data fim (YYYY-MM-DD) - opcional
        
        Returns:
            Dict com DataFrames para cada timeframe
        """
        dados_mtf = {}
        
        for tf in timeframes:
            print(f"📊 Coletando dados históricos: {symbol} {tf} de {start_date} até {end_date or 'agora'}")
            
            try:
                # Converter datas para timestamp
                start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
                end_ts = int(pd.Timestamp(end_date).timestamp() * 1000) if end_date else None
                
                all_data = []
                current_start = start_ts
                
                while True:
                    params = {
                        'symbol': symbol,
                        'interval': tf,
                        'startTime': current_start,
                        'limit': 1000
                    }
                    
                    if end_ts:
                        params['endTime'] = min(current_start + (1000 * self._interval_to_ms(tf)), end_ts)
                    
                    response = self.session.get(self.base_url, params=params)
                    
                    if response.status_code != 200:
                        print(f"❌ Erro na API para {tf}: {response.status_code}")
                        break
                    
                    data = response.json()
                    
                    if not data:
                        break
                    
                    all_data.extend(data)
                    
                    # Próximo batch
                    current_start = data[-1][0] + 1
                    
                    if end_ts and current_start >= end_ts:
                        break
                    
                    # Rate limiting
                    time.sleep(0.1)
                
                if not all_data:
                    print(f"❌ Nenhum dado coletado para {symbol} {tf}")
                    continue
                
                # Converter para DataFrame
                df = pd.DataFrame(all_data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                # Converter tipos
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                # Definir índice
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                
                # Remover colunas desnecessárias
                df = df[['open', 'high', 'low', 'close', 'volume']]
                
                dados_mtf[tf] = df
                print(f"✅ {len(df)} candles coletados para {symbol} {tf}")
                
            except Exception as e:
                print(f"❌ Erro ao coletar dados {tf}: {e}")
                continue
        
        return dados_mtf
    
    def _interval_to_ms(self, interval: str) -> int:
        """Converte intervalo para milissegundos"""
        intervals = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000
        }
        return intervals.get(interval, 60 * 1000)

class BacktestSNEMTF:
    """Motor de backtest do SNE Radar com análise MTF candle por candle"""
    
    def __init__(self, capital_inicial: float = 10000.0):
        self.capital_inicial = capital_inicial
        self.capital_atual = capital_inicial
        self.posicao_atual = None
        self.trades = []
        self.equity_curve = []
        
        # Configurações do backtest
        self.comissao_pct = 0.001  # 0.1%
        self.stop_loss_pct = 0.015  # 1.5%
        self.take_profit_pct = 0.035  # 3.5%
        
        # Thresholds para abertura de posições (mais permissivos para MTF)
        self.confianca_minima = 50  # Confiança mínima para abrir posição
        self.score_minimo_long = 4.5  # Score mínimo para LONG
        self.score_maximo_short = 5.5  # Score máximo para SHORT
        
        # Confluência MTF mínima
        self.min_timeframes_confluencia = 2  # Mínimo de timeframes alinhados
        
        # Filtros adicionais
        self.filtro_volume_minimo = 0.3  # Volume mínimo (múltiplo da média)
        self.filtro_volatilidade_maxima = 200  # Volatilidade máxima (ATR %)
        
        # Bridge para análise SNE real
        self.sne_bridge = None
        
        # Cache de análises MTF para otimização
        self.cache_analises_mtf = {}
        self.timeframes_analise = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        
        # Histórico de sinais MTF para tracking
        self.historico_sinais_mtf = []
        
        # Dados MTF carregados
        self.dados_mtf = {}
    
    def carregar_dados_mtf(self, dados_mtf: Dict[str, pd.DataFrame]):
        """Carrega dados de múltiplos timeframes"""
        self.dados_mtf = dados_mtf
        print(f"📊 Dados MTF carregados: {list(dados_mtf.keys())}")
    
    def executar_backtest_mtf(self, symbol: str, start_date: str, end_date: str):
        """
        Executa backtest com análise MTF candle por candle
        
        Args:
            symbol: Par para análise
            start_date: Data início
            end_date: Data fim
        """
        print(f"\n🚀 INICIANDO BACKTEST SNE RADAR MTF")
        print(f"📊 Par: {symbol}")
        print(f"📅 Período: {start_date} até {end_date}")
        print(f"💰 Capital inicial: ${self.capital_inicial:,.2f}")
        print("=" * 60)
        
        # Usar dados do timeframe menor (1m) como base
        if '1m' not in self.dados_mtf:
            print("❌ Dados de 1m necessários para análise candle por candle")
            return
        
        df_base = self.dados_mtf['1m']
        
        # Filtrar período
        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)
        df_periodo = df_base.loc[start_ts:end_ts].copy()
        
        if df_periodo.empty:
            print(f"❌ Sem dados no período especificado")
            return
        
        print(f"📈 Analisando {len(df_periodo)} candles de 1m...")
        
        # Loop candle por candle
        for i in range(100, len(df_periodo)):  # Começar após 100 candles
            try:
                candle_atual = df_periodo.iloc[i]
                timestamp_atual = df_periodo.index[i]
                
                # Analisar MTF para este momento
                analise_mtf = self._analisar_mtf_candle(symbol, timestamp_atual, i)
                
                if analise_mtf:
                    # Detectar sinais MTF
                    sinais_mtf = self._detectar_sinais_mtf(analise_mtf)
                    
                    # Validar confluência MTF
                    acao, sinal_principal = self._validar_confluencia_mtf(sinais_mtf)
                    
                    # Gerenciar posição atual
                    if self.posicao_atual:
                        acao_posicao = self._gerenciar_posicao_mtf(analise_mtf)
                        if acao_posicao == 'FECHAR':
                            self._fechar_posicao_mtf(candle_atual, i, "Confluência MTF perdida")
                    
                    # Abrir nova posição se necessário
                    if acao in ['LONG', 'SHORT'] and not self.posicao_atual:
                        self._abrir_posicao_mtf(acao, sinal_principal, candle_atual, i)
                
                # Atualizar posição sempre (para stop loss/take profit)
                self._atualizar_posicao_mtf(candle_atual, i)
                
                # Log de progresso
                if i % 1000 == 0:
                    progresso = (i / len(df_periodo)) * 100
                    trades_abertos = len([t for t in self.trades if 'preco_saida' not in t])
                    print(f"⏳ Progresso: {progresso:.1f}% - Capital: ${self.capital_atual:,.2f} - Trades: {len(self.trades)} (Abertos: {trades_abertos})")
                
            except Exception as e:
                print(f"❌ Erro no candle {i}: {e}")
                continue
        
        # Fechar posição final se houver
        if self.posicao_atual:
            self._fechar_posicao_mtf(df_periodo.iloc[-1], len(df_periodo)-1, "Fim do período")
        
        # Calcular métricas finais
        self._calcular_metricas()
        
        print(f"\n✅ BACKTEST MTF CONCLUÍDO!")
        print(f"💰 Capital final: ${self.capital_atual:,.2f}")
        print(f"📊 Total de trades: {len(self.trades)}")
        print(f"📈 Retorno: {((self.capital_atual / self.capital_inicial) - 1) * 100:.2f}%")
    
    def _analisar_mtf_candle(self, symbol: str, timestamp: pd.Timestamp, candle_index: int) -> Optional[Dict]:
        """
        Analisa MTF para um candle específico
        
        Args:
            symbol: Par para análise
            timestamp: Timestamp do candle atual
            candle_index: Índice do candle
        
        Returns:
            Dict com análises de todos os timeframes
        """
        try:
            analises_mtf = {}
            
            for tf in self.timeframes_analise:
                if tf not in self.dados_mtf:
                    continue
                
                df_tf = self.dados_mtf[tf]
                
                # Encontrar dados até o timestamp atual
                df_ate_agora = df_tf[df_tf.index <= timestamp]
                
                if len(df_ate_agora) < 50:  # Mínimo para indicadores
                    continue
                
                # Executar análise SNE para este timeframe
                analise_tf = self._executar_analise_sne_tf(df_ate_agora, symbol, tf)
                
                if analise_tf:
                    analises_mtf[tf] = analise_tf
            
            return analises_mtf
            
        except Exception as e:
            print(f"❌ Erro na análise MTF: {e}")
            return None
    
    def _executar_analise_sne_tf(self, dados: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Dict]:
        """
        Executa análise SNE para um timeframe específico
        
        Args:
            dados: DataFrame com dados históricos
            symbol: Par para análise
            timeframe: Timeframe da análise
        
        Returns:
            Dict com análise do SNE
        """
        try:
            # Usar análise simplificada por enquanto (otimização)
            analise = {
                'timeframe': timeframe,
                'indicadores': self._calcular_indicadores_tf(dados),
                'estrutura': self._analisar_estrutura_tf(dados),
                'contexto': self._analisar_contexto_tf(dados),
                'confluencia': self._calcular_confluencia_tf(dados),
                'sintese': self._gerar_sintese_tf(dados)
            }
            
            return analise
            
        except Exception as e:
            print(f"❌ Erro na análise {timeframe}: {e}")
            return None
    
    def _calcular_indicadores_tf(self, dados: pd.DataFrame) -> Dict:
        """Calcula indicadores técnicos para um timeframe"""
        try:
            # Médias móveis
            ema8 = dados['close'].ewm(span=8).mean()
            ema21 = dados['close'].ewm(span=21).mean()
            sma200 = dados['close'].rolling(200).mean()
            
            # RSI
            delta = dados['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            macd_line = ema8 - ema21
            macd_signal = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - macd_signal
            
            # ATR
            high_low = dados['high'] - dados['low']
            high_close = np.abs(dados['high'] - dados['close'].shift())
            low_close = np.abs(dados['low'] - dados['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(14).mean()
            
            # Volume médio
            volume_medio = dados['volume'].rolling(20).mean()
            
            return {
                'ema8': ema8.iloc[-1] if not ema8.empty else 0,
                'ema21': ema21.iloc[-1] if not ema21.empty else 0,
                'sma200': sma200.iloc[-1] if not sma200.empty else 0,
                'rsi': rsi.iloc[-1] if not rsi.empty else 50,
                'macd': macd_line.iloc[-1] if not macd_line.empty else 0,
                'macd_signal': macd_signal.iloc[-1] if not macd_signal.empty else 0,
                'macd_histogram': macd_histogram.iloc[-1] if not macd_histogram.empty else 0,
                'atr': atr.iloc[-1] if not atr.empty else 0,
                'volume_medio': volume_medio.iloc[-1] if not volume_medio.empty else 0,
                'preco_atual': dados['close'].iloc[-1]
            }
            
        except Exception as e:
            print(f"❌ Erro no cálculo de indicadores: {e}")
            return {}
    
    def _analisar_estrutura_tf(self, dados: pd.DataFrame) -> Dict:
        """Analisa estrutura de mercado para um timeframe"""
        try:
            preco_atual = dados['close'].iloc[-1]
            
            # Suportes e resistências simples
            highs = dados['high'].rolling(20).max()
            lows = dados['low'].rolling(20).min()
            
            resistencia = highs.iloc[-1] if not highs.empty else preco_atual * 1.02
            suporte = lows.iloc[-1] if not lows.empty else preco_atual * 0.98
            
            # Estado do mercado
            if preco_atual > resistencia * 0.998:
                estado = "IMPULSO"
            elif preco_atual < suporte * 1.002:
                estado = "IMPULSO"
            else:
                estado = "LATERAL"
            
            return {
                'resistencia': resistencia,
                'suporte': suporte,
                'estado': estado,
                'range_pct': ((resistencia - suporte) / preco_atual) * 100
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de estrutura: {e}")
            return {}
    
    def _analisar_contexto_tf(self, dados: pd.DataFrame) -> Dict:
        """Analisa contexto de mercado para um timeframe"""
        try:
            # Volatilidade
            returns = dados['close'].pct_change()
            volatilidade = returns.std() * 100
            
            # Volume
            volume_atual = dados['volume'].iloc[-1]
            volume_medio = dados['volume'].rolling(20).mean().iloc[-1]
            volume_ratio = volume_atual / volume_medio if volume_medio > 0 else 1
            
            # Regime de mercado
            if volatilidade > 3:
                regime = "ALTA_VOLATILIDADE"
            elif volatilidade < 1:
                regime = "BAIXA_VOLATILIDADE"
            else:
                regime = "VOLATILIDADE_NORMAL"
            
            return {
                'volatilidade': volatilidade,
                'volume_ratio': volume_ratio,
                'regime': regime,
                'score_oportunidade': min(10, max(0, (volatilidade * volume_ratio) / 2))
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de contexto: {e}")
            return {}
    
    def _calcular_confluencia_tf(self, dados: pd.DataFrame) -> Dict:
        """Calcula confluência para um timeframe"""
        try:
            indicadores = self._calcular_indicadores_tf(dados)
            estrutura = self._analisar_estrutura_tf(dados)
            contexto = self._analisar_contexto_tf(dados)
            
            # Score de direção
            score_direcao = 0
            
            # RSI
            if indicadores['rsi'] > 70:
                score_direcao -= 2
            elif indicadores['rsi'] < 30:
                score_direcao += 2
            elif indicadores['rsi'] > 50:
                score_direcao += 1
            else:
                score_direcao -= 1
            
            # MACD
            if indicadores['macd'] > indicadores['macd_signal']:
                score_direcao += 1
            else:
                score_direcao -= 1
            
            # EMA alignment
            if indicadores['ema8'] > indicadores['ema21'] > indicadores['sma200']:
                score_direcao += 2
            elif indicadores['ema8'] < indicadores['ema21'] < indicadores['sma200']:
                score_direcao -= 2
            
            # Normalizar score
            score_normalizado = (score_direcao + 5) / 10  # 0-1
            
            # Confiança baseada na força do sinal
            confianca = min(100, max(0, abs(score_direcao) * 15 + contexto['score_oportunidade'] * 5))
            
            return {
                'score_direcao': score_normalizado,
                'confianca': confianca,
                'forca_sinal': abs(score_direcao),
                'confluencia_total': score_normalizado * confianca / 100
            }
            
        except Exception as e:
            print(f"❌ Erro no cálculo de confluência: {e}")
            return {}
    
    def _gerar_sintese_tf(self, dados: pd.DataFrame) -> Dict:
        """Gera síntese para um timeframe"""
        try:
            confluencia = self._calcular_confluencia_tf(dados)
            contexto = self._analisar_contexto_tf(dados)
            
            # Decisão baseada no score
            if confluencia['score_direcao'] > 0.6:
                acao = "LONG"
                score = confluencia['score_direcao'] * 10
            elif confluencia['score_direcao'] < 0.4:
                acao = "SHORT"
                score = (1 - confluencia['score_direcao']) * 10
            else:
                acao = "AGUARDAR"
                score = 5
            
            return {
                'acao': acao,
                'score': score,
                'confianca': confluencia['confianca'],
                'justificativa': f"Score: {score:.1f}, Confiança: {confluencia['confianca']:.1f}%"
            }
            
        except Exception as e:
            print(f"❌ Erro na geração de síntese: {e}")
            return {}
    
    def _detectar_sinais_mtf(self, analise_mtf: Dict) -> List[Dict]:
        """
        Detecta sinais em todos os timeframes
        
        Args:
            analise_mtf: Dict com análises de todos os timeframes
        
        Returns:
            Lista de sinais detectados
        """
        sinais = []
        
        for tf, analise in analise_mtf.items():
            sintese = analise.get('sintese', {})
            
            if sintese.get('acao') in ['LONG', 'SHORT'] and sintese.get('confianca', 0) >= self.confianca_minima:
                sinais.append({
                    'timeframe': tf,
                    'direcao': sintese['acao'],
                    'confianca': sintese['confianca'],
                    'score': sintese['score'],
                    'timestamp': pd.Timestamp.now()
                })
        
        return sinais
    
    def _validar_confluencia_mtf(self, sinais: List[Dict]) -> Tuple[str, Optional[Dict]]:
        """
        Valida confluência MTF
        
        Args:
            sinais: Lista de sinais detectados
        
        Returns:
            Tuple (acao, sinal_principal)
        """
        if not sinais:
            return 'AGUARDAR', None
        
        # Agrupar sinais por direção
        sinais_alta = [s for s in sinais if s['direcao'] == 'LONG']
        sinais_baixa = [s for s in sinais if s['direcao'] == 'SHORT']
        
        # Verificar confluência
        if len(sinais_alta) >= self.min_timeframes_confluencia:
            # Escolher sinal com maior confiança
            sinal_principal = max(sinais_alta, key=lambda x: x['confianca'])
            return 'LONG', sinal_principal
        elif len(sinais_baixa) >= self.min_timeframes_confluencia:
            # Escolher sinal com maior confiança
            sinal_principal = max(sinais_baixa, key=lambda x: x['confianca'])
            return 'SHORT', sinal_principal
        else:
            return 'AGUARDAR', None
    
    def _gerenciar_posicao_mtf(self, analise_mtf: Dict) -> str:
        """
        Gerencia posição atual baseada na confluência MTF
        
        Args:
            analise_mtf: Análise MTF atual
        
        Returns:
            'MANTER' ou 'FECHAR'
        """
        if not self.posicao_atual:
            return 'AGUARDAR'
        
        # Verificar se o sinal original ainda é válido
        sinal_origem = self.posicao_atual.get('sinal_origem', {})
        tf_origem = sinal_origem.get('timeframe', '1h')
        
        if tf_origem in analise_mtf:
            analise_origem = analise_mtf[tf_origem]
            sintese_origem = analise_origem.get('sintese', {})
            
            # Se o sinal original perdeu força significativamente
            if sintese_origem.get('acao') != sinal_origem.get('direcao'):
                return 'FECHAR'
            
            # Se a confiança caiu muito
            if sintese_origem.get('confianca', 0) < self.confianca_minima * 0.7:
                return 'FECHAR'
        
        return 'MANTER'
    
    def _abrir_posicao_mtf(self, acao: str, sinal_principal: Dict, candle: pd.Series, candle_index: int):
        """
        Abre posição baseada em sinal MTF
        
        Args:
            acao: 'LONG' ou 'SHORT'
            sinal_principal: Sinal principal que gerou a entrada
            candle: Candle atual
            candle_index: Índice do candle
        """
        try:
            preco_entrada = candle['close']
            
            # Calcular tamanho da posição
            tamanho_posicao = self.capital_atual * 0.95  # Usar 95% do capital
            
            # Calcular stop loss e take profit
            if acao == 'LONG':
                stop_loss = preco_entrada * (1 - self.stop_loss_pct)
                take_profit = preco_entrada * (1 + self.take_profit_pct)
            else:  # SHORT
                stop_loss = preco_entrada * (1 + self.stop_loss_pct)
                take_profit = preco_entrada * (1 - self.take_profit_pct)
            
            # Criar posição
            self.posicao_atual = {
                'acao': acao,
                'preco_entrada': preco_entrada,
                'tamanho': tamanho_posicao,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'candle_entrada': candle_index,
                'timestamp_entrada': candle.name,
                'sinal_origem': sinal_principal
            }
            
            # Adicionar ao histórico de trades
            trade = {
                'acao': acao,
                'preco_entrada': preco_entrada,
                'timestamp_entrada': candle.name,
                'candle_entrada': candle_index,
                'confianca_entrada': sinal_principal['confianca'],
                'score_entrada': sinal_principal['score'],
                'timeframe_origem': sinal_principal['timeframe']
            }
            
            self.trades.append(trade)
            
            print(f"📈 {acao} aberto em ${preco_entrada:,.2f} (Confiança: {sinal_principal['confianca']:.1f}%, TF: {sinal_principal['timeframe']})")
            
        except Exception as e:
            print(f"❌ Erro ao abrir posição: {e}")
    
    def _fechar_posicao_mtf(self, candle: pd.Series, candle_index: int, motivo: str):
        """
        Fecha posição atual
        
        Args:
            candle: Candle atual
            candle_index: Índice do candle
            motivo: Motivo do fechamento
        """
        if not self.posicao_atual:
            return
        
        try:
            preco_saida = candle['close']
            acao = self.posicao_atual['acao']
            preco_entrada = self.posicao_atual['preco_entrada']
            tamanho = self.posicao_atual['tamanho']
            
            # Calcular resultado
            if acao == 'LONG':
                resultado_pct = (preco_saida - preco_entrada) / preco_entrada
            else:  # SHORT
                resultado_pct = (preco_entrada - preco_saida) / preco_entrada
            
            # Aplicar comissão
            resultado_pct -= self.comissao_pct * 2  # Entrada + saída
            
            # Calcular lucro/prejuízo
            resultado_valor = tamanho * resultado_pct
            
            # Atualizar capital
            self.capital_atual += resultado_valor
            
            # Atualizar trade
            trade_atual = self.trades[-1]
            trade_atual.update({
                'preco_saida': preco_saida,
                'timestamp_saida': candle.name,
                'candle_saida': candle_index,
                'resultado_pct': resultado_pct,
                'resultado_valor': resultado_valor,
                'motivo_saida': motivo
            })
            
            # Adicionar à curva de equity
            self.equity_curve.append({
                'timestamp': candle.name,
                'capital': self.capital_atual,
                'trade_id': len(self.trades) - 1
            })
            
            print(f"📉 Posição fechada em ${preco_saida:,.2f} - {motivo} - {resultado_pct:+.2%}")
            
            # Limpar posição
            self.posicao_atual = None
            
        except Exception as e:
            print(f"❌ Erro ao fechar posição: {e}")
    
    def _atualizar_posicao_mtf(self, candle: pd.Series, candle_index: int):
        """
        Atualiza posição atual (stop loss / take profit)
        
        Args:
            candle: Candle atual
            candle_index: Índice do candle
        """
        if not self.posicao_atual:
            return
        
        try:
            preco_atual = candle['close']
            acao = self.posicao_atual['acao']
            stop_loss = self.posicao_atual['stop_loss']
            take_profit = self.posicao_atual['take_profit']
            
            # Verificar stop loss / take profit
            if acao == 'LONG':
                if preco_atual <= stop_loss:
                    self._fechar_posicao_mtf(candle, candle_index, "Stop Loss")
                elif preco_atual >= take_profit:
                    self._fechar_posicao_mtf(candle, candle_index, "Take Profit")
            else:  # SHORT
                if preco_atual >= stop_loss:
                    self._fechar_posicao_mtf(candle, candle_index, "Stop Loss")
                elif preco_atual <= take_profit:
                    self._fechar_posicao_mtf(candle, candle_index, "Take Profit")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar posição: {e}")
    
    def _calcular_metricas(self):
        """Calcula métricas finais do backtest"""
        try:
            if not self.trades:
                print("❌ Nenhum trade executado")
                return
            
            # Filtrar trades completos
            trades_completos = [t for t in self.trades if 'preco_saida' in t]
            
            if not trades_completos:
                print("❌ Nenhum trade completo")
                return
            
            # Métricas básicas
            total_trades = len(trades_completos)
            trades_lucrativos = len([t for t in trades_completos if t['resultado_pct'] > 0])
            trades_prejuizo = total_trades - trades_lucrativos
            
            win_rate = (trades_lucrativos / total_trades) * 100
            
            # Retorno total
            retorno_total = ((self.capital_atual / self.capital_inicial) - 1) * 100
            
            # Profit factor
            lucro_total = sum([t['resultado_valor'] for t in trades_completos if t['resultado_valor'] > 0])
            prejuizo_total = abs(sum([t['resultado_valor'] for t in trades_completos if t['resultado_valor'] < 0]))
            
            profit_factor = lucro_total / prejuizo_total if prejuizo_total > 0 else float('inf')
            
            # Volatilidade e Sharpe
            retornos = [t['resultado_pct'] for t in trades_completos]
            volatilidade = np.std(retornos) * 100
            retorno_medio = np.mean(retornos) * 100
            sharpe_ratio = retorno_medio / volatilidade if volatilidade > 0 else 0
            
            # Max drawdown
            equity_values = [e['capital'] for e in self.equity_curve]
            max_drawdown = self._calcular_max_drawdown(equity_values)
            
            # Salvar métricas
            self.metricas = {
                'capital_inicial': self.capital_inicial,
                'capital_final': self.capital_atual,
                'retorno_total': retorno_total,
                'total_trades': total_trades,
                'trades_lucrativos': trades_lucrativos,
                'trades_prejuizo': trades_prejuizo,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'volatilidade': volatilidade,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            }
            
            # Exibir relatório
            self._exibir_relatorio()
            
        except Exception as e:
            print(f"❌ Erro no cálculo de métricas: {e}")
    
    def _calcular_max_drawdown(self, equity_values: List[float]) -> float:
        """Calcula máximo drawdown"""
        try:
            peak = equity_values[0]
            max_dd = 0
            
            for value in equity_values:
                if value > peak:
                    peak = value
                dd = (peak - value) / peak * 100
                if dd > max_dd:
                    max_dd = dd
            
            return max_dd
            
        except Exception as e:
            print(f"❌ Erro no cálculo de drawdown: {e}")
            return 0
    
    def _exibir_relatorio(self):
        """Exibe relatório final do backtest"""
        try:
            m = self.metricas
            
            print(f"\n📊 RELATÓRIO DE BACKTEST SNE RADAR MTF")
            print("=" * 50)
            print(f"\n💰 PERFORMANCE FINANCEIRA:")
            print(f"   Capital Inicial: ${m['capital_inicial']:,.2f}")
            print(f"   Capital Final: ${m['capital_final']:,.2f}")
            print(f"   Retorno Total: {m['retorno_total']:+.2f}%")
            print(f"   Retorno Médio por Trade: {m['retorno_total']/m['total_trades']:+.2f}%")
            
            print(f"\n📈 MÉTRICAS DE TRADING:")
            print(f"   Total de Trades: {m['total_trades']}")
            print(f"   Trades Lucrativos: {m['trades_lucrativos']}")
            print(f"   Trades com Prejuízo: {m['trades_prejuizo']}")
            print(f"   Win Rate: {m['win_rate']:.1f}%")
            print(f"   Profit Factor: {m['profit_factor']:.2f}")
            
            print(f"\n⚠️ MÉTRICAS DE RISCO:")
            print(f"   Volatilidade (Std): {m['volatilidade']:.2f}%")
            print(f"   Sharpe Ratio: {m['sharpe_ratio']:.2f}")
            print(f"   Max Drawdown: {m['max_drawdown']:.2f}%")
            
            # Avaliação
            print(f"\n🎯 AVALIAÇÃO:")
            if m['retorno_total'] > 0:
                print("   ✅ ESTRATÉGIA LUCRATIVA")
            else:
                print("   ❌ ESTRATÉGIA COM PREJUÍZO")
            
            if m['win_rate'] >= 50:
                print("   ✅ WIN RATE ADEQUADO")
            else:
                print("   ❌ WIN RATE BAIXO")
            
            if m['max_drawdown'] <= 15:
                print("   ✅ RISCO CONTROLADO")
            else:
                print("   ⚠️ RISCO ELEVADO")
            
        except Exception as e:
            print(f"❌ Erro na exibição do relatório: {e}")
    
    def salvar_resultados(self, filename: str):
        """Salva resultados do backtest"""
        try:
            resultados = {
                'metricas': self.metricas,
                'trades': self.trades,
                'equity_curve': self.equity_curve,
                'configuracoes': {
                    'capital_inicial': self.capital_inicial,
                    'comissao_pct': self.comissao_pct,
                    'stop_loss_pct': self.stop_loss_pct,
                    'take_profit_pct': self.take_profit_pct,
                    'confianca_minima': self.confianca_minima,
                    'score_minimo_long': self.score_minimo_long,
                    'score_maximo_short': self.score_maximo_short,
                    'min_timeframes_confluencia': self.min_timeframes_confluencia
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(resultados, f, indent=2, default=str)
            
            print(f"💾 Resultados salvos em: {filename}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")

def executar_backtest_mtf_rapido():
    """Executa backtest MTF rápido para teste"""
    print("⚡ BACKTEST MTF RÁPIDO - BTC 6 MESES")
    print("-" * 40)
    print("📊 Par: BTCUSDT")
    print("⏰ Timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d")
    print("📅 Período: 2025-04-18 até 2025-10-15")
    print("💰 Capital: $10,000")
    
    resposta = input("\n🚀 Executar backtest MTF rápido? (s/n): ").lower().strip()
    
    if resposta != 's':
        print("❌ Backtest cancelado")
        return
    
    print("\n🚀 Executando backtest MTF rápido...")
    
    try:
        # Coletar dados MTF
        coletor = ColetorDadosHistoricosMTF()
        timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
        
        print("📊 Coletando dados MTF...")
        dados_mtf = coletor.coletar_dados_mtf('BTCUSDT', timeframes, '2025-04-18', '2025-10-15')
        
        if not dados_mtf:
            print("❌ Falha ao coletar dados MTF")
            return
        
        # Salvar dados MTF
        os.makedirs('backtest_data_mtf', exist_ok=True)
        for tf, df in dados_mtf.items():
            filename = f"backtest_data_mtf/BTCUSDT_{tf}_historico.csv"
            df.to_csv(filename)
            print(f"💾 Dados salvos: {filename}")
        
        # Executar backtest MTF
        backtest = BacktestSNEMTF(capital_inicial=10000.0)
        backtest.carregar_dados_mtf(dados_mtf)
        backtest.executar_backtest_mtf('BTCUSDT', '2025-04-18', '2025-10-15')
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_results_mtf_BTCUSDT_{timestamp}.json"
        backtest.salvar_resultados(filename)
        
        print(f"\n✅ Backtest MTF rápido concluído!")
        print(f"📊 Gerando visualizações...")
        
        # Gerar visualizações
        try:
            from visualizacao_backtest import VisualizadorBacktest
            visualizador = VisualizadorBacktest()
            visualizador.carregar_resultados(filename)
            visualizador.gerar_todos_graficos('BTCUSDT')
            print("✅ Visualização completa gerada!")
        except Exception as e:
            print(f"⚠️ Erro na visualização: {e}")
        
    except Exception as e:
        print(f"❌ Erro no backtest MTF: {e}")

if __name__ == "__main__":
    executar_backtest_mtf_rapido()


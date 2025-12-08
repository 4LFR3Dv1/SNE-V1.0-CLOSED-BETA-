#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMPO MAGNÉTICO SNE - SISTEMA DE MAPEAMENTO ENERGÉTICO
Transforma análise técnica em mapa de campo magnético visual
Baseado na teoria de campos de liquidez e fluxo energético
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata, RBFInterpolator
from scipy.ndimage import gaussian_filter
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import json


class CampoMagneticoSNE:
    """
    Sistema de Campos Magnéticos para análise de mercado
    
    Converte dados de mercado em mapa de campo magnético onde:
    - Polos magnéticos = zonas de liquidez (equal highs/lows, order blocks)
    - Linhas de campo = fluxo dinâmico entre polos
    - Vetores de força = movimento do preço
    - Densidade = concentração de liquidez
    """
    
    def __init__(self):
        """Inicializa o sistema de campos magnéticos"""
        self.config = {
            'resolucao_campo': 100,  # Resolução da grade de campo
            'raio_influencia': 0.02,  # Raio de influência dos polos (2%)
            'intensidade_base': 1.0,  # Intensidade base do campo
            'decay_exponencial': 2.0,  # Decaimento exponencial da força
            'threshold_liquidez': 0.001,  # Threshold mínimo de liquidez
        }
        
        # Cores do campo magnético
        self.cores_campo = {
            'fundo': '#0a0a0a',
            'polo_atrativo': '#0066ff',  # Azul - liquidez de compra
            'polo_repulsivo': '#ff3300',  # Vermelho - liquidez de venda
            'linha_campo': '#ffffff',
            'vetor_forca': '#ffff00',
            'equalizacao': '#ffffff',
            'nucleo': '#ff00ff'
        }
        
        # Cache de dados
        self.cache_dados = {}
        self.cache_campos = {}
        
    def coletar_dados_campo(self, symbol: str, timeframe: str = '1h', limit: int = 500) -> Dict[str, Any]:
        """
        Coleta dados necessários para gerar o campo magnético
        
        Args:
            symbol: Par a analisar
            timeframe: Timeframe dos dados
            limit: Número de candles
            
        Returns:
            Dict com dados de mercado processados
        """
        try:
            print(f"🧲 Coletando dados de campo magnético para {symbol} ({timeframe})...")
            
            # 1. Dados de candles (fluxo)
            df_candles = self._obter_dados_candles(symbol, timeframe, limit)
            
            # 2. Dados de profundidade (liquidez)
            df_depth = self._obter_dados_profundidade(symbol)
            
            # 3. Identificar polos magnéticos
            polos = self._identificar_polos_magneticos(df_candles)
            
            # 4. Calcular fluxo dinâmico
            fluxo = self._calcular_fluxo_dinamico(df_candles)
            
            # 5. Detectar equalizações
            equalizacoes = self._detectar_equalizacoes(df_candles)
            
            dados_campo = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'candles': df_candles,
                'profundidade': df_depth,
                'polos': polos,
                'fluxo': fluxo,
                'equalizacoes': equalizacoes,
                'preco_atual': df_candles['close'].iloc[-1] if not df_candles.empty else 0
            }
            
            # Cache dos dados
            cache_key = f"{symbol}_{timeframe}_{limit}"
            self.cache_dados[cache_key] = dados_campo
            
            print(f"✅ Dados coletados: {len(df_candles)} candles, {len(polos)} polos")
            return dados_campo
            
        except Exception as e:
            print(f"❌ Erro ao coletar dados de campo: {e}")
            return {}
    
    def calcular_campo_magnetico(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula o campo magnético baseado nos dados coletados
        
        Args:
            dados: Dados de mercado processados
            
        Returns:
            Dict com informações do campo magnético
        """
        try:
            print("🧲 Calculando campo magnético...")
            
            if not dados or 'polos' not in dados:
                return {}
            
            polos = dados['polos']
            preco_atual = dados['preco_atual']
            
            # Criar grade de campo
            preco_min = preco_atual * 0.95
            preco_max = preco_atual * 1.05
            grade_precos = np.linspace(preco_min, preco_max, self.config['resolucao_campo'])
            
            # Calcular densidade de campo para cada ponto
            densidade_campo = np.zeros(self.config['resolucao_campo'])
            vetores_forca = np.zeros(self.config['resolucao_campo'])
            
            for i, preco in enumerate(grade_precos):
                densidade_total = 0
                forca_total = 0
                
                # Calcular influência de cada polo
                for polo in polos:
                    distancia = abs(preco - polo['preco']) / polo['preco']
                    
                    if distancia <= self.config['raio_influencia']:
                        # Campo magnético: F = (Liquidez / Distância²) * Direção
                        intensidade = polo['liquidez'] / (distancia ** self.config['decay_exponencial'])
                        densidade_total += intensidade * polo['direcao']
                        
                        # Vetor de força baseado na direção do polo
                        forca_total += intensidade * polo['direcao']
                
                densidade_campo[i] = densidade_total
                vetores_forca[i] = forca_total
            
            # Normalizar densidade
            if np.max(np.abs(densidade_campo)) > 0:
                densidade_campo = densidade_campo / np.max(np.abs(densidade_campo))
            
            # Calcular linhas de campo
            linhas_campo = self._calcular_linhas_campo(polos, grade_precos)
            
            # Calcular núcleo de equilíbrio
            nucleo = self._calcular_nucleo_equilibrio(densidade_campo, grade_precos)
            
            campo_magnetico = {
                'grade_precos': grade_precos,
                'densidade_campo': densidade_campo,
                'vetores_forca': vetores_forca,
                'linhas_campo': linhas_campo,
                'nucleo': nucleo,
                'polos': polos,
                'intensidade_total': np.sum(np.abs(densidade_campo)),
                'polaridade_dominante': 'ATRATIVA' if np.sum(densidade_campo) > 0 else 'REPULSIVA'
            }
            
            print(f"✅ Campo calculado: {len(polos)} polos, intensidade {campo_magnetico['intensidade_total']:.2f}")
            return campo_magnetico
            
        except Exception as e:
            print(f"❌ Erro ao calcular campo magnético: {e}")
            return {}
    
    def interpretar_campo_simbolico(self, campo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpreta o campo magnético usando lógica simbólica
        
        Args:
            campo: Dados do campo magnético calculado
            
        Returns:
            Dict com interpretação simbólica
        """
        try:
            print("🧠 Interpretando campo magnético...")
            
            if not campo:
                return {}
            
            densidade = campo['densidade_campo']
            nucleo = campo['nucleo']
            polos = campo['polos']
            intensidade_total = campo['intensidade_total']
            
            # Análise de densidade
            densidade_max = np.max(np.abs(densidade))
            densidade_media = np.mean(np.abs(densidade))
            
            # Detectar eventos magnéticos
            eventos = []
            interpretacoes = []
            
            # 1. Análise de compressão
            if densidade_max > 0.8:
                eventos.append("COMPRESSAO_INTENSA")
                interpretacoes.append("Campo magnético em compressão máxima — força latente em formação")
            
            # 2. Análise de expansão
            elif densidade_max < 0.3:
                eventos.append("EXPANSAO")
                interpretacoes.append("Campo magnético em expansão — energia liberada")
            
            # 3. Análise de equalização
            if abs(nucleo['forca']) < 0.1:
                eventos.append("EQUALIZACAO")
                interpretacoes.append("Campo superior equalizado — atração se inverte")
            
            # 4. Análise de polaridade
            if campo['polaridade_dominante'] == 'ATRATIVA':
                eventos.append("ATRACAO_DOMINANTE")
                interpretacoes.append("Polo atrativo dominante — preço sendo puxado para baixo")
            else:
                eventos.append("REPULSAO_DOMINANTE")
                interpretacoes.append("Polo repulsivo dominante — preço sendo empurrado para cima")
            
            # 5. Análise de convergência
            if len(polos) >= 3:
                eventos.append("CONVERGENCIA_POLOS")
                interpretacoes.append("Múltiplos polos convergindo — campo complexo em formação")
            
            # Calcular score de confluência magnética
            score_confluencia = min(10.0, (densidade_max * 5) + (len(polos) * 0.5) + (intensidade_total * 2))
            
            interpretacao = {
                'eventos_detectados': eventos,
                'interpretacoes': interpretacoes,
                'score_confluencia': score_confluencia,
                'densidade_maxima': densidade_max,
                'densidade_media': densidade_media,
                'nucleo_equilibrio': nucleo,
                'polaridade_dominante': campo['polaridade_dominante'],
                'intensidade_total': intensidade_total,
                'recomendacao': self._gerar_recomendacao_magnetica(eventos, score_confluencia)
            }
            
            print(f"✅ Interpretação: {len(eventos)} eventos, score {score_confluencia:.1f}")
            return interpretacao
            
        except Exception as e:
            print(f"❌ Erro na interpretação simbólica: {e}")
            return {}
    
    def _obter_dados_candles(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Obtém dados de candles da Binance"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": timeframe,
                "limit": limit
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Converter tipos
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao obter candles: {e}")
            return pd.DataFrame()
    
    def _obter_dados_profundidade(self, symbol: str) -> Dict[str, Any]:
        """Obtém dados de profundidade (order book)"""
        try:
            url = f"https://api.binance.com/api/v3/depth"
            params = {"symbol": symbol, "limit": 1000}
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return {
                'bids': [[float(price), float(qty)] for price, qty in data['bids']],
                'asks': [[float(price), float(qty)] for price, qty in data['asks']]
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter profundidade: {e}")
            return {'bids': [], 'asks': []}
    
    def _identificar_polos_magneticos(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identifica polos magnéticos (equal highs/lows, order blocks)"""
        polos = []
        
        if df.empty:
            return polos
        
        # 1. Equal Highs (polos repulsivos)
        highs = df['high'].rolling(window=5, center=True).max()
        equal_highs = df[df['high'] == highs]
        
        for idx, row in equal_highs.iterrows():
            polos.append({
                'preco': row['high'],
                'tipo': 'EQUAL_HIGH',
                'direcao': -1,  # Repulsivo
                'liquidez': row['volume'] * 0.8,
                'timestamp': idx,
                'forca': row['volume'] / df['volume'].mean()
            })
        
        # 2. Equal Lows (polos atrativos)
        lows = df['low'].rolling(window=5, center=True).min()
        equal_lows = df[df['low'] == lows]
        
        for idx, row in equal_lows.iterrows():
            polos.append({
                'preco': row['low'],
                'tipo': 'EQUAL_LOW',
                'direcao': 1,  # Atrativo
                'liquidez': row['volume'] * 0.8,
                'timestamp': idx,
                'forca': row['volume'] / df['volume'].mean()
            })
        
        # 3. Order Blocks (zonas de liquidez institucional)
        order_blocks = self._detectar_order_blocks(df)
        polos.extend(order_blocks)
        
        # Filtrar polos por força mínima
        polos = [polo for polo in polos if polo['forca'] > self.config['threshold_liquidez']]
        
        return polos
    
    def _detectar_order_blocks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detecta order blocks (zonas de liquidez institucional)"""
        order_blocks = []
        
        if len(df) < 20:
            return order_blocks
        
        # Detectar candles de alta com volume significativo
        volume_medio = df['volume'].rolling(window=20).mean()
        candles_significativos = df[df['volume'] > volume_medio * 1.5]
        
        for idx, row in candles_significativos.iterrows():
            # Order block de compra (candle de alta com wick baixo)
            if row['close'] > row['open'] and (row['low'] - row['open']) < (row['close'] - row['open']) * 0.3:
                order_blocks.append({
                    'preco': (row['open'] + row['close']) / 2,
                    'tipo': 'ORDER_BLOCK_BUY',
                    'direcao': 1,
                    'liquidez': row['volume'] * 1.2,
                    'timestamp': idx,
                    'forca': row['volume'] / df['volume'].mean()
                })
            
            # Order block de venda (candle de baixa com wick alto)
            elif row['close'] < row['open'] and (row['high'] - row['open']) < (row['open'] - row['close']) * 0.3:
                order_blocks.append({
                    'preco': (row['open'] + row['close']) / 2,
                    'tipo': 'ORDER_BLOCK_SELL',
                    'direcao': -1,
                    'liquidez': row['volume'] * 1.2,
                    'timestamp': idx,
                    'forca': row['volume'] / df['volume'].mean()
                })
        
        return order_blocks
    
    def _calcular_fluxo_dinamico(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula fluxo dinâmico entre polos"""
        if df.empty:
            return {}
        
        # Calcular momentum
        df['momentum'] = df['close'].pct_change()
        df['volume_momentum'] = df['volume'].pct_change()
        
        # Calcular fluxo direcional
        fluxo_positivo = df[df['momentum'] > 0]['volume'].sum()
        fluxo_negativo = df[df['momentum'] < 0]['volume'].sum()
        
        return {
            'fluxo_positivo': fluxo_positivo,
            'fluxo_negativo': fluxo_negativo,
            'fluxo_liquido': fluxo_positivo - fluxo_negativo,
            'ratio_fluxo': fluxo_positivo / fluxo_negativo if fluxo_negativo > 0 else 1.0
        }
    
    def _detectar_equalizacoes(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detecta equalizações (reversões em polos)"""
        equalizacoes = []
        
        if len(df) < 10:
            return equalizacoes
        
        # Detectar reversões significativas
        df['reversao'] = (df['close'] - df['open']) * df['close'].shift(1) - df['open'].shift(1)
        reversoes = df[abs(df['reversao']) > df['close'] * 0.01]
        
        for idx, row in reversoes.iterrows():
            equalizacoes.append({
                'timestamp': idx,
                'preco': row['close'],
                'intensidade': abs(row['reversao']) / df['close'].mean(),
                'tipo': 'REVERSAO_POLO'
            })
        
        return equalizacoes
    
    def _calcular_linhas_campo(self, polos: List[Dict], grade_precos: np.ndarray) -> List[Dict]:
        """Calcula linhas de campo entre polos"""
        linhas = []
        
        if len(polos) < 2:
            return linhas
        
        # Conectar polos opostos
        polos_atrativos = [p for p in polos if p['direcao'] > 0]
        polos_repulsivos = [p for p in polos if p['direcao'] < 0]
        
        for polo_atrativo in polos_atrativos:
            for polo_repulsivo in polos_repulsivos:
                # Criar linha de campo usando interpolação
                linhas.append({
                    'polo_inicio': polo_atrativo,
                    'polo_fim': polo_repulsivo,
                    'intensidade': (polo_atrativo['forca'] + polo_repulsivo['forca']) / 2,
                    'tipo': 'LINHA_CAMPO'
                })
        
        return linhas
    
    def _calcular_nucleo_equilibrio(self, densidade: np.ndarray, grade_precos: np.ndarray) -> Dict[str, Any]:
        """Calcula núcleo de equilíbrio do campo"""
        # Encontrar ponto de menor densidade absoluta
        idx_nucleo = np.argmin(np.abs(densidade))
        
        return {
            'preco': grade_precos[idx_nucleo],
            'densidade': densidade[idx_nucleo],
            'forca': densidade[idx_nucleo],
            'tipo': 'NUCLEO_EQUILIBRIO'
        }
    
    def _gerar_recomendacao_magnetica(self, eventos: List[str], score: float) -> str:
        """Gera recomendação baseada nos eventos magnéticos"""
        if 'COMPRESSAO_INTENSA' in eventos:
            return "AGUARDAR_EXPANSAO"
        elif 'EXPANSAO' in eventos:
            return "MONITORAR_EQUALIZACAO"
        elif 'EQUALIZACAO' in eventos:
            return "AGUARDAR_NOVO_POLO"
        elif score > 7.0:
            return "ALTA_CONFLUENCIA"
        elif score < 3.0:
            return "BAIXA_CONFLUENCIA"
        else:
            return "NEUTRO"


def gerar_campo_magnetico_completo(symbol: str, timeframe: str = '1h') -> Dict[str, Any]:
    """
    Função principal para gerar campo magnético completo
    
    Args:
        symbol: Par a analisar
        timeframe: Timeframe dos dados
        
    Returns:
        Dict com dados completos do campo magnético
    """
    try:
        print(f"🧲 GERANDO CAMPO MAGNÉTICO COMPLETO - {symbol}")
        print("=" * 60)
        
        # Inicializar sistema
        campo_sne = CampoMagneticoSNE()
        
        # 1. Coletar dados
        dados = campo_sne.coletar_dados_campo(symbol, timeframe)
        if not dados:
            return {}
        
        # 2. Calcular campo magnético
        campo = campo_sne.calcular_campo_magnetico(dados)
        if not campo:
            return {}
        
        # 3. Interpretar simbolicamente
        interpretacao = campo_sne.interpretar_campo_simbolico(campo)
        
        # 4. Compilar resultado final
        resultado = {
            'metadata': {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'versao': 'CAMPO_MAGNETICO_v1.0'
            },
            'dados_brutos': dados,
            'campo_magnetico': campo,
            'interpretacao': interpretacao,
            'resumo': {
                'polos_detectados': len(campo.get('polos', [])),
                'intensidade_total': campo.get('intensidade_total', 0),
                'polaridade_dominante': campo.get('polaridade_dominante', 'NEUTRA'),
                'score_confluencia': interpretacao.get('score_confluencia', 0),
                'recomendacao': interpretacao.get('recomendacao', 'NEUTRO')
            }
        }
        
        print("✅ Campo magnético gerado com sucesso!")
        print(f"   📊 Polos: {resultado['resumo']['polos_detectados']}")
        print(f"   🧲 Intensidade: {resultado['resumo']['intensidade_total']:.2f}")
        print(f"   🎯 Score: {resultado['resumo']['score_confluencia']:.1f}")
        print(f"   💡 Recomendação: {resultado['resumo']['recomendacao']}")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro ao gerar campo magnético: {e}")
        import traceback
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    # Teste do sistema de campos magnéticos
    print("🧲 TESTANDO SISTEMA DE CAMPOS MAGNÉTICOS")
    print("=" * 50)
    
    resultado = gerar_campo_magnetico_completo('BTCUSDT', '1h')
    
    if resultado:
        print("\n🎉 SISTEMA FUNCIONANDO!")
        print(f"📊 Resumo: {resultado['resumo']}")
    else:
        print("\n❌ Sistema com problemas")





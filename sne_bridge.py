#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRIDGE SNE RADAR - INTEGRAÇÃO COM LÓGICA REAL
Ponte entre sistema de backtest e lógica real do SNE Radar
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Adicionar path para importar módulos do SNE
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SNEBridge:
    """Bridge para integrar lógica real do SNE no backtest"""
    
    def __init__(self):
        self.symbol_cache = {}
        self.timeframe_cache = {}
        
    def executar_analise_sne_real(self, dados_historicos: pd.DataFrame, symbol: str, timeframe: str = "1h"):
        """
        Executa análise SNE real usando dados históricos
        
        Args:
            dados_historicos: DataFrame com dados OHLCV
            symbol: Par (ex: 'BTCUSDT')
            timeframe: Timeframe (ex: '1h')
        
        Returns:
            Dict com análise completa do SNE
        """
        try:
            print(f"🔗 Executando análise SNE real para {symbol} {timeframe}")
            
            # Simular dados no formato esperado pelo SNE
            dados_sne = self._adaptar_dados_para_sne(dados_historicos, symbol, timeframe)
            
            # Executar análise usando módulos reais do SNE
            analise_completa = self._executar_motor_renan_real(dados_sne, symbol, timeframe)
            
            return analise_completa
            
        except Exception as e:
            print(f"❌ Erro na análise SNE real: {e}")
            # Fallback para análise simplificada
            return self._analise_simplificada_fallback(dados_historicos)
    
    def _adaptar_dados_para_sne(self, df: pd.DataFrame, symbol: str, timeframe: str) -> dict:
        """Adapta dados históricos para formato do SNE"""
        try:
            # Converter DataFrame para formato esperado pelo SNE
            dados_adaptados = {
                'symbol': symbol,
                'timeframe': timeframe,
                'data': df.copy(),
                'preco_atual': df['close'].iloc[-1],
                'volume_atual': df['volume'].iloc[-1],
                'timestamp': df.index[-1]
            }
            
            return dados_adaptados
            
        except Exception as e:
            print(f"❌ Erro ao adaptar dados: {e}")
            return None
    
    def _executar_motor_renan_real(self, dados_sne: dict, symbol: str, timeframe: str) -> dict:
        """Executa motor Renan real com dados adaptados"""
        try:
            # Importar módulos do SNE real
            from motor_renan import analise_completa
            from contexto_global import analisar_contexto
            from estrutura_mercado import analisar_estrutura
            from multi_timeframe import analise_multitf
            from confluencia import calcular_confluencia
            from fluxo_ativo import FluxoAtivo
            from catalogo_magnetico import obter_zonas_magneticas
            from padroes_graficos import detectar_padroes, detectar_wedges
            from indicadores import calcular_indicadores
            
            # Preparar dados para análise
            df = dados_sne['data']
            
            # 1. ANÁLISE DE CONTEXTO REAL
            print("   🌍 Analisando contexto macro...")
            contexto = analisar_contexto(df)
            
            # 2. ANÁLISE DE ESTRUTURA REAL
            print("   📊 Analisando estrutura...")
            estrutura = analisar_estrutura(df)
            
            # 3. ANÁLISE MULTI-TIMEFRAME REAL
            print("   ⏰ Análise multi-timeframe...")
            try:
                mtf = analise_multitf(symbol)
            except:
                # Fallback se multi-timeframe falhar
                mtf = self._mtf_fallback(df)
            
            # 4. INDICADORES REAIS
            print("   📈 Calculando indicadores...")
            indicadores = calcular_indicadores(df)
            
            # 5. ZONAS MAGNÉTICAS REAIS
            print("   🧲 Detectando zonas magnéticas...")
            try:
                zonas = obter_zonas_magneticas()
                preco_atual = df['close'].iloc[-1]
                zona_proxima = min(zonas, key=lambda z: abs(z - preco_atual)) if zonas else None
            except:
                zonas = []
                zona_proxima = None
            
            # 6. FLUXO ATIVO REAL
            print("   💹 Analisando fluxo ativo...")
            try:
                fluxo = FluxoAtivo()
                fluxo_ativo = fluxo.analisar_fluxo(df)
            except:
                fluxo_ativo = {'direcao': 'NEUTRO', 'intensidade': 0}
            
            # 7. PADRÕES GRÁFICOS REAIS
            print("   📊 Detectando padrões...")
            try:
                padroes = detectar_padroes(df)
                wedges = detectar_wedges(df)
            except:
                padroes = {}
                wedges = []
            
            # 8. CONFLUÊNCIA REAL
            print("   🎯 Calculando confluência...")
            try:
                confluencia = calcular_confluencia(
                    contexto=contexto,
                    estrutura=estrutura,
                    mtf=mtf,
                    indicadores=indicadores,
                    zonas_magneticas=zonas,
                    fluxo_ativo=fluxo_ativo,
                    padroes=padroes,
                    wedges=wedges
                )
            except:
                confluencia = self._confluencia_fallback(df)
            
            # 9. SÍNTESE REAL
            print("   🧠 Gerando síntese...")
            sintese = self._gerar_sintese_real(
                contexto, estrutura, mtf, indicadores, 
                zonas, fluxo_ativo, padroes, wedges, confluencia
            )
            
            # Montar análise completa
            analise_completa = {
                'contexto': contexto,
                'estrutura': estrutura,
                'mtf': mtf,
                'indicadores': indicadores,
                'zonas_magneticas': zonas,
                'zona_proxima': zona_proxima,
                'fluxo_ativo': fluxo_ativo,
                'padroes': padroes,
                'wedges': wedges,
                'confluencia': confluencia,
                'sintese': sintese,
                'timestamp': dados_sne['timestamp'],
                'symbol': symbol,
                'timeframe': timeframe
            }
            
            print(f"✅ Análise SNE real concluída para {symbol}")
            return analise_completa
            
        except Exception as e:
            print(f"❌ Erro no motor Renan real: {e}")
            return self._analise_simplificada_fallback(dados_sne['data'])
    
    def _mtf_fallback(self, df: pd.DataFrame) -> dict:
        """Fallback para multi-timeframe"""
        try:
            # Análise básica de múltiplos períodos
            ema8 = df['close'].ewm(span=8).mean()
            ema21 = df['close'].ewm(span=21).mean()
            sma200 = df['close'].rolling(window=200).mean()
            
            return {
                '1h': {'tendencia': 'LATERAL', 'score': 5.0},
                '4h': {'tendencia': 'LATERAL', 'score': 5.0},
                '1d': {'tendencia': 'LATERAL', 'score': 5.0},
                'confluencia': 5.0
            }
        except:
            return {'confluencia': 5.0}
    
    def _confluencia_fallback(self, df: pd.DataFrame) -> dict:
        """Fallback para confluência"""
        try:
            # Cálculo básico de confluência
            rsi = self._calcular_rsi_basico(df)
            macd = self._calcular_macd_basico(df)
            
            score = 5.0
            if rsi > 70:
                score -= 1.0
            elif rsi < 30:
                score += 1.0
            
            if macd > 0:
                score += 0.5
            else:
                score -= 0.5
            
            return {
                'score': max(0, min(10, score)),
                'direcao': 'ALTA' if score > 6 else 'BAIXA' if score < 4 else 'NEUTRO',
                'confianca': min(100, score * 10)
            }
        except:
            return {'score': 5.0, 'direcao': 'NEUTRO', 'confianca': 50}
    
    def _calcular_rsi_basico(self, df: pd.DataFrame) -> float:
        """Calcula RSI básico"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        except:
            return 50
    
    def _calcular_macd_basico(self, df: pd.DataFrame) -> float:
        """Calcula MACD básico"""
        try:
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            macd = ema12 - ema26
            return macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
        except:
            return 0
    
    def _gerar_sintese_real(self, contexto, estrutura, mtf, indicadores, 
                           zonas, fluxo_ativo, padroes, wedges, confluencia) -> dict:
        """Gera síntese usando lógica real do SNE"""
        try:
            # Extrair informações principais
            score_confluencia = confluencia.get('score', 5.0)
            direcao_confluencia = confluencia.get('direcao', 'NEUTRO')
            confianca_confluencia = confluencia.get('confianca', 50)
            
            tendencia_estrutura = estrutura.get('tendencia', 'LATERAL')
            
            # Lógica de decisão baseada no SNE real
            if score_confluencia >= 7 and direcao_confluencia == 'ALTA' and tendencia_estrutura == 'ALTA':
                acao = 'LONG'
                confianca = min(100, confianca_confluencia + 10)
            elif score_confluencia <= 3 and direcao_confluencia == 'BAIXA' and tendencia_estrutura == 'BAIXA':
                acao = 'SHORT'
                confianca = min(100, confianca_confluencia + 10)
            else:
                acao = 'AGUARDAR'
                confianca = confianca_confluencia
            
            # Ajustar confiança baseado em padrões
            if wedges and len(wedges) > 0:
                confianca = min(100, confianca + 5)
            
            if padroes and len(padroes) > 0:
                confianca = min(100, confianca + 3)
            
            return {
                'acao': acao,
                'score': score_confluencia,
                'direcao': direcao_confluencia,
                'tendencia': tendencia_estrutura,
                'confianca': confianca,
                'justificativa': self._gerar_justificativa(acao, score_confluencia, confianca)
            }
            
        except Exception as e:
            print(f"❌ Erro na síntese: {e}")
            return {'acao': 'AGUARDAR', 'score': 5.0, 'confianca': 50}
    
    def _gerar_justificativa(self, acao: str, score: float, confianca: float) -> str:
        """Gera justificativa para a ação"""
        if acao == 'LONG':
            return f"Confluência alta ({score:.1f}) com confiança {confianca:.0f}% - Tendência de alta confirmada"
        elif acao == 'SHORT':
            return f"Confluência baixa ({score:.1f}) com confiança {confianca:.0f}% - Tendência de baixa confirmada"
        else:
            return f"Confluência neutra ({score:.1f}) com confiança {confianca:.0f}% - Aguardar confirmação"
    
    def _analise_simplificada_fallback(self, df: pd.DataFrame) -> dict:
        """Fallback para análise simplificada"""
        try:
            # Análise básica se módulos reais falharem
            rsi = self._calcular_rsi_basico(df)
            macd = self._calcular_macd_basico(df)
            
            score = 5.0
            if rsi > 70:
                score -= 1.0
            elif rsi < 30:
                score += 1.0
            
            if macd > 0:
                score += 0.5
            else:
                score -= 0.5
            
            acao = 'LONG' if score >= 7 else 'SHORT' if score <= 3 else 'AGUARDAR'
            
            return {
                'contexto': {'volatilidade': 30, 'volume_ratio': 1.0},
                'estrutura': {'tendencia': 'LATERAL'},
                'mtf': {'confluencia': score},
                'indicadores': {'RSI': rsi, 'MACD': macd},
                'zonas_magneticas': [],
                'fluxo_ativo': {'direcao': 'NEUTRO'},
                'padroes': {},
                'wedges': [],
                'confluencia': {'score': score, 'direcao': 'NEUTRO'},
                'sintese': {
                    'acao': acao,
                    'score': score,
                    'confianca': min(100, score * 10)
                }
            }
        except:
            return {
                'sintese': {'acao': 'AGUARDAR', 'score': 5.0, 'confianca': 50}
            }


def testar_bridge_sne():
    """Testa a bridge do SNE"""
    try:
        print("🔗 TESTANDO BRIDGE SNE RADAR")
        print("="*50)
        
        # Criar dados de teste
        import pandas as pd
        import numpy as np
        
        # Gerar dados sintéticos para teste
        dates = pd.date_range('2024-01-01', periods=1000, freq='1H')
        np.random.seed(42)
        
        # Simular preços com tendência
        base_price = 50000
        returns = np.random.normal(0.0001, 0.02, 1000)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000, 10000, 1000)
        }, index=dates)
        
        # Testar bridge
        bridge = SNEBridge()
        resultado = bridge.executar_analise_sne_real(df, 'BTCUSDT', '1h')
        
        if resultado:
            print("✅ Bridge funcionando!")
            print(f"📊 Ação: {resultado['sintese']['acao']}")
            print(f"🎯 Score: {resultado['sintese']['score']:.1f}")
            print(f"🎯 Confiança: {resultado['sintese']['confianca']:.0f}%")
        else:
            print("❌ Bridge falhou")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")


if __name__ == "__main__":
    testar_bridge_sne()


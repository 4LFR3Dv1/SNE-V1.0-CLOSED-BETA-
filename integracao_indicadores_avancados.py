#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração dos Indicadores Avançados com o Sistema SNE Radar
Conecta os novos modelos de análise técnica ao sistema principal
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Importar módulos do sistema atual
from indicadores import calcular_indicadores, detectar_padroes_candlestick
from indicadores_avancados import (
    calcular_indicadores_avancados,
    analisar_confluencia_indicadores,
    gerar_sinal_completo
)

# Importar módulos do sistema principal (se disponíveis)
try:
    from contexto_global import analisar_contexto_global
    from estrutura_mercado import analisar_estrutura_mercado
    from multi_timeframe import analisar_multi_timeframe
    from padroes_graficos import analisar_padroes_graficos
    CONTEXTO_AVAILABLE = True
except ImportError:
    CONTEXTO_AVAILABLE = False
    print("⚠️ Módulos de contexto não disponíveis - usando análise básica")

try:
    from confluencia import calcular_confluencia
    CONFLUENCIA_AVAILABLE = True
except ImportError:
    CONFLUENCIA_AVAILABLE = False
    print("⚠️ Módulo de confluência não disponível - usando análise básica")


class SistemaAnaliseAvancada:
    """Sistema integrado de análise técnica avançada"""
    
    def __init__(self):
        self.indicadores_disponiveis = [
            'RSI', 'MACD', 'Bollinger_Bands', 'Stochastic', 'ATR',
            'Williams_R', 'CCI', 'MFI', 'ADX', 'Parabolic_SAR',
            'OBV', 'Volume_Profile', 'Keltner_Channels', 'Donchian_Channels'
        ]
        
        self.padroes_disponiveis = [
            'Candlestick_Basic', 'Head_Shoulders', 'Triangles', 
            'Flags_Pennants', 'Engolfo', 'Doji', 'Martelo'
        ]
    
    def analise_completa_integrada(self, df, symbol="BTCUSDT", timeframe="1h"):
        """
        Análise completa integrada com todos os modelos avançados
        """
        try:
            print(f"🚀 Iniciando análise completa integrada para {symbol} ({timeframe})")
            
            # 1. Calcular indicadores avançados
            df_completo = calcular_indicadores_avancados(df.copy())
            
            # 2. Análise de confluência dos indicadores
            confluencia_indicadores = analisar_confluencia_indicadores(df_completo)
            
            # 3. Análise de contexto global (se disponível)
            contexto_global = None
            if CONTEXTO_AVAILABLE:
                try:
                    contexto_global = analisar_contexto_global(df_completo)
                except Exception as e:
                    print(f"⚠️ Erro na análise de contexto: {e}")
            
            # 4. Análise de estrutura de mercado (se disponível)
            estrutura_mercado = None
            if CONTEXTO_AVAILABLE:
                try:
                    estrutura_mercado = analisar_estrutura_mercado(df_completo)
                except Exception as e:
                    print(f"⚠️ Erro na análise de estrutura: {e}")
            
            # 5. Análise multi-timeframe (se disponível)
            multi_timeframe = None
            if CONTEXTO_AVAILABLE:
                try:
                    multi_timeframe = analisar_multi_timeframe(df_completo)
                except Exception as e:
                    print(f"⚠️ Erro na análise multi-timeframe: {e}")
            
            # 6. Análise de padrões gráficos (se disponível)
            padroes_graficos = None
            if CONTEXTO_AVAILABLE:
                try:
                    padroes_graficos = analisar_padroes_graficos(df_completo)
                except Exception as e:
                    print(f"⚠️ Erro na análise de padrões: {e}")
            
            # 7. Calcular confluência geral (se disponível)
            confluencia_geral = None
            if CONFLUENCIA_AVAILABLE:
                try:
                    confluencia_geral = calcular_confluencia(df_completo)
                except Exception as e:
                    print(f"⚠️ Erro na confluência geral: {e}")
            
            # 8. Gerar sinal completo
            sinal_completo = gerar_sinal_completo(df)
            
            # 9. Compilar resultados
            resultado = {
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": df_completo.index[-1],
                "preco_atual": df_completo['close'].iloc[-1],
                
                # Indicadores e sinais
                "confluencia_indicadores": confluencia_indicadores,
                "sinal_completo": sinal_completo,
                
                # Análises contextuais (se disponíveis)
                "contexto_global": contexto_global,
                "estrutura_mercado": estrutura_mercado,
                "multi_timeframe": multi_timeframe,
                "padroes_graficos": padroes_graficos,
                "confluencia_geral": confluencia_geral,
                
                # Indicadores chave
                "indicadores_chave": self._extrair_indicadores_chave(df_completo),
                
                # Recomendação final
                "recomendacao_final": self._gerar_recomendacao_final(
                    confluencia_indicadores, sinal_completo, confluencia_geral
                ),
                
                # Metadados
                "total_candles": len(df_completo),
                "indicadores_calculados": len(self.indicadores_disponiveis),
                "padroes_detectados": len(self.padroes_disponiveis)
            }
            
            print(f"✅ Análise completa integrada concluída!")
            print(f"🎯 Recomendação: {resultado['recomendacao_final']['sinal']}")
            print(f"🎲 Confiança: {resultado['recomendacao_final']['confianca']:.1%}")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Erro na análise completa integrada: {e}")
            return None
    
    def _extrair_indicadores_chave(self, df):
        """Extrai indicadores chave para análise rápida"""
        try:
            ultimo = df.iloc[-1]
            
            indicadores = {
                # Osciladores
                "RSI": ultimo.get('RSI', 0),
                "Williams_R": ultimo.get('Williams_R', 0),
                "CCI": ultimo.get('CCI', 0),
                "MFI": ultimo.get('MFI', 0),
                "ADX": ultimo.get('ADX', 0),
                
                # Momentum
                "MACD": ultimo.get('MACD', 0),
                "MACD_Signal": ultimo.get('MACD_Signal', 0),
                "MACD_Hist": ultimo.get('MACD_Hist', 0),
                
                # Volatilidade
                "ATR": ultimo.get('ATR', 0),
                "BB_Position": self._calcular_bb_position(ultimo),
                "KC_Position": self._calcular_kc_position(ultimo),
                
                # Volume
                "Volume_Ratio": ultimo.get('volume', 0) / ultimo.get('Volume_MA', 1),
                "OBV": ultimo.get('OBV', 0),
                
                # Tendência
                "EMA8": ultimo.get('EMA8', 0),
                "EMA21": ultimo.get('EMA21', 0),
                "EMA50": ultimo.get('EMA50', 0),
                "PSAR_Trend": ultimo.get('PSAR_Trend', 0),
                
                # Volume Profile
                "Volume_Profile_POC": ultimo.get('Volume_Profile_POC', 0),
                "Volume_Profile_VAL": ultimo.get('Volume_Profile_VAL', 0),
                "Volume_Profile_VAH": ultimo.get('Volume_Profile_VAH', 0)
            }
            
            return indicadores
            
        except Exception as e:
            print(f"❌ Erro ao extrair indicadores chave: {e}")
            return {}
    
    def _calcular_bb_position(self, ultimo):
        """Calcula posição do preço nas Bollinger Bands"""
        try:
            if 'BB_Upper' in ultimo and 'BB_Lower' in ultimo:
                bb_range = ultimo['BB_Upper'] - ultimo['BB_Lower']
                if bb_range > 0:
                    return (ultimo['close'] - ultimo['BB_Lower']) / bb_range
            return 0.5
        except:
            return 0.5
    
    def _calcular_kc_position(self, ultimo):
        """Calcula posição do preço nos Keltner Channels"""
        try:
            if 'KC_Upper' in ultimo and 'KC_Lower' in ultimo:
                kc_range = ultimo['KC_Upper'] - ultimo['KC_Lower']
                if kc_range > 0:
                    return (ultimo['close'] - ultimo['KC_Lower']) / kc_range
            return 0.5
        except:
            return 0.5
    
    def _gerar_recomendacao_final(self, confluencia_indicadores, sinal_completo, confluencia_geral):
        """Gera recomendação final baseada em todas as análises"""
        try:
            # Score base dos indicadores
            score_indicadores = confluencia_indicadores.get('confluencia_score', 0)
            
            # Score do sinal completo
            score_sinal = 0
            if sinal_completo:
                confianca_sinal = sinal_completo.get('confianca', 0)
                sinal = sinal_completo.get('recomendacao', 'NEUTRO')
                
                if sinal == 'COMPRA_FORTE':
                    score_sinal = 8
                elif sinal == 'COMPRA':
                    score_sinal = 5
                elif sinal == 'VENDA_FORTE':
                    score_sinal = -8
                elif sinal == 'VENDA':
                    score_sinal = -5
                else:
                    score_sinal = 0
                
                score_sinal *= confianca_sinal
            
            # Score da confluência geral (se disponível)
            score_confluencia = 0
            if confluencia_geral:
                score_confluencia = confluencia_geral.get('score', 0)
            
            # Calcular score final ponderado
            score_final = (score_indicadores * 0.4 + score_sinal * 0.4 + score_confluencia * 0.2)
            
            # Determinar recomendação
            if score_final >= 6:
                sinal_final = "COMPRA_FORTE"
                confianca_final = min(abs(score_final) / 10, 1.0)
            elif score_final >= 3:
                sinal_final = "COMPRA"
                confianca_final = min(abs(score_final) / 10, 1.0)
            elif score_final <= -6:
                sinal_final = "VENDA_FORTE"
                confianca_final = min(abs(score_final) / 10, 1.0)
            elif score_final <= -3:
                sinal_final = "VENDA"
                confianca_final = min(abs(score_final) / 10, 1.0)
            else:
                sinal_final = "NEUTRO"
                confianca_final = 0.3
            
            return {
                "sinal": sinal_final,
                "confianca": confianca_final,
                "score_final": score_final,
                "score_indicadores": score_indicadores,
                "score_sinal": score_sinal,
                "score_confluencia": score_confluencia
            }
            
        except Exception as e:
            print(f"❌ Erro ao gerar recomendação final: {e}")
            return {
                "sinal": "NEUTRO",
                "confianca": 0.0,
                "score_final": 0,
                "score_indicadores": 0,
                "score_sinal": 0,
                "score_confluencia": 0
            }
    
    def gerar_relatorio_integrado(self, resultado):
        """Gera relatório integrado com todos os resultados"""
        try:
            if not resultado:
                return "❌ Nenhum resultado disponível para relatório"
            
            relatorio = f"""
📊 RELATÓRIO DE ANÁLISE TÉCNICA INTEGRADA
{'='*60}
🎯 Símbolo: {resultado['symbol']} ({resultado['timeframe']})
💰 Preço Atual: ${resultado['preco_atual']:,.2f}
📅 Timestamp: {resultado['timestamp']}

🎯 RECOMENDAÇÃO FINAL:
📈 Sinal: {resultado['recomendacao_final']['sinal']}
🎲 Confiança: {resultado['recomendacao_final']['confianca']:.1%}
📊 Score Final: {resultado['recomendacao_final']['score_final']:.2f}/10

📊 ANÁLISE DE CONFLUÊNCIA:
🎯 Score Indicadores: {resultado['confluencia_indicadores']['confluencia_score']:.2f}/10
📈 Sinal Indicadores: {resultado['confluencia_indicadores']['sinal']}
🔢 Total Indicadores: {resultado['confluencia_indicadores']['total_indicadores']}

📋 Detalhes dos Sinais:
"""
            
            # Adicionar detalhes dos sinais
            for detalhe in resultado['confluencia_indicadores']['detalhes']:
                relatorio += f"  - {detalhe[0]}: {detalhe[1]} (peso: {detalhe[2]})\n"
            
            # Adicionar indicadores chave
            relatorio += f"""
🔑 INDICADORES CHAVE:
📊 RSI: {resultado['indicadores_chave'].get('RSI', 0):.2f}
📈 MACD: {resultado['indicadores_chave'].get('MACD', 0):.2f}
📊 Williams %R: {resultado['indicadores_chave'].get('Williams_R', 0):.2f}
📊 CCI: {resultado['indicadores_chave'].get('CCI', 0):.2f}
📊 MFI: {resultado['indicadores_chave'].get('MFI', 0):.2f}
📊 ADX: {resultado['indicadores_chave'].get('ADX', 0):.2f}
📊 ATR: {resultado['indicadores_chave'].get('ATR', 0):.2f}
📊 Volume Ratio: {resultado['indicadores_chave'].get('Volume_Ratio', 0):.2f}

📈 TENDÊNCIA:
📊 EMA8: ${resultado['indicadores_chave'].get('EMA8', 0):,.2f}
📊 EMA21: ${resultado['indicadores_chave'].get('EMA21', 0):,.2f}
📊 EMA50: ${resultado['indicadores_chave'].get('EMA50', 0):,.2f}
📊 PSAR Trend: {resultado['indicadores_chave'].get('PSAR_Trend', 0)}

📊 VOLUME PROFILE:
📊 POC: ${resultado['indicadores_chave'].get('Volume_Profile_POC', 0):,.2f}
📊 VAL: ${resultado['indicadores_chave'].get('Volume_Profile_VAL', 0):,.2f}
📊 VAH: ${resultado['indicadores_chave'].get('Volume_Profile_VAH', 0):,.2f}
"""
            
            # Adicionar informações do sinal completo
            if resultado['sinal_completo']:
                sinal = resultado['sinal_completo']
                relatorio += f"""
📊 PADRÕES DETECTADOS:
📊 Candlestick: {sinal.get('padroes_candlestick', [])}
📊 Avançados: {sinal.get('padroes_avancados', 'Nenhum')}
"""
            
            relatorio += f"""
📊 METADADOS:
📊 Total Candles: {resultado['total_candles']}
📊 Indicadores Calculados: {resultado['indicadores_calculados']}
📊 Padrões Disponíveis: {resultado['padroes_detectados']}

{'='*60}
✅ Relatório gerado com sucesso!
"""
            
            return relatorio
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório integrado: {e}")
            return f"❌ Erro ao gerar relatório: {e}"


def integrar_com_sistema_principal(df, symbol="BTCUSDT", timeframe="1h"):
    """
    Função principal para integrar com o sistema SNE Radar
    """
    try:
        print(f"🚀 Integrando análise avançada com sistema principal...")
        
        # Criar instância do sistema
        sistema = SistemaAnaliseAvancada()
        
        # Executar análise completa integrada
        resultado = sistema.analise_completa_integrada(df, symbol, timeframe)
        
        if resultado:
            # Gerar relatório
            relatorio = sistema.gerar_relatorio_integrado(resultado)
            
            # Salvar resultado (opcional)
            # with open(f"analise_integrada_{symbol}_{timeframe}.txt", "w") as f:
            #     f.write(relatorio)
            
            return resultado, relatorio
        else:
            return None, "❌ Falha na análise integrada"
            
    except Exception as e:
        print(f"❌ Erro na integração com sistema principal: {e}")
        return None, f"❌ Erro: {e}"


# ============================================================================
# FUNÇÃO DE TESTE DE INTEGRAÇÃO
# ============================================================================

def testar_integracao_completa():
    """Testa a integração completa com dados simulados"""
    print("🧪 Testando integração completa...")
    
    # Criar dados de teste
    np.random.seed(42)
    n_candles = 200
    base_price = 50000
    
    dates = pd.date_range('2024-01-01', periods=n_candles, freq='1H')
    returns = np.random.normal(0.001, 0.02, n_candles)
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    df = pd.DataFrame({
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, n_candles)
    }, index=dates)
    
    # Ajustar high/low
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    print(f"📊 Dados de teste criados: {len(df)} candles")
    
    # Testar integração
    resultado, relatorio = integrar_com_sistema_principal(df, "BTCUSDT", "1h")
    
    if resultado:
        print("\n✅ INTEGRAÇÃO TESTADA COM SUCESSO!")
        print(f"🎯 Recomendação: {resultado['recomendacao_final']['sinal']}")
        print(f"🎲 Confiança: {resultado['recomendacao_final']['confianca']:.1%}")
        
        # Mostrar parte do relatório
        print("\n📋 PARTE DO RELATÓRIO:")
        linhas = relatorio.split('\n')[:20]
        for linha in linhas:
            print(linha)
        print("...")
        
        return True
    else:
        print("❌ Falha no teste de integração")
        return False


if __name__ == "__main__":
    # Executar teste quando executado diretamente
    testar_integracao_completa()











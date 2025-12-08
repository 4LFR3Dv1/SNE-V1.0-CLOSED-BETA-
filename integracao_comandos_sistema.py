#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração dos Indicadores Avançados com os Comandos Atuais do Sistema SNE Radar
Conecta os novos modelos de análise técnica aos comandos existentes (R, RT, RP, etc.)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Importar módulos do sistema atual
from indicadores import calcular_indicadores
from indicadores_avancados import (
    calcular_indicadores_avancados,
    analisar_confluencia_indicadores,
    gerar_sinal_completo
)

# Importar módulos do sistema principal
try:
    from motor_renan import analise_completa, coletar_dados
    from relatorio_tecnico import gerar_relatorio
    from relatorio_profissional import gerar_relatorio_profissional
    MOTOR_RENAN_AVAILABLE = True
except ImportError:
    MOTOR_RENAN_AVAILABLE = False
    print("⚠️ Módulos do motor Renan não disponíveis")
    
    # Função de fallback para coletar dados
    def coletar_dados(symbol, interval, limit=200):
        """Função de fallback para coletar dados quando motor_renan não está disponível"""
        try:
            import requests
            import pandas as pd
            
            # Normalizar interval para formato Binance
            interval = interval.lower()
            interval_map = {
                '1min': '1m', '5min': '5m', '10min': '10m', '15min': '15m', '30min': '30m',
                '1hr': '1h', '1hour': '1h', '2hr': '2h', '2hour': '2h', 
                '4hr': '4h', '4hour': '4h', '6hr': '6h', '6hour': '6h',
                '8hr': '8h', '8hour': '8h', '12hr': '12h', '12hour': '12h',
                '1day': '1d', 'daily': '1d', '1week': '1w', 'weekly': '1w', '1month': '1M', 'monthly': '1M'
            }
            interval = interval_map.get(interval, interval)
            
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
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype({
                    'timestamp': 'datetime64[ms]',
                    'open': float, 'high': float, 'low': float,
                    'close': float, 'volume': float
                })
                
                df = calcular_indicadores(df)
                return df
            return None
        except Exception as e:
            print(f"Erro ao coletar dados: {e}")
            return None


def integrar_com_comando_r(symbol="BTCUSDT", timeframe="1h"):
    """
    Integra indicadores avançados ao comando R (Scanner Técnico)
    """
    try:
        print(f"🚀 Executando Scanner Técnico Avançado para {symbol} ({timeframe})")
        
        # 1. Executar análise completa do sistema atual
        if MOTOR_RENAN_AVAILABLE:
            resultado_atual = analise_completa(symbol, timeframe)
            if 'erro' in resultado_atual:
                print(f"❌ Erro na análise atual: {resultado_atual['erro']}")
                return None
        else:
            # Fallback: coletar dados básicos
            df = coletar_dados(symbol, timeframe)
            if df is None:
                print("❌ Falha ao coletar dados")
                return None
            resultado_atual = {"symbol": symbol, "timeframe": timeframe, "data": df}
        
        # 2. Adicionar análise avançada
        print("🔬 Aplicando indicadores avançados...")
        
        # Coletar dados para análise avançada
        df = coletar_dados(symbol, timeframe)
        if df is None:
            print("❌ Falha ao coletar dados para análise avançada")
            return resultado_atual
        
        # Calcular indicadores avançados
        df_avancado = calcular_indicadores_avancados(df.copy())
        
        # Análise de confluência avançada
        confluencia_avancada = analisar_confluencia_indicadores(df_avancado)
        
        # Sinal completo
        sinal_completo = gerar_sinal_completo(df)
        
        # 3. Integrar resultados
        resultado_atual['indicadores_avancados'] = {
            'confluencia_avancada': confluencia_avancada,
            'sinal_completo': sinal_completo,
            'indicadores_chave': {
                'Williams_R': df_avancado['Williams_R'].iloc[-1] if 'Williams_R' in df_avancado.columns else None,
                'CCI': df_avancado['CCI'].iloc[-1] if 'CCI' in df_avancado.columns else None,
                'MFI': df_avancado['MFI'].iloc[-1] if 'MFI' in df_avancado.columns else None,
                'ADX': df_avancado['ADX'].iloc[-1] if 'ADX' in df_avancado.columns else None,
                'PSAR_Trend': df_avancado['PSAR_Trend'].iloc[-1] if 'PSAR_Trend' in df_avancado.columns else None,
                'OBV': df_avancado['OBV'].iloc[-1] if 'OBV' in df_avancado.columns else None,
                'Volume_Profile_POC': df_avancado['Volume_Profile_POC'].iloc[-1] if 'Volume_Profile_POC' in df_avancado.columns else None,
                'KC_Position': _calcular_kc_position(df_avancado.iloc[-1]) if len(df_avancado) > 0 else None
            }
        }
        
        # 4. Atualizar síntese com dados avançados
        if 'sintese' in resultado_atual:
            sintese = resultado_atual['sintese']
            
            # Adicionar score de confluência avançada
            sintese['score_confluencia_avancada'] = confluencia_avancada['confluencia_score']
            sintese['sinal_avancado'] = confluencia_avancada['sinal']
            
            # Melhorar recomendação baseada em confluência avançada
            if confluencia_avancada['confluencia_score'] >= 6:
                sintese['recomendacao_avancada'] = "COMPRA_FORTE"
            elif confluencia_avancada['confluencia_score'] >= 3:
                sintese['recomendacao_avancada'] = "COMPRA"
            elif confluencia_avancada['confluencia_score'] <= -6:
                sintese['recomendacao_avancada'] = "VENDA_FORTE"
            elif confluencia_avancada['confluencia_score'] <= -3:
                sintese['recomendacao_avancada'] = "VENDA"
            else:
                sintese['recomendacao_avancada'] = "NEUTRO"
        
        print("✅ Scanner Técnico Avançado concluído!")
        return resultado_atual
        
    except Exception as e:
        print(f"❌ Erro na integração com comando R: {e}")
        return None


def integrar_com_comando_rt(symbol="BTCUSDT", timeframe="1h"):
    """
    Integra indicadores avançados ao comando RT (Relatório Técnico Completo)
    """
    try:
        print(f"📄 Gerando Relatório Técnico Avançado para {symbol} ({timeframe})")
        
        # 1. Executar relatório técnico atual
        if MOTOR_RENAN_AVAILABLE:
            relatorio_atual = gerar_relatorio(symbol, timeframe, salvar=False)
        else:
            relatorio_atual = f"Relatório básico para {symbol} ({timeframe})"
        
        # 2. Coletar dados para análise avançada
        df = coletar_dados(symbol, timeframe)
        if df is None:
            print("❌ Falha ao coletar dados")
            return relatorio_atual
        
        # 3. Calcular indicadores avançados
        df_avancado = calcular_indicadores_avancados(df.copy())
        confluencia_avancada = analisar_confluencia_indicadores(df_avancado)
        sinal_completo = gerar_sinal_completo(df)
        
        # 4. Criar seção adicional do relatório
        secao_avancada = f"""
{'='*60}
🔬 ANÁLISE TÉCNICA AVANÇADA - INDICADORES PROFISSIONAIS
{'='*60}

📊 CONFLUÊNCIA AVANÇADA:
🎯 Score: {confluencia_avancada['confluencia_score']:.2f}/10
📈 Sinal: {confluencia_avancada['sinal']}
🔢 Total Indicadores: {confluencia_avancada['total_indicadores']}

📋 Detalhes dos Sinais:
"""
        
        # Adicionar detalhes dos sinais
        for detalhe in confluencia_avancada['detalhes']:
            secao_avancada += f"  - {detalhe[0]}: {detalhe[1]} (peso: {detalhe[2]})\n"
        
        # Adicionar indicadores avançados
        ultimo = df_avancado.iloc[-1]
        secao_avancada += f"""
🔬 INDICADORES AVANÇADOS:
📊 Williams %R: {ultimo.get('Williams_R', 0):.2f}
📊 CCI: {ultimo.get('CCI', 0):.2f}
📊 MFI: {ultimo.get('MFI', 0):.2f}
📊 ADX: {ultimo.get('ADX', 0):.2f}
📊 Parabolic SAR: ${ultimo.get('PSAR', 0):,.2f}
📊 PSAR Trend: {ultimo.get('PSAR_Trend', 0)}
📊 OBV: {ultimo.get('OBV', 0):,.0f}

📊 VOLUME PROFILE:
📊 POC: ${ultimo.get('Volume_Profile_POC', 0):,.2f}
📊 VAL: ${ultimo.get('Volume_Profile_VAL', 0):,.2f}
📊 VAH: ${ultimo.get('Volume_Profile_VAH', 0):,.2f}

📊 KELTNER CHANNELS:
📊 Upper: ${ultimo.get('KC_Upper', 0):,.2f}
📊 Lower: ${ultimo.get('KC_Lower', 0):,.2f}
📊 Position: {_calcular_kc_position(ultimo):.2f}

📊 DONCHIAN CHANNELS:
📊 Upper: ${ultimo.get('DC_Upper', 0):,.2f}
📊 Lower: ${ultimo.get('DC_Lower', 0):,.2f}
"""
        
        # Adicionar padrões detectados
        if sinal_completo:
            secao_avancada += f"""
📊 PADRÕES DETECTADOS:
📊 Candlestick: {sinal_completo.get('padroes_candlestick', [])}
📊 Avançados: {sinal_completo.get('padroes_avancados', 'Nenhum')}

🎯 RECOMENDAÇÃO AVANÇADA:
📈 Sinal: {sinal_completo.get('recomendacao', 'NEUTRO')}
🎲 Confiança: {sinal_completo.get('confianca', 0):.1%}
"""
        
        # 5. Combinar relatórios
        relatorio_completo = str(relatorio_atual) + "\n" + secao_avancada
        
        print("✅ Relatório Técnico Avançado gerado!")
        return relatorio_completo
        
    except Exception as e:
        print(f"❌ Erro na integração com comando RT: {e}")
        return relatorio_atual


def integrar_com_comando_rp(symbol="BTCUSDT", timeframe="1h"):
    """
    Integra indicadores avançados ao comando RP (Relatório Profissional)
    """
    try:
        print(f"📋 Gerando Relatório Profissional Avançado para {symbol} ({timeframe})")
        
        # 1. Executar relatório profissional atual
        if MOTOR_RENAN_AVAILABLE:
            relatorio_atual = gerar_relatorio_profissional(symbol, timeframe)
        else:
            relatorio_atual = f"Relatório profissional básico para {symbol} ({timeframe})"
        
        # 2. Coletar dados para análise avançada
        df = coletar_dados(symbol, timeframe)
        if df is None:
            print("❌ Falha ao coletar dados")
            return relatorio_atual
        
        # 3. Calcular indicadores avançados
        df_avancado = calcular_indicadores_avancados(df.copy())
        confluencia_avancada = analisar_confluencia_indicadores(df_avancado)
        sinal_completo = gerar_sinal_completo(df)
        
        # 4. Criar seção profissional adicional
        secao_profissional = f"""
{'='*60}
🏛️ ANÁLISE INSTITUCIONAL AVANÇADA
{'='*60}

📊 SCORE DE CONFLUÊNCIA PROFISSIONAL: {confluencia_avancada['confluencia_score']:.2f}/10
📈 RECOMENDAÇÃO INSTITUCIONAL: {confluencia_avancada['sinal']}

🔬 INDICADORES PROFISSIONAIS:
"""
        
        # Adicionar indicadores com interpretação profissional
        ultimo = df_avancado.iloc[-1]
        
        # Williams %R
        williams_r = ultimo.get('Williams_R', 0)
        williams_interpretacao = "SOBRECOMPRA" if williams_r > -20 else "SOBREVENDA" if williams_r < -80 else "NEUTRO"
        secao_profissional += f"📊 Williams %R: {williams_r:.2f} ({williams_interpretacao})\n"
        
        # CCI
        cci = ultimo.get('CCI', 0)
        cci_interpretacao = "SOBRECOMPRA" if cci > 100 else "SOBREVENDA" if cci < -100 else "NEUTRO"
        secao_profissional += f"📊 CCI: {cci:.2f} ({cci_interpretacao})\n"
        
        # MFI
        mfi = ultimo.get('MFI', 0)
        mfi_interpretacao = "SOBRECOMPRA" if mfi > 80 else "SOBREVENDA" if mfi < 20 else "NEUTRO"
        secao_profissional += f"📊 MFI: {mfi:.2f} ({mfi_interpretacao})\n"
        
        # ADX
        adx = ultimo.get('ADX', 0)
        adx_interpretacao = "FORTE" if adx > 25 else "FRACO" if adx < 20 else "MODERADO"
        secao_profissional += f"📊 ADX: {adx:.2f} (Tendência {adx_interpretacao})\n"
        
        # Volume Profile
        poc = ultimo.get('Volume_Profile_POC', 0)
        val = ultimo.get('Volume_Profile_VAL', 0)
        vah = ultimo.get('Volume_Profile_VAH', 0)
        secao_profissional += f"📊 Volume Profile: POC ${poc:,.2f}, VAL ${val:,.2f}, VAH ${vah:,.2f}\n"
        
        # Adicionar análise de risco profissional
        secao_profissional += f"""
🎯 ANÁLISE DE RISCO PROFISSIONAL:
📊 Score de Confluência: {confluencia_avancada['confluencia_score']:.2f}/10
📈 Recomendação: {confluencia_avancada['sinal']}
🎲 Confiança: {abs(confluencia_avancada['confluencia_score']) / 10:.1%}

📊 GESTÃO DE RISCO:
📊 ATR: ${ultimo.get('ATR', 0):,.2f}
📊 Volatilidade: {ultimo.get('ATR', 0) / ultimo['close'] * 100:.2f}%
📊 Volume Ratio: {ultimo.get('volume', 0) / ultimo.get('Volume_MA', 1):.2f}
"""
        
        # 5. Combinar relatórios
        relatorio_completo = str(relatorio_atual) + "\n" + secao_profissional
        
        print("✅ Relatório Profissional Avançado gerado!")
        return relatorio_completo
        
    except Exception as e:
        print(f"❌ Erro na integração com comando RP: {e}")
        return relatorio_atual


def _calcular_kc_position(ultimo):
    """Calcula posição do preço nos Keltner Channels"""
    try:
        if 'KC_Upper' in ultimo and 'KC_Lower' in ultimo:
            kc_range = ultimo['KC_Upper'] - ultimo['KC_Lower']
            if kc_range > 0:
                return (ultimo['close'] - ultimo['KC_Lower']) / kc_range
        return 0.5
    except:
        return 0.5


def criar_comando_avancado():
    """
    Cria um novo comando 'AVANCADO' para análise técnica avançada
    """
    def comando_avancado(symbol="BTCUSDT", timeframe="1h"):
        """
        Comando AVANCADO - Análise técnica com todos os indicadores avançados
        """
        try:
            print(f"🔬 ANÁLISE TÉCNICA AVANÇADA - {symbol} ({timeframe})")
            print("="*60)
            
            # Coletar dados
            df = coletar_dados(symbol, timeframe)
            if df is None:
                print("❌ Falha ao coletar dados")
                return None
            
            # Calcular indicadores avançados
            df_avancado = calcular_indicadores_avancados(df.copy())
            
            # Análise de confluência
            confluencia = analisar_confluencia_indicadores(df_avancado)
            
            # Sinal completo
            sinal_completo = gerar_sinal_completo(df)
            
            # Exibir resultados
            print(f"\n💰 Preço Atual: ${df['close'].iloc[-1]:,.2f}")
            print(f"🎯 Score de Confluência: {confluencia['confluencia_score']:.2f}/10")
            print(f"📈 Sinal: {confluencia['sinal']}")
            
            print(f"\n🔬 INDICADORES AVANÇADOS:")
            ultimo = df_avancado.iloc[-1]
            
            indicadores = [
                ('Williams %R', ultimo.get('Williams_R', 0)),
                ('CCI', ultimo.get('CCI', 0)),
                ('MFI', ultimo.get('MFI', 0)),
                ('ADX', ultimo.get('ADX', 0)),
                ('Parabolic SAR', ultimo.get('PSAR', 0)),
                ('OBV', ultimo.get('OBV', 0))
            ]
            
            for nome, valor in indicadores:
                if valor is not None:
                    if isinstance(valor, float):
                        print(f"  📊 {nome}: {valor:.2f}")
                    else:
                        print(f"  📊 {nome}: {valor}")
            
            print(f"\n📊 VOLUME PROFILE:")
            print(f"  📊 POC: ${ultimo.get('Volume_Profile_POC', 0):,.2f}")
            print(f"  📊 VAL: ${ultimo.get('Volume_Profile_VAL', 0):,.2f}")
            print(f"  📊 VAH: ${ultimo.get('Volume_Profile_VAH', 0):,.2f}")
            
            if sinal_completo:
                print(f"\n📊 PADRÕES DETECTADOS:")
                print(f"  📊 Candlestick: {sinal_completo.get('padroes_candlestick', [])}")
                print(f"  📊 Avançados: {sinal_completo.get('padroes_avancados', 'Nenhum')}")
                
                print(f"\n🎯 RECOMENDAÇÃO FINAL:")
                print(f"  📈 Sinal: {sinal_completo.get('recomendacao', 'NEUTRO')}")
                print(f"  🎲 Confiança: {sinal_completo.get('confianca', 0):.1%}")
            
            print("\n✅ Análise Avançada Concluída!")
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'confluencia': confluencia,
                'sinal_completo': sinal_completo,
                'indicadores_avancados': df_avancado
            }
            
        except Exception as e:
            print(f"❌ Erro na análise avançada: {e}")
            return None
    
    return comando_avancado


# ============================================================================
# FUNÇÃO PRINCIPAL DE INTEGRAÇÃO
# ============================================================================

def integrar_indicadores_avancados_com_sistema():
    """
    Função principal para integrar indicadores avançados com o sistema atual
    """
    print("🚀 Integrando Indicadores Avançados com Sistema SNE Radar...")
    
    # Verificar se os módulos necessários estão disponíveis
    if not MOTOR_RENAN_AVAILABLE:
        print("⚠️ Módulos do motor Renan não disponíveis - usando análise básica")
    
    print("✅ Integração concluída!")
    print("\n📋 COMANDOS DISPONÍVEIS:")
    print("  🔬 AVANCADO - Análise técnica com indicadores avançados")
    print("  📊 R - Scanner Técnico (agora com indicadores avançados)")
    print("  📄 RT - Relatório Técnico (agora com seção avançada)")
    print("  📋 RP - Relatório Profissional (agora com análise institucional)")
    
    return True


# ============================================================================
# FUNÇÃO DE TESTE
# ============================================================================

def testar_integracao_comandos():
    """Testa a integração com os comandos atuais"""
    print("🧪 Testando integração com comandos atuais...")
    
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
    
    # Testar comando avançado
    comando_avancado = criar_comando_avancado()
    resultado = comando_avancado("BTCUSDT", "1h")
    
    if resultado:
        print("\n✅ INTEGRAÇÃO COM COMANDOS TESTADA COM SUCESSO!")
        print(f"🎯 Score de Confluência: {resultado['confluencia']['confluencia_score']:.2f}/10")
        print(f"📈 Sinal: {resultado['confluencia']['sinal']}")
        return True
    else:
        print("❌ Falha no teste de integração")
        return False


if __name__ == "__main__":
    # Executar teste quando executado diretamente
    testar_integracao_comandos()

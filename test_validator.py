#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Multi-Timeframe Validator - SNE Radar
Demonstração do sistema de validação de sinais
"""

import pandas as pd
import numpy as np
from datetime import datetime
from multi_timeframe_validator import validator, validar_sinal_completo, detectar_divergencias_completo

def criar_dados_teste():
    """Cria dados de teste para demonstração"""
    
    # Dados simulados para diferentes timeframes
    dados_teste = {}
    
    # 1m - Tempo real (dados mais voláteis)
    df_1m = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'EMA8': [100.5, 101.2, 102.1, 103.0, 103.9, 104.8, 105.7, 106.6, 107.5, 108.4],
        'EMA21': [100.0, 100.5, 101.0, 101.5, 102.0, 102.5, 103.0, 103.5, 104.0, 104.5],
        'SMA200': [100.0, 100.1, 100.2, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9],
        'rsi': [55, 58, 62, 65, 68, 70, 72, 74, 76, 78],
        'volume_ratio': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
        'volatilidade': [2.5, 2.8, 3.1, 3.4, 3.7, 4.0, 4.3, 4.6, 4.9, 5.2]
    })
    dados_teste['1m'] = df_1m
    
    # 5m - Curto prazo
    df_5m = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'EMA8': [100.3, 101.0, 101.8, 102.6, 103.4, 104.2, 105.0, 105.8, 106.6, 107.4],
        'EMA21': [100.0, 100.3, 100.6, 100.9, 101.2, 101.5, 101.8, 102.1, 102.4, 102.7],
        'SMA200': [100.0, 100.05, 100.1, 100.15, 100.2, 100.25, 100.3, 100.35, 100.4, 100.45],
        'rsi': [52, 55, 58, 61, 64, 67, 70, 73, 76, 79],
        'volume_ratio': [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45],
        'volatilidade': [2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8]
    })
    dados_teste['5m'] = df_5m
    
    # 15m - Médio prazo
    df_15m = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'EMA8': [100.2, 100.9, 101.6, 102.3, 103.0, 103.7, 104.4, 105.1, 105.8, 106.5],
        'EMA21': [100.0, 100.2, 100.4, 100.6, 100.8, 101.0, 101.2, 101.4, 101.6, 101.8],
        'SMA200': [100.0, 100.02, 100.04, 100.06, 100.08, 100.1, 100.12, 100.14, 100.16, 100.18],
        'rsi': [50, 53, 56, 59, 62, 65, 68, 71, 74, 77],
        'volume_ratio': [1.0, 1.03, 1.06, 1.09, 1.12, 1.15, 1.18, 1.21, 1.24, 1.27],
        'volatilidade': [1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6]
    })
    dados_teste['15m'] = df_15m
    
    # 1h - Médio-longo prazo
    df_1h = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'EMA8': [100.1, 100.7, 101.3, 101.9, 102.5, 103.1, 103.7, 104.3, 104.9, 105.5],
        'EMA21': [100.0, 100.1, 100.2, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9],
        'SMA200': [100.0, 100.01, 100.02, 100.03, 100.04, 100.05, 100.06, 100.07, 100.08, 100.09],
        'rsi': [48, 51, 54, 57, 60, 63, 66, 69, 72, 75],
        'volume_ratio': [1.0, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18],
        'volatilidade': [1.5, 1.7, 1.9, 2.1, 2.3, 2.5, 2.7, 2.9, 3.1, 3.3]
    })
    dados_teste['1h'] = df_1h
    
    # 4h - Longo prazo
    df_4h = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'EMA8': [100.05, 100.6, 101.15, 101.7, 102.25, 102.8, 103.35, 103.9, 104.45, 105.0],
        'EMA21': [100.0, 100.05, 100.1, 100.15, 100.2, 100.25, 100.3, 100.35, 100.4, 100.45],
        'SMA200': [100.0, 100.005, 100.01, 100.015, 100.02, 100.025, 100.03, 100.035, 100.04, 100.045],
        'rsi': [45, 48, 51, 54, 57, 60, 63, 66, 69, 72],
        'volume_ratio': [1.0, 1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09],
        'volatilidade': [1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0]
    })
    dados_teste['4h'] = df_4h
    
    # 1d - Tendência principal
    df_1d = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'EMA8': [100.02, 100.5, 100.98, 101.46, 101.94, 102.42, 102.9, 103.38, 103.86, 104.34],
        'EMA21': [100.0, 100.02, 100.04, 100.06, 100.08, 100.1, 100.12, 100.14, 100.16, 100.18],
        'SMA200': [100.0, 100.001, 100.002, 100.003, 100.004, 100.005, 100.006, 100.007, 100.008, 100.009],
        'rsi': [42, 45, 48, 51, 54, 57, 60, 63, 66, 69],
        'volume_ratio': [1.0, 1.005, 1.01, 1.015, 1.02, 1.025, 1.03, 1.035, 1.04, 1.045],
        'volatilidade': [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8]
    })
    dados_teste['1d'] = df_1d
    
    return dados_teste

def testar_validacao_compra():
    """Testa validação de sinal de compra"""
    print("🟢 TESTANDO VALIDAÇÃO DE SINAL DE COMPRA")
    print("=" * 50)
    
    dados_teste = criar_dados_teste()
    
    # Validar sinal de compra
    validacao = validar_sinal_completo("BTCUSDT", "compra", dados_teste)
    
    print(f"📊 Resultado da Validação:")
    print(f"   Símbolo: {validacao['symbol']}")
    print(f"   Tipo de Sinal: {validacao['sinal_tipo'].upper()}")
    print(f"   Válido: {'✅ SIM' if validacao['valido'] else '❌ NÃO'}")
    print(f"   Confiança: {validacao['confianca']:.1f}%")
    print(f"   Score Final: {validacao['score_final']:.1f}/100")
    print(f"   Recomendação: {validacao['recomendacao']}")
    
    print(f"\n📈 Concordância Multi-Timeframe:")
    concordancia = validacao['concordancia']
    print(f"   Score Bullish: {concordancia['score_bullish']:.1f}")
    print(f"   Score Bearish: {concordancia['score_bearish']:.1f}")
    print(f"   Tendência Dominante: {concordancia['tendencia_dominante'].upper()}")
    print(f"   Força do Sinal: {concordancia['forca_sinal']:.1f}")
    print(f"   Concordância: {concordancia['concordancia']}")
    print(f"   Timeframes Analisados: {concordancia['total_timeframes']}")
    
    print(f"\n✅ Critérios Atendidos ({len(validacao['criterios_atendidos'])}):")
    for criterio in validacao['criterios_atendidos']:
        print(f"   • {criterio}")
    
    print(f"\n❌ Critérios Falhados ({len(validacao['criterios_falhados'])}):")
    for criterio in validacao['criterios_falhados']:
        print(f"   • {criterio}")
    
    print(f"\n🚨 Divergências Detectadas ({len(validacao['divergencias'])}):")
    for i, divergencia in enumerate(validacao['divergencias'], 1):
        print(f"   {i}. {divergencia['tipo']} - {divergencia['severidade']}")
        print(f"      Descrição: {divergencia['descricao']}")
        if 'recomendacao' in divergencia:
            print(f"      Recomendação: {divergencia['recomendacao']}")
    
    return validacao

def testar_validacao_venda():
    """Testa validação de sinal de venda"""
    print("\n🔴 TESTANDO VALIDAÇÃO DE SINAL DE VENDA")
    print("=" * 50)
    
    dados_teste = criar_dados_teste()
    
    # Modificar dados para simular tendência de baixa
    for timeframe in dados_teste:
        df = dados_teste[timeframe]
        df['EMA8'] = df['EMA8'] * 0.95  # EMA8 menor que EMA21
        df['rsi'] = df['rsi'] * 0.8     # RSI mais baixo
        df['volume_ratio'] = df['volume_ratio'] * 1.3  # Volume maior
    
    # Validar sinal de venda
    validacao = validar_sinal_completo("ETHUSDT", "venda", dados_teste)
    
    print(f"📊 Resultado da Validação:")
    print(f"   Símbolo: {validacao['symbol']}")
    print(f"   Tipo de Sinal: {validacao['sinal_tipo'].upper()}")
    print(f"   Válido: {'✅ SIM' if validacao['valido'] else '❌ NÃO'}")
    print(f"   Confiança: {validacao['confianca']:.1f}%")
    print(f"   Score Final: {validacao['score_final']:.1f}/100")
    print(f"   Recomendação: {validacao['recomendacao']}")
    
    return validacao

def testar_deteccao_divergencias():
    """Testa detecção de divergências"""
    print("\n🚨 TESTANDO DETECÇÃO DE DIVERGÊNCIAS")
    print("=" * 50)
    
    dados_teste = criar_dados_teste()
    
    # Criar divergência artificial
    # Timeframes curtos bullish, longos bearish
    timeframes_curtos = ['1m', '5m', '15m']
    timeframes_longos = ['1h', '4h', '1d']
    
    for tf in timeframes_curtos:
        df = dados_teste[tf]
        df['EMA8'] = df['EMA8'] * 1.05  # Bullish
        df['rsi'] = df['rsi'] * 1.1     # RSI alto
    
    for tf in timeframes_longos:
        df = dados_teste[tf]
        df['EMA8'] = df['EMA8'] * 0.95  # Bearish
        df['rsi'] = df['rsi'] * 0.9     # RSI baixo
    
    # Detectar divergências
    divergencias = detectar_divergencias_completo(dados_teste)
    
    print(f"🔍 Divergências Detectadas: {len(divergencias)}")
    
    for i, divergencia in enumerate(divergencias, 1):
        print(f"\n{i}. {divergencia['tipo']}")
        print(f"   Severidade: {divergencia['severidade']}")
        print(f"   Descrição: {divergencia['descricao']}")
        if 'recomendacao' in divergencia:
            print(f"   Recomendação: {divergencia['recomendacao']}")
        if 'timeframes_curtos' in divergencia:
            print(f"   Timeframes Curtos: {divergencia['timeframes_curtos']}")
        if 'timeframes_longos' in divergencia:
            print(f"   Timeframes Longos: {divergencia['timeframes_longos']}")
    
    return divergencias

def testar_analise_timeframe():
    """Testa análise individual de timeframes"""
    print("\n📊 TESTANDO ANÁLISE INDIVIDUAL DE TIMEFRAMES")
    print("=" * 50)
    
    dados_teste = criar_dados_teste()
    
    for timeframe, df in dados_teste.items():
        print(f"\n{timeframe.upper()} - {validator.timeframes_config[timeframe]['name']}:")
        
        analysis = validator.calcular_score_timeframe(df, timeframe)
        
        print(f"   Score: {analysis['score']:.1f}/100")
        print(f"   Tendência: {analysis['tendencia'].upper()}")
        print(f"   Confiança: {analysis['confianca']:.1f}")
        print(f"   RSI: {analysis['rsi']:.1f}")
        print(f"   Volume Ratio: {analysis['volume_ratio']:.2f}")
        print(f"   Volatilidade: {analysis['volatilidade']:.2f}%")

def gerar_relatorio_completo():
    """Gera relatório completo de validação"""
    print("\n📋 GERANDO RELATÓRIO COMPLETO")
    print("=" * 50)
    
    # Primeiro fazer uma validação
    dados_teste = criar_dados_teste()
    validar_sinal_completo("SOLUSDT", "compra", dados_teste)
    
    # Gerar relatório
    relatorio = validator.gerar_relatorio_validacao("SOLUSDT")
    print(relatorio)

def mostrar_estatisticas():
    """Mostra estatísticas do validador"""
    print("\n📈 ESTATÍSTICAS DO VALIDADOR")
    print("=" * 50)
    
    stats = validator.get_estatisticas_validacao()
    
    print(f"Total de Validações: {stats['total_validacoes']}")
    print(f"Validações Válidas: {stats['validacoes_validas']}")
    print(f"Validações Inválidas: {stats['validacoes_invalidas']}")
    print(f"Taxa de Sucesso: {stats['taxa_sucesso']:.1f}%")
    print(f"Confiança Média: {stats['confianca_media']:.1f}%")
    print(f"Última Atualização: {stats['ultima_atualizacao']}")

def main():
    """Função principal de teste"""
    print("🧪 TESTE DO MULTI-TIMEFRAME VALIDATOR")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Testar validação de compra
        testar_validacao_compra()
        
        # Testar validação de venda
        testar_validacao_venda()
        
        # Testar detecção de divergências
        testar_deteccao_divergencias()
        
        # Testar análise individual de timeframes
        testar_analise_timeframe()
        
        # Gerar relatório completo
        gerar_relatorio_completo()
        
        # Mostrar estatísticas
        mostrar_estatisticas()
        
        print("\n✅ Todos os testes concluídos com sucesso!")
        print("🎯 Sistema de validação multi-timeframe funcionando corretamente!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

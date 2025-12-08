#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXEMPLO DE USO - ANÁLISE DETALHADA DE CANDLES
Demonstra como usar a nova funcionalidade de análise detalhada de candles
"""

from analise_candles_detalhada import analisar_candle_atual
from analise_candles_integracao import incluir_analise_candles_relatorio, formatar_candles_para_relatorio
from motor_renan import analise_completa
from relatorio_tecnico import gerar_relatorio
import pandas as pd
import requests


def exemplo_analise_candle_individual():
    """Exemplo de análise de um candle individual"""
    
    print("="*60)
    print("EXEMPLO: ANÁLISE DETALHADA DE CANDLE INDIVIDUAL")
    print("="*60)
    
    # Buscar dados
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": "1h", "limit": 100}
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df.index = pd.to_datetime([pd.Timestamp(int(ts), unit='ms') for ts in [d[0] for d in data]])
        
        # Analisar candle atual
        analise = analisar_candle_atual(df, "1h")
        
        if 'erro' not in analise:
            print("✅ Análise realizada com sucesso!")
            print(f"\n📊 Resumo: {analise['resumo']}")
            
            # Exibir informações principais
            candle_info = analise['candle_atual']
            precos = analise['precos']
            classificacao = analise['classificacao']
            tendencia = analise['tendencia']
            
            print(f"\n🕐 Horário: {candle_info['timestamp_inicio']} - {candle_info['timestamp_fechamento']}")
            print(f"⏱️ Tempo Restante: {candle_info['tempo_restante']}")
            print(f"💰 Range: ${precos['range']:,.2f} ({precos['range_percentual']}%)")
            print(f"🎯 Tipo: {classificacao['tipo']} - {classificacao['significado']}")
            print(f"📈 Tendência: {tendencia['direcao']} {tendencia['intensidade']}")
            
        else:
            print(f"❌ Erro: {analise['erro']}")
    else:
        print("❌ Erro ao buscar dados da Binance")


def exemplo_integracao_relatorio():
    """Exemplo de integração com relatório completo"""
    
    print("\n" + "="*60)
    print("EXEMPLO: INTEGRAÇÃO COM RELATÓRIO COMPLETO")
    print("="*60)
    
    # Gerar relatório completo com análise de candles
    print("🔄 Gerando relatório completo com análise de candles...")
    
    try:
        relatorio = gerar_relatorio("BTCUSDT", "1h", salvar=False)
        
        # Verificar se a análise de candles foi incluída
        if "ANÁLISE DETALHADA DO CANDLE ATUAL" in relatorio:
            print("✅ Análise de candles incluída no relatório!")
            
            # Extrair seção de candles
            inicio = relatorio.find("🕐 ANÁLISE DETALHADA DO CANDLE ATUAL:")
            fim = relatorio.find("😨 SENTIMENT:", inicio)
            
            if inicio != -1 and fim != -1:
                secao_candles = relatorio[inicio:fim].strip()
                print("\n📋 Seção de Candles do Relatório:")
                print("-" * 40)
                print(secao_candles)
                print("-" * 40)
        else:
            print("⚠️ Análise de candles não encontrada no relatório")
            
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")


def exemplo_motor_renan_com_candles():
    """Exemplo usando Motor Renan com análise de candles"""
    
    print("\n" + "="*60)
    print("EXEMPLO: MOTOR RENAN COM ANÁLISE DE CANDLES")
    print("="*60)
    
    print("🔄 Executando análise completa com Motor Renan...")
    
    try:
        resultado = analise_completa("BTCUSDT", "1h")
        
        if 'erro' not in resultado:
            print("✅ Análise completa realizada!")
            
            # Verificar se análise de candles está presente
            if 'candles_detalhados' in resultado:
                candles = resultado['candles_detalhados']
                
                if 'erro' not in candles:
                    print("\n🕐 Informações do Candle Atual:")
                    candle_info = candles['candle_atual']
                    precos = candles['precos']
                    classificacao = candles['classificacao']
                    
                    print(f"   Horário: {candle_info['timestamp_inicio']} - {candle_info['timestamp_fechamento']}")
                    print(f"   Restante: {candle_info['tempo_restante']}")
                    print(f"   Range: ${precos['range']:,.2f} ({precos['range_percentual']}%)")
                    print(f"   Tipo: {classificacao['tipo']}")
                    print(f"   Significado: {classificacao['significado']}")
                    print(f"   Força: {classificacao['forca']}")
                    
                    # Análise técnica
                    analise_tecnica = candles['analise_tecnica']
                    print(f"\n⚡ Análise Técnica:")
                    print(f"   Força: {analise_tecnica['forca_candle']['classificacao']} ({analise_tecnica['forca_candle']['score']}/100)")
                    print(f"   Momentum: {analise_tecnica['momentum']['classificacao']} ({analise_tecnica['momentum']['valor']}%)")
                    print(f"   Volatilidade: {analise_tecnica['volatilidade']['classificacao']} ({analise_tecnica['volatilidade']['valor']}%)")
                    print(f"   Posição: {analise_tecnica['posicao_relativa']['posicao']} ({analise_tecnica['posicao_relativa']['percentual']}%)")
                    
                    # Padrões detectados
                    padroes = candles['padroes']
                    print(f"\n🔍 Padrões: {padroes['descricao']}")
                    if padroes['padroes']:
                        for padrao in padroes['padroes']:
                            print(f"   • {padrao['nome']} ({padrao['tipo']}) - {padrao['confianca']}")
                    
                    print(f"\n📋 Resumo: {candles['resumo']}")
                    
                else:
                    print(f"❌ Erro na análise de candles: {candles['erro']}")
            else:
                print("⚠️ Análise de candles não incluída no resultado")
        else:
            print(f"❌ Erro na análise: {resultado['erro']}")
            
    except Exception as e:
        print(f"❌ Erro ao executar análise: {e}")


def exemplo_formatacao_personalizada():
    """Exemplo de formatação personalizada para relatórios"""
    
    print("\n" + "="*60)
    print("EXEMPLO: FORMATAÇÃO PERSONALIZADA")
    print("="*60)
    
    # Buscar dados
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "ETHUSDT", "interval": "15m", "limit": 100}
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df.index = pd.to_datetime([pd.Timestamp(int(ts), unit='ms') for ts in [d[0] for d in data]])
        
        # Analisar candle
        analise = analisar_candle_atual(df, "15m")
        
        if 'erro' not in analise:
            # Formatar para relatório
            texto_formatado = formatar_candles_para_relatorio(analise)
            
            print("✅ Formatação personalizada realizada!")
            print("\n📋 Relatório Formatado:")
            print("-" * 50)
            print(texto_formatado)
            print("-" * 50)
        else:
            print(f"❌ Erro: {analise['erro']}")
    else:
        print("❌ Erro ao buscar dados da Binance")


if __name__ == "__main__":
    print("🚀 EXEMPLOS DE USO - ANÁLISE DETALHADA DE CANDLES")
    print("="*60)
    
    # Executar exemplos
    exemplo_analise_candle_individual()
    exemplo_integracao_relatorio()
    exemplo_motor_renan_com_candles()
    exemplo_formatacao_personalizada()
    
    print("\n" + "="*60)
    print("✅ TODOS OS EXEMPLOS EXECUTADOS!")
    print("="*60)
    
    print("\n📋 COMO USAR EM SEUS PRÓPRIOS CÓDIGOS:")
    print("""
1. Análise Individual:
   from analise_candles_detalhada import analisar_candle_atual
   analise = analisar_candle_atual(df, "1h")

2. Integração com Relatórios:
   from analise_candles_integracao import incluir_analise_candles_relatorio
   resultado = incluir_analise_candles_relatorio(resultado, df, timeframe)

3. Motor Renan Completo:
   from motor_renan import analise_completa
   resultado = analise_completa("BTCUSDT", "1h")
   # A análise de candles já está incluída automaticamente

4. Relatório Técnico:
   from relatorio_tecnico import gerar_relatorio
   relatorio = gerar_relatorio("BTCUSDT", "1h")
   # A análise de candles já está incluída automaticamente
    """)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST SNE RADAR - SCRIPT PRINCIPAL
Interface principal para executar backtests do SNE Radar
"""

import os
import sys
from datetime import datetime, timedelta
import argparse
from backtest_sne import executar_backtest_completo, executar_backtest_diario, executar_backtest_rapido_otimizado, executar_backtest_rapido_melhorado, ColetorDadosHistoricos
from visualizacao_backtest import visualizar_backtest_completo

def menu_backtest():
    """Menu principal do sistema de backtest"""
    
    while True:
        print("\n" + "="*60)
        print("🚀 BACKTEST SNE RADAR - SISTEMA DE VALIDAÇÃO")
        print("="*60)
        print("1️⃣  Executar Backtest Completo")
        print("2️⃣  Coletar Dados Históricos")
        print("3️⃣  Visualizar Resultados")
        print("4️⃣  Backtest Rápido Otimizado (BTC 6 meses)")
        print("5️⃣  Backtest Rápido Melhorado (BTC 6 meses)")
        print("6️⃣  Backtest Diário (Swing Trading)")
        print("7️⃣  Backtest Diário Interativo")
        print("8️⃣  Backtest Multi-Pares")
        print("9️⃣  Comparar Estratégias")
        print("0️⃣  Sair")
        print("="*60)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            executar_backtest_interativo()
        elif opcao == "2":
            coletar_dados_interativo()
        elif opcao == "3":
            visualizar_resultados_interativo()
        elif opcao == "4":
            backtest_rapido()
        elif opcao == "5":
            backtest_rapido_melhorado()
        elif opcao == "6":
            backtest_diario()
        elif opcao == "7":
            backtest_diario_interativo()
        elif opcao == "8":
            backtest_multi_pares()
        elif opcao == "9":
            comparar_estrategias()
        elif opcao == "0":
            print("👋 Saindo do sistema de backtest...")
            break
        else:
            print("❌ Opção inválida!")

def executar_backtest_interativo():
    """Executa backtest com parâmetros interativos"""
    try:
        print("\n📊 EXECUTAR BACKTEST COMPLETO")
        print("-" * 40)
        
        # Parâmetros
        symbol = input("Par (ex: BTCUSDT): ").strip().upper()
        if not symbol:
            symbol = "BTCUSDT"
        
        print("\nTimeframes disponíveis:")
        print("1m, 5m, 15m, 30m, 1h, 4h, 1d")
        interval = input("Timeframe (ex: 1h): ").strip()
        if not interval:
            interval = "1h"
        
        # Datas
        print("\n📅 Período do backtest:")
        start_date = input("Data início (YYYY-MM-DD): ").strip()
        if not start_date:
            start_date = "2024-01-01"
        
        end_date = input("Data fim (YYYY-MM-DD) [Enter para hoje]: ").strip()
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Configurações
        print("\n⚙️ Configurações:")
        capital = input("Capital inicial ($) [10000]: ").strip()
        capital_inicial = int(capital) if capital.isdigit() else 10000
        
        print(f"\n🚀 Iniciando backtest...")
        print(f"📊 Par: {symbol}")
        print(f"⏰ Timeframe: {interval}")
        print(f"📅 Período: {start_date} até {end_date}")
        print(f"💰 Capital: ${capital_inicial:,}")
        
        # Executar backtest
        metricas = executar_backtest_completo(symbol, interval, start_date, end_date)
        
        if metricas:
            print("\n✅ Backtest concluído!")
            
            # Perguntar se quer visualizar
            visualizar = input("\n📊 Gerar visualizações? (s/n): ").strip().lower()
            if visualizar in ['s', 'sim', 'y', 'yes']:
                arquivo = f"backtest_results_{symbol}_{interval}_{start_date}.json"
                if os.path.exists(arquivo):
                    visualizar_backtest_completo(arquivo)
                else:
                    print("❌ Arquivo de resultados não encontrado")
        
    except Exception as e:
        print(f"❌ Erro no backtest: {e}")

def coletar_dados_interativo():
    """Coleta dados históricos interativamente"""
    try:
        print("\n📊 COLETAR DADOS HISTÓRICOS")
        print("-" * 40)
        
        coletor = ColetorDadosHistoricos()
        
        symbol = input("Par (ex: BTCUSDT): ").strip().upper()
        if not symbol:
            symbol = "BTCUSDT"
        
        print("\nTimeframes disponíveis:")
        print("1m, 5m, 15m, 30m, 1h, 4h, 1d")
        interval = input("Timeframe: ").strip()
        if not interval:
            interval = "1h"
        
        start_date = input("Data início (YYYY-MM-DD): ").strip()
        if not start_date:
            start_date = "2024-01-01"
        
        end_date = input("Data fim (YYYY-MM-DD) [Enter para hoje]: ").strip()
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n📊 Coletando dados: {symbol} {interval}")
        df = coletor.coletar_dados(symbol, interval, start_date, end_date)
        
        if not df.empty:
            coletor.salvar_dados(df, symbol, interval)
            print(f"✅ {len(df)} candles coletados e salvos!")
        else:
            print("❌ Falha ao coletar dados")
        
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")

def visualizar_resultados_interativo():
    """Visualiza resultados interativamente"""
    try:
        print("\n📊 VISUALIZAR RESULTADOS")
        print("-" * 40)
        
        # Listar arquivos de resultados
        arquivos = [f for f in os.listdir('.') if f.startswith('backtest_results_') and f.endswith('.json')]
        
        if not arquivos:
            print("❌ Nenhum arquivo de resultados encontrado")
            return
        
        print("📁 Arquivos de resultados disponíveis:")
        for i, arquivo in enumerate(arquivos, 1):
            print(f"   {i}. {arquivo}")
        
        escolha = input("\nEscolha um arquivo (número): ").strip()
        
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(arquivos):
                arquivo = arquivos[idx]
                print(f"\n📊 Visualizando: {arquivo}")
                visualizar_backtest_completo(arquivo)
            else:
                print("❌ Número inválido")
        except ValueError:
            print("❌ Entrada inválida")
        
    except Exception as e:
        print(f"❌ Erro na visualização: {e}")

def backtest_rapido():
    """Executa backtest rápido otimizado com parâmetros ultra agressivos"""
    try:
        print("\n⚡ BACKTEST RÁPIDO - BTC 6 MESES")
        print("-" * 40)
        
        # Parâmetros padrão
        symbol = "BTCUSDT"
        interval = "1h"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        print(f"📊 Par: {symbol}")
        print(f"⏰ Timeframe: {interval}")
        print(f"📅 Período: {start_date} até {end_date}")
        print(f"💰 Capital: $10,000")
        print(f"🎯 Estratégia: Day Trading Otimizado")
        
        print(f"\n📊 Parâmetros ultra agressivos:")
        print(f"   🛡️ Stop Loss: 2.0% (otimizado)")
        print(f"   🎯 Take Profit: 4.0% (melhor R:R)")
        print(f"   📊 Confiança mínima: 45% (muito permissivo)")
        print(f"   🔄 Modo ultra agressivo: Ativado")
        print(f"   🚨 Modo emergência: Após 100 candles")
        
        confirmar = input("\n🚀 Executar backtest rápido? (s/n): ").strip().lower()
        if confirmar not in ['s', 'sim', 'y', 'yes']:
            return
        
        print("\n⚡ Executando backtest rápido otimizado...")
        metricas = executar_backtest_rapido_otimizado(symbol, start_date, end_date)
        
        if metricas:
            print("\n✅ Backtest rápido otimizado concluído!")
            
            # Gerar visualizações automaticamente
            arquivo = f"backtest_rapido_{symbol}_{start_date}.json"
            if os.path.exists(arquivo):
                print("📊 Gerando visualizações...")
                visualizar_backtest_completo(arquivo)
        
    except Exception as e:
        print(f"❌ Erro no backtest rápido: {e}")

def backtest_rapido_melhorado():
    """Executa backtest rápido melhorado com parâmetros conservadores e filtros"""
    try:
        print("\n⚡ BACKTEST RÁPIDO MELHORADO - BTC 6 MESES")
        print("-" * 50)
        
        # Parâmetros padrão
        symbol = "BTCUSDT"
        interval = "1h"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        print(f"📊 Par: {symbol}")
        print(f"⏰ Timeframe: {interval}")
        print(f"📅 Período: {start_date} até {end_date}")
        print(f"💰 Capital: $10,000")
        print(f"🎯 Estratégia: Day Trading Melhorado")
        
        print(f"\n📊 Parâmetros equilibrados com estratégia S/R + Volume ULTRA PERMISSIVA:")
        print(f"   🛡️ Stop Loss: 1% (mais apertado)")
        print(f"   🎯 Take Profit: 2% (mais rápido)")
        print(f"   📊 Confiança mínima: 30% (ULTRA PERMISSIVA para SHORTs)")
        print(f"   🔄 Modo agressivo: Ativado com estratégia S/R + Volume")
        print(f"   📈 COMPRAR: Suporte + Volume alto + Score ≥6.0")
        print(f"   📉 VENDER: Resistência + Volume baixo + Score ≤4.0")
        print(f"   🎯 Meta: MUITO MAIS SHORTs + Win Rate 60-70%")
        print(f"   ⚡ Timing: Baseado em S/R + Volume + Força dos níveis")
        
        confirmar = input("\n🚀 Executar backtest rápido melhorado? (s/n): ").strip().lower()
        if confirmar not in ['s', 'sim', 'y', 'yes']:
            return
        
        print("\n⚡ Executando backtest rápido melhorado...")
        metricas = executar_backtest_rapido_melhorado(symbol, start_date, end_date)
        
        if metricas:
            print("\n✅ Backtest rápido melhorado concluído!")
            
            # Gerar visualizações automaticamente
            arquivo = f"backtest_rapido_melhorado_{symbol}_{start_date}.json"
            if os.path.exists(arquivo):
                print("📊 Gerando visualizações...")
                visualizar_backtest_completo(arquivo)
        
    except Exception as e:
        print(f"❌ Erro no backtest rápido melhorado: {e}")


def backtest_diario():
    """Executa backtest diário otimizado para swing trading"""
    try:
        print("\n📅 BACKTEST DIÁRIO - SWING TRADING")
        print("-" * 50)
        
        # Parâmetros padrão para swing trading
        symbol = "BTCUSDT"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 ano
        
        print(f"📊 Par: {symbol}")
        print(f"⏰ Timeframe: 1D (Diário)")
        print(f"📅 Período: {start_date} até {end_date}")
        print(f"💰 Capital: $10,000")
        print(f"🎯 Estratégia: Swing Trading Diário")
        
        print(f"\n📊 Parâmetros otimizados para diário:")
        print(f"   🛡️ Stop Loss: 3.0% (mais conservador)")
        print(f"   🎯 Take Profit: 6.0% (melhor R:R)")
        print(f"   📊 Confiança mínima: 55% (mais conservador)")
        
        confirmar = input("\n🚀 Executar backtest diário? (s/n): ").strip().lower()
        if confirmar not in ['s', 'sim', 'y', 'yes']:
            return
        
        print("\n📅 Executando backtest diário...")
        metricas = executar_backtest_diario(symbol, start_date, end_date)
        
        if metricas:
            print("\n✅ Backtest diário concluído!")
            
            # Gerar visualizações automaticamente
            arquivo = f"backtest_diario_{symbol}_{start_date}.json"
            if os.path.exists(arquivo):
                print("📊 Gerando visualizações...")
                visualizar_backtest_completo(arquivo)
        
    except Exception as e:
        print(f"❌ Erro no backtest diário: {e}")

def backtest_diario_interativo():
    """Executa backtest diário com parâmetros interativos"""
    try:
        print("\n📅 BACKTEST DIÁRIO INTERATIVO")
        print("-" * 50)
        
        # Escolher par
        print("Pares disponíveis:")
        pares = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOTUSDT"]
        for i, par in enumerate(pares, 1):
            print(f"   {i}. {par}")
        
        escolha_par = input("\nEscolha o par (1-5) ou digite customizado: ").strip()
        
        if escolha_par.isdigit() and 1 <= int(escolha_par) <= len(pares):
            symbol = pares[int(escolha_par) - 1]
        else:
            symbol = escolha_par.upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
        
        # Escolher período
        print(f"\nPeríodos disponíveis:")
        print("   1. 6 meses")
        print("   2. 1 ano")
        print("   3. 2 anos")
        print("   4. Customizado")
        
        escolha_periodo = input("Escolha o período (1-4): ").strip()
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        if escolha_periodo == "1":
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        elif escolha_periodo == "2":
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif escolha_periodo == "3":
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        elif escolha_periodo == "4":
            start_date = input("Data início (YYYY-MM-DD): ").strip()
        else:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        print(f"\n📊 Configuração:")
        print(f"   Par: {symbol}")
        print(f"   Timeframe: 1D (Diário)")
        print(f"   Período: {start_date} até {end_date}")
        print(f"   Capital: $10,000")
        
        confirmar = input("\n🚀 Executar backtest diário interativo? (s/n): ").strip().lower()
        if confirmar not in ['s', 'sim', 'y', 'yes']:
            return
        
        print("\n📅 Executando backtest diário interativo...")
        metricas = executar_backtest_diario(symbol, start_date, end_date)
        
        if metricas:
            print("\n✅ Backtest diário interativo concluído!")
            
            # Gerar visualizações automaticamente
            arquivo = f"backtest_diario_{symbol}_{start_date}.json"
            if os.path.exists(arquivo):
                print("📊 Gerando visualizações...")
                visualizar_backtest_completo(arquivo)
        
    except Exception as e:
        print(f"❌ Erro no backtest diário interativo: {e}")

def backtest_multi_pares():
    """Executa backtest em múltiplos pares"""
    try:
        print("\n📊 BACKTEST MULTI-PARES")
        print("-" * 40)
        
        # Pares padrão
        pares = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        
        print("Pares disponíveis:")
        for i, par in enumerate(pares, 1):
            print(f"   {i}. {par}")
        
        escolha = input("\nEscolha os pares (ex: 1,2,3 ou Enter para todos): ").strip()
        
        if escolha:
            try:
                indices = [int(x.strip()) - 1 for x in escolha.split(',')]
                pares_selecionados = [pares[i] for i in indices if 0 <= i < len(pares)]
            except:
                pares_selecionados = pares
        else:
            pares_selecionados = pares
        
        # Parâmetros
        interval = input("Timeframe (ex: 1h): ").strip() or "1h"
        start_date = input("Data início (YYYY-MM-DD): ").strip() or "2024-01-01"
        end_date = input("Data fim (YYYY-MM-DD): ").strip() or datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n🚀 Executando backtest em {len(pares_selecionados)} pares...")
        
        resultados_multi = {}
        
        for par in pares_selecionados:
            print(f"\n📊 Processando {par}...")
            metricas = executar_backtest_completo(par, interval, start_date, end_date)
            if metricas:
                resultados_multi[par] = metricas
        
        # Resumo comparativo
        print("\n📊 RESUMO COMPARATIVO:")
        print("-" * 50)
        print(f"{'Par':<10} {'Retorno':<10} {'Win Rate':<10} {'Trades':<8} {'Sharpe':<8}")
        print("-" * 50)
        
        for par, metricas in resultados_multi.items():
            retorno = metricas.get('retorno_total', 0)
            win_rate = metricas.get('win_rate', 0)
            trades = metricas.get('total_trades', 0)
            sharpe = metricas.get('sharpe_ratio', 0)
            
            print(f"{par:<10} {retorno:>+8.1f}% {win_rate:>8.1f}% {trades:>6} {sharpe:>6.2f}")
        
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Erro no backtest multi-pares: {e}")

def comparar_estrategias():
    """Compara diferentes estratégias de backtest"""
    try:
        print("\n📊 COMPARAR ESTRATÉGIAS")
        print("-" * 40)
        print("Esta funcionalidade será implementada em versão futura")
        print("Permitirá comparar diferentes configurações de:")
        print("- Stop Loss / Take Profit")
        print("- Thresholds de confiança")
        print("- Timeframes")
        print("- Filtros de volume")
        
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")

def main():
    """Função principal"""
    try:
        print("🚀 SNE RADAR - SISTEMA DE BACKTEST")
        print("Versão 1.0 - Validação de Estratégias")
        print("="*50)
        
        # Verificar dependências
        try:
            import requests
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
        except ImportError as e:
            print(f"❌ Dependência não encontrada: {e}")
            print("Instale com: pip install requests pandas numpy matplotlib")
            return
        
        # Criar diretórios necessários
        os.makedirs("backtest_data", exist_ok=True)
        os.makedirs("backtest_results", exist_ok=True)
        
        # Executar menu
        menu_backtest()
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")

if __name__ == "__main__":
    main()

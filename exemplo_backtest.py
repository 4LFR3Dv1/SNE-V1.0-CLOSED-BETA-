#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXEMPLO PRÁTICO - BACKTEST SNE RADAR
Demonstração completa do sistema de backtest
"""

from backtest_sne import executar_backtest_completo, ColetorDadosHistoricos
from visualizacao_backtest import visualizar_backtest_completo
import os

def exemplo_backtest_completo():
    """Exemplo completo de backtest"""
    
    print("🚀 EXEMPLO PRÁTICO - BACKTEST SNE RADAR")
    print("="*60)
    
    # Parâmetros do exemplo
    symbol = "BTCUSDT"
    interval = "1h"
    start_date = "2024-01-01"
    end_date = "2024-06-30"
    
    print(f"📊 Parâmetros do exemplo:")
    print(f"   Par: {symbol}")
    print(f"   Timeframe: {interval}")
    print(f"   Período: {start_date} até {end_date}")
    print(f"   Capital inicial: $10,000")
    print()
    
    try:
        # 1. Executar backtest
        print("🚀 Executando backtest...")
        metricas = executar_backtest_completo(symbol, interval, start_date, end_date)
        
        if not metricas:
            print("❌ Falha no backtest")
            return
        
        # 2. Mostrar resultados principais
        print("\n📊 RESULTADOS PRINCIPAIS:")
        print("-" * 40)
        print(f"💰 Capital inicial: ${metricas.get('capital_inicial', 0):,.2f}")
        print(f"💰 Capital final: ${metricas.get('capital_final', 0):,.2f}")
        print(f"📈 Retorno total: {metricas.get('retorno_total', 0):+.2f}%")
        print(f"🎯 Win rate: {metricas.get('win_rate', 0):.1f}%")
        print(f"📊 Total de trades: {metricas.get('total_trades', 0)}")
        print(f"⚡ Sharpe ratio: {metricas.get('sharpe_ratio', 0):.2f}")
        print(f"📉 Max drawdown: {metricas.get('max_drawdown', 0):.2f}%")
        
        # 3. Avaliação qualitativa
        print("\n🎯 AVALIAÇÃO:")
        retorno = metricas.get('retorno_total', 0)
        win_rate = metricas.get('win_rate', 0)
        sharpe = metricas.get('sharpe_ratio', 0)
        drawdown = metricas.get('max_drawdown', 0)
        
        if retorno > 0:
            print("✅ Estratégia lucrativa")
        else:
            print("❌ Estratégia com prejuízo")
        
        if win_rate > 50:
            print("✅ Win rate aceitável")
        else:
            print("❌ Win rate baixo")
        
        if sharpe > 1.0:
            print("✅ Sharpe ratio bom")
        else:
            print("⚠️ Sharpe ratio baixo")
        
        if drawdown > -20:
            print("✅ Drawdown controlado")
        else:
            print("⚠️ Drawdown alto")
        
        # 4. Gerar visualizações
        print("\n📊 Gerando visualizações...")
        arquivo_resultados = f"backtest_results_{symbol}_{interval}_{start_date}.json"
        
        if os.path.exists(arquivo_resultados):
            visualizar_backtest_completo(arquivo_resultados)
            print("✅ Visualizações geradas!")
        else:
            print("❌ Arquivo de resultados não encontrado")
        
        # 5. Próximos passos sugeridos
        print("\n💡 PRÓXIMOS PASSOS SUGERIDOS:")
        print("1. Testar em diferentes períodos")
        print("2. Validar em outros pares (ETH, SOL)")
        print("3. Otimizar parâmetros (SL/TP)")
        print("4. Implementar filtros adicionais")
        print("5. Testar em timeframes diferentes")
        
    except Exception as e:
        print(f"❌ Erro no exemplo: {e}")

def exemplo_coleta_dados():
    """Exemplo de coleta de dados históricos"""
    
    print("\n📊 EXEMPLO - COLETA DE DADOS HISTÓRICOS")
    print("-" * 50)
    
    try:
        coletor = ColetorDadosHistoricos()
        
        # Coletar dados de BTC
        print("📊 Coletando dados de BTCUSDT...")
        df_btc = coletor.coletar_dados("BTCUSDT", "1h", "2024-01-01", "2024-06-30")
        
        if not df_btc.empty:
            print(f"✅ {len(df_btc)} candles coletados para BTC")
            coletor.salvar_dados(df_btc, "BTCUSDT", "1h")
        
        # Coletar dados de ETH
        print("📊 Coletando dados de ETHUSDT...")
        df_eth = coletor.coletar_dados("ETHUSDT", "1h", "2024-01-01", "2024-06-30")
        
        if not df_eth.empty:
            print(f"✅ {len(df_eth)} candles coletados para ETH")
            coletor.salvar_dados(df_eth, "ETHUSDT", "1h")
        
        print("\n💾 Dados salvos em pasta 'backtest_data/'")
        
    except Exception as e:
        print(f"❌ Erro na coleta: {e}")

def exemplo_backtest_multi_pares():
    """Exemplo de backtest em múltiplos pares"""
    
    print("\n📊 EXEMPLO - BACKTEST MULTI-PARES")
    print("-" * 50)
    
    pares = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    interval = "1h"
    start_date = "2024-01-01"
    end_date = "2024-06-30"
    
    resultados = {}
    
    try:
        for par in pares:
            print(f"\n📊 Processando {par}...")
            metricas = executar_backtest_completo(par, interval, start_date, end_date)
            
            if metricas:
                resultados[par] = metricas
                print(f"✅ {par}: {metricas.get('retorno_total', 0):+.1f}%")
        
        # Comparação
        if resultados:
            print("\n📊 COMPARAÇÃO DE RESULTADOS:")
            print("-" * 60)
            print(f"{'Par':<10} {'Retorno':<10} {'Win Rate':<10} {'Trades':<8} {'Sharpe':<8}")
            print("-" * 60)
            
            for par, metricas in resultados.items():
                retorno = metricas.get('retorno_total', 0)
                win_rate = metricas.get('win_rate', 0)
                trades = metricas.get('total_trades', 0)
                sharpe = metricas.get('sharpe_ratio', 0)
                
                print(f"{par:<10} {retorno:>+8.1f}% {win_rate:>8.1f}% {trades:>6} {sharpe:>6.2f}")
            
            print("-" * 60)
            
            # Melhor par
            melhor_par = max(resultados.keys(), key=lambda x: resultados[x].get('retorno_total', 0))
            melhor_retorno = resultados[melhor_par].get('retorno_total', 0)
            
            print(f"\n🏆 Melhor performance: {melhor_par} ({melhor_retorno:+.1f}%)")
        
    except Exception as e:
        print(f"❌ Erro no backtest multi-pares: {e}")

def main():
    """Função principal do exemplo"""
    
    print("🚀 EXEMPLOS PRÁTICOS - BACKTEST SNE RADAR")
    print("="*60)
    print("Este script demonstra as principais funcionalidades")
    print("do sistema de backtest do SNE Radar.")
    print()
    
    try:
        # Exemplo 1: Backtest completo
        exemplo_backtest_completo()
        
        # Exemplo 2: Coleta de dados
        exemplo_coleta_dados()
        
        # Exemplo 3: Multi-pares
        exemplo_backtest_multi_pares()
        
        print("\n✅ EXEMPLOS CONCLUÍDOS!")
        print("\n💡 Para usar o sistema completo, execute:")
        print("   python3 backtest_main.py")
        
    except KeyboardInterrupt:
        print("\n\n👋 Exemplos interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")

if __name__ == "__main__":
    main()


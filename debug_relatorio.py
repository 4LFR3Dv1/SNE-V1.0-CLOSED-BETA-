#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG RELATÓRIO - Identifica onde está o erro 'close'
"""

import sys
import os
import traceback

# Adicionar o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from relatorio_tecnico import coletar_dados
from indicadores import calcular_indicadores

def debug_relatorio():
    """Debug passo a passo para identificar o erro"""
    print("🔍 DEBUG RELATÓRIO - Identificando erro 'close'")
    
    try:
        # 1. Coletar dados
        print("\n1️⃣ Coletando dados...")
        dados = coletar_dados("BTCUSDT", "1h")
        if dados is None:
            print("❌ Falha na coleta de dados")
            return
        
        print(f"✅ Dados coletados: {len(dados)} candles")
        print(f"📊 Colunas disponíveis: {list(dados.columns)}")
        
        # 2. Verificar se 'close' existe
        if 'close' not in dados.columns:
            print("❌ Coluna 'close' não encontrada!")
            return
        
        print(f"✅ Coluna 'close' encontrada: {dados['close'].iloc[-1]}")
        
        # 3. Testar cada função de análise individualmente
        print("\n2️⃣ Testando funções de análise...")
        
        # Teste contexto_global
        try:
            print("   📊 Testando contexto_global...")
            import contexto_global
            ctx = contexto_global.analisar_contexto(dados)
            print("   ✅ contexto_global OK")
        except Exception as e:
            print(f"   ❌ Erro em contexto_global: {e}")
            traceback.print_exc()
            return
        
        # Teste estrutura_mercado
        try:
            print("   📊 Testando estrutura_mercado...")
            import estrutura_mercado
            est = estrutura_mercado.analisar_estrutura(dados)
            print("   ✅ estrutura_mercado OK")
        except Exception as e:
            print(f"   ❌ Erro em estrutura_mercado: {e}")
            traceback.print_exc()
            return
        
        # Teste multi_timeframe
        try:
            print("   📊 Testando multi_timeframe...")
            import multi_timeframe
            mtf = multi_timeframe.analise_multitf("BTCUSDT")
            print("   ✅ multi_timeframe OK")
        except Exception as e:
            print(f"   ❌ Erro em multi_timeframe: {e}")
            traceback.print_exc()
            return
        
        # Teste padroes_graficos
        try:
            print("   📊 Testando padroes_graficos...")
            import padroes_graficos
            pad = padroes_graficos.detectar_padroes(dados)
            print("   ✅ padroes_graficos OK")
        except Exception as e:
            print(f"   ❌ Erro em padroes_graficos: {e}")
            traceback.print_exc()
            return
        
        # Teste wedges
        try:
            print("   📊 Testando wedges...")
            wedges = padroes_graficos.detectar_wedges(dados)
            print("   ✅ wedges OK")
        except Exception as e:
            print(f"   ❌ Erro em wedges: {e}")
            traceback.print_exc()
            return
        
        # Teste analise_candles_integracao
        try:
            print("   📊 Testando analise_candles_integracao...")
            from analise_candles_integracao import incluir_analise_candles_relatorio
            dados_modificados = incluir_analise_candles_relatorio({'dados': dados}, dados, "1h")
            print("   ✅ analise_candles_integracao OK")
        except Exception as e:
            print(f"   ❌ Erro em analise_candles_integracao: {e}")
            traceback.print_exc()
            return
        
        print("\n✅ Todas as funções de análise funcionaram!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_relatorio()













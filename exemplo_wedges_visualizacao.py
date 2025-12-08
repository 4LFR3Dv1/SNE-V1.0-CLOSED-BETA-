#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXEMPLO DE USO - WEDGES COM VISUALIZAÇÃO
Demonstra como usar a detecção de wedges com gráficos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Importar funções do sistema
from padroes_graficos import detectar_wedges, verificar_confirmacao_quebra
from visualizacao_wedges import criar_grafico_wedge, criar_grafico_comparativo

def criar_dados_exemplo():
    """Cria dados de exemplo simulando um wedge"""
    
    # Gerar timestamps
    start_date = datetime.now() - timedelta(hours=100)
    timestamps = pd.date_range(start=start_date, periods=100, freq='1H')
    
    # Simular dados de preço com wedge pattern
    base_price = 50000
    
    # Criar padrão de Rising Wedge
    prices = []
    for i in range(100):
        # Tendência geral ascendente com convergência
        trend = i * 2  # Tendência geral
        noise = np.random.normal(0, 50)  # Ruído
        
        # Criar convergência (wedge)
        convergence_factor = 1 - (i / 100) * 0.3  # Reduz amplitude ao longo do tempo
        
        price = base_price + trend + noise * convergence_factor
        prices.append(price)
    
    # Criar DataFrame OHLCV
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': prices,
        'high': [p + np.random.uniform(10, 100) for p in prices],
        'low': [p - np.random.uniform(10, 100) for p in prices],
        'close': prices,
        'volume': [np.random.uniform(1000, 5000) for _ in range(100)]
    })
    
    # Ajustar high/low para serem consistentes
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    df.set_index('timestamp', inplace=True)
    return df

def demonstrar_wedges():
    """Demonstra a detecção e visualização de wedges"""
    
    print("🔺 DEMONSTRAÇÃO DE WEDGES COM VISUALIZAÇÃO")
    print("=" * 50)
    
    # Criar dados de exemplo
    print("📊 Criando dados de exemplo...")
    df = criar_dados_exemplo()
    
    # Detectar wedges
    print("🔍 Detectando padrões de wedge...")
    wedges = detectar_wedges(df)
    
    if wedges.get('wedge_detectado', False):
        print(f"✅ {wedges['nome']} detectado!")
        print(f"   📊 Confiança: {wedges['confianca']}%")
        print(f"   ⚡ Prob. Reversão: {wedges['probabilidade_reversao']}%")
        print(f"   📐 Ângulo: {wedges.get('angulo_convergencia', 0):.1f}°")
        print(f"   🎯 Toques Resistência: {wedges['num_touches_resistencia']}")
        print(f"   🎯 Toques Suporte: {wedges['num_touches_suporte']}")
        
        # Verificar quebra
        print("\n🔍 Verificando confirmação de quebra...")
        quebra = verificar_confirmacao_quebra(df, wedges)
        
        if quebra.get('quebrado', False):
            print(f"🚨 QUEBRA CONFIRMADA!")
            print(f"   Tipo: {quebra['tipo_quebra']}")
            print(f"   Preço: ${quebra['preco_quebra']:,.2f}")
            print(f"   Volume: {'✅ Confirmado' if quebra['volume_confirma'] else '❌ Baixo'}")
        else:
            print(f"⏳ {quebra.get('motivo', 'Aguardando confirmação')}")
        
        # Criar gráfico
        print("\n📈 Criando gráfico com wedge traçado...")
        try:
            grafico_bytes = criar_grafico_wedge(df, wedges, "BTCUSDT", "1h")
            if grafico_bytes:
                print("✅ Gráfico criado com sucesso!")
                print(f"   📏 Tamanho: {len(grafico_bytes)} bytes")
                
                # Salvar gráfico para visualização
                with open('exemplo_wedge.png', 'wb') as f:
                    f.write(grafico_bytes)
                print("💾 Gráfico salvo como 'exemplo_wedge.png'")
            else:
                print("❌ Falha ao criar gráfico")
        except Exception as e:
            print(f"❌ Erro ao criar gráfico: {e}")
        
        # Mostrar níveis operacionais
        print("\n🎯 NÍVEIS OPERACIONAIS:")
        if wedges.get('alvo_teorico'):
            alvo = wedges['alvo_teorico']
            print(f"   🎯 Alvo: ${alvo['preco']:,.2f} ({alvo['direcao']})")
            print(f"   📏 Distância: {alvo['percentual']:.1f}%")
        
        if wedges.get('stop_loss'):
            stop = wedges['stop_loss']
            print(f"   🛑 Stop Loss: ${stop['preco']:,.2f}")
            print(f"   📏 Distância SL: {stop['percentual']:.1f}%")
        
        # Interpretação
        print(f"\n📚 INTERPRETAÇÃO:")
        if wedges['tipo'] == 'RISING_WEDGE':
            print("   🔴 Rising Wedge = Sinal BEARISH")
            print("   📉 Expectativa: Queda após rompimento do suporte")
            print("   💡 Recomendação: Considerar posições SHORT")
        else:
            print("   🟢 Falling Wedge = Sinal BULLISH")
            print("   📈 Expectativa: Alta após rompimento da resistência")
            print("   💡 Recomendação: Considerar posições LONG")
    
    else:
        print("❌ Nenhum padrão wedge detectado")
        print(f"   Motivo: {wedges.get('motivo', 'Não identificado')}")
    
    print("\n" + "=" * 50)
    print("✅ Demonstração concluída!")

if __name__ == "__main__":
    demonstrar_wedges()


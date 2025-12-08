#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MULTI-PAIR ANÁLISE - Comparação técnica entre pares
"""

from motor_renan import analise_completa


PARES_PRINCIPAIS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'AVAXUSDT']


def analise_multi_pair(pares=None, timeframe="1h"):
    """Análise comparativa de múltiplos pares"""
    
    if pares is None:
        pares = PARES_PRINCIPAIS
    
    print(f"\n📊 ANALISANDO {len(pares)} PARES...")
    
    resultados = []
    
    for par in pares:
        print(f"   🔄 {par}...", end=' ', flush=True)
        
        # Suprimir prints verbosos do motor_renan
        import sys
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        analise = analise_completa(par, timeframe)
        
        sys.stdout = old_stdout
        
        if 'erro' not in analise:
            resultados.append(analise)
            print("✅")
        else:
            print("❌")
    
    # Ranking por confluência
    resultados_sorted = sorted(resultados, key=lambda x: x['confluencia']['score'], reverse=True)
    
    return {
        'pares': resultados_sorted,
        'total': len(resultados),
        'melhor': resultados_sorted[0] if resultados_sorted else None,
        'pior': resultados_sorted[-1] if resultados_sorted else None
    }


def exibir_multi_pair(resultado):
    """Exibe análise multi-pair"""
    print("\n" + "="*60)
    print("📊 ANÁLISE MULTI-PAIR TÉCNICA")
    print("="*60)
    
    print(f"\n🏆 RANKING POR CONFLUÊNCIA:")
    print(f"\n{'#':<3} {'Par':<12} {'Score':<8} {'Viés':<20} {'Recomendação':<30}")
    print("-" * 60)
    
    for i, analise in enumerate(resultado['pares'], 1):
        par = analise['symbol']
        score = analise['confluencia']['score']
        vies = analise['sintese']['vies']
        rec = analise['sintese']['recomendacao']
        
        print(f"{i:<3} {par:<12} {score:<8.1f} {vies:<20} {rec:<30}")
    
    if resultado['melhor']:
        print(f"\n✅ MELHOR SETUP:")
        m = resultado['melhor']
        print(f"   {m['symbol']} - Score {m['confluencia']['score']}/10")
        print(f"   {m['sintese']['recomendacao']}")
    
    if resultado['pior']:
        print(f"\n❌ EVITAR:")
        p = resultado['pior']
        print(f"   {p['symbol']} - Score {p['confluencia']['score']}/10")
        print(f"   {p['sintese']['recomendacao']}")
    
    print("\n" + "="*60)


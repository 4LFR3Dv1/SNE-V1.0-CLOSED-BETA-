#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOM PROFUNDO - Análise avançada de liquidez
"""

from fluxo_ativo import FluxoAtivo


def analise_dom_profunda(symbol="BTCUSDT"):
    """Análise profunda do order book"""
    
    print(f"\n🌊 ANALISANDO DOM PROFUNDO - {symbol}...")
    
    fluxo = FluxoAtivo()
    
    # Análise de pressão
    pressao = fluxo.calcular_pressao_liquidez(symbol)
    
    # Análise de depth
    depth = fluxo.obter_depth(symbol)
    
    if not depth or 'erro' in depth:
        return {'erro': 'Falha ao obter DOM'}
    
    # Calcular métricas avançadas
    bids = depth['bids']
    asks = depth['asks']
    
    # Volume total por lado
    bid_volume = sum(float(b[1]) for b in bids)
    ask_volume = sum(float(a[1]) for a in asks)
    
    # Densidade por nível
    bid_levels = len(bids)
    ask_levels = len(asks)
    
    # Spread
    best_bid = float(bids[0][0]) if bids else 0
    best_ask = float(asks[0][0]) if asks else 0
    spread = best_ask - best_bid
    spread_pct = (spread / best_bid * 100) if best_bid > 0 else 0
    
    # Paredes (níveis com > 5x volume médio)
    avg_bid_vol = bid_volume / bid_levels if bid_levels > 0 else 0
    avg_ask_vol = ask_volume / ask_levels if ask_levels > 0 else 0
    
    paredes_compra = [b for b in bids if float(b[1]) > avg_bid_vol * 5]
    paredes_venda = [a for a in asks if float(a[1]) > avg_ask_vol * 5]
    
    return {
        'symbol': symbol,
        'pressao': pressao,
        'bid_volume': bid_volume,
        'ask_volume': ask_volume,
        'ratio': bid_volume / ask_volume if ask_volume > 0 else 0,
        'spread': spread,
        'spread_pct': spread_pct,
        'paredes_compra': len(paredes_compra),
        'paredes_venda': len(paredes_venda),
        'best_bid': best_bid,
        'best_ask': best_ask
    }


def exibir_dom(resultado):
    """Exibe DOM profundo"""
    print("\n" + "="*60)
    print(f"🌊 ANÁLISE PROFUNDA DE LIQUIDEZ - {resultado['symbol']}")
    print("="*60)
    
    print(f"\n📊 BOOK DE OFERTAS:")
    print(f"   Best Bid:     ${resultado['best_bid']:,.2f}")
    print(f"   Best Ask:     ${resultado['best_ask']:,.2f}")
    print(f"   Spread:       ${resultado['spread']:.2f} ({resultado['spread_pct']:.3f}%)")
    
    print(f"\n💰 VOLUMES:")
    print(f"   Bid Volume:   {resultado['bid_volume']:,.2f}")
    print(f"   Ask Volume:   {resultado['ask_volume']:,.2f}")
    print(f"   Ratio:        {resultado['ratio']:.3f}")
    
    if 'pressao' in resultado['pressao']:
        print(f"\n⚡ PRESSÃO:")
        print(f"   Direção:      {resultado['pressao']['pressao']}")
        print(f"   Intensidade:  {resultado['pressao'].get('intensidade', 0):.0f}%")
    
    print(f"\n🧱 PAREDES DE LIQUIDEZ:")
    print(f"   Compra:       {resultado['paredes_compra']} níveis fortes")
    print(f"   Venda:        {resultado['paredes_venda']} níveis fortes")
    
    # Interpretação combinada (ratio + pressão detectada)
    ratio = resultado['ratio']
    pressao_dir = resultado['pressao'].get('pressao', 'NEUTRO')
    
    if ratio > 1.3:
        interpretacao = "🟢 Pressão de COMPRA dominante"
        recomendacao = "Favorável para LONG"
    elif ratio < 0.7:
        interpretacao = "🔴 Pressão de VENDA dominante"
        recomendacao = "Favorável para SHORT"
    elif ratio < 0.8 and pressao_dir == "VENDA":
        interpretacao = "🟠 Leve pressão de VENDA"
        recomendacao = "Cautela em LONG, considere SHORT"
    elif ratio > 1.2 and pressao_dir == "COMPRA":
        interpretacao = "🟡 Leve pressão de COMPRA"
        recomendacao = "Cautela em SHORT, considere LONG"
    else:
        interpretacao = "⚪ Mercado equilibrado"
        recomendacao = "Aguardar definição de direção"
    
    print(f"\n✨ INTERPRETAÇÃO:")
    print(f"   {interpretacao}")
    print(f"   💡 {recomendacao}")
    
    print("\n" + "="*60)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOM HEATMAP - Visualização de liquidez em heatmap
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
import os
from fluxo_ativo import FluxoAtivo


def gerar_heatmap_dom(symbol="BTCUSDT", output_dir="reports/dom/", profundidade=500):
    """
    Gera heatmap visual do DOM (Depth of Market)
    
    Args:
        symbol: Par a analisar
        output_dir: Diretório de saída
        profundidade: Número de níveis a analisar (padrão: 500, máx: 5000)
    
    Returns:
        Caminho do arquivo gerado
    """
    print(f"\n📊 Gerando heatmap DOM para {symbol}...")
    print(f"   📏 Profundidade: {profundidade} níveis por lado")
    
    # Obter dados do DOM com maior profundidade
    fluxo = FluxoAtivo()
    depth = fluxo.obter_depth(symbol, limit=min(profundidade, 5000))
    
    if not depth or 'erro' in depth:
        print("❌ Erro ao obter dados do DOM")
        return None
    
    # Usar todos os níveis disponíveis
    bids = depth['bids'][:profundidade]
    asks = depth['asks'][:profundidade]
    
    print(f"   ✅ Obtidos {len(bids)} bids e {len(asks)} asks")
    
    # Extrair preços e volumes
    bid_prices = [float(b[0]) for b in bids]
    bid_volumes = [float(b[1]) for b in bids]
    
    ask_prices = [float(a[0]) for a in asks]
    ask_volumes = [float(a[1]) for a in asks]
    
    # Agrupar níveis para visualização (mostrar 100 níveis agrupados)
    def agrupar_niveis(prices, volumes, num_grupos=100):
        """Agrupa níveis em bins para melhor visualização"""
        if len(prices) <= num_grupos:
            return prices, volumes
        
        tamanho_grupo = len(prices) // num_grupos
        prices_agrupados = []
        volumes_agrupados = []
        
        for i in range(0, len(prices), tamanho_grupo):
            grupo_prices = prices[i:i+tamanho_grupo]
            grupo_volumes = volumes[i:i+tamanho_grupo]
            
            if grupo_prices:
                prices_agrupados.append(np.mean(grupo_prices))
                volumes_agrupados.append(np.sum(grupo_volumes))
        
        return prices_agrupados, volumes_agrupados
    
    # Agrupar para visualização
    bid_prices_vis, bid_volumes_vis = agrupar_niveis(bid_prices, bid_volumes)
    ask_prices_vis, ask_volumes_vis = agrupar_niveis(ask_prices, ask_volumes)
    
    # Calcular métricas
    best_bid = bid_prices[0] if bid_prices else 0
    best_ask = ask_prices[0] if ask_prices else 0
    mid_price = (best_bid + best_ask) / 2
    
    total_bid_vol = sum(bid_volumes)
    total_ask_vol = sum(ask_volumes)
    ratio = total_bid_vol / total_ask_vol if total_ask_vol > 0 else 0
    
    # Criar figura com 3 subplots
    fig = plt.figure(figsize=(16, 12), facecolor='#0a0a0a')
    
    # Layout: [Heatmap Bids | Spread Info | Heatmap Asks]
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # ============================================================
    # SUBPLOT 1: HEATMAP DE BIDS (Esquerda)
    # ============================================================
    ax1 = fig.add_subplot(gs[0:2, 0])
    ax1.set_facecolor('#1a1a1a')
    
    # Normalizar volumes para colormap
    bid_volumes_norm = np.array(bid_volumes_vis) / max(bid_volumes_vis) if bid_volumes_vis else []
    
    # Criar barras horizontais com gradiente de cor
    colors_bid = plt.cm.Greens(bid_volumes_norm)
    
    y_positions = np.arange(len(bid_prices_vis))
    bars_bid = ax1.barh(y_positions, bid_volumes_vis, color=colors_bid, edgecolor='green', linewidth=0.5)
    
    # Configurar eixos
    ax1.set_yticks(y_positions[::10])  # Mostrar apenas alguns labels
    ax1.set_yticklabels([f"${p:,.2f}" for p in bid_prices_vis[::10]], fontsize=8, color='white')
    ax1.set_xlabel('Volume (BTC)', fontsize=10, color='white')
    ax1.set_title('🟢 BIDS (Ordens de Compra)', fontsize=12, color='white', weight='bold')
    ax1.tick_params(axis='x', colors='white', labelsize=9)
    ax1.spines['bottom'].set_color('white')
    ax1.spines['left'].set_color('white')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.invert_yaxis()  # Preços maiores no topo
    ax1.grid(axis='x', alpha=0.2, color='white')
    
    # ============================================================
    # SUBPLOT 2: HEATMAP DE ASKS (Direita)
    # ============================================================
    ax2 = fig.add_subplot(gs[0:2, 2])
    ax2.set_facecolor('#1a1a1a')
    
    # Normalizar volumes para colormap
    ask_volumes_norm = np.array(ask_volumes_vis) / max(ask_volumes_vis) if ask_volumes_vis else []
    
    # Criar barras horizontais com gradiente de cor
    colors_ask = plt.cm.Reds(ask_volumes_norm)
    
    y_positions_ask = np.arange(len(ask_prices_vis))
    bars_ask = ax2.barh(y_positions_ask, ask_volumes_vis, color=colors_ask, edgecolor='red', linewidth=0.5)
    
    # Configurar eixos
    ax2.set_yticks(y_positions_ask[::10])
    ax2.set_yticklabels([f"${p:,.2f}" for p in ask_prices_vis[::10]], fontsize=8, color='white')
    ax2.set_xlabel('Volume (BTC)', fontsize=10, color='white')
    ax2.set_title('🔴 ASKS (Ordens de Venda)', fontsize=12, color='white', weight='bold')
    ax2.tick_params(axis='x', colors='white', labelsize=9)
    ax2.spines['bottom'].set_color('white')
    ax2.spines['left'].set_color('white')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.2, color='white')
    
    # ============================================================
    # SUBPLOT 3: INFORMAÇÕES CENTRAIS (Centro)
    # ============================================================
    ax3 = fig.add_subplot(gs[0:2, 1])
    ax3.set_facecolor('#1a1a1a')
    ax3.axis('off')
    
    # Determinar pressão dominante
    if ratio > 1.3:
        pressao_cor = '#00ff00'
        pressao_texto = 'COMPRA'
        pressao_emoji = '🟢'
    elif ratio < 0.7:
        pressao_cor = '#ff0000'
        pressao_texto = 'VENDA'
        pressao_emoji = '🔴'
    else:
        pressao_cor = '#ffff00'
        pressao_texto = 'NEUTRO'
        pressao_emoji = '🟡'
    
    # Calcular range de preços analisados
    bid_range_pct = ((best_bid - bid_prices[-1]) / best_bid * 100) if bid_prices else 0
    ask_range_pct = ((ask_prices[-1] - best_ask) / best_ask * 100) if ask_prices else 0
    
    # Texto central
    info_text = f"""
    
    📊 {symbol}
    
    ━━━━━━━━━━━━━━━━━━━━━
    
    💰 PREÇO MÉDIO
    ${mid_price:,.2f}
    
    ━━━━━━━━━━━━━━━━━━━━━
    
    📈 BEST BID
    ${best_bid:,.2f}
    
    📉 BEST ASK
    ${best_ask:,.2f}
    
    📏 SPREAD
    ${best_ask - best_bid:.2f}
    
    ━━━━━━━━━━━━━━━━━━━━━
    
    📏 PROFUNDIDADE
    {len(bids)} níveis
    Range: ±{max(bid_range_pct, ask_range_pct):.2f}%
    
    ━━━━━━━━━━━━━━━━━━━━━
    
    🟢 BID VOLUME
    {total_bid_vol:.2f} BTC
    
    🔴 ASK VOLUME
    {total_ask_vol:.2f} BTC
    
    ⚖️ RATIO
    {ratio:.3f}
    
    ━━━━━━━━━━━━━━━━━━━━━
    
    {pressao_emoji} PRESSÃO
    {pressao_texto}
    
    """
    
    ax3.text(
        0.5, 0.5,
        info_text,
        transform=ax3.transAxes,
        fontsize=11,
        color='white',
        ha='center',
        va='center',
        family='monospace',
        weight='bold',
        bbox=dict(boxstyle='round,pad=1', facecolor='#1a1a1a', edgecolor=pressao_cor, linewidth=2)
    )
    
    # ============================================================
    # SUBPLOT 4: GRÁFICO DE VOLUME CUMULATIVO (Inferior)
    # ============================================================
    ax4 = fig.add_subplot(gs[2, :])
    ax4.set_facecolor('#1a1a1a')
    
    # Calcular volume cumulativo
    bid_cumulative = np.cumsum(bid_volumes[::-1])[::-1]  # Inverter para ordem correta
    ask_cumulative = np.cumsum(ask_volumes)
    
    # Plotar
    ax4.fill_between(bid_prices, 0, bid_cumulative, color='green', alpha=0.3, label='Bid Cumulative')
    ax4.plot(bid_prices, bid_cumulative, color='green', linewidth=2)
    
    ax4.fill_between(ask_prices, 0, ask_cumulative, color='red', alpha=0.3, label='Ask Cumulative')
    ax4.plot(ask_prices, ask_cumulative, color='red', linewidth=2)
    
    # Linha vertical no preço médio
    ax4.axvline(x=mid_price, color='yellow', linestyle='--', linewidth=2, alpha=0.7, label=f'Mid: ${mid_price:,.2f}')
    
    ax4.set_xlabel('Preço (USDT)', fontsize=10, color='white')
    ax4.set_ylabel('Volume Cumulativo (BTC)', fontsize=10, color='white')
    ax4.set_title('📊 PROFUNDIDADE DE MERCADO (Cumulative)', fontsize=12, color='white', weight='bold')
    ax4.tick_params(axis='both', colors='white', labelsize=9)
    ax4.spines['bottom'].set_color('white')
    ax4.spines['left'].set_color('white')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.grid(alpha=0.2, color='white')
    ax4.legend(loc='upper left', fontsize=9, facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
    
    # ============================================================
    # TÍTULO PRINCIPAL
    # ============================================================
    timestamp_grafico = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    fig.suptitle(
        f'SNE RADAR - HEATMAP DOM - {symbol}',
        fontsize=18,
        color='white',
        weight='bold',
        y=0.98
    )
    
    # Subtítulo
    fig.text(
        0.5, 0.95,
        f'Análise de Liquidez | {timestamp_grafico}',
        ha='center',
        fontsize=12,
        color='white',
        weight='bold'
    )
    
    # Marca d'água
    fig.text(
        0.98, 0.02,
        'SNE RADAR',
        ha='right',
        va='bottom',
        fontsize=10,
        color='white',
        alpha=0.3,
        style='italic'
    )
    
    # Salvar
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}{symbol}_{timestamp}_dom_heatmap.png"
    
    plt.savefig(
        filename,
        dpi=150,
        bbox_inches='tight',
        facecolor='#0a0a0a',
        edgecolor='white',
        pad_inches=0.2
    )
    plt.close()
    
    print(f"✅ Heatmap DOM salvo: {filename}")
    
    return filename


if __name__ == "__main__":
    # Teste
    gerar_heatmap_dom("BTCUSDT")


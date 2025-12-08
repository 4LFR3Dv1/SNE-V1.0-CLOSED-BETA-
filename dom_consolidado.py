#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOM CONSOLIDADO - Heatmap de liquidez para múltiplos pares
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import warnings
import requests

# Suprimir warnings
warnings.filterwarnings('ignore', category=UserWarning)


def gerar_heatmap_dom_consolidado(pares, output_dir="reports/auto/"):
    """
    Gera heatmap consolidado de DOM para múltiplos pares
    
    Args:
        pares: Lista de symbols ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        output_dir: Diretório de saída
    
    Returns:
        Caminho do arquivo gerado
    """
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Coletar dados de DOM para cada par
    dados_dom = {}
    
    for symbol in pares:
        try:
            url = "https://api.binance.com/api/v3/depth"
            params = {"symbol": symbol, "limit": 100}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                depth = response.json()
                
                # Calcular pressão
                bid_volume = sum([float(b[1]) for b in depth['bids']])
                ask_volume = sum([float(a[1]) for a in depth['asks']])
                total = bid_volume + ask_volume
                
                bid_pct = (bid_volume / total * 100) if total > 0 else 50
                ask_pct = (ask_volume / total * 100) if total > 0 else 50
                
                dados_dom[symbol] = {
                    'bid_pct': bid_pct,
                    'ask_pct': ask_pct,
                    'ratio': bid_volume / ask_volume if ask_volume > 0 else 1.0
                }
        except:
            dados_dom[symbol] = {
                'bid_pct': 50,
                'ask_pct': 50,
                'ratio': 1.0
            }
    
    # Criar visualização
    fig = plt.figure(figsize=(12, 6))
    fig.patch.set_facecolor('#0a0a0a')
    
    # Configurar subplot
    ax = plt.subplot(111)
    ax.set_facecolor('#0a0a0a')
    
    # Preparar dados para heatmap
    labels = [symbol.replace('USDT', '') for symbol in pares]
    bid_values = [dados_dom[symbol]['bid_pct'] for symbol in pares]
    ask_values = [dados_dom[symbol]['ask_pct'] for symbol in pares]
    
    # Posições das barras
    x = np.arange(len(labels))
    width = 0.6
    
    # Criar barras empilhadas
    p1 = ax.barh(x, bid_values, width, color='#00ff00', alpha=0.7, label='BIDs (Compra)')
    p2 = ax.barh(x, ask_values, width, left=bid_values, color='#ff0000', alpha=0.7, label='ASKs (Venda)')
    
    # Adicionar linha de equilíbrio (50%)
    ax.axvline(x=50, color='white', linestyle='--', linewidth=1, alpha=0.3)
    
    # Adicionar valores nas barras
    for i, (bid, ask) in enumerate(zip(bid_values, ask_values)):
        # Valor BID
        ax.text(bid/2, i, f'{bid:.1f}%', ha='center', va='center', 
               color='white', fontsize=10, weight='bold')
        # Valor ASK
        ax.text(bid + ask/2, i, f'{ask:.1f}%', ha='center', va='center',
               color='white', fontsize=10, weight='bold')
        
        # Ratio ao lado
        ratio = dados_dom[pares[i]]['ratio']
        if ratio > 1.1:
            ratio_text = f"📈 {ratio:.2f}x"
            color = '#00ff00'
        elif ratio < 0.9:
            ratio_text = f"📉 {ratio:.2f}x"
            color = '#ff0000'
        else:
            ratio_text = f"➡️ {ratio:.2f}x"
            color = '#ffaa00'
        
        ax.text(102, i, ratio_text, ha='left', va='center',
               color=color, fontsize=9, weight='bold')
    
    # Configurar eixos
    ax.set_yticks(x)
    ax.set_yticklabels(labels, color='white', fontsize=12, weight='bold')
    ax.set_xlim(0, 100)
    ax.set_xlabel('Distribuição de Liquidez (%)', color='white', fontsize=11)
    
    # Remover spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(colors='white')
    
    # Título
    timestamp = datetime.now().strftime('%H:%M')
    fig.suptitle(f'SNE RADAR - HEATMAP DE LIQUIDEZ (DOM)\n{timestamp}', 
                color='white', fontsize=14, weight='bold', y=0.98)
    
    # Legenda
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), 
             ncol=2, facecolor='#1a1a1a', edgecolor='white', 
             labelcolor='white', fontsize=10)
    
    # Salvar
    filename = f"dom_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', 
               facecolor='#0a0a0a', edgecolor='none')
    plt.close()
    
    print(f"✅ Heatmap DOM salvo: {filepath}")
    return filepath


if __name__ == "__main__":
    # Teste
    pares = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    gerar_heatmap_dom_consolidado(pares)





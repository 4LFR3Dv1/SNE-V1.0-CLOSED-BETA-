#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MULTI-PAIR VISUAL - Visualização comparativa de múltiplos pares
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
import os
import sys
import io
import warnings

# Suprimir warnings de emojis ausentes
warnings.filterwarnings('ignore', category=UserWarning, message='.*Glyph.*missing from font.*')


def gerar_visual_multi_pair(dados_pares, timeframe='1h', output_dir="reports/multi_pair/"):
    """
    Gera visualização comparativa de múltiplos pares
    
    Args:
        dados_pares: Lista de dicts com dados dos pares
        timeframe: Timeframe analisado
        output_dir: Diretório de saída
    
    Returns:
        Caminho do arquivo gerado
    """
    print(f"\n📊 Gerando visualização comparativa...")
    
    if not dados_pares:
        print("❌ Nenhum dado disponível")
        return None
    
    # Ordenar por confluência
    dados_pares = sorted(dados_pares, key=lambda x: x.get('confluencia', 0), reverse=True)
    
    # Criar figura com múltiplos painéis
    fig = plt.figure(figsize=(18, 12), facecolor='#0a0a0a')
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # ============================================================
    # PAINEL 1: RANKING DE CONFLUÊNCIA (Barras Horizontais)
    # ============================================================
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_facecolor('#1a1a1a')
    
    symbols = [d['symbol'].replace('USDT', '') for d in dados_pares]
    confluencias = [d.get('confluencia', 0) for d in dados_pares]
    
    # Cores baseadas na confluência
    cores = ['#00ff00' if c >= 7 else '#ffff00' if c >= 5 else '#ff0000' for c in confluencias]
    
    bars = ax1.barh(symbols, confluencias, color=cores, edgecolor='white', linewidth=1.5)
    
    # Adicionar valores nas barras
    for i, (bar, val) in enumerate(zip(bars, confluencias)):
        ax1.text(val + 0.2, bar.get_y() + bar.get_height()/2, 
                f'{val:.1f}', va='center', color='white', fontsize=10, weight='bold')
    
    # Linhas de referência
    ax1.axvline(x=5, color='yellow', linestyle='--', alpha=0.3, linewidth=1)
    ax1.axvline(x=7, color='green', linestyle='--', alpha=0.3, linewidth=1)
    
    ax1.set_xlabel('Confluência (0-10)', color='white', fontsize=11)
    ax1.set_title('🏆 RANKING DE CONFLUÊNCIA', color='white', fontsize=14, weight='bold', pad=10)
    ax1.tick_params(axis='both', colors='white', labelsize=10)
    ax1.spines['bottom'].set_color('white')
    ax1.spines['left'].set_color('white')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='x', alpha=0.2, color='white')
    ax1.set_xlim(0, 10)
    
    # ============================================================
    # PAINEL 2: MELHOR SETUP (Destaque)
    # ============================================================
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_facecolor('#1a1a1a')
    ax2.axis('off')
    
    melhor = dados_pares[0]
    
    melhor_text = f"""
    🏆 MELHOR SETUP
    
    ━━━━━━━━━━━━━━━━━
    
    {melhor['symbol'].replace('USDT', '')}
    
    Score: {melhor.get('confluencia', 0):.1f}/10
    
    Viés: {melhor.get('vies', 'N/A')}
    
    ━━━━━━━━━━━━━━━━━
    
    {melhor.get('recomendacao', 'AGUARDAR')}
    """
    
    cor_melhor = '#00ff00' if melhor.get('confluencia', 0) >= 7 else '#ffff00'
    
    ax2.text(
        0.5, 0.5,
        melhor_text,
        transform=ax2.transAxes,
        fontsize=12,
        color='white',
        ha='center',
        va='center',
        family='monospace',
        weight='bold',
        bbox=dict(boxstyle='round,pad=1', facecolor='#1a1a1a', edgecolor=cor_melhor, linewidth=3)
    )
    
    # ============================================================
    # PAINEL 3: RADAR CHART (Comparação Multi-Dimensional)
    # ============================================================
    ax3 = fig.add_subplot(gs[1, :], projection='polar')
    ax3.set_facecolor('#1a1a1a')
    
    # Categorias
    categorias = ['Confluência', 'Volatilidade', 'Liquidez', 'Força Regime', 'Volume']
    num_vars = len(categorias)
    
    # Ângulos para cada categoria
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Fechar o círculo
    
    # Plotar top 3 pares
    cores_radar = ['#00ff00', '#ffff00', '#ff8800']
    
    for i, par in enumerate(dados_pares[:3]):
        valores = [
            par.get('confluencia', 0) / 10,  # Normalizar para 0-1
            min(par.get('volatilidade', 0) / 5, 1),  # Normalizar
            par.get('liquidez', 0) / 10,
            par.get('forca_regime', 0) / 10,
            min(par.get('volume_24h', 0) / 5e9, 1)  # Normalizar volume
        ]
        valores += valores[:1]  # Fechar o círculo
        
        ax3.plot(angles, valores, 'o-', linewidth=2, color=cores_radar[i], 
                label=par['symbol'].replace('USDT', ''))
        ax3.fill(angles, valores, alpha=0.15, color=cores_radar[i])
    
    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(categorias, color='white', fontsize=10)
    ax3.set_ylim(0, 1)
    ax3.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax3.set_yticklabels(['2', '4', '6', '8', '10'], color='white', fontsize=8)
    ax3.grid(color='white', alpha=0.3)
    ax3.set_title('📊 COMPARAÇÃO MULTI-DIMENSIONAL (Top 3)', 
                  color='white', fontsize=14, weight='bold', pad=20)
    ax3.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), 
              fontsize=10, facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
    
    # ============================================================
    # PAINEL 4: DISTRIBUIÇÃO DE VIÉS (Pizza)
    # ============================================================
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.set_facecolor('#1a1a1a')
    
    # Contar vieses
    vieses_count = {}
    for d in dados_pares:
        vies = d.get('vies', 'INDEFINIDO')
        # Simplificar viés
        if 'BULL' in vies or 'COMPRA' in vies:
            vies_simples = 'COMPRA'
        elif 'BEAR' in vies or 'VENDA' in vies:
            vies_simples = 'VENDA'
        else:
            vies_simples = 'NEUTRO'
        
        vieses_count[vies_simples] = vieses_count.get(vies_simples, 0) + 1
    
    cores_vies = {
        'COMPRA': '#00ff00',
        'VENDA': '#ff0000',
        'NEUTRO': '#ffff00'
    }
    
    labels = list(vieses_count.keys())
    sizes = list(vieses_count.values())
    colors = [cores_vies.get(v, '#888888') for v in labels]
    
    wedges, texts, autotexts = ax4.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.0f%%',
        startangle=90,
        textprops={'color': 'white', 'weight': 'bold', 'fontsize': 11}
    )
    
    ax4.set_title('📊 DISTRIBUIÇÃO DE VIÉS', color='white', fontsize=12, weight='bold', pad=10)
    
    # ============================================================
    # PAINEL 5: VOLATILIDADE vs VOLUME (Scatter)
    # ============================================================
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.set_facecolor('#1a1a1a')
    
    volatilidades = [d.get('volatilidade', 0) for d in dados_pares]
    volumes = [d.get('volume_24h', 0) / 1e9 for d in dados_pares]  # Em bilhões
    
    # Cores por confluência
    cores_scatter = ['#00ff00' if d.get('confluencia', 0) >= 7 else 
                    '#ffff00' if d.get('confluencia', 0) >= 5 else '#ff0000' 
                    for d in dados_pares]
    
    scatter = ax5.scatter(
        volatilidades,
        volumes,
        s=300,
        c=cores_scatter,
        alpha=0.7,
        edgecolors='white',
        linewidths=2
    )
    
    # Adicionar labels
    for i, d in enumerate(dados_pares):
        ax5.annotate(
            d['symbol'].replace('USDT', ''),
            (volatilidades[i], volumes[i]),
            color='white',
            fontsize=9,
            ha='center',
            va='center',
            weight='bold'
        )
    
    ax5.set_xlabel('Volatilidade (%)', color='white', fontsize=10)
    ax5.set_ylabel('Volume 24h ($B)', color='white', fontsize=10)
    ax5.set_title('📈 VOLATILIDADE vs VOLUME', color='white', fontsize=12, weight='bold', pad=10)
    ax5.tick_params(axis='both', colors='white', labelsize=9)
    ax5.spines['bottom'].set_color('white')
    ax5.spines['left'].set_color('white')
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)
    ax5.grid(alpha=0.2, color='white')
    
    # ============================================================
    # PAINEL 6: RECOMENDAÇÕES (Tabela)
    # ============================================================
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.set_facecolor('#1a1a1a')
    ax6.axis('off')
    
    recom_text = "📋 RECOMENDAÇÕES\n"
    recom_text += "━" * 30 + "\n\n"
    
    for i, d in enumerate(dados_pares, 1):
        emoji = '🟢' if d.get('confluencia', 0) >= 7 else '🟡' if d.get('confluencia', 0) >= 5 else '🔴'
        recom_text += f"{emoji} #{i} {d['symbol'].replace('USDT', ''):6s}\n"
        recom_text += f"   {d.get('recomendacao', 'AGUARDAR')[:20]}\n\n"
    
    ax6.text(
        0.5, 0.5,
        recom_text,
        transform=ax6.transAxes,
        fontsize=9,
        color='white',
        ha='center',
        va='center',
        family='monospace',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#1a1a1a', edgecolor='white', linewidth=2)
    )
    
    # ============================================================
    # TÍTULO PRINCIPAL
    # ============================================================
    timestamp_grafico = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    fig.suptitle(
        f'SNE RADAR - ANÁLISE MULTI-PAIR ({timeframe})',
        fontsize=18,
        color='white',
        weight='bold',
        y=0.98
    )
    
    fig.text(
        0.5, 0.95,
        f'{len(dados_pares)} pares analisados | {timestamp_grafico}',
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
    filename = f"{output_dir}multi_pair_{timeframe}_{timestamp}.png"
    
    plt.savefig(
        filename,
        dpi=150,
        bbox_inches='tight',
        facecolor='#0a0a0a',
        edgecolor='white',
        pad_inches=0.2
    )
    plt.close()
    
    print(f"✅ Visualização salva: {filename}")
    
    return filename


if __name__ == "__main__":
    # Teste
    dados_teste = [
        {'symbol': 'BTCUSDT', 'confluencia': 8.5, 'vies': 'BULL_TREND', 'recomendacao': 'COMPRAR', 
         'volatilidade': 2.1, 'liquidez': 9, 'forca_regime': 8, 'volume_24h': 3e9},
        {'symbol': 'ETHUSDT', 'confluencia': 7.2, 'vies': 'CONSOLIDATION', 'recomendacao': 'AGUARDAR',
         'volatilidade': 1.8, 'liquidez': 8, 'forca_regime': 6, 'volume_24h': 2.5e9},
    ]
    gerar_visual_multi_pair(dados_teste)


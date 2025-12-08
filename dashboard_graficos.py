#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD GRÁFICOS - Visualizações profissionais dos relatórios
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo
plt.style.use('dark_background')
sns.set_palette("husl")


def gerar_grafico_confluencia(dados_ciclo, pares, ciclo_num):
    """Gráfico de barras horizontal - Direção das ondas"""
    
    fig, axes = plt.subplots(len(pares), 1, figsize=(12, 8))
    if len(pares) == 1:
        axes = [axes]
    
    tfs = ['1m', '5m', '15m', '30m']
    tipos = {'1m': 'SCALP', '5m': 'SCALP', '15m': 'DAY', '30m': 'INTRA'}
    
    for idx, par in enumerate(pares):
        par_nome = par.replace('USDT', '')
        ax = axes[idx]
        
        direcoes = []
        cores = []
        labels = []
        
        for tf in tfs:
            if tf in dados_ciclo and par in dados_ciclo[tf]:
                forca = dados_ciclo[tf][par]['forca']
                
                if '↑' in forca:
                    direcoes.append(1)
                    # Determinar intensidade da cor verde
                    if 'FORTE' in forca:
                        cores.append('#00ff00')  # Verde forte
                    elif 'MODERADA' in forca:
                        cores.append('#90ee90')  # Verde médio
                    else:
                        cores.append('#adff2f')  # Verde fraco
                elif '↓' in forca:
                    direcoes.append(-1)
                    # Determinar intensidade da cor vermelha
                    if 'FORTE' in forca:
                        cores.append('#ff0000')  # Vermelho forte
                    elif 'MODERADA' in forca:
                        cores.append('#ff6b6b')  # Vermelho médio
                    else:
                        cores.append('#ff9999')  # Vermelho fraco
                else:
                    direcoes.append(0)
                    cores.append('#808080')  # Cinza neutro
                
                labels.append(f"{tf.upper()} ({tipos[tf]})")
        
        # Plotar barras
        y_pos = np.arange(len(labels))
        bars = ax.barh(y_pos, direcoes, color=cores, edgecolor='white', linewidth=1)
        
        # Configurar eixos
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10, color='white')
        ax.set_xlim(-1.5, 1.5)
        ax.set_xlabel('Direção', fontsize=10, color='white')
        ax.axvline(0, color='white', linewidth=1, linestyle='--', alpha=0.5)
        
        # Adicionar símbolos
        for i, (d, c) in enumerate(zip(direcoes, cores)):
            if d > 0:
                ax.text(d + 0.1, i, '↑', fontsize=14, va='center', color=c)
            elif d < 0:
                ax.text(d - 0.1, i, '↓', fontsize=14, va='center', color=c, ha='right')
            else:
                ax.text(0, i, '↔', fontsize=14, va='center', color=c, ha='center')
        
        # Calcular confluência
        alta_count = sum(1 for d in direcoes if d > 0)
        baixa_count = sum(1 for d in direcoes if d < 0)
        
        if alta_count >= 3:
            confluencia_str = f"✅ ALTA CONFIRMADA ({alta_count}/4 ↑)"
            confluencia_cor = '#00ff00'
        elif baixa_count >= 3:
            confluencia_str = f"✅ BAIXA CONFIRMADA ({baixa_count}/4 ↓)"
            confluencia_cor = '#ff0000'
        elif alta_count == baixa_count:
            confluencia_str = f"⚠️ DIVERGÊNCIA ({alta_count}↑ vs {baixa_count}↓)"
            confluencia_cor = '#ffff00'
        else:
            tendencia = "ALTA" if alta_count > baixa_count else "BAIXA"
            confluencia_str = f"📊 {tendencia} MODERADA"
            confluencia_cor = '#ffa500'
        
        ax.set_title(f"{par_nome} - Confluência Multi-TF | {confluencia_str}", 
                    fontsize=12, color=confluencia_cor, fontweight='bold', pad=10)
        ax.grid(axis='x', alpha=0.3)
    
    fig.suptitle(f'🌊 CONFLUÊNCIA MULTI-TIMEFRAME - Ciclo #{ciclo_num}', 
                fontsize=16, color='white', fontweight='bold', y=0.98)
    
    plt.tight_layout()
    filepath = f'reports/dashboard/confluencia_ciclo_{ciclo_num}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    
    return filepath


def gerar_heatmap_scores(dados_ciclo, pares, ciclo_num):
    """Heatmap de scores por TF e Par"""
    
    tfs = ['1m', '5m', '15m', '30m']
    scores_matrix = []
    
    for par in pares:
        row = []
        for tf in tfs:
            if tf in dados_ciclo and par in dados_ciclo[tf]:
                score = float(dados_ciclo[tf][par]['score'])
                row.append(score)
            else:
                row.append(0)
        scores_matrix.append(row)
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Criar heatmap
    im = ax.imshow(scores_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=10)
    
    # Configurar eixos
    ax.set_xticks(np.arange(len(tfs)))
    ax.set_yticks(np.arange(len(pares)))
    ax.set_xticklabels(tfs, fontsize=12, color='white')
    ax.set_yticklabels([p.replace('USDT', '') for p in pares], fontsize=12, color='white')
    
    # Adicionar valores nas células
    for i in range(len(pares)):
        for j in range(len(tfs)):
            score = scores_matrix[i][j]
            text_color = 'black' if score > 5 else 'white'
            text = ax.text(j, i, f'{score:.1f}', ha="center", va="center", 
                          color=text_color, fontsize=14, fontweight='bold')
    
    # Adicionar média por linha
    for i, row in enumerate(scores_matrix):
        media = np.mean(row)
        emoji = '🟢' if media >= 7.5 else '🟡' if media >= 6 else '🔴'
        ax.text(len(tfs) + 0.3, i, f'{media:.1f} {emoji}', 
               va='center', fontsize=12, color='white', fontweight='bold')
    
    # Título e labels
    ax.set_xlabel('Timeframe', fontsize=12, color='white', fontweight='bold')
    ax.set_ylabel('Par', fontsize=12, color='white', fontweight='bold')
    ax.set_title(f'📊 HEATMAP DE SCORES MULTI-TIMEFRAME - Ciclo #{ciclo_num}', 
                fontsize=14, color='white', fontweight='bold', pad=15)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, pad=0.1)
    cbar.set_label('Score (0-10)', rotation=270, labelpad=20, color='white', fontsize=10)
    cbar.ax.tick_params(colors='white')
    
    # Legenda
    legend_elements = [
        mpatches.Patch(color='#00ff00', label='🟢 Alto (≥7.5)'),
        mpatches.Patch(color='#ffff00', label='🟡 Médio (6-7.5)'),
        mpatches.Patch(color='#ff0000', label='🔴 Baixo (<6)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.15, 1), 
             framealpha=0.9, facecolor='#1a1a1a', edgecolor='white')
    
    plt.tight_layout()
    filepath = f'reports/dashboard/heatmap_ciclo_{ciclo_num}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    
    return filepath


# FUNÇÃO REMOVIDA - Substituída por gerar_niveis_sr_unificados()
# def gerar_scatter_sr(dados_ciclo, par, ciclo_num):
#     """Scatter plot de níveis S/R - REMOVIDA"""
#     pass


# FUNÇÃO REMOVIDA - Substituída por gerar_medidores_unificados()
# def gerar_gauge_confluencia(dados_ciclo, par, ciclo_num):
#     """Gauge/medidor de confluência - REMOVIDA"""
#     pass
    


# FUNÇÃO REMOVIDA - Substituída por gráficos unificados
# def gerar_painel_combinado(dados_ciclo, pares, ciclo_num):
#     """Painel multi-gráfico 4-in-1 - REMOVIDA"""
#     pass
    


# FUNÇÕES AUXILIARES REMOVIDAS - Não mais necessárias com gráficos unificados
# def gerar_confluencia_subplot(ax, dados_ciclo, pares):
# def gerar_heatmap_subplot(ax, dados_ciclo, pares):
# def gerar_sr_subplot(ax, dados_ciclo, par):
# def gerar_radar_subplot(ax, dados_ciclo, par):








def gerar_medidores_unificados(dados_ciclo, pares, ciclo_num):
    """Gera gráfico unificado com medidores de todos os pares"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'🎛️ MEDIDORES UNIFICADOS - CICLO #{ciclo_num}', 
                fontsize=16, color='white', fontweight='bold')
    
    # Cores para cada par
    cores_pares = {
        'BTCUSDT': '#f7931a',
        'ETHUSDT': '#627eea', 
        'SOLUSDT': '#9945ff',
        'ADAUSDT': '#0033ad',
        'DOTUSDT': '#e6007a'
    }
    
    for idx, par in enumerate(pares):
        if idx >= 4:  # Máximo 4 pares
            break
            
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        par_nome = par.replace('USDT', '')
        cor_par = cores_pares.get(par, '#ffffff')
        
        # Coletar dados do último timeframe (30m)
        dados_par = None
        if '30m' in dados_ciclo and par in dados_ciclo['30m']:
            dados_par = dados_ciclo['30m'][par]
        elif '15m' in dados_ciclo and par in dados_ciclo['15m']:
            dados_par = dados_ciclo['15m'][par]
        elif '5m' in dados_ciclo and par in dados_ciclo['5m']:
            dados_par = dados_ciclo['5m'][par]
        
        if dados_par:
            # Criar gauge circular
            score = float(dados_par['score'])
            forca = dados_par['forca']
            estado = dados_par['estado']
            preco = dados_par['preco']
            
            # Ângulos para o gauge
            theta = np.linspace(0, np.pi, 100)
            r_inner = 0.5
            r_outer = 1.0
            
            # Fundo do gauge
            ax.fill_between(theta, r_inner, r_outer, alpha=0.3, color='gray')
            
            # Score atual (arco colorido)
            score_angle = (score / 10) * np.pi
            theta_score = np.linspace(0, score_angle, 50)
            
            # Cor baseada no score
            if score >= 7.5:
                cor_score = '#00ff00'  # Verde
            elif score >= 6.0:
                cor_score = '#ffff00'  # Amarelo
            else:
                cor_score = '#ff4444'  # Vermelho
            
            ax.fill_between(theta_score, r_inner, r_outer, alpha=0.8, color=cor_score)
            
            # Linha do score atual
            ax.plot([score_angle, score_angle], [r_inner, r_outer], 
                   color='white', linewidth=3, alpha=0.9)
            
            # Texto central
            ax.text(0, 0, f'{score:.1f}', ha='center', va='center', 
                   fontsize=24, fontweight='bold', color='white')
            
            # Informações do par
            ax.text(0, -0.3, f'{par_nome}', ha='center', va='center',
                   fontsize=14, fontweight='bold', color=cor_par)
            
            ax.text(0, -0.5, f'${preco:,.0f}', ha='center', va='center',
                   fontsize=12, color='white')
            
            # Estado e força
            ax.text(0, -0.7, f'{estado}', ha='center', va='center',
                   fontsize=10, color='white')
            
            ax.text(0, -0.85, f'{forca}', ha='center', va='center',
                   fontsize=9, color='white')
        
        # Configurar subplot
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
    
    # Remover subplots vazios se necessário
    for idx in range(len(pares), 4):
        row = idx // 2
        col = idx % 2
        axes[row, col].axis('off')
    
    plt.tight_layout()
    
    filepath = f'reports/dashboard/medidores_unificados_ciclo_{ciclo_num}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    
    return filepath


def gerar_niveis_sr_unificados(dados_ciclo, pares, ciclo_num):
    """Gera gráfico unificado com níveis S/R de todos os pares"""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'🎯 NÍVEIS S/R UNIFICADOS - CICLO #{ciclo_num}', 
                fontsize=16, color='white', fontweight='bold')
    
    tfs = ['1m', '5m', '15m', '30m']
    
    for idx, par in enumerate(pares):
        if idx >= 4:  # Máximo 4 pares
            break
            
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        par_nome = par.replace('USDT', '')
        preco_atual = None
        niveis_r = []
        niveis_s = []
        
        # Coletar níveis
        for tf_idx, tf in enumerate(tfs):
            if tf in dados_ciclo and par in dados_ciclo[tf]:
                dados = dados_ciclo[tf][par]
                preco_atual = dados['preco']
                
                try:
                    r_str = dados['resistencia']
                    s_str = dados['suporte']
                    
                    r_val = float(r_str.split('$')[1].split()[0].replace(',', ''))
                    s_val = float(s_str.split('$')[1].split()[0].replace(',', ''))
                    
                    # Plotar resistência (vermelho)
                    size = 80 + (tf_idx * 20)
                    ax.scatter(tf_idx, r_val, color='#ff4444', s=size, alpha=0.8, 
                              edgecolors='white', linewidth=1.5, zorder=3)
                    
                    # Plotar suporte (verde)
                    ax.scatter(tf_idx, s_val, color='#44ff44', s=size, alpha=0.8, 
                              edgecolors='white', linewidth=1.5, zorder=3)
                    
                    # Labels dos níveis
                    ax.text(tf_idx + 0.1, r_val, f"{tf.upper()}\n{r_str.split('(')[1].strip(')')}", 
                           fontsize=8, color='#ff4444', va='center')
                    ax.text(tf_idx + 0.1, s_val, f"{tf.upper()}\n{s_str.split('(')[1].strip(')')}", 
                           fontsize=8, color='#44ff44', va='center')
                    
                    niveis_r.append(r_val)
                    niveis_s.append(s_val)
                except:
                    continue
        
        # Linha do preço atual
        if preco_atual:
            ax.axhline(preco_atual, color='#00bfff', linewidth=2, linestyle='--', 
                      label=f'Preço: ${preco_atual:,.0f}', zorder=2)
            
            # Zonas de decisão
            if niveis_r and niveis_s:
                r_min = min(niveis_r)
                s_max = max(niveis_s)
                
                # Zona de resistência
                ax.axhspan(preco_atual, r_min, alpha=0.15, color='red', zorder=1)
                # Zona de suporte
                ax.axhspan(s_max, preco_atual, alpha=0.15, color='green', zorder=1)
        
        # Configurar eixos
        ax.set_xticks(range(len(tfs)))
        ax.set_xticklabels([f"{tf}\n{['SCALP','SCALP','DAY','INTRA'][i]}" 
                            for i, tf in enumerate(tfs)], fontsize=9, color='white')
        ax.set_xlabel('Timeframe', fontsize=10, color='white')
        ax.set_ylabel('Preço ($)', fontsize=10, color='white')
        ax.tick_params(colors='white')
        
        # Título do subplot
        ax.set_title(f'{par_nome}', fontsize=12, color='white', fontweight='bold')
        
        # Legenda simplificada
        legend_elements = [
            mpatches.Patch(color='#ff4444', label='R'),
            mpatches.Patch(color='#44ff44', label='S'),
            mpatches.Patch(color='#00bfff', label='Preço')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=8, 
                 framealpha=0.9, facecolor='#1a1a1a', edgecolor='white')
        
        ax.grid(axis='y', alpha=0.3, color='white', linestyle='--')
    
    # Remover subplots vazios se necessário
    for idx in range(len(pares), 4):
        row = idx // 2
        col = idx % 2
        axes[row, col].axis('off')
    
    plt.tight_layout()
    
    filepath = f'reports/dashboard/niveis_sr_unificados_ciclo_{ciclo_num}.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    
    return filepath


def gerar_todos_graficos(dados_ciclo, pares, ciclo_num):
    """Gera todos os gráficos unificados e retorna lista de filepaths"""
    
    import os
    os.makedirs('reports/dashboard', exist_ok=True)
    
    graficos = []
    
    print(f"\n📊 Gerando gráficos unificados do Ciclo #{ciclo_num}...")
    
    # 1. Confluência Multi-TF
    print("   1️⃣ Confluência Multi-TF...")
    graficos.append(gerar_grafico_confluencia(dados_ciclo, pares, ciclo_num))
    
    # 2. Heatmap de Scores
    print("   2️⃣ Heatmap de Scores...")
    graficos.append(gerar_heatmap_scores(dados_ciclo, pares, ciclo_num))
    
    # 3. Medidores Unificados (substitui gauges individuais)
    print("   3️⃣ Medidores Unificados...")
    graficos.append(gerar_medidores_unificados(dados_ciclo, pares, ciclo_num))
    
    # 4. Níveis S/R Unificados (substitui S/R individuais)
    print("   4️⃣ Níveis S/R Unificados...")
    graficos.append(gerar_niveis_sr_unificados(dados_ciclo, pares, ciclo_num))
    
    print(f"   ✅ {len(graficos)} gráficos unificados gerados!\n")
    
    return graficos



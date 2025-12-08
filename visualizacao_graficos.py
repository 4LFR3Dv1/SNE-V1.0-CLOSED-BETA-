#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISUALIZAÇÃO GRÁFICA - SNE RADAR
Gera relatórios visuais profissionais a partir das análises
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
from datetime import datetime
import os


class VisualizadorGrafico:
    """Classe para gerar relatórios visuais"""
    
    def __init__(self):
        self.figsize = (16, 10)
        self.style = 'dark_background'
        self.output_dir = 'reports/graficos/'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def gerar_relatorio_completo(self, resultado_motor_renan, symbol, timeframe):
        """
        Gera relatório visual completo do Motor Renan
        
        Args:
            resultado_motor_renan: dict com análise completa
            symbol: Par analisado
            timeframe: Timeframe usado
        """
        plt.style.use(self.style)
        
        # Criar figura com grid
        fig = plt.figure(figsize=self.figsize)
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. GRÁFICO PRINCIPAL - Confluência e Score
        ax1 = fig.add_subplot(gs[0, :2])
        self._plot_confluencia(ax1, resultado_motor_renan)
        
        # 2. GAUGE - Score de Confiança
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_gauge_score(ax2, resultado_motor_renan['confluencia']['score'])
        
        # 3. MULTI-TIMEFRAME
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_multi_timeframe(ax3, resultado_motor_renan.get('mtf', {}))
        
        # 4. ESTRUTURA DE MERCADO
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_estrutura(ax4, resultado_motor_renan.get('estrutura', {}))
        
        # 5. FLUXO DOM
        ax5 = fig.add_subplot(gs[1, 2])
        self._plot_fluxo_dom(ax5, resultado_motor_renan.get('fluxo', {}))
        
        # 6. INDICADORES
        ax6 = fig.add_subplot(gs[2, 0])
        self._plot_indicadores(ax6, resultado_motor_renan.get('indicadores', {}))
        
        # 7. CONTEXTO
        ax7 = fig.add_subplot(gs[2, 1])
        self._plot_contexto(ax7, resultado_motor_renan.get('contexto', {}))
        
        # 8. SÍNTESE (TEXTO)
        ax8 = fig.add_subplot(gs[2, 2])
        self._plot_sintese(ax8, resultado_motor_renan.get('sintese', {}))
        
        # Título geral
        fig.suptitle(f'📊 RELATÓRIO TÉCNICO COMPLETO - {symbol} | {timeframe}', 
                     fontsize=20, fontweight='bold', color='#00D9FF')
        
        # Salvar
        filename = f"{self.output_dir}{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close()
        
        return filename
    
    def _plot_confluencia(self, ax, resultado):
        """Gráfico de barras de confluência por camada"""
        validacoes = resultado['confluencia'].get('validacoes', [])
        
        if not validacoes:
            ax.text(0.5, 0.5, 'Sem dados de confluência', 
                   ha='center', va='center', fontsize=12, color='gray')
            ax.axis('off')
            return
        
        camadas = [v['camada'] for v in validacoes]
        scores = [v['contribuicao'] for v in validacoes]
        cores = ['#00FF00' if v['status'] == '✅' else '#FFA500' for v in validacoes]
        
        bars = ax.barh(camadas, scores, color=cores, alpha=0.7, edgecolor='white', linewidth=1)
        
        # Adicionar valores
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 0.1, i, f'{score:.1f}', va='center', fontsize=10, color='white')
        
        ax.set_xlabel('Contribuição ao Score', fontsize=12, color='white')
        ax.set_title('📊 Confluência por Camada', fontsize=14, fontweight='bold', color='#00D9FF')
        ax.set_xlim(0, max(scores) * 1.2 if scores else 10)
        ax.grid(axis='x', alpha=0.3)
        ax.tick_params(colors='white')
    
    def _plot_gauge_score(self, ax, score):
        """Gauge (velocímetro) do score de confiança"""
        # Criar gauge semicircular
        theta = np.linspace(0, np.pi, 100)
        
        # Background
        ax.fill_between(theta, 0, 1, color='#333333', alpha=0.3)
        
        # Zonas coloridas
        ax.fill_between(theta[0:33], 0, 1, color='#FF0000', alpha=0.5)  # 0-3.3 (Baixo)
        ax.fill_between(theta[33:66], 0, 1, color='#FFA500', alpha=0.5)  # 3.3-6.6 (Médio)
        ax.fill_between(theta[66:100], 0, 1, color='#00FF00', alpha=0.5)  # 6.6-10 (Alto)
        
        # Ponteiro
        angle = np.pi * (1 - score / 10)
        ax.plot([0, np.cos(angle)], [0, np.sin(angle)], 'w-', linewidth=4)
        ax.plot(0, 0, 'wo', markersize=10)
        
        # Texto do score
        ax.text(0, -0.3, f'{score:.1f}/10', ha='center', va='top', 
               fontsize=24, fontweight='bold', color='white')
        
        # Título
        ax.set_title('🎯 Score de Confiança', fontsize=12, fontweight='bold', color='#00D9FF')
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.5, 1.2)
        ax.axis('off')
    
    def _plot_multi_timeframe(self, ax, mtf_data):
        """Gráfico de alinhamento multi-timeframe"""
        if not mtf_data or 'timeframes' not in mtf_data:
            ax.text(0.5, 0.5, 'Sem dados MTF', ha='center', va='center', color='gray')
            ax.axis('off')
            return
        
        tfs = list(mtf_data['timeframes'].keys())
        tendencias = []
        cores = []
        
        for tf in tfs:
            tendencia = mtf_data['timeframes'][tf].get('tendencia', 'NEUTRO')
            tendencias.append(tendencia)
            
            if tendencia == 'ALTA':
                cores.append('#00FF00')
            elif tendencia == 'BAIXA':
                cores.append('#FF0000')
            else:
                cores.append('#808080')
        
        y_pos = np.arange(len(tfs))
        bars = ax.barh(y_pos, [1]*len(tfs), color=cores, alpha=0.7)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(tfs, fontsize=10, color='white')
        ax.set_xlim(0, 1)
        ax.set_title('⏰ Multi-Timeframe', fontsize=12, fontweight='bold', color='#00D9FF')
        ax.axis('off')
        
        # Adicionar labels
        for i, (tf, tend) in enumerate(zip(tfs, tendencias)):
            ax.text(0.5, i, tend, ha='center', va='center', fontsize=10, 
                   color='black' if tend == 'ALTA' else 'white', fontweight='bold')
    
    def _plot_estrutura(self, ax, estrutura):
        """Gráfico de estrutura de mercado"""
        tendencia = estrutura.get('tendencia', 'INDEFINIDA')
        tipo = estrutura.get('tipo_estrutura', 'N/A')
        
        # Cor baseada na tendência
        if tendencia == 'ALTA':
            cor = '#00FF00'
            emoji = '📈'
        elif tendencia == 'BAIXA':
            cor = '#FF0000'
            emoji = '📉'
        else:
            cor = '#808080'
            emoji = '↔️'
        
        # Círculo grande
        circle = plt.Circle((0.5, 0.5), 0.4, color=cor, alpha=0.3)
        ax.add_patch(circle)
        
        # Texto
        ax.text(0.5, 0.6, emoji, ha='center', va='center', fontsize=40)
        ax.text(0.5, 0.3, tendencia, ha='center', va='center', 
               fontsize=14, fontweight='bold', color='white')
        ax.text(0.5, 0.15, tipo[:20], ha='center', va='center', 
               fontsize=9, color='gray')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('📊 Estrutura', fontsize=12, fontweight='bold', color='#00D9FF')
        ax.axis('off')
    
    def _plot_fluxo_dom(self, ax, fluxo):
        """Gráfico de pressão DOM"""
        if 'erro' in fluxo or 'fluxo_ratio' not in fluxo:
            ax.text(0.5, 0.5, 'Sem dados DOM', ha='center', va='center', color='gray')
            ax.axis('off')
            return
        
        ratio = fluxo.get('fluxo_ratio', 1.0)
        pressao = fluxo.get('pressao', 'NEUTRO')
        
        # Barra de pressão
        if pressao == 'COMPRA':
            cor = '#00FF00'
            valor = ratio
        elif pressao == 'VENDA':
            cor = '#FF0000'
            valor = 1 / ratio if ratio > 0 else 1
        else:
            cor = '#808080'
            valor = 1
        
        # Desenhar barra horizontal
        ax.barh([0], [valor], color=cor, alpha=0.7, height=0.3)
        
        # Texto
        ax.text(0.5, 0.5, f'{pressao}\n{ratio:.3f}', ha='center', va='center',
               fontsize=12, fontweight='bold', color='white')
        
        ax.set_xlim(0, 2)
        ax.set_ylim(-0.5, 1)
        ax.set_title('🌊 Fluxo DOM', fontsize=12, fontweight='bold', color='#00D9FF')
        ax.axis('off')
    
    def _plot_indicadores(self, ax, indicadores):
        """Gráfico de indicadores principais"""
        if not indicadores:
            ax.text(0.5, 0.5, 'Sem indicadores', ha='center', va='center', color='gray')
            ax.axis('off')
            return
        
        # Dados
        labels = ['EMA8', 'EMA21', 'RSI']
        valores = [
            indicadores.get('ema8', 0),
            indicadores.get('ema21', 0),
            indicadores.get('rsi', 0)
        ]
        
        # Normalizar para visualização
        max_val = max(valores) if valores else 1
        valores_norm = [v/max_val for v in valores]
        
        # Barras
        x = np.arange(len(labels))
        bars = ax.bar(x, valores_norm, color=['#00D9FF', '#FF6B00', '#9D00FF'], alpha=0.7)
        
        # Labels
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10, color='white')
        ax.set_title('📊 Indicadores', fontsize=12, fontweight='bold', color='#00D9FF')
        
        # Valores reais como texto
        for i, (bar, val) in enumerate(zip(bars, valores)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                   f'{val:.1f}', ha='center', va='bottom', fontsize=9, color='white')
        
        ax.set_ylim(0, 1.3)
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(colors='white')
    
    def _plot_contexto(self, ax, contexto):
        """Gráfico de contexto de mercado"""
        regime = contexto.get('regime', 'INDEFINIDO')
        forca = contexto.get('forca_regime', 0)
        volatilidade = contexto.get('volatilidade', 0)
        
        # Cor por regime
        cores = {
            'BULL_TREND': '#00FF00',
            'BEAR_TREND': '#FF0000',
            'CONSOLIDATION': '#FFA500',
            'VOLATILE': '#FF00FF',
            'SIDEWAYS': '#808080'
        }
        cor = cores.get(regime, '#808080')
        
        # Pizza chart simples
        sizes = [forca, 10-forca]
        colors = [cor, '#333333']
        
        wedges, texts = ax.pie(sizes, colors=colors, startangle=90, 
                               wedgeprops={'alpha': 0.7, 'edgecolor': 'white'})
        
        # Texto central
        ax.text(0, 0, f'{regime}\n{forca:.1f}/10', ha='center', va='center',
               fontsize=11, fontweight='bold', color='white')
        
        ax.set_title('🌍 Contexto', fontsize=12, fontweight='bold', color='#00D9FF')
    
    def _plot_sintese(self, ax, sintese):
        """Box de texto com síntese"""
        if not sintese:
            ax.text(0.5, 0.5, 'Sem síntese', ha='center', va='center', color='gray')
            ax.axis('off')
            return
        
        # Texto formatado
        texto = f"""
VIÉS:
{sintese.get('vies', 'N/A')}

RECOMENDAÇÃO:
{sintese.get('recomendacao', 'N/A')[:30]}...

RISCO:
{sintese.get('risco', 'N/A')}
        """
        
        ax.text(0.1, 0.9, texto.strip(), ha='left', va='top',
               fontsize=10, color='white', family='monospace',
               bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('✨ Síntese', fontsize=12, fontweight='bold', color='#00D9FF')
        ax.axis('off')


def gerar_grafico_comparacao_pares(resultado_multi_pair):
    """
    Gera gráfico de comparação entre pares
    
    Args:
        resultado_multi_pair: dict com análise multi-pair
    """
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    pares_data = resultado_multi_pair.get('pares', [])
    
    if not pares_data:
        return None
    
    # Dados
    symbols = [p['symbol'] for p in pares_data[:5]]
    scores = [p['confluencia']['score'] for p in pares_data[:5]]
    vieses = [p['sintese']['vies'] for p in pares_data[:5]]
    
    # Gráfico 1: Ranking por Score
    cores_score = ['#00FF00' if s >= 7 else '#FFA500' if s >= 5 else '#FF0000' for s in scores]
    bars1 = ax1.barh(symbols, scores, color=cores_score, alpha=0.7, edgecolor='white')
    
    ax1.set_xlabel('Score de Confluência', fontsize=12, color='white')
    ax1.set_title('🏆 Ranking por Score', fontsize=14, fontweight='bold', color='#00D9FF')
    ax1.set_xlim(0, 10)
    ax1.grid(axis='x', alpha=0.3)
    
    # Adicionar valores
    for bar, score in zip(bars1, scores):
        ax1.text(score + 0.2, bar.get_y() + bar.get_height()/2, 
                f'{score:.1f}', va='center', fontsize=10, color='white')
    
    # Gráfico 2: Distribuição de Viés
    vieses_count = {}
    for vies in vieses:
        key = vies.split()[0] if vies else 'INDEFINIDO'  # Primeira palavra
        vieses_count[key] = vieses_count.get(key, 0) + 1
    
    ax2.pie(vieses_count.values(), labels=vieses_count.keys(), autopct='%1.0f%%',
           colors=['#00FF00', '#FF0000', '#FFA500', '#808080'][:len(vieses_count)],
           textprops={'color': 'white', 'fontsize': 12})
    ax2.set_title('📊 Distribuição de Viés', fontsize=14, fontweight='bold', color='#00D9FF')
    
    # Salvar
    output_dir = 'reports/graficos/'
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}comparacao_pares_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    
    return filename


def gerar_heatmap_visual(resultado_heatmap):
    """
    Gera visualização de heatmap de correlações
    
    Args:
        resultado_heatmap: dict com matriz de correlações
    """
    if 'correlacoes' not in resultado_heatmap:
        return None
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 8))
    
    corr_matrix = resultado_heatmap['correlacoes']
    
    # Heatmap
    im = ax.imshow(corr_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)
    
    # Labels
    pares = resultado_heatmap['pares']
    ax.set_xticks(np.arange(len(pares)))
    ax.set_yticks(np.arange(len(pares)))
    ax.set_xticklabels([p[:6] for p in pares], fontsize=10, color='white')
    ax.set_yticklabels([p[:6] for p in pares], fontsize=10, color='white')
    
    # Valores nas células
    for i in range(len(pares)):
        for j in range(len(pares)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=9)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Correlação', color='white', fontsize=12)
    cbar.ax.tick_params(colors='white')
    
    ax.set_title('🔥 Heatmap de Correlações', fontsize=16, fontweight='bold', 
                color='#00D9FF', pad=20)
    
    # Salvar
    output_dir = 'reports/graficos/'
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}heatmap_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    
    return filename


if __name__ == "__main__":
    print("📊 Módulo de Visualização Gráfica carregado!")
    print("Use: VisualizadorGrafico().gerar_relatorio_completo(resultado, symbol, tf)")





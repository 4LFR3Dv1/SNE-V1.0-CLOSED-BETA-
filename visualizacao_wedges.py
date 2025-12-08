#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISUALIZAÇÃO DE WEDGES
Funções para traçar padrões de wedge nos gráficos
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime
import io
import base64

def criar_grafico_wedge(df, wedges, symbol="BTCUSDT", timeframe="1h"):
    """
    Cria gráfico com padrão de wedge traçado
    
    Args:
        df: DataFrame com dados OHLCV
        wedges: Dict com informações do wedge detectado
        symbol: Par analisado
        timeframe: Timeframe do gráfico
    
    Returns:
        Bytes da imagem do gráfico
    """
    try:
        # Configurar estilo
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Preparar dados
        df_plot = df.tail(100)  # Últimos 100 períodos
        df_plot['timestamp'] = pd.to_datetime(df_plot.index)
        df_plot['timestamp_num'] = mdates.date2num(df_plot['timestamp'])
        
        # Plotar candlesticks
        from mplfinance.original_flavor import candlestick_ohlc
        
        ohlc_data = []
        for i, row in df_plot.iterrows():
            ohlc_data.append([
                row['timestamp_num'],
                row['open'],
                row['high'],
                row['low'],
                row['close']
            ])
        
        candlestick_ohlc(ax, ohlc_data, width=0.0008, colorup='#00ff88', colordown='#ff4444')
        
        # Traçar linhas do wedge se detectado
        if wedges.get('wedge_detectado', False):
            tracar_linhas_wedge(ax, df_plot, wedges)
        
        # Configurar gráfico
        ax.set_title(f'{symbol} - {timeframe} | Padrão Wedge Detectado', 
                    color='white', fontsize=16, fontweight='bold')
        ax.set_ylabel('Preço (USDT)', color='white', fontsize=12)
        ax.set_xlabel('Tempo', color='white', fontsize=12)
        
        # Configurar eixos
        ax.tick_params(colors='white')
        ax.grid(True, color='gray', alpha=0.3, linestyle='--')
        
        # Formatar eixo X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        
        # Adicionar informações do wedge
        if wedges.get('wedge_detectado', False):
            adicionar_info_wedge(ax, wedges)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Converter para bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='black', edgecolor='none')
        buffer.seek(0)
        image_bytes = buffer.getvalue()
        
        plt.close(fig)
        return image_bytes
        
    except Exception as e:
        print(f"[ERRO GRÁFICO] Falha ao criar gráfico: {e}")
        return None

def tracar_linhas_wedge(ax, df, wedges):
    """
    Traça as linhas de tendência do wedge no gráfico
    
    Args:
        ax: Eixo matplotlib
        df: DataFrame com dados
        wedges: Dict com informações do wedge
    """
    try:
        pontos_res = wedges['pontos_resistencia']
        pontos_sup = wedges['pontos_suporte']
        
        # Converter índices para timestamps
        timestamps = df['timestamp_num'].values
        
        # Linha de resistência
        if len(pontos_res['x']) >= 2:
            x_res = timestamps[pontos_res['x']]
            y_res = pontos_res['y']
            
            # Estender linha para o futuro
            x_extended = np.linspace(x_res[0], x_res[-1] + (x_res[-1] - x_res[0]) * 0.3, 50)
            y_extended = np.interp(x_extended, x_res, y_res)
            
            ax.plot(x_extended, y_extended, color='#ff6b6b', linewidth=2.5, 
                   linestyle='--', alpha=0.8, label='Resistência')
            
            # Marcar pontos de toque
            ax.scatter(x_res, y_res, color='#ff6b6b', s=60, marker='o', 
                      edgecolors='white', linewidth=2, zorder=5)
        
        # Linha de suporte
        if len(pontos_sup['x']) >= 2:
            x_sup = timestamps[pontos_sup['x']]
            y_sup = pontos_sup['y']
            
            # Estender linha para o futuro
            x_extended = np.linspace(x_sup[0], x_sup[-1] + (x_sup[-1] - x_sup[0]) * 0.3, 50)
            y_extended = np.interp(x_extended, x_sup, y_sup)
            
            ax.plot(x_extended, y_extended, color='#4ecdc4', linewidth=2.5, 
                   linestyle='--', alpha=0.8, label='Suporte')
            
            # Marcar pontos de toque
            ax.scatter(x_sup, y_sup, color='#4ecdc4', s=60, marker='o', 
                      edgecolors='white', linewidth=2, zorder=5)
        
        # Destacar ponto de convergência
        if wedges.get('ponto_convergencia'):
            conv = wedges['ponto_convergencia']
            if conv and conv.get('x') and conv.get('y'):
                # Converter índice para timestamp
                if conv['x'] < len(timestamps):
                    conv_timestamp = timestamps[int(conv['x'])]
                    ax.scatter(conv_timestamp, conv['y'], color='#ffd93d', s=100, 
                             marker='*', edgecolors='black', linewidth=2, zorder=6)
                    ax.annotate('Convergência', 
                              xy=(conv_timestamp, conv['y']),
                              xytext=(10, 10), textcoords='offset points',
                              bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                              fontsize=10, fontweight='bold')
        
        # Adicionar legenda
        ax.legend(loc='upper left', fontsize=10)
        
    except Exception as e:
        print(f"[ERRO LINHAS] Falha ao traçar linhas: {e}")

def adicionar_info_wedge(ax, wedges):
    """
    Adiciona informações do wedge no gráfico
    
    Args:
        ax: Eixo matplotlib
        wedges: Dict com informações do wedge
    """
    try:
        # Informações principais
        info_text = f"""
🔺 {wedges['nome']}
📊 Confiança: {wedges['confianca']}%
⚡ Prob. Reversão: {wedges['probabilidade_reversao']}%
📐 Ângulo: {wedges.get('angulo_convergencia', 0):.1f}°
🎯 Toques: R:{wedges['num_touches_resistencia']} S:{wedges['num_touches_suporte']}
"""
        
        # Adicionar alvo se disponível
        if wedges.get('alvo_teorico'):
            alvo = wedges['alvo_teorico']
            info_text += f"🎯 Alvo: ${alvo['preco']:,.0f} ({alvo['direcao']})"
        
        # Posicionar texto
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               fontsize=11, verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8,
                        edgecolor='white', linewidth=1),
               color='white', fontweight='bold')
        
        # Adicionar sinal
        if wedges['tipo'] == 'RISING_WEDGE':
            sinal_text = "🔴 SINAL BEARISH"
            sinal_color = '#ff4444'
        else:
            sinal_text = "🟢 SINAL BULLISH"
            sinal_color = '#00ff88'
        
        ax.text(0.98, 0.98, sinal_text, transform=ax.transAxes,
               fontsize=14, verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round,pad=0.5', facecolor=sinal_color, alpha=0.8),
               color='white', fontweight='bold')
        
    except Exception as e:
        print(f"[ERRO INFO] Falha ao adicionar informações: {e}")

def criar_grafico_comparativo(df, wedges, symbol="BTCUSDT"):
    """
    Cria gráfico comparativo mostrando o padrão em diferentes timeframes
    
    Args:
        df: DataFrame principal
        wedges: Informações do wedge
        symbol: Par analisado
    
    Returns:
        Bytes da imagem
    """
    try:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'{symbol} - Análise Multi-Timeframe de Wedge', 
                    color='white', fontsize=16, fontweight='bold')
        
        timeframes = ['15m', '1h', '4h', '1d']
        
        for i, tf in enumerate(timeframes):
            ax = axes[i//2, i%2]
            
            # Simular dados para diferentes timeframes (em produção, coletaria dados reais)
            df_tf = df.resample(tf).agg({
                'open': 'first',
                'high': 'max', 
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            if len(df_tf) > 20:
                # Plotar candlesticks
                df_tf['timestamp'] = pd.to_datetime(df_tf.index)
                df_tf['timestamp_num'] = mdates.date2num(df_tf['timestamp'])
                
                ohlc_data = []
                for idx, row in df_tf.iterrows():
                    ohlc_data.append([
                        row['timestamp_num'],
                        row['open'],
                        row['high'],
                        row['low'],
                        row['close']
                    ])
                
                from mplfinance.original_flavor import candlestick_ohlc
                candlestick_ohlc(ax, ohlc_data, width=0.0008, colorup='#00ff88', colordown='#ff4444')
                
                # Configurar subplot
                ax.set_title(f'{tf}', color='white', fontsize=12)
                ax.tick_params(colors='white')
                ax.grid(True, color='gray', alpha=0.3)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        plt.tight_layout()
        
        # Converter para bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor='black', edgecolor='none')
        buffer.seek(0)
        image_bytes = buffer.getvalue()
        
        plt.close(fig)
        return image_bytes
        
    except Exception as e:
        print(f"[ERRO COMPARATIVO] Falha ao criar gráfico comparativo: {e}")
        return None


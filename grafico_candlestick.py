#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRÁFICO DE CANDLESTICK PROFISSIONAL
Gera visualização de candlesticks com indicadores técnicos
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter
import mplfinance as mpf
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import os
import warnings

# Suprimir warnings de tight_layout
warnings.filterwarnings('ignore', category=UserWarning, message='.*tight_layout.*')


def obter_dados_candlestick(symbol, interval="15m", limit=200):
    """Obtém dados OHLCV da Binance"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Criar DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Converter para tipos corretos
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            # Definir timestamp como índice
            df.set_index('timestamp', inplace=True)
            
            return df[['open', 'high', 'low', 'close', 'volume']]
        
        return None
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None


def calcular_indicadores_grafico(df):
    """Calcula indicadores básicos e avançados para o gráfico"""
    # INDICADORES BÁSICOS
    # EMA 8 e 21
    df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['SMA50'] = df['close'].rolling(window=50).mean()
    df['SMA200'] = df['close'].rolling(window=200).mean()
    
    # Bollinger Bands
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # Volume médio
    df['Volume_MA'] = df['volume'].rolling(window=20).mean()
    
    # INDICADORES AVANÇADOS
    try:
        # Importar módulo de indicadores avançados
        from indicadores_avancados import calcular_indicadores_avancados
        
        # Calcular indicadores avançados
        df_avancado = calcular_indicadores_avancados(df.copy())
        
        # Adicionar indicadores avançados ao DataFrame original
        indicadores_avancados = [
            'Williams_R', 'CCI', 'MFI', 'ADX', 'PSAR', 'PSAR_Trend',
            'OBV', 'Volume_Profile_POC', 'Volume_Profile_VAL', 'Volume_Profile_VAH',
            'KC_Upper', 'KC_Lower', 'DC_Upper', 'DC_Lower'
        ]
        
        for indicador in indicadores_avancados:
            if indicador in df_avancado.columns:
                df[indicador] = df_avancado[indicador]
        
        print(f"✅ Indicadores avançados adicionados ao gráfico")
        
    except Exception as e:
        print(f"⚠️ Erro ao calcular indicadores avançados: {e}")
        print("📊 Usando apenas indicadores básicos")
    
    return df


def gerar_grafico_distribuido(symbol, interval="15m", output_dir="reports/", 
                               entry=None, stop=None, tp1=None, tp2=None, tp3=None,
                               suportes=None, resistencias=None, range_data=None, anotacoes=None, resultado_analise=None):
    """
    Gera gráfico de candlestick profissional com layout distribuído em subplots
    
    Args:
        symbol: Par a analisar
        interval: Timeframe
        output_dir: Diretório de saída
        entry, stop, tp1, tp2, tp3: Níveis operacionais
        resultado_analise: Resultado completo da análise para padrões avançados
    """
    print(f"📊 Coletando dados para {symbol} ({interval})...")
    
    # Obter dados
    df = obter_dados_candlestick(symbol, interval)
    
    if df is None or df.empty:
        print("❌ Erro ao obter dados")
        return None
    
    # Calcular indicadores
    df = calcular_indicadores_grafico(df)
    
    # CRIAR LAYOUT DISTRIBUÍDO COM SUBPLOTS MELHORADO
    fig = plt.figure(figsize=(20, 14), facecolor='#1a1a1a')
    
    # Criar grid de subplots com espaçamento adequado
    gs = fig.add_gridspec(4, 1, height_ratios=[4, 1.5, 1.5, 1.5], hspace=0.3, 
                          left=0.08, right=0.95, top=0.92, bottom=0.08)
    
    # Título principal
    fig.suptitle(f'{symbol} - {interval.upper()} - Análise Técnica Avançada', 
                 fontsize=18, color='white', y=0.96, fontweight='bold')
    
    # 1. GRÁFICO PRINCIPAL - Candlestick + EMAs + Volume Profile + Níveis
    ax_main = fig.add_subplot(gs[0])
    ax_main.set_facecolor('#1a1a1a')
    
    # Plotar candlesticks como linha de preço
    ax_main.plot(df.index, df['close'], color='white', linewidth=2, alpha=0.9, label='Preço')
    
    # EMAs com cores distintas
    ax_main.plot(df.index, df['EMA8'], color='#00ffff', linewidth=2, label='EMA 8', alpha=0.8)
    ax_main.plot(df.index, df['EMA21'], color='#ff8c00', linewidth=2, label='EMA 21', alpha=0.8)
    
    # SMAs (se disponíveis)
    if not df['SMA50'].isna().all():
        ax_main.plot(df.index, df['SMA50'], color='#ffff00', linewidth=1.5, alpha=0.7, label='SMA 50')
    if not df['SMA200'].isna().all():
        ax_main.plot(df.index, df['SMA200'], color='#ff00ff', linewidth=1.5, alpha=0.7, label='SMA 200')
    
    # Bollinger Bands com preenchimento
    ax_main.plot(df.index, df['BB_upper'], color='#808080', linewidth=1, alpha=0.6, label='BB Upper')
    ax_main.plot(df.index, df['BB_lower'], color='#808080', linewidth=1, alpha=0.6, label='BB Lower')
    ax_main.fill_between(df.index, df['BB_lower'], df['BB_upper'], alpha=0.1, color='gray')
    
    # VOLUME PROFILE VISUAL
    if 'Volume_Profile_POC' in df.columns and 'Volume_Profile_VAL' in df.columns and 'Volume_Profile_VAH' in df.columns:
        poc = df['Volume_Profile_POC'].iloc[-1]
        val = df['Volume_Profile_VAL'].iloc[-1]
        vah = df['Volume_Profile_VAH'].iloc[-1]
        
        if poc > 0 and val > 0 and vah > 0:
            # Value Area (zona de alta liquidez)
            ax_main.axhspan(val, vah, alpha=0.2, color='blue', label='Value Area')
            
            # POC (Point of Control) - linha destacada
            ax_main.axhline(y=poc, color='#0066ff', linestyle='-', linewidth=3, alpha=0.9, label=f'POC: ${poc:,.2f}')
            
            # VAL e VAH como linhas de referência
            ax_main.axhline(y=val, color='#0066ff', linestyle=':', linewidth=2, alpha=0.7, label=f'VAL: ${val:,.2f}')
            ax_main.axhline(y=vah, color='#0066ff', linestyle=':', linewidth=2, alpha=0.7, label=f'VAH: ${vah:,.2f}')
    
    # KELTNER CHANNELS
    if 'KC_Upper' in df.columns and 'KC_Lower' in df.columns:
        ax_main.plot(df.index, df['KC_Upper'], color='#800080', alpha=0.7, linewidth=1.5, label='Keltner Upper')
        ax_main.plot(df.index, df['KC_Lower'], color='#800080', alpha=0.7, linewidth=1.5, label='Keltner Lower')
        ax_main.fill_between(df.index, df['KC_Lower'], df['KC_Upper'], alpha=0.08, color='purple')
    
    # DONCHIAN CHANNELS
    if 'DC_Upper' in df.columns and 'DC_Lower' in df.columns:
        ax_main.plot(df.index, df['DC_Upper'], color='#ffa500', alpha=0.6, linewidth=1, label='Donchian Upper')
        ax_main.plot(df.index, df['DC_Lower'], color='#ffa500', alpha=0.6, linewidth=1, label='Donchian Lower')
    
    # PARABOLIC SAR
    if 'PSAR' in df.columns:
        # Plotar apenas os últimos pontos para não poluir o gráfico
        ultimos_psar = df['PSAR'].tail(50)
        ax_main.scatter(ultimos_psar.index, ultimos_psar.values, color='red', s=20, alpha=0.8, label='Parabolic SAR')
    
    # NÍVEIS OPERACIONAIS
    if entry:
        ax_main.axhline(y=entry, color='white', linestyle='--', linewidth=2, alpha=0.9, label=f'Entry: ${entry:,.2f}')
    if stop:
        ax_main.axhline(y=stop, color='red', linestyle='--', linewidth=2, alpha=0.9, label=f'Stop: ${stop:,.2f}')
    if tp1:
        ax_main.axhline(y=tp1, color='lime', linestyle='--', linewidth=1.5, alpha=0.8, label=f'TP1: ${tp1:,.2f}')
    if tp2:
        ax_main.axhline(y=tp2, color='lime', linestyle='--', linewidth=1.5, alpha=0.7, label=f'TP2: ${tp2:,.2f}')
    if tp3:
        ax_main.axhline(y=tp3, color='lime', linestyle='--', linewidth=1.5, alpha=0.6, label=f'TP3: ${tp3:,.2f}')
    
    # SUPORTES E RESISTÊNCIAS
    if suportes:
        for i, s in enumerate(suportes, 1):
            ax_main.axhline(y=s, color='green', linestyle=':', linewidth=2, alpha=0.7, label=f'S{i}: ${s:,.2f}')
    if resistencias:
        for i, r in enumerate(resistencias, 1):
            ax_main.axhline(y=r, color='red', linestyle=':', linewidth=2, alpha=0.7, label=f'R{i}: ${r:,.2f}')
    
    # PADRÕES GRÁFICOS VISUAIS
    adicionar_padroes_graficos_visuais(ax_main, df, resultado_analise)
    
    # Configurar gráfico principal
    ax_main.set_ylabel('Preço (USDT)', color='white', fontsize=12, fontweight='bold')
    ax_main.tick_params(axis='both', colors='white', labelsize=11)
    ax_main.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_main.legend(loc='upper left', fontsize=9, framealpha=0.9, facecolor='#2a2a2a', edgecolor='white')
    
    # 2. OSCILADORES - RSI, Williams %R, CCI, MFI
    ax_osc = fig.add_subplot(gs[1])
    ax_osc.set_facecolor('#1a1a1a')
    
    # RSI (se disponível)
    if 'RSI' in df.columns:
        ax_osc.plot(df.index, df['RSI'], color='#ffff00', linewidth=2, label='RSI')
        ax_osc.axhline(y=70, color='red', linestyle='--', alpha=0.7, linewidth=1.5, label='Sobrecompra')
        ax_osc.axhline(y=30, color='green', linestyle='--', alpha=0.7, linewidth=1.5, label='Sobrevenda')
        ax_osc.axhline(y=50, color='white', linestyle='-', alpha=0.4, linewidth=1)
        ax_osc.fill_between(df.index, 30, 70, alpha=0.1, color='yellow')
    
    # Williams %R
    if 'Williams_R' in df.columns:
        ax_osc.plot(df.index, df['Williams_R'], color='#00ffff', linewidth=1.5, label='Williams %R')
        ax_osc.axhline(y=-20, color='red', linestyle='--', alpha=0.6, linewidth=1)
        ax_osc.axhline(y=-80, color='green', linestyle='--', alpha=0.6, linewidth=1)
    
    # CCI
    if 'CCI' in df.columns:
        ax_osc.plot(df.index, df['CCI'], color='#ff8c00', linewidth=1.5, label='CCI')
        ax_osc.axhline(y=100, color='red', linestyle='--', alpha=0.6, linewidth=1)
        ax_osc.axhline(y=-100, color='green', linestyle='--', alpha=0.6, linewidth=1)
    
    # MFI
    if 'MFI' in df.columns:
        ax_osc.plot(df.index, df['MFI'], color='#800080', linewidth=1.5, label='MFI')
        ax_osc.axhline(y=80, color='red', linestyle='--', alpha=0.6, linewidth=1)
        ax_osc.axhline(y=20, color='green', linestyle='--', alpha=0.6, linewidth=1)
    
    ax_osc.set_ylabel('Osciladores', color='white', fontsize=12, fontweight='bold')
    ax_osc.tick_params(axis='both', colors='white', labelsize=10)
    ax_osc.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_osc.legend(loc='upper left', fontsize=8, framealpha=0.9, facecolor='#2a2a2a', edgecolor='white')
    
    # 3. TENDÊNCIA - ADX, MACD
    ax_trend = fig.add_subplot(gs[2])
    ax_trend.set_facecolor('#1a1a1a')
    
    # ADX
    if 'ADX' in df.columns:
        ax_trend.plot(df.index, df['ADX'], color='#ff0000', linewidth=2, label='ADX')
        ax_trend.axhline(y=25, color='white', linestyle='--', alpha=0.7, linewidth=1.5, label='Tendência Forte')
        ax_trend.axhline(y=20, color='gray', linestyle='--', alpha=0.6, linewidth=1, label='Tendência Fraca')
        ax_trend.fill_between(df.index, 20, 25, alpha=0.1, color='red')
    
    # MACD (se disponível)
    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        ax_trend.plot(df.index, df['MACD'], color='#0066ff', linewidth=2, label='MACD')
        ax_trend.plot(df.index, df['MACD_Signal'], color='#ff0000', linewidth=2, label='MACD Signal')
        ax_trend.axhline(y=0, color='white', linestyle='-', alpha=0.4, linewidth=1)
    
    ax_trend.set_ylabel('Tendência', color='white', fontsize=12, fontweight='bold')
    ax_trend.tick_params(axis='both', colors='white', labelsize=10)
    ax_trend.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_trend.legend(loc='upper left', fontsize=8, framealpha=0.9, facecolor='#2a2a2a', edgecolor='white')
    
    # 4. VOLUME - OBV, Volume Profile
    ax_vol = fig.add_subplot(gs[3])
    ax_vol.set_facecolor('#1a1a1a')
    
    # OBV
    if 'OBV' in df.columns:
        ax_vol.plot(df.index, df['OBV'], color='#00ff00', linewidth=2, label='OBV')
    
    # Volume normalizado
    volume_norm = (df['volume'] - df['volume'].min()) / (df['volume'].max() - df['volume'].min()) * 100
    ax_vol.bar(df.index, volume_norm, alpha=0.4, color='#0066ff', label='Volume Normalizado', width=0.8)
    
    ax_vol.set_ylabel('Volume', color='white', fontsize=12, fontweight='bold')
    ax_vol.set_xlabel('Tempo', color='white', fontsize=12, fontweight='bold')
    ax_vol.tick_params(axis='both', colors='white', labelsize=10)
    ax_vol.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_vol.legend(loc='upper left', fontsize=8, framealpha=0.9, facecolor='#2a2a2a', edgecolor='white')
    
    # Salvar gráfico
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}{symbol}_{interval}_{timestamp}_candlestick_distribuido.png"
    
    # Salvar com alta qualidade
    plt.savefig(filename, dpi=200, bbox_inches='tight', facecolor='#1a1a1a', edgecolor='white', 
                pad_inches=0.2, format='png')
    plt.close()
    
    print(f"✅ Gráfico distribuído salvo: {filename}")
    
    return filename


def gerar_grafico_candlestick(symbol, interval="15m", output_dir="reports/", 
                               entry=None, stop=None, tp1=None, tp2=None, tp3=None,
                               suportes=None, resistencias=None, range_data=None, anotacoes=None, resultado_analise=None):
    """
    Gera gráfico de candlestick profissional
    
    Args:
        symbol: Par a analisar
        interval: Timeframe
        output_dir: Diretório de saída
        entry, stop, tp1, tp2, tp3: Níveis operacionais
    """
    print(f"📊 Coletando dados para {symbol} ({interval})...")
    
    # Obter dados
    df = obter_dados_candlestick(symbol, interval)
    
    if df is None or df.empty:
        print("❌ Erro ao obter dados")
        return None
    
    # Calcular indicadores
    df = calcular_indicadores_grafico(df)
    
    # Configurar estilo
    mc = mpf.make_marketcolors(
        up='#00ff00',
        down='#ff0000',
        edge='inherit',
        wick={'up':'#00ff00', 'down':'#ff0000'},
        volume='in',
        alpha=0.9
    )
    
    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle='',
        y_on_right=False,
        rc={
            'font.size': 11,
            'axes.labelcolor': 'white',
            'axes.edgecolor': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'text.color': 'white'
        },
        facecolor='#1a1a1a',
        edgecolor='#ffffff',
        figcolor='#0a0a0a',
        gridcolor='#333333'
    )
    
    # Preparar adicional plots
    apds = []
    
    # EMAs
    apds.append(mpf.make_addplot(df['EMA8'], color='cyan', width=1.5, label='EMA 8'))
    apds.append(mpf.make_addplot(df['EMA21'], color='orange', width=1.5, label='EMA 21'))
    
    # SMAs (opcional, se houver dados suficientes)
    if not df['SMA50'].isna().all():
        apds.append(mpf.make_addplot(df['SMA50'], color='yellow', width=1, alpha=0.5, label='SMA 50'))
    
    if not df['SMA200'].isna().all():
        apds.append(mpf.make_addplot(df['SMA200'], color='magenta', width=1, alpha=0.5, label='SMA 200'))
    
    # Bollinger Bands
    apds.append(mpf.make_addplot(df['BB_upper'], color='gray', width=0.7, alpha=0.3))
    apds.append(mpf.make_addplot(df['BB_lower'], color='gray', width=0.7, alpha=0.3))
    
    # INDICADORES AVANÇADOS - Adicionar de forma sutil
    # Keltner Channels
    if 'KC_Upper' in df.columns and 'KC_Lower' in df.columns:
        apds.append(mpf.make_addplot(df['KC_Upper'], color='purple', width=0.8, alpha=0.4, label='KC Upper'))
        apds.append(mpf.make_addplot(df['KC_Lower'], color='purple', width=0.8, alpha=0.4, label='KC Lower'))
    
    # Donchian Channels
    if 'DC_Upper' in df.columns and 'DC_Lower' in df.columns:
        apds.append(mpf.make_addplot(df['DC_Upper'], color='orange', width=0.6, alpha=0.3, label='DC Upper'))
        apds.append(mpf.make_addplot(df['DC_Lower'], color='orange', width=0.6, alpha=0.3, label='DC Lower'))
    
    # Parabolic SAR (apenas últimos pontos para não poluir)
    if 'PSAR' in df.columns:
        # Criar uma série com NaN para os primeiros valores e PSAR para os últimos
        psar_plot = df['PSAR'].copy()
        psar_plot.iloc[:-20] = np.nan  # Primeiros valores como NaN
        apds.append(mpf.make_addplot(psar_plot, color='red', width=0.5, alpha=0.6, type='scatter', markersize=3, label='PSAR'))
    
    # Criar figura
    fig, axes = mpf.plot(
        df,
        type='candle',
        style=s,
        title='',  # Título será customizado depois
        ylabel='Preço (USDT)',
        volume=True,
        ylabel_lower='Volume',
        addplot=apds,
        figsize=(16, 10),
        returnfig=True,
        warn_too_much_data=300
    )
    
    # Adicionar níveis operacionais
    ax = axes[0]
    
    if entry:
        ax.axhline(y=entry, color='white', linestyle='--', linewidth=1.5, alpha=0.8, label=f'Entry: ${entry:,.2f}')
    
    if stop:
        ax.axhline(y=stop, color='red', linestyle='--', linewidth=1.5, alpha=0.8, label=f'Stop: ${stop:,.2f}')
    
    if tp1:
        ax.axhline(y=tp1, color='lime', linestyle='--', linewidth=1, alpha=0.7, label=f'TP1: ${tp1:,.2f}')
    
    if tp2:
        ax.axhline(y=tp2, color='lime', linestyle='--', linewidth=1, alpha=0.6, label=f'TP2: ${tp2:,.2f}')
    
    if tp3:
        ax.axhline(y=tp3, color='lime', linestyle='--', linewidth=1, alpha=0.5, label=f'TP3: ${tp3:,.2f}')
    
    # Adicionar suportes e resistências
    if suportes:
        for i, s in enumerate(suportes, 1):
            ax.axhline(y=s, color='green', linestyle=':', linewidth=1.5, alpha=0.6, label=f'S{i}: ${s:,.2f}')
    
    if resistencias:
        for i, r in enumerate(resistencias, 1):
            ax.axhline(y=r, color='red', linestyle=':', linewidth=1.5, alpha=0.6, label=f'R{i}: ${r:,.2f}')
    
    # VOLUME PROFILE VISUAL (apenas se não estiver nos addplots)
    if 'Volume_Profile_POC' in df.columns and 'Volume_Profile_VAL' in df.columns and 'Volume_Profile_VAH' in df.columns:
        poc = df['Volume_Profile_POC'].iloc[-1]
        val = df['Volume_Profile_VAL'].iloc[-1]
        vah = df['Volume_Profile_VAH'].iloc[-1]
        
        if poc > 0 and val > 0 and vah > 0:
            # Value Area (zona de alta liquidez)
            ax.axhspan(val, vah, alpha=0.15, color='blue', label='Value Area (VAL-VAH)')
            
            # POC (Point of Control) - linha destacada
            ax.axhline(y=poc, color='blue', linestyle='-', linewidth=2, alpha=0.8, label=f'POC: ${poc:,.2f}')
            
            # VAL e VAH como linhas de referência
            ax.axhline(y=val, color='blue', linestyle=':', linewidth=1, alpha=0.6, label=f'VAL: ${val:,.2f}')
            ax.axhline(y=vah, color='blue', linestyle=':', linewidth=1, alpha=0.6, label=f'VAH: ${vah:,.2f}')
    
    # PADRÕES GRÁFICOS VISUAIS
    adicionar_padroes_graficos_visuais(ax, df, resultado_analise)
    
    # Adicionar zona de range (ATR)
    if range_data:
        # Zona de range como área sombreada
        ax.axhspan(
            range_data['range_inferior'], 
            range_data['range_superior'],
            alpha=0.1, 
            color='yellow',
            label=f"Range ATR ({range_data['volatilidade_status']})"
        )
        
        # Linhas das bordas do range
        ax.axhline(
            y=range_data['range_superior'], 
            color='orange', 
            linestyle='-.', 
            linewidth=1, 
            alpha=0.5
        )
        ax.axhline(
            y=range_data['range_inferior'], 
            color='orange', 
            linestyle='-.', 
            linewidth=1, 
            alpha=0.5
        )
    
    # Adicionar título customizado
    preco_atual = df['close'].iloc[-1]
    timestamp_grafico = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    fig.suptitle(
        f'SNE RADAR - {symbol} ({interval})',
        fontsize=18,
        color='white',
        weight='bold',
        y=0.98
    )
    
    # Adicionar subtítulo com preço e timestamp
    ax.text(
        0.5, 1.02,
        f'Preço: ${preco_atual:,.2f} | {timestamp_grafico}',
        transform=ax.transAxes,
        fontsize=12,
        color='white',
        ha='center',
        weight='bold'
    )
    
    # Adicionar marca d'água SNE
    ax.text(
        0.98, 0.02,
        'SNE RADAR',
        transform=ax.transAxes,
        fontsize=10,
        color='white',
        alpha=0.3,
        ha='right',
        va='bottom',
        style='italic'
    )
    
    # Adicionar anotações técnicas
    # Anotações desabilitadas por solicitação do usuário
    # if anotacoes:
    #     adicionar_anotacoes_grafico(ax, df, anotacoes)
    
    # Adicionar legenda FORA do gráfico (lado direito)
    legend = ax.legend(
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),  # Posiciona fora, à direita
        fontsize=9,
        framealpha=0.9,
        facecolor='#1a1a1a',
        edgecolor='white',
        labelcolor='white',
        ncol=1,  # 1 coluna vertical
        title='INDICADORES',
        title_fontsize=10
    )
    legend.get_title().set_color('white')
    
    # Garantir que todos os textos estejam em branco
    ax.tick_params(axis='both', colors='white', labelsize=10)
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    
    # Ajustar cor do eixo de volume também
    if len(axes) > 1:
        axes[1].tick_params(axis='both', colors='white', labelsize=10)
        axes[1].yaxis.label.set_color('white')
        axes[1].xaxis.label.set_color('white')
    
    # Salvar
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}{symbol}_{interval}_{timestamp}_candlestick.png"
    
    # Ajustar layout com espaço para título e legenda externa
    plt.tight_layout(rect=[0, 0, 0.85, 0.96])  # Deixa espaço à direita para legenda
    plt.savefig(
        filename, 
        dpi=150, 
        bbox_inches='tight',  # Inclui a legenda externa
        facecolor='#0a0a0a', 
        edgecolor='white',
        pad_inches=0.2  # Padding extra
    )
    plt.close()
    
    print(f"✅ Gráfico salvo: {filename}")
    
    return filename


def adicionar_padroes_graficos_visuais(ax, df, resultado_analise=None):
    """
    Adiciona padrões gráficos detectados visualmente ao gráfico
    """
    try:
        # Obter padrões da análise de candles passados se disponível
        padroes_candlestick = []
        padroes_graficos = []
        
        if resultado_analise and 'analise_candles_passados' in resultado_analise:
            analise_candles = resultado_analise['analise_candles_passados']
            if 'erro' not in analise_candles:
                padroes_candlestick = analise_candles.get('padroes_candlestick', [])
                padroes_graficos = analise_candles.get('padroes_graficos', [])
        
        # PULAR padrões candlestick - focar em padrões mais avançados
        if padroes_candlestick:
            print(f"📊 {len(padroes_candlestick)} padrões candlestick detectados (não plotados no gráfico)")
        
        # Plotar TODOS os padrões avançados (exceto candlestick)
        padroes_para_plotar = []
        
        # Coletar todos os padrões avançados
        if analise_candles and 'erro' not in analise_candles:
            padroes_para_plotar.extend(analise_candles.get('padroes_sequencia', []))
            padroes_para_plotar.extend(analise_candles.get('padroes_breakout', []))
            padroes_para_plotar.extend(analise_candles.get('padroes_divergencia', []))
            padroes_para_plotar.extend(analise_candles.get('padroes_liquidez', []))
            padroes_para_plotar.extend(analise_candles.get('padroes_sentimento', []))
            padroes_para_plotar.extend(analise_candles.get('padroes_volume', []))
            padroes_para_plotar.extend(analise_candles.get('padroes_momentum', []))
            padroes_para_plotar.extend(analise_candles.get('padroes_graficos', []))
        
        if padroes_para_plotar:
            print(f"🎨 Plotando {len(padroes_para_plotar)} padrões avançados no gráfico...")
            
            # Limitar a 15 padrões mais significativos
            padroes_ordenados = sorted(padroes_para_plotar, 
                                     key=lambda x: x.get('confianca', 0), 
                                     reverse=True)[:15]
            
            for i, padrao in enumerate(padroes_ordenados):
                try:
                    # Obter informações do padrão
                    nome = padrao.get('nome', 'PADRÃO')
                    sinal = padrao.get('sinal', 'NEUTRO')
                    confianca = padrao.get('confianca', 0.5)
                    categoria = padrao.get('categoria', 'OUTRO')
                    
                    # Tentar usar posição específica do padrão se disponível
                    if 'index' in padrao and padrao['index'] is not None:
                        # Usar posição específica do padrão
                        posicao_idx = padrao['index']
                        if posicao_idx >= len(df):
                            posicao_idx = len(df) - 1
                        posicao_x = posicao_idx  # Usar índice numérico
                        preco_posicao = df['close'].iloc[posicao_idx]
                        print(f"📍 {nome} ({categoria}) na posição específica {posicao_idx}")
                    else:
                        # Distribuir uniformemente ao longo do gráfico
                        if len(padroes_ordenados) == 1:
                            posicao_idx = len(df) // 2
                        else:
                            posicao_idx = int((i / (len(padroes_ordenados) - 1)) * (len(df) - 1))
                        
                        posicao_idx = max(0, min(posicao_idx, len(df) - 1))
                        posicao_x = posicao_idx  # Usar índice numérico
                        preco_posicao = df['close'].iloc[posicao_idx]
                        print(f"📍 {nome} ({categoria}) distribuído na posição {posicao_idx}")
                    
                    # Adicionar offset vertical baseado na categoria para evitar sobreposição
                    if categoria == 'SEQUENCIA':
                        offset_y = 0.008 * preco_posicao  # 0.8% acima
                    elif categoria == 'BREAKOUT':
                        offset_y = -0.008 * preco_posicao  # 0.8% abaixo
                    elif categoria == 'DIVERGENCIA':
                        offset_y = 0.012 * preco_posicao  # 1.2% acima
                    elif categoria == 'LIQUIDEZ':
                        offset_y = -0.012 * preco_posicao  # 1.2% abaixo
                    elif categoria == 'SENTIMENTO':
                        offset_y = 0.016 * preco_posicao  # 1.6% acima
                    else:
                        offset_y = (i % 3) * 0.005 * preco_posicao  # Alternar
                    
                    preco_final = preco_posicao + offset_y
                    
                    # Escolher cor e marcador baseado na categoria
                    cores_categoria = {
                        'SEQUENCIA': ('lime', '^'),
                        'BREAKOUT': ('orange', 'D'),
                        'DIVERGENCIA': ('cyan', '*'),
                        'LIQUIDEZ': ('yellow', 'o'),
                        'SENTIMENTO': ('magenta', 'd'),
                        'VOLUME': ('brown', 's'),
                        'MOMENTUM': ('pink', '^'),
                        'GRAFICO': ('blue', 'v')
                    }
                    
                    cor, marcador = cores_categoria.get(categoria, ('white', 'o'))
                    
                    # Ajustar tamanho baseado na confiança
                    tamanho = int(100 + confianca * 200)
                    
                    # Plotar o padrão usando posição numérica
                    ax.scatter(posicao_x, preco_final, color=cor, s=tamanho, marker=marcador, 
                              alpha=0.8, edgecolors='black', linewidth=1,
                              label=f'{nome} ({categoria})')
                    
                    # Adicionar texto com offset baseado na categoria
                    offset_text = (10 + (i % 4) * 5, 10 + (i % 4) * 5)
                    
                    ax.annotate(f'{nome}\n({categoria})', (posicao_x, preco_final), 
                               xytext=offset_text, textcoords='offset points', 
                               fontsize=8, fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor=cor, alpha=0.7))
                    
                except Exception as e:
                    print(f"⚠️ Erro ao plotar padrão {padrao.get('nome', 'UNKNOWN')}: {e}")
                    continue
        
        # Adicionar legenda se houver padrões avançados
        if padroes_para_plotar:
            ax.legend(loc='upper left', fontsize=8, framealpha=0.8)
            print("✅ Padrões avançados adicionados ao gráfico com legenda!")
        
    except Exception as e:
        print(f"⚠️ Erro ao adicionar padrões gráficos: {e}")


def gerar_grafico_com_niveis(symbol, interval, output_dir, niveis_dict, sr_data=None, range_data=None, anotacoes=None, resultado_analise=None):
    """
    Gera gráfico com níveis operacionais, S/R, range e anotações técnicas
    Usa a base original do mplfinance com indicadores avançados integrados
    
    Args:
        niveis_dict: {'entry': float, 'stop': float, 'tp1': float, 'tp2': float, 'tp3': float}
        sr_data: {'suportes': list, 'resistencias': list}
        range_data: {'range_superior': float, 'range_inferior': float, 'volatilidade_status': str}
        anotacoes: Dict com padrões técnicos detectados
        resultado_analise: Resultado completo da análise para padrões avançados
    """
    suportes = sr_data.get('suportes', []) if sr_data else None
    resistencias = sr_data.get('resistencias', []) if sr_data else None
    
    # Usar a função original como base, mas com indicadores avançados
    return gerar_grafico_candlestick(
        symbol=symbol,
        interval=interval,
        output_dir=output_dir,
        entry=niveis_dict.get('entry'),
        stop=niveis_dict.get('stop'),
        tp1=niveis_dict.get('tp1'),
        tp2=niveis_dict.get('tp2'),
        tp3=niveis_dict.get('tp3'),
        suportes=suportes,
        resistencias=resistencias,
        range_data=range_data,
        anotacoes=anotacoes,
        resultado_analise=resultado_analise
    )


def adicionar_anotacoes_grafico(ax, df, anotacoes):
    """
    Adiciona anotações técnicas ao gráfico (apenas as mais relevantes)
    
    Args:
        ax: Eixo do matplotlib
        df: DataFrame com dados
        anotacoes: Dict com padrões detectados
    """
    # Cores e símbolos para cada tipo (usar marcadores matplotlib padrão)
    config_anotacoes = {
        'BREAKOUT': {'marker': '^', 'color': '#00ff00', 'size': 12, 'label': 'BO'},
        'BREAKDOWN': {'marker': 'v', 'color': '#ff0000', 'size': 12, 'label': 'BD'},
        'FALHA_BREAKOUT': {'marker': 'x', 'color': '#ff8800', 'size': 10, 'label': 'Falha'},
        'FALHA_BREAKDOWN': {'marker': 'x', 'color': '#ff8800', 'size': 10, 'label': 'Falha'},
        'ENTRADA_COMPRA': {'marker': '^', 'color': '#00ff00', 'size': 14, 'label': 'BUY'},
        'ENTRADA_VENDA': {'marker': 'v', 'color': '#ff0000', 'size': 14, 'label': 'SELL'}
    }
    
    # Filtrar apenas eventos relevantes e recentes (últimos 30% do gráfico)
    tamanho_janela = len(df)
    inicio_janela = int(tamanho_janela * 0.7)  # Últimos 30%
    
    eventos_filtrados = []
    
    # Priorizar: Entradas > Rompimentos > Falhas
    prioridades = {
        'pontos_entrada_saida': 3,
        'rompimentos': 2,
        'falhas': 1
    }
    
    for categoria, eventos in anotacoes.items():
        if not eventos or categoria not in prioridades:
            continue
        
        for evento in eventos:
            idx = evento.get('index')
            tipo = evento.get('tipo')
            
            # Filtrar apenas eventos recentes e relevantes
            if idx is None or idx < inicio_janela or idx >= len(df):
                continue
            
            if tipo not in config_anotacoes:
                continue
            
            # Adicionar prioridade
            evento['prioridade'] = prioridades[categoria]
            evento['categoria'] = categoria
            eventos_filtrados.append(evento)
    
    # Ordenar por prioridade (maior primeiro)
    eventos_filtrados.sort(key=lambda x: x['prioridade'], reverse=True)
    
    # Limitar a 10 anotações máximo
    eventos_filtrados = eventos_filtrados[:10]
    
    # Plotar apenas eventos filtrados
    for evento in eventos_filtrados:
        idx = evento.get('index')
        tipo = evento.get('tipo')
        preco = evento.get('preco')
        categoria = evento.get('categoria')
        
        config = config_anotacoes[tipo]
        
        # Plotar marcador (sem texto, apenas ícone)
        ax.plot(
            idx, 
            preco,
            marker=config['marker'],
            markersize=config['size'],
            color=config['color'],
            markeredgecolor='white',
            markeredgewidth=2,
            zorder=5,
            alpha=0.9
        )
        
        # Adicionar texto APENAS para entradas com resultado
        if categoria == 'pontos_entrada_saida':
            resultado = evento.get('resultado', '')
            sucesso = evento.get('sucesso', False)
            
            # Apenas mostrar se foi lucrativo
            if sucesso:
                cor_texto = '#00ff00'
                offset_y = preco * 0.01 if 'COMPRA' in tipo else -preco * 0.01
                
                ax.annotate(
                    resultado,
                    xy=(idx, preco),
                    xytext=(idx, preco + offset_y),
                    color=cor_texto,
                    fontsize=8,
                    weight='bold',
                    ha='center',
                    va='bottom' if offset_y > 0 else 'top',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a1a', 
                             edgecolor=cor_texto, alpha=0.9, linewidth=1.5)
                )


if __name__ == "__main__":
    # Teste
    gerar_grafico_candlestick("BTCUSDT", "15m", "reports/", entry=67000, stop=66500, tp1=67500, tp2=68000)


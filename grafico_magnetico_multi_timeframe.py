#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRÁFICO MAGNÉTICO MULTI-TIMEFRAME - SNE RADAR
Sistema integrado que combina campos magnéticos com análise multi-timeframe
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
from typing import Dict, List, Optional, Tuple

# Suprimir warnings
warnings.filterwarnings('ignore', category=UserWarning, message='.*tight_layout.*')


class ExecutorMagneticoMultiTimeframe:
    """Classe para gerar gráficos magnéticos multi-timeframe especializados"""
    
    def __init__(self):
        self.figsize = (28, 22)
        self.output_dir = 'reports/magnetico_multi_tf/'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Paleta de cores magnética expandida
        self.cores = {
            'fundo': '#000000',
            'lmh_azul': '#1a4d80',      # Campo magnético azul (compressão)
            'lmh_vermelho': '#801a1a',  # Campo magnético vermelho (expansão)
            'led_cinza': '#404040',     # Estrutura magnética neutra
            'led_verde': '#2d5a2d',     # Estrutura magnética alta
            'led_vermelho': '#5a2d2d',  # Estrutura magnética baixa
            'zv_preto': '#1a1a1a',      # Zona de vácuo
            'ema8_ciano': '#00ffff',    # Fluxo visual claro
            'ema21_dourado': '#ffd700',  # Fluxo visual dourado
            'sma200_magenta': '#ff00ff', # Estrutura de longo prazo
            'psar_pontos': '#ff4444',   # Timing magnético
            'volume_azul': '#0066cc',   # Campo de concentração
            'candle_up': '#00ff00',     # Candle de alta
            'candle_down': '#ff0000',   # Candle de baixa
            'grid': '#333333'           # Grid
        }
    
    def obter_dados_candlestick(self, symbol, interval="5m", limit=200):
        """Obtém dados OHLCV da Binance"""
        try:
            import requests
            url = "https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
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
                
                df.set_index('timestamp', inplace=True)
                return df[['open', 'high', 'low', 'close', 'volume']]
            
            return None
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return None
    
    def calcular_campos_magneticos(self, df):
        """Calcula campos magnéticos horizontais (LMH) e zonas de vácuo (ZV)"""
        try:
            # Volume Profile para LMH
            poc = df['close'].rolling(window=20).mean().iloc[-1]  # POC simplificado
            
            # VAL e VAH baseados em percentis de preço
            val = df['close'].rolling(window=20).quantile(0.25).iloc[-1]
            vah = df['close'].rolling(window=20).quantile(0.75).iloc[-1]
            
            # EMA8 e EMA21 para estrutura magnética
            df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
            df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
            df['SMA200'] = df['close'].rolling(window=200).mean()
            
            # Campo Dinâmico de Pressão (diferença EMA8-EMA21)
            df['Campo_Dinamico'] = df['EMA8'] - df['EMA21']
            df['Campo_Dinamico_MA'] = df['Campo_Dinamico'].rolling(window=10).mean()
            
            # PSAR para timing magnético
            df['PSAR'] = self._calcular_psar(df)
            
            # Identificar zonas de vácuo (onde não há estrutura magnética)
            df['Zona_Vacuo'] = self._identificar_zonas_vacuo(df)
            
            # RSI para análise de momentum
            df['RSI'] = self._calcular_rsi(df)
            
            # Volume médio para análise de volume
            df['Volume_MA20'] = df['volume'].rolling(window=20).mean()
            df['Volume_MA50'] = df['volume'].rolling(window=50).mean()
            
            return {
                'poc': float(poc),
                'val': float(val),
                'vah': float(vah),
                'campo_dinamico': float(df['Campo_Dinamico'].iloc[-1]),
                'campo_dinamico_tendencia': 'expansao' if df['Campo_Dinamico'].iloc[-1] > df['Campo_Dinamico_MA'].iloc[-1] else 'compressao',
                'zonas_vacuo': df['Zona_Vacuo'].iloc[-20:].tolist(),  # Últimas 20 zonas
                'rsi_atual': float(df['RSI'].iloc[-1]) if not df['RSI'].isna().all() else 50,
                'volume_atual': float(df['volume'].iloc[-1]),
                'volume_media': float(df['Volume_MA20'].iloc[-1]) if not df['Volume_MA20'].isna().all() else float(df['volume'].iloc[-1])
            }
            
        except Exception as e:
            print(f"Erro ao calcular campos magnéticos: {e}")
            return None
    
    def _calcular_psar(self, df, af=0.02, max_af=0.2):
        """Calcula Parabolic SAR simplificado"""
        try:
            if len(df) < 2:
                return np.zeros(len(df))
            
            psar = np.zeros(len(df))
            trend = np.zeros(len(df))
            
            # Inicializar
            psar[0] = df['low'].iloc[0]
            trend[0] = 1  # 1 = alta, -1 = baixa
            
            for i in range(1, len(df)):
                if trend[i-1] == 1:  # Tendência de alta
                    psar[i] = psar[i-1] + af * (df['high'].iloc[i-1] - psar[i-1])
                    if df['low'].iloc[i] <= psar[i]:
                        trend[i] = -1
                        psar[i] = df['high'].iloc[i-1]
                    else:
                        trend[i] = 1
                else:  # Tendência de baixa
                    psar[i] = psar[i-1] + af * (df['low'].iloc[i-1] - psar[i-1])
                    if df['high'].iloc[i] >= psar[i]:
                        trend[i] = 1
                        psar[i] = df['low'].iloc[i-1]
                    else:
                        trend[i] = -1
            
            return psar
        except Exception as e:
            print(f"Erro ao calcular PSAR: {e}")
            return np.zeros(len(df))
    
    def _identificar_zonas_vacuo(self, df):
        """Identifica zonas de vácuo (sem estrutura magnética)"""
        try:
            # Verificar se as EMAs existem
            if 'EMA8' not in df.columns or 'EMA21' not in df.columns:
                return np.zeros(len(df))
            
            # Zona de vácuo = área onde EMA8 e EMA21 estão distantes
            distancia_emas = abs(df['EMA8'] - df['EMA21'])
            media_distancia = distancia_emas.rolling(window=20).mean()
            
            # Zona de vácuo quando a distância é maior que a média
            zonas_vacuo = (distancia_emas > media_distancia * 1.5).astype(int)
            
            # Preencher NaN com 0
            zonas_vacuo = zonas_vacuo.fillna(0)
            
            return zonas_vacuo
        except Exception as e:
            print(f"Erro ao identificar zonas de vácuo: {e}")
            return np.zeros(len(df))
    
    def _calcular_rsi(self, df, periodo=14):
        """Calcula RSI (Relative Strength Index)"""
        try:
            if len(df) < periodo + 1:
                return pd.Series([50] * len(df), index=df.index)
            
            # Calcular mudanças de preço
            delta = df['close'].diff()
            
            # Separar ganhos e perdas
            ganhos = delta.where(delta > 0, 0)
            perdas = -delta.where(delta < 0, 0)
            
            # Calcular médias móveis exponenciais
            avg_ganhos = ganhos.ewm(span=periodo, adjust=False).mean()
            avg_perdas = perdas.ewm(span=periodo, adjust=False).mean()
            
            # Calcular RS e RSI
            rs = avg_ganhos / avg_perdas
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50)  # Preencher NaN com 50 (neutro)
        except Exception as e:
            print(f"Erro ao calcular RSI: {e}")
            return pd.Series([50] * len(df), index=df.index)
    
    def gerar_grafico_magnetico_multi_timeframe(self, symbol, timeframes=None, 
                                              niveis_dict=None, sr_data=None):
        """
        Gera gráfico magnético multi-timeframe especializado
        
        Args:
            symbol: Par a analisar
            timeframes: Lista de timeframes (ex: ['5m', '15m', '1h', '4h'])
            niveis_dict: Níveis operacionais do Motor Renan
            sr_data: Dados de suporte/resistência
        """
        if timeframes is None:
            timeframes = ['5m', '15m', '1h', '4h']
        
        print(f"🧲 Coletando dados magnéticos multi-timeframe para {symbol}...")
        print(f"   📊 Timeframes: {', '.join(timeframes)}")
        
        # Coletar dados para cada timeframe
        dados_tf = {}
        campos_tf = {}
        
        for tf in timeframes:
            print(f"   🔄 Processando {tf}...")
            df = self.obter_dados_candlestick(symbol, tf)
            if df is not None and not df.empty:
                campos = self.calcular_campos_magneticos(df)
                if campos:
                    dados_tf[tf] = df
                    campos_tf[tf] = campos
                    print(f"   ✅ {tf}: {len(df)} candles, POC: ${campos['poc']:.2f}")
                else:
                    print(f"   ❌ {tf}: Erro ao calcular campos magnéticos")
            else:
                print(f"   ❌ {tf}: Erro ao obter dados")
        
        if not dados_tf:
            print("❌ Nenhum timeframe válido encontrado")
            return None
        
        # Criar figura multi-timeframe
        plt.style.use('dark_background')
        fig = plt.figure(figsize=self.figsize)
        
        # Estrutura otimizada: gráficos principais maiores + indicadores menores
        num_tf = len(timeframes)
        
        # Usar GridSpec com heights personalizados para dar mais espaço aos gráficos principais
        gs = GridSpec(6, 2, figure=fig, hspace=0.4, wspace=0.3, 
                     height_ratios=[3, 3, 1.5, 1.5, 1, 1])
        
        # Plotar cada timeframe em gráficos maiores
        tf_keys = list(dados_tf.keys())
        
        for i, tf in enumerate(tf_keys[:4]):  # Máximo 4 timeframes
            df = dados_tf[tf]
            campos = campos_tf[tf]
            
            # Posicionar gráficos em grid 2x2 com mais espaço
            if i < 2:
                ax = fig.add_subplot(gs[0, i])
            else:
                ax = fig.add_subplot(gs[1, i-2])
            
            self._plot_timeframe_magnetico(ax, df, tf, symbol, campos, niveis_dict, sr_data)
        
        # Painel de Volume Multi-Timeframe (menor)
        ax_volume = fig.add_subplot(gs[2, :])
        self._plot_volume_multi_timeframe(ax_volume, dados_tf, symbol)
        
        # Painel de RSI Multi-Timeframe (menor)
        ax_rsi = fig.add_subplot(gs[3, :])
        self._plot_rsi_multi_timeframe(ax_rsi, dados_tf, symbol)
        
        # Painel de análise consolidada (menor)
        ax_analise = fig.add_subplot(gs[4:, :])
        self._plot_analise_magnetico_consolidada(ax_analise, dados_tf, campos_tf, symbol)
        
        # Título principal
        timestamp_grafico = datetime.now().strftime('%d/%m/%Y %H:%M')
        fig.suptitle(
            f'🧲 SNE RADAR MAGNÉTICO MULTI-TIMEFRAME - {symbol}',
            fontsize=24,
            color='white',
            weight='bold',
            y=0.98
        )
        
        # Subtítulo com informações magnéticas
        fig.text(
            0.5, 0.95,
            f'Análise Magnética Multi-Timeframe | {timestamp_grafico}',
            fontsize=14,
            color='white',
            ha='center',
            weight='bold'
        )
        
        # Salvar gráfico
        filename = self._salvar_grafico_magnetico_multi_tf(symbol, timeframes)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(
            filename,
            dpi=150,
            bbox_inches='tight',
            facecolor=self.cores['fundo'],
            edgecolor='white',
            pad_inches=0.3
        )
        plt.close()
        
        print(f"✅ Gráfico magnético multi-timeframe salvo: {filename}")
        return filename
    
    def _plot_timeframe_magnetico(self, ax, df, tf, symbol, campos, niveis_dict, sr_data):
        """Plota um timeframe com elementos magnéticos"""
        ax.clear()
        
        # Verificar dados
        if df is None or df.empty:
            ax.text(0.5, 0.5, 'Dados não disponíveis', ha='center', va='center', 
                   transform=ax.transAxes, color='white', fontsize=12)
            ax.set_title(f'{symbol} | {tf.upper()} - SEM DADOS', color='white')
            return
        
        print(f"   📊 Plotando {len(df)} candles magnéticos para {tf}")
        
        # Plotar candles manualmente
        for i, (timestamp, row) in enumerate(df.iterrows()):
            # Determinar cor baseada na direção do candle
            if row['close'] >= row['open']:
                color = self.cores['candle_up']
                edge_color = '#00cc00'
            else:
                color = self.cores['candle_down']
                edge_color = '#cc0000'
            
            # Corpo do candle
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['open'], row['close'])
            
            if body_height > 0:
                ax.bar(i, body_height, bottom=body_bottom, color=color, alpha=0.9, 
                      width=0.6, edgecolor=edge_color, linewidth=0.5)
            else:
                # Doji
                ax.plot([i-0.3, i+0.3], [row['close'], row['close']], 
                       color=color, linewidth=2, alpha=0.9)
            
            # Sombras (wick)
            ax.plot([i, i], [row['low'], row['high']], color=edge_color, 
                   linewidth=1, alpha=0.8)
        
        # Médias móveis magnéticas
        if not df['EMA8'].isna().all():
            ax.plot(range(len(df)), df['EMA8'], color=self.cores['ema8_ciano'], 
                   linewidth=2, label='EMA8 (Fluxo)', alpha=0.9)
        if not df['EMA21'].isna().all():
            ax.plot(range(len(df)), df['EMA21'], color=self.cores['ema21_dourado'], 
                   linewidth=2, label='EMA21 (Campo)', alpha=0.9)
        if not df['SMA200'].isna().all():
            ax.plot(range(len(df)), df['SMA200'], color=self.cores['sma200_magenta'], 
                   linewidth=1.5, label='SMA200 (Estrutura)', alpha=0.7)
        
        # PSAR (timing magnético - apenas últimos pontos)
        if 'PSAR' in df.columns:
            psar_plot = df['PSAR'].copy()
            psar_plot.iloc[:-10] = np.nan  # Apenas últimos 10 pontos
            ax.scatter(range(len(df)), psar_plot, color=self.cores['psar_pontos'], 
                     s=20, alpha=0.8, label='PSAR (Timing)', zorder=5)
        
        # Campos Magnéticos Horizontais (LMH)
        val = campos['val']
        vah = campos['vah']
        poc = campos['poc']
        
        # LMH Azul (compressão) - VAL até POC
        ax.axhspan(val, poc, alpha=0.15, color=self.cores['lmh_azul'], 
                 label=f'LMH Azul (Compressão)')
        
        # LMH Vermelho (expansão) - POC até VAH
        ax.axhspan(poc, vah, alpha=0.15, color=self.cores['lmh_vermelho'], 
                 label=f'LMH Vermelho (Expansão)')
        
        # Linhas de referência LMH
        ax.axhline(y=val, color=self.cores['lmh_azul'], linestyle='--', 
                  linewidth=1.5, alpha=0.8, label=f'VAL: ${val:.2f}')
        ax.axhline(y=poc, color='white', linestyle='-', 
                  linewidth=2, alpha=0.9, label=f'POC: ${poc:.2f}')
        ax.axhline(y=vah, color=self.cores['lmh_vermelho'], linestyle='--', 
                  linewidth=1.5, alpha=0.8, label=f'VAH: ${vah:.2f}')
        
        # Zonas de Vácuo (ZV)
        zonas_vacuo = campos['zonas_vacuo']
        for i, zona in enumerate(zonas_vacuo[-10:]):  # Últimas 10 zonas
            if zona == 1:  # Zona de vácuo ativa
                ax.axhspan(df['low'].iloc[-10+i], df['high'].iloc[-10+i], 
                          alpha=0.1, color=self.cores['zv_preto'])
        
        # Níveis operacionais do Motor Renan
        if niveis_dict:
            entry = niveis_dict.get('entry')
            stop = niveis_dict.get('stop')
            tp1 = niveis_dict.get('tp1')
            tp2 = niveis_dict.get('tp2')
            tp3 = niveis_dict.get('tp3')
            
            if entry:
                ax.axhline(y=entry, color='white', linestyle='-', 
                          linewidth=2, alpha=0.9, label=f'Entry: ${entry:,.2f}')
            if stop:
                ax.axhline(y=stop, color='red', linestyle='-', 
                          linewidth=2, alpha=0.9, label=f'Stop: ${stop:,.2f}')
            if tp1:
                ax.axhline(y=tp1, color='lime', linestyle=':', 
                          linewidth=1.5, alpha=0.8, label=f'TP1: ${tp1:,.2f}')
            if tp2:
                ax.axhline(y=tp2, color='lime', linestyle=':', 
                          linewidth=1.5, alpha=0.7, label=f'TP2: ${tp2:,.2f}')
            if tp3:
                ax.axhline(y=tp3, color='lime', linestyle=':', 
                          linewidth=1.5, alpha=0.6, label=f'TP3: ${tp3:,.2f}')
        
        # Suportes e resistências
        if sr_data:
            suportes = sr_data.get('suportes', [])
            resistencias = sr_data.get('resistencias', [])
            
            for i, s in enumerate(suportes[:3], 1):
                ax.axhline(y=s, color='green', linestyle=':', 
                          linewidth=1, alpha=0.6, label=f'S{i}: ${s:,.2f}')
            
            for i, r in enumerate(resistencias[:3], 1):
                ax.axhline(y=r, color='red', linestyle=':', 
                          linewidth=1, alpha=0.6, label=f'R{i}: ${r:,.2f}')
        
        # Configurar eixo
        ax.set_title(f'{symbol} | {tf.upper()} | Campo: {campos["campo_dinamico_tendencia"].upper()}', 
                    color='white', fontsize=14, weight='bold')
        ax.set_ylabel('Preço (USDT)', color='white', fontsize=12)
        ax.tick_params(axis='both', colors='white', labelsize=11)
        ax.grid(True, alpha=0.3, color=self.cores['grid'])
        ax.set_facecolor(self.cores['fundo'])
        
        # Configurar bordas
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        
        # Configurar eixo X
        if len(df) > 0:
            step = max(1, len(df) // 6)
            x_positions = range(0, len(df), step)
            x_labels = [df.index[i].strftime('%d/%m %H:%M') for i in x_positions]
            
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
        
        # Legenda compacta
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc='upper left', fontsize=9, framealpha=0.9, 
                     facecolor=self.cores['fundo'], edgecolor='white', 
                     labelcolor='white', ncol=2)
    
    def _plot_volume_multi_timeframe(self, ax, dados_tf, symbol):
        """Plota volume consolidado multi-timeframe"""
        ax.clear()
        
        # Configurar fundo
        ax.set_facecolor(self.cores['fundo'])
        ax.set_title(f'VOLUME MAGNÉTICO MULTI-TIMEFRAME | {symbol}', 
                    color='white', fontsize=12, weight='bold')
        
        # Cores para cada timeframe
        cores_tf = {'5m': '#00bfff', '15m': '#ff8c00', '1h': '#32cd32', '4h': '#ff1493', 
                   '1m': '#ff69b4', '30m': '#ffd700', '8h': '#00ffff', '1d': '#ff4500'}
        
        # Plotar volume para cada timeframe
        for tf, df in dados_tf.items():
            if 'volume' in df.columns and not df['volume'].isna().all():
                cor = cores_tf.get(tf, 'white')
                
                # Volume com cores baseadas na direção do candle
                colors = []
                for _, row in df.iterrows():
                    if row['close'] >= row['open']:
                        colors.append('#00ff00')  # Verde para alta
                    else:
                        colors.append('#ff0000')  # Vermelho para baixa
                
                # Plotar barras de volume
                x_positions = range(len(df))
                ax.bar(x_positions, df['volume'], color=colors, alpha=0.7, 
                      width=0.8, label=f'Volume {tf.upper()}')
                
                # Volume médio
                if 'Volume_MA20' in df.columns and not df['Volume_MA20'].isna().all():
                    ax.plot(range(len(df)), df['Volume_MA20'], color=cor, 
                           linewidth=2, alpha=0.8, linestyle='--', 
                           label=f'Vol MA20 {tf.upper()}')
        
        # Configurar eixo
        ax.set_ylabel('Volume', color='white', fontsize=10)
        ax.tick_params(axis='both', colors='white', labelsize=8)
        ax.grid(True, alpha=0.3, color=self.cores['grid'])
        
        # Configurar bordas
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        
        # Legenda
        ax.legend(loc='upper right', fontsize=7, framealpha=0.9, 
                 facecolor=self.cores['fundo'], edgecolor='white', labelcolor='white')
    
    def _plot_rsi_multi_timeframe(self, ax, dados_tf, symbol):
        """Plota RSI consolidado multi-timeframe"""
        ax.clear()
        
        # Configurar fundo
        ax.set_facecolor(self.cores['fundo'])
        ax.set_title(f'RSI MAGNÉTICO MULTI-TIMEFRAME | {symbol}', 
                    color='white', fontsize=12, weight='bold')
        
        # Linhas de referência RSI
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Sobrecompra (70)')
        ax.axhline(y=50, color='white', linestyle='-', alpha=0.5, label='Neutro (50)')
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Sobrevenda (30)')
        
        # Cores para cada timeframe
        cores_tf = {'5m': '#00bfff', '15m': '#ff8c00', '1h': '#32cd32', '4h': '#ff1493', 
                   '1m': '#ff69b4', '30m': '#ffd700', '8h': '#00ffff', '1d': '#ff4500'}
        
        # Plotar RSI para cada timeframe
        for tf, df in dados_tf.items():
            if 'RSI' in df.columns and not df['RSI'].isna().all():
                cor = cores_tf.get(tf, 'white')
                ax.plot(range(len(df)), df['RSI'], color=cor, 
                       linewidth=2, alpha=0.8, label=f'RSI {tf.upper()}')
        
        # Configurar eixo
        ax.set_ylim(0, 100)
        ax.set_ylabel('RSI', color='white', fontsize=10)
        ax.tick_params(axis='both', colors='white', labelsize=8)
        ax.grid(True, alpha=0.3, color=self.cores['grid'])
        
        # Configurar bordas
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        
        # Legenda
        ax.legend(loc='upper right', fontsize=7, framealpha=0.9, 
                 facecolor=self.cores['fundo'], edgecolor='white', labelcolor='white')
    
    def _plot_analise_magnetico_consolidada(self, ax, dados_tf, campos_tf, symbol):
        """Plota análise consolidada dos campos magnéticos"""
        ax.clear()
        
        # Configurar fundo
        ax.set_facecolor(self.cores['fundo'])
        ax.set_title(f'ANÁLISE MAGNÉTICA CONSOLIDADA | {symbol}', 
                    color='white', fontsize=12, weight='bold')
        
        # Preparar dados da tabela
        tabela_dados = []
        headers = ['Timeframe', 'Campo Dinâmico', 'Tendência', 'RSI', 'Volume Status', 'POC', 'Preço Atual', 'Status']
        
        for tf, df in dados_tf.items():
            if tf in campos_tf:
                campos = campos_tf[tf]
                
                # Campo dinâmico
                campo_dinamico = campos['campo_dinamico']
                tendencia = campos['campo_dinamico_tendencia']
                
                # RSI atual
                rsi_atual = campos.get('rsi_atual', 50)
                
                # Status do volume
                volume_atual = campos.get('volume_atual', 0)
                volume_media = campos.get('volume_media', volume_atual)
                volume_ratio = volume_atual / volume_media if volume_media > 0 else 1
                
                if volume_ratio > 1.5:
                    vol_status = 'ALTO'
                elif volume_ratio > 0.8:
                    vol_status = 'NORMAL'
                else:
                    vol_status = 'BAIXO'
                
                # Status baseado no campo dinâmico
                if tendencia == 'expansao':
                    status = 'EXPANSÃO'
                else:
                    status = 'COMPRESSÃO'
                
                # Preço atual
                preco_atual = df['close'].iloc[-1]
                
                tabela_dados.append([
                    tf.upper(),
                    f"{campo_dinamico:.4f}",
                    tendencia.upper(),
                    f"{rsi_atual:.1f}",
                    vol_status,
                    f"${campos['poc']:.2f}",
                    f"${preco_atual:,.2f}",
                    status
                ])
        
        # Criar tabela
        if tabela_dados:
            tabela = ax.table(cellText=tabela_dados, colLabels=headers,
                            cellLoc='center', loc='center',
                            bbox=[0, 0, 1, 1])
            
            # Configurar estilo da tabela
            tabela.auto_set_font_size(False)
            tabela.set_fontsize(11)
            tabela.scale(1, 2.5)
            
            # Colorir células baseado no conteúdo
            for i in range(len(tabela_dados)):
                for j in range(len(headers)):
                    cell = tabela[(i+1, j)]
                    cell.set_facecolor('#1a1a1a')
                    cell.set_text_props(weight='bold', color='white')
                    
                    # Colorir tendência
                    if j == 2:  # Coluna tendência
                        if tabela_dados[i][j] == 'EXPANSAO':
                            cell.set_facecolor('#00ff00')
                            cell.set_text_props(color='black')
                        else:
                            cell.set_facecolor('#0066cc')
                            cell.set_text_props(color='white')
                    
                    # Colorir RSI
                    elif j == 3:  # Coluna RSI
                        try:
                            rsi_val = float(tabela_dados[i][j])
                            if rsi_val > 70:
                                cell.set_facecolor('#ff4444')
                                cell.set_text_props(color='white')
                            elif rsi_val < 30:
                                cell.set_facecolor('#44ff44')
                                cell.set_text_props(color='black')
                        except:
                            pass
                    
                    # Colorir volume
                    elif j == 4:  # Coluna volume
                        if tabela_dados[i][j] == 'ALTO':
                            cell.set_facecolor('#ffff00')
                            cell.set_text_props(color='black')
                        elif tabela_dados[i][j] == 'BAIXO':
                            cell.set_facecolor('#ff8800')
                            cell.set_text_props(color='white')
                    
                    # Colorir status
                    elif j == 7:  # Coluna status
                        if tabela_dados[i][j] == 'EXPANSÃO':
                            cell.set_facecolor('#00ff00')
                            cell.set_text_props(color='black')
                        else:
                            cell.set_facecolor('#0066cc')
                            cell.set_text_props(color='white')
            
            # Cabeçalho
            for j in range(len(headers)):
                cell = tabela[(0, j)]
                cell.set_facecolor('#333333')
                cell.set_text_props(weight='bold', color='white')
        
        ax.axis('off')
    
    def _salvar_grafico_magnetico_multi_tf(self, symbol, timeframes):
        """Salva o gráfico magnético multi-timeframe"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            tf_str = '_'.join(timeframes)
            filename = f"{self.output_dir}{symbol}_multi_tf_{tf_str}_{timestamp}_magnetico.png"
            
            return filename
            
        except Exception as e:
            print(f"Erro ao salvar gráfico magnético multi-timeframe: {e}")
            return None


def gerar_grafico_magnetico_multi_timeframe_completo(symbol, timeframes=None, 
                                                   niveis_dict=None, sr_data=None):
    """
    Função principal para gerar gráfico magnético multi-timeframe completo
    
    Args:
        symbol: Par a analisar
        timeframes: Lista de timeframes (ex: ['5m', '15m', '1h', '4h'])
        niveis_dict: Níveis operacionais
        sr_data: Dados S/R
    
    Returns:
        Caminho do arquivo gerado
    """
    executor = ExecutorMagneticoMultiTimeframe()
    return executor.gerar_grafico_magnetico_multi_timeframe(
        symbol=symbol,
        timeframes=timeframes,
        niveis_dict=niveis_dict,
        sr_data=sr_data
    )


if __name__ == "__main__":
    # Teste do executor magnético multi-timeframe
    print("🧲 Testando Executor Magnético Multi-Timeframe...")
    
    executor = ExecutorMagneticoMultiTimeframe()
    filename = executor.gerar_grafico_magnetico_multi_timeframe(
        "BTCUSDT", 
        timeframes=['5m', '15m', '1h', '4h']
    )
    
    if filename:
        print(f"✅ Teste concluído: {filename}")
    else:
        print("❌ Erro no teste")


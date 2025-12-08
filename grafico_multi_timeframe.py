#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRÁFICOS MULTI-TIMEFRAME PROFISSIONAIS - SNE RADAR
Sistema robusto para análise técnica multi-timeframe com elementos essenciais
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
from typing import Dict, List, Optional, Tuple

# Tentar importar mplfinance, se não estiver disponível, usar matplotlib
try:
    import mplfinance as mpf
    MPLFINANCE_AVAILABLE = True
except ImportError:
    MPLFINANCE_AVAILABLE = False
    print("⚠️ mplfinance não disponível, usando matplotlib")

# Suprimir warnings
warnings.filterwarnings('ignore', category=UserWarning, message='.*tight_layout.*')


class GraficoMultiTimeframe:
    """Classe para gerar gráficos multi-timeframe profissionais"""
    
    def __init__(self):
        self.figsize = (20, 16)
        self.style = 'dark_background'
        self.output_dir = 'reports/multi_tf/'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configurações de cores profissionais
        self.colors = {
            'ema8': '#00bfff',      # Azul claro
            'ema21': '#ff8c00',     # Laranja
            'sma50': '#32cd32',     # Verde
            'sma200': '#ff1493',    # Rosa
            'bb_upper': '#808080',  # Cinza
            'bb_lower': '#808080',  # Cinza
            'bb_middle': '#dda0dd', # Roxo claro
            'volume_up': '#00ff00', # Verde
            'volume_down': '#ff0000', # Vermelho
            'support': '#00ff00',   # Verde
            'resistance': '#ff0000', # Vermelho
            'fibonacci': '#ffff00', # Amarelo
            'entry': '#ffffff',     # Branco
            'stop': '#ff4500',      # Vermelho laranja
            'tp': '#00ff00'         # Verde
        }
    
    def obter_dados_binance(self, symbol: str, interval: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Obtém dados OHLCV da Binance usando função existente do sistema"""
        try:
            # Usar função existente do sistema
            from main import buscar_dados_binance
            
            df = buscar_dados_binance(symbol, interval, limit)
            
            if df is not None and not df.empty:
                # Renomear colunas para compatibilidade
                df = df.rename(columns={'trades': 'quote_volume'})
                
                # Garantir que temos as colunas necessárias
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                if all(col in df.columns for col in required_cols):
                    return df[required_cols + ['quote_volume'] if 'quote_volume' in df.columns else required_cols]
            
            return None
        except Exception as e:
            print(f"❌ Erro ao obter dados: {e}")
            return None
    
    def calcular_indicadores_completos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos os indicadores técnicos essenciais"""
        # Médias móveis essenciais
        df['EMA8'] = df['close'].ewm(span=8, adjust=False).mean()
        df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['SMA50'] = df['close'].rolling(window=50).mean()
        df['SMA100'] = df['close'].rolling(window=100).mean()
        df['SMA200'] = df['close'].rolling(window=200).mean()
        
        # Bollinger Bands
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        df['ATR'] = true_range.rolling(window=14).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # Volume médio
        df['Volume_MA20'] = df['volume'].rolling(window=20).mean()
        df['Volume_MA50'] = df['volume'].rolling(window=50).mean()
        
        # Ichimoku (para timeframes maiores)
        if len(df) >= 52:
            df['Ichimoku_A'] = ((df['high'].rolling(9).max() + df['low'].rolling(9).min()) / 2).shift(26)
            df['Ichimoku_B'] = ((df['high'].rolling(26).max() + df['low'].rolling(26).min()) / 2).shift(26)
            df['Ichimoku_base'] = ((df['high'].rolling(26).max() + df['low'].rolling(26).min()) / 2)
            df['Ichimoku_conversion'] = ((df['high'].rolling(9).max() + df['low'].rolling(9).min()) / 2)
        
        return df
    
    def calcular_suportes_resistencias(self, df: pd.DataFrame) -> Dict:
        """Calcula suportes e resistências dinâmicos e estáticos"""
        # Suportes e resistências estáticos (máximas/mínimas recentes)
        recent_data = df.tail(100)  # Últimos 100 candles
        
        # Encontrar máximas e mínimas locais
        highs = recent_data['high'].rolling(window=5, center=True).max()
        lows = recent_data['low'].rolling(window=5, center=True).min()
        
        # Identificar pontos de reversão
        resistance_levels = []
        support_levels = []
        
        for i in range(2, len(highs) - 2):
            if highs.iloc[i] == recent_data['high'].iloc[i]:
                resistance_levels.append(highs.iloc[i])
            if lows.iloc[i] == recent_data['low'].iloc[i]:
                support_levels.append(lows.iloc[i])
        
        # Remover duplicatas e ordenar
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]
        support_levels = sorted(list(set(support_levels)))[:5]
        
        # Suportes e resistências dinâmicos (médias móveis)
        dynamic_resistance = []
        dynamic_support = []
        
        if not df['EMA21'].isna().all():
            dynamic_resistance.append(df['EMA21'].iloc[-1])
        if not df['SMA50'].isna().all():
            dynamic_resistance.append(df['SMA50'].iloc[-1])
        if not df['SMA200'].isna().all():
            dynamic_resistance.append(df['SMA200'].iloc[-1])
        
        return {
            'resistencias': resistance_levels,
            'suportes': support_levels,
            'resistencias_dinamicas': dynamic_resistance,
            'suportes_dinamicos': dynamic_support
        }
    
    def calcular_fibonacci(self, df: pd.DataFrame) -> Dict:
        """Calcula níveis de Fibonacci baseados em swing recente"""
        recent_data = df.tail(50)
        
        # Encontrar swing high e swing low
        swing_high = recent_data['high'].max()
        swing_low = recent_data['low'].min()
        
        # Calcular níveis de Fibonacci
        diff = swing_high - swing_low
        
        fib_levels = {
            '0%': swing_high,
            '23.6%': swing_high - (diff * 0.236),
            '38.2%': swing_high - (diff * 0.382),
            '50%': swing_high - (diff * 0.5),
            '61.8%': swing_high - (diff * 0.618),
            '78.6%': swing_high - (diff * 0.786),
            '100%': swing_low
        }
        
        return fib_levels
    
    def detectar_padroes_graficos(self, df: pd.DataFrame) -> Dict:
        """Detecta padrões gráficos básicos"""
        patterns = {
            'wedges': [],
            'flags': [],
            'triangles': [],
            'divergencias': []
        }
        
        # Detectar divergências RSI vs Preço
        if len(df) >= 50:
            recent_data = df.tail(50)
            
            # Encontrar máximas e mínimas no preço
            price_highs = recent_data['high'].rolling(window=5, center=True).max()
            price_lows = recent_data['low'].rolling(window=5, center=True).min()
            
            # Encontrar máximas e mínimas no RSI
            rsi_highs = recent_data['RSI'].rolling(window=5, center=True).max()
            rsi_lows = recent_data['RSI'].rolling(window=5, center=True).min()
            
            # Detectar divergência bearish (preço faz máxima mais alta, RSI máxima mais baixa)
            for i in range(10, len(recent_data) - 10):
                if (price_highs.iloc[i] == recent_data['high'].iloc[i] and 
                    rsi_highs.iloc[i] == recent_data['RSI'].iloc[i]):
                    
                    # Verificar se há divergência
                    prev_high_idx = None
                    for j in range(i-10, i):
                        if price_highs.iloc[j] == recent_data['high'].iloc[j]:
                            prev_high_idx = j
                            break
                    
                    if prev_high_idx is not None:
                        if (recent_data['high'].iloc[i] > recent_data['high'].iloc[prev_high_idx] and
                            recent_data['RSI'].iloc[i] < recent_data['RSI'].iloc[prev_high_idx]):
                            patterns['divergencias'].append({
                                'tipo': 'bearish',
                                'preco': recent_data['high'].iloc[i],
                                'timestamp': recent_data.index[i]
                            })
        
        return patterns
    
    def gerar_grafico_multi_timeframe(self, symbol: str, timeframes: List[str] = None, 
                                    niveis_operacionais: Dict = None) -> str:
        """Gera gráfico multi-timeframe com estrutura específica"""
        if timeframes is None:
            timeframes = ['15m', '1h']
        
        plt.style.use(self.style)
        fig = plt.figure(figsize=(20, 16))
        
        # Estrutura específica: 2 gráficos principais + 2 volumes + RSI + Análise
        gs = GridSpec(4, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # Coletar dados para cada timeframe
        dados_tf = {}
        for tf in timeframes:
            df = self.obter_dados_binance(symbol, tf, limit=300)
            if df is not None and not df.empty:
                df = self.calcular_indicadores_completos(df)
                dados_tf[tf] = df
        
        # Gráficos principais dinâmicos baseados nos timeframes fornecidos
        tf_keys = list(dados_tf.keys())
        
        # Gráfico Principal (primeiro timeframe): Candles + EMAs + Bollinger + S/R + Níveis operacionais
        if len(tf_keys) > 0:
            tf1 = tf_keys[0]
            ax_tf1 = fig.add_subplot(gs[0, :2])
            self._plot_candlestick_completo(ax_tf1, dados_tf[tf1], tf1, symbol, niveis_operacionais)
            
            # Volume (primeiro timeframe): Barras de volume + Volume médio
            ax_vol_tf1 = fig.add_subplot(gs[0, 2])
            self._plot_volume_indicators(ax_vol_tf1, dados_tf[tf1], tf1)
        
        # Gráfico Principal (segundo timeframe): Candles + EMAs + Bollinger + S/R + Níveis operacionais
        if len(tf_keys) > 1:
            tf2 = tf_keys[1]
            ax_tf2 = fig.add_subplot(gs[1, :2])
            self._plot_candlestick_completo(ax_tf2, dados_tf[tf2], tf2, symbol, niveis_operacionais)
            
            # Volume (segundo timeframe): Barras de volume + Volume médio
            ax_vol_tf2 = fig.add_subplot(gs[1, 2])
            self._plot_volume_indicators(ax_vol_tf2, dados_tf[tf2], tf2)
        
        # RSI Multi-Timeframe: RSI consolidado com linhas de referência
        ax_rsi = fig.add_subplot(gs[2, :])
        self._plot_rsi_multi_timeframe(ax_rsi, dados_tf, symbol)
        
        # Análise Consolidada: Tabela com tendências, RSI, volume por timeframe
        ax_analise = fig.add_subplot(gs[3, :])
        self._plot_analise_consolidada(ax_analise, dados_tf, symbol)
        
        # Salvar gráfico
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.output_dir}{symbol}_multi_tf_{timestamp}.png"
        
        plt.suptitle(f'SNE RADAR - {symbol} | ANÁLISE MULTI-TIMEFRAME PROFISSIONAL', 
                    fontsize=20, color='white', weight='bold', y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(filename, dpi=150, bbox_inches='tight', 
                   facecolor='#0a0a0a', edgecolor='white', pad_inches=0.3)
        plt.close()
        
        print(f"✅ Gráfico multi-timeframe salvo: {filename}")
        return filename
    
    def _plot_candlestick_completo(self, ax, df: pd.DataFrame, timeframe: str, 
                                 symbol: str, niveis_operacionais: Dict = None):
        """Plota candlestick usando a mesma lógica do comando R mas mantendo especificações"""
        # Limpar eixo
        ax.clear()
        
        # Verificar se temos dados válidos
        if df is None or df.empty:
            ax.text(0.5, 0.5, 'Dados não disponíveis', ha='center', va='center', 
                   transform=ax.transAxes, color='white', fontsize=12)
            ax.set_title(f'{symbol} | {timeframe.upper()} - SEM DADOS', color='white')
            return
        
        print(f"   📊 Plotando {len(df)} candles para {timeframe}")
        
        # Debug: Verificar dados
        print(f"   🔍 Debug - Primeiros 3 candles:")
        for i, (timestamp, row) in enumerate(df.head(3).iterrows()):
            print(f"      Candle {i}: O={row['open']:.2f} H={row['high']:.2f} L={row['low']:.2f} C={row['close']:.2f}")
        
        # Plotar candles manualmente com especificações melhoradas (sem dependências externas)
        candles_plotados = 0
        for i, (timestamp, row) in enumerate(df.iterrows()):
            # Determinar cor baseada na direção do candle
            if row['close'] >= row['open']:
                color = '#00ff00'  # Verde para alta
                edge_color = '#00cc00'
            else:
                color = '#ff0000'  # Vermelho para baixa
                edge_color = '#cc0000'
            
            # Corpo do candle
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['open'], row['close'])
            
            if body_height > 0:
                # Candle com corpo
                ax.bar(i, body_height, bottom=body_bottom, color=color, alpha=0.9, 
                      width=0.6, edgecolor=edge_color, linewidth=0.5)
                candles_plotados += 1
            else:
                # Doji - linha horizontal
                ax.plot([i-0.3, i+0.3], [row['close'], row['close']], 
                       color=color, linewidth=2, alpha=0.9)
                candles_plotados += 1
            
            # Sombras (wick)
            ax.plot([i, i], [row['low'], row['high']], color=edge_color, 
                   linewidth=1, alpha=0.8)
        
        print(f"   ✅ {candles_plotados} candles plotados para {timeframe}")
        
        # Configurar limites do eixo Y para garantir visibilidade
        if len(df) > 0:
            min_price = df[['low']].min().min()
            max_price = df[['high']].max().max()
            margin = (max_price - min_price) * 0.05
            ax.set_ylim(min_price - margin, max_price + margin)
        
        # Debug: Verificar médias móveis
        print(f"   🔍 Debug - Médias móveis:")
        print(f"      EMA8: {df['EMA8'].iloc[-1] if not df['EMA8'].isna().all() else 'N/A'}")
        print(f"      EMA21: {df['EMA21'].iloc[-1] if not df['EMA21'].isna().all() else 'N/A'}")
        print(f"      SMA50: {df['SMA50'].iloc[-1] if not df['SMA50'].isna().all() else 'N/A'}")
        print(f"      SMA200: {df['SMA200'].iloc[-1] if not df['SMA200'].isna().all() else 'N/A'}")
        
        # Médias móveis com especificações completas - usar índices numéricos
        if not df['EMA8'].isna().all():
            print(f"   📈 Plotando EMA8 com cor {self.colors['ema8']}")
            ax.plot(range(len(df)), df['EMA8'], color=self.colors['ema8'], linewidth=1.5, label='EMA 8', alpha=0.9)
        if not df['EMA21'].isna().all():
            print(f"   📈 Plotando EMA21 com cor {self.colors['ema21']}")
            ax.plot(range(len(df)), df['EMA21'], color=self.colors['ema21'], linewidth=1.5, label='EMA 21', alpha=0.9)
        if not df['SMA50'].isna().all():
            print(f"   📈 Plotando SMA50 com cor {self.colors['sma50']}")
            ax.plot(range(len(df)), df['SMA50'], color=self.colors['sma50'], linewidth=1, label='SMA 50', alpha=0.7)
        if not df['SMA200'].isna().all():
            print(f"   📈 Plotando SMA200 com cor {self.colors['sma200']}")
            ax.plot(range(len(df)), df['SMA200'], color=self.colors['sma200'], linewidth=1, label='SMA 200', alpha=0.7)
        
        # Bollinger Bands - usar índices numéricos
        if not df['BB_upper'].isna().all():
            ax.plot(range(len(df)), df['BB_upper'], color=self.colors['bb_upper'], linewidth=0.8, alpha=0.5, linestyle='--')
            ax.plot(range(len(df)), df['BB_lower'], color=self.colors['bb_lower'], linewidth=0.8, alpha=0.5, linestyle='--')
            ax.fill_between(range(len(df)), df['BB_upper'], df['BB_lower'], 
                           color='gray', alpha=0.1)
        
        # Suportes e resistências
        sr_data = self.calcular_suportes_resistencias(df)
        
        # Resistências
        for i, res in enumerate(sr_data['resistencias'][:3]):
            ax.axhline(y=res, color=self.colors['resistance'], linestyle=':', 
                      linewidth=1.5, alpha=0.7, label=f'R{i+1}' if i == 0 else "")
        
        # Suportes
        for i, sup in enumerate(sr_data['suportes'][:3]):
            ax.axhline(y=sup, color=self.colors['support'], linestyle=':', 
                      linewidth=1.5, alpha=0.7, label=f'S{i+1}' if i == 0 else "")
        
        # Níveis operacionais com especificações completas
        if niveis_operacionais:
            if niveis_operacionais.get('entry'):
                ax.axhline(y=niveis_operacionais['entry'], color=self.colors['entry'], 
                          linestyle='--', linewidth=2, alpha=0.9, label=f'Entry: ${niveis_operacionais["entry"]:,.2f}')
            if niveis_operacionais.get('stop'):
                ax.axhline(y=niveis_operacionais['stop'], color=self.colors['stop'], 
                          linestyle='--', linewidth=2, alpha=0.9, label=f'Stop: ${niveis_operacionais["stop"]:,.2f}')
            if niveis_operacionais.get('tp1'):
                ax.axhline(y=niveis_operacionais['tp1'], color=self.colors['tp'], 
                          linestyle='--', linewidth=1.5, alpha=0.8, label=f'TP1: ${niveis_operacionais["tp1"]:,.2f}')
            if niveis_operacionais.get('tp2'):
                ax.axhline(y=niveis_operacionais['tp2'], color=self.colors['tp'], 
                          linestyle='--', linewidth=1.5, alpha=0.6, label=f'TP2: ${niveis_operacionais["tp2"]:,.2f}')
        
        # Fibonacci (apenas para timeframes maiores)
        if timeframe in ['4h', '1d', '1w']:
            fib_levels = self.calcular_fibonacci(df)
            for level, price in fib_levels.items():
                if level in ['38.2%', '50%', '61.8%']:
                    ax.axhline(y=price, color=self.colors['fibonacci'], 
                              linestyle='-.', linewidth=1, alpha=0.6, 
                              label=f'Fib {level}' if level == '38.2%' else "")
        
        # Adicionar zonas de demanda e oferta
        self._adicionar_zonas_demanda_oferta(ax, df)
        
        # Configurar eixo X com timestamps corretos
        if len(df) > 0:
            # Criar labels para o eixo X (mostrar apenas algumas datas para não sobrecarregar)
            step = max(1, len(df) // 8)  # Máximo 8 labels
            x_positions = range(0, len(df), step)
            x_labels = [df.index[i].strftime('%d/%m %H:%M') for i in x_positions]
            
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
        
        # Configurar eixo
        ax.set_title(f'{symbol} | {timeframe.upper()}', color='white', fontsize=12, weight='bold')
        ax.set_ylabel('Preço (USDT)', color='white', fontsize=10)
        ax.tick_params(axis='both', colors='white', labelsize=9)
        ax.grid(True, alpha=0.3, color='gray')
        
        # Configurar fundo do eixo
        ax.set_facecolor('#1a1a1a')
        
        # Remover bordas desnecessárias
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        
        # Forçar atualização do gráfico
        ax.figure.canvas.draw()
        
        # Adicionar legenda apenas se houver elementos para mostrar
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc='upper left', fontsize=8, framealpha=0.9, 
                     facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
    
    def _adicionar_zonas_demanda_oferta(self, ax, df: pd.DataFrame):
        """Adiciona zonas de demanda e oferta baseadas em clusters de volume"""
        try:
            # Calcular clusters de volume (áreas com alto volume)
            volume_threshold = df['volume'].quantile(0.8)  # Top 20% de volume
            
            # Identificar zonas de alta demanda (alto volume + preço baixo)
            zonas_demanda = []
            zonas_oferta = []
            
            for i in range(len(df)):
                if df['volume'].iloc[i] > volume_threshold:
                    preco_medio = (df['high'].iloc[i] + df['low'].iloc[i]) / 2
                    
                    # Se o preço fechou próximo ao mínimo, é zona de demanda
                    if df['close'].iloc[i] <= df['low'].iloc[i] * 1.01:
                        zonas_demanda.append({
                            'preco': preco_medio,
                            'volume': df['volume'].iloc[i],
                            'index': i
                        })
                    
                    # Se o preço fechou próximo ao máximo, é zona de oferta
                    elif df['close'].iloc[i] >= df['high'].iloc[i] * 0.99:
                        zonas_oferta.append({
                            'preco': preco_medio,
                            'volume': df['volume'].iloc[i],
                            'index': i
                        })
            
            # Plotar zonas de demanda (verde) - apenas as mais recentes e relevantes
            zonas_demanda_relevantes = sorted(zonas_demanda, key=lambda x: x['volume'], reverse=True)[:3]
            for i, zona in enumerate(zonas_demanda_relevantes):
                ax.axhline(y=zona['preco'], color='green', linestyle='-', 
                          linewidth=2, alpha=0.7, label='Zona Demanda' if i == 0 else "")
                
                # Adicionar texto apenas para a zona mais forte
                if i == 0:
                    ax.text(zona['index'], zona['preco'], f'DEMANDA\nVol: {zona["volume"]:.0f}', 
                           fontsize=7, color='green', weight='bold',
                           ha='center', va='bottom',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.4))
            
            # Plotar zonas de oferta (vermelho) - apenas as mais recentes e relevantes
            zonas_oferta_relevantes = sorted(zonas_oferta, key=lambda x: x['volume'], reverse=True)[:3]
            for i, zona in enumerate(zonas_oferta_relevantes):
                ax.axhline(y=zona['preco'], color='red', linestyle='-', 
                          linewidth=2, alpha=0.7, label='Zona Oferta' if i == 0 else "")
                
                # Adicionar texto apenas para a zona mais forte
                if i == 0:
                    ax.text(zona['index'], zona['preco'], f'OFERTA\nVol: {zona["volume"]:.0f}', 
                           fontsize=7, color='red', weight='bold',
                           ha='center', va='top',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.4))
            
        except Exception as e:
            print(f"⚠️ Erro ao adicionar zonas de demanda/oferta: {e}")
    
    def _plot_volume_indicators(self, ax, df: pd.DataFrame, timeframe: str):
        """Plota indicadores de volume e momentum"""
        # Limpar eixo
        ax.clear()
        
        # Verificar se temos dados válidos
        if df is None or df.empty:
            ax.text(0.5, 0.5, 'Volume não disponível', ha='center', va='center', 
                   transform=ax.transAxes, color='white', fontsize=10)
            ax.set_title(f'Volume | {timeframe} - SEM DADOS', color='white')
            return
        
        print(f"   📊 Plotando volume para {timeframe}: {len(df)} pontos")
        
        # Volume com especificações completas (cores baseadas na direção do candle)
        colors = []
        for _, row in df.iterrows():
            if row['close'] >= row['open']:
                colors.append(self.colors['volume_up'])
            else:
                colors.append(self.colors['volume_down'])
        
        # Plotar barras de volume com especificações completas
        x_positions = range(len(df))
        ax.bar(x_positions, df['volume'], color=colors, alpha=0.7, width=0.8, edgecolor='black', linewidth=0.3)
        
        # Configurar limites do eixo Y para garantir visibilidade
        if len(df) > 0:
            max_volume = df['volume'].max()
            ax.set_ylim(0, max_volume * 1.1)  # 10% de margem no topo
        
        # Volume médio com especificações completas - usar índices numéricos
        if not df['Volume_MA20'].isna().all():
            ax.plot(range(len(df)), df['Volume_MA20'], color='yellow', linewidth=1.5, alpha=0.8, label='Vol MA20')
        
        # Volume médio de 50 períodos
        if not df['Volume_MA50'].isna().all():
            ax.plot(range(len(df)), df['Volume_MA50'], color='orange', linewidth=1, alpha=0.6, label='Vol MA50')
        
        # Adicionar informações de volume atual
        volume_atual = df['volume'].iloc[-1]
        volume_media_20 = df['Volume_MA20'].iloc[-1] if not df['Volume_MA20'].isna().all() else volume_atual
        volume_ratio = volume_atual / volume_media_20 if volume_media_20 > 0 else 1
        
        # Status do volume
        if volume_ratio > 1.5:
            status_volume = "ALTO"
            cor_status = "green"
        elif volume_ratio > 0.8:
            status_volume = "NORMAL"
            cor_status = "yellow"
        else:
            status_volume = "BAIXO"
            cor_status = "red"
        
        ax.set_title(f'Volume | {timeframe}\nAtual: {volume_atual:.0f} | Status: {status_volume}', 
                    color='white', fontsize=10)
        ax.tick_params(axis='both', colors='white', labelsize=8)
        ax.grid(True, alpha=0.3, color='gray')
        
        # Configurar fundo do eixo
        ax.set_facecolor('#1a1a1a')
        
        # Remover bordas desnecessárias
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        
        # Forçar atualização do gráfico
        ax.figure.canvas.draw()
        
        # Adicionar legenda apenas se houver elementos para mostrar
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(fontsize=7, framealpha=0.9, facecolor='#1a1a1a', 
                     edgecolor='white', labelcolor='white')
        
        # Adicionar texto com informações de volume
        ax.text(0.02, 0.98, f'Ratio: {volume_ratio:.1f}x\nVol: {volume_atual:.0f}', 
                transform=ax.transAxes, fontsize=8, color=cor_status,
                verticalalignment='top', bbox=dict(boxstyle='round', 
                facecolor='#1a1a1a', alpha=0.8))
        
        # Configurar eixo X do volume
        if len(df) > 0:
            step = max(1, len(df) // 5)  # Menos labels para volume
            x_positions = range(0, len(df), step)
            x_labels = [df.index[i].strftime('%H:%M') for i in x_positions]
            
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=7)
    
    def _plot_indicadores_consolidados(self, ax, dados_tf: Dict):
        """Plota indicadores técnicos consolidados"""
        # RSI para diferentes timeframes
        ax2 = ax.twinx()
        
        for tf, df in dados_tf.items():
            if not df['RSI'].isna().all():
                ax.plot(df['RSI'], label=f'RSI {tf}', linewidth=1.5, alpha=0.8)
        
        # Linhas de referência RSI
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Sobrecompra')
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Sobrevenda')
        ax.axhline(y=50, color='white', linestyle='-', alpha=0.3, label='Neutro')
        
        ax.set_title('RSI Multi-Timeframe', color='white', fontsize=12, weight='bold')
        ax.set_ylabel('RSI', color='white', fontsize=10)
        ax.set_ylim(0, 100)
        ax.tick_params(axis='both', colors='white', labelsize=9)
        ax.grid(True, alpha=0.3, color='gray')
        ax.legend(loc='upper left', fontsize=8, framealpha=0.9, 
                 facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
    
    def _plot_analise_multi_timeframe(self, ax, dados_tf: Dict, symbol: str):
        """Plota análise consolidada multi-timeframe"""
        # Criar tabela de análise
        analise_data = []
        
        for tf, df in dados_tf.items():
            if df.empty:
                continue
                
            # Análise de tendência
            tendencia = "LATERAL"
            if not df['EMA8'].isna().all() and not df['EMA21'].isna().all():
                if df['EMA8'].iloc[-1] > df['EMA21'].iloc[-1]:
                    tendencia = "ALTA"
                elif df['EMA8'].iloc[-1] < df['EMA21'].iloc[-1]:
                    tendencia = "BAIXA"
            
            # RSI atual
            rsi_atual = df['RSI'].iloc[-1] if not df['RSI'].isna().all() else 50
            
            # Volume vs média
            vol_atual = df['volume'].iloc[-1]
            vol_media = df['Volume_MA20'].iloc[-1] if not df['Volume_MA20'].isna().all() else vol_atual
            vol_ratio = vol_atual / vol_media if vol_media > 0 else 1
            
            analise_data.append({
                'Timeframe': tf,
                'Tendência': tendencia,
                'RSI': f"{rsi_atual:.1f}",
                'Volume': f"{vol_ratio:.1f}x",
                'EMA8': f"${df['EMA8'].iloc[-1]:,.0f}" if not df['EMA8'].isna().all() else "N/A",
                'EMA21': f"${df['EMA21'].iloc[-1]:,.0f}" if not df['EMA21'].isna().all() else "N/A"
            })
        
        # Criar tabela visual
        if analise_data:
            headers = ['Timeframe', 'Tendência', 'RSI', 'Volume', 'EMA8', 'EMA21']
            table_data = [[row[h] for h in headers] for row in analise_data]
            
            table = ax.table(cellText=table_data, colLabels=headers,
                           cellLoc='center', loc='center',
                           bbox=[0, 0, 1, 1])
            
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            
            # Colorir células
            for i in range(len(table_data)):
                for j in range(len(headers)):
                    cell = table[(i+1, j)]
                    cell.set_facecolor('#1a1a1a')
                    cell.set_text_props(weight='bold', color='white')
            
            # Cabeçalho
            for j in range(len(headers)):
                cell = table[(0, j)]
                cell.set_facecolor('#333333')
                cell.set_text_props(weight='bold', color='white')
        
        ax.set_title(f'ANÁLISE CONSOLIDADA MULTI-TIMEFRAME | {symbol}', 
                    color='white', fontsize=14, weight='bold')
        ax.axis('off')
    
    def _plot_rsi_multi_timeframe(self, ax, dados_tf: Dict, symbol: str):
        """Plota RSI consolidado com linhas de referência"""
        ax.clear()
        
        # Configurar fundo
        ax.set_facecolor('#1a1a1a')
        ax.set_title(f'RSI MULTI-TIMEFRAME | {symbol}', color='white', fontsize=14, weight='bold')
        
        # Linhas de referência RSI
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Sobrecompra (70)')
        ax.axhline(y=50, color='white', linestyle='-', alpha=0.5, label='Neutro (50)')
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Sobrevenda (30)')
        
        # Plotar RSI para cada timeframe
        colors_rsi = {'15m': '#00bfff', '1h': '#ff8c00', '4h': '#32cd32', '1d': '#ff1493'}
        
        for tf, df in dados_tf.items():
            if 'RSI' in df.columns and not df['RSI'].isna().all():
                ax.plot(range(len(df)), df['RSI'], color=colors_rsi.get(tf, 'white'), 
                       linewidth=2, alpha=0.8, label=f'RSI {tf.upper()}')
        
        # Configurar eixo
        ax.set_ylim(0, 100)
        ax.set_ylabel('RSI', color='white', fontsize=12)
        ax.tick_params(axis='both', colors='white', labelsize=10)
        ax.grid(True, alpha=0.3, color='gray')
        
        # Configurar bordas
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        
        # Legenda
        ax.legend(loc='upper right', fontsize=9, framealpha=0.9, 
                 facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
    
    def _plot_analise_consolidada(self, ax, dados_tf: Dict, symbol: str):
        """Plota tabela com tendências, RSI, volume por timeframe"""
        ax.clear()
        
        # Configurar fundo
        ax.set_facecolor('#1a1a1a')
        ax.set_title(f'ANÁLISE CONSOLIDADA MULTI-TIMEFRAME | {symbol}', 
                    color='white', fontsize=14, weight='bold')
        
        # Preparar dados da tabela
        tabela_dados = []
        headers = ['Timeframe', 'Tendência', 'RSI', 'Volume Status', 'EMA8', 'EMA21', 'Preço Atual']
        
        for tf, df in dados_tf.items():
            if df is not None and not df.empty:
                # Determinar tendência
                if 'EMA8' in df.columns and 'EMA21' in df.columns:
                    ema8_atual = df['EMA8'].iloc[-1]
                    ema21_atual = df['EMA21'].iloc[-1]
                    if ema8_atual > ema21_atual:
                        tendencia = 'ALTA'
                    elif ema8_atual < ema21_atual:
                        tendencia = 'BAIXA'
                    else:
                        tendencia = 'LATERAL'
                else:
                    tendencia = 'N/A'
                
                # RSI atual
                rsi_atual = df['RSI'].iloc[-1] if 'RSI' in df.columns else 'N/A'
                rsi_str = f"{rsi_atual:.1f}" if isinstance(rsi_atual, (int, float)) else str(rsi_atual)
                
                # Status do volume
                volume_atual = df['volume'].iloc[-1]
                volume_media = df['volume'].mean()
                if volume_atual > volume_media * 1.5:
                    vol_status = 'ALTO'
                elif volume_atual < volume_media * 0.5:
                    vol_status = 'BAIXO'
                else:
                    vol_status = 'NORMAL'
                
                # EMAs
                ema8_str = f"{ema8_atual:.2f}" if isinstance(ema8_atual, (int, float)) else 'N/A'
                ema21_str = f"{ema21_atual:.2f}" if isinstance(ema21_atual, (int, float)) else 'N/A'
                
                # Preço atual
                preco_atual = df['close'].iloc[-1]
                preco_str = f"${preco_atual:,.2f}"
                
                tabela_dados.append([
                    tf.upper(),
                    tendencia,
                    rsi_str,
                    vol_status,
                    ema8_str,
                    ema21_str,
                    preco_str
                ])
        
        # Criar tabela
        if tabela_dados:
            tabela = ax.table(cellText=tabela_dados, colLabels=headers,
                            cellLoc='center', loc='center',
                            bbox=[0, 0, 1, 1])
            
            # Configurar estilo da tabela
            tabela.auto_set_font_size(False)
            tabela.set_fontsize(10)
            tabela.scale(1, 2)
            
            # Colorir células baseado no conteúdo
            for i in range(len(tabela_dados)):
                for j in range(len(headers)):
                    cell = tabela[(i+1, j)]
                    cell.set_facecolor('#1a1a1a')
                    cell.set_text_props(weight='bold', color='white')
                    
                    # Colorir tendência
                    if j == 1:  # Coluna tendência
                        if tabela_dados[i][j] == 'ALTA':
                            cell.set_facecolor('#00ff00')
                            cell.set_text_props(color='black')
                        elif tabela_dados[i][j] == 'BAIXA':
                            cell.set_facecolor('#ff0000')
                            cell.set_text_props(color='white')
                    
                    # Colorir RSI
                    elif j == 2:  # Coluna RSI
                        try:
                            rsi_val = float(tabela_dados[i][j])
                            if rsi_val > 70:
                                cell.set_facecolor('#ff4444')
                            elif rsi_val < 30:
                                cell.set_facecolor('#44ff44')
                        except:
                            pass
                    
                    # Colorir volume
                    elif j == 3:  # Coluna volume
                        if tabela_dados[i][j] == 'ALTO':
                            cell.set_facecolor('#ffff00')
                            cell.set_text_props(color='black')
                        elif tabela_dados[i][j] == 'BAIXO':
                            cell.set_facecolor('#ff8800')
                            cell.set_text_props(color='white')
            
            # Cabeçalho
            for j in range(len(headers)):
                cell = tabela[(0, j)]
                cell.set_facecolor('#333333')
                cell.set_text_props(weight='bold', color='white')
        
        ax.axis('off')


def gerar_grafico_multi_timeframe_profissional(symbol: str, timeframes: List[str] = None, 
                                             niveis_operacionais: Dict = None) -> str:
    """
    Função principal para gerar gráfico multi-timeframe profissional
    
    Args:
        symbol: Par a analisar (ex: 'BTCUSDT')
        timeframes: Lista de timeframes (ex: ['15m', '1h', '4h', '1d'])
        niveis_operacionais: Dict com níveis de entrada, stop, TPs
    
    Returns:
        Caminho do arquivo gerado
    """
    grafico_mtf = GraficoMultiTimeframe()
    return grafico_mtf.gerar_grafico_multi_timeframe(symbol, timeframes, niveis_operacionais)


if __name__ == "__main__":
    # Teste do sistema
    print("🧪 TESTANDO GRÁFICO MULTI-TIMEFRAME PROFISSIONAL")
    print("=" * 60)
    
    # Exemplo de níveis operacionais
    niveis_exemplo = {
        'entry': 106500,
        'stop': 106000,
        'tp1': 107000,
        'tp2': 107500,
        'tp3': 108000
    }
    
    # Gerar gráfico
    arquivo = gerar_grafico_multi_timeframe_profissional(
        symbol='BTCUSDT',
        timeframes=['15m', '1h', '4h', '1d'],
        niveis_operacionais=niveis_exemplo
    )
    
    print(f"✅ Gráfico gerado: {arquivo}")
    print("🎯 Sistema multi-timeframe profissional implementado!")

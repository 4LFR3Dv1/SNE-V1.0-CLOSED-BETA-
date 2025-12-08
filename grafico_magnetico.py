#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRÁFICO MAGNÉTICO SNE RADAR
Executor Magnético para estratégia de redução de volume e operação por campo magnético dominante
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import mplfinance as mpf
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import os
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore', category=UserWarning, message='.*tight_layout.*')


class ExecutorMagnetico:
    """Classe para gerar gráficos magnéticos especializados"""
    
    def __init__(self):
        self.figsize = (18, 12)
        self.output_dir = 'reports/magnetico/'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Paleta de cores magnética
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
            'volume_azul': '#0066cc'    # Campo de concentração
        }
    
    def obter_dados_candlestick(self, symbol, interval="5m", limit=200):
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
            
            return {
                'poc': float(poc),
                'val': float(val),
                'vah': float(vah),
                'campo_dinamico': float(df['Campo_Dinamico'].iloc[-1]),
                'campo_dinamico_tendencia': 'expansao' if df['Campo_Dinamico'].iloc[-1] > df['Campo_Dinamico_MA'].iloc[-1] else 'compressao',
                'zonas_vacuo': df['Zona_Vacuo'].iloc[-20:].tolist()  # Últimas 20 zonas
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
    
    def gerar_grafico_magnetico(self, symbol, interval="5m", niveis_dict=None, 
                              sr_data=None, resultado_analise=None):
        """
        Gera gráfico magnético especializado
        
        Args:
            symbol: Par a analisar
            interval: Timeframe (recomendado 5m para timing magnético)
            niveis_dict: Níveis operacionais do Motor Renan
            sr_data: Dados de suporte/resistência
            resultado_analise: Resultado completo da análise
        """
        print(f"🧲 Coletando dados magnéticos para {symbol} ({interval})...")
        
        # Obter dados
        df = self.obter_dados_candlestick(symbol, interval)
        if df is None or df.empty:
            print("❌ Erro ao obter dados magnéticos")
            return None
        
        # Calcular campos magnéticos
        campos = self.calcular_campos_magneticos(df)
        if campos is None:
            print("❌ Erro ao calcular campos magnéticos")
            return None
        
        # Configurar estilo magnético
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
            facecolor=self.cores['fundo'],
            edgecolor='#ffffff',
            figcolor=self.cores['fundo'],
            gridcolor='#333333'
        )
        
        # Preparar plots magnéticos (apenas essenciais)
        apds = []
        
        # EMAs magnéticas (fluxo visual claro)
        apds.append(mpf.make_addplot(df['EMA8'], color=self.cores['ema8_ciano'], 
                                   width=2, label='EMA8 (Fluxo)'))
        apds.append(mpf.make_addplot(df['EMA21'], color=self.cores['ema21_dourado'], 
                                   width=2, label='EMA21 (Campo)'))
        
        # SMA200 (estrutura de longo prazo)
        if not df['SMA200'].isna().all():
            apds.append(mpf.make_addplot(df['SMA200'], color=self.cores['sma200_magenta'], 
                                       width=1.5, alpha=0.7, label='SMA200 (Estrutura)'))
        
        # PSAR (timing magnético - apenas últimos pontos)
        if 'PSAR' in df.columns:
            psar_plot = df['PSAR'].copy()
            psar_plot.iloc[:-10] = np.nan  # Apenas últimos 10 pontos
            apds.append(mpf.make_addplot(psar_plot, color=self.cores['psar_pontos'], 
                                       width=0.5, alpha=0.8, type='scatter', 
                                       markersize=4, label='PSAR (Timing)'))
        
        # Criar figura magnética
        fig, axes = mpf.plot(
            df,
            type='candle',
            style=s,
            title='',
            ylabel='Preço (USDT)',
            volume=True,
            ylabel_lower='Volume Magnético',
            addplot=apds,
            figsize=self.figsize,
            returnfig=True,
            warn_too_much_data=300
        )
        
        # Adicionar campos magnéticos visuais
        ax = axes[0]
        self._adicionar_campos_magneticos(ax, df, campos, niveis_dict, sr_data)
        
        # Adicionar título magnético
        self._adicionar_titulo_magnetico(fig, ax, symbol, interval, campos)
        
        # Adicionar legenda magnética
        self._adicionar_legenda_magnetica(ax)
        
        # Adicionar subpainel de campo dinâmico
        self._adicionar_subpainel_campo_dinamico(fig, df, campos)
        
        # Salvar gráfico magnético
        filename = self._salvar_grafico_magnetico(symbol, interval)
        
        plt.close()
        
        print(f"✅ Gráfico magnético salvo: {filename}")
        return filename
    
    def _adicionar_campos_magneticos(self, ax, df, campos, niveis_dict, sr_data):
        """Adiciona campos magnéticos horizontais (LMH) e zonas de vácuo (ZV)"""
        try:
            # Campos Magnéticos Horizontais (LMH)
            val = campos['val']
            vah = campos['vah']
            poc = campos['poc']
            
            # LMH Azul (compressão) - VAL até POC
            ax.axhspan(val, poc, alpha=0.15, color=self.cores['lmh_azul'], 
                     label=f'LMH Azul (Compressão): ${val:.2f}-${poc:.2f}')
            
            # LMH Vermelho (expansão) - POC até VAH
            ax.axhspan(poc, vah, alpha=0.15, color=self.cores['lmh_vermelho'], 
                     label=f'LMH Vermelho (Expansão): ${poc:.2f}-${vah:.2f}')
            
            # Linhas de referência LMH
            ax.axhline(y=val, color=self.cores['lmh_azul'], linestyle='--', 
                      linewidth=1.5, alpha=0.8, label=f'VAL: ${val:.2f}')
            ax.axhline(y=poc, color='white', linestyle='-', 
                      linewidth=2, alpha=0.9, label=f'POC: ${poc:.2f}')
            ax.axhline(y=vah, color=self.cores['lmh_vermelho'], linestyle='--', 
                      linewidth=1.5, alpha=0.8, label=f'VAH: ${vah:.2f}')
            
            # Zonas de Vácuo (ZV) - áreas sem estrutura magnética
            zonas_vacuo = campos['zonas_vacuo']
            for i, zona in enumerate(zonas_vacuo[-10:]):  # Últimas 10 zonas
                if zona == 1:  # Zona de vácuo ativa
                    # Criar faixa semi-transparente preta
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
            
        except Exception as e:
            print(f"Erro ao adicionar campos magnéticos: {e}")
    
    def _adicionar_titulo_magnetico(self, fig, ax, symbol, interval, campos):
        """Adiciona título magnético especializado"""
        try:
            timestamp_grafico = datetime.now().strftime('%d/%m/%Y %H:%M')
            campo_dinamico = campos['campo_dinamico']
            tendencia_campo = campos['campo_dinamico_tendencia']
            
            # Emoji baseado na tendência do campo
            emoji_campo = '🧲' if tendencia_campo == 'expansao' else '⚡'
            
            fig.suptitle(
                f'{emoji_campo} SNE RADAR MAGNÉTICO - {symbol} ({interval})',
                fontsize=20,
                color='white',
                weight='bold',
                y=0.98
            )
            
            # Subtítulo com informações magnéticas
            ax.text(
                0.5, 1.02,
                f'Campo Dinâmico: {campo_dinamico:.4f} | Tendência: {tendencia_campo.upper()} | {timestamp_grafico}',
                transform=ax.transAxes,
                fontsize=12,
                color='white',
                ha='center',
                weight='bold'
            )
            
            # Marca d'água magnética
            ax.text(
                0.98, 0.02,
                'EXECUTOR MAGNÉTICO',
                transform=ax.transAxes,
                fontsize=10,
                color='white',
                alpha=0.3,
                ha='right',
                va='bottom',
                style='italic'
            )
            
        except Exception as e:
            print(f"Erro ao adicionar título magnético: {e}")
    
    def _adicionar_legenda_magnetica(self, ax):
        """Adiciona legenda magnética hierarquizada"""
        try:
            legend = ax.legend(
                loc='center left',
                bbox_to_anchor=(1.02, 0.5),
                fontsize=9,
                framealpha=0.9,
                facecolor=self.cores['fundo'],
                edgecolor='white',
                labelcolor='white',
                ncol=1,
                title='CAMPOS MAGNÉTICOS',
                title_fontsize=10
            )
            legend.get_title().set_color('white')
            
        except Exception as e:
            print(f"Erro ao adicionar legenda magnética: {e}")
    
    def _adicionar_subpainel_campo_dinamico(self, fig, df, campos):
        """Adiciona subpainel com campo dinâmico de pressão"""
        try:
            # Criar subpainel para campo dinâmico
            gs = GridSpec(4, 1, figure=fig, hspace=0.1)
            
            # Subpainel do campo dinâmico
            ax_campo = fig.add_subplot(gs[3, 0])
            
            # Plotar campo dinâmico
            campo_dinamico = df['Campo_Dinamico']
            campo_ma = df['Campo_Dinamico_MA']
            
            ax_campo.plot(campo_dinamico.index, campo_dinamico, 
                         color=self.cores['ema8_ciano'], linewidth=1.5, label='Campo Dinâmico')
            ax_campo.plot(campo_ma.index, campo_ma, 
                         color=self.cores['ema21_dourado'], linewidth=1, alpha=0.7, label='Média')
            
            # Linha zero
            ax_campo.axhline(y=0, color='white', linestyle='-', alpha=0.5)
            
            # Configurar subpainel
            ax_campo.set_title('Campo Dinâmico de Pressão (EMA8-EMA21)', 
                              color='white', fontsize=10, pad=10)
            ax_campo.set_ylabel('Pressão', color='white', fontsize=9)
            ax_campo.tick_params(axis='both', colors='white', labelsize=8)
            ax_campo.set_facecolor(self.cores['fundo'])
            ax_campo.grid(True, alpha=0.3, color='gray')
            
            # Legenda do subpainel
            ax_campo.legend(fontsize=8, loc='upper right', 
                          facecolor=self.cores['fundo'], 
                          edgecolor='white', labelcolor='white')
            
        except Exception as e:
            print(f"Erro ao adicionar subpainel campo dinâmico: {e}")
    
    def _salvar_grafico_magnetico(self, symbol, interval):
        """Salva o gráfico magnético"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.output_dir}{symbol}_{interval}_{timestamp}_magnetico.png"
            
            plt.tight_layout(rect=[0, 0, 0.85, 0.96])
            plt.savefig(
                filename,
                dpi=150,
                bbox_inches='tight',
                facecolor=self.cores['fundo'],
                edgecolor='white',
                pad_inches=0.2
            )
            
            return filename
            
        except Exception as e:
            print(f"Erro ao salvar gráfico magnético: {e}")
            return None


def gerar_grafico_magnetico_completo(symbol, interval="5m", niveis_dict=None, 
                                    sr_data=None, resultado_analise=None):
    """
    Função principal para gerar gráfico magnético completo
    
    Args:
        symbol: Par a analisar
        interval: Timeframe (recomendado 5m)
        niveis_dict: Níveis operacionais
        sr_data: Dados S/R
        resultado_analise: Análise completa
    
    Returns:
        Caminho do arquivo gerado
    """
    executor = ExecutorMagnetico()
    return executor.gerar_grafico_magnetico(
        symbol=symbol,
        interval=interval,
        niveis_dict=niveis_dict,
        sr_data=sr_data,
        resultado_analise=resultado_analise
    )


if __name__ == "__main__":
    # Teste do executor magnético
    print("🧲 Testando Executor Magnético...")
    
    executor = ExecutorMagnetico()
    filename = executor.gerar_grafico_magnetico("BTCUSDT", "5m")
    
    if filename:
        print(f"✅ Teste concluído: {filename}")
    else:
        print("❌ Erro no teste")

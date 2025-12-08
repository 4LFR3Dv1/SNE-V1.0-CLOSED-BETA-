#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMANDO MAG TRADICIONAL SNE
Gera gráficos magnéticos tradicionais com candlesticks e análise técnica
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import requests

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def obter_dados_binance(symbol: str, timeframe: str = "4h", limit: int = 200):
    """Obtém dados da Binance"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": limit
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data:
            return None
            
        # Processar dados
        timestamps = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for candle in data:
            timestamps.append(datetime.fromtimestamp(candle[0] / 1000))
            opens.append(float(candle[1]))
            highs.append(float(candle[2]))
            lows.append(float(candle[3]))
            closes.append(float(candle[4]))
            volumes.append(float(candle[5]))
        
        return {
            'timestamps': timestamps,
            'opens': opens,
            'highs': highs,
            'lows': lows,
            'closes': closes,
            'volumes': volumes
        }
        
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        return None


def calcular_medias_moveis(precos, periodos):
    """Calcula médias móveis"""
    medias = {}
    for periodo in periodos:
        if len(precos) >= periodo:
            medias[f'EMA{periodo}'] = []
            alpha = 2 / (periodo + 1)
            ema = precos[0]
            medias[f'EMA{periodo}'].append(ema)
            
            for i in range(1, len(precos)):
                ema = alpha * precos[i] + (1 - alpha) * ema
                medias[f'EMA{periodo}'].append(ema)
        else:
            medias[f'EMA{periodo}'] = precos
    
    return medias


def calcular_psar(highs, lows, closes, af=0.02, max_af=0.2):
    """Calcula Parabolic SAR"""
    psar = []
    trend = []
    
    if len(highs) < 2:
        return psar, trend
    
    # Inicializar
    psar.append(lows[0])
    trend.append(1)  # 1 = alta, -1 = baixa
    
    af_current = af
    ep = highs[0]  # Extreme Point
    
    for i in range(1, len(highs)):
        if trend[i-1] == 1:  # Tendência de alta
            psar.append(psar[i-1] + af_current * (ep - psar[i-1]))
            
            # Verificar se deve inverter
            if lows[i] <= psar[i]:
                trend.append(-1)
                psar[i] = ep
                ep = lows[i]
                af_current = af
            else:
                trend.append(1)
                if highs[i] > ep:
                    ep = highs[i]
                    af_current = min(af_current + af, max_af)
        else:  # Tendência de baixa
            psar.append(psar[i-1] + af_current * (ep - psar[i-1]))
            
            # Verificar se deve inverter
            if highs[i] >= psar[i]:
                trend.append(1)
                psar[i] = ep
                ep = highs[i]
                af_current = af
            else:
                trend.append(-1)
                if lows[i] < ep:
                    ep = lows[i]
                    af_current = min(af_current + af, max_af)
    
    return psar, trend


def calcular_volume_profile(highs, lows, volumes, bins=20):
    """Calcula Volume Profile"""
    price_min = min(lows)
    price_max = max(highs)
    price_range = price_max - price_min
    
    # Criar bins de preço
    bin_size = price_range / bins
    bins_prices = [price_min + i * bin_size for i in range(bins + 1)]
    
    # Calcular volume por bin
    volume_by_bin = [0] * bins
    for i in range(len(volumes)):
        bin_index = min(int((highs[i] - price_min) / bin_size), bins - 1)
        volume_by_bin[bin_index] += volumes[i]
    
    # Encontrar POC (Point of Control)
    poc_index = volume_by_bin.index(max(volume_by_bin))
    poc_price = bins_prices[poc_index]
    
    # Calcular VAL e VAH (70% do volume)
    total_volume = sum(volume_by_bin)
    target_volume = total_volume * 0.7
    
    # Encontrar VAL e VAH
    val_price = price_min
    vah_price = price_max
    
    # Implementação simplificada
    return {
        'poc': poc_price,
        'val': price_min + price_range * 0.3,
        'vah': price_min + price_range * 0.7,
        'lmh_azul': (price_min + price_range * 0.2, poc_price),
        'lmh_vermelho': (poc_price, price_min + price_range * 0.8)
    }


def calcular_suportes_resistencias(highs, lows, closes):
    """Calcula níveis de suporte e resistência"""
    # Implementação simplificada
    price_range = max(highs) - min(lows)
    current_price = closes[-1]
    
    # Níveis baseados no preço atual
    s1 = current_price - price_range * 0.1
    s2 = current_price - price_range * 0.2
    s3 = current_price - price_range * 0.3
    
    r1 = current_price + price_range * 0.1
    r2 = current_price + price_range * 0.2
    r3 = current_price + price_range * 0.3
    
    return {
        'S1': s1,
        'S2': s2,
        'S3': s3,
        'R1': r1,
        'R2': r2,
        'R3': r3
    }


def gerar_grafico_magnetico_tradicional(symbol: str, timeframe: str = "4h"):
    """Gera gráfico magnético tradicional"""
    try:
        print(f"INFO: Gerando gráfico magnético tradicional para {symbol} ({timeframe})...")
        
        # Obter dados
        dados = obter_dados_binance(symbol, timeframe)
        if not dados:
            print("ERROR: Erro ao obter dados")
            return None
        
        # Calcular indicadores
        medias = calcular_medias_moveis(dados['closes'], [8, 21, 200])
        psar, trend = calcular_psar(dados['highs'], dados['lows'], dados['closes'])
        volume_profile = calcular_volume_profile(dados['highs'], dados['lows'], dados['volumes'])
        sr_levels = calcular_suportes_resistencias(dados['highs'], dados['lows'], dados['closes'])
        
        # Calcular campo dinâmico (EMA8 - EMA21)
        campo_dinamico = []
        for i in range(len(medias['EMA8'])):
            campo_dinamico.append(medias['EMA8'][i] - medias['EMA21'][i])
        
        # Calcular campo atual e tendência para usar no painel
        campo_atual = campo_dinamico[-1] if campo_dinamico else 0
        tendencia = "EXPANSAO" if campo_atual > 0 else "COMPRESSAO"
        
        # Criar figura com layout melhorado
        fig = plt.figure(figsize=(26, 16), facecolor='#0a0a0a')
        gs = fig.add_gridspec(3, 5, height_ratios=[4, 1, 0.5], width_ratios=[4, 0.8, 0.8, 0.8, 0.8], 
                             hspace=0.15, wspace=0.12)
        
        # Gráfico principal (ocupa mais espaço)
        ax1 = fig.add_subplot(gs[0, 0], facecolor='#0a0a0a')
        ax1.set_facecolor('#0a0a0a')
        
        # Gráfico de campo dinâmico (mais compacto)
        ax2 = fig.add_subplot(gs[1, 0], facecolor='#0a0a0a')
        ax2.set_facecolor('#0a0a0a')
        
        # Painel de informações (lado direito - mais largo)
        ax_info = fig.add_subplot(gs[0, 1:], facecolor='#0a0a0a')
        ax_info.set_facecolor('#0a0a0a')
        ax_info.axis('off')
        
        # Plotar candlesticks melhorados
        for i in range(len(dados['timestamps'])):
            # Cores mais profissionais
            if dados['closes'][i] >= dados['opens'][i]:
                color = '#00ff80'  # Verde para alta
                alpha = 0.8
            else:
                color = '#ff4040'  # Vermelho para baixa
                alpha = 0.8
            
            # Corpo do candle (mais espesso)
            ax1.plot([dados['timestamps'][i], dados['timestamps'][i]], 
                    [dados['opens'][i], dados['closes'][i]], color=color, linewidth=4, alpha=alpha)
            
            # Sombras do candle (mais finas)
            ax1.plot([dados['timestamps'][i], dados['timestamps'][i]], 
                    [dados['lows'][i], dados['highs'][i]], color=color, linewidth=1, alpha=alpha*0.7)
        
        # Plotar médias móveis melhoradas
        ax1.plot(dados['timestamps'], medias['EMA8'], color='#00bfff', linewidth=3, 
                label='EMA8 (Fluxo)', alpha=0.9)
        ax1.plot(dados['timestamps'], medias['EMA21'], color='#ffff00', linewidth=3, 
                label='EMA21 (Campo)', alpha=0.9)
        ax1.plot(dados['timestamps'], medias['EMA200'], color='#ff00ff', linewidth=2, 
                label='SMA200 (Estrutura)', alpha=0.8)
        
        # Plotar PSAR melhorado
        for i in range(len(psar)):
            color = '#ff0000' if trend[i] == -1 else '#00ff00'
            ax1.scatter(dados['timestamps'][i], psar[i], color=color, s=30, alpha=0.8, 
                       edgecolors='white', linewidth=0.5)
        
        # Plotar níveis de volume profile melhorados
        ax1.axhline(y=volume_profile['val'], color='#ffffff', linestyle='-', linewidth=2, alpha=0.9, 
                   label=f'VAL: ${volume_profile["val"]:.2f}')
        ax1.axhline(y=volume_profile['poc'], color='#ffff00', linestyle='-', linewidth=2, alpha=0.9, 
                   label=f'POC: ${volume_profile["poc"]:.2f}')
        ax1.axhline(y=volume_profile['vah'], color='#ffffff', linestyle='-', linewidth=2, alpha=0.9, 
                   label=f'VAH: ${volume_profile["vah"]:.2f}')
        
        # Plotar LMH melhorado
        ax1.axhspan(volume_profile['lmh_azul'][0], volume_profile['lmh_azul'][1], 
                   alpha=0.15, color='#0080ff', label='LMH Azul (Compressão)')
        ax1.axhspan(volume_profile['lmh_vermelho'][0], volume_profile['lmh_vermelho'][1], 
                   alpha=0.15, color='#ff4040', label='LMH Vermelho (Expansão)')
        
        # Plotar suportes e resistências melhorados
        for level, price in sr_levels.items():
            if level.startswith('S'):
                ax1.axhline(y=price, color='#ff8080', linestyle='--', alpha=0.8, linewidth=1.5)
            else:
                ax1.axhline(y=price, color='#ff8080', linestyle='--', alpha=0.8, linewidth=1.5)
        
        # Configurar gráfico principal melhorado
        ax1.set_title(f'SNE RADAR MAGNÉTICO - {symbol} ({timeframe})', color='white', fontsize=18, pad=25, weight='bold')
        ax1.set_ylabel('Preço (USDT)', color='white', fontsize=14, weight='bold')
        ax1.grid(True, alpha=0.2, color='#444444', linestyle='-', linewidth=0.5)
        ax1.tick_params(colors='white', labelsize=11)
        
        # Formatar eixo X melhorado
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax1.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Adicionar bordas ao gráfico
        for spine in ax1.spines.values():
            spine.set_edgecolor('#666666')
            spine.set_linewidth(1)
        
        # === PAINEL DE INFORMAÇÕES MELHORADO ===
        # Título do painel
        ax_info.text(0.05, 0.95, 'CAMPOS MAGNÉTICOS', transform=ax_info.transAxes, 
                    fontsize=16, weight='bold', color='white', ha='left', va='top')
        
        # Informações organizadas em seções com espaçamento melhorado
        y_pos = 0.88
        
        # Seção 1: Médias Móveis
        ax_info.text(0.05, y_pos, 'MÉDIAS MÓVEIS:', transform=ax_info.transAxes, 
                    fontsize=12, weight='bold', color='#00bfff', ha='left', va='top')
        y_pos -= 0.10
        
        ax_info.text(0.05, y_pos, '• EMA8 (Fluxo)', transform=ax_info.transAxes, 
                    fontsize=10, color='#00bfff', ha='left', va='top')
        y_pos -= 0.06
        
        ax_info.text(0.05, y_pos, '• EMA21 (Campo)', transform=ax_info.transAxes, 
                    fontsize=10, color='#ffff00', ha='left', va='top')
        y_pos -= 0.06
        
        ax_info.text(0.05, y_pos, '• SMA200 (Estrutura)', transform=ax_info.transAxes, 
                    fontsize=10, color='#ff00ff', ha='left', va='top')
        y_pos -= 0.12
        
        # Seção 2: Volume Profile
        ax_info.text(0.05, y_pos, 'VOLUME PROFILE:', transform=ax_info.transAxes, 
                    fontsize=12, weight='bold', color='#ffff00', ha='left', va='top')
        y_pos -= 0.10
        
        ax_info.text(0.05, y_pos, f'• VAL: ${volume_profile["val"]:.2f}', transform=ax_info.transAxes, 
                    fontsize=10, color='white', ha='left', va='top')
        y_pos -= 0.06
        
        ax_info.text(0.05, y_pos, f'• POC: ${volume_profile["poc"]:.2f}', transform=ax_info.transAxes, 
                    fontsize=10, color='#ffff00', ha='left', va='top')
        y_pos -= 0.06
        
        ax_info.text(0.05, y_pos, f'• VAH: ${volume_profile["vah"]:.2f}', transform=ax_info.transAxes, 
                    fontsize=10, color='white', ha='left', va='top')
        y_pos -= 0.12
        
        # Seção 3: LMH
        ax_info.text(0.05, y_pos, 'LIQUIDEZ MAGNÉTICA:', transform=ax_info.transAxes, 
                    fontsize=12, weight='bold', color='#0080ff', ha='left', va='top')
        y_pos -= 0.10
        
        ax_info.text(0.05, y_pos, f'• Azul: {volume_profile["lmh_azul"][0]:.0f}-{volume_profile["lmh_azul"][1]:.0f}', 
                    transform=ax_info.transAxes, fontsize=9, color='#0080ff', ha='left', va='top')
        y_pos -= 0.06
        
        ax_info.text(0.05, y_pos, f'• Vermelho: {volume_profile["lmh_vermelho"][0]:.0f}-{volume_profile["lmh_vermelho"][1]:.0f}', 
                    transform=ax_info.transAxes, fontsize=9, color='#ff4040', ha='left', va='top')
        y_pos -= 0.12
        
        # Seção 4: Suportes e Resistências
        ax_info.text(0.05, y_pos, 'S/R LEVELS:', transform=ax_info.transAxes, 
                    fontsize=12, weight='bold', color='#ff8080', ha='left', va='top')
        y_pos -= 0.10
        
        for level, price in sr_levels.items():
            ax_info.text(0.05, y_pos, f'• {level}: ${price:,.0f}', transform=ax_info.transAxes, 
                        fontsize=9, color='#ff8080', ha='left', va='top')
            y_pos -= 0.05
        
        y_pos -= 0.05
        
        # Seção 5: Estado Atual
        ax_info.text(0.05, y_pos, 'ESTADO ATUAL:', transform=ax_info.transAxes, 
                    fontsize=12, weight='bold', color='#00ff80', ha='left', va='top')
        y_pos -= 0.10
        
        ax_info.text(0.05, y_pos, f'• Campo: {campo_atual:.4f}', transform=ax_info.transAxes, 
                    fontsize=10, color='white', ha='left', va='top')
        y_pos -= 0.06
        
        ax_info.text(0.05, y_pos, f'• Tendência: {tendencia}', transform=ax_info.transAxes, 
                    fontsize=10, color='#00ff80' if campo_atual > 0 else '#ff4040', ha='left', va='top')
        
        # Gráfico de campo dinâmico melhorado
        ax2.plot(dados['timestamps'], campo_dinamico, color='#00bfff', linewidth=3, label='Campo Dinâmico', alpha=0.9)
        ax2.axhline(y=0, color='#666666', linestyle='-', alpha=0.7, linewidth=1)
        
        # Preenchimento colorido
        ax2.fill_between(dados['timestamps'], campo_dinamico, 0, 
                        where=[x >= 0 for x in campo_dinamico], color='#00ff80', alpha=0.3, label='Pressão Positiva')
        ax2.fill_between(dados['timestamps'], campo_dinamico, 0, 
                        where=[x < 0 for x in campo_dinamico], color='#ff4040', alpha=0.3, label='Pressão Negativa')
        
        ax2.set_title('Campo Dinâmico de Pressão (EMA8-EMA21)', color='white', fontsize=14, weight='bold', pad=15)
        ax2.set_ylabel('Pressão', color='white', fontsize=12, weight='bold')
        ax2.grid(True, alpha=0.2, color='#444444', linestyle='-', linewidth=0.5)
        ax2.tick_params(colors='white', labelsize=10)
        
        # Formatar eixo X do subplot
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Adicionar bordas ao subplot
        for spine in ax2.spines.values():
            spine.set_edgecolor('#666666')
            spine.set_linewidth(1)
        
        # Adicionar informações dinâmicas melhoradas (já calculadas acima)
        
        # Adicionar texto "EXECUTOR MAGNÉTICO" melhorado
        ax1.text(0.98, 0.02, 'EXECUTOR MAGNÉTICO', transform=ax1.transAxes, 
                ha='right', va='bottom', color='white', fontsize=14, weight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#333333', alpha=0.8))
        
        # Salvar imagem com qualidade melhorada
        os.makedirs('reports/magnetico', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_{timeframe}_{timestamp}_magnetico_melhorado.png"
        caminho = f"reports/magnetico/{filename}"
        
        plt.tight_layout()
        plt.savefig(caminho, dpi=200, facecolor='#0a0a0a', edgecolor='none', bbox_inches='tight')
        plt.close(fig)
        
        print(f"SUCCESS: Gráfico magnético tradicional melhorado salvo: {caminho}")
        print(f"FIELD: Campo dinâmico atual: {campo_atual:.4f}")
        print(f"TREND: Tendência: {tendencia}")
        print(f"LEVELS: Níveis calculados: {len(sr_levels)}")
        print(f"LAYOUT: Interface melhorada com painel lateral")
        
        return caminho
        
    except Exception as e:
        print(f"ERROR: Erro ao gerar gráfico magnético tradicional: {e}")
        import traceback
        traceback.print_exc()
        return None


def executar_comando_mag_tradicional():
    """Executa o comando MAG tradicional"""
    try:
        print("\n🧲 ANÁLISE MAGNÉTICA SNE - SISTEMA TRADICIONAL")
        print("=" * 60)
        print("   Gera gráficos magnéticos tradicionais com candlesticks")
        print("   Inclui EMA, PSAR, Volume Profile e Campos Dinâmicos")
        print("=" * 60)
        
        # 1. Configuração do par
        par = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
        symbol = (par + 'USDT') if par and not par.endswith('USDT') else (par if par else 'BTCUSDT')
        
        # 2. Configuração do timeframe
        print("\n⏰ Timeframes disponíveis:")
        print("   1️⃣ 4h (recomendado)")
        print("   2️⃣ 1h")
        print("   3️⃣ 1d")
        print("   4️⃣ Personalizado")
        
        opcao_tf = input("   Escolha (1-4, Enter para 4h): ").strip()
        
        if opcao_tf == "2":
            timeframe = "1h"
        elif opcao_tf == "3":
            timeframe = "1d"
        elif opcao_tf == "4":
            print("   ⏰ Timeframes disponíveis: 1m, 5m, 15m, 30m, 1h, 4h, 8h, 12h, 1d, 1w, 1M")
            tf_custom = input("   Digite o timeframe desejado (ex: 4h): ").strip()
            timeframe = tf_custom if tf_custom else "4h"
        else:
            timeframe = "4h"
        
        # 3. Gerar gráfico magnético tradicional
        print(f"\n🧲 Gerando gráfico magnético tradicional de {symbol} ({timeframe})...")
        caminho = gerar_grafico_magnetico_tradicional(symbol, timeframe)
        
        if not caminho:
            print("ERROR: Erro ao gerar gráfico magnético tradicional")
            return
        
        # 4. Enviar automaticamente para Telegram
        try:
            from xenos_bot import enviar_foto
            
            print("TELEGRAM: Enviando gráfico magnético tradicional para Telegram...")
            
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            msg = f"""🧲 <b>ANÁLISE MAGNÉTICA SNE TRADICIONAL</b>
📊 {symbol} ({timeframe})
⏰ {timestamp}

🧲 <b>Sistema Magnético Tradicional:</b>
• Candlesticks com análise técnica clássica
• EMA8, EMA21, SMA200 (Fluxo, Campo, Estrutura)
• Parabolic SAR para timing
• Volume Profile (POC, VAL, VAH)
• Campos Dinâmicos de Pressão
• Níveis de Suporte e Resistência
• LMH (Liquidez Magnética Horizontal)

⚡ <b>Análise Técnica:</b>
• Gráfico principal com candlesticks
• Subplot de pressão dinâmica
• Legenda completa de indicadores
• Níveis de preço calculados

🧠 <b>Baseado em:</b>
• Médias móveis exponenciais
• Volume Profile tradicional
• Análise de suporte/resistência
• Campos magnéticos de pressão

🌊 <i>Sistema Magnético SNE Tradicional</i>"""
            
            enviar_foto(caminho, msg)
            print("SUCCESS: Gráfico magnético tradicional enviado para Telegram!")
                
        except ImportError:
            print("WARNING: Módulo Telegram não disponível")
            print(f"SAVED: Gráfico magnético tradicional salvo: {caminho}")
        except Exception as e:
            print(f"ERROR: Erro ao enviar para Telegram: {e}")
            print(f"SAVED: Gráfico magnético tradicional salvo: {caminho}")
        
        print("\nSUCCESS: Análise magnética tradicional gerada com sucesso!")
        
    except KeyboardInterrupt:
        print("\nWARNING: Comando cancelado pelo usuário")
    except Exception as e:
        print(f"\nERROR: Erro no comando magnético tradicional: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    executar_comando_mag_tradicional()

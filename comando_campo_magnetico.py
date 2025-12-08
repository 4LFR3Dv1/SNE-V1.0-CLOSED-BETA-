#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMANDO CAMPO MAGNÉTICO SNE - VERSÃO SIMPLIFICADA
Gera imagem e envia para Telegram
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import requests

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def calcular_atr(precos, periodos=14):
    """Calcula Average True Range para normalização"""
    if len(precos) < periodos + 1:
        return 1.0
    
    tr_values = []
    for i in range(1, len(precos)):
        tr = abs(precos[i] - precos[i-1])
        tr_values.append(tr)
    
    # Calcular média sem numpy
    if tr_values:
        valores_periodo = tr_values[-periodos:]
        return sum(valores_periodo) / len(valores_periodo)
    else:
        return 1.0

def campo_magnetico_continuo(x, polos, k=1.0):
    """
    Calcula densidade de campo magnético contínua
    F(x) = Σ k * (L_i / ((x - P_i)² + ε)) * direcao_i
    """
    eps = 1e-6  # Evitar divisão por zero
    campo_total = 0.0
    
    for polo in polos:
        distancia = abs(x - polo['preco'])
        liquidez = polo['liquidez']
        direcao = polo['direcao']
        
        # Fórmula de campo magnético
        intensidade = k * liquidez / (distancia**2 + eps)
        campo_total += intensidade * direcao
    
    return campo_total

def obter_dados_orderbook(symbol: str):
    """Obtém dados do order book para análise de liquidez"""
    try:
        url = f"https://api.binance.com/api/v3/depth"
        params = {"symbol": symbol, "limit": 1000}
        response = requests.get(url, params=params)
        data = response.json()
        
        bids = [[float(price), float(qty)] for price, qty in data['bids']]
        asks = [[float(price), float(qty)] for price, qty in data['asks']]
        
        return {'bids': bids, 'asks': asks}
    except:
        return {'bids': [], 'asks': []}

def calcular_cvd(candles):
    """Calcula Cumulative Volume Delta"""
    cvd = 0
    cvd_values = []
    
    for candle in candles:
        close = float(candle[4])
        open_price = float(candle[1])
        volume = float(candle[5])
        
        # Delta baseado na direção do candle
        if close > open_price:
            delta = volume  # Compra
        elif close < open_price:
            delta = -volume  # Venda
        else:
            delta = 0  # Neutro
        
        cvd += delta
        cvd_values.append(cvd)
    
    return cvd_values

def gerar_campo_magnetico_simples(symbol: str, timeframe: str = '1h'):
    """
    Gera campo magnético intuitivo com topologia energética avançada
    """
    try:
        print(f"🧲 Gerando campo magnético intuitivo para {symbol} ({timeframe})...")
        
        # Obter dados básicos
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": 200
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if not data:
            print("❌ Erro ao obter dados")
            return None
        
        # Processar dados
        precos = [float(candle[4]) for candle in data]  # Close prices
        volumes = [float(candle[5]) for candle in data]  # Volumes
        highs = [float(candle[2]) for candle in data]  # High prices
        lows = [float(candle[3]) for candle in data]  # Low prices
        
        preco_atual = precos[-1]
        preco_min = min(lows)
        preco_max = max(highs)
        
        # Calcular ATR e CVD
        atr = calcular_atr(precos)
        cvd_values = calcular_cvd(data)
        
        # Obter dados do order book
        orderbook = obter_dados_orderbook(symbol)
        
        # Identificar polos magnéticos baseados em liquidez real
        polos_atrativos = []
        polos_repulsivos = []
        
        # Detectar equal highs/lows com janela adaptativa
        janela = max(5, len(precos) // 20)
        
        for i in range(janela, len(precos)-janela):
            # Equal highs (polos repulsivos) - liquidez de venda
            if all(highs[i] >= highs[i-j] for j in range(1, janela+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, janela+1)):
                
                # Calcular força baseada em CVD e volume
                volume_norm = volumes[i] / max(volumes) if max(volumes) > 0 else 0.1
                cvd_norm = abs(cvd_values[i]) / max([abs(v) for v in cvd_values]) if cvd_values else 0.1
                volatilidade = (highs[i] - lows[i]) / precos[i] if precos[i] > 0 else 0.01
                
                # Força magnética baseada em liquidez real
                forca = (volume_norm * cvd_norm * volatilidade * 15) + 0.1
                
                polos_repulsivos.append({
                    'preco': highs[i],
                    'liquidez': forca,
                    'direcao': -1,
                    'tipo': 'EQUAL_HIGH',
                    'volume': volumes[i],
                    'cvd': cvd_values[i]
                })
            
            # Equal lows (polos atrativos) - liquidez de compra
            if all(lows[i] <= lows[i-j] for j in range(1, janela+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, janela+1)):
                
                volume_norm = volumes[i] / max(volumes) if max(volumes) > 0 else 0.1
                cvd_norm = abs(cvd_values[i]) / max([abs(v) for v in cvd_values]) if cvd_values else 0.1
                volatilidade = (highs[i] - lows[i]) / precos[i] if precos[i] > 0 else 0.01
                
                forca = (volume_norm * cvd_norm * volatilidade * 15) + 0.1
                
                polos_atrativos.append({
                    'preco': lows[i],
                    'liquidez': forca,
                    'direcao': 1,
                    'tipo': 'EQUAL_LOW',
                    'volume': volumes[i],
                    'cvd': cvd_values[i]
                })
        
        # Adicionar polos baseados no order book
        if orderbook['bids'] and orderbook['asks']:
            # Concentração de liquidez nos bids (polos atrativos)
            for price, qty in orderbook['bids'][:10]:  # Top 10 bids
                if preco_min <= price <= preco_max:
                    qty_norm = qty / max([q for _, q in orderbook['bids']]) if orderbook['bids'] else 0.1
                    polos_atrativos.append({
                        'preco': price,
                        'liquidez': qty_norm * 0.5,  # Peso menor para order book
                        'direcao': 1,
                        'tipo': 'ORDER_BOOK_BID',
                        'volume': qty,
                        'cvd': 0
                    })
            
            # Concentração de liquidez nos asks (polos repulsivos)
            for price, qty in orderbook['asks'][:10]:  # Top 10 asks
                if preco_min <= price <= preco_max:
                    qty_norm = qty / max([q for _, q in orderbook['asks']]) if orderbook['asks'] else 0.1
                    polos_repulsivos.append({
                        'preco': price,
                        'liquidez': qty_norm * 0.5,  # Peso menor para order book
                        'direcao': -1,
                        'tipo': 'ORDER_BOOK_ASK',
                        'volume': qty,
                        'cvd': 0
                    })
        
        # Combinar todos os polos
        todos_polos = polos_atrativos + polos_repulsivos
        
        # === DETECTAR ZONAS DE INTERESSE HISTÓRICAS ===
        print("INFO: Detectando zonas de interesse históricas...")
        
        zonas_interesse = []
        
        # Detectar topos e bases significativos (últimos 50 candles)
        janela_interesse = min(20, len(precos) // 10)
        candles_recentes = data[-50:] if len(data) >= 50 else data
        
        for i, candle in enumerate(candles_recentes):
            idx_global = len(data) - len(candles_recentes) + i
            
            if idx_global < janela_interesse or idx_global >= len(data) - janela_interesse:
                continue
                
            high = float(candle[2])
            low = float(candle[3])
            volume = float(candle[5])
            
            # Detectar topo significativo (máximo local com volume alto)
            is_top = True
            for j in range(max(0, idx_global-janela_interesse), min(len(data), idx_global+janela_interesse+1)):
                if j != idx_global and float(data[j][2]) >= high:
                    is_top = False
                    break
            
            if is_top and volume > np.mean(volumes) * 1.2:  # Volume 20% acima da média
                zonas_interesse.append({
                    'preco': high,
                    'tipo': 'TOPO',
                    'forca': min(1.0, volume / np.mean(volumes)),
                    'volume': volume,
                    'volume_relativo': volume / np.mean(volumes),
                    'cor': '#ff6b6b',
                    'alpha': 0.3,
                    'indice': idx_global
                })
            
            # Detectar base significativa (mínimo local com volume alto)
            is_base = True
            for j in range(max(0, idx_global-janela_interesse), min(len(data), idx_global+janela_interesse+1)):
                if j != idx_global and float(data[j][3]) <= low:
                    is_base = False
                    break
            
            if is_base and volume > np.mean(volumes) * 1.2:  # Volume 20% acima da média
                zonas_interesse.append({
                    'preco': low,
                    'tipo': 'BASE',
                    'forca': min(1.0, volume / np.mean(volumes)),
                    'volume': volume,
                    'volume_relativo': volume / np.mean(volumes),
                    'cor': '#4ecdc4',
                    'alpha': 0.3,
                    'indice': idx_global
                })
        
        # Criar figura com layout profissional avançado
        # === CONFIGURAÇÃO VISUAL PROFISSIONAL v2.3 ===
        fig = plt.figure(figsize=(24, 20), facecolor='#0a0a0a')
        
        # Criar subplots: campo magnético (principal) + histograma de volume (inferior)
        gs = fig.add_gridspec(2, 1, height_ratios=[4, 1], hspace=0.1)
        ax = fig.add_subplot(gs[0], facecolor='#0a0a0a')
        ax_volume = fig.add_subplot(gs[1], facecolor='#0a0a0a')
        
        # Configurar eixo principal com escala profissional
        ax.set_xlim(preco_min * 0.995, preco_max * 1.005)
        ax.set_ylim(-5, 5)  # Escala expandida para profundidade de campo
        
        # === CAMADA 1: GRADIENTE DINÂMICO MAGNÉTICO ===
        print("INFO: Renderizando gradiente dinâmico...")
        
        # Criar grade de campo
        x_campo = np.linspace(preco_min * 0.995, preco_max * 1.005, 300)
        y_campo = np.linspace(-4, 4, 150)
        X, Y = np.meshgrid(x_campo, y_campo)
        
        # Calcular densidade de campo para cada ponto
        Z = np.zeros_like(X)
        polaridade_global = 0
        
        for i in range(len(x_campo)):
            campo_valor = campo_magnetico_continuo(x_campo[i], todos_polos, k=atr)
            Z[:, i] = np.tanh(campo_valor) * 3  # Normalizar com tanh
            polaridade_global += campo_valor
        
        # Determinar tom emocional global e estado do campo
        polaridade_media = polaridade_global / len(x_campo)
        intensidade_campo = abs(polaridade_media)
        
        # Paleta emocional evolvida baseada no estado do campo
        if polaridade_media > 0.3:  # Altamente Atrativo - Expansão
            estado_campo = "ALTAMENTE_ATRATIVO"
            tom_emocional = "Expansão"
            cores = ['#00ff80', '#00ffaa', '#00ffcc', '#00ffee', '#00ffff', 
                    '#33ffff', '#66ffff', '#99ffff', '#ccffff', '#ffffff']
            cor_base = '#00ff80'
            interpretacao = "Liquidez entrando, 'respiração compradora'"
        elif polaridade_media > 0.1:  # Atrativo - Confiança
            estado_campo = "ATRATIVO"
            tom_emocional = "Confiança"
            cores = ['#0066ff', '#0088ff', '#00aaff', '#00ccff', '#00eeff', 
                    '#33ffff', '#66ffff', '#99ffff', '#ccffff', '#ffffff']
            cor_base = '#0066ff'
            interpretacao = "Campo comprador dominante"
        elif polaridade_media > -0.1:  # Neutro - Suspensão
            estado_campo = "NEUTRO"
            tom_emocional = "Suspensão"
            cores = ['#8080ff', '#9999ff', '#b3b3ff', '#ccccff', '#e6e6ff', 
                    '#ffffff', '#ffe6e6', '#ffcccc', '#ffb3b3', '#ff9999']
            cor_base = '#8080ff'
            interpretacao = "Mercado respirando, indecisão"
        elif polaridade_media > -0.3:  # Levemente Repulsivo - Cautela
            estado_campo = "LEVEMENTE_REPULSIVO"
            tom_emocional = "Cautela"
            cores = ['#ff80ff', '#ff99ff', '#ffb3ff', '#ffccff', '#ffe6ff', 
                    '#ffffff', '#ffe6cc', '#ffcc99', '#ffb366', '#ff9933']
            cor_base = '#ff80ff'
            interpretacao = "Tensão latente"
        else:  # Fortemente Repulsivo - Colapso
            estado_campo = "FORTEMENTE_REPULSIVO"
            tom_emocional = "Colapso"
            cores = ['#ff4040', '#ff6060', '#ff8080', '#ffa0a0', '#ffc0c0', 
                    '#ffe0e0', '#ffffff', '#ffe0e0', '#ffc0c0', '#ffa0a0']
            cor_base = '#ff4040'
            interpretacao = "Expulsão de liquidez, fuga de capital"
        
        cmap_magnetico = LinearSegmentedColormap.from_list('campo_dinamico', cores)
        
        # Renderizar gradiente de campo com profundidade variável
        im = ax.imshow(Z, extent=[preco_min * 0.995, preco_max * 1.005, -5, 5], 
                      cmap=cmap_magnetico, alpha=0.6, aspect='auto', origin='lower')
        
        # === CAMADA 2: ZONAS DE MAGNETIZAÇÃO ===
        print("INFO: Renderizando zonas de magnetização...")
        
        # Zonas de atração (verde suave)
        for polo in polos_atrativos:
            if polo['liquidez'] > 0.3:  # Só zonas significativas
                ax.axvspan(polo['preco'] - atr*0.5, polo['preco'] + atr*0.5, 
                          alpha=0.15, color='#00ff00', zorder=1)
        
        # Zonas de repulsão (vermelho suave)
        for polo in polos_repulsivos:
            if polo['liquidez'] > 0.3:  # Só zonas significativas
                ax.axvspan(polo['preco'] - atr*0.5, polo['preco'] + atr*0.5, 
                          alpha=0.15, color='#ff0000', zorder=1)
        
        # === CAMADA 3: NÚCLEO DE EQUILÍBRIO E ZONAS NEUTRAS ===
        print("INFO: Renderizando núcleo de equilíbrio...")
        
        # Calcular ponto de equilíbrio (onde campo = 0)
        campo_zero = []
        for x in x_campo:
            if abs(campo_magnetico_continuo(x, todos_polos, k=atr)) < 0.1:
                campo_zero.append(x)
        
        nucleo_preco = np.mean(campo_zero) if campo_zero else (preco_min + preco_max) / 2
        
        # Zona de silêncio (faixa branca translúcida)
        ax.axhspan(-0.3, 0.3, xmin=(nucleo_preco - preco_min) / (preco_max - preco_min) - 0.08,
                  xmax=(nucleo_preco - preco_min) / (preco_max - preco_min) + 0.08,
                  color='white', alpha=0.4, zorder=2)
        
        # Zonas neutras (cinza translúcido) onde campo é próximo de zero
        for i in range(0, len(x_campo), 10):
            x_pos = x_campo[i]
            campo_valor = campo_magnetico_continuo(x_pos, todos_polos, k=atr)
            if abs(campo_valor) < 0.05:  # Zona neutra
                ax.axvspan(x_pos - atr*0.1, x_pos + atr*0.1, 
                          alpha=0.1, color='#888888', zorder=1)
        
        # === CAMADA 4: LINHAS DE FLUXO DIRECIONAIS ===
        print("INFO: Renderizando linhas de fluxo direcionais...")
        
        if todos_polos:
            # Conectar polos próximos com fluxo direcional
            for i, polo1 in enumerate(todos_polos):
                for j, polo2 in enumerate(todos_polos[i+1:], i+1):
                    distancia = abs(polo1['preco'] - polo2['preco'])
                    
                    # Só conectar polos próximos (dentro de 3 ATR)
                    if distancia < 3 * atr:
                        # Criar spline suave entre polos
                        x_spline = np.linspace(polo1['preco'], polo2['preco'], 100)
                        
                        # Calcular curva baseada na força dos polos
                        forca_media = (polo1['liquidez'] + polo2['liquidez']) / 2
                        amplitude = min(2.0, forca_media * 3)
                        
                        # Curva orgânica usando função seno modificada
                        y_spline = amplitude * np.sin(np.linspace(0, np.pi, 100))
                        
                        # Cor baseada na direção dos polos
                        if polo1['direcao'] == polo2['direcao']:
                            cor = '#00ff00' if polo1['direcao'] > 0 else '#ff0000'
                            alpha = 0.8
                        else:
                            cor = '#ffff00'  # Campo neutro
                            alpha = 0.6
                        
                        # Espessura baseada na força
                        espessura = max(1, forca_media * 4)
                        
                        ax.plot(x_spline, y_spline, color=cor, alpha=alpha, 
                               linewidth=espessura, zorder=3)
                        
                        # Adicionar setas direcionais
                        for k in range(10, len(x_spline), 20):
                            dx = x_spline[k+1] - x_spline[k]
                            dy = y_spline[k+1] - y_spline[k]
                            ax.annotate('', xy=(x_spline[k+1], y_spline[k+1]), 
                                       xytext=(x_spline[k], y_spline[k]),
                                       arrowprops=dict(arrowstyle='->', color=cor, 
                                                     alpha=0.6, lw=1))
        
        # === CAMADA 5: POLOS COM VIBRAÇÃO DINÂMICA ===
        print("INFO: Renderizando polos com vibração dinâmica...")
        
        # Polos atrativos com vibração em expansão e correlação de volume
        for polo in polos_atrativos:
            # Calcular profundidade baseada na força
            profundidade = min(0.8, polo['liquidez'] * 2)
            
            # Verificar se há correlação com volume alto
            volume_correlacionado = False
            volume_relativo = 1.0
            for zona in zonas_interesse:
                if abs(zona['preco'] - polo['preco']) < (preco_max - preco_min) * 0.01:  # 1% de tolerância
                    volume_correlacionado = True
                    volume_relativo = zona['volume_relativo']
                    break
            
            # Múltiplas camadas para efeito de vibração
            tamanho_base = 500
            tamanho_vibracao1 = tamanho_base + (polo['liquidez'] * 1000)
            tamanho_vibracao2 = tamanho_vibracao1 + (polo['liquidez'] * 600)
            tamanho_vibracao3 = tamanho_vibracao2 + (polo['liquidez'] * 300)
            
            # Cor especial para polos com alto volume
            cor_polo = '#ffff00' if volume_correlacionado and volume_relativo > 1.5 else '#00ff80'
            cor_borda = '#ffff00' if volume_correlacionado and volume_relativo > 1.5 else 'white'
            linewidth_borda = 6 if volume_correlacionado and volume_relativo > 1.5 else 4
            
            # Vibração externa (expansão)
            ax.scatter(polo['preco'], 0, s=tamanho_vibracao3, c=cor_polo, 
                      alpha=0.1, zorder=4)
            
            # Vibração média
            ax.scatter(polo['preco'], 0, s=tamanho_vibracao2, c=cor_polo, 
                      alpha=0.2, zorder=5)
            
            # Vibração interna
            ax.scatter(polo['preco'], 0, s=tamanho_vibracao1, c=cor_polo, 
                      alpha=0.3, zorder=6)
            
            # Núcleo sólido
            ax.scatter(polo['preco'], 0, s=tamanho_base, c=cor_polo, 
                      alpha=0.9, edgecolors=cor_borda, linewidth=linewidth_borda, zorder=7)
            
            # Label com profundidade e volume
            tipo_simbolo = 'ATR' if polo['tipo'] == 'EQUAL_LOW' else 'BID'
            volume_texto = f'V:{volume_relativo:.1f}' if volume_correlacionado else ''
            ax.annotate(f'{tipo_simbolo}\n{polo["liquidez"]:.2f}\nD:{profundidade:.1f}\n{volume_texto}', 
                       xy=(polo['preco'], 0), xytext=(polo['preco'], 2.5),
                       ha='center', va='bottom', color='white', fontsize=11,
                       bbox=dict(boxstyle='round,pad=0.5', facecolor=cor_polo, alpha=0.9))
        
        # Polos repulsivos com vibração em contração e correlação de volume
        for polo in polos_repulsivos:
            # Calcular profundidade baseada na força
            profundidade = min(0.8, polo['liquidez'] * 2)
            
            # Verificar se há correlação com volume alto
            volume_correlacionado = False
            volume_relativo = 1.0
            for zona in zonas_interesse:
                if abs(zona['preco'] - polo['preco']) < (preco_max - preco_min) * 0.01:  # 1% de tolerância
                    volume_correlacionado = True
                    volume_relativo = zona['volume_relativo']
                    break
            
            # Múltiplas camadas para efeito de contração
            tamanho_base = 500
            tamanho_vibracao1 = tamanho_base + (polo['liquidez'] * 1000)
            tamanho_vibracao2 = tamanho_vibracao1 + (polo['liquidez'] * 600)
            tamanho_vibracao3 = tamanho_vibracao2 + (polo['liquidez'] * 300)
            
            # Cor especial para polos com alto volume
            cor_polo = '#ffff00' if volume_correlacionado and volume_relativo > 1.5 else '#ff4040'
            cor_borda = '#ffff00' if volume_correlacionado and volume_relativo > 1.5 else 'white'
            linewidth_borda = 6 if volume_correlacionado and volume_relativo > 1.5 else 4
            
            # Vibração externa (contração)
            ax.scatter(polo['preco'], 0, s=tamanho_vibracao3, c=cor_polo, 
                      alpha=0.1, zorder=4)
            
            # Vibração média
            ax.scatter(polo['preco'], 0, s=tamanho_vibracao2, c=cor_polo, 
                      alpha=0.2, zorder=5)
            
            # Vibração interna
            ax.scatter(polo['preco'], 0, s=tamanho_vibracao1, c=cor_polo, 
                      alpha=0.3, zorder=6)
            
            # Núcleo sólido
            ax.scatter(polo['preco'], 0, s=tamanho_base, c=cor_polo, 
                      alpha=0.9, edgecolors=cor_borda, linewidth=linewidth_borda, zorder=7)
            
            # Label com profundidade e volume
            tipo_simbolo = 'REP' if polo['tipo'] == 'EQUAL_HIGH' else 'ASK'
            volume_texto = f'V:{volume_relativo:.1f}' if volume_correlacionado else ''
            ax.annotate(f'{tipo_simbolo}\n{polo["liquidez"]:.2f}\nD:{profundidade:.1f}\n{volume_texto}', 
                       xy=(polo['preco'], 0), xytext=(polo['preco'], -2.5),
                       ha='center', va='top', color='white', fontsize=11,
                       bbox=dict(boxstyle='round,pad=0.5', facecolor=cor_polo, alpha=0.9))
        
        # === CAMADA 6: PREÇO ATUAL COM AURA ENERGÉTICA ===
        print("INFO: Renderizando preço atual com aura...")
        
        # Aura energética ao redor do preço atual
        campo_atual = campo_magnetico_continuo(preco_atual, todos_polos, k=atr)
        
        if campo_atual > 0.1:  # Campo atrativo
            cor_aura = '#00ff00'
            alpha_aura = 0.3
        elif campo_atual < -0.1:  # Campo repulsivo
            cor_aura = '#ff0000'
            alpha_aura = 0.3
        else:  # Campo neutro
            cor_aura = '#ffff00'
            alpha_aura = 0.2
        
        # Aura externa
        ax.axvspan(preco_atual - atr*0.3, preco_atual + atr*0.3, 
                  alpha=alpha_aura, color=cor_aura, zorder=7)
        
        # Linha vertical pulsante principal
        ax.axvline(preco_atual, color='#ffff00', linewidth=6, alpha=0.9, 
                  label=f'Preço Atual: ${preco_atual:.2f}', zorder=8)
        
        # Efeito de pulsação (linha mais fina)
        ax.axvline(preco_atual, color='#ffff00', linewidth=12, alpha=0.2, zorder=7)
        
        # === CAMADA 7: REGIÕES CRÍTICAS COM ANÉIS DE INVERSÃO ===
        print("INFO: Renderizando regiões críticas com anéis de inversão...")
        
        # Detectar regiões onde campo muda de polaridade
        inversoes = []
        zonas_inversao = []
        
        for i in range(1, len(x_campo)):
            campo_anterior = campo_magnetico_continuo(x_campo[i-1], todos_polos, k=atr)
            campo_atual_regiao = campo_magnetico_continuo(x_campo[i], todos_polos, k=atr)
            
            if (campo_anterior > 0.1 and campo_atual_regiao < -0.1) or \
               (campo_anterior < -0.1 and campo_atual_regiao > 0.1):
                inversoes.append(x_campo[i])
                
                # Calcular equilíbrio entre polos próximos
                polos_proximos_atrativos = [p for p in polos_atrativos if abs(p['preco'] - x_campo[i]) < 2*atr]
                polos_proximos_repulsivos = [p for p in polos_repulsivos if abs(p['preco'] - x_campo[i]) < 2*atr]
                
                forca_atrativa = sum(p['liquidez'] for p in polos_proximos_atrativos)
                forca_repulsiva = sum(p['liquidez'] for p in polos_proximos_repulsivos)
                
                # Determinar cor do anel baseado no equilíbrio
                if forca_atrativa > forca_repulsiva * 1.5:
                    cor_anel = '#0066ff'  # Dominância de compra
                elif forca_repulsiva > forca_atrativa * 1.5:
                    cor_anel = '#ff4040'  # Dominância de venda
                else:
                    cor_anel = '#ff80ff'  # Equilíbrio tenso
                
                zonas_inversao.append({
                    'preco': x_campo[i],
                    'cor': cor_anel,
                    'forca_atrativa': forca_atrativa,
                    'forca_repulsiva': forca_repulsiva
                })
        
        # Renderizar anéis de inversão pulsantes
        for zona in zonas_inversao:
            # Anel externo
            ax.axvspan(zona['preco'] - atr*0.4, zona['preco'] + atr*0.4, 
                      alpha=0.15, color=zona['cor'], zorder=2)
            
            # Anel interno
            ax.axvspan(zona['preco'] - atr*0.2, zona['preco'] + atr*0.2, 
                      alpha=0.3, color=zona['cor'], zorder=3)
            
            # Linha central
            ax.axvline(zona['preco'], color=zona['cor'], linewidth=3, alpha=0.9, zorder=4)
        
        # === CAMADA 8: ZONAS DE INTERESSE HISTÓRICAS ===
        print("INFO: Renderizando zonas de interesse históricas...")
        
        for zona in zonas_interesse:
            # Faixa de interesse
            ax.axvspan(zona['preco'] * 0.999, zona['preco'] * 1.001, 
                      alpha=zona['alpha'], color=zona['cor'], zorder=1)
            
            # Linha de referência
            ax.axvline(zona['preco'], color=zona['cor'], linewidth=2, 
                      alpha=0.7, linestyle='--', zorder=2)
            
            # Label da zona
            tipo_texto = 'TOPO' if zona['tipo'] == 'TOPO' else 'BASE'
            ax.annotate(f'{tipo_texto}\n{zona["preco"]:.2f}\nF:{zona["forca"]:.2f}', 
                       xy=(zona['preco'], 0), xytext=(zona['preco'], 3.5 if zona['tipo'] == 'TOPO' else -3.5),
                       ha='center', va='bottom' if zona['tipo'] == 'TOPO' else 'top', 
                       color='white', fontsize=10,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=zona['cor'], alpha=0.8))
        
        # === CONFIGURAÇÃO VISUAL PROFISSIONAL ===
        ax.set_title(f'CAMPO MAGNÉTICO PROFISSIONAL SNE v2.4 - {symbol} ({timeframe})\n'
                    f'Estado: {estado_campo} | Tom Emocional: {tom_emocional}', 
                    color='white', fontsize=22, pad=35, weight='bold')
        ax.set_xlabel('Preço (USD)', color='white', fontsize=18)
        ax.set_ylabel('Tensão de Liquidez (Ψ)', color='white', fontsize=18)
        ax.grid(True, alpha=0.2, color='#333333')
        ax.tick_params(colors='white', labelsize=14)
        # Legenda principal
        ax.legend(loc='upper left', facecolor='black', edgecolor='white', fontsize=16)
        
        # === LEGENDA EXPLICATIVA DAS ZONAS DE INTERESSE ===
        print("INFO: Adicionando legenda explicativa...")
        
        # Legenda das zonas de interesse (canto superior esquerdo)
        legenda_zonas = f"""ZONAS DE INTERESSE HISTÓRICAS

RED TOPOS: Máximos locais com volume alto
   → Resistência potencial, liquidez de venda
   → Preço pode reverter ou acelerar

BLUE BASES: Mínimos locais com volume alto  
   → Suporte potencial, liquidez de compra
   → Concentração de ordens de compra

YELLOW POLOS: Correlação com volume
   → Polos magnéticos + picos de volume
   → Maior probabilidade de reação

VOLUME: Verde=Compra, Vermelho=Venda
   → Intensidade proporcional à altura
   → Amarelo=Volume extremamente alto"""
        
        ax.text(0.02, 0.98, legenda_zonas, transform=ax.transAxes, 
               verticalalignment='top', horizontalalignment='left', 
               color='white', fontsize=11,
               bbox=dict(boxstyle='round,pad=1.0', facecolor='black', alpha=0.9))
        
        # === HISTOGRAMA DE VOLUME (Subplot Inferior) ===
        print("INFO: Renderizando histograma de volume...")
        
        # Configurar eixo de volume
        ax_volume.set_xlim(preco_min * 0.995, preco_max * 1.005)
        ax_volume.set_facecolor('#0a0a0a')
        
        # Criar histograma de volume com cores baseadas na direção do preço e intensidade
        volumes_norm = np.array(volumes) / max(volumes) if volumes else np.array([0])
        cores_volume = []
        alphas_volume = []
        
        for i, candle in enumerate(data):
            close = float(candle[4])
            open_price = float(candle[1])
            volume = float(candle[5])
            volume_relativo = volume / np.mean(volumes) if np.mean(volumes) > 0 else 1
            
            # Cores baseadas na direção e intensidade
            if close > open_price:
                # Volume de compra - tons de verde
                if volume_relativo > 2.0:
                    cores_volume.append('#00ff00')  # Verde brilhante para volume muito alto
                elif volume_relativo > 1.5:
                    cores_volume.append('#00ff80')  # Verde médio
                else:
                    cores_volume.append('#4ecdc4')  # Verde suave
            elif close < open_price:
                # Volume de venda - tons de vermelho
                if volume_relativo > 2.0:
                    cores_volume.append('#ff0000')  # Vermelho brilhante para volume muito alto
                elif volume_relativo > 1.5:
                    cores_volume.append('#ff4040')  # Vermelho médio
                else:
                    cores_volume.append('#ff6b6b')  # Vermelho suave
            else:
                cores_volume.append('#808080')  # Cinza para neutro
            
            # Alpha baseado na intensidade do volume
            alpha_base = 0.7
            if volume_relativo > 2.0:
                alphas_volume.append(min(1.0, alpha_base + 0.3))
            elif volume_relativo > 1.5:
                alphas_volume.append(min(1.0, alpha_base + 0.2))
            else:
                alphas_volume.append(alpha_base)
        
        # Plotar barras de volume com cores e alphas individuais
        precos_centro = [(float(candle[2]) + float(candle[3])) / 2 for candle in data]
        for i, (preco, volume, cor, alpha) in enumerate(zip(precos_centro, volumes_norm, cores_volume, alphas_volume)):
            ax_volume.bar(preco, volume, width=(preco_max - preco_min) / len(data) * 0.8,
                         color=cor, alpha=alpha, edgecolor='none')
        
        # Destacar volumes extremamente altos com bordas especiais
        volume_medio = np.mean(volumes) if volumes else 0
        for i, (preco, volume) in enumerate(zip(precos_centro, volumes)):
            if volume > volume_medio * 2.5:  # Volume 150% acima da média
                ax_volume.bar(preco, volumes_norm[i], width=(preco_max - preco_min) / len(data) * 0.8,
                             color='#ffff00', alpha=0.9, edgecolor='white', linewidth=2)
        
        # Configurar eixo de volume
        ax_volume.set_ylabel('Volume\nNormalizado', color='white', fontsize=14)
        ax_volume.tick_params(colors='white', labelsize=12)
        ax_volume.grid(True, alpha=0.2, color='#333333')
        
        # Adicionar linha do preço atual no histograma
        ax_volume.axvline(preco_atual, color='#ffff00', linewidth=3, alpha=0.9, zorder=10)
        
        # === LEITURA COGNITIVA INSTANTÂNEA (Canto Superior Direito) ===
        print("INFO: Renderizando leitura cognitiva instantânea...")
        
        # Calcular métricas para leitura cognitiva
        campo_global_percent = min(100, max(0, (polaridade_media + 1) * 50))  # 0-100%
        tensao_liquidez = abs(polaridade_media)
        
        # Determinar fluxo predominante
        if polaridade_media > 0.1:
            fluxo_predominante = "Norte (Comprador)"
            cor_fluxo = '#00ff80'
        elif polaridade_media < -0.1:
            fluxo_predominante = "Sul (Vendedor)"
            cor_fluxo = '#ff4040'
        else:
            fluxo_predominante = "Lateral (Neutro)"
            cor_fluxo = '#8080ff'
        
        # Calcular zona de inversão
        if zonas_inversao:
            precos_inversao = [z['preco'] for z in zonas_inversao]
            zona_inversao_texto = f"{min(precos_inversao):.0f}–{max(precos_inversao):.0f}"
        else:
            zona_inversao_texto = "Nenhuma detectada"
        
        # Calcular pressão institucional
        total_liquidez = sum(p['liquidez'] for p in todos_polos)
        if total_liquidez > 5:
            pressao_institucional = "Alta"
        elif total_liquidez > 2:
            pressao_institucional = "Moderada"
        else:
            pressao_institucional = "Baixa"
        
        # Leitura cognitiva instantânea
        leitura_cognitiva = f"""LEITURA COGNITIVA INSTANTÂNEA

Campo Global: {estado_campo} ({campo_global_percent:.0f}%)
Tensão de Liquidez: {tensao_liquidez:.3f}
Fluxo Predominante: {fluxo_predominante}
Zona de Inversão: {zona_inversao_texto}
Pressão Institucional: {pressao_institucional}

Interpretação:
{interpretacao}

Tom Emocional: {tom_emocional}"""
        
        ax.text(0.98, 0.98, leitura_cognitiva, transform=ax.transAxes, 
               verticalalignment='top', horizontalalignment='right', 
               color='white', fontsize=13,
               bbox=dict(boxstyle='round,pad=1.2', facecolor='black', alpha=0.95))
        
        # Informações técnicas detalhadas (canto inferior esquerdo)
        info_tecnica = f"""ANÁLISE TÉCNICA DETALHADA
Polos Atrativos: {len(polos_atrativos)}
Polos Repulsivos: {len(polos_repulsivos)}
Zonas de Interesse: {len(zonas_interesse)}
Preço Atual: ${preco_atual:.2f}
Campo Local: {campo_atual:.3f}
ATR: {atr:.2f}
Regiões Críticas: {len(inversoes)}
CVD Atual: {cvd_values[-1] if cvd_values else 0:.0f}
Volume Médio: {np.mean(volumes):.0f}"""
        
        ax.text(0.02, 0.02, info_tecnica, transform=ax.transAxes, 
               verticalalignment='bottom', color='white', fontsize=12,
               bbox=dict(boxstyle='round,pad=1.0', facecolor='black', alpha=0.9))
        
        # Salvar imagem
        os.makedirs('reports/campo_magnetico', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_{timeframe}_{timestamp}_campo_profissional_v2.4.png"
        caminho = f"reports/campo_magnetico/{filename}"
        
        fig.savefig(caminho, dpi=200, facecolor='#0a0a0a', 
                   edgecolor='none', bbox_inches='tight')
        plt.close(fig)
        
        print(f"SUCCESS: Campo magnético profissional v2.4 salvo: {caminho}")
        print(f"MAGNETIC: Polos detectados: {len(todos_polos)}")
        print(f"ZONES: Zonas de interesse: {len(zonas_interesse)}")
        print(f"FIELD: Campo atual: {campo_atual:.3f}")
        print(f"STATE: Estado do campo: {estado_campo}")
        print(f"EMOTION: Tom emocional: {tom_emocional}")
        print(f"CRITICAL: Regiões críticas: {len(inversoes)}")
        print(f"PRESSURE: Pressão institucional: {pressao_institucional}")
        print(f"VOLUME: Volume médio: {np.mean(volumes):.0f}")
        
        # Retornar dicionário com informações para Telegram
        return {
            'caminho': caminho,
            'estado_campo': estado_campo,
            'tom_emocional': tom_emocional,
            'fluxo_predominante': fluxo_predominante,
            'pressao_institucional': pressao_institucional,
            'polos_total': len(todos_polos),
            'zonas_interesse': len(zonas_interesse),
            'campo_atual': campo_atual,
            'regioes_criticas': len(inversoes),
            'volume_medio': np.mean(volumes)
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar campo magnético: {e}")
        import traceback
        traceback.print_exc()
        return None


def executar_comando_campo_magnetico():
    """
    Executa o comando de campo magnético no terminal SNE
    """
    try:
        print("\n🧲 CAMPO MAGNÉTICO SNE - SISTEMA DE MAPEAMENTO ENERGÉTICO")
        print("=" * 70)
        print("   Transforma análise técnica em mapa de campo magnético visual")
        print("   Baseado na teoria de campos de liquidez e fluxo energético")
        print("=" * 70)
        
        # 1. Configuração do par
        par = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
        symbol = (par + 'USDT') if par and not par.endswith('USDT') else (par if par else 'BTCUSDT')
        
        # 2. Configuração do timeframe
        print("\n⏰ Timeframes disponíveis:")
        print("   1️⃣ 1h (recomendado)")
        print("   2️⃣ 4h")
        print("   3️⃣ 1d")
        print("   4️⃣ Personalizado")
        
        opcao_tf = input("   Escolha (1-4, Enter para 1): ").strip()
        
        if opcao_tf == "2":
            timeframe = "4h"
        elif opcao_tf == "3":
            timeframe = "1d"
        elif opcao_tf == "4":
            print("   ⏰ Timeframes disponíveis: 1m, 5m, 15m, 30m, 1h, 4h, 8h, 12h, 1d, 1w, 1M")
            tf_custom = input("   Digite o timeframe desejado (ex: 1h): ").strip()
            timeframe = tf_custom if tf_custom else "1h"
        else:
            timeframe = "1h"
        
        # 3. Gerar campo magnético
        print(f"\n🧲 Gerando campo magnético de {symbol} ({timeframe})...")
        resultado = gerar_campo_magnetico_simples(symbol, timeframe)
        
        if not resultado:
            print("❌ Erro ao gerar campo magnético")
            return
        
        # Extrair informações do resultado
        caminho = resultado.get('caminho') if isinstance(resultado, dict) else resultado
        estado_campo = resultado.get('estado_campo', 'NEUTRO') if isinstance(resultado, dict) else 'NEUTRO'
        tom_emocional = resultado.get('tom_emocional', 'Neutro') if isinstance(resultado, dict) else 'Neutro'
        fluxo_predominante = resultado.get('fluxo_predominante', 'Lateral') if isinstance(resultado, dict) else 'Lateral'
        pressao_institucional = resultado.get('pressao_institucional', 'Baixa') if isinstance(resultado, dict) else 'Baixa'
        zonas_interesse = resultado.get('zonas_interesse', 0) if isinstance(resultado, dict) else 0
        volume_medio = resultado.get('volume_medio', 0) if isinstance(resultado, dict) else 0
        
        # 4. Enviar automaticamente para Telegram
        try:
            from xenos_bot import enviar_foto
            
            print("TELEGRAM: Enviando campo magnético automaticamente para Telegram...")
            
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            msg = f"""🧲 <b>CAMPO MAGNÉTICO PROFISSIONAL SNE v2.4</b>
📊 {symbol} ({timeframe})
⏰ {timestamp}

🧲 <b>Topologia Energética Profissional:</b>
• Zonas de interesse históricas (topos/bases)
• Correlação volume-polos (amarelo=alto volume)
• Histograma de volume com cores diferenciadas
• Paleta emocional evolvida (5 estados)
• Polos com vibração dinâmica
• Profundidade de campo tridimensional
• Anéis de inversão inteligentes
• Leitura cognitiva instantânea
• Legenda explicativa integrada

⚡ <b>Análise Cognitiva:</b>
• Estado: {estado_campo}
• Tom Emocional: {tom_emocional}
• Fluxo: {fluxo_predominante}
• Pressão Institucional: {pressao_institucional}
• Zonas de Interesse: {zonas_interesse}

🧠 <b>Baseado em Liquidez Real:</b>
• Order book + CVD + Equal highs/lows
• ATR para normalização
• Detecção de regiões críticas
• Validação por volume
• Correlação volume-polos

🌊 <i>Sistema de Campos Magnéticos SNE v2.4 - Profissional</i>"""
            
            enviar_foto(caminho, msg)
            print("SUCCESS: Campo magnético enviado automaticamente para Telegram!")
                
        except ImportError:
            print("WARNING: Módulo Telegram não disponível")
            print(f"SAVED: Campo magnético salvo: {caminho}")
        except Exception as e:
            print(f"ERROR: Erro ao enviar para Telegram: {e}")
            print(f"SAVED: Campo magnético salvo: {caminho}")
        
        print("\nSUCCESS: Campo magnético gerado com sucesso!")
        
    except KeyboardInterrupt:
        print("\nWARNING: Comando cancelado pelo usuário")
    except Exception as e:
        print(f"\nERROR: Erro no comando campo magnético: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    executar_comando_campo_magnetico()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONTEXTO MACRO VISUAL - Visualização avançada do contexto de mercado
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import mplfinance as mpf
import numpy as np
import pandas as pd
from datetime import datetime
import os
import requests
from motor_renan import analise_completa, coletar_dados


def gerar_visual_contexto_macro(pares=None, output_dir="reports/contexto/"):
    """
    Gera visualização completa do contexto macro com gráficos de preço
    
    Args:
        pares: Lista de pares a analisar
        output_dir: Diretório de saída
    
    Returns:
        Caminho do arquivo gerado
    """
    if pares is None:
        pares = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT']
    
    print(f"\n📊 Gerando visualização de contexto macro...")
    print(f"   Analisando {len(pares)} pares...")
    
    # Coletar dados de todos os pares
    dados_pares = []
    
    for symbol in pares:
        print(f"   🔄 {symbol}...", end=' ', flush=True)
        
        try:
            # Suprimir prints do motor_renan
            import sys
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            analise = analise_completa(symbol, '1h')
            
            sys.stdout = old_stdout
            
            if analise and 'erro' not in analise:
                # Extrair confluência (pode ser dict ou número)
                confluencia_val = analise.get('confluencia', 0)
                if isinstance(confluencia_val, dict):
                    confluencia_val = confluencia_val.get('score', 0)
                
                dados_pares.append({
                    'symbol': symbol,
                    'regime': analise.get('regime', 'INDEFINIDO'),
                    'forca_regime': float(analise.get('forca_regime', 0)),
                    'volatilidade': float(analise.get('volatilidade', 0)),
                    'liquidez': float(analise.get('score_liquidez', 0)),
                    'confluencia': float(confluencia_val),
                    'recomendacao': analise.get('recomendacao', 'AGUARDAR')
                })
                print("✅")
            else:
                print("❌")
        except Exception as e:
            print(f"❌ ({e})")
    
    if not dados_pares:
        print("❌ Nenhum dado coletado")
        return None
    
    # Obter dados de sentiment
    sentiment_data = obter_sentiment_global()
    
    # Criar figura com múltiplos painéis - Layout otimizado para 5 pares
    fig = plt.figure(figsize=(26, 18), facecolor='#0a0a0a')
    gs = fig.add_gridspec(4, 4, hspace=0.45, wspace=0.35, 
                          height_ratios=[1.6, 1.6, 1.0, 1.0],
                          left=0.05, right=0.95, top=0.93, bottom=0.05)
    
    # ============================================================
    # FUNÇÃO AUXILIAR: Plotar Gráfico de Preço com S/R
    # ============================================================
    def plotar_grafico_par(ax, par_data, posicao):
        """Plota gráfico de candlestick com S/R para um par"""
        symbol = par_data['symbol']
        
        # Coletar dados de preço
        df_preco = coletar_dados(symbol, '4h')
        
        if df_preco is None or df_preco.empty:
            ax.text(0.5, 0.5, 'Sem dados', ha='center', va='center', 
                   color='white', transform=ax.transAxes)
            return
        
        # Pegar últimas 60 velas
        df_preco = df_preco.tail(60).copy()
        
        # Calcular EMAs
        df_preco['EMA8'] = df_preco['close'].ewm(span=8, adjust=False).mean()
        df_preco['EMA21'] = df_preco['close'].ewm(span=21, adjust=False).mean()
        
        # Calcular S/R
        from calcular_suportes_resistencias import calcular_suportes_resistencias
        sr_data = calcular_suportes_resistencias(df_preco)
        
        # Plotar candlesticks
        for i in range(len(df_preco)):
            row = df_preco.iloc[i]
            cor = '#00ff00' if row['close'] > row['open'] else '#ff0000'
            
            # Corpo
            height = abs(row['close'] - row['open'])
            bottom = min(row['close'], row['open'])
            ax.add_patch(plt.Rectangle(
                (i, bottom), 0.8, height,
                facecolor=cor, edgecolor='white', linewidth=0.5, alpha=0.8
            ))
            
            # Sombras
            ax.plot([i+0.4, i+0.4], [row['low'], row['high']], 
                   color='white', linewidth=0.5, alpha=0.5)
        
        # Plotar EMAs
        ax.plot(range(len(df_preco)), df_preco['EMA8'], 
               color='#00ffff', linewidth=1.5, label='EMA8', alpha=0.8)
        ax.plot(range(len(df_preco)), df_preco['EMA21'], 
               color='#ff00ff', linewidth=1.5, label='EMA21', alpha=0.8)
        
        # Plotar S/R
        suportes = sr_data.get('suportes', [])
        resistencias = sr_data.get('resistencias', [])
        
        for s in suportes[:2]:  # Top 2 suportes
            ax.axhline(y=s, color='#00ff00', linestyle=':', linewidth=1.5, alpha=0.6)
        
        for r in resistencias[:2]:  # Top 2 resistências
            ax.axhline(y=r, color='#ff0000', linestyle=':', linewidth=1.5, alpha=0.6)
        
        # Configurar eixos
        ax.set_facecolor('#1a1a1a')
        ax.set_xlim(-1, len(df_preco))
        ax.set_ylim(df_preco['low'].min() * 0.998, df_preco['high'].max() * 1.002)
        
        # Título
        preco_atual = df_preco['close'].iloc[-1]
        variacao = ((preco_atual - df_preco['close'].iloc[0]) / df_preco['close'].iloc[0]) * 100
        
        ax.set_title(
            f"#{posicao} {symbol.replace('USDT', '')} ${preco_atual:,.2f} ({variacao:+.2f}%)",
            color='white', fontsize=11, weight='bold', pad=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a0a', 
                     edgecolor='#00ffff', alpha=0.7, linewidth=1)
        )
        
        # Info box
        info = f"Score: {par_data['confluencia']:.1f}/10\n{par_data['regime']}"
        ax.text(
            0.02, 0.98, info,
            transform=ax.transAxes,
            fontsize=8, color='white',
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a0a', 
                     edgecolor='white', alpha=0.8, linewidth=1)
        )
        
        ax.tick_params(axis='both', colors='white', labelsize=7)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(alpha=0.2, color='white')
        ax.legend(loc='upper left', fontsize=6, framealpha=0.8, 
                facecolor='#1a1a1a', edgecolor='white')
    
    # ============================================================
    # PAINÉIS 1-3: GRÁFICOS DOS TOP 3 PARES (Linha 1)
    # ============================================================
    top_pares = sorted(dados_pares, key=lambda x: x['confluencia'], reverse=True)[:5]
    
    for idx in range(3):
        if idx < len(top_pares):
            ax = fig.add_subplot(gs[0, idx])
            plotar_grafico_par(ax, top_pares[idx], idx + 1)
    
    # ============================================================
    # PAINEL 4: FEAR & GREED GAUGE (Linha 1, coluna 4)
    # ============================================================
    ax_fg = fig.add_subplot(gs[0, 3])
    ax_fg.set_facecolor('#1a1a1a')
    ax_fg.axis('off')
    
    fear_greed = sentiment_data.get('fear_greed', 50)
    
    # Usar a função criar_gauge_sentiment (termômetro gráfico)
    criar_gauge_sentiment(ax_fg, fear_greed)
    
    # Info adicional (Funding e OI) abaixo do gauge
    funding = sentiment_data.get('funding_status', 'N/A')
    oi = sentiment_data.get('oi_status', 'N/A')
    info_fg = f"Funding: {funding}\nOI: {oi}"
    ax_fg.text(
        0, -0.65,
        info_fg,
        ha='center',
        va='top',
        fontsize=7,
        color='white',
        family='monospace',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a0a', 
                 edgecolor='white', linewidth=1, alpha=0.8)
    )
    
    # ============================================================
    # PAINÉIS 5-6: GRÁFICOS DOS PARES 4 e 5 (Linha 2)
    # ============================================================
    for idx in range(3, 5):
        if idx < len(top_pares):
            ax = fig.add_subplot(gs[1, idx - 3])
            plotar_grafico_par(ax, top_pares[idx], idx + 1)
    
    # ============================================================
    # PAINEL 7: VOLUME PROFILE (Top Par)
    # ============================================================
    ax_vp = fig.add_subplot(gs[1, 2])
    ax_vp.set_facecolor('#1a1a1a')
    
    if len(top_pares) > 0:
        top_par = top_pares[0]
        df_vp = coletar_dados(top_par['symbol'], '4h')
        
        if df_vp is not None and not df_vp.empty:
            df_vp = df_vp.tail(100).copy()
            
            # Calcular distribuição de volume por faixa de preço
            min_price = df_vp['low'].min()
            max_price = df_vp['high'].max()
            price_bins = np.linspace(min_price, max_price, 30)
            volume_profile = np.zeros(len(price_bins) - 1)
            
            for _, row in df_vp.iterrows():
                for i in range(len(price_bins) - 1):
                    if price_bins[i] <= row['close'] < price_bins[i+1]:
                        volume_profile[i] += row['volume']
            
            # Plotar volume profile horizontal
            price_centers = (price_bins[:-1] + price_bins[1:]) / 2
            ax_vp.barh(price_centers, volume_profile, height=(price_bins[1]-price_bins[0])*0.9,
                      color='#00ffff', alpha=0.6, edgecolor='white', linewidth=0.5)
            
            # Marcar POC (Point of Control)
            poc_idx = np.argmax(volume_profile)
            poc_price = price_centers[poc_idx]
            ax_vp.axhline(y=poc_price, color='#ff00ff', linestyle='--', linewidth=2, 
                         label=f'POC: ${poc_price:,.2f}')
            
            # Preço atual
            preco_atual = df_vp['close'].iloc[-1]
            ax_vp.axhline(y=preco_atual, color='white', linestyle='-', linewidth=2, 
                         label=f'Atual: ${preco_atual:,.2f}')
            
            ax_vp.set_xlabel('Volume', color='white', fontsize=8)
            ax_vp.set_ylabel('Preço', color='white', fontsize=8)
            ax_vp.set_title(f'VOLUME PROFILE\n{top_par["symbol"].replace("USDT", "")}', 
                          color='white', fontsize=9, weight='bold', pad=5)
            ax_vp.tick_params(axis='both', colors='white', labelsize=7)
            ax_vp.spines['bottom'].set_color('white')
            ax_vp.spines['left'].set_color('white')
            ax_vp.spines['top'].set_visible(False)
            ax_vp.spines['right'].set_visible(False)
            ax_vp.grid(alpha=0.2, color='white')
            ax_vp.legend(loc='upper right', fontsize=6, framealpha=0.8, 
                        facecolor='#1a1a1a', edgecolor='white')
    
    # ============================================================
    # PAINEL 8: DOM PRESSURE (Top Par)
    # ============================================================
    ax_dom = fig.add_subplot(gs[1, 3])
    ax_dom.set_facecolor('#1a1a1a')
    
    if len(top_pares) > 0:
        top_par = top_pares[0]
        
        from fluxo_ativo import FluxoAtivo
        fluxo = FluxoAtivo()
        dom_data = fluxo.calcular_pressao_liquidez(top_par['symbol'])
        
        # Barras de pressão
        labels = ['BID\nPressure', 'ASK\nPressure']
        values = [dom_data['bid_density'], dom_data['ask_density']]
        colors = ['#00ff00', '#ff0000']
        
        bars = ax_dom.bar(labels, values, color=colors, alpha=0.7, edgecolor='white', linewidth=2)
        
        # Linha de equilíbrio
        avg = np.mean(values)
        ax_dom.axhline(y=avg, color='white', linestyle='--', alpha=0.5, linewidth=1)
        
        # Ratio e pressão
        ratio = dom_data['ratio']
        pressao = dom_data['pressao']
        
        cor_pressao = {
            'COMPRA': '#00ff00',
            'VENDA': '#ff0000',
            'NEUTRO': '#ffff00'
        }.get(pressao, '#888888')
        
        ax_dom.text(
            0.5, 0.95,
            f"Ratio: {ratio:.2f}\nPressao: {pressao}",
            transform=ax_dom.transAxes,
            ha='center', va='top',
            fontsize=8, color=cor_pressao, weight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a0a', 
                     edgecolor=cor_pressao, linewidth=1.5, alpha=0.8)
        )
        
        ax_dom.set_ylabel('Densidade', color='white', fontsize=8)
        ax_dom.set_title(f'DOM PRESSURE\n{top_par["symbol"].replace("USDT", "")}', 
                        color='white', fontsize=9, weight='bold', pad=5)
        ax_dom.tick_params(axis='both', colors='white', labelsize=7)
        ax_dom.spines['bottom'].set_color('white')
        ax_dom.spines['left'].set_color('white')
        ax_dom.spines['top'].set_visible(False)
        ax_dom.spines['right'].set_visible(False)
        ax_dom.grid(axis='y', alpha=0.2, color='white')
    
    # ============================================================
    # PAINEL 9: ZONAS MAGNÉTICAS (Linha 3, painéis 1-2)
    # ============================================================
    ax_zm = fig.add_subplot(gs[2, :2])
    ax_zm.set_facecolor('#1a1a1a')
    ax_zm.axis('off')
    
    # Obter zonas magnéticas do catálogo
    import pandas as pd
    from catalogo_magnetico import CAMINHO_CATALOGO
    
    try:
        catalogo = pd.read_csv(CAMINHO_CATALOGO)
        if not catalogo.empty:
            # Pegar top 5 zonas por força
            catalogo = catalogo.sort_values('forca_total', ascending=False).head(5)
            
            zonas_info = "ZONAS MAGNETICAS (CATALOGO)\n"
            zonas_info += "=" * 50 + "\n\n"
            
            for idx, row in catalogo.iterrows():
                zona = row['zona']
                forca = row['forca_total']
                
                # Determinar par mais próximo
                par_proximo = None
                dist_min = float('inf')
                
                for par in top_pares:
                    df_check = coletar_dados(par['symbol'], '4h')
                    if df_check is not None and not df_check.empty:
                        preco = df_check['close'].iloc[-1]
                        dist = abs(preco - zona)
                        if dist < dist_min:
                            dist_min = dist
                            par_proximo = (par['symbol'].replace('USDT', ''), preco)
                
                if par_proximo:
                    dist_pct = (dist_min / par_proximo[1]) * 100
                    
                    zonas_info += f"${zona:>10,.2f} | F:{forca:>5.1f} | "
                    zonas_info += f"{par_proximo[0]:>5s} {dist_pct:>5.2f}%\n"
            
            ax_zm.text(
                0.5, 0.5,
                zonas_info,
                transform=ax_zm.transAxes,
                fontsize=10,
                color='#00ffff',
                ha='center',
                va='center',
                family='monospace',
                weight='bold',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='#0a0a0a', 
                         edgecolor='#00ffff', linewidth=2, alpha=0.9)
            )
            
            # Guardar zonas para usar na tabela
            zonas = catalogo['zona'].tolist()
        else:
            zonas = []
            ax_zm.text(0.5, 0.5, "Catalogo vazio", transform=ax_zm.transAxes,
                      fontsize=10, color='white', ha='center', va='center')
    except FileNotFoundError:
        zonas = []
        ax_zm.text(0.5, 0.5, "Catalogo nao encontrado", transform=ax_zm.transAxes,
                  fontsize=10, color='white', ha='center', va='center')
    
    # ============================================================
    # PAINEL 10: INFO ADICIONAL (Linha 3, painéis 3-4)
    # ============================================================
    ax_info = fig.add_subplot(gs[2, 2:])
    ax_info.set_facecolor('#1a1a1a')
    ax_info.axis('off')
    
    info_text = "ANALISE MACRO\n"
    info_text += "=" * 35 + "\n\n"
    
    # Calcular estatísticas
    scores = [p['confluencia'] for p in top_pares]
    avg_score = np.mean(scores) if scores else 0
    
    regimes = [p['regime'] for p in top_pares]
    regime_dominante = max(set(regimes), key=regimes.count) if regimes else 'N/A'
    
    info_text += f"Score Medio: {avg_score:.1f}/10\n"
    info_text += f"Regime Dom.: {regime_dominante}\n"
    info_text += f"F&G Index: {fear_greed}/100\n\n"
    
    info_text += "TOP 3 SETUPS:\n"
    for i, par in enumerate(top_pares[:3], 1):
        acao = {
            'COMPRAR': '[BUY]',
            'VENDER': '[SELL]',
            'AGUARDAR': '[WAIT]'
        }.get(par.get('recomendacao', 'AGUARDAR'), '[---]')
        
        info_text += f"{i}. {par['symbol'].replace('USDT', '')}: {acao}\n"
        info_text += f"   Score {par['confluencia']:.1f}/10\n"
    
    ax_info.text(
        0.5, 0.5,
        info_text,
        transform=ax_info.transAxes,
        fontsize=9,
        color='white',
        ha='center',
        va='center',
        family='monospace',
        weight='bold',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#0a0a0a', 
                 edgecolor='white', linewidth=2, alpha=0.9)
    )
    
    # ============================================================
    # PAINEL 11: TABELA DE SETUPS OPERACIONAIS (Linha 4, todas colunas)
    # ============================================================
    ax_table = fig.add_subplot(gs[3, :])
    ax_table.set_facecolor('#1a1a1a')
    ax_table.axis('off')
    
    # Criar tabela de setups LEGÍVEL
    setup_lines = []
    setup_lines.append("SETUPS OPERACIONAIS - TOP 5 PARES")
    setup_lines.append("=" * 85)
    setup_lines.append("")
    
    for i, par in enumerate(top_pares[:5], 1):
        symbol = par['symbol'].replace('USDT', '')
        
        # Obter dados para cálculo de entry/sl/tp
        df_setup = coletar_dados(par['symbol'], '4h')
        if df_setup is not None and not df_setup.empty:
            preco_atual = df_setup['close'].iloc[-1]
            
            # Calcular níveis básicos baseado em ATR
            from calcular_suportes_resistencias import calcular_range_atr
            range_data = calcular_range_atr(df_setup)
            atr = range_data.get('atr', preco_atual * 0.01)
            
            # Entry, SL, TP baseados em direção
            vies = par.get('sintese', {}).get('vies', 'N/A') if 'sintese' in par else 'N/A'
            
            if 'ALTA' in vies or 'BULL' in par.get('regime', ''):
                entry = preco_atual
                sl = preco_atual - (atr * 1.5)
                tp1 = preco_atual + (atr * 2)
                direcao = "LONG"
            elif 'BAIXA' in vies or 'BEAR' in par.get('regime', ''):
                entry = preco_atual
                sl = preco_atual + (atr * 1.5)
                tp1 = preco_atual - (atr * 2)
                direcao = "SHORT"
            else:
                entry = preco_atual
                sl = preco_atual - (atr * 1.5)
                tp1 = preco_atual + (atr * 1.5)
                direcao = "WAIT"
            
            rr = abs((tp1 - entry) / (entry - sl)) if (entry - sl) != 0 else 0
            
            # Verificar proximidade de zona magnética
            zona_info = ""
            if zonas and len(zonas) > 0:
                for zona in zonas[:3]:
                    dist_pct = abs((preco_atual - zona) / preco_atual) * 100
                    if dist_pct < 2:
                        zona_info = f" | Zona: ${zona:,.0f} ({dist_pct:.1f}%)"
                        break
            
            # Linha principal do setup
            setup_lines.append(f"#{i} {symbol:>6s} | Score: {par['confluencia']:.1f}/10 | {direcao:>5s}")
            setup_lines.append(f"   Preco:  ${preco_atual:>10,.2f}{zona_info}")
            setup_lines.append(f"   Entry:  ${entry:>10,.2f}")
            setup_lines.append(f"   Stop:   ${sl:>10,.2f}")
            setup_lines.append(f"   TP1:    ${tp1:>10,.2f}  (R:R {rr:.1f})")
            setup_lines.append("")
        else:
            setup_lines.append(f"#{i} {symbol:>6s} | Sem dados disponiveis")
            setup_lines.append("")
    
    setup_lines.append("=" * 85)
    setup_lines.append(f"F&G: {fear_greed}/100 ({'Fear' if fear_greed < 45 else 'Neutral' if fear_greed < 55 else 'Greed'}) | TF: 4h")
    
    setup_text = "\n".join(setup_lines)
    
    ax_table.text(
        0.5, 0.5,
        setup_text,
        transform=ax_table.transAxes,
        fontsize=9,
        color='white',
        ha='center',
        va='center',
        family='monospace',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#0a0a0a', 
                 edgecolor='white', linewidth=2, alpha=0.95)
    )
    
    # ============================================================
    # TÍTULO PRINCIPAL E HIERARQUIA VISUAL
    # ============================================================
    timestamp_grafico = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    # Título principal com destaque
    fig.text(
        0.5, 0.97,
        'SNE RADAR - CONTEXTO MACRO DE MERCADO',
        ha='center',
        fontsize=20,
        color='white',
        weight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a1a', 
                 edgecolor='#00ffff', linewidth=2, alpha=0.9)
    )
    
    # Subtítulo
    fig.text(
        0.5, 0.945,
        f'{len(pares)} pares | {timestamp_grafico} | Timeframe: 4h',
        ha='center',
        fontsize=11,
        color='#00ffff',
        weight='bold'
    )
    
    # Separadores visuais entre seções
    # Linha após gráficos superiores
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.62, 0.62], 
                              color='#00ffff', linewidth=1, alpha=0.3))
    
    # Linha antes da tabela final
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.26, 0.26], 
                              color='#00ffff', linewidth=1, alpha=0.3))
    
    # Labels de seção
    fig.text(0.03, 0.88, 'TOP 3 SETUPS', rotation=90, va='center',
            fontsize=10, color='#00ffff', weight='bold', alpha=0.7)
    
    fig.text(0.03, 0.48, 'PARES 4-5', rotation=90, va='center',
            fontsize=10, color='#00ffff', weight='bold', alpha=0.7)
    
    fig.text(0.03, 0.38, 'ANALISE AVANCADA', rotation=90, va='center',
            fontsize=10, color='#00ffff', weight='bold', alpha=0.7)
    
    fig.text(0.03, 0.13, 'SETUPS OPERACIONAIS', rotation=90, va='center',
            fontsize=10, color='#00ffff', weight='bold', alpha=0.7)
    
    # Marca d'água
    fig.text(
        0.98, 0.02,
        'SNE RADAR',
        ha='right',
        va='bottom',
        fontsize=12,
        color='white',
        alpha=0.3,
        style='italic'
    )
    
    # Salvar
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}contexto_macro_{timestamp}.png"
    
    plt.savefig(
        filename,
        dpi=150,
        bbox_inches='tight',
        facecolor='#0a0a0a',
        edgecolor='white',
        pad_inches=0.2
    )
    plt.close()
    
    print(f"\n✅ Visualização salva: {filename}")
    
    return filename


def criar_gauge_sentiment(ax, valor):
    """Cria um gauge visual para o Fear & Greed Index"""
    
    # Determinar cor e label
    if valor < 25:
        cor = '#8B0000'
        label = 'EXTREME FEAR'
    elif valor < 45:
        cor = '#ff0000'
        label = 'FEAR'
    elif valor < 55:
        cor = '#ffff00'
        label = 'NEUTRAL'
    elif valor < 75:
        cor = '#00ff00'
        label = 'GREED'
    else:
        cor = '#006400'
        label = 'EXTREME GREED'
    
    # Criar arco do gauge
    theta = np.linspace(0, np.pi, 100)
    x = np.cos(theta)
    y = np.sin(theta)
    
    # Desenhar arco de fundo
    ax.plot(x, y, color='#333333', linewidth=10, zorder=1)
    
    # Desenhar arco colorido até o valor
    theta_valor = np.linspace(0, np.pi * (valor / 100), 100)
    x_valor = np.cos(theta_valor)
    y_valor = np.sin(theta_valor)
    ax.plot(x_valor, y_valor, color=cor, linewidth=10, zorder=2)
    
    # Adicionar ponteiro
    angulo = np.pi * (1 - valor / 100)
    ax.plot([0, np.cos(angulo) * 0.7], [0, np.sin(angulo) * 0.7], 
            color='white', linewidth=3, zorder=3)
    
    # Adicionar texto
    ax.text(0, -0.3, f'{valor}', ha='center', va='center', 
            fontsize=36, color='white', weight='bold')
    ax.text(0, -0.5, label, ha='center', va='center', 
            fontsize=12, color=cor, weight='bold')
    ax.text(0, 1.2, '😨 FEAR & GREED INDEX', ha='center', va='center',
            fontsize=12, color='white', weight='bold')
    
    # Configurar eixos
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.7, 1.4)
    ax.set_aspect('equal')


def obter_sentiment_global():
    """Obtém dados de sentiment global"""
    try:
        # Fear & Greed Index (API alternativa)
        response = requests.get('https://api.alternative.me/fng/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            fear_greed = int(data['data'][0]['value'])
            return {'fear_greed': fear_greed}
    except:
        pass
    
    return {'fear_greed': 50}  # Neutro como fallback


if __name__ == "__main__":
    # Teste
    gerar_visual_contexto_macro()


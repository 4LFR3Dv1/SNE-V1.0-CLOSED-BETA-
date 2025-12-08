#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO ANÁLISE - Sistema automático 24/7 com relatórios visuais
"""

import time
import asyncio
import sys
import io
import os
import requests
from datetime import datetime
from motor_renan import analise_completa
from xenos_bot import enviar_oraculo, enviar_foto
from grafico_candlestick import gerar_grafico_com_niveis
from calcular_suportes_resistencias import calcular_suportes_resistencias, calcular_range_atr
from dom_consolidado import gerar_heatmap_dom_consolidado

# Pares principais para monitoramento (ordem fixa: BTC, ETH, SOL)
PARES_AUTO = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

# Armazenar níveis S/R para alertas
ultimos_niveis = {}

# Controle de último preço para evitar spam do mesmo alerta
ultimos_precos_alertados = {}


def verificar_alertas_sr(symbol, preco_atual, sr_data):
    """
    Verifica se o preço está próximo de suportes ou resistências
    Otimizado para alertas em tempo real úteis para operação
    """
    alertas = []
    
    if not sr_data:
        return alertas
    
    suportes = sr_data.get('suportes', [])
    resistencias = sr_data.get('resistencias', [])
    
    # Margem de proximidade ajustada (0.25%)
    margem = preco_atual * 0.0025
    
    # Verificar suportes
    for i, suporte in enumerate(suportes[:3], 1):
        dist = abs(preco_atual - suporte)
        if dist <= margem:
            dist_pct = (dist / preco_atual) * 100
            
            # Direção do movimento
            direcao = "TESTANDO" if preco_atual > suporte else "ROMPENDO"
            
            # Força do nível baseado na posição
            forca = "FORTE" if i == 1 else "MÉDIO" if i == 2 else "FRACO"
            
            alertas.append({
                'tipo': '🔵 SUPORTE',
                'nivel': suporte,
                'distancia': dist_pct,
                'preco_atual': preco_atual,
                'direcao': direcao,
                'forca': forca,
                'acao': "Aguardar reação" if direcao == "TESTANDO" else "Confirmação de rompimento"
            })
            break  # Apenas o mais próximo
    
    # Verificar resistências
    for i, resistencia in enumerate(resistencias[:3], 1):
        dist = abs(preco_atual - resistencia)
        if dist <= margem:
            dist_pct = (dist / preco_atual) * 100
            
            # Direção do movimento
            direcao = "TESTANDO" if preco_atual < resistencia else "ROMPENDO"
            
            # Força do nível baseado na posição
            forca = "FORTE" if i == 1 else "MÉDIO" if i == 2 else "FRACO"
            
            alertas.append({
                'tipo': '🔴 RESISTÊNCIA',
                'nivel': resistencia,
                'distancia': dist_pct,
                'preco_atual': preco_atual,
                'direcao': direcao,
                'forca': forca,
                'acao': "Aguardar rejeição" if direcao == "TESTANDO" else "Confirmação de rompimento"
            })
            break  # Apenas o mais próximo
    
    return alertas


async def monitorar_alertas_tempo_real(pares, intervalo_check=30):
    """
    Monitora alertas em tempo real - Otimizado para operação
    Sem cooldown, apenas anti-spam inteligente
    """
    global ultimos_niveis, ultimos_precos_alertados
    
    while True:
        try:
            for symbol in pares:
                # Obter preço atual
                url = "https://api.binance.com/api/v3/ticker/price"
                response = requests.get(url, params={'symbol': symbol}, timeout=5)
                
                if response.status_code == 200:
                    preco_atual = float(response.json()['price'])
                    
                    # Verificar se temos níveis salvos
                    if symbol in ultimos_niveis:
                        sr_data = ultimos_niveis[symbol]
                        alertas = verificar_alertas_sr(symbol, preco_atual, sr_data)
                        
                        for alerta in alertas:
                            # Criar chave única baseada no nível
                            chave_nivel = f"{symbol}_{alerta['nivel']:.2f}"
                            
                            # Verificar se o preço mudou significativamente desde último alerta (0.1%)
                            if chave_nivel in ultimos_precos_alertados:
                                variacao = abs(preco_atual - ultimos_precos_alertados[chave_nivel]) / ultimos_precos_alertados[chave_nivel] * 100
                                # Só envia novo alerta se preço variou > 0.1%
                                if variacao < 0.1:
                                    continue
                            
                            par_nome = symbol.replace('USDT', '')
                            
                            # Emoji baseado na direção
                            if alerta['direcao'] == "TESTANDO":
                                emoji_dir = "⚡" if "SUPORTE" in alerta['tipo'] else "⚡"
                                acao_desc = "POSSÍVEL REAÇÃO"
                            else:
                                emoji_dir = "🔥" if "SUPORTE" in alerta['tipo'] else "🔥"
                                acao_desc = "POSSÍVEL ROMPIMENTO"
                            
                            msg = f"""
{emoji_dir} <b>{acao_desc}</b>

📊 <b>{par_nome}</b> | ${alerta['preco_atual']:,.2f}

{alerta['tipo']} <b>{alerta['forca']}</b>
   Nível: ${alerta['nivel']:,.2f}
   Status: {alerta['direcao']}
   Dist: {alerta['distancia']:.2f}%

💡 <b>Ação:</b> {alerta['acao']}
"""
                            enviar_oraculo(msg)
                            print(f"\n{emoji_dir} ALERTA: {par_nome} {alerta['direcao']} {alerta['tipo']} ${alerta['nivel']:,.2f}")
                            
                            # Registrar preço do alerta
                            ultimos_precos_alertados[chave_nivel] = preco_atual
            
            await asyncio.sleep(intervalo_check)
            
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n⚠️ Monitoramento de alertas encerrado")
            break
        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")
            await asyncio.sleep(intervalo_check)


async def auto_analise_continua(pares=None, intervalo=3600, enviar_telegram=True):
    """Análise automática contínua com relatórios visuais e gráficos"""
    
    if pares is None:
        pares = PARES_AUTO
    
    print("\n" + "="*80)
    print("🤖 ANÁLISE AUTOMÁTICA 24/7 - SNE RADAR")
    print("="*80)
    print(f"\n📊 Pares Fixos: BTC, ETH, SOL")
    print(f"⏰ Análise Completa: A cada {intervalo//60} min")
    print(f"🚨 Alertas S/R: Tempo real (30s) - SEM cooldown")
    print(f"📱 Telegram: {'Ativado' if enviar_telegram else 'Desativado'}")
    print(f"📈 Relatórios: Visual + Heatmap DOM + Gráficos")
    print("\n⚡ Pressione Ctrl+C para parar\n")
    
    contador = 0
    
    try:
        while True:
            contador += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n{'='*80}")
            print(f"🔄 CICLO #{contador} - {timestamp}")
            print(f"{'='*80}\n")
            
            # Análise individual com supressão de prints verbose
            analises = []
            
            for par in pares:
                print(f"📊 {par}...", end=' ', flush=True)
                
                # Suprimir prints verbose
                old_stdout = sys.stdout
                sys.stdout = io.StringIO()
                
                analise = analise_completa(par, "1h")
                
                sys.stdout = old_stdout
                
                if 'erro' not in analise:
                    analises.append(analise)
                    score = analise.get('confluencia', {}).get('score', 0)
                    if isinstance(score, dict):
                        score = score.get('score', 0)
                    score = float(score)
                    
                    # Emoji baseado no score
                    if score >= 7.5:
                        emoji = "🟢"
                    elif score >= 6.5:
                        emoji = "🟡"
                    else:
                        emoji = "🔴"
                    
                    print(f"{emoji} {score:.1f}/10")
            
            # Gerar Heatmap DOM consolidado
            print(f"\n🌊 Gerando Heatmap DOM...", end=' ', flush=True)
            heatmap_dom = gerar_heatmap_dom_consolidado(pares, output_dir="reports/auto/")
            print("✅")
            
            # Gerar gráficos individuais para TODOS os 3 pares (BTC, ETH, SOL)
            analises_ordenadas = sorted(analises, key=lambda x: float(x.get('confluencia', {}).get('score', 0) if not isinstance(x.get('confluencia', {}).get('score', 0), dict) else x.get('confluencia', {}).get('score', {}).get('score', 0)), reverse=True)
            
            graficos_gerados = []
            
            for i, analise in enumerate(analises_ordenadas):  # TODOS os 3 pares
                symbol = analise['symbol']
                sintese = analise['sintese']
                
                print(f"📈 Gráfico {symbol}...", end=' ', flush=True)
                
                # Coletar dados para gráfico
                from motor_renan import coletar_dados
                df = coletar_dados(symbol, '1h')
                
                if df is not None and not df.empty:
                    # Calcular S/R e Range
                    sr_data = calcular_suportes_resistencias(df)
                    range_data = calcular_range_atr(df)
                    anotacoes = None  # Anotações desabilitadas
                    
                    # Salvar níveis S/R para alertas
                    global ultimos_niveis
                    ultimos_niveis[symbol] = sr_data
                    
                    # Níveis operacionais
                    niveis = {
                        'entry': sintese.get('entry_price'),
                        'stop': sintese.get('stop_loss'),
                        'tp1': sintese.get('tp1'),
                        'tp2': sintese.get('tp2'),
                        'tp3': sintese.get('tp3')
                    }
                    
                    # Gerar gráfico
                    grafico_path = gerar_grafico_com_niveis(
                        symbol=symbol,
                        interval='1h',
                        output_dir='reports/auto/',
                        niveis_dict=niveis,
                        sr_data=sr_data,
                        range_data=range_data,
                        anotacoes=anotacoes
                    )
                    
                    if grafico_path:
                        graficos_gerados.append((symbol, grafico_path, analise))
                        print("✅")
                    else:
                        print("⚠️")
                else:
                    print("⚠️")
            
            # Montar relatório consolidado
            print(f"\n📝 Montando relatório...", end=' ', flush=True)
            
            relatorio = f"""
🤖 <b>ANÁLISE AUTOMÁTICA #{contador}</b>
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            # Relatório par por par (sempre BTC, ETH, SOL)
            for analise in analises_ordenadas:
                symbol = analise['symbol']
                score = analise.get('confluencia', {}).get('score', 0)
                if isinstance(score, dict):
                    score = score.get('score', 0)
                score = float(score)
                
                sintese = analise['sintese']
                contexto = analise.get('contexto', {})
                estrutura = analise.get('estrutura', {})
                indicadores = analise.get('indicadores', {})
                
                preco = indicadores.get('preco', 0)
                regime = contexto.get('regime', 'N/A')
                volatilidade = contexto.get('volatilidade', 0)
                tendencia = estrutura.get('tendencia', 'N/A')
                
                # Emoji por score
                if score >= 7.5:
                    emoji = "🟢"
                    status = "SETUP FORTE"
                elif score >= 6.5:
                    emoji = "🟡"
                    status = "SETUP MODERADO"
                else:
                    emoji = "🔴"
                    status = "AGUARDAR"
                
                par_nome = symbol.replace('USDT', '')
                
                relatorio += f"""
{emoji} <b>{par_nome}</b> | ${preco:,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Status:</b> {status} ({score:.1f}/10)
📈 <b>Tendência:</b> {tendencia}
🌊 <b>Regime:</b> {regime}
⚡ <b>Volatilidade:</b> {volatilidade:.2f}%

"""
                
                # SEMPRE mostrar níveis (motor agora sempre gera)
                acao = sintese.get('acao', 'N/A')
                entry_price = sintese.get('entry_price', preco)
                stop_loss = sintese.get('stop_loss', preco)
                tp2 = sintese.get('tp2', preco)
                rr = sintese.get('rr_ratio', 'N/A')
                
                relatorio += f"""📍 <b>NÍVEIS OPERACIONAIS:</b>
   {acao}
   Entry:  ${entry_price:,.2f}
   Stop:   ${stop_loss:,.2f}
   TP:     ${tp2:,.2f}
   R:R:    {rr}

"""
                
                relatorio += f"""💡 <b>Ação:</b>
{sintese.get('recomendacao', 'N/A')}

"""
            
            # Rodapé
            relatorio += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Próximo ciclo em {(intervalo//60)} minutos
"""
            
            print("✅")
            
            # Enviar para Telegram
            if enviar_telegram:
                print(f"\n📤 Enviando para Telegram...", end=' ', flush=True)
                
                # Enviar relatório texto
                enviar_oraculo(relatorio)
                
                # Enviar Heatmap DOM
                if heatmap_dom and os.path.exists(heatmap_dom):
                    enviar_foto(heatmap_dom, "🌊 Heatmap de Liquidez (DOM)")
                
                # Enviar TODOS os gráficos individuais (BTC, ETH, SOL)
                for symbol, grafico_path, analise in graficos_gerados:
                    score = analise.get('confluencia', {}).get('score', 0)
                    if isinstance(score, dict):
                        score = score.get('score', 0)
                    score = float(score)
                    
                    legenda = f"📈 {symbol} | Score: {score:.1f}/10"
                    enviar_foto(grafico_path, legenda)
                
                print("✅")
            
            # Exibir resumo no terminal
            print(f"\n{'='*80}")
            print(f"✅ Ciclo #{contador} completo!")
            print(f"📊 {len(analises)} pares analisados")
            print(f"📈 {len(graficos_gerados)} gráficos gerados")
            print(f"📱 Relatório enviado para Telegram")
            print(f"{'='*80}")
            
            print(f"\n⏳ Próximo ciclo em {intervalo//60} min...\n")
            await asyncio.sleep(intervalo)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("✅ ANÁLISE AUTOMÁTICA FINALIZADA")
        print(f"📊 Total de ciclos executados: {contador}")
        print("="*80 + "\n")


async def executar_sistema_completo():
    """Executa análise automática + monitoramento de alertas + relatórios multi-TF em paralelo"""
    from relatorios_multi_tf import executar_relatorio_periodico
    
    print("\n🚨 Sistema de Alertas em Tempo Real: ATIVADO")
    print("   ⚡ Monitorando S/R a cada 30 segundos")
    print("   💡 SEM cooldown - Alertas operacionais em tempo real")
    print("\n📊 Relatórios Multi-Timeframe: ATIVADOS")
    print("   • 5min  → A cada 5 minutos (com gráficos)")
    print("   • 10min → A cada 10 minutos (com gráficos)")  
    print("   • 30min → A cada 30 minutos (com gráficos)")
    print("   • 1hr   → A cada 1 hora (com gráficos + DOM)\n")
    
    try:
        # Executar todas as tarefas em paralelo
        await asyncio.gather(
            auto_analise_continua(),
            monitorar_alertas_tempo_real(PARES_AUTO, intervalo_check=30),
            executar_relatorio_periodico('5m'),
            executar_relatorio_periodico('10m'),
            executar_relatorio_periodico('30m')
        )
    except asyncio.CancelledError:
        print("\n⚠️ Análise automática cancelada pelo usuário")
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário (Ctrl+C)")


def iniciar_auto_analise():
    """Iniciar análise automática com alertas em tempo real"""
    try:
        asyncio.run(executar_sistema_completo())
    except KeyboardInterrupt:
        print("\n\n✅ Análise automática encerrada")
        print("📊 Retornando ao menu principal...")


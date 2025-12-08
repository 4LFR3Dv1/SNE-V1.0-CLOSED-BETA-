#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIOS MULTI-TIMEFRAME - Sistema de relatórios automáticos em diferentes intervalos
"""

import asyncio
import time
from datetime import datetime
from motor_renan import analise_completa
from xenos_bot import enviar_oraculo, enviar_foto
from grafico_candlestick import gerar_grafico_com_niveis
from calcular_suportes_resistencias import calcular_suportes_resistencias, calcular_range_atr
from motor_renan import coletar_dados


# Configuração de timeframes
CONFIGURACOES_TF = {
    '5m': {'intervalo': 300, 'pares': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']},
    '10m': {'intervalo': 600, 'pares': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']},
    '30m': {'intervalo': 1800, 'pares': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']},
    '1h': {'intervalo': 3600, 'pares': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']}
}


async def gerar_relatorio_tf(timeframe, pares):
    """Gera relatório detalhado para um timeframe específico"""
    
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    relatorio = f"""
📊 <b>RELATÓRIO {timeframe.upper()}</b>
⏰ {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    graficos = []
    
    for symbol in pares:
        # Análise completa
        print(f"   📊 {symbol} ({timeframe})...", end=' ')
        
        analise = analise_completa(symbol, timeframe)
        
        if 'erro' not in analise:
            sintese = analise['sintese']
            contexto = analise.get('contexto', {})
            indicadores = analise.get('indicadores', {})
            candles_detalhados = analise.get('candles_detalhados', {})
            
            preco = indicadores.get('preco', 0)
            volatilidade = contexto.get('volatilidade', 0)
            
            par_nome = symbol.replace('USDT', '')
            
            relatorio += f"""
📈 <b>{par_nome}</b> | ${preco:,.2f}

⚡ Volatilidade: {volatilidade:.2f}%
💡 Viés: {sintese.get('vies', 'N/A')}
"""
            
            # Análise de candles
            if candles_detalhados and 'erro' not in candles_detalhados:
                candle_info = candles_detalhados['candle_atual']
                precos = candles_detalhados['precos']
                classificacao = candles_detalhados['classificacao']
                tendencia = candles_detalhados['tendencia']
                
                relatorio += f"""
🕐 <b>CANDLE ATUAL:</b>
   Horário: {candle_info['timestamp_inicio']} - {candle_info['timestamp_fechamento']}
   Restante: {candle_info['tempo_restante']}
   OHLC: O:${precos['open']:,.2f} H:${precos['high']:,.2f} L:${precos['low']:,.2f} C:${precos['close']:,.2f}
   Range: ${precos['range']:,.2f} ({precos['range_percentual']}%)
   Tipo: {classificacao['tipo']} - {classificacao['significado']}
   Tendência: {tendencia['direcao']} {tendencia['intensidade']}
   Resumo: {candles_detalhados['resumo']}
"""
            
            # Adicionar níveis se houver
            entry_price = sintese.get('entry_price')
            if entry_price:
                acao = sintese.get('acao', 'N/A')
                stop_loss = sintese.get('stop_loss')
                tp2 = sintese.get('tp2')
                rr = sintese.get('rr_ratio', 'N/A')
                
                relatorio += f"""
📍 {acao}
   Entry: ${entry_price:,.2f}
   Stop:  ${stop_loss:,.2f}
   TP:    ${tp2:,.2f}
   R:R:   {rr}

"""
            else:
                relatorio += f"""
💬 {sintese.get('recomendacao', 'Aguardar')}

"""
            
            # Gerar gráfico para TODOS os timeframes
            df = coletar_dados(symbol, timeframe)
            if df is not None and not df.empty:
                sr_data = calcular_suportes_resistencias(df)
                range_data = calcular_range_atr(df)
                
                niveis = {
                    'entry': sintese.get('entry_price'),
                    'stop': sintese.get('stop_loss'),
                    'tp1': sintese.get('tp1'),
                    'tp2': sintese.get('tp2'),
                    'tp3': sintese.get('tp3')
                }
                
                grafico_path = gerar_grafico_com_niveis(
                    symbol=symbol,
                    interval=timeframe,
                    output_dir=f'reports/auto_{timeframe}/',
                    niveis_dict=niveis,
                    sr_data=sr_data,
                    range_data=range_data,
                    anotacoes=None
                )
                
                if grafico_path:
                    graficos.append((symbol, grafico_path))
            
            print("✅")
        else:
            print("❌")
    
    relatorio += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Timeframe: {timeframe.upper()}
"""
    
    return relatorio, graficos


async def executar_relatorio_periodico(timeframe):
    """Executa relatórios periódicos para um timeframe"""
    
    config = CONFIGURACOES_TF[timeframe]
    intervalo = config['intervalo']
    pares = config['pares']
    
    print(f"🔄 Relatório {timeframe.upper()} iniciado (a cada {intervalo//60} min)")
    
    contador = 0
    
    while True:
        try:
            contador += 1
            print(f"\n📊 [{timeframe.upper()}] Ciclo #{contador} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Gerar relatório
            relatorio, graficos = await gerar_relatorio_tf(timeframe, pares)
            
            # Enviar para Telegram
            enviar_oraculo(relatorio)
            
            # Enviar TODOS os gráficos
            for symbol, grafico_path in graficos:
                enviar_foto(grafico_path, f"📈 {symbol.replace('USDT', '')} | {timeframe.upper()}")
            
            print(f"   ✅ Relatório {timeframe.upper()} enviado!")
            
            # Aguardar próximo ciclo
            await asyncio.sleep(intervalo)
            
        except (KeyboardInterrupt, asyncio.CancelledError):
            print(f"\n⚠️ Relatório {timeframe.upper()} encerrado")
            break
        except Exception as e:
            print(f"   ❌ Erro no relatório {timeframe.upper()}: {e}")
            await asyncio.sleep(intervalo)


async def executar_sistema_multi_tf():
    """Executa todos os relatórios em paralelo"""
    
    print("\n" + "="*80)
    print("📊 SISTEMA DE RELATÓRIOS MULTI-TIMEFRAME")
    print("="*80)
    print("\n📈 Timeframes configurados:")
    print("   • 5min  → A cada 5 minutos")
    print("   • 10min → A cada 10 minutos")
    print("   • 30min → A cada 30 minutos")
    print("   • 1hr   → A cada 1 hora (com gráficos)")
    print("\n⚡ Pressione Ctrl+C para parar\n")
    
    # Executar todos em paralelo
    tarefas = [
        executar_relatorio_periodico('5m'),
        executar_relatorio_periodico('10m'),
        executar_relatorio_periodico('30m'),
        executar_relatorio_periodico('1h')
    ]
    
    try:
        await asyncio.gather(*tarefas)
    except KeyboardInterrupt:
        print("\n\n✅ Sistema de relatórios finalizado")


if __name__ == "__main__":
    asyncio.run(executar_sistema_multi_tf())


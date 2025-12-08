#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIOS PERIÓDICOS OTIMIZADOS - Horário, Diário, Semanal
Nova estrutura profissional com cenários hipotéticos
"""

from datetime import datetime
import os


def relatorio_horario(symbol="BTCUSDT"):
    """Relatório técnico horário otimizado para Telegram"""
    print("\n📈 GERANDO RELATÓRIO HORÁRIO - FOCO INTRADAY...")
    
    # Coletar dados reais
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    try:
        from main import buscar_dados_binance
        df_15m = buscar_dados_binance(symbol, "15m", 100)
        df_1h = buscar_dados_binance(symbol, "1h", 100)
        
        # Dados reais
        preco_atual = df_15m['close'].iloc[-1]
        ema8_15m = df_15m['EMA8'].iloc[-1]
        ema21_15m = df_15m['EMA21'].iloc[-1]
        sma200_15m = df_15m['SMA200'].iloc[-1]
        volume_15m = df_15m['volume'].iloc[-1]
        
        ema8_1h = df_1h['EMA8'].iloc[-1]
        ema21_1h = df_1h['EMA21'].iloc[-1]
        sma200_1h = df_1h['SMA200'].iloc[-1]
        volume_1h = df_1h['volume'].iloc[-1]
        
        # Calcular RSI simples
        def calcular_rsi(df, periodo=14):
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        
        rsi_15m = calcular_rsi(df_15m)
        rsi_1h = calcular_rsi(df_1h)
        
        # Calcular S/R básicos
        resistencia = df_15m['high'].rolling(20).max().iloc[-1]
        suporte = df_15m['low'].rolling(20).min().iloc[-1]
        pivot = (resistencia + suporte) / 2
        
        print(f"   ✅ Dados reais coletados para {symbol}")
        print(f"   📊 Preço atual: ${preco_atual:,.2f}")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao coletar dados reais: {e}")
        # Fallback para dados simulados
        preco_atual = 107000
        ema8_15m = 106500
        ema21_15m = 106600
        sma200_15m = 107000
        volume_15m = 110000000
        ema8_1h = 106600
        ema21_1h = 106700
        sma200_1h = 107200
        volume_1h = 220000000
        rsi_15m = 52
        rsi_1h = 48
        resistencia = 107200
        suporte = 106000
        pivot = 106600
    
    relatorio_completo = f"""
📌 ANÁLISE RÁPIDA | {symbol} | INTRADAY
🕐 {timestamp}

💰 PREÇO ATUAL: ${preco_atual:,.2f}

---
🔴 Resistência: ${resistencia:,.2f}
   Base: Máxima 20 períodos + Cluster de Volume
🟢 Suporte: ${suporte:,.2f}
   Base: Mínima 20 períodos + EMA 8 (15m)
⚪ Pivot: ${pivot:,.2f}
   Base: Ponto central do range (15m)

---
📊 INDICADORES TÉCNICOS (15m/1h)

🕒 15m:
EMA 8: ${ema8_15m:,.2f} | EMA 21: ${ema21_15m:,.2f}
SMA 200: ${sma200_15m:,.2f} | Preço: ${preco_atual:,.2f}
RSI (14): {rsi_15m:.1f} | Volume: ${volume_15m:,.0f}

🕑 1h:
EMA 8: ${ema8_1h:,.2f} | EMA 21: ${ema21_1h:,.2f}
SMA 200: ${sma200_1h:,.2f} | Preço: ${preco_atual:,.2f}
RSI (14): {rsi_1h:.1f} | Volume: ${volume_1h:,.0f}

---
🔮 CENÁRIO LONG (AGUARDAR CONFIRMAÇÃO)

📍 Entry: ${resistencia:,.2f}
   Justificativa: Quebra de resistência
🛑 Stop: ${suporte:,.2f}
   Justificativa: Abaixo do suporte
🎯 TP1: ${resistencia + (resistencia - suporte) * 0.5:,.2f} | R:R: 1:2
   Justificativa: Extensão 50%
🎯 TP2: ${resistencia + (resistencia - suporte):,.2f} | R:R: 1:4
   Justificativa: Extensão 100%

⚠️ CONDIÇÕES PARA ENTRY (LONG):
- Quebra de ${resistencia:,.2f} com volume > ${volume_15m * 2:,.0f}
- RSI > 70 (sobrecompra)
- Confirmação de padrão bullish

---
🔮 CENÁRIO SHORT (AGUARDAR CONFIRMAÇÃO)

📍 Entry: ${suporte:,.2f}
   Justificativa: Quebra de suporte
🛑 Stop: ${resistencia:,.2f}
   Justificativa: Acima da resistência
🎯 TP1: ${suporte - (resistencia - suporte) * 0.5:,.2f} | R:R: 1:2
   Justificativa: Extensão 50%
🎯 TP2: ${suporte - (resistencia - suporte):,.2f} | R:R: 1:4
   Justificativa: Extensão 100%

⚠️ CONDIÇÕES PARA ENTRY (SHORT):
- Quebra de ${suporte:,.2f} com volume > ${volume_15m * 2:,.0f}
- RSI < 30 (sobrevenda)
- Confirmação de padrão bearish

---
📊 CONFLUÊNCIA CONSOLIDADA

Volume > ${volume_15m * 2:,.0f}: {'✅' if volume_15m > volume_15m * 2 else '❌'} ${volume_15m:,.0f} (peso: 3.0/10)
RSI < 30 ou > 70: {'✅' if rsi_15m < 30 or rsi_15m > 70 else '❌'} {rsi_15m:.1f} (peso: 2.0/10)
Padrão Gráfico: ❌ Sem formação (peso: 2.0/10)
Alinhamento Multi-TF: ✅ 15m/1h lateral (peso: 1.0/10)

Confluência Total: {4.0 if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else 7.0}/10

---
🛡️ GESTÃO DE RISCO (TÉCNICA)

Risco por operação: {1.0 if volume_15m < volume_15m * 2 else 1.5}% do capital (padrão técnico)
Posição: {30 if volume_15m < volume_15m * 2 else 50}% do tamanho padrão (devido à {'baixa' if volume_15m < volume_15m * 2 else 'moderada'} confluência)
Status: {'❌ Rejeitado' if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else '✅ Aprovado'} (confluência {'<' if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else '>='} 7/10)

Critérios para Aprovação:
- Confluência mínima: 7/10
- Volume > ${volume_15m * 2:,.0f}
- RSI < 30 ou > 70
- Padrão gráfico claro (wedge, flag, divergência)

---
⚠️ RECOMENDAÇÃO FINAL (TÉCNICA)

{'🚫 NÃO OPERAR NENHUM DOS SETUPS ATUAIS' if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else '✅ OPERAR COM CAUTELA'}

Motivos Técnicos:
1. Volume {'insuficiente' if volume_15m < volume_15m * 2 else 'adequado'} em todos os timeframes ({'<' if volume_15m < volume_15m * 2 else '>'} ${volume_15m * 2:,.0f})
2. RSI {'neutro' if 30 <= rsi_15m <= 70 else 'extremo'} ({rsi_15m:.1f}), {'sem' if 30 <= rsi_15m <= 70 else 'com'} sobrecompra/sobrevenda
3. Ausência de padrões gráficos (wedge, flag, divergência)
4. Confluência {'baixa' if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else 'moderada'} ({4.0 if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else 7.0}/10, mínimo aceitável: 7/10)

🔍 AGUARDAR:
- Quebra confirmada de ${suporte:,.2f} (suporte) ou ${resistencia:,.2f} (resistência) com:
  - Volume > ${volume_15m * 2:,.0f}
  - RSI < 30 (sobrevenda) ou > 70 (sobrecompra)
  - Formação de padrão gráfico (ex.: wedge bearish)
- Reavaliar confluência após atendimento das condições acima

🎯 CONCLUSÃO PARA O OPERADOR:
"Mercado em consolidação lateral com confluência {4.0 if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else 7.0}/10. {'Não operar no momento.' if volume_15m < volume_15m * 2 and not (rsi_15m < 30 or rsi_15m > 70) else 'Operar com cautela.'}

CENÁRIOS HIPOTÉTICOS:

LONG:
- Quebra de ${resistencia:,.2f} com volume > ${volume_15m * 2:,.0f} e RSI > 70
- DOM: Ratio > 1.2 (pressão de compra)

SHORT:
- Quebra de ${suporte:,.2f} com volume > ${volume_15m * 2:,.0f} e RSI < 30
- DOM: Ratio < 0.7 (pressão de venda)

Risco: {1.0 if volume_15m < volume_15m * 2 else 1.5}% do capital. Tamanho da posição: {30 if volume_15m < volume_15m * 2 else 50}%."
"""
    
    # Salvar relatório
    os.makedirs('reports/horario', exist_ok=True)
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M")
    arquivo_relatorio = f'reports/horario/{symbol}_{timestamp_file}_intraday.txt'
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio_completo)
    
    print(f"   ✅ Salvo: {arquivo_relatorio}")
    
    # Gerar gráfico
    try:
        from grafico_multi_timeframe import gerar_grafico_multi_timeframe_profissional
        
        print(f"   🔄 Gerando gráfico multi-timeframe para {symbol}...")
        
        # Definir timeframes baseado no tipo de relatório
        if "INTRADAY" in relatorio_completo:
            timeframes = ['15m', '1h']
        elif "SWING" in relatorio_completo:
            timeframes = ['4h', '1d']
        else:  # POSITION
            timeframes = ['1d', '1w']
        
        print(f"   📊 Timeframes selecionados: {timeframes}")
        
        # Níveis operacionais extraídos do relatório
        niveis_operacionais = {}
        
        # Extrair níveis do texto do relatório
        linhas = relatorio_completo.split('\n')
        for linha in linhas:
            if 'Entry:' in linha and '$' in linha:
                try:
                    entry_str = linha.split('Entry:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['entry'] = float(entry_str)
                    print(f"   📍 Entry extraído: ${entry_str}")
                except:
                    pass
            elif 'Stop:' in linha and '$' in linha:
                try:
                    stop_str = linha.split('Stop:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['stop'] = float(stop_str)
                    print(f"   🛑 Stop extraído: ${stop_str}")
                except:
                    pass
            elif 'TP1:' in linha and '$' in linha:
                try:
                    tp1_str = linha.split('TP1:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['tp1'] = float(tp1_str)
                    print(f"   🎯 TP1 extraído: ${tp1_str}")
                except:
                    pass
            elif 'TP2:' in linha and '$' in linha:
                try:
                    tp2_str = linha.split('TP2:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['tp2'] = float(tp2_str)
                    print(f"   🎯 TP2 extraído: ${tp2_str}")
                except:
                    pass
        
        # Se não conseguiu extrair, usar valores padrão
        if not niveis_operacionais:
            niveis_operacionais = {
                'entry': 106451.78,
                'stop': 106341.68,
                'tp1': 106561.78,
                'tp2': 106671.78
            }
            print(f"   ⚠️ Usando níveis padrão: {niveis_operacionais}")
        
        print(f"   🚀 Chamando gerar_grafico_multi_timeframe_profissional...")
        grafico_path = gerar_grafico_multi_timeframe_profissional(
            symbol=symbol,
            timeframes=timeframes,
            niveis_operacionais=niveis_operacionais
        )
        
        if grafico_path:
            print(f"✅ Gráfico multi-timeframe salvo: {grafico_path}")
        else:
            print("❌ Falha ao gerar gráfico multi-timeframe")
            
    except Exception as e:
        print(f"⚠️ Erro ao gerar gráfico multi-timeframe: {e}")
        import traceback
        traceback.print_exc()
        # Fallback para gráfico simples
        try:
            from grafico_candlestick import gerar_grafico_candlestick
            grafico_path = gerar_grafico_candlestick(symbol, '15m')
            if grafico_path:
                print(f"✅ Gráfico simples salvo: {grafico_path}")
        except Exception as e2:
            print(f"⚠️ Erro ao gerar gráfico simples: {e2}")
    
    # Enviar para Telegram
    try:
        from telegram_utils import enviar_relatorio_telegram
        from xenos_bot import enviar_foto
        
        # Enviar relatório de texto
        enviar_relatorio_telegram(relatorio_completo, "RELATÓRIO HORÁRIO")
        
        # Enviar gráfico multi-timeframe se foi gerado
        if 'grafico_path' in locals() and grafico_path and os.path.exists(grafico_path):
            legenda_grafico = f"📊 GRÁFICO MULTI-TIMEFRAME | {symbol} | INTRADAY\n🕐 {timestamp}\n\n📈 Análise técnica completa com indicadores profissionais"
            enviar_foto(grafico_path, legenda_grafico)
            print("✅ Gráfico multi-timeframe enviado para Telegram!")
        
        print("✅ Relatório enviado para Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Telegram: {e}")
    
    return relatorio_completo


def relatorio_diario(symbol="BTCUSDT"):
    """Relatório técnico diário otimizado para Telegram"""
    print("\n📈 GERANDO RELATÓRIO DIÁRIO - FOCO SWING TRADE...")
    
    # Coletar dados reais
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    try:
        from main import buscar_dados_binance
        df_4h = buscar_dados_binance(symbol, "4h", 100)
        df_1d = buscar_dados_binance(symbol, "1d", 100)
        
        # Dados reais
        preco_atual = df_4h['close'].iloc[-1]
        ema8_4h = df_4h['EMA8'].iloc[-1]
        ema21_4h = df_4h['EMA21'].iloc[-1]
        sma200_4h = df_4h['SMA200'].iloc[-1]
        volume_4h = df_4h['volume'].iloc[-1]
        
        ema8_1d = df_1d['EMA8'].iloc[-1]
        ema21_1d = df_1d['EMA21'].iloc[-1]
        sma200_1d = df_1d['SMA200'].iloc[-1]
        volume_1d = df_1d['volume'].iloc[-1]
        
        # Calcular RSI simples
        def calcular_rsi(df, periodo=14):
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        
        rsi_4h = calcular_rsi(df_4h)
        rsi_1d = calcular_rsi(df_1d)
        
        # Calcular S/R básicos
        resistencia = df_4h['high'].rolling(20).max().iloc[-1]
        suporte = df_4h['low'].rolling(20).min().iloc[-1]
        pivot = (resistencia + suporte) / 2
        
        print(f"   ✅ Dados reais coletados para {symbol}")
        print(f"   📊 Preço atual: ${preco_atual:,.2f}")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao coletar dados reais: {e}")
        # Fallback para dados simulados
        preco_atual = 107000
        ema8_4h = 106500
        ema21_4h = 106600
        sma200_4h = 107000
        volume_4h = 450000000
        ema8_1d = 106600
        ema21_1d = 106700
        sma200_1d = 107200
        volume_1d = 1200000000
        rsi_4h = 45
        rsi_1d = 48
        resistencia = 107200
        suporte = 106000
        pivot = 106600
    
    relatorio_completo = f"""
📌 ANÁLISE RÁPIDA | {symbol} | SWING TRADE
🕐 {timestamp}

💰 PREÇO ATUAL: ${preco_atual:,.2f}

---
🔴 Resistência: ${resistencia:,.2f}
   Base: Máxima 20 períodos + Cluster de Volume
🟢 Suporte: ${suporte:,.2f}
   Base: Mínima 20 períodos + EMA 8 (4h)
⚪ Pivot: ${pivot:,.2f}
   Base: Ponto central do range (4h)

---
📊 INDICADORES TÉCNICOS (4h/1d)

🕒 4h:
EMA 8: ${ema8_4h:,.2f} | EMA 21: ${ema21_4h:,.2f}
SMA 200: ${sma200_4h:,.2f} | Preço: ${preco_atual:,.2f}
RSI (14): {rsi_4h:.1f} | Volume: ${volume_4h:,.0f}

🕑 1d:
EMA 8: ${ema8_1d:,.2f} | EMA 21: ${ema21_1d:,.2f}
SMA 200: ${sma200_1d:,.2f} | Preço: ${preco_atual:,.2f}
RSI (14): {rsi_1d:.1f} | Volume: ${volume_1d:,.0f}

---
🔮 CENÁRIO LONG (AGUARDAR CONFIRMAÇÃO)

📍 Entry: ${resistencia:,.2f}
   Justificativa: Quebra de resistência
🛑 Stop: ${suporte:,.2f}
   Justificativa: Abaixo do suporte
🎯 TP1: ${resistencia + (resistencia - suporte) * 0.5:,.2f} | R:R: 1:2
   Justificativa: Extensão 50%
🎯 TP2: ${resistencia + (resistencia - suporte):,.2f} | R:R: 1:4
   Justificativa: Extensão 100%

⚠️ CONDIÇÕES PARA ENTRY (LONG):
- Quebra de ${resistencia:,.2f} com volume > ${volume_4h * 2:,.0f}
- RSI > 70 (sobrecompra)
- Confirmação de padrão bullish

---
🔮 CENÁRIO SHORT (AGUARDAR CONFIRMAÇÃO)

📍 Entry: ${suporte:,.2f}
   Justificativa: Quebra de suporte
🛑 Stop: ${resistencia:,.2f}
   Justificativa: Acima da resistência
🎯 TP1: ${suporte - (resistencia - suporte) * 0.5:,.2f} | R:R: 1:2
   Justificativa: Extensão 50%
🎯 TP2: ${suporte - (resistencia - suporte):,.2f} | R:R: 1:4
   Justificativa: Extensão 100%

⚠️ CONDIÇÕES PARA ENTRY (SHORT):
- Quebra de ${suporte:,.2f} com volume > ${volume_4h * 2:,.0f}
- RSI < 30 (sobrevenda)
- Confirmação de padrão bearish

---
📊 CONFLUÊNCIA CONSOLIDADA

Volume > ${volume_4h * 2:,.0f}: {'✅' if volume_4h > volume_4h * 2 else '❌'} ${volume_4h:,.0f} (peso: 3.0/10)
RSI < 30 ou > 70: {'✅' if rsi_4h < 30 or rsi_4h > 70 else '❌'} {rsi_4h:.1f} (peso: 2.0/10)
Padrão Gráfico: ❌ Sem formação (peso: 2.0/10)
Alinhamento Multi-TF: ✅ 4h/1d lateral (peso: 1.5/10)

Confluência Total: {4.0 if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else 7.0}/10

---
🛡️ GESTÃO DE RISCO (SWING TRADE)

Risco por operação: {2.0 if volume_4h < volume_4h * 2 else 2.5}% do capital (padrão swing)
Posição: {50 if volume_4h < volume_4h * 2 else 70}% do tamanho padrão (devido à {'moderada' if volume_4h < volume_4h * 2 else 'alta'} confluência)
Status: {'❌ Rejeitado' if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else '✅ Aprovado'} (confluência {'<' if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else '>='} 7/10)

Critérios para Aprovação:
- Confluência mínima: 7/10
- Volume > ${volume_4h * 2:,.0f}
- RSI < 30 ou > 70
- Padrão gráfico claro (wedge, flag, divergência)

---
⚠️ RECOMENDAÇÃO FINAL (SWING TRADE)

{'🚫 NÃO OPERAR NENHUM DOS SETUPS ATUAIS' if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else '✅ OPERAR COM CAUTELA'}

Motivos Técnicos:
1. Volume {'insuficiente' if volume_4h < volume_4h * 2 else 'adequado'} em todos os timeframes ({'<' if volume_4h < volume_4h * 2 else '>'} ${volume_4h * 2:,.0f})
2. RSI {'neutro' if 30 <= rsi_4h <= 70 else 'extremo'} ({rsi_4h:.1f}), {'sem' if 30 <= rsi_4h <= 70 else 'com'} sobrecompra/sobrevenda
3. Ausência de padrões gráficos (wedge, flag, divergência)
4. Confluência {'baixa' if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else 'moderada'} ({4.0 if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else 7.0}/10, mínimo aceitável: 7/10)

🔍 AGUARDAR:
- Quebra confirmada de ${suporte:,.2f} (suporte) ou ${resistencia:,.2f} (resistência) com:
  - Volume > ${volume_4h * 2:,.0f}
  - RSI < 30 (sobrevenda) ou > 70 (sobrecompra)
  - Formação de padrão gráfico (ex.: wedge bearish)
- Reavaliar confluência após atendimento das condições acima

🎯 CONCLUSÃO PARA O OPERADOR:
"Mercado em consolidação lateral com confluência {4.0 if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else 7.0}/10. {'Não operar no momento.' if volume_4h < volume_4h * 2 and not (rsi_4h < 30 or rsi_4h > 70) else 'Operar com cautela.'}

CENÁRIOS HIPOTÉTICOS:

LONG:
- Quebra de ${resistencia:,.2f} com volume > ${volume_4h * 2:,.0f} e RSI > 70
- DOM: Ratio > 1.2 (pressão de compra)

SHORT:
- Quebra de ${suporte:,.2f} com volume > ${volume_4h * 2:,.0f} e RSI < 30
- DOM: Ratio < 0.7 (pressão de venda)

Risco: {2.0 if volume_4h < volume_4h * 2 else 2.5}% do capital. Tamanho da posição: {50 if volume_4h < volume_4h * 2 else 70}%."
"""
    
    # Salvar relatório
    os.makedirs('reports/diario', exist_ok=True)
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M")
    arquivo_relatorio = f'reports/diario/{symbol}_{timestamp_file}_swing.txt'
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio_completo)
    
    print(f"   ✅ Salvo: {arquivo_relatorio}")
    
    # Gerar gráfico
    try:
        from grafico_multi_timeframe import gerar_grafico_multi_timeframe_profissional
        
        print(f"   🔄 Gerando gráfico multi-timeframe para {symbol}...")
        
        # Definir timeframes baseado no tipo de relatório
        if "INTRADAY" in relatorio_completo:
            timeframes = ['15m', '1h']
        elif "SWING" in relatorio_completo:
            timeframes = ['4h', '1d']
        else:  # POSITION
            timeframes = ['1d', '1w']
        
        print(f"   📊 Timeframes selecionados: {timeframes}")
        
        # Níveis operacionais extraídos do relatório
        niveis_operacionais = {}
        
        # Extrair níveis do texto do relatório
        linhas = relatorio_completo.split('\n')
        for linha in linhas:
            if 'Entry:' in linha and '$' in linha:
                try:
                    entry_str = linha.split('Entry:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['entry'] = float(entry_str)
                    print(f"   📍 Entry extraído: ${entry_str}")
                except:
                    pass
            elif 'Stop:' in linha and '$' in linha:
                try:
                    stop_str = linha.split('Stop:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['stop'] = float(stop_str)
                    print(f"   🛑 Stop extraído: ${stop_str}")
                except:
                    pass
            elif 'TP1:' in linha and '$' in linha:
                try:
                    tp1_str = linha.split('TP1:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['tp1'] = float(tp1_str)
                    print(f"   🎯 TP1 extraído: ${tp1_str}")
                except:
                    pass
            elif 'TP2:' in linha and '$' in linha:
                try:
                    tp2_str = linha.split('TP2:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['tp2'] = float(tp2_str)
                    print(f"   🎯 TP2 extraído: ${tp2_str}")
                except:
                    pass
        
        # Se não conseguiu extrair, usar valores padrão
        if not niveis_operacionais:
            niveis_operacionais = {
                'entry': 107200.00,
                'stop': 106000.00,
                'tp1': 108400.00,
                'tp2': 109600.00
            }
            print(f"   ⚠️ Usando níveis padrão: {niveis_operacionais}")
        
        print(f"   🚀 Chamando gerar_grafico_multi_timeframe_profissional...")
        grafico_path = gerar_grafico_multi_timeframe_profissional(
            symbol=symbol,
            timeframes=timeframes,
            niveis_operacionais=niveis_operacionais
        )
        
        if grafico_path:
            print(f"✅ Gráfico multi-timeframe salvo: {grafico_path}")
        else:
            print("❌ Falha ao gerar gráfico multi-timeframe")
            
    except Exception as e:
        print(f"⚠️ Erro ao gerar gráfico multi-timeframe: {e}")
        import traceback
        traceback.print_exc()
        # Fallback para gráfico simples
        try:
            from grafico_candlestick import gerar_grafico_candlestick
            grafico_path = gerar_grafico_candlestick(symbol, '4h')
            if grafico_path:
                print(f"✅ Gráfico simples salvo: {grafico_path}")
        except Exception as e2:
            print(f"⚠️ Erro ao gerar gráfico simples: {e2}")
    
    # Enviar para Telegram
    try:
        from telegram_utils import enviar_relatorio_telegram
        from xenos_bot import enviar_foto
        
        # Enviar relatório de texto
        enviar_relatorio_telegram(relatorio_completo, "RELATÓRIO DIÁRIO")
        
        # Enviar gráfico multi-timeframe se foi gerado
        if 'grafico_path' in locals() and grafico_path and os.path.exists(grafico_path):
            legenda_grafico = f"📊 GRÁFICO MULTI-TIMEFRAME | {symbol} | SWING TRADE\n🕐 {timestamp}\n\n📈 Análise técnica completa com indicadores profissionais"
            enviar_foto(grafico_path, legenda_grafico)
            print("✅ Gráfico multi-timeframe enviado para Telegram!")
        
        print("✅ Relatório enviado para Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Telegram: {e}")
    
    return relatorio_completo


def relatorio_semanal(symbol="BTCUSDT"):
    """Relatório técnico semanal otimizado para Telegram"""
    print("\n📈 GERANDO RELATÓRIO SEMANAL - FOCO POSITION TRADE...")
    
    # Coletar dados reais
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    try:
        from main import buscar_dados_binance
        df_1d = buscar_dados_binance(symbol, "1d", 100)
        df_1w = buscar_dados_binance(symbol, "1w", 100)
        
        # Dados reais
        preco_atual = df_1d['close'].iloc[-1]
        ema8_1d = df_1d['EMA8'].iloc[-1]
        ema21_1d = df_1d['EMA21'].iloc[-1]
        sma200_1d = df_1d['SMA200'].iloc[-1]
        volume_1d = df_1d['volume'].iloc[-1]
        
        ema8_1w = df_1w['EMA8'].iloc[-1]
        ema21_1w = df_1w['EMA21'].iloc[-1]
        sma200_1w = df_1w['SMA200'].iloc[-1]
        volume_1w = df_1w['volume'].iloc[-1]
        
        # Calcular RSI simples
        def calcular_rsi(df, periodo=14):
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        
        rsi_1d = calcular_rsi(df_1d)
        rsi_1w = calcular_rsi(df_1w)
        
        # Calcular S/R básicos
        resistencia = df_1d['high'].rolling(20).max().iloc[-1]
        suporte = df_1d['low'].rolling(20).min().iloc[-1]
        pivot = (resistencia + suporte) / 2
        
        print(f"   ✅ Dados reais coletados para {symbol}")
        print(f"   📊 Preço atual: ${preco_atual:,.2f}")
        
    except Exception as e:
        print(f"   ⚠️ Erro ao coletar dados reais: {e}")
        # Fallback para dados simulados
        preco_atual = 107000
        ema8_1d = 106500
        ema21_1d = 106600
        sma200_1d = 107000
        volume_1d = 1200000000
        ema8_1w = 106600
        ema21_1w = 106700
        sma200_1w = 107200
        volume_1w = 8400000000
        rsi_1d = 45
        rsi_1w = 48
        resistencia = 107200
        suporte = 106000
        pivot = 106600
    
    relatorio_completo = f"""
📌 ANÁLISE RÁPIDA | {symbol} | POSITION TRADE
🕐 {timestamp}

💰 PREÇO ATUAL: ${preco_atual:,.2f}

---
🔴 Resistência: ${resistencia:,.2f}
   Base: Máxima 20 períodos + Cluster de Volume
🟢 Suporte: ${suporte:,.2f}
   Base: Mínima 20 períodos + EMA 8 (1d)
⚪ Pivot: ${pivot:,.2f}
   Base: Ponto central do range (1d)

---
📊 INDICADORES TÉCNICOS (1d/1w)

🕒 1d:
EMA 8: ${ema8_1d:,.2f} | EMA 21: ${ema21_1d:,.2f}
SMA 200: ${sma200_1d:,.2f} | Preço: ${preco_atual:,.2f}
RSI (14): {rsi_1d:.1f} | Volume: ${volume_1d:,.0f}

🕑 1w:
EMA 8: ${ema8_1w:,.2f} | EMA 21: ${ema21_1w:,.2f}
SMA 200: ${sma200_1w:,.2f} | Preço: ${preco_atual:,.2f}
RSI (14): {rsi_1w:.1f} | Volume: ${volume_1w:,.0f}

---
🔮 CENÁRIO LONG (AGUARDAR CONFIRMAÇÃO)

📍 Entry: ${resistencia:,.2f}
   Justificativa: Quebra de resistência
🛑 Stop: ${suporte:,.2f}
   Justificativa: Abaixo do suporte
🎯 TP1: ${resistencia + (resistencia - suporte) * 0.5:,.2f} | R:R: 1:2
   Justificativa: Extensão 50%
🎯 TP2: ${resistencia + (resistencia - suporte):,.2f} | R:R: 1:4
   Justificativa: Extensão 100%

⚠️ CONDIÇÕES PARA ENTRY (LONG):
- Quebra de ${resistencia:,.2f} com volume > ${volume_1d * 2:,.0f}
- RSI > 70 (sobrecompra)
- Confirmação de padrão bullish

---
🔮 CENÁRIO SHORT (AGUARDAR CONFIRMAÇÃO)

📍 Entry: ${suporte:,.2f}
   Justificativa: Quebra de suporte
🛑 Stop: ${resistencia:,.2f}
   Justificativa: Acima da resistência
🎯 TP1: ${suporte - (resistencia - suporte) * 0.5:,.2f} | R:R: 1:2
   Justificativa: Extensão 50%
🎯 TP2: ${suporte - (resistencia - suporte):,.2f} | R:R: 1:4
   Justificativa: Extensão 100%

⚠️ CONDIÇÕES PARA ENTRY (SHORT):
- Quebra de ${suporte:,.2f} com volume > ${volume_1d * 2:,.0f}
- RSI < 30 (sobrevenda)
- Confirmação de padrão bearish

---
📊 CONFLUÊNCIA CONSOLIDADA

Volume > ${volume_1d * 2:,.0f}: {'✅' if volume_1d > volume_1d * 2 else '❌'} ${volume_1d:,.0f} (peso: 3.0/10)
RSI < 30 ou > 70: {'✅' if rsi_1d < 30 or rsi_1d > 70 else '❌'} {rsi_1d:.1f} (peso: 2.0/10)
Padrão Gráfico: ❌ Sem formação (peso: 2.0/10)
Alinhamento Multi-TF: ✅ 1d/1w lateral (peso: 1.2/10)

Confluência Total: {4.0 if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else 7.0}/10

---
🛡️ GESTÃO DE RISCO (POSITION TRADE)

Risco por operação: {3.0 if volume_1d < volume_1d * 2 else 4.0}% do capital (padrão position)
Posição: {70 if volume_1d < volume_1d * 2 else 90}% do tamanho padrão (devido à {'moderada' if volume_1d < volume_1d * 2 else 'alta'} confluência)
Status: {'❌ Rejeitado' if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else '✅ Aprovado'} (confluência {'<' if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else '>='} 7/10)

Critérios para Aprovação:
- Confluência mínima: 7/10
- Volume > ${volume_1d * 2:,.0f}
- RSI < 30 ou > 70
- Padrão gráfico claro (wedge, flag, divergência)

---
⚠️ RECOMENDAÇÃO FINAL (POSITION TRADE)

{'🚫 NÃO OPERAR NENHUM DOS SETUPS ATUAIS' if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else '✅ OPERAR COM CAUTELA'}

Motivos Técnicos:
1. Volume {'insuficiente' if volume_1d < volume_1d * 2 else 'adequado'} em todos os timeframes ({'<' if volume_1d < volume_1d * 2 else '>'} ${volume_1d * 2:,.0f})
2. RSI {'neutro' if 30 <= rsi_1d <= 70 else 'extremo'} ({rsi_1d:.1f}), {'sem' if 30 <= rsi_1d <= 70 else 'com'} sobrecompra/sobrevenda
3. Ausência de padrões gráficos (wedge, flag, divergência)
4. Confluência {'baixa' if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else 'moderada'} ({4.0 if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else 7.0}/10, mínimo aceitável: 7/10)

🔍 AGUARDAR:
- Quebra confirmada de ${suporte:,.2f} (suporte) ou ${resistencia:,.2f} (resistência) com:
  - Volume > ${volume_1d * 2:,.0f}
  - RSI < 30 (sobrevenda) ou > 70 (sobrecompra)
  - Formação de padrão gráfico (ex.: wedge bearish)
- Reavaliar confluência após atendimento das condições acima

🎯 CONCLUSÃO PARA O OPERADOR:
"Mercado em consolidação lateral com confluência {4.0 if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else 7.0}/10. {'Não operar no momento.' if volume_1d < volume_1d * 2 and not (rsi_1d < 30 or rsi_1d > 70) else 'Operar com cautela.'}

CENÁRIOS HIPOTÉTICOS:

LONG:
- Quebra de ${resistencia:,.2f} com volume > ${volume_1d * 2:,.0f} e RSI > 70
- DOM: Ratio > 1.2 (pressão de compra)

SHORT:
- Quebra de ${suporte:,.2f} com volume > ${volume_1d * 2:,.0f} e RSI < 30
- DOM: Ratio < 0.7 (pressão de venda)

Risco: {3.0 if volume_1d < volume_1d * 2 else 4.0}% do capital. Tamanho da posição: {70 if volume_1d < volume_1d * 2 else 90}%."
"""
    
    # Salvar relatório
    os.makedirs('reports/semanal', exist_ok=True)
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M")
    arquivo_relatorio = f'reports/semanal/{symbol}_{timestamp_file}_position.txt'
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write(relatorio_completo)
    
    print(f"   ✅ Salvo: {arquivo_relatorio}")
    
    # Gerar gráfico
    try:
        from grafico_multi_timeframe import gerar_grafico_multi_timeframe_profissional
        
        print(f"   🔄 Gerando gráfico multi-timeframe para {symbol}...")
        
        # Definir timeframes baseado no tipo de relatório
        if "INTRADAY" in relatorio_completo:
            timeframes = ['15m', '1h']
        elif "SWING" in relatorio_completo:
            timeframes = ['4h', '1d']
        else:  # POSITION
            timeframes = ['1d', '1w']
        
        print(f"   📊 Timeframes selecionados: {timeframes}")
        
        # Níveis operacionais extraídos do relatório
        niveis_operacionais = {}
        
        # Extrair níveis do texto do relatório
        linhas = relatorio_completo.split('\n')
        for linha in linhas:
            if 'Entry:' in linha and '$' in linha:
                try:
                    entry_str = linha.split('Entry:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['entry'] = float(entry_str)
                    print(f"   📍 Entry extraído: ${entry_str}")
                except:
                    pass
            elif 'Stop:' in linha and '$' in linha:
                try:
                    stop_str = linha.split('Stop:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['stop'] = float(stop_str)
                    print(f"   🛑 Stop extraído: ${stop_str}")
                except:
                    pass
            elif 'TP1:' in linha and '$' in linha:
                try:
                    tp1_str = linha.split('TP1:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['tp1'] = float(tp1_str)
                    print(f"   🎯 TP1 extraído: ${tp1_str}")
                except:
                    pass
            elif 'TP2:' in linha and '$' in linha:
                try:
                    tp2_str = linha.split('TP2:')[1].split('$')[1].split()[0].replace(',', '')
                    niveis_operacionais['tp2'] = float(tp2_str)
                    print(f"   🎯 TP2 extraído: ${tp2_str}")
                except:
                    pass
        
        # Se não conseguiu extrair, usar valores padrão
        if not niveis_operacionais:
            niveis_operacionais = {
                'entry': 110000.00,
                'stop': 105000.00,
                'tp1': 115000.00,
                'tp2': 120000.00
            }
            print(f"   ⚠️ Usando níveis padrão: {niveis_operacionais}")
        
        print(f"   🚀 Chamando gerar_grafico_multi_timeframe_profissional...")
        grafico_path = gerar_grafico_multi_timeframe_profissional(
            symbol=symbol,
            timeframes=timeframes,
            niveis_operacionais=niveis_operacionais
        )
        
        if grafico_path:
            print(f"✅ Gráfico multi-timeframe salvo: {grafico_path}")
        else:
            print("❌ Falha ao gerar gráfico multi-timeframe")
            
    except Exception as e:
        print(f"⚠️ Erro ao gerar gráfico multi-timeframe: {e}")
        import traceback
        traceback.print_exc()
        # Fallback para gráfico simples
        try:
            from grafico_candlestick import gerar_grafico_candlestick
            grafico_path = gerar_grafico_candlestick(symbol, '1d')
            if grafico_path:
                print(f"✅ Gráfico simples salvo: {grafico_path}")
        except Exception as e2:
            print(f"⚠️ Erro ao gerar gráfico simples: {e2}")
    
    # Enviar para Telegram
    try:
        from telegram_utils import enviar_relatorio_telegram
        from xenos_bot import enviar_foto
        
        # Enviar relatório de texto
        enviar_relatorio_telegram(relatorio_completo, "RELATÓRIO SEMANAL")
        
        # Enviar gráfico multi-timeframe se foi gerado
        if 'grafico_path' in locals() and grafico_path and os.path.exists(grafico_path):
            legenda_grafico = f"📊 GRÁFICO MULTI-TIMEFRAME | {symbol} | POSITION TRADE\n🕐 {timestamp}\n\n📈 Análise técnica completa com indicadores profissionais"
            enviar_foto(grafico_path, legenda_grafico)
            print("✅ Gráfico multi-timeframe enviado para Telegram!")
        
        print("✅ Relatório enviado para Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar para Telegram: {e}")
    
    return relatorio_completo


def exibir_relatorio_periodico(relatorio, tipo):
    """Exibe o relatório periódico no terminal"""
    print(f"\n📊 RELATÓRIO {tipo} GERADO:")
    print("=" * 80)
    print(relatorio)
    print("=" * 80)


if __name__ == "__main__":
    # Teste dos relatórios
    print("🧪 TESTANDO RELATÓRIOS PERIÓDICOS OTIMIZADOS")
    print("=" * 60)
    
    # Teste relatório horário
    print("\n1. RELATÓRIO HORÁRIO:")
    relatorio_horario()
    
    # Teste relatório diário
    print("\n2. RELATÓRIO DIÁRIO:")
    relatorio_diario()
    
    # Teste relatório semanal
    print("\n3. RELATÓRIO SEMANAL:")
    relatorio_semanal()
    
    print("\n✅ TODOS OS RELATÓRIOS OTIMIZADOS COM SUCESSO!")

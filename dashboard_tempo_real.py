#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD TEMPO REAL - Monitoramento contínuo otimizado
"""

import time
import sys
import io
from motor_renan import analise_completa
from multi_pair_analise import PARES_PRINCIPAIS
from datetime import datetime


def dashboard_tempo_real(pares=None, intervalo=15):
    """Dashboard de monitoramento em tempo real - INTRADAY RÁPIDO"""
    
    if pares is None:
        pares = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']  # Pares fixos principais
    
    # Timeframes curtos rotativos - 4 ONDAS (removido 10m)
    timeframes = ['1m', '5m', '15m', '30m']
    
    print("\n" + "="*120)
    print("🎛️ DASHBOARD TÉCNICO TEMPO REAL - SISTEMA DE ONDAS")
    print("="*120)
    print(f"📊 Monitorando: {', '.join([p.replace('USDT', '') for p in pares])}")
    print(f"⏰ Atualização: A cada {intervalo}s")
    print(f"🌊 Ondas: 1️⃣ 1m → 2️⃣ 5m → 3️⃣ 15m → 4️⃣ 30m (ciclo)")
    print(f"📱 Relatório Texto: A cada 1 min (todos os ciclos)")
    print(f"📊 Gráficos Unificados: Primeiro ciclo (#1) + depois a cada 5 min (#6, #11, #16...)")
    print(f"🎯 Total: 4 gráficos (Confluência + Heatmap + Medidores + S/R)")
    print("\n⚡ Pressione Ctrl+C para parar\n")
    
    try:
        contador = 0
        ciclo_num = 1
        dados_ciclo = {}
        
        while True:
            contador += 1
            # Rotacionar timeframes a cada ciclo
            tf_atual = timeframes[(contador - 1) % len(timeframes)]
            
            # Coletar dados da onda
            dados_onda = exibir_dashboard(pares, contador, tf_atual, retornar_dados=True)
            dados_ciclo[tf_atual] = dados_onda
            
            # Verificar se completou ciclo de 4 ondas
            if contador % len(timeframes) == 0:
                # Verificar se deve gerar gráficos:
                # - Sempre no primeiro ciclo (ciclo_num == 1)
                # - Depois a cada 5 minutos (ciclos 6, 11, 16, 21...)
                enviar_graficos = (ciclo_num == 1) or ((ciclo_num - 1) % 5 == 0 and ciclo_num > 1)
                
                graficos = None
                if enviar_graficos:
                    # Gerar gráficos unificados no primeiro ciclo e depois a cada 5 min
                    print(f"\n📊 Gerando 4 gráficos unificados (ciclo {ciclo_num})...")
                    from dashboard_graficos import gerar_todos_graficos
                    graficos = gerar_todos_graficos(dados_ciclo, pares, ciclo_num)
                
                # Enviar relatório ao Telegram (sempre texto, gráficos só a cada 5 min)
                print(f"\n📤 Enviando relatório do Ciclo #{ciclo_num} ao Telegram...")
                enviar_relatorio_telegram(dados_ciclo, ciclo_num, pares, graficos)
                
                ciclo_num += 1
                dados_ciclo = {}  # Resetar para próximo ciclo
            
            # Countdown visual
            for i in range(intervalo, 0, -1):
                sys.stdout.write(f"\r⏳ Próxima atualização em {i:02d}s (próximo TF: {timeframes[contador % len(timeframes)]})... (Ctrl+C para sair)   ")
                sys.stdout.flush()
                time.sleep(1)
            print()  # Nova linha após countdown
            
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard finalizado - Retornando ao menu principal...")


def exibir_dashboard(pares, ciclo=1, timeframe='5m', retornar_dados=False):
    """Exibe dashboard formatado com supressão de prints verbose"""
    
    # Limpar tela (multiplataforma)
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Armazenar dados se solicitado
    dados_retorno = {} if retornar_dados else None
    
    hora_atual = datetime.now().strftime('%H:%M:%S')
    data_atual = datetime.now().strftime('%d/%m/%Y')
    
    # Cache para ATR médio histórico por par (calibração adaptativa)
    global atr_historico_cache
    if 'atr_historico_cache' not in globals():
        atr_historico_cache = {}
    
    # Determinar tipo de análise por TF e número da onda
    tf_info = {
        '1m':  {'tipo': 'SCALP', 'onda': '1️⃣'},
        '5m':  {'tipo': 'SCALP', 'onda': '2️⃣'},
        '15m': {'tipo': 'DAY',   'onda': '3️⃣'},
        '30m': {'tipo': 'INTRA', 'onda': '4️⃣'}
    }
    
    info = tf_info.get(timeframe, {'tipo': 'INTRA', 'onda': '🌊'})
    
    print("="*120)
    print(f"🎛️ ONDA {info['onda']} - TF: {timeframe.upper()} ({info['tipo']}) | Ciclo #{ciclo}")
    print("="*120)
    print(f"🕐 {hora_atual} | 📅 {data_atual}\n")
    
    # Header da tabela - FOCADO EM POSIÇÃO ABERTA (colunas maiores)
    print(f"{'Par':<6} {'Preço':<14} {'Estado':<15} {'Resistência':<18} {'Suporte':<18} {'Range':<15} {'Força':<16} {'Score':<6}")
    print("-" * 120)
    
    for par in pares:
        try:
            # Suprimir prints verbose do analise_completa
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            analise = analise_completa(par, timeframe)
            
            sys.stdout = old_stdout
            
            if analise and 'erro' not in analise:
                preco = analise['indicadores'].get('preco', 0)
                ind = analise['indicadores']
                estrutura = analise['estrutura']
                contexto = analise['contexto']
                
                # Score pode ser dict ou float
                score_raw = analise['confluencia'].get('score', 0)
                score = score_raw.get('score', 0) if isinstance(score_raw, dict) else score_raw
                
                # ESTADO DO MERCADO - considerar ATR/Range no timeframe
                tendencia = estrutura.get('tendencia', 'LATERAL')
                regime = contexto.get('regime', 'N/A')
                
                # Determinar estado baseado em ADX, volatilidade E range
                adx = ind.get('ADX', 0)
                volatilidade = contexto.get('volatilidade', 0)
                
                # Calcular ATR primeiro para usar na classificação
                atr_temp = ind.get('ATR') or ind.get('atr') or 0
                if not atr_temp or atr_temp == 0:
                    bb_upper_temp = ind.get('BB_upper', ind.get('bb_upper', 0))
                    bb_lower_temp = ind.get('BB_lower', ind.get('bb_lower', 0))
                    if bb_upper_temp and bb_lower_temp:
                        atr_temp = (bb_upper_temp - bb_lower_temp) / 2
                    else:
                        vol_temp = contexto.get('volatilidade', 1.5)
                        atr_temp = preco * (vol_temp / 100)
                
                # ATR % do preço
                atr_pct_calc = (atr_temp / preco * 100) if preco > 0 and atr_temp > 0 else 0
                
                # CALIBRAÇÃO ADAPTATIVA POR ATIVO (baseado no ATR histórico real)
                # Calcular ATR médio histórico para criar critérios personalizados
                cache_key = f"{par}_{timeframe}"
                
                if cache_key not in atr_historico_cache:
                    try:
                        # Coletar dados históricos para calibrar
                        from motor_renan import coletar_dados
                        import pandas as pd
                        
                        df_cal = coletar_dados(par, timeframe, limit=100)
                        if df_cal is not None and not df_cal.empty:
                            # Calcular ATR médio histórico (14 períodos)
                            high_low = df_cal['high'] - df_cal['low']
                            high_close = abs(df_cal['high'] - df_cal['close'].shift())
                            low_close = abs(df_cal['low'] - df_cal['close'].shift())
                            ranges = pd.concat([high_low, high_close, low_close], axis=1)
                            true_range = ranges.max(axis=1)
                            atr_medio_hist = true_range.rolling(14).mean().iloc[-1]
                            atr_pct_medio_hist = (atr_medio_hist / df_cal['close'].iloc[-1] * 100)
                            atr_historico_cache[cache_key] = atr_pct_medio_hist
                        else:
                            atr_historico_cache[cache_key] = None
                    except:
                        atr_historico_cache[cache_key] = None
                
                # Obter ATR médio histórico do cache
                atr_medio_historico = atr_historico_cache.get(cache_key)
                
                # PERFIL DE VOLATILIDADE ADAPTATIVO
                if atr_medio_historico and atr_medio_historico > 0:
                    # Usar ATR histórico para ajustar critérios dinamicamente
                    # Quanto maior o ATR histórico do ativo, mais "largo" os critérios
                    vol_multiplier = max(0.5, min(atr_medio_historico / 0.15, 2.0))
                else:
                    # Fallback: Perfil manual por ativo conhecido
                    par_nome_check = par.replace('USDT', '')
                    
                    if par_nome_check == 'BTC':
                        # BTC: Menos volátil, critérios mais apertados
                        vol_multiplier = 0.8
                    elif par_nome_check == 'ETH':
                        # ETH: Volatilidade média
                        vol_multiplier = 1.0
                    elif par_nome_check == 'SOL':
                        # SOL: Mais volátil, critérios mais largos
                        vol_multiplier = 1.3
                    else:
                        # Outros: Usar volatilidade do contexto
                        vol_multiplier = max(0.8, min(volatilidade / 1.5, 1.5)) if volatilidade > 0 else 1.0
                
                # Critérios BASE por timeframe (para ETH como referência) - 4 ondas
                if timeframe == '1m':
                    base_alto = 0.08
                    base_medio = 0.05
                elif timeframe == '5m':
                    base_alto = 0.15
                    base_medio = 0.10
                elif timeframe == '15m':
                    base_alto = 0.35
                    base_medio = 0.20
                else:  # 30m
                    base_alto = 0.50
                    base_medio = 0.30
                
                # Aplicar multiplicador específico do ativo
                range_alto = atr_pct_calc > (base_alto * vol_multiplier)
                range_medio = atr_pct_calc > (base_medio * vol_multiplier)
                
                # Classificação combinada
                if range_alto or volatilidade > 2.0:
                    estado = "🔥 IMPULSO"
                elif adx > 30 or (adx > 20 and range_medio):
                    estado = "📈 TENDÊNCIA"
                elif adx > 15 or range_medio:
                    estado = "🔄 MOVIMENTO"
                else:
                    estado = "📊 LATERAL"
                
                # S/R ADAPTATIVOS POR TIMEFRAME - níveis relevantes para cada período
                try:
                    # Indicadores base
                    bb_upper = ind.get('BB_upper', ind.get('bb_upper', 0))
                    bb_lower = ind.get('BB_lower', ind.get('bb_lower', 0))
                    ema8 = ind.get('EMA8', ind.get('ema8', 0))
                    ema21 = ind.get('EMA21', ind.get('ema21', 0))
                    ema50 = ind.get('EMA50', ind.get('ema50', 0))
                    sma200 = ind.get('SMA200', ind.get('sma200', 0))
                    
                    # ESTRATÉGIA DE S/R POR TIMEFRAME (4 ondas)
                    if timeframe == '1m':
                        # SCALP: BB e EMAs curtas (níveis imediatos)
                        r_candidates = [bb_upper, ema8]
                        s_candidates = [bb_lower, ema8]
                        fallback_pct = 0.003  # 0.3% (scalp)
                        
                    elif timeframe == '5m':
                        # SCALP: BB, EMA8 e EMA21 (níveis curto prazo)
                        r_candidates = [bb_upper, ema21, ema8]
                        s_candidates = [bb_lower, ema21, ema8]
                        fallback_pct = 0.005  # 0.5%
                        
                    elif timeframe == '15m':
                        # DAY: EMA50, EMA21 e Zonas (níveis estruturais)
                        r_candidates = [ema50, ema21, bb_upper]
                        s_candidates = [ema50, ema21, bb_lower]
                        fallback_pct = 0.012  # 1.2%
                        
                    else:  # 30m
                        # INTRA: EMA50, SMA200 (níveis macro)
                        r_candidates = [ema50, sma200, ema21]
                        s_candidates = [ema50, sma200, ema21]
                        fallback_pct = 0.020  # 2.0%
                    
                    # Encontrar RESISTÊNCIA mais próxima ACIMA do preço
                    r_prox = None
                    for candidate in r_candidates:
                        if candidate and candidate > preco:
                            if r_prox is None or candidate < r_prox:
                                r_prox = candidate
                    
                    # Encontrar SUPORTE mais próximo ABAIXO do preço
                    s_prox = None
                    for candidate in s_candidates:
                        if candidate and candidate < preco:
                            if s_prox is None or candidate > s_prox:
                                s_prox = candidate
                    
                    # Fallback adaptativo por timeframe
                    if not r_prox:
                        r_prox = preco * (1 + fallback_pct)
                    if not s_prox:
                        s_prox = preco * (1 - fallback_pct)
                    
                    # Formatar strings
                    if r_prox and s_prox:
                        dist_r = ((r_prox - preco) / preco) * 100
                        dist_s = ((preco - s_prox) / preco) * 100
                        r_str = f"${r_prox:,.0f} (+{dist_r:.1f}%)"
                        s_str = f"${s_prox:,.0f} (-{dist_s:.1f}%)"
                    else:
                        r_str = "Consolidado"
                        s_str = "Consolidado"
                        
                except Exception as e:
                    r_str = "N/A"
                    s_str = "N/A"
                
                # RANGE DO MOVIMENTO - usar BB width ou calcular aproximado
                # ATR pode estar em diferentes formatos
                atr = ind.get('ATR') or ind.get('atr') or 0
                
                # Se ATR for 0, calcular baseado em Bollinger Bands
                if not atr or atr == 0:
                    bb_upper = ind.get('BB_upper', ind.get('bb_upper', 0))
                    bb_lower = ind.get('BB_lower', ind.get('bb_lower', 0))
                    
                    if bb_upper and bb_lower:
                        # BB width como proxy para volatilidade
                        atr = (bb_upper - bb_lower) / 2
                    else:
                        # Usar volatilidade do contexto ou 1.5% padrão
                        vol = contexto.get('volatilidade', 1.5)
                        atr = preco * (vol / 100)
                
                atr_pct = (atr / preco * 100) if preco > 0 and atr > 0 else 0
                
                if atr > 0:
                    range_str = f"${atr:,.0f} ({atr_pct:.2f}%)"
                else:
                    range_str = "N/A"
                
                # FORÇA DO MOVIMENTO - Cálculo composto (RSI + ADX + Volume + Momentum)
                rsi = ind.get('RSI', 50)
                adx_forca = ind.get('ADX', 0)
                macd = ind.get('MACD', 0)
                macd_signal = ind.get('MACD_signal', 0)
                volume_ratio = contexto.get('volume_ratio', 1.0)  # Volume atual vs média
                
                # 1. DIREÇÃO (Alta/Baixa) baseada em múltiplos fatores
                direcao_score = 0
                
                # RSI contribution (peso maior para RSI)
                if rsi > 50:
                    direcao_score += (rsi - 50) / 25  # 0 a 2 para alta (mais sensível)
                else:
                    direcao_score -= (50 - rsi) / 25  # 0 a -2 para baixa (mais sensível)
                
                # MACD contribution (peso maior para momentum)
                if macd > macd_signal:
                    direcao_score += 0.5  # Momentum de alta (aumentado)
                else:
                    direcao_score -= 0.5  # Momentum de baixa (aumentado)
                
                # Tendência contribution (peso maior para tendência)
                if tendencia == 'ALTA':
                    direcao_score += 0.8  # Tendência de alta (aumentado)
                elif tendencia == 'BAIXA':
                    direcao_score -= 0.8  # Tendência de baixa (aumentado)
                
                # Preço vs Médias (contribuição adicional)
                ema8 = ind.get('EMA8', preco)
                ema21 = ind.get('EMA21', preco)
                
                if preco > ema8 and ema8 > ema21:
                    direcao_score += 0.3  # Alinhamento bullish
                elif preco < ema8 and ema8 < ema21:
                    direcao_score -= 0.3  # Alinhamento bearish
                
                # 2. INTENSIDADE (Fraco/Forte) baseada em ADX + Volume
                intensidade = 0
                
                # ADX contribution (força da tendência)
                if adx_forca > 40:
                    intensidade += 2  # Muito forte
                elif adx_forca > 25:
                    intensidade += 1  # Forte
                elif adx_forca > 15:
                    intensidade += 0.5  # Moderado
                
                # Volume contribution
                if volume_ratio > 1.5:
                    intensidade += 1  # Volume alto
                elif volume_ratio > 1.2:
                    intensidade += 0.5  # Volume acima da média
                
                # ATR contribution (volatilidade = movimento)
                if atr_pct_calc > base_alto * vol_multiplier:
                    intensidade += 1  # Range alto
                elif atr_pct_calc > base_medio * vol_multiplier:
                    intensidade += 0.5  # Range médio
                
                # 3. CLASSIFICAR FORÇA + DIREÇÃO (thresholds ajustados)
                # Extremos primeiro (sobrecompra/sobrevenda)
                if rsi > 70 and direcao_score > 0.3:
                    forca = "🔴 SOBRECOMPRA ↑"
                elif rsi < 30 and direcao_score < -0.3:
                    forca = "🔴 SOBREVENDA ↓"
                
                # Alta (threshold reduzido para ser mais sensível)
                elif direcao_score > 0.3:
                    if intensidade >= 2:
                        forca = "🔥 ALTA FORTE ↑"
                    elif intensidade >= 1:
                        forca = "🟠 ALTA MODERADA ↑"
                    else:
                        forca = "🟡 ALTA FRACA ↑"
                
                # Baixa (threshold reduzido para ser mais sensível)
                elif direcao_score < -0.3:
                    if intensidade >= 2:
                        forca = "🔵 BAIXA FORTE ↓"
                    elif intensidade >= 1:
                        forca = "🟣 BAIXA MODERADA ↓"
                    else:
                        forca = "⚪ BAIXA FRACA ↓"
                
                # Neutro/Lateral (range mais estreito)
                else:
                    if intensidade >= 1.5:
                        forca = "⚡ VOLATILIDADE ↔"
                    else:
                        forca = "⭐ NEUTRO ↔"
                
                # Emoji por score
                if score >= 7.5:
                    emoji = "🟢"
                elif score >= 6.5:
                    emoji = "🟡"
                else:
                    emoji = "🔴"
                
                par_nome = par.replace('USDT', '')
                
                try:
                    score_str = f"{float(score):.1f}/10"
                except (ValueError, TypeError):
                    score_str = "N/A"
                
                # Limitar tamanho das strings para caber nas colunas
                r_str_trunc = r_str[:16] if len(r_str) > 16 else r_str
                s_str_trunc = s_str[:16] if len(s_str) > 16 else s_str
                
                print(f"{emoji} {par_nome:<4} ${preco:<12,.2f} {estado:<15} {r_str_trunc:<18} {s_str_trunc:<18} {range_str:<15} {forca:<16} {score_str:<6}")
                
                # Armazenar dados se solicitado
                if retornar_dados:
                    dados_retorno[par] = {
                        'preco': preco,
                        'estado': estado,
                        'resistencia': r_str,
                        'suporte': s_str,
                        'range': range_str,
                        'forca': forca,
                        'score': score,
                        'emoji': emoji
                    }
                
        except Exception as e:
            par_nome = par.replace('USDT', '')
            print(f"❌ {par_nome:<6} Erro na análise: {str(e)[:40]}")
    
    print("\n" + "="*120)
    
    # Legenda - SISTEMA DE ONDAS (4 ondas)
    print("🌊 ONDAS: 1️⃣ 1m (BB/EMA8) | 2️⃣ 5m (BB/EMA21) | 3️⃣ 15m (EMA50/21) | 4️⃣ 30m (EMA50/SMA200)")
    print("📊 ESTADO: 🔥 Impulso (Range Alto) | 📈 Tendência (ADX>30) | 🔄 Movimento (Range Médio) | 📊 Lateral")
    print("⚡ FORÇA + DIREÇÃO: ↑ Alta | ↓ Baixa | ↔ Neutro/Volatilidade | 🔥🟠🟡 (Forte/Mod/Fraca) | 🔴 Extremos")
    print("🎯 S/R ADAPTATIVO: Níveis por TF | Range: ATR calibrado | Força: RSI+ADX+Vol+MACD")
    
    # Retornar dados se solicitado
    if retornar_dados:
        return dados_retorno
    return None


def enviar_relatorio_telegram(dados_ciclo, ciclo_num, pares, graficos=None):
    """Envia relatório detalhado do ciclo completo ao Telegram com gráficos"""
    
    try:
        from xenos_bot import enviar_oraculo, enviar_foto
        from datetime import datetime
        
        hora_relatorio = datetime.now().strftime("%H:%M:%S")
        data_relatorio = datetime.now().strftime("%d/%m/%Y")
        
        # Cabeçalho do relatório
        msg = f"""🌊 <b>RELATÓRIO DASHBOARD - CICLO #{ciclo_num}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ {hora_relatorio} | 📅 {data_relatorio}

"""
        
        # Analisar cada par
        for par in pares:
            par_nome = par.replace('USDT', '')
            msg += f"\n<b>{par_nome}</b> 📊\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Dados de cada timeframe
            ondas_info = []
            for tf in ['1m', '5m', '15m', '30m']:
                if tf in dados_ciclo and par in dados_ciclo[tf]:
                    dados = dados_ciclo[tf][par]
                    
                    # Emoji da onda
                    onda_emoji = {'1m': '1️⃣', '5m': '2️⃣', '15m': '3️⃣', '30m': '4️⃣'}[tf]
                    
                    # Determinar tipo de estratégia
                    tipo_estrategia = {'1m': 'SCALP', '5m': 'SCALP', '15m': 'DAY', '30m': 'INTRA'}[tf]
                    
                    ondas_info.append({
                        'tf': tf,
                        'emoji': onda_emoji,
                        'tipo': tipo_estrategia,
                        'dados': dados
                    })
            
            # Exibir ondas
            for info in ondas_info:
                tf = info['tf']
                emoji_onda = info['emoji']
                tipo = info['tipo']
                d = info['dados']
                
                msg += f"{emoji_onda} <b>{tf.upper()}</b> ({tipo})\n"
                msg += f"   💰 Preço: ${d['preco']:,.2f}\n"
                msg += f"   📊 Estado: {d['estado']}\n"
                msg += f"   ⚡ Força: {d['forca']}\n"
                msg += f"   🎯 Score: {float(d['score']):.1f}/10\n"
                msg += f"   🔴 Resistência: {d['resistencia']}\n"
                msg += f"   🟢 Suporte: {d['suporte']}\n"
                msg += f"   📏 Range: {d['range']}\n\n"
            
            # Análise de confluência melhorada (considerar força e direção)
            direcoes = []
            scores_forca = []
            
            for info in ondas_info:
                dados_tf = info['dados']
                forca = dados_tf['forca']
                score_tf = float(dados_tf['score'])
                
                # Determinar direção com peso baseado no score
                if '↑' in forca:
                    direcoes.append('ALTA')
                    scores_forca.append(score_tf if '↑' in forca else 0)
                elif '↓' in forca:
                    direcoes.append('BAIXA')
                    scores_forca.append(score_tf if '↓' in forca else 0)
                else:
                    direcoes.append('NEUTRO')
                    scores_forca.append(score_tf * 0.5)  # Neutro tem peso menor
            
            # Contar confluência com pesos
            alta_count = direcoes.count('ALTA')
            baixa_count = direcoes.count('BAIXA')
            neutro_count = direcoes.count('NEUTRO')
            
            # Calcular score médio por direção
            score_alta = sum(scores_forca[i] for i, d in enumerate(direcoes) if d == 'ALTA') / max(alta_count, 1)
            score_baixa = sum(scores_forca[i] for i, d in enumerate(direcoes) if d == 'BAIXA') / max(baixa_count, 1)
            score_neutro = sum(scores_forca[i] for i, d in enumerate(direcoes) if d == 'NEUTRO') / max(neutro_count, 1)
            
            msg += "<b>💡 CONFLUÊNCIA MULTI-TF:</b>\n"
            
            # Lógica melhorada de confluência
            if alta_count >= 3 and score_alta >= 6.0:
                msg += f"   ✅ <b>ALTA CONFIRMADA</b> ({alta_count}/4 ondas ↑ | Score: {score_alta:.1f})\n"
                msg += "   🎯 <b>Ação:</b> Buscar entradas LONG em pullbacks\n"
            elif baixa_count >= 3 and score_baixa >= 6.0:
                msg += f"   ✅ <b>BAIXA CONFIRMADA</b> ({baixa_count}/4 ondas ↓ | Score: {score_baixa:.1f})\n"
                msg += "   🎯 <b>Ação:</b> Buscar entradas SHORT em rejeições\n"
            elif alta_count == baixa_count and alta_count >= 2:
                msg += f"   ⚠️ <b>DIVERGÊNCIA</b> (Alta:{alta_count} | Baixa:{baixa_count})\n"
                msg += "   🎯 <b>Ação:</b> AGUARDAR definição clara\n"
            elif alta_count > baixa_count:
                # Verificar força da tendência alta
                if score_alta >= 7.0:
                    msg += f"   🔥 <b>ALTA FORTE</b> ({alta_count}/4 ondas ↑ | Score: {score_alta:.1f})\n"
                    msg += "   🎯 <b>Ação:</b> Buscar entradas LONG\n"
                else:
                    msg += f"   📊 <b>ALTA MODERADA</b> ({alta_count}/4 ondas ↑ | Score: {score_alta:.1f})\n"
                    msg += "   🎯 <b>Ação:</b> Operar com cautela, confirmar em TFs maiores\n"
            elif baixa_count > alta_count:
                # Verificar força da tendência baixa
                if score_baixa >= 7.0:
                    msg += f"   🔥 <b>BAIXA FORTE</b> ({baixa_count}/4 ondas ↓ | Score: {score_baixa:.1f})\n"
                    msg += "   🎯 <b>Ação:</b> Buscar entradas SHORT\n"
                else:
                    msg += f"   📊 <b>BAIXA MODERADA</b> ({baixa_count}/4 ondas ↓ | Score: {score_baixa:.1f})\n"
                    msg += "   🎯 <b>Ação:</b> Operar com cautela, confirmar em TFs maiores\n"
            else:
                msg += f"   ⚪ <b>INDEFINIDO</b> (Neutro:{neutro_count} | Score: {score_neutro:.1f})\n"
                msg += "   🎯 <b>Ação:</b> AGUARDAR definição clara\n"
            
            msg += "\n"
        
        # Rodapé
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "⏰ <b>Próximo relatório:</b> Após 4 ondas (~1 min)\n"
        
        # Indicar quando será o próximo envio de gráficos unificados
        if graficos:
            msg += "📊 <b>Gráficos Unificados:</b> Inclusos neste relatório\n"
            msg += "📈 <b>Próximos gráficos:</b> Em ~5 minutos"
        else:
            # Calcular quantos ciclos faltam para o próximo envio
            if ciclo_num == 1:
                # Já enviou no primeiro, próximo em 5 min
                proximo_grafico = 5
            else:
                # Calcular até o próximo múltiplo de 5 + 1 (6, 11, 16...)
                proximo_ciclo = ((ciclo_num // 5) + 1) * 5 + 1
                proximo_grafico = proximo_ciclo - ciclo_num
            msg += f"📊 <b>Próximos gráficos unificados:</b> Em ~{proximo_grafico} min"
        
        msg += "\n🌊 <b>Sistema de Ondas:</b> 1m → 5m → 15m → 30m"
        
        # Enviar texto ao Telegram
        enviar_oraculo(msg)
        print(f"✅ Relatório texto Ciclo #{ciclo_num} enviado")
        
        # Enviar gráficos unificados ao Telegram (apenas se houver)
        if graficos:
            print(f"\n📸 Enviando {len(graficos)} gráficos unificados ao Telegram...")
            for idx, grafico_path in enumerate(graficos, 1):
                try:
                    enviar_foto(grafico_path)
                    print(f"   ✅ Gráfico {idx}/{len(graficos)} enviado")
                except Exception as e:
                    print(f"   ❌ Erro ao enviar gráfico {idx}: {e}")
            
            print(f"✅ Relatório completo Ciclo #{ciclo_num} enviado (texto + {len(graficos)} gráficos unificados)")
        else:
            # Calcular até o próximo envio
            if ciclo_num == 1:
                proximo = 5
            else:
                proximo_ciclo = ((ciclo_num // 5) + 1) * 5 + 1
                proximo = proximo_ciclo - ciclo_num
            print(f"ℹ️  Próximos gráficos unificados em {proximo} ciclos (~{proximo} min)")
        
    except Exception as e:
        print(f"❌ Erro ao enviar relatório: {e}")


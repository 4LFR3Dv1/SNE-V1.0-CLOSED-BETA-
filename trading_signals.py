#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Sinais de Trading - Simples e Direto
Complementa o sistema existente sem substituir
"""

import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import requests

def buscar_dados_rapido(symbol: str, interval: str = "1m", limit: int = 100):
    """Busca dados da Binance de forma rápida"""
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        return df
    except Exception as e:
        print(f"❌ Erro ao buscar {symbol}: {e}")
        return None

def analisar_oportunidade_real(symbol: str, df: pd.DataFrame):
    """
    Analisa e retorna oportunidade REAL ou None
    Critérios práticos e diretos
    """
    
    if df is None or len(df) < 20:
        return None
    
    try:
        # Dados básicos
        preco_atual = df['close'].iloc[-1]
        sma20 = df['close'].rolling(20).mean().iloc[-1]
        volume_atual = df['volume'].iloc[-1]
        volume_medio = df['volume'].rolling(20).mean().iloc[-1]
        
        # Suporte e Resistência (últimas 20 velas)
        suporte = df['low'].rolling(20).min().iloc[-1]
        resistencia = df['high'].rolling(20).max().iloc[-1]
        
        # Momentum (últimas 5 velas)
        if len(df) >= 6:
            momentum = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100
        else:
            momentum = 0
        
        # Volatilidade (últimas 20 velas)
        volatilidade = df['close'].pct_change().tail(20).std() * 100
        
        # === SISTEMA DE SCORE PRÁTICO ===
        score = 0
        razoes = []
        
        # 1. MOMENTUM FORTE (40 pontos)
        if abs(momentum) > 0.5:  # Movimento de pelo menos 0.5%
            score += 40
            direcao = "alta" if momentum > 0 else "queda"
            razoes.append(f"📈 Preço em {direcao} ({momentum:+.2f}% em 5 velas)")
        
        # 2. VOLUME SIGNIFICATIVO (30 pontos)
        if volume_medio > 0:
            volume_ratio = volume_atual / volume_medio
            if volume_ratio > 1.3:  # 30% acima da média
                score += 30
                razoes.append(f"📊 Volume {(volume_ratio-1)*100:.0f}% acima da média")
            elif volume_ratio > 1.0:
                score += 15
                razoes.append(f"📊 Volume ligeiramente acima da média")
        
        # 3. VOLATILIDADE ADEQUADA (30 pontos)
        if 0.3 < volatilidade < 3:  # Volatilidade ideal para trading
            score += 30
            razoes.append(f"⚡ Volatilidade ideal para trading ({volatilidade:.2f}%)")
        elif volatilidade >= 3:
            score += 15
            razoes.append(f"⚡ Alta volatilidade ({volatilidade:.2f}%)")
        
        # Só retornar se score >= 60 (reduzido de 70 para ter mais oportunidades)
        if score < 60:
            return None
        
        # === DETERMINAR AÇÃO ===
        if momentum > 0:
            acao = "COMPRAR"
            emoji = "🟢"
            tipo = "LONG"
            # Níveis para compra
            entrada = preco_atual
            alvo = resistencia
            stop = suporte * 0.995  # Stop 0.5% abaixo do suporte
        else:
            acao = "VENDER"
            emoji = "🔴"
            tipo = "SHORT"
            # Níveis para venda
            entrada = preco_atual
            alvo = suporte
            stop = resistencia * 1.005  # Stop 0.5% acima da resistência
        
        # Calcular retorno e risco
        retorno_pct = abs((alvo - entrada) / entrada * 100)
        risco_pct = abs((stop - entrada) / entrada * 100)
        risco_retorno = retorno_pct / risco_pct if risco_pct > 0 else 0
        
        # Validar risco/retorno mínimo
        if risco_retorno < 1.5:  # Risco/retorno deve ser pelo menos 1.5:1
            return None
        
        return {
            'symbol': symbol,
            'score': score,
            'acao': acao,
            'tipo': tipo,
            'emoji': emoji,
            'preco_atual': preco_atual,
            'entrada': entrada,
            'alvo': alvo,
            'stop': stop,
            'retorno_pct': retorno_pct,
            'risco_pct': risco_pct,
            'risco_retorno': risco_retorno,
            'suporte': suporte,
            'resistencia': resistencia,
            'momentum': momentum,
            'volatilidade': volatilidade,
            'volume_ratio': volume_atual / volume_medio if volume_medio > 0 else 1,
            'razoes': razoes,
            'timestamp': datetime.now(pytz.timezone("America/Sao_Paulo"))
        }
    
    except Exception as e:
        print(f"❌ Erro ao analisar {symbol}: {e}")
        return None

def encontrar_melhor_oportunidade(pares: list = None):
    """
    Analisa todos os pares e retorna a MELHOR oportunidade
    """
    
    if pares is None:
        pares = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOTUSDT", 
                 "AVAXUSDT", "MATICUSDT", "LINKUSDT", "UNIUSDT", "ATOMUSDT",
                 "NEARUSDT", "FTMUSDT"]
    
    oportunidades = []
    
    print(f"🔍 Analisando {len(pares)} pares...")
    
    for symbol in pares:
        df = buscar_dados_rapido(symbol)
        if df is not None:
            oportunidade = analisar_oportunidade_real(symbol, df)
            if oportunidade:
                oportunidades.append(oportunidade)
                print(f"✅ {symbol} - Score: {oportunidade['score']}")
    
    if not oportunidades:
        return None
    
    # Ordenar por score e risco/retorno
    oportunidades.sort(key=lambda x: (x['score'], x['risco_retorno']), reverse=True)
    
    return oportunidades

def exibir_oportunidade(oportunidade):
    """
    Exibe oportunidade de forma clara e acionável
    """
    
    if not oportunidade:
        print("\n" + "="*60)
        print("⏸️ NENHUMA OPORTUNIDADE NO MOMENTO")
        print("="*60)
        print("\n💡 Critérios para oportunidade:")
        print("   • Score ≥ 60/100")
        print("   • Momentum > 0.5%")
        print("   • Volume acima da média")
        print("   • Risco/Retorno ≥ 1.5:1")
        print("\n⏰ Aguarde por um setup adequado")
        print("="*60)
        return
    
    print(f"\n{'='*60}")
    print(f"🎯 MELHOR OPORTUNIDADE: {oportunidade['symbol']}")
    print(f"{'='*60}")
    
    print(f"\n{oportunidade['emoji']} AÇÃO: {oportunidade['acao']} ({oportunidade['tipo']})")
    print(f"💰 Preço Atual: ${oportunidade['preco_atual']:.4f}")
    print(f"📍 Entrada: ${oportunidade['entrada']:.4f}")
    print(f"🎯 Alvo (Take Profit): ${oportunidade['alvo']:.4f} ({oportunidade['retorno_pct']:+.2f}%)")
    print(f"🛡️ Stop Loss: ${oportunidade['stop']:.4f} ({-oportunidade['risco_pct']:.2f}%)")
    print(f"⚖️ Risco/Retorno: 1:{oportunidade['risco_retorno']:.1f}")
    
    print(f"\n📊 ANÁLISE TÉCNICA:")
    print(f"   • Suporte: ${oportunidade['suporte']:.4f}")
    print(f"   • Resistência: ${oportunidade['resistencia']:.4f}")
    print(f"   • Momentum: {oportunidade['momentum']:+.2f}%")
    print(f"   • Volatilidade: {oportunidade['volatilidade']:.2f}%")
    print(f"   • Volume Ratio: {oportunidade['volume_ratio']:.2f}x")
    
    print(f"\n✅ RAZÕES (Score: {oportunidade['score']}/100):")
    for razao in oportunidade['razoes']:
        print(f"   • {razao}")
    
    timestamp = oportunidade['timestamp'].strftime('%H:%M:%S')
    print(f"\n⏰ Análise gerada em: {timestamp}")
    print(f"⏱️ Válido por: 15-30 minutos")
    print(f"{'='*60}")

def exibir_top_oportunidades(oportunidades: list, top: int = 3):
    """
    Exibe top N oportunidades de forma resumida
    """
    
    if not oportunidades:
        print("\n⏸️ Nenhuma oportunidade no momento")
        return
    
    print(f"\n{'='*60}")
    print(f"🏆 TOP {min(top, len(oportunidades))} OPORTUNIDADES")
    print(f"{'='*60}")
    
    for i, opp in enumerate(oportunidades[:top], 1):
        print(f"\n{i}. {opp['emoji']} {opp['symbol']} - {opp['acao']}")
        print(f"   Score: {opp['score']}/100 | R/R: 1:{opp['risco_retorno']:.1f}")
        print(f"   Entrada: ${opp['entrada']:.4f} → Alvo: ${opp['alvo']:.4f} ({opp['retorno_pct']:+.2f}%)")
        print(f"   Razão: {opp['razoes'][0] if opp['razoes'] else 'N/A'}")
    
    print(f"\n{'='*60}")

def gerar_mensagem_telegram(oportunidade):
    """
    Gera mensagem formatada para Telegram
    """
    
    if not oportunidade:
        return None
    
    mensagem = f"""🎯 <b>OPORTUNIDADE DETECTADA</b>

{oportunidade['emoji']} <b>{oportunidade['symbol']}</b> - {oportunidade['acao']}

💰 <b>Entrada:</b> ${oportunidade['entrada']:.4f}
🎯 <b>Alvo:</b> ${oportunidade['alvo']:.4f} ({oportunidade['retorno_pct']:+.2f}%)
🛡️ <b>Stop:</b> ${oportunidade['stop']:.4f} ({-oportunidade['risco_pct']:.2f}%)
⚖️ <b>R/R:</b> 1:{oportunidade['risco_retorno']:.1f}

📊 <b>Score:</b> {oportunidade['score']}/100

✅ <b>Razões:</b>
"""
    
    for razao in oportunidade['razoes']:
        mensagem += f"• {razao}\n"
    
    timestamp = oportunidade['timestamp'].strftime('%H:%M:%S')
    mensagem += f"\n⏰ {timestamp}"
    
    return mensagem






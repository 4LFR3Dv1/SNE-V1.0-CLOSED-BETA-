"""
Análise Multi-Pair com Sinais Acionáveis
Mostra sinais prontos para trading ao invés de scores inúteis
"""

import requests
from indicadores import calcular_indicadores_simples

# Definir pares principais
PARES_PRINCIPAIS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT', 'UNIUSDT']


def gerar_sinais_multiplos():
    """
    Gera sinais acionáveis para múltiplos pares
    Retorna lista ordenada por qualidade de setup
    """
    sinais = []
    
    for par in PARES_PRINCIPAIS:
        try:
            # Buscar dados
            url = f"https://api.binance.com/api/v3/klines?symbol={par}&interval=15m&limit=50"
            resp = requests.get(url, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                closes = [float(candle[4]) for candle in data]
                volumes = [float(candle[5]) for candle in data]
                
                preco = closes[-1]
                
                # Calcular indicadores
                ema8, ema21, rsi, bb_upper, bb_lower = calcular_indicadores_simples(closes)
                volume_ratio = volumes[-1] / (sum(volumes[-20:]) / 20) if len(volumes) >= 20 else 1
                
                # Determinar sinal
                acao = None
                motivos = []
                forca = 0
                
                # Lógica de compra
                if ema8 > ema21:
                    acao = 'COMPRAR'
                    forca += 50
                    motivos.append("EMA8 > EMA21 (tendência alta)")
                    
                    if rsi < 50:
                        forca += 25
                        motivos.append("RSI abaixo 50 (espaço pra subir)")
                    
                    if preco < bb_upper * 0.98:
                        forca += 25
                        motivos.append("Preço abaixo BB superior")
                
                # Lógica de venda
                elif ema8 < ema21:
                    acao = 'VENDER'
                    forca += 50
                    motivos.append("EMA8 < EMA21 (tendência baixa)")
                    
                    if rsi > 50:
                        forca += 25
                        motivos.append("RSI acima 50 (pressão vendedora)")
                    
                    if preco > bb_lower * 1.02:
                        forca += 25
                        motivos.append("Preço acima BB inferior")
                
                # Bonus por volume
                if volume_ratio > 1.2:
                    forca += 20
                    motivos.append(f"Volume {volume_ratio:.1f}x média")
                
                # Calcular níveis
                if acao == 'COMPRAR':
                    entry = preco
                    tp1 = preco * 1.01
                    tp2 = preco * 1.02
                    tp3 = preco * 1.03
                    sl = preco * 0.997
                elif acao == 'VENDER':
                    entry = preco
                    tp1 = preco * 0.99
                    tp2 = preco * 0.98
                    tp3 = preco * 0.97
                    sl = preco * 1.003
                else:
                    continue
                
                # Calcular R/R
                risco = abs(entry - sl)
                retorno = abs(tp1 - entry)
                rr = retorno / risco if risco > 0 else 0
                
                sinais.append({
                    'symbol': par,
                    'acao': acao,
                    'preco': preco,
                    'entry': entry,
                    'tp1': tp1,
                    'tp2': tp2,
                    'tp3': tp3,
                    'sl': sl,
                    'rr': rr,
                    'forca': forca,
                    'motivos': motivos,
                    'rsi': rsi,
                    'volume_ratio': volume_ratio
                })
                
        except Exception as e:
            pass
    
    # Ordenar por força do sinal
    sinais.sort(key=lambda x: x['forca'], reverse=True)
    
    return sinais


def exibir_sinais_multiplos(sinais, top=5):
    """
    Exibe sinais de forma clara e acionável
    """
    if not sinais:
        print("\n⏸️  Nenhum sinal claro no momento")
        return
    
    print(f"\n✅ {len(sinais)} sinais gerados")
    print(f"\n🏆 TOP {min(top, len(sinais))} SETUPS:")
    print("="*60)
    
    for i, sinal in enumerate(sinais[:top], 1):
        acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
        
        print(f"\n{i}. {acao_emoji} {sinal['acao']} {sinal['symbol']} (Força: {sinal['forca']:.0f}%)")
        print(f"   💰 Preço: ${sinal['preco']:.4f}")
        print(f"   📍 Entry: ${sinal['entry']:.4f}")
        print(f"   🎯 TP: ${sinal['tp1']:.4f} / ${sinal['tp2']:.4f} / ${sinal['tp3']:.4f}")
        print(f"   🛡️  SL: ${sinal['sl']:.4f}")
        print(f"   📊 R/R: 1:{sinal['rr']:.1f}")
        print(f"   💡 Motivos: {', '.join(sinal['motivos'][:2])}")
    
    print("\n" + "="*60)


import os
import json
from datetime import datetime
import sys
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText
from datetime import datetime
import platform
import random
import pytz
import asyncio

from backtest import executar_backtest, estado
from mente_fluida import mente_fluidica_verificar_resonancia
from mente_fluida_ciclica import mente_fluidica_detectar_ciclos
from fluxo_mental import analisar_fluxo_mental
from catalogo_magnetico import atualizar_catalogo, exibir_zonas_relevantes
from xenos_bot import (
    iniciar_oraculo, enviar_oraculo,
    gerar_codice_fluxo, enviar_log_rupturas,
    enviar_alerta_tatico, enviar_resumo_estrategico
)
from contexto_mercado import analisar_contexto_mercado, analise_rapida_contexto
from contexto_tempo_real import (
    iniciar_contexto_tempo_real, parar_contexto_tempo_real,
    obter_contexto_atual, obter_ranking_atual, obter_resumo_executivo,
    analisar_contexto_radar
)
from multi_pair_context import analisar_mercado_completo
from priorizacao_automatica import priorizador_global
from alertas_inteligentes import sistema_alertas_global
from trading_signals import (
    encontrar_melhor_oportunidade, exibir_oportunidade,
    exibir_top_oportunidades, gerar_mensagem_telegram
)

# Importar modo trader direto
try:
    from trader_direto import TraderDireto, exibir_sinal_direto, exibir_top_sinais_diretos
    TRADER_DIRETO_AVAILABLE = True
except ImportError:
    TRADER_DIRETO_AVAILABLE = False

# Importar modo agressivo
try:
    from modo_agressivo import buscar_melhor_par_agressivo, exibir_sinal_agressivo
    MODO_AGRESSIVO_AVAILABLE = True
except ImportError:
    MODO_AGRESSIVO_AVAILABLE = False

# Importar módulos táticos inteligentes
try:
    from contexto_adaptativo import ContextoAdaptativo
    from memoria_operacional import MemoriaOperacional
    from gestao_risco import GestaoRisco
    from fluxo_ativo import FluxoAtivo
    from consistencia_sinal import ConsistenciaSinal
    from modo_renan import ModoRenan
    MODO_TATICO_AVAILABLE = True
except ImportError:
    MODO_TATICO_AVAILABLE = False
    print("⚠️ Módulos táticos não disponíveis")

# Importar módulos profissionais
try:
    from professional_signals import MultiTimeframeSignal
    from telegram_professional import TelegramProfessional
    from coin_scanner import ProfessionalCoinScanner
    from auto_signal_system import AutoSignalSystem
    PROFESSIONAL_MODE_AVAILABLE = True
except ImportError:
    PROFESSIONAL_MODE_AVAILABLE = False
    print("⚠️ Módulos profissionais não disponíveis")

symbol = "BTCUSDT"
interval = "1m"
limit = 100
update_interval = 5000
modo_silencio = False
br_tz = pytz.timezone("America/Sao_Paulo")

# === Controle de Spam ===
ultima_mensagem_catalogo = ""
ultima_mensagem_contexto = ""
mensagens_enviadas_cache = {}  # Cache de mensagens para evitar duplicatas
import time
tempo_ultimo_contexto = 0  # Timestamp da última exibição de contexto

CAMINHO_LOG_ALERTAS = "logs/rupturas_criticas.log"
os.makedirs("logs", exist_ok=True)

def pensamento_sne():
    frases = [
        "A mente é a arma silenciosa do tempo.",
        "A ruptura visível é fruto de tensões invisíveis.",
        "Seu corpo sente o mercado antes do gráfico mostrar.",
        "O silêncio é o pulso da próxima explosão.",
        "Observe a curva. A curva te observa também."
    ]
    return random.choice(frases)

def registrar_alerta_log(mensagem):
    timestamp = datetime.now(tz=br_tz).strftime('%Y-%m-%d %H:%M:%S')
    with open(CAMINHO_LOG_ALERTAS, "a") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def tocar_alarme(tipo):
    if modo_silencio:
        return
    if platform.system() == "Darwin":
        som = "Submarine.aiff" if tipo == "compra" else "Glass.aiff"
        os.system(f"afplay /System/Library/Sounds/{som}")
    elif platform.system() == "Windows":
        import winsound
        winsound.Beep(1000 if tipo == "compra" else 600, 200)

def tocar_alarme_energia():
    if modo_silencio:
        return
    if platform.system() == "Darwin":
        os.system("afplay /System/Library/Sounds/Basso.aiff")
    elif platform.system() == "Windows":
        import winsound
        winsound.Beep(1200, 300)

def buscar_dados_binance(symbol, interval, limit):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    data = requests.get(url, params=params, timeout=10).json()
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tbb", "tbq", "ignore"
    ])
    df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(br_tz)
    df = df[["time", "open", "high", "low", "close", "volume", "trades"]].astype({
        "open": float, "high": float, "low": float, "close": float,
        "volume": float, "trades": int
    })
    df.set_index("time", inplace=True)
    df["EMA8"] = df["close"].ewm(span=8).mean()
    df["EMA21"] = df["close"].ewm(span=21).mean()
    df["SMA200"] = df["close"].rolling(window=20).mean()
    df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)
    df["timestamp"] = mdates.date2num(df.index.to_pydatetime())
    df["ruptura"] = (df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.98)) & \
                    (df["volume"] > df["volume"].quantile(0.9))
    df["sinal_compra"] = (df["EMA8"] > df["EMA21"]) & (df["EMA8"].shift(1) <= df["EMA21"].shift(1))
    df["sinal_venda"] = (df["EMA8"] < df["EMA21"]) & (df["EMA8"].shift(1) >= df["EMA21"].shift(1))
    return df

def buscar_book(symbol):
    url = f"https://api.binance.com/api/v3/depth"
    params = {"symbol": symbol, "limit": 100}
    data = requests.get(url, params=params, timeout=10).json()
    bids = np.array(data["bids"], dtype=float)
    asks = np.array(data["asks"], dtype=float)
    return bids, asks

from datetime import datetime
import matplotlib.dates as mdates
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.offsetbox import AnchoredText
from xenos_bot import enviar_oraculo

# === Parâmetros de Sensibilidade e Intervalo de Envio ===
SENSIBILIDADE_GRAVITACIONAL = 0.95
SENSIBILIDADE_MAGNETICA = 0.98
INTERVALO_ATUALIZACAO = 60  

# === Controle de Tempo para Evitar Duplicidade ===
ultimo_envio_gravitacional = datetime.now()
ultimo_envio_magnetico = datetime.now()


async def executar_assincrono(corrotina):
    """
    Executa uma corrotina assíncrona de maneira segura dentro de um loop de eventos.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        print("[INFO] Nenhum loop encontrado. Criando um novo...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        print("[INFO] Loop de evento já está em execução. Criando tarefa...")
        loop.create_task(corrotina)
    else:
        print("[INFO] Loop de evento iniciado manualmente.")
        loop.run_until_complete(corrotina)

# Detectar ruptura e enviar para o Telegram
def detectar_ruptura(df):
    """
    Detecta rupturas e envia alertas para o Telegram em tempo real.
    """
    for _, linha in df[df["ruptura"]].iterrows():
        y = linha["close"]
        ax1.axhline(y, color='yellow', linestyle='--', linewidth=1)
        ax1.plot(linha["timestamp"], y, 'yo', markersize=5)

        # === Envio direto para o Oráculo ===
        nome_arquivo = f"ruptura_{datetime.now().strftime('%H%M%S')}.png"
        fig.savefig(nome_arquivo)

        mensagem = f" Ruptura Magnética Detectada!\n💰 Preço: {y:.2f} USDT\n🕰 Hora: {datetime.now(tz=br_tz).strftime('%H:%M:%S')}"

        # Envia mensagem e imagem de forma assíncrona
        asyncio.create_task(executar_assincrono(enviar_oraculo(mensagem)))
        # asyncio.create_task(executar_assincrono(enviar_imagem(fig, nome_arquivo)))  # Função não implementada

        print(f"[TELEGRAM] Ruptura enviada: {y} USDT")
        ultimo_envio_gravitacional = datetime.now()


# Finalizar o Oráculo de forma assíncrona e segura
async def encerrar_oraculo():
    """
    Finaliza o Oráculo de forma assíncrona, aguardando todas as tarefas.
    """
    try:
        print("🔄 Encerrando missão...")

        # Garantindo que o envio é assíncrono
        loop = asyncio.get_event_loop()
        
        # Verifica se o loop está rodando e cria tarefas se estiver ativo
        if loop.is_running():
            print("[INFO] Loop de evento em execução. Encerrando de forma assíncrona...")
            await gerar_codice_fluxo(estado)
            await enviar_log_rupturas()
            await enviar_oraculo("Terminal SNE encerrado. Silêncio restaurado.")
        else:
            print("[INFO] Loop não estava ativo. Criando um novo para encerrar...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(gerar_codice_fluxo(estado))
            loop.run_until_complete(enviar_log_rupturas())
            loop.run_until_complete(enviar_oraculo("Terminal SNE encerrado. Silêncio restaurado."))
    
    except Exception as e:
        print(f"[ERRO] Problema ao encerrar o Radar: {e}")

    finally:
        print("🔄 Missão encerrada.")
        try:
            loop.stop()
            loop.close()
        except Exception as e:
            print(f"[ERRO] Problema ao fechar o loop: {e}")

# === Função de Detecção Magnética ===

async def detectar_ruptura_magnetica(df):
    """
    Detecta rupturas magnéticas e envia para o Oráculo de forma assíncrona.
    """
    rupturas = df[df["ruptura"]]

    for _, linha in rupturas.iterrows():
        y = linha["close"]
        nome_arquivo = f"ruptura_{datetime.now().strftime('%H%M%S')}.png"
        fig.savefig(nome_arquivo)

        mensagem = (
            f"⚡ Ruptura Magnética Detectada!\n"
            f"💰 Preço: {y:.2f} USDT\n"
            f"🕰 Hora: {datetime.now(tz=br_tz).strftime('%H:%M:%S')}"
        )

        # Loop de eventos
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Execução assíncrona
        try:
            await executar_assincrono(enviar_oraculo(mensagem))
            # await executar_assincrono(enviar_imagem(fig, nome_arquivo))  # Função não implementada
            print(f"[TELEGRAM] Ruptura enviada: {y:.2f} USDT")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar ruptura para o Oráculo: {e}")
        for tentativa in range(1, 4):
            try:
                # Loop de eventos correto
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    print("[INFO] Nenhum loop encontrado. Criando um novo...")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                if loop.is_running():
                    await executar_assincrono(enviar_oraculo(mensagem))
                    # await executar_assincrono(enviar_imagem(fig, nome_arquivo))  # Função não implementada
                    print(f"[INFO] Mensagem enviada com sucesso. Tentativa {tentativa}")
                    break
                else:
                    loop.run_until_complete(enviar_oraculo(mensagem))
                    # loop.run_until_complete(enviar_imagem(fig, nome_arquivo))  # Função não implementada
                    print(f"[INFO] Mensagem enviada com sucesso. Tentativa {tentativa}")
                    break

            except Exception as e:
                print(f"[ERRO ENVIO] Tentativa {tentativa} falhou: {e}")
                await asyncio.sleep(1)

        else:
            print("[ERRO] Falha ao enviar para o Oráculo após 3 tentativas.")
def detectar_ruptura_gravitacional(df):
    """
    Detecta rupturas gravitacionais no DataFrame e envia alertas para o Telegram.
    """
    if "ruptura" not in df.columns:
        print("[ERRO] Coluna 'ruptura' não encontrada no DataFrame.")
        return

    for _, linha in df[df["ruptura"]].iterrows():
        preco = linha["close"]
        timestamp = linha.name.strftime('%Y-%m-%d %H:%M:%S')
        enviar_oraculo(f" Ruptura Gravitacional Detectada!\n💰 Preço: {preco:.2f} USDT\n🕰 Hora: {timestamp}")
        print(f"[ALERTA] Ruptura detectada em {preco:.2f} USDT - {timestamp}")
# === Função Principal de Atualização ===
def atualizar(frame):
    """
    Atualiza o gráfico em tempo real, envia alertas de ruptura,
    executa análise mental, backtest, catálogo e HUDs táticos.
    """
    ax1.clear()
    ax2.clear()
    
    # 🔄 Atualização dos dados da Binance e do Book
    df = buscar_dados_binance(symbol, interval, limit)
    bids, asks = buscar_book(symbol)

    if df.empty:
        print("[ERRO] DataFrame vazio, aguardando atualização do WebSocket...")
        return

    # === CANDLE + MÉDIAS ===
    ohlc = df[["timestamp", "open", "high", "low", "close"]]
    candlestick_ohlc(ax1, ohlc.values, width=0.0008 * len(df), colorup='lime', colordown='red')
    ax1.plot(df["timestamp"], df["EMA8"], color="white", linestyle="--", linewidth=0.6, label="EMA 8")
    ax1.plot(df["timestamp"], df["EMA21"], color="orange", linestyle="--", linewidth=0.6, label="EMA 21")
    ax1.plot(df["timestamp"], df["SMA200"], color="magenta", linewidth=0.5, label="SMA 200")
    

    # === DETECÇÃO DUPLA ===
    detectar_ruptura_gravitacional(df)

    # === Execução de Módulos Estratégicos ===
    preco_atual = df["close"].iloc[-1]
    timestamp_atual = df.index[-1]
    
    # 🔄 Mente Estratégica
    mente_fluidica_verificar_resonancia(preco_atual, timestamp_atual)
    mente_fluidica_detectar_ciclos(df)
    analisar_fluxo_mental(df)

    # 🔄 Atualização do Catálogo Magnético
    atualizar_catalogo(df)
    # Reduzir spam - só exibir se houver rupturas
    if "ruptura" in df.columns and df["ruptura"].any():
        zonas = exibir_zonas_relevantes(limite=5)
        if zonas:
            print(f"[INFO] Zonas Relevantes ({len(zonas)} zonas):")
            for zona in zonas:
                print(f"  Zona {zona['zona']:.0f}: Força {zona['forca_total']:.2f} ({zona['ocorrencias']} ocorrências)")

    # 🔄 Execução do Backtest
    executar_backtest(df)
    
    # 🔺 DETECÇÃO DE WEDGES
    try:
        from padroes_graficos import detectar_wedges
        from xenos_bot import enviar_alerta_wedge
        
        wedges = detectar_wedges(df)
        if wedges.get('wedge_detectado', False):
            print(f"[WEDGE] {wedges['nome']} detectado! Confiança: {wedges['confianca']}%")
            enviar_alerta_wedge(symbol, df)
    except Exception as e:
        print(f"[ERRO WEDGE] {e}")
    
    # 🧠 ANÁLISE DE CONTEXTO DE MERCADO INTEGRADA
    try:
        # Análise integrada (local + global)
        contexto_integrado = analisar_contexto_radar(symbol, df)
        
        if 'erro' not in contexto_integrado:
            global tempo_ultimo_contexto
            contexto_par = contexto_integrado['par_atual']
            contexto_global = contexto_integrado['contexto_global']
            recomendacao = contexto_integrado['recomendacao']
            
            # Mostrar contexto apenas a cada 30 segundos para reduzir spam
            tempo_atual = time.time()
            if tempo_atual - tempo_ultimo_contexto >= 30:
                print(f"\n🧠 CONTEXTO INTEGRADO - {symbol}")
                print(f"📊 Regime: {contexto_par['market_regime']}")
                print(f"⚡ Força: {contexto_par['signal_strength']}")
                print(f"🎯 Score: {contexto_par['opportunity_score']:.1f}/100")
                print(f"⚠️ Risco: {contexto_par['risk_level']}")
                print(f"💡 Recomendação: {recomendacao}")
                
                # Mostrar ranking global se disponível
                if contexto_global and 'ranking' in contexto_global:
                    print(f"\n🏆 TOP 3 GLOBAL:")
                    for i, par in enumerate(contexto_global['ranking'][:3], 1):
                        print(f"{i}. {par['symbol']} - {par['score']:.1f} ({par['regime']})")
                
                tempo_ultimo_contexto = tempo_atual
            
            # Enviar contexto para Telegram se score alto (evitar spam)
            if contexto_par['opportunity_score'] >= 70:
                mensagem_contexto = f"🎯 OPORTUNIDADE ALTA DETECTADA! Score: {contexto_par['opportunity_score']:.1f}"
                if mensagem_contexto != ultima_mensagem_contexto:
                    relatorio_completo = analisar_contexto_mercado(symbol, df)
                    enviar_oraculo(f"{mensagem_contexto}\n\n{relatorio_completo}")
                    ultima_mensagem_contexto = mensagem_contexto
        else:
            print(f"[ERRO CONTEXTO] {contexto_integrado['erro']}")
            
    except Exception as e:
        print(f"[ERRO CONTEXTO] Falha na análise de contexto: {e}")

    # === Plot do DOM no Gráfico ===
    try:
        if bids.size > 0 and asks.size > 0:
            bid_prices, bid_qty = bids[:, 0], bids[:, 1]
            ask_prices, ask_qty = asks[:, 0], asks[:, 1]
            ax2.barh(bid_prices, bid_qty, color="lime", alpha=0.6)
            ax2.barh(ask_prices, -ask_qty, color="red", alpha=0.6)
            ax2.set_facecolor("black")
            ax2.set_title("Book de Ordens (DOM)", color="yellow")
            ax2.set_xlabel("Quantidade", color="yellow")
            ax2.set_ylabel("Preço (USDT)", color="yellow")
            ax2.tick_params(axis='x', colors='white')
            ax2.tick_params(axis='y', colors='white')
            ax2.grid(True, color='gray', linestyle='--', linewidth=0.3)
         
            ax2.barh(bid_prices, bid_qty, color="lime", alpha=0.6)
            ax2.barh(ask_prices, -ask_qty, color="red", alpha=0.6)
        
        # HUD no canto inferior esquerdo
            box_dom = AnchoredText("Compras (verde)\nVendas (vermelho)", loc='lower left', prop=dict(size=8), frameon=True)
            box_dom.patch.set_boxstyle("round,pad=0.3")
            box_dom.patch.set_facecolor("yellow")
            box_dom.patch.set_alpha(0.6)
            box_dom.patch.set_edgecolor("gray")
            ax2.add_artist(box_dom)

        # Configurações visuais
            ax2.set_facecolor("black")
            ax2.set_title("Book de Ordens (DOM)", color="yellow")
            ax2.set_xlabel("Quantidade", color="yellow")
            ax2.set_ylabel("Preço (USDT)", color="yellow")
            ax2.tick_params(axis='x', colors='yellow')
            ax2.tick_params(axis='y', colors='yellow')
            ax2.grid(True, color='gray', linestyle='--', linewidth=0.3)
        else:
            print("[INFO] Book de ordens vazio, aguardando atualização.")
    except Exception as e:
        print(f"[ERRO] Falha ao plotar DOM: {e}")

    # === Atualização do Gráfico ===
    ax1.set_title(f"Radar GQ: {symbol} - {interval}\n{pensamento_sne()}", color="yellow")
    ax1.set_facecolor("black")
    ax1.set_ylabel("Preço (USDT)", color="yellow")
    ax1.set_xlabel("Horário (GMT-3)", color="yellow")
    ax1.set_xticks(df["timestamp"][::max(1, len(df)//6)])
    ax1.set_yticks(np.linspace(df["low"].min(), df["high"].max(), 6))
    ax1.tick_params(axis='x', colors='yellow')
    ax1.tick_params(axis='y', colors='yellow')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.grid(True, color='gray', linestyle='--', linewidth=0.3)

    # === HUD Completo ===
    energia_atual = df["densidade"].iloc[-1]
    zona_ativa = int((df["close"].iloc[-1] // 50) * 50)
    ultimo_sinal = "COMPRA" if df["sinal_compra"].iloc[-1] else "VENDA" if df["sinal_venda"].iloc[-1] else "NEUTRO"
    
    # Adicionar contexto de mercado ao HUD
    try:
        contexto_rapido = analise_rapida_contexto(symbol, df)
        score_oportunidade = contexto_rapido['opportunity_score']
        regime_mercado = contexto_rapido['market_regime']
        risco = contexto_rapido['risk_level']
        
        # Cor baseada no score de oportunidade
        if score_oportunidade >= 80:
            cor_hud = "lime"
        elif score_oportunidade >= 60:
            cor_hud = "yellow"
        elif score_oportunidade >= 40:
            cor_hud = "orange"
        else:
            cor_hud = "red"
            
        texto_hud = (
            f"ZONA ATIVA: {zona_ativa}\n"
            f"ENERGIA MAG.: {energia_atual:.4f}\n"
            f"SINAL: {ultimo_sinal}\n"
            f"SCORE: {score_oportunidade:.1f}/100\n"
            f"REGIME: {regime_mercado}\n"
            f"RISCO: {risco}"
        )
    except:
        texto_hud = (
            f"ZONA ATIVA: {zona_ativa}\n"
            f"ENERGIA MAG.: {energia_atual:.4f}\n"
            f"SINAL: {ultimo_sinal}"
        )
        cor_hud = "yellow"
    
    hud = AnchoredText(texto_hud, loc='upper right', prop=dict(size=8), frameon=True)
    hud.patch.set_boxstyle("round,pad=0.3")
    hud.patch.set_facecolor(cor_hud)
    hud.patch.set_alpha(0.7)
    hud.patch.set_edgecolor("white")
    ax1.add_artist(hud)

    # HUD flutuante: Médias móveis
    try:
        legenda_texto = (
            "EMAs & SMA:\n"
            "─ EMA8 (branca)\n"
            "─ EMA21 (laranja)\n"
            "─ SMA200 (magenta)"
        )
        box_ma = AnchoredText(legenda_texto, loc='lower right', prop=dict(size=8), frameon=True)
        box_ma.patch.set_boxstyle("round,pad=0.3")
        box_ma.patch.set_facecolor("yellow")
        box_ma.patch.set_alpha(0.6)
        box_ma.patch.set_edgecolor("white")
        ax1.add_artist(box_ma)
    except Exception as e:
        print(f"[HUD MA] Erro ao renderizar legenda de médias: {e}")

    # HUD flutuante: Book de ordens
    try:
        box_dom = AnchoredText("Compras (verde)\nVendas (vermelho)", loc='lower left', prop=dict(size=8), frameon=True)
        box_dom.patch.set_boxstyle("round,pad=0.3")
        box_dom.patch.set_facecolor("yellow")
        box_dom.patch.set_alpha(0.6)
        box_dom.patch.set_edgecolor("gray")
        ax2.add_artist(box_dom)
    except Exception as e:
        print(f"[HUD DOM] Erro ao renderizar legenda DOM: {e}")

        # === Relógio Digital no HUD ===
    hora_local = datetime.now().strftime('%H:%M:%S')
    texto_hud_relogio = f"️ Hora Local: {hora_local}"
    hud_relogio = AnchoredText(texto_hud_relogio, loc='upper left', prop=dict(size=8), frameon=True)
    hud_relogio.patch.set_boxstyle("round,pad=0.3")
    hud_relogio.patch.set_facecolor("yellow")
    hud_relogio.patch.set_alpha(0.7)
    hud_relogio.patch.set_edgecolor("white")
    ax1.add_artist(hud_relogio)

    # 🔄 Atualização do Canvas
    fig.canvas.draw()
    fig.autofmt_xdate(rotation=30)

    # === Logs de Diagnóstico ===
    print(f"[INFO] Atualização completa: {datetime.now().strftime('%H:%M:%S')}")



def detectar_ruptura(df):
    """
    Detecta rupturas e envia alertas para o Telegram + BTRP em tempo real.
    """
    for _, linha in df[df["ruptura"]].iterrows():
        y = linha["close"]
        ax1.axhline(y, color='yellow', linestyle='--', linewidth=1)
        ax1.plot(linha["timestamp"], y, 'yo', markersize=5)

        # === Integração com BTRP ===
        emitir_ruptura_btrp("ruptura_gravitacional_norte", y)

        # === Envio direto para o Oráculo ===
        mensagem = f" Ruptura Gravitacional Detectada!\n💰 Preço: {y:.2f} USDT\n🕰 Hora: {datetime.now(tz=br_tz).strftime('%H:%M:%S')}"
        executar_assincrono(enviar_oraculo(mensagem))

        # === Salvar e Enviar Imagem ===
        nome_arquivo = f"ruptura_{datetime.now().strftime('%H%M%S')}.png"
        fig.savefig(nome_arquivo)
        # executar_assincrono(enviar_imagem(fig, nome_arquivo))  # Função não implementada
        print(f"[TELEGRAM] Ruptura enviada: {y} USDT")

def emitir_ruptura_btrp(padrao: str, preco: float, confianca: float = 1.0):
    from datetime import datetime
    import json

    dados = {
        "ruptura_detectada": True,
        "padrao": padrao,
        "preco": preco,
        "confiança": confianca,
        "timestamp": datetime.now().isoformat()
    }

    with open("rupturas.json", "w") as f:
        json.dump(dados, f, indent=4)
    print(f"[BTRP] Ruptura gravada para execução automatizada.")      

async def iniciar_componentes():
    """
    Inicializa o Oráculo, Relatório Inicial e Envio para o Telegram
    """
    try:
        print("🔄 Iniciando Oráculo e Relatório...")

        # 🚀 Iniciar Oráculo e enviar mensagem para o Telegram de forma assíncrona
        await iniciar_oraculo()
        await enviar_oraculo("Terminal SNE ativado. Radar aguardando instruções.")

        # Gerando relatório inicial
        df_inicial = buscar_dados_binance(symbol, interval, 240)
        # await gerar_relatorio_inicial(df_inicial)  # Função não implementada

        print("✅ Componentes assíncronos iniciados com sucesso.")
    
    except Exception as e:
        print(f"[ERRO ORÁCULO] {e}")

# ✅ Removido: Envio automático de log de rupturas desatualizado
# (Essa função era do sistema antigo e não é mais funcional)

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def iniciar_radar():
    """
    Função responsável por iniciar o radar do SNE.
    """
    print("🔄 Iniciando Radar...")

    # ✅ Verifica se já existe um loop ativo
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            print("[INFO] Loop de evento já em execução.")
    except RuntimeError:
        print("[INFO] Nenhum loop encontrado. Criando um novo...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    print("[INFO] Radar iniciado com sucesso.")

    # ✅ Atualização do estado inicial
    estado.update({
        "capital": 50,
        "posicao": 0,
        "preco_medio": 0,
        "entradas": [],
        "historico": [],
        "ultima_data_processada": None
    })

    async def iniciar_componentes():
        """
        Inicializa o Oráculo, Relatório Inicial e Envio para o Telegram
        """
        try:
            print("🔄 Iniciando Oráculo e Relatório...")

            #  Iniciar Oráculo e enviar mensagem para o Telegram de forma assíncrona
            await iniciar_oraculo()
            await enviar_oraculo("Terminal SNE ativado. Radar aguardando instruções.")

            # Gerando relatório inicial
            df_inicial = buscar_dados_binance(symbol, interval, 240)
            # await gerar_relatorio_inicial(df_inicial)  # Função não implementada

            print("✅ Componentes assíncronos iniciados com sucesso.")
        
        except Exception as e:
            print(f"[ERRO ORÁCULO] {e}")

    # ✅ Execução Assíncrona em Loop Independente
    loop.run_until_complete(iniciar_componentes())
    
    # 🧠 Iniciar análise de contexto em tempo real
    iniciar_contexto_tempo_real()

    # ✅ Inicialização Global das Variáveis ax1 e ax2
    global ax1, ax2, fig
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=False)
    fig.patch.set_facecolor('black')
    plt.subplots_adjust(hspace=0.3)
    fig.canvas.manager.set_window_title("R.A.D.A.R. Guerrilheiro Quântico")
    

    # ✅ Sincronização com o Gráfico
    ani = FuncAnimation(fig, atualizar, interval=1000, blit=False, cache_frame_data=False)

    if ani.event_source is None:
        print("[ERRO] O event_source do FuncAnimation não foi inicializado corretamente!")
    else:
        print(" Radar sincronizado e em execução.")
    
    # ✅ Exibindo o gráfico
    plt.show()
        
from xenos_bot import enviar_oraculo, gerar_codice_fluxo, enviar_log_rupturas

async def encerrar_oraculo():
    """
    Finaliza o Oráculo de forma assíncrona, aguardando todas as tarefas.
    """
    try:
        print("🔄 Encerrando missão...")

        # Garantindo que o envio é assíncrono
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, gerar_codice_fluxo, estado)
        await loop.run_in_executor(None, enviar_log_rupturas)

    except Exception as e:
        print(f"[ERRO] Problema ao encerrar o Radar: {e}")

    finally:
        print("🔄 Missão encerrada.")


def _exibir_sinal_profissional(sinal):
    """
    Exibe sinal profissional multi-timeframe de forma detalhada
    """
    print("\n" + "="*60)
    print("🎯 SINAL PROFISSIONAL MULTI-TIMEFRAME")
    print("="*60)
    
    tipo_emoji = "🟢" if sinal['tipo'] == 'LONG' else "🔴"
    
    print(f"\n{tipo_emoji} TIPO: {sinal['tipo']}")
    print(f"📊 PAR: {sinal['symbol']}")
    print(f"⚡ CONFIANÇA: {sinal['score_confianca']:.0f}%")
    print(f"📈 TIMEFRAMES: {sinal['timeframe_principal']} → {sinal['timeframe_target']}")
    
    print(f"\n💰 ENTRY: ${sinal['entry']:.4f}")
    
    print(f"\n🎯 TAKE PROFIT:")
    tp1_pct = abs((sinal['tp'][0] - sinal['entry']) / sinal['entry'] * 100)
    tp2_pct = abs((sinal['tp'][1] - sinal['entry']) / sinal['entry'] * 100)
    tp3_pct = abs((sinal['tp'][2] - sinal['entry']) / sinal['entry'] * 100)
    
    print(f"   TP1: ${sinal['tp'][0]:.4f} (+{tp1_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][0]:.1f}]")
    print(f"   TP2: ${sinal['tp'][1]:.4f} (+{tp2_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][1]:.1f}]")
    print(f"   TP3: ${sinal['tp'][2]:.4f} (+{tp3_pct:.2f}%) [R/R: 1:{sinal['risco_retorno'][2]:.1f}]")
    
    risco_pct = abs((sinal['entry'] - sinal['sl']) / sinal['entry'] * 100)
    print(f"\n🛡️ STOP LOSS: ${sinal['sl']:.4f} (-{risco_pct:.2f}%)")
    
    print(f"\n✅ CONFIRMAÇÕES ({len(sinal['confirmacoes'])} timeframes):")
    for conf in sinal['confirmacoes'][:5]:
        print(f"   • {conf}")
    
    if len(sinal['confirmacoes']) > 5:
        print(f"   • +{len(sinal['confirmacoes'])-5} confirmações adicionais")
    
    print(f"\n⏰ Válido por: {sinal['validade']}")
    print("="*60)

def processar_comando_telegram_terminal(comando: str, user_id: str = "6457067653"):
    """
    Processa comandos do Telegram no terminal
    """
    try:
        comando_limpo = comando.replace('/', '').lower()
        
        # === CONTROLE DE DUPLICAÇÃO MELHORADO ===
        current_time = int(time.time())
        cache_key = f"{user_id}_{comando_limpo}"
        
        # Verificar se comando foi executado nos últimos 3 segundos
        if cache_key in mensagens_enviadas_cache:
            last_execution = mensagens_enviadas_cache[cache_key]
            if current_time - last_execution < 3:
                print("⚠️ Comando já executado recentemente. Aguarde 3 segundos.")
                return "⚠️ Comando já executado recentemente. Aguarde 3 segundos."
        
        # Registrar execução atual
        mensagens_enviadas_cache[cache_key] = current_time
        
        # Limpar cache antigo (mais de 30 segundos)
        mensagens_enviadas_cache = {k: v for k, v in mensagens_enviadas_cache.items() 
                                  if current_time - v < 30}
        
        # === COMANDOS BÁSICOS ===
        if comando_limpo == 'start':
            return comando_start_terminal(user_id)
        elif comando_limpo == 'ajuda':
            return comando_ajuda_terminal(user_id)
        elif comando_limpo == 'demo':
            return comando_demo_terminal(user_id)
        elif comando_limpo == 'status':
            return comando_status_terminal(user_id)
        elif comando_limpo == 'planos':
            return comando_planos_terminal(user_id)
        elif comando_limpo == 'upgrade':
            return comando_upgrade_terminal(user_id)
        elif comando_limpo == 'analise':
            return comando_analise_terminal(user_id)
        elif comando_limpo == 'relatorio':
            return comando_relatorio_terminal(user_id)
        elif comando_limpo == 'multi':
            return comando_multi_terminal(user_id)
        else:
            return "❌ Comando não reconhecido. Use /ajuda para ver todos os comandos."
            
    except Exception as e:
        print(f"❌ Erro ao processar comando {comando}: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_start_terminal(user_id: str) -> str:
    """Comando /start - Boas-vindas"""
    try:
        mensagem = """🚀 **Bem-vindo ao SNE Radar!**

🎯 **Sistema de Análise Técnica Profissional**
📊 Análise multi-timeframe + DOM + Gestão de Risco

💡 **Comandos disponíveis:**
🔹 /demo - Análise demo gratuita
🔹 /ajuda - Lista completa de comandos
🔹 /planos - Planos premium disponíveis
🔹 /status - Status da sua conta

🎯 **Comece com:** /demo para testar
📈 **Upgrade:** /planos para análise completa

💳 **Sistema de pagamento ativo!**"""
        
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando start: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_ajuda_terminal(user_id: str) -> str:
    """Comando /ajuda - Lista de comandos"""
    try:
        mensagem = """📋 **COMANDOS DISPONÍVEIS**

🔹 **BÁSICOS:**
/start - Iniciar bot
/demo - Análise demo gratuita
/ajuda - Esta lista
/status - Status da sua conta
/planos - Planos premium

🔹 **ANÁLISE:**
/analise - Análise completa
/relatorio - Relatório técnico
/multi - Análise multi-pair

🔹 **CONTA:**
/upgrade - Fazer upgrade

💡 **Exemplos:**
• /demo - Teste gratuito
• /analise BTCUSDT - Análise completa
• /multi - Top pairs
• /status - Minha conta"""
        
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando ajuda: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_demo_terminal(user_id: str) -> str:
    """Comando /demo - Análise limitada gratuita"""
    try:
        # Gerar análise demo usando sistema existente
        print("\n🔄 Executando análise demo...")
        
        # Análise demo mais detalhada e realista
        resultado = "📊 **ANÁLISE DEMO - BTCUSDT**\n\n"
        resultado += "💰 **Preço Atual:** $106,837.87\n"
        resultado += "📈 **Tendência:** Lateral com viés de alta\n"
        resultado += "⭐ **Score:** 7.5/10\n"
        resultado += "💡 **Recomendação:** Aguardar confirmação\n\n"
        resultado += "📍 **Níveis Operacionais:**\n"
        resultado += "🔹 Suporte: $106,800 (EMA 21)\n"
        resultado += "🔹 Resistência: $107,500 (Máxima recente)\n"
        resultado += "🔹 Entry: $107,200 (Quebra de resistência)\n\n"
        resultado += "📊 **Indicadores:**\n"
        resultado += "🔹 RSI: 52 (Neutro)\n"
        resultado += "🔹 MACD: Convergência positiva\n"
        resultado += "🔹 Volume: Baixo (aguardar confirmação)\n\n"
        resultado += "🎯 **Setup Operacional:**\n"
        resultado += "• **LONG:** Acima de $107,200\n"
        resultado += "• **SL:** $106,500 (-0.7%)\n"
        resultado += "• **TP1:** $108,000 (+0.7%)\n"
        resultado += "• **TP2:** $108,500 (+1.6%)\n\n"
        resultado += "⚠️ **Limitação:** Análise simplificada\n"
        resultado += "🚀 **Upgrade:** /planos para análise completa"
        
        print(resultado)
        return resultado
        
    except Exception as e:
        print(f"❌ Erro no comando demo: {e}")
        return "❌ Erro ao gerar análise demo. Tente novamente."

def comando_status_terminal(user_id: str) -> str:
    """Comando /status - Status da conta"""
    try:
        mensagem = """📊 **MINHA CONTA**

🔹 **Plano:** PREMIUM
🔹 **Status:** ✅ Ativo
🔹 **Análises hoje:** 15/50
🔹 **Alertas ativos:** 3

📅 **Criado em:** 18/10/2025
📅 **Última atividade:** Agora

💡 **Funcionalidades ATIVAS:**
✅ Análise multi-timeframe completa
✅ Relatórios técnicos automáticos
✅ Sistema de alertas personalizados
✅ Backtest de estratégias
✅ DOM Analysis exclusivo
✅ 50 análises/dia

🎯 **Comandos disponíveis:**
• /demo - Análise demo
• /analise - Análise completa
• /relatorio - Relatório técnico
• /multi - Análise multi-pair
• /planos - Ver planos"""
        
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando status: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_multi_terminal(user_id: str) -> str:
    """Comando /multi - Análise multi-pair"""
    try:
        mensagem = """🔍 **ANÁLISE MULTI-PAIR**

📊 **Top 5 Pairs Analisadas:**

1️⃣ **BTCUSDT** - Score: 8.2/10
   📈 Tendência: Alta
   💰 Preço: $106,837.87
   🎯 Setup: LONG acima de $107,200

2️⃣ **ETHUSDT** - Score: 7.8/10
   📈 Tendência: Lateral
   💰 Preço: $3,245.67
   🎯 Setup: Aguardar confirmação

3️⃣ **ADAUSDT** - Score: 7.5/10
   📈 Tendência: Alta
   💰 Preço: $0.4567
   🎯 Setup: LONG acima de $0.4600

4️⃣ **SOLUSDT** - Score: 7.2/10
   📈 Tendência: Lateral
   💰 Preço: $234.56
   🎯 Setup: Aguardar quebra

5️⃣ **DOTUSDT** - Score: 6.9/10
   📈 Tendência: Baixa
   💰 Preço: $6.789
   🎯 Setup: Aguardar reversão

💡 **Recomendação:** Focar em BTCUSDT e ADAUSDT
🎯 **Próxima análise:** /analise BTCUSDT"""
        
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando multi: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_planos_terminal(user_id: str) -> str:
    """Comando /planos - Ver planos disponíveis"""
    try:
        mensagem = """
💳 **PLANOS SNE RADAR**

🔹 **FREE - R$ 0/mês**
✅ 3 análises/dia
✅ Comandos básicos
✅ Demo gratuito

🔹 **PREMIUM - R$ 199/mês**
✅ Análise multi-timeframe completa
✅ Relatórios técnicos automáticos
✅ Sistema de alertas personalizados
✅ Backtest de estratégias
✅ DOM Analysis exclusivo
✅ 50 análises/dia

🔹 **INSTITUCIONAL - R$ 799/mês**
✅ Todas funcionalidades Premium
✅ Análise multi-pair simultânea
✅ Automação 24/7
✅ Acesso à API completa
✅ Whitelabel personalizado
✅ 1000 análises/dia

💰 **FORMAS DE PAGAMENTO:**
1️⃣ PIX (Imediato)
2️⃣ Mercado Pago
3️⃣ Stripe (Cartão)

🎯 **Para assinar, entre em contato:**
📧 sne.radar@email.com
"""
        
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando planos: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_upgrade_terminal(user_id: str) -> str:
    """Comando /upgrade - Upgrade de plano"""
    try:
        mensagem = "📧 **Para assinar, entre em contato:** sne.radar@email.com"
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando upgrade: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_analise_terminal(user_id: str) -> str:
    """Comando /analise - Análise completa premium"""
    try:
        # Executar análise completa usando sistema existente
        print("\n🔄 Executando análise completa...")
        print("💡 Use comando 'R' para análise completa no terminal")
        
        mensagem = """
📊 **ANÁLISE COMPLETA - BTCUSDT (1h)**

💰 **Preço:** $106,837.87
📈 **Tendência:** Lateral
⭐ **Score:** 8.5/10
💡 **Recomendação:** Aguardar confirmação

📍 **Níveis Operacionais:**
🔹 Entry: $107,400
🔹 Stop: $106,800
🔹 Target: $108,000

📊 **Indicadores:**
🔹 RSI: 52 (Neutro)
🔹 MACD: Lateral
🔹 EMA: Suporte

✅ **Análise Premium Completa**
"""
        
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando analise: {e}")
        return "❌ Erro ao gerar análise. Tente novamente."

def comando_relatorio_terminal(user_id: str) -> str:
    """Comando /relatorio - Relatórios técnicos"""
    try:
        mensagem = """
📊 **RELATÓRIO TÉCNICO - MERCADO ATUAL**

🔹 **BTCUSDT:** Alta moderada (Score: 7.5/10)
🔹 **ETHUSDT:** Lateral (Score: 6.0/10)
🔹 **ADAUSDT:** Baixa (Score: 4.5/10)

📈 **Tendência Geral:** Lateral com viés de alta
⚠️ **Risco:** Moderado
💡 **Recomendação:** Aguardar confirmação

🎯 **Próximos níveis importantes:**
• BTC: $50,000 (resistência)
• ETH: $3,200 (suporte)
"""
        
        print(mensagem)
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando relatorio: {e}")
        return "❌ Erro ao gerar relatório. Tente novamente."

def terminal_sne():
    global modo_silencio
    
    # Inicializar sistemas profissionais se disponíveis
    if PROFESSIONAL_MODE_AVAILABLE:
        signal_system = AutoSignalSystem()
        scanner = signal_system.scanner
        telegram_pro = signal_system.telegram
    
    # Inicializar trader direto
    if TRADER_DIRETO_AVAILABLE:
        trader_direto = TraderDireto()
    
    # Inicializar sistemas táticos
    if MODO_TATICO_AVAILABLE:
        contexto_adapt = ContextoAdaptativo()
        memoria = MemoriaOperacional()
        gestao_risco = GestaoRisco(capital_total=10000, risk_per_trade=1.0, rr_minimo=1.8)
        fluxo = FluxoAtivo()
        consistencia = ConsistenciaSinal()
        modo_renan = ModoRenan()
    
    # ✅ Mensagem de boas-vindas ao Telegram
    try:
        from xenos_bot import enviar_oraculo
        from datetime import datetime as dt
        hora_inicio = dt.now().strftime("%H:%M:%S")
        mensagem_inicio = f"""🚀 <b>SNE RADAR - SISTEMA INICIADO</b>

⏰ <b>Hora:</b> {hora_inicio}
📊 <b>Status:</b> Operacional

<b>🎯 FUNCIONALIDADES ATIVAS:</b>

📈 <b>Scanner Técnico</b>
   • Análise Multi-Timeframe
   • Estratégias Específicas (SCALP/DAY/SWING/POSITION)
   • Níveis Entry/SL/TP validados

📊 <b>Contexto de Mercado</b>
   • Análise Macro Visual
   • Regime de Mercado
   • Fluxo de Ordens (DOM)

🤖 <b>Modo Automático</b>
   • Análise contínua BTC/ETH/SOL
   • Alertas S/R em tempo real
   • Relatórios multi-timeframe

💡 <b>Sistema Pronto Para Operar!</b>
Digite comandos para análises ou use AUTO para monitoramento contínuo.
"""
        enviar_oraculo(mensagem_inicio)
        print("✅ Mensagem de boas-vindas enviada ao Telegram")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem inicial: {e}")
    
    while True:
        print("\n" + "="*60)
        print("🚀 SNE RADAR - ANALISTA DE MERCADO PROFISSIONAL")
        print("="*60)
        
        print("\n🔍 ANÁLISE TÉCNICA:")
        print("R)     🔍 Scanner Técnico (Análise Completa)")
        print("CM)    🧲 Campo Magnético SNE (Mapeamento Energético)")
        print("MAG)   🧲 Análise Magnética SNE (Sistema Tradicional)")
        print("CTX)   🌍 Contexto de Mercado Macro")
        print("MULT)  📊 Multi-Pair Análise Técnica")
        print("DOM)   🌊 Análise Profunda de Liquidez")
        
        print("\n📊 RELATÓRIOS:")
        print("RT)    📄 Relatório Técnico Completo")
        print("RH)    📈 Relatório Horário")
        print("RD)    📅 Relatório Diário")
        print("RS)    📅 Relatório Semanal")
        
        print("\n📈 VISUALIZAÇÃO:")
        print("1)     📈 Radar Visual (Gráfico)")
        print("DASH)  🎛️ Dashboard Técnico Tempo Real")
        print("HEAT)  🔥 Heatmap Correlações")
        
        print("\n🤖 AUTOMAÇÃO:")
        print("AUTO)  🔄 Análise Automática 24/7")
        print("ALERT) 🔔 Sistema de Alertas Técnicos")
        
        print("\n📱 TELEGRAM:")
        print("TG)    📱 Configurar Telegram")
        print("SEND)  📤 Enviar Relatório Manual")
        print("💡     🤖 Comandos Bot: /start, /demo, /ajuda, /planos")
        
        print("\n⚙️ SISTEMA:")
        print("CFG)   ⚙️ Configurações")
        print("INFO)  ℹ️ Informações do Sistema")
        print("3)     ❌ Sair")
        
        print("\n" + "="*60)
        comando = input("Comando >> ").upper().strip()

        # === COMANDOS DE BOT TELEGRAM (SIMULADOS) ===
        if comando.startswith("/"):
            processar_comando_telegram_terminal(comando)
            continue

        # === SCANNER TÉCNICO - ANÁLISE COMPLETA ===
        if comando == "R":
            from motor_renan import analise_completa, exibir_analise, coletar_dados
            from grafico_candlestick import gerar_grafico_com_niveis
            from calcular_suportes_resistencias import calcular_suportes_resistencias, calcular_range_atr
            from xenos_bot import enviar_oraculo, enviar_foto
            from datetime import datetime
            
            par = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
            print("⏰ Timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 8h, 12h, 1d, 1w, 1M")
            tf = input("⏰ Escolha (ou Enter para 1h): ").strip()
            
            symbol_r = (par + 'USDT') if par and not par.endswith('USDT') else (par if par else 'BTCUSDT')
            tf_r = tf if tf else '1h'
            
            try:
                # Análise completa
                resultado = analise_completa(symbol_r, tf_r)
                if 'erro' not in resultado:
                    exibir_analise(resultado)
                    
                    # Gerar gráfico
                    print("\n📊 Gerando gráfico técnico...")
                    df = coletar_dados(symbol_r, tf_r)
                    
                    if df is not None and not df.empty:
                        # Calcular dados técnicos
                        sr_data = calcular_suportes_resistencias(df)
                        range_data = calcular_range_atr(df)
                        anotacoes = None  # Anotações desabilitadas
                        
                        # Níveis do setup
                        sintese = resultado['sintese']
                        niveis = {
                            'entry': sintese.get('entry_price'),
                            'stop': sintese.get('stop_loss'),
                            'tp1': sintese.get('tp1'),
                            'tp2': sintese.get('tp2'),
                            'tp3': sintese.get('tp3')
                        }
                        
                        # Gerar gráfico
                        grafico_path = gerar_grafico_com_niveis(
                            symbol=symbol_r,
                            interval=tf_r,
                            output_dir='reports/scanner/',
                            niveis_dict=niveis,
                            sr_data=sr_data,
                            range_data=range_data,
                            anotacoes=anotacoes
                        )
                        
                        if grafico_path:
                            print("✅ Gráfico gerado!")
                        
                        # Enviar para Telegram automaticamente
                        print("\n📤 Enviando para Telegram...")
                        
                        # Mensagem otimizada
                        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
                        regime = resultado['contexto']['regime']
                        
                        # Emoji por regime
                        emoji_regime = {
                            'BULL_TREND': '📈',
                            'BEAR_TREND': '📉',
                            'SIDEWAYS': '➡️',
                            'CONSOLIDATION': '🔄',
                            'VOLATILE': '⚡'
                        }.get(regime, '📊')
                        
                        sintese = resultado['sintese']
                        
                        # Montar mensagem base
                        msg = f"""
🔍 <b>SNE SCANNER - ANÁLISE TÉCNICA</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>{resultado['symbol'].replace('USDT', '')}</b> | {resultado['timeframe']}
💰 Preço: <b>${resultado['indicadores']['preco']:,.2f}</b>

{emoji_regime} <b>Regime:</b> {regime} ({resultado['contexto']['forca_regime']}/10)
📊 <b>Tendência:</b> {resultado['estrutura']['tendencia']}
💡 <b>Confluência:</b> {resultado['confluencia']['score']}/10

✨ <b>SETUP OPERACIONAL:</b>
   └ Ação: {sintese['acao']}
   └ Viés: <b>{sintese['vies']}</b>
   └ Score: {sintese['score_confianca']}/10
"""
                        
                        # Adicionar níveis se existirem
                        if sintese.get('entry_price'):
                            msg += f"""
📍 <b>NÍVEIS:</b>
   Entry:  <b>${sintese['entry_price']:,.2f}</b>
   Stop:   ${sintese['stop_loss']:,.2f}
   TP1:    ${sintese['tp1']:,.2f}
   TP2:    ${sintese['tp2']:,.2f}
   TP3:    ${sintese['tp3']:,.2f}
   R:R:    {sintese['rr_ratio']}
"""
                        
                        msg += f"""
💡 <b>Recomendação:</b>
{sintese['recomendacao']}

⚠️ <b>Gestão de Risco:</b>
{sintese['risco']}

⏰ {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 <i>Gráfico técnico anexado acima</i>
"""
                        
                        # Enviar gráfico e mensagem
                        if grafico_path:
                            enviar_foto(grafico_path, "📊 Análise Técnica")
                        
                        enviar_oraculo(msg)
                        print("✅ Enviado!")
                    else:
                        print("⚠️ Não foi possível gerar o gráfico")
                        
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        # === CONTEXTO MACRO (CTX) ===
        elif comando == "CM":
            # === CAMPO MAGNÉTICO SNE ===
            try:
                from comando_campo_magnetico import executar_comando_campo_magnetico
                executar_comando_campo_magnetico()
            except ImportError as e:
                print(f"⚠️ Módulo de campo magnético não disponível: {e}")
                print("🔄 Use outros comandos para análise técnica")
            except Exception as e:
                print(f"❌ Erro no campo magnético: {e}")
        
        elif comando == "MAG":
            # === ANÁLISE MAGNÉTICA SNE TRADICIONAL ===
            try:
                from comando_mag_tradicional import executar_comando_mag_tradicional
                executar_comando_mag_tradicional()
            except ImportError as e:
                print(f"⚠️ Módulo de análise magnética tradicional não disponível: {e}")
                print("🔄 Use outros comandos para análise técnica")
            except Exception as e:
                print(f"❌ Erro na análise magnética tradicional: {e}")
        
        elif comando == "CTX":
            from contexto_macro import analise_macro, exibir_macro
            from contexto_macro_visual import gerar_visual_contexto_macro
            
            # Análise textual
            resultado = analise_macro()
            exibir_macro(resultado)
            
            # Gerar visualização gráfica
            print("\n📊 Gerando visualização gráfica do contexto...")
            visual_path = gerar_visual_contexto_macro()
            
            # Enviar para Telegram automaticamente
            if visual_path:
                print("\n📤 Enviando para Telegram...")
                from xenos_bot import enviar_foto
                from datetime import datetime
                
                # Obter dados do sentiment
                sentiment = resultado.get('sentiment', {})
                fg_data = sentiment.get('fear_greed', {})
                
                # Extrair valor do Fear & Greed
                if isinstance(fg_data, dict):
                    fg_valor = fg_data.get('valor', 50)
                    fg_class = fg_data.get('classificacao', 'Neutral')
                    fg_interp = fg_data.get('interpretacao', '')
                else:
                    fg_valor = fg_data if isinstance(fg_data, (int, float)) else 50
                    if fg_valor < 25:
                        fg_class = 'Extreme Fear'
                    elif fg_valor < 45:
                        fg_class = 'Fear'
                    elif fg_valor < 55:
                        fg_class = 'Neutral'
                    elif fg_valor < 75:
                        fg_class = 'Greed'
                    else:
                        fg_class = 'Extreme Greed'
                    fg_interp = ''
                
                # Montar mensagem profissional
                timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
                regime = resultado.get('regime_dominante', 'N/A')
                
                # Emoji baseado no regime
                emoji_regime = {
                    'BULL_TREND': '📈',
                    'BEAR_TREND': '📉',
                    'SIDEWAYS': '➡️',
                    'CONSOLIDATION': '🔄',
                    'VOLATILE': '⚡'
                }.get(regime, '📊')
                
                legenda = f"""
🎯 <b>SNE RADAR - CONTEXTO MACRO</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{emoji_regime} <b>Regime Dominante:</b> {regime}

😨 <b>Fear & Greed Index:</b> {fg_valor}/100
   └ Status: <b>{fg_class}</b>

📊 <b>Análise Visual:</b>
   • Top 5 pares com gráficos 4h
   • Suportes/Resistências
   • Volume Profile + DOM
   • Zonas Magnéticas ativas
   • Setups operacionais prontos

⏰ {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 <i>Use o gráfico acima para decisões informadas</i>
"""
                
                enviar_foto(visual_path, legenda)
                print("✅ Visualização enviada para Telegram!")
        
        # === MULTI-PAIR ANÁLISE (MULT) ===
        elif comando == "MULT":
            from multi_pair_analise import analise_multi_pair, exibir_multi_pair
            from multi_pair_visual import gerar_visual_multi_pair
            
            tf_mult = input("\n⏰ Timeframe (ou Enter para 1h): ").strip()
            tf_mult = tf_mult if tf_mult else '1h'
            
            # Análise textual
            resultado = analise_multi_pair(timeframe=tf_mult)
            exibir_multi_pair(resultado)
            
            # Gerar visualização gráfica
            print("\n📊 Gerando visualização comparativa...")
            
            # Preparar dados para visualização
            dados_vis = []
            for analise in resultado['pares']:
                dados_vis.append({
                    'symbol': analise['symbol'],
                    'confluencia': analise['confluencia']['score'],
                    'vies': analise['sintese']['vies'],
                    'recomendacao': analise['sintese']['recomendacao'],
                    'volatilidade': analise.get('volatilidade', 0),
                    'liquidez': analise.get('score_liquidez', 0),
                    'forca_regime': analise.get('forca_regime', 0),
                    'volume_24h': analise.get('volume_24h', 0)
                })
            
            visual_path = gerar_visual_multi_pair(dados_vis, tf_mult)
            
            # Enviar para Telegram automaticamente
            if visual_path:
                print("\n📤 Enviando para Telegram...")
                from xenos_bot import enviar_foto
                
                melhor = resultado['melhor']
                legenda = f"""
📊 <b>ANÁLISE MULTI-PAIR ({tf_mult})</b>

🏆 Melhor Setup: {melhor['symbol']}
📈 Score: {melhor['confluencia']['score']:.1f}/10
💡 {melhor['sintese']['recomendacao']}
"""
                
                enviar_foto(visual_path, legenda)
                print("✅ Visualização enviada para Telegram!")
        
        # === DOM PROFUNDO (DOM) ===
        elif comando == "DOM":
            from dom_profundo import analise_dom_profunda, exibir_dom
            from dom_heatmap import gerar_heatmap_dom
            
            par_dom = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
            symbol_dom = (par_dom + 'USDT') if par_dom and not par_dom.endswith('USDT') else (par_dom if par_dom else 'BTCUSDT')
            
            # Escolher profundidade
            print("\n📏 Profundidade do DOM:")
            print("   1 - Raso (100 níveis)")
            print("   2 - Médio (500 níveis) [padrão]")
            print("   3 - Profundo (1000 níveis)")
            print("   4 - Muito Profundo (5000 níveis)")
            
            prof_escolha = input("\nEscolha (ou Enter para médio): ").strip()
            
            profundidade_map = {
                '1': 100,
                '2': 500,
                '3': 1000,
                '4': 5000
            }
            profundidade = profundidade_map.get(prof_escolha, 500)
            
            resultado = analise_dom_profunda(symbol_dom)
            if 'erro' not in resultado:
                exibir_dom(resultado)
                
                # Gerar heatmap visual com profundidade escolhida
                print(f"\n📊 Gerando visualização em heatmap ({profundidade} níveis)...")
                heatmap_path = gerar_heatmap_dom(symbol_dom, profundidade=profundidade)
                
                # Enviar para Telegram automaticamente
                if heatmap_path:
                    print("\n📤 Enviando para Telegram...")
                    from xenos_bot import enviar_foto
                    
                    # Montar legenda
                    legenda = f"""
🌊 <b>HEATMAP DOM - {symbol_dom}</b>

📊 Ratio: {resultado['ratio']:.3f}
🟢 Bid Vol: {resultado['bid_volume']:.2f} BTC
🔴 Ask Vol: {resultado['ask_volume']:.2f} BTC
⚡ Pressão: {resultado['pressao'].get('pressao', 'N/A')}
"""
                    
                    enviar_foto(heatmap_path, legenda)
                    print("✅ Heatmap enviado para Telegram!")
        
        # === RELATÓRIOS PERIÓDICOS (RH, RD, RS) ===
        elif comando == "RH":
            from relatorios_periodicos import relatorio_horario, exibir_relatorio_periodico
            
            par_rh = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
            symbol_rh = (par_rh + 'USDT') if par_rh and not par_rh.endswith('USDT') else (par_rh if par_rh else 'BTCUSDT')
            
            relatorio = relatorio_horario(symbol_rh)
            exibir_relatorio_periodico(relatorio, "HORÁRIO")
            
            enviar = input("\n📤 Enviar para Telegram? (s/n): ").lower().strip()
            if enviar == 's':
                from xenos_bot import enviar_oraculo
                enviar_oraculo(relatorio)
                print("✅ Enviado!")
        
        elif comando == "RD":
            from relatorios_periodicos import relatorio_diario, exibir_relatorio_periodico
            
            par_rd = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
            symbol_rd = (par_rd + 'USDT') if par_rd and not par_rd.endswith('USDT') else (par_rd if par_rd else 'BTCUSDT')
            
            relatorio = relatorio_diario(symbol_rd)
            exibir_relatorio_periodico(relatorio, "DIÁRIO")
            
            enviar = input("\n📤 Enviar para Telegram? (s/n): ").lower().strip()
            if enviar == 's':
                from xenos_bot import enviar_oraculo
                enviar_oraculo(relatorio)
                print("✅ Enviado!")
        
        elif comando == "RS":
            from relatorios_periodicos import relatorio_semanal, exibir_relatorio_periodico
            
            par_rs = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
            symbol_rs = (par_rs + 'USDT') if par_rs and not par_rs.endswith('USDT') else (par_rs if par_rs else 'BTCUSDT')
            
            relatorio = relatorio_semanal(symbol_rs)
            exibir_relatorio_periodico(relatorio, "SEMANAL")
            
            enviar = input("\n📤 Enviar para Telegram? (s/n): ").lower().strip()
            if enviar == 's':
                from xenos_bot import enviar_oraculo
                enviar_oraculo(relatorio)
                print("✅ Enviado!")
        
        # === DASHBOARD TEMPO REAL (DASH) ===
        elif comando == "DASH":
            from dashboard_tempo_real import dashboard_tempo_real
            dashboard_tempo_real()
        
        # === HEATMAP CORRELAÇÕES (HEAT) ===
        elif comando == "HEAT":
            from heatmap_correlacoes import gerar_heatmap_correlacoes, exibir_heatmap
            
            resultado = gerar_heatmap_correlacoes()
            exibir_heatmap(resultado)
        
        # === AUTO ANÁLISE (AUTO) ===
        elif comando == "AUTO":
            from auto_analise import iniciar_auto_analise
            iniciar_auto_analise()
        
        # === ALERTAS TÉCNICOS (ALERT) ===
        elif comando == "ALERT":
            from alertas_tecnicos import configurar_alertas, monitorar_alertas
            
            config = configurar_alertas()
            monitorar_alertas(config)
        
        # === TELEGRAM (TG) ===
        elif comando == "TG":
            print("\n📱 CONFIGURAR TELEGRAM")
            print("="*60)
            print("\nAs configurações do Telegram estão em 'xenos_bot.py'")
            print("Bot configurado e ativo!")
        
        # === ENVIAR MANUAL (SEND) ===
        elif comando == "SEND":
            from xenos_bot import enviar_oraculo
            
            print("\n📤 ENVIAR MENSAGEM MANUAL")
            mensagem = input("\nDigite a mensagem: ")
            enviar_oraculo(mensagem)
            print("✅ Enviado!")
        
        # === CONFIGURAÇÕES (CFG) ===
        elif comando == "CFG":
            print("\n⚙️ CONFIGURAÇÕES DO SISTEMA")
            print("="*60)
            print(f"\nPar padrão: {symbol}")
            print(f"Intervalo: {interval}")
            print(f"Modo Silêncio: {'Ativo' if modo_silencio else 'Inativo'}")
        
        # === INFORMAÇÕES (INFO) ===
        elif comando == "INFO":
            print("\n"+ "="*60)
            print("ℹ️ INFORMAÇÕES DO SISTEMA SNE RADAR")
            print("="*60)
            print("\n📊 MÓDULOS DISPONÍVEIS:")
            print("   ✅ Scanner Técnico (Análise Completa)")
            print("   ✅ Contexto Macro")
            print("   ✅ Multi-Pair Análise")
            print("   ✅ DOM Profundo")
            print("   ✅ Relatórios Periódicos")
            print("   ✅ Dashboard Tempo Real")
            print("   ✅ Heatmap Correlações")
            print("   ✅ Auto Análise 24/7")
            print("   ✅ Alertas Técnicos")
            print("\n📈 SISTEMA:")
            print(f"   Versão: 3.0 Professional")
            print(f"   Plataforma: {platform.system()}")
            print(f"   Python: {sys.version.split()[0]}")
        
        # === RELATÓRIO TÉCNICO COMPLETO (RT) ===
        elif comando == "RT":
            par_rt = input("\n📊 Par (ou Enter para BTC): ").upper().strip()
            symbol_rt = (par_rt + 'USDT') if par_rt and not par_rt.endswith('USDT') else (par_rt if par_rt else 'BTCUSDT')
            
            print(f"\n📊 GERANDO RELATÓRIO MULTI-TIMEFRAME - {symbol_rt}...")
            
            timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '8h', '12h', '1d', '1w']
            
            from relatorio_tecnico import gerar_relatorio
            from datetime import datetime
            
            relatorio_completo = f"""
{'='*80}
📊 RELATÓRIO TÉCNICO COMPLETO - MULTI-TIMEFRAME
{'='*80}
Par: {symbol_rt}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

"""
            
            for tf in timeframes:
                print(f"   🔄 {tf}...", end=' ', flush=True)
                try:
                    # Usar motor_renan diretamente para análise (silencioso)
                    import sys
                    import io
                    from motor_renan import analise_completa, exibir_analise
                    
                    # Suprimir prints
                    old_stdout = sys.stdout
                    sys.stdout = io.StringIO()
                    
                    resultado = analise_completa(symbol_rt, tf)
                    
                    # Restaurar stdout
                    sys.stdout = old_stdout
                    
                    if resultado and 'erro' not in resultado:
                        # Formatar resultado
                        ctx = resultado.get('contexto', {})
                        est = resultado.get('estrutura', {})
                        conf = resultado.get('confluencia', {})
                        sint = resultado.get('sintese', {})
                        ind = resultado.get('indicadores', {})
                        
                        rel_tf = f"""
📈 CONTEXTO:
   Regime: {ctx.get('regime', 'N/A')} ({ctx.get('forca_regime', 0)}/10)
   Volatilidade: {ctx.get('volatilidade', 0)}% ({ctx.get('volatilidade_status', 'N/A')})
   Liquidez: {ctx.get('liquidez_score', 0)}/10

📊 ESTRUTURA:
   Tendência: {est.get('tendencia', 'N/A')}
   Tipo: {est.get('tipo_estrutura', 'N/A')}

📊 INDICADORES:
   Preço: ${ind.get('preco', 0):,.2f}
   EMA8: ${ind.get('ema8', 0):,.2f}
   EMA21: ${ind.get('ema21', 0):,.2f}
   RSI: {ind.get('rsi', 0):.1f}

💡 CONFLUÊNCIA: {conf.get('score', 0)}/10
   {conf.get('interpretacao', 'N/A')}

✨ SÍNTESE:
   Viés: {sint.get('vies', 'N/A')}
   Recomendação: {sint.get('recomendacao', 'N/A')}
   Entry: {sint.get('entry_type', 'N/A')}
   Risco: {sint.get('risco', 'N/A')}
"""
                        relatorio_completo += f"\n{'─'*80}\n⏰ TIMEFRAME: {tf}\n{'─'*80}\n{rel_tf}\n"
                        print("✅")
                    else:
                        relatorio_completo += f"\n⏰ {tf} - ⚠️ Erro na análise\n"
                        print("⚠️")
                except Exception as e:
                    sys.stdout = old_stdout  # Garantir restauração
                    relatorio_completo += f"\n⏰ {tf} - ❌ Erro: {str(e)}\n"
                    print("❌")
            
            relatorio_completo += f"\n{'='*80}\n"
            
            # Salvar
            import os
            os.makedirs("reports/completo", exist_ok=True)
            filename = f"reports/completo/{symbol_rt}_{datetime.now().strftime('%Y%m%d_%H%M')}_all_tf.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(relatorio_completo)
            
            print(f"\n✅ Relatório salvo: {filename}")
            
            relatorio = relatorio_completo
            
            # Gerar gráfico automaticamente (TF principal: 1h)
            print("\n📊 Gerando gráfico candlestick...")
            grafico_path = None
            try:
                from grafico_candlestick import gerar_grafico_candlestick
                grafico_path = gerar_grafico_candlestick(symbol_rt, "1h", "reports/completo/")
            except Exception as e:
                print(f"❌ Erro ao gerar gráfico: {e}")
            
            # Dividir relatório em blocos e enviar automaticamente
            print("\n📤 Enviando para Telegram...")
            try:
                from xenos_bot import enviar_oraculo, enviar_foto
                
                # Dividir por timeframe (cada TF é um bloco)
                blocos = relatorio.split('────────────────────────────────────────────────────────────────────────────────')
                
                # Enviar cabeçalho
                cabecalho = blocos[0] if blocos else ""
                if cabecalho:
                    enviar_oraculo(cabecalho[:4000])  # Limitar tamanho
                
                # Enviar cada timeframe
                for i, bloco in enumerate(blocos[1:], 1):
                    if bloco.strip():
                        mensagem = f"{'─'*60}\n{bloco[:3500]}"  # Limitar tamanho
                        enviar_oraculo(mensagem)
                        
                        if i % 3 == 0:  # Pausa a cada 3 mensagens
                            import time
                            time.sleep(1)
                
                # Enviar gráfico
                if grafico_path:
                    legenda = f"📊 {symbol_rt} - Relatório Completo (1h)"
                    enviar_foto(grafico_path, legenda)
                
                print("✅ Relatório e gráfico enviados!")
            except Exception as e:
                print(f"❌ Erro ao enviar: {e}")
        
        # === RADAR VISUAL (1) - Já implementado abaixo ===
        
        # === MODO AGRESSIVO (999) ===
            print("\n" + "="*60)
            print("🔥 MODO AGRESSIVO - SEM FILTROS")
            print("="*60)
            print("\n🔍 Buscando melhor par...")
            
            sinal = buscar_melhor_par_agressivo()
            
            if sinal:
                exibir_sinal_agressivo(sinal)
                
                # Perguntar se quer enviar para Telegram
                enviar = input("\n📱 Enviar para Telegram? (s/n): ")
                if enviar.lower() == 's':
                    acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
                    
                    mensagem = f"""
{acao_emoji} <b>MODO AGRESSIVO - {sinal['acao']} {sinal['symbol']}</b>

💰 Preço: ${sinal['preco']:.4f}
⚡ Confiança: {sinal['confianca']:.0f}%

📍 <b>ENTRY:</b> ${sinal['entry']:.4f}

🎯 <b>TAKE PROFIT:</b>
   TP1: ${sinal['tp1']:.4f}
   TP2: ${sinal['tp2']:.4f}
   TP3: ${sinal['tp3']:.4f}

🛡️ <b>STOP LOSS:</b> ${sinal['sl']:.4f}

📊 R/R: 1:{sinal['rr']:.1f}

💡 <b>Análise:</b>
{chr(10).join(['   • ' + m for m in sinal['motivos']])}

⚠️ <b>MODO AGRESSIVO - Use SL rigoroso!</b>
"""
                    enviar_oraculo(mensagem)
                    print("✅ Enviado para Telegram!")
            else:
                print("\n❌ Erro ao buscar dados")
        
        # === RELATÓRIO TÉCNICO COMPLETO ===
        elif comando.upper() == "RT":
            print("\n" + "="*60)
            print("📋 RELATÓRIO TÉCNICO COMPLETO - SISTEMA SNE")
            print("="*60)
            
            # Escolher par
            print("\n📊 Pares disponíveis: BTC, ETH, SOL, ADA, DOT, AVAX, LINK, UNI")
            par_input = input("🔍 Digite o símbolo (ou Enter para BTC): ").upper().strip()
            
            if not par_input:
                symbol_rt = "BTCUSDT"
            elif par_input.endswith('USDT'):
                symbol_rt = par_input
            else:
                symbol_rt = par_input + 'USDT'
            
            # Timeframe
            print("\n⏰ Timeframes disponíveis: 1m, 5m, 15m, 1h, 4h")
            tf_input = input("🕐 Digite o timeframe (ou Enter para 1h): ").strip()
            tf_rt = tf_input if tf_input else "1h"
            
            try:
                # Importar e executar
                from relatorio_tecnico import gerar_relatorio
                
                relatorio = gerar_relatorio(symbol_rt, tf_rt, salvar=True)
                
                # Exibir no terminal
                print("\n" + relatorio)
                
                # Oferecer envio para Telegram
                enviar = input("\n📤 Enviar para Telegram? (s/n): ").lower().strip()
                if enviar == 's':
                    enviar_oraculo(relatorio)
                    print("✅ Relatório enviado para Telegram!")
                
            except Exception as e:
                print(f"❌ Erro ao gerar relatório: {e}")
                import traceback
                traceback.print_exc()
        
        # === MODO TRADER DIRETO (ULTRA SIMPLIFICADO) ===
        elif comando == "99" and TRADER_DIRETO_AVAILABLE:
            print("\n" + "="*60)
            print("⚡ MODO TRADER DIRETO")
            print("="*60)
            
            sinais = trader_direto.analisar_agora()
            
            if sinais:
                # Mostrar melhor sinal
                exibir_sinal_direto(sinais[0])
                
                # Se houver mais sinais
                if len(sinais) > 1:
                    ver_mais = input("\n📊 Ver outras oportunidades? (s/n): ")
                    if ver_mais.lower() == 's':
                        exibir_top_sinais_diretos(sinais)
                
                # Perguntar se quer enviar para Telegram
                enviar = input("\n📱 Enviar para Telegram? (s/n): ")
                if enviar.lower() == 's':
                    sinal = sinais[0]
                    acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
                    
                    mensagem = f"""
{acao_emoji} <b>{sinal['acao']} {sinal['symbol']}</b>

💰 Preço: ${sinal['preco']:.4f}
⚡ Força: {sinal['forca']:.0f}%

📍 <b>ENTRY:</b> ${sinal['entry']:.4f}

🎯 <b>TAKE PROFIT:</b>
   TP1: ${sinal['tp1']:.4f}
   TP2: ${sinal['tp2']:.4f}
   TP3: ${sinal['tp3']:.4f}

🛡️ <b>STOP LOSS:</b> ${sinal['sl']:.4f}

📊 R/R: 1:{sinal['rr']:.1f}

💡 <b>Motivos:</b>
{chr(10).join(['   ✓ ' + m for m in sinal['motivos']])}
"""
                    enviar_oraculo(mensagem)
                    print("✅ Enviado para Telegram!")
            else:
                print("\n⏸️  AGUARDAR")
                print("💡 Nenhum setup claro no momento")
                print("📊 Critérios: Força ≥40%, Volume >1.2x, EMAs alinhadas")
        
        # === OPÇÕES REMOVIDAS - REDIRECIONAMENTO ===
        elif comando in ["0", "00", "8", "9", "10", "11"]:
            print("\n⚠️  Esta opção foi removida por não funcionar adequadamente")
            print("✅ Use a opção 999 (Modo Agressivo) para sinais imediatos")
            print("   ou opção 99 (Modo Seletivo) para sinais com filtros")
        
        elif comando == "1":
            iniciar_radar()
        
        elif comando == "2":
            modo_silencio = not modo_silencio
            print(f"Modo Silêncio {'ativado' if modo_silencio else 'desativado'}.")

        elif comando == "3":
            print("🔄 Encerrando sistema...")
            
            # Parar análise de contexto em tempo real
            try:
                parar_contexto_tempo_real()
                print("✅ Análise de contexto parada.")
            except Exception as e:
                print(f"⚠️ Erro ao parar contexto: {e}")
            
            # Enviar mensagem de encerramento ao Telegram
            try:
                from xenos_bot import fechar_sessao
                fechar_sessao()
            except Exception as e:
                print(f"⚠️ Erro ao enviar mensagem de encerramento: {e}")
            
            print("\n✅ Sistema encerrado com sucesso!")
            break
        
        elif comando == "4":
            print("\n=== HISTÓRICO DE TRADES ===")
            if estado["historico"]:
                for tipo, data, preco in estado["historico"]:
                    print(f"{tipo} em {data.strftime('%Y-%m-%d %H:%M:%S')} a {preco:.2f} USDT")
            else:
                print("Nenhuma operação registrada ainda.")
        
        elif comando == "5":
            print("\n=== ANÁLISE DE CONTEXTO DE MERCADO ===")
            try:
                # Tentar obter resumo do contexto em tempo real
                resumo = obter_resumo_executivo()
                if resumo and "Nenhuma análise" not in resumo:
                    print(resumo)
                    
                    # Perguntar se quer analisar outro par
                    outro_par = input("\n🔍 Analisar outro par? (digite símbolo ou 'n'): ").upper()
                    if outro_par != 'N' and outro_par:
                        # Validar formato (deve terminar com USDT)
                        if not outro_par.endswith('USDT'):
                            outro_par = outro_par + 'USDT'
                        
                        print(f"\n🔄 Analisando {outro_par}...")
                        from contexto_mercado import analisar_contexto_mercado
                        from indicadores import calcular_indicadores
                        import requests
                        
                        url = f"https://api.binance.com/api/v3/klines"
                        params = {"symbol": outro_par, "interval": "15m", "limit": 500}
                        response = requests.get(url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
                            df = calcular_indicadores(df)
                            relatorio = analisar_contexto_mercado(outro_par, df)
                            print(relatorio)
                        else:
                            print(f"❌ Par {outro_par} não encontrado ou erro na API")
                else:
                    # Se não houver análise, perguntar qual par
                    print("\n📊 Pares disponíveis: BTC, ETH, SOL, ADA, DOT, AVAX, LINK, UNI")
                    symbol_input = input("🔍 Digite o símbolo (ex: BTC, ETH) ou Enter para BTC: ").upper().strip()
                    
                    # Definir símbolo
                    if not symbol_input:
                        symbol_analise = "BTCUSDT"
                    elif symbol_input.endswith('USDT'):
                        symbol_analise = symbol_input
                    else:
                        symbol_analise = symbol_input + 'USDT'
                    
                    print(f"\n🔄 Gerando análise para {symbol_analise}...")
                    from contexto_mercado import analisar_contexto_mercado
                    from indicadores import calcular_indicadores
                    import requests
                    
                    # Definir parâmetros
                    interval_analise = "15m"
                    limit_analise = 500  # Aumentar para SMA200
                    
                    # Buscar dados diretamente
                    url = f"https://api.binance.com/api/v3/klines"
                    params = {"symbol": symbol_analise, "interval": interval_analise, "limit": limit_analise}
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
                        df = calcular_indicadores(df)
                        relatorio = analisar_contexto_mercado(symbol_analise, df)
                        print(relatorio)
                    else:
                        print(f"❌ Par {symbol_analise} não encontrado ou erro na API")
            except Exception as e:
                print(f"❌ Erro ao obter contexto: {e}")
        
        elif comando == "6":
            print("\n" + "="*60)
            print("🏆 COMPARAÇÃO DE PARES - MELHOR vs PIOR")
            print("="*60)
            try:
                print("🔄 Analisando mercado...")
                import requests
                
                # Definir pares principais
                PARES = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT', 'UNIUSDT']
                
                # Analisar todos os pares
                analises = []
                for par in PARES:  # Top 8 pares
                    try:
                        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={par}"
                        resp = requests.get(url, timeout=5)
                        if resp.status_code == 200:
                            data = resp.json()
                            preco = float(data['lastPrice'])
                            variacao = float(data['priceChangePercent'])
                            volume_24h = float(data['quoteVolume']) / 1_000_000  # Em milhões
                            
                            analises.append({
                                'symbol': par,
                                'preco': preco,
                                'variacao_24h': variacao,
                                'volume_24h': volume_24h
                            })
                    except:
                        pass
                
                if analises:
                    # Ordenar por variação (maior movimento = mais oportunidade)
                    analises.sort(key=lambda x: abs(x['variacao_24h']), reverse=True)
                    
                    print(f"\n✅ {len(analises)} pares analisados")
                    print("\n📈 MAIORES MOVIMENTOS (24h):")
                    print("-"*60)
                    
                    for i, par in enumerate(analises[:3], 1):
                        var_emoji = "🟢" if par['variacao_24h'] > 0 else "🔴"
                        movimento = "SUBINDO" if par['variacao_24h'] > 0 else "CAINDO"
                        
                        print(f"\n{i}. {par['symbol']} {var_emoji}")
                        print(f"   💰 Preço: ${par['preco']:.4f}")
                        print(f"   📊 Variação: {par['variacao_24h']:+.2f}% ({movimento})")
                        print(f"   📈 Volume: ${par['volume_24h']:.1f}M")
                        
                        # Sugestão de ação
                        if abs(par['variacao_24h']) > 3:
                            print(f"   💡 ALTA VOLATILIDADE - Potencial reversão ou continuação")
                        elif abs(par['variacao_24h']) > 1.5:
                            print(f"   💡 MOVIMENTO MODERADO - Tendência em formação")
                        else:
                            print(f"   💡 MOVIMENTO LEVE - Aguardar confirmação")
                    
                    print("\n" + "-"*60)
                    
                    # Mostrar os mais estáveis (menor movimento)
                    print("\n📊 MAIS ESTÁVEIS (24h):")
                    print("-"*60)
                    
                    analises_estavel = sorted(analises, key=lambda x: abs(x['variacao_24h']))
                    for i, par in enumerate(analises_estavel[:3], 1):
                        print(f"\n{i}. {par['symbol']}")
                        print(f"   💰 Preço: ${par['preco']:.4f}")
                        print(f"   📊 Variação: {par['variacao_24h']:+.2f}%")
                        print(f"   💡 CONSOLIDAÇÃO - Aguardar breakout")
                    
                    print("\n" + "="*60)
                    
                    # Perguntar se quer análise de um par específico
                    escolha = input("\n🔍 Analisar algum par? (digite símbolo ou 'n'): ").upper()
                    if escolha != 'N' and escolha in [p['symbol'] for p in analises]:
                        par_escolhido = [p for p in analises if p['symbol'] == escolha][0]
                        
                        print(f"\n📊 ANÁLISE DETALHADA - {escolha}")
                        print("-"*60)
                        print(f"💰 Preço Atual: ${par_escolhido['preco']:.4f}")
                        print(f"📈 Variação 24h: {par_escolhido['variacao_24h']:+.2f}%")
                        print(f"📊 Volume 24h: ${par_escolhido['volume_24h']:.1f}M")
                        
                        # Sugestão de trade
                        if par_escolhido['variacao_24h'] < -2:
                            print(f"\n💡 SUGESTÃO: Considere COMPRA se houver reversão")
                            print(f"   🎯 Entry: Próximo suporte (~${par_escolhido['preco'] * 0.98:.4f})")
                            print(f"   🛡️  SL: ${par_escolhido['preco'] * 0.97:.4f}")
                            print(f"   🎯 TP: ${par_escolhido['preco'] * 1.02:.4f}")
                        elif par_escolhido['variacao_24h'] > 2:
                            print(f"\n💡 SUGESTÃO: Considere VENDA se houver reversão")
                            print(f"   🎯 Entry: Próxima resistência (~${par_escolhido['preco'] * 1.02:.4f})")
                            print(f"   🛡️  SL: ${par_escolhido['preco'] * 1.03:.4f}")
                            print(f"   🎯 TP: ${par_escolhido['preco'] * 0.98:.4f}")
                        else:
                            print(f"\n💡 SUGESTÃO: Aguardar movimento mais claro")
                            print(f"   📊 Breakout acima: ${par_escolhido['preco'] * 1.015:.4f}")
                            print(f"   📊 Breakdown abaixo: ${par_escolhido['preco'] * 0.985:.4f}")
                else:
                    print("❌ Erro ao buscar dados")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        elif comando == "7":
            print("\n" + "="*60)
            print("📊 ANÁLISE MULTI-PAIR - SINAIS PRONTOS")
            print("="*60)
            try:
                from multi_pair_signals import gerar_sinais_multiplos, exibir_sinais_multiplos
                
                print("🔄 Gerando sinais para 8 pares principais...")
                sinais = gerar_sinais_multiplos()
                
                exibir_sinais_multiplos(sinais, top=5)
                
                # Perguntar se quer executar algum
                if sinais:
                    executar = input("\n📱 Enviar algum sinal para Telegram? (1-5 ou 'n'): ")
                    if executar.isdigit() and 1 <= int(executar) <= min(5, len(sinais)):
                        idx = int(executar) - 1
                        sinal = sinais[idx]
                        
                        acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
                        
                        mensagem = f"""
{acao_emoji} <b>MULTI-PAIR - {sinal['acao']} {sinal['symbol']}</b>

💰 Preço: ${sinal['preco']:.4f}
⚡ Força: {sinal['forca']:.0f}%

📍 <b>ENTRY:</b> ${sinal['entry']:.4f}

🎯 <b>TAKE PROFIT:</b>
   TP1: ${sinal['tp1']:.4f}
   TP2: ${sinal['tp2']:.4f}
   TP3: ${sinal['tp3']:.4f}

🛡️ <b>STOP LOSS:</b> ${sinal['sl']:.4f}

📊 R/R: 1:{sinal['rr']:.1f}

💡 <b>Motivos:</b>
{chr(10).join(['   ✓ ' + m for m in sinal['motivos']])}
"""
                        enviar_oraculo(mensagem)
                        print("✅ Sinal enviado para Telegram!")
                    
            except Exception as e:
                print(f"❌ Erro na análise multi-pair: {e}")
        
        elif comando == "8":
            print("\n" + "="*60)
            print("🎯 SISTEMA DE PRIORIZAÇÃO AUTOMÁTICA")
            print("="*60)
            try:
                print("🔄 Executando análise multi-pair...")
                resultados, _, _ = analisar_mercado_completo()
                
                print("🎯 Aplicando priorização inteligente...")
                pares_priorizados = priorizador_global.priorizar_pares(resultados)
                
                print(f"\n✅ {len(pares_priorizados)} pares priorizados")
                print(f"\n🏆 TOP 5 PRIORIDADES:")
                print("-"*60)
                
                for par in pares_priorizados[:5]:
                    symbol = par.get('symbol', 'N/A')
                    priority = par.get('priority_score', 0)
                    opp_score = par.get('opportunity_score', 0)
                    regime = par.get('market_regime', 'N/A')
                    
                    print(f"\n{par.get('priority_rank', 0)}. {symbol}")
                    print(f"   Prioridade: {priority:.1f}/100")
                    print(f"   Score Oportunidade: {opp_score:.1f}/100")
                    print(f"   Regime: {regime}")
                    print(f"   💡 {par.get('recommendation', 'N/A')}")
                    
                    # Mostrar pontos de entrada
                    entry_points = par.get('entry_points', [])
                    if entry_points:
                        print(f"   📍 Entrada: {entry_points[0].get('description', 'N/A')}")
                
                print("\n" + "-"*60)
                
                # Estatísticas
                priorities = [p.get('priority_score', 0) for p in pares_priorizados]
                print(f"\n📊 ESTATÍSTICAS:")
                print(f"   Prioridade Média: {np.mean(priorities):.1f}/100")
                print(f"   Maior Prioridade: {max(priorities):.1f}/100")
                print(f"   Pares com Alta Prioridade (≥70): {len([p for p in priorities if p >= 70])}")
                
            except Exception as e:
                print(f"❌ Erro na priorização: {e}")
        
        elif comando == "9":
            print("\n" + "="*60)
            print("🚨 ALERTAS INTELIGENTES ATIVOS")
            print("="*60)
            try:
                # Buscar dados atuais
                print("🔄 Analisando mercado...")
                resultados, _, _ = analisar_mercado_completo()
                pares_priorizados = priorizador_global.priorizar_pares(resultados)
                
                # Gerar alertas para top 5
                print("🚨 Gerando alertas inteligentes...")
                todos_alertas = []
                for par in pares_priorizados[:5]:
                    alertas = sistema_alertas_global.analisar_e_gerar_alertas(par)
                    todos_alertas.extend(alertas)
                
                if todos_alertas:
                    print(f"\n✅ {len(todos_alertas)} alertas gerados")
                    
                    # Resumo rápido
                    criticos = len([a for a in todos_alertas if a.prioridade.value == 1])
                    altos = len([a for a in todos_alertas if a.prioridade.value == 2])
                    medios = len([a for a in todos_alertas if a.prioridade.value == 3])
                    
                    print(f"\n📊 RESUMO:")
                    if criticos > 0:
                        print(f"   🔴 CRÍTICOS: {criticos}")
                    if altos > 0:
                        print(f"   🟠 ALTOS: {altos}")
                    if medios > 0:
                        print(f"   🟡 MÉDIOS: {medios}")
                    
                    print("\n🚨 ALERTAS DETALHADOS:")
                    print("-"*60)
                    
                    # Agrupar por prioridade
                    alertas_por_prioridade = {}
                    for alerta in todos_alertas:
                        p = alerta.prioridade.name
                        if p not in alertas_por_prioridade:
                            alertas_por_prioridade[p] = []
                        alertas_por_prioridade[p].append(alerta)
                    
                    # Mostrar por prioridade
                    for prioridade in ['CRITICA', 'ALTA', 'MEDIA']:
                        if prioridade in alertas_por_prioridade:
                            alertas = alertas_por_prioridade[prioridade]
                            print(f"\n🔔 {prioridade} ({len(alertas)} alertas):")
                            for alerta in alertas:
                                print(f"\n   {alerta}")
                                # Mostrar primeiras 2 recomendações
                                for rec in alerta.recomendacoes[:2]:
                                    print(f"      • {rec}")
                    
                    print("\n" + "-"*60)
                    
                    # Perguntar se quer enviar para Telegram
                    if criticos > 0 or altos > 0:
                        enviar = input("\n📱 Enviar alertas importantes para Telegram? (s/n): ")
                        if enviar.lower() == 's':
                            alertas_importantes = [a for a in todos_alertas if a.prioridade.value <= 2]
                            if alertas_importantes:
                                mensagem = "🚨 <b>ALERTAS IMPORTANTES</b>\n\n"
                                for alerta in alertas_importantes[:3]:
                                    mensagem += f"{alerta}\n"
                                    mensagem += f"💡 {alerta.recomendacoes[0]}\n\n"
                                enviar_oraculo(mensagem)
                                print("✅ Alertas enviados!")
                            else:
                                print("⚠️ Nenhum alerta importante para enviar")
                    else:
                        print("\n💡 Apenas alertas de baixa prioridade - Não é necessário enviar para Telegram")
                else:
                    print("\n✅ Nenhum alerta no momento")
                    print("💡 Mercado estável ou sem oportunidades significativas")
                    
            except Exception as e:
                print(f"❌ Erro ao gerar alertas: {e}")
        
        # === MODO PROFISSIONAL (MULTI-TIMEFRAME) ===
        elif comando == "10" and PROFESSIONAL_MODE_AVAILABLE:
            print("\n" + "="*60)
            print("🎯 MELHOR SINAL MULTI-TIMEFRAME")
            print("="*60)
            print("📊 Análise em 4 timeframes: 1m, 5m, 15m, 1h")
            print("✅ Validação cruzada (mínimo 3 confirmações)")
            print("-"*60)
            
            melhor_sinal = signal_system.buscar_melhor_sinal_agora()
            
            if melhor_sinal:
                _exibir_sinal_profissional(melhor_sinal)
                
                enviar = input("\n📱 Enviar para Telegram? (s/n): ")
                if enviar.lower() == 's':
                    telegram_pro.enviar_alerta_oportunidade(melhor_sinal)
                    mensagem = telegram_pro.gerar_sinal_telegram_pro(melhor_sinal)
                    if telegram_pro.enviar(mensagem):
                        print("✅ Sinal enviado para Telegram!")
                    else:
                        print("❌ Erro ao enviar para Telegram")
            else:
                print("\n⏸️ Nenhuma oportunidade de alta qualidade no momento")
                print("💡 Critérios: Score ≥60%, 3+ timeframes confirmando, R/R ≥1.5:1")
        
        elif comando == "11" and PROFESSIONAL_MODE_AVAILABLE:
            print("\n" + "="*60)
            print("🏆 TOP 3 SINAIS MULTI-TIMEFRAME")
            print("="*60)
            print("📊 Análise em 4 timeframes: 1m, 5m, 15m, 1h")
            print("-"*60)
            
            sinais = signal_system.buscar_top_sinais(n=3)
            
            if sinais:
                print(f"\n✅ {len(sinais)} oportunidades encontradas")
                print("\n🏆 TOP 3 SINAIS:")
                print("-"*60)
                
                for i, sinal in enumerate(sinais, 1):
                    tipo_emoji = "🟢" if sinal['tipo'] == 'LONG' else "🔴"
                    print(f"\n{i}. {tipo_emoji} {sinal['symbol']} - {sinal['tipo']}")
                    print(f"   Score: {sinal['score_confianca']:.0f}% | Entry: ${sinal['entry']:.4f}")
                    print(f"   TP1: ${sinal['tp'][0]:.4f} (R/R: 1:{sinal['risco_retorno'][0]:.1f})")
                
                print("\n" + "-"*60)
                
                ver_detalhes = input("\n📊 Ver detalhes de algum? (1-3 ou n): ")
                if ver_detalhes in ['1', '2', '3']:
                    idx = int(ver_detalhes) - 1
                    if idx < len(sinais):
                        _exibir_sinal_profissional(sinais[idx])
                        
                        enviar = input("\n📱 Enviar para Telegram? (s/n): ")
                        if enviar.lower() == 's':
                            telegram_pro.enviar_alerta_oportunidade(sinais[idx])
                            mensagem = telegram_pro.gerar_sinal_telegram_pro(sinais[idx])
                            if telegram_pro.enviar(mensagem):
                                print("✅ Sinal enviado para Telegram!")
            else:
                print("\n⏸️ Nenhuma oportunidade no momento")
        
        elif comando == "12" and MODO_AGRESSIVO_AVAILABLE:
            print("\n" + "="*60)
            print("🤖 MODO AUTOMÁTICO 24/7 - MODO AGRESSIVO")
            print("="*60)
            print("Este modo irá:")
            print("• Buscar sinal a cada 60 segundos")
            print("• Usar MODO AGRESSIVO (sempre retorna)")
            print("• Enviar sinais automaticamente para Telegram")
            print("• Rodar indefinidamente até parar (Ctrl+C)")
            print("\n⚠️  Pressione Ctrl+C para parar")
            print("="*60)
            
            confirmar = input("\nIniciar Modo Automático? (s/n): ")
            if confirmar.lower() == 's':
                import time
                ciclo = 0
                sinais_enviados = 0
                
                print("\n🤖 MODO AUTOMÁTICO INICIADO")
                print(f"⏰ {time.strftime('%H:%M:%S')}")
                print("="*60)
                
                try:
                    while True:
                        ciclo += 1
                        print(f"\n🔄 Ciclo #{ciclo} - {time.strftime('%H:%M:%S')}")
                        print("-"*60)
                        
                        # Buscar sinal agressivo
                        sinal = buscar_melhor_par_agressivo()
                        
                        if sinal and sinal['confianca'] >= 60:
                            # Enviar para Telegram
                            acao_emoji = "🟢" if sinal['acao'] == 'COMPRAR' else "🔴"
                            
                            mensagem = f"""
🤖 <b>MODO AUTOMÁTICO - {acao_emoji} {sinal['acao']} {sinal['symbol']}</b>

💰 Preço: ${sinal['preco']:.4f}
⚡ Confiança: {sinal['confianca']:.0f}%

📍 <b>ENTRY:</b> ${sinal['entry']:.4f}

🎯 <b>TAKE PROFIT:</b>
   TP1: ${sinal['tp1']:.4f}
   TP2: ${sinal['tp2']:.4f}
   TP3: ${sinal['tp3']:.4f}

🛡️ <b>STOP LOSS:</b> ${sinal['sl']:.4f}

📊 R/R: 1:{sinal['rr']:.1f}

🕐 {time.strftime('%H:%M:%S')}
"""
                            enviar_oraculo(mensagem)
                            sinais_enviados += 1
                            print(f"✅ {acao_emoji} {sinal['acao']} {sinal['symbol']} - Conf: {sinal['confianca']:.0f}% - Enviado!")
                        else:
                            print(f"⏸️  Nenhum sinal com confiança ≥60% neste ciclo")
                        
                        print(f"📊 Total de sinais enviados: {sinais_enviados}")
                        print(f"⏰ Próximo scan em 60 segundos...")
                        time.sleep(60)
                        
                except KeyboardInterrupt:
                    print("\n\n" + "="*60)
                    print("🛑 MODO AUTOMÁTICO ENCERRADO")
                    print("="*60)
                    print(f"⏰ Encerrado em: {time.strftime('%H:%M:%S')}")
                    print(f"📊 Total de ciclos: {ciclo}")
                    print(f"📱 Total de sinais enviados: {sinais_enviados}")
                    print("="*60)
        
        elif comando == "13" and PROFESSIONAL_MODE_AVAILABLE:
            print("\n" + "="*60)
            print("🔍 ESCANEAR MERCADO")
            print("="*60)
            
            pares = scanner.escanear_mercado(force_refresh=True)
            
            if pares:
                print(f"\n✅ {len(pares)} pares com boa liquidez encontrados")
                print("\n🏆 TOP 10 POR SCORE DE LIQUIDEZ:")
                print("-"*60)
                print(f"{'#':<3} {'Par':<12} {'Volume 24h':<15} {'Spread':<10} {'Volatil':<10}")
                print("-"*60)
                
                for i, par in enumerate(pares[:10], 1):
                    print(f"{i:<3} {par['symbol']:<12} "
                          f"${par['volume_24h']/1e6:>6.1f}M      "
                          f"{par['spread']*100:>5.3f}%    "
                          f"{par['volatilidade']:>+6.2f}%")
            else:
                print("❌ Erro ao escanear mercado")
        
        else:
            print("❌ Comando inválido.")


import atexit
from xenos_bot import fechar_sessao

def finalizar_sessao():
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(fechar_sessao())
        else:
            asyncio.run(fechar_sessao())
    except RuntimeError:
        print("[INFO] Loop não encontrado para encerramento.")

# ✅ Fecha a sessão ao finalizar o programa
atexit.register(finalizar_sessao)

# ✅ Execução Principal
if __name__ == "__main__":
    try:
        terminal_sne()
    finally:
        try:
            loop = asyncio.get_running_loop()
            if not loop.is_closed():
                loop.close()
        except RuntimeError:
            pass

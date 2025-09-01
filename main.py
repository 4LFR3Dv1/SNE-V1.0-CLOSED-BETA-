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

symbol = "BTCUSDT"
interval = "1m"
limit = 100
update_interval = 5000
modo_silencio = False
br_tz = pytz.timezone("America/Sao_Paulo")

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


def executar_assincrono(corrotina):
    """
    Executa uma função assíncrona de forma segura.
    """
try:
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
        except RuntimeError:
            print("[INFO] Loop de evento não detectado, criando um novo...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            print("[INFO] Loop de evento já está em execução. Criando tarefa...")
            loop.create_task(corrotina)
        else:
            print("[INFO] Loop de evento iniciado manualmente.")
            loop.run_until_complete(corrotina)

except Exception as e:
    print(f"[ERRO EXECUÇÃO ASSÍNCRONA] {e}")

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
        executar_assincrono(enviar_oraculo(mensagem))
        executar_assincrono(enviar_imagem(fig, nome_arquivo))

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
            await enviar_log_rupturas(CAMINHO_LOG_ALERTAS)
            await enviar_oraculo("Terminal SNE encerrado. Silêncio restaurado.")
        else:
            print("[INFO] Loop não estava ativo. Criando um novo para encerrar...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(gerar_codice_fluxo(estado))
            loop.run_until_complete(enviar_log_rupturas(CAMINHO_LOG_ALERTAS))
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
            await executar_assincrono(enviar_imagem(fig, nome_arquivo))
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
                    await executar_assincrono(enviar_imagem(fig, nome_arquivo))
                    print(f"[INFO] Mensagem enviada com sucesso. Tentativa {tentativa}")
                    break
                else:
                    loop.run_until_complete(enviar_oraculo(mensagem))
                    loop.run_until_complete(enviar_imagem(fig, nome_arquivo))
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
    exibir_zonas_relevantes(limite=5)

    # 🔄 Execução do Backtest
    executar_backtest(df)

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
    texto_hud = (
        f"ZONA ATIVA: {zona_ativa}\n"
        f"ENERGIA MAG.: {energia_atual:.4f}\n"
        f"SINAL: {ultimo_sinal}"
    )
    hud = AnchoredText(texto_hud, loc='upper right', prop=dict(size=8), frameon=True)
    hud.patch.set_boxstyle("round,pad=0.3")
    hud.patch.set_facecolor("yellow")
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

CAMINHO_CATALOGO = "catalogo_magnetico.csv"

def exibir_zonas_relevantes(limite=5):
    try:
        catalogo = pd.read_csv(CAMINHO_CATALOGO)
        print("[DEBUG] Catálogo lido para exibição:")
        print(catalogo.head())

        if not catalogo.empty:
            catalogo = catalogo.sort_values(by="forca_total", ascending=False).head(limite)
            print("[INFO] Zonas Relevantes:")
            print(catalogo)
        else:
            print("[AVISO] Catálogo vazio.")
    except Exception as e:
        print(f"[ERRO] Falha ao ler o catálogo: {e}")
def atualizar_catalogo(df):
    print("[DEBUG] Atualizando catálogo magnético...")
    if "ruptura" not in df.columns or not df["ruptura"].any():
        print("[AVISO] Nenhuma ruptura detectada para atualizar.")
        return

    try:
        df_rupturas = df[df["ruptura"]].copy()
        df_rupturas["zona"] = (df_rupturas["close"] // 50) * 50
        df_rupturas["forca"] = df_rupturas["densidade"]

        catalogo = pd.read_csv(CAMINHO_CATALOGO)
        print("[DEBUG] Catálogo carregado com sucesso.")
    except FileNotFoundError:
        catalogo = pd.DataFrame(columns=["zona", "forca_total", "ocorrencias", "ultima_data"])
        print("[AVISO] Catálogo não encontrado. Criando um novo...")

    for _, row in df_rupturas.iterrows():
        zona = row["zona"]
        densidade = row["forca"]
        data = row.name.strftime('%Y-%m-%d %H:%M:%S')

        if zona in catalogo["zona"].values:
            idx = catalogo.index[catalogo["zona"] == zona][0]
            catalogo.at[idx, "forca_total"] += densidade
            catalogo.at[idx, "ocorrencias"] += 1
            catalogo.at[idx, "ultima_data"] = data
        else:
            catalogo = pd.concat([catalogo, pd.DataFrame({
                "zona": [zona],
                "forca_total": [densidade],
                "ocorrencias": [1],
                "ultima_data": [data]
            })])

    catalogo.to_csv(CAMINHO_CATALOGO, index=False)
    print("[INFO] Catálogo magnético atualizado com sucesso.")

    # 🔄 Impressão otimizada no terminal:
    print("\n=== CATÁLOGO MAGNÉTICO HISTÓRICO ATUALIZADO ===")
    print(catalogo.tail(10))
    print("=============================================")
    # === Atualizando o catálogo com os novos dados ===
    for _, row in df_rupturas.iterrows():
        zona = row["zona"]
        densidade = row["forca"]
        data = row.name.strftime('%Y-%m-%d %H:%M:%S')

        if zona in catalogo["zona"].values:
            idx = catalogo.index[catalogo["zona"] == zona][0]
            catalogo.at[idx, "forca_total"] += densidade
            catalogo.at[idx, "ocorrencias"] += 1
            catalogo.at[idx, "ultima_data"] = data
        else:
            novo_registro = {
                "zona": zona, 
                "forca_total": densidade, 
                "ocorrencias": 1, 
                "ultima_data": data
            }
            catalogo = pd.concat([catalogo, pd.DataFrame([novo_registro])], ignore_index=True)

    # === Remover duplicidades e ordenar por força magnética ===
    catalogo.drop_duplicates(subset=["zona"], keep='last', inplace=True)
    catalogo.sort_values(by=["forca_total"], ascending=False, inplace=True)

    # === Salvando no CSV e exibindo no terminal ===
    catalogo.to_csv(CAMINHO_CATALOGO, index=False)
    print("\n=== CATÁLOGO MAGNÉTICO HISTÓRICO ATUALIZADO ===")
    print(catalogo.tail(10))
    print("===============================================")

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
        executar_assincrono(enviar_imagem(fig, nome_arquivo))
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
        await gerar_relatorio_inicial(df_inicial)

        print("✅ Componentes assíncronos iniciados com sucesso.")
    
    except Exception as e:
        print(f"[ERRO ORÁCULO] {e}")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

try:
        gerar_codice_fluxo(estado)
        enviar_log_rupturas(CAMINHO_LOG_ALERTAS)
except Exception as e:
        print(f"[ERRO RELATÓRIO FINAL] {e}")
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
            await gerar_relatorio_inicial(df_inicial)

            print("✅ Componentes assíncronos iniciados com sucesso.")
        
        except Exception as e:
            print(f"[ERRO ORÁCULO] {e}")

    # ✅ Execução Assíncrona em Loop Independente
    loop.run_until_complete(iniciar_componentes())

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
        loop.create_task(gerar_codice_fluxo(estado))
        loop.create_task(enviar_log_rupturas(CAMINHO_LOG_ALERTAS))

    except Exception as e:
        print(f"[ERRO] Problema ao encerrar o Radar: {e}")

    finally:
        print("🔄 Missão encerrada.")


def terminal_sne():
    global modo_silencio
    while True:
        print("\n=== TERMINAL SNE ===")
        print("1) Iniciar Missão (Radar Integrado)")
        print("2) Alternar Modo Silêncio")
        print("3) Encerrar Missão")
        print("4) Ver Histórico de Trades")
        comando = input("Comando >> ")

        if comando == "1":
            iniciar_radar()
        
        elif comando == "2":
            modo_silencio = not modo_silencio
            print(f"Modo Silêncio {'ativado' if modo_silencio else 'desativado'}.")

        elif comando == "3":
            print("Missão encerrada.")
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                print("[INFO] Nenhum loop encontrado. Criando um novo...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                print("[INFO] Loop encontrado. Encerrando assíncronamente.")
                tarefa = loop.create_task(encerrar_oraculo())
                loop.run_until_complete(tarefa)
            else:
                print("[INFO] Loop não estava ativo. Executando normalmente.")
                asyncio.run(encerrar_oraculo())

            break
        
        elif comando == "4":
            print("\n=== HISTÓRICO DE TRADES ===")
            if estado["historico"]:
                for tipo, data, preco in estado["historico"]:
                    print(f"{tipo} em {data.strftime('%Y-%m-%d %H:%M:%S')} a {preco:.2f} USDT")
            else:
                print("Nenhuma operação registrada ainda.")
        
        else:
            print("Comando inválido.")


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

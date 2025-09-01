import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
from datetime import datetime

# === CONFIGURAÇÕES ===
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 100
URL = "https://api.binance.com/api/v3/klines"

# ✅ Função para buscar dados em tempo real da Binance
def buscar_dados(symbol=SYMBOL, interval=INTERVAL, limit=LIMIT):
    print("[SNE] 🔄 Buscando dados da Binance...")
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(URL, params=params, timeout=10)
    data = r.json()
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tbb", "tbq", "ignore"
    ])
    df["time"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df[["time", "open", "high", "low", "close", "volume"]].astype(float)
    df["timestamp"] = mdates.date2num(pd.to_datetime(df["time"]))
    df.set_index("time", inplace=True)
    print("[SNE] ✅ Dados carregados com sucesso.")
    return df

# ✅ Função para detectar rupturas gravitacionais
def detectar_rupturas(df):
    """
    Detecta rupturas magnéticas no DataFrame e adiciona a coluna 'ruptura'.
    """
    print("[SNE] 🔎 Detectando rupturas gravitacionais...")

    # Calcula as médias móveis necessárias
    df["EMA8"] = df["close"].ewm(span=8).mean()
    df["EMA21"] = df["close"].ewm(span=21).mean()
    df["SMA200"] = df["close"].rolling(window=20).mean()
    
    # Calcula a densidade magnética
    df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)

    # === Detecção das rupturas ===
    rupturas = df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.97)
    
    # === Verificação de volume para validar ruptura ===
    df["ruptura"] = rupturas & (df["volume"] > df["volume"].quantile(0.7))

    print(f"[SNE] ✅ {df['ruptura'].sum()} rupturas detectadas.")
    return df

# ✅ Função para mapear zonas críticas
def detectar_zonas_criticas(df):
    """
    Detecta zonas críticas baseadas em rupturas magnéticas.
    """
    print("[SNE] 🌌 Mapeando Zonas Críticas...")

    # ✅ Verifica se a coluna "ruptura" existe
    if "ruptura" not in df.columns:
        print("[ERRO] Coluna 'ruptura' não encontrada no DataFrame.")
        return [], []

    # 🔄 Filtra apenas os pontos de ruptura
    rupturas = df[df["ruptura"]]

    # ✅ Cria uma lista de dicionários com os dados essenciais
    zonas_criticas = [
        {
            "preco": row["close"],
            "volume": row["volume"],
            "timestamp": idx
        }
        for idx, row in rupturas.iterrows()
    ]

    # ✅ Simulação de canais para retorno (pode ser aprimorado)
    canais_mapeados = [{"inicio": zona["timestamp"], "fim": zona["timestamp"] + pd.Timedelta(minutes=5)} for zona in zonas_criticas]

    print(f"[SNE] ✅ Total de Zonas Críticas Detectadas: {len(zonas_criticas)}")
    return zonas_criticas, canais_mapeados

# ✅ Função para exportar o relatório visual e texto
def exportar_analise(df, nome_base="mapeamento_gravitacional"):
    print("[SNE] 📊 Exportando análise visual e relatório...")

    # Plot do gráfico
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df.index, df["close"], label="Preço", color="gray", linewidth=1)
    ax.plot(df.index, df["EMA8"], label="EMA8", linestyle="--", color="blue", alpha=0.6)
    ax.plot(df.index, df["EMA21"], label="EMA21", linestyle="--", color="orange", alpha=0.6)
    ax.plot(df.index, df["SMA200"], label="SMA200", linestyle="--", color="red", alpha=0.5)

    # Marcações de ruptura
    rupturas = df[df["ruptura"]]
    for i in rupturas.index:
        ax.axvline(x=i, color="yellow", linestyle="--", alpha=0.6)

    ax.set_title("Mapeamento Gravitacional com Rupturas")
    ax.set_ylabel("Preço")
    ax.legend()
    plt.tight_layout()

    # Caminhos de arquivo
    caminho_img = f"{nome_base}_visual.png"
    caminho_txt = f"{nome_base}_analise.txt"
    
    # Salva o gráfico
    fig.savefig(caminho_img)

    # Salva as zonas de ruptura
    rupturas_str = [f"{i.strftime('%Y-%m-%d %H:%M:%S')} - {df.loc[i]['close']:.2f}" for i in rupturas.index]
    with open(caminho_txt, "w") as f:
        f.write("=== ZONAS DE RUPTURA DETECTADAS ===\n")
        f.write("\n".join(rupturas_str))
        f.write(f"\n\nTotal de rupturas: {len(rupturas)}")

    print(f"[SNE] ✅ Exportação realizada: {caminho_img} e {caminho_txt}")

# ✅ Função principal de execução
def executar_mapeamento_gravitacional():
    print("[SNE] 🚀 Executando Mapeamento Gravitacional...")
    df = buscar_dados()
    df = detectar_rupturas(df)
    zonas = mapear_zonas_criticas(df)
    exportar_analise(df)
    print("[SNE] 🌌 Mapeamento Gravitacional Finalizado.")
    return zonas
def detectar_rupturas(df):
    """
    Detecta rupturas magnéticas no DataFrame e adiciona a coluna 'ruptura'.
    """
    print("[SNE] 🔎 Detectando rupturas gravitacionais...")

    # Calcula as médias móveis necessárias
    df["EMA8"] = df["close"].ewm(span=8).mean()
    df["EMA21"] = df["close"].ewm(span=21).mean()
    df["SMA200"] = df["close"].rolling(window=20).mean()
    
    # Calcula a densidade magnética
    df["densidade"] = 1 / (abs(df["EMA8"] - df["EMA21"]) + abs(df["EMA21"] - df["SMA200"]) + 1e-6)

    # Detecção das rupturas
    rupturas = df["densidade"].diff().abs() > df["densidade"].diff().abs().quantile(0.97)
    df["ruptura"] = rupturas & (df["volume"] > df["volume"].quantile(0.9))

    print(f"[SNE] ✅ {df['ruptura'].sum()} rupturas detectadas.")
    return df
def gerar_grafico_zonas(df, zonas):
    """
    Gera um gráfico visual destacando as zonas críticas.
    """
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['close'], label='Preço', color='gray')
    
    for zona in zonas:
        plt.axvline(x=zona['timestamp'], color='red', linestyle='--')
    
    plt.title('Zonas Críticas Mapeadas')
    plt.legend()
    plt.savefig('mapeamento_zonas.png')
    plt.close()
    print("[SNE] ✅ Gráfico das Zonas Críticas gerado com sucesso.")

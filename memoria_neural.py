import os
from datetime import datetime
import pytz
import pandas as pd

# === Configurações ===
zona = pytz.timezone("America/Sao_Paulo")
caminho_log = "sne_registro_mental.txt"
caminho_memoria = "sne_memoria_neural.txt"
memoria_mercado = []  # Memória neural em tempo real

# ✅ Verifica Ressonância com o passado
def mente_fluidica_verificar_resonancia(preco_atual, timestamp_atual, densidade_atual=None):
    memoria = []

    if not os.path.exists(caminho_log):
        return

    with open(caminho_log, "r") as f:
        for linha in f:
            if "Ruptura detectada em" in linha:
                try:
                    hora_raw = linha.split("]")[0].replace("[", "").strip()
                    hora = datetime.strptime(hora_raw, "%Y-%m-%d %H:%M:%S.%f")
                    hora = zona.localize(hora)
                    preco = float(linha.split("em")[1].replace("USDT", "").strip())
                    memoria.append((hora, preco))
                except Exception as e:
                    print(f"[ERRO] Falha ao processar ressonância: {e}")
                    continue

    if timestamp_atual.tzinfo is None:
        timestamp_atual = zona.localize(timestamp_atual)

    for mem_hora, mem_preco in memoria:
        if mem_hora.tzinfo is None:
            mem_hora = zona.localize(mem_hora)

        delta = abs((timestamp_atual - mem_hora).total_seconds())
        if delta < 300:
            if abs(mem_preco - preco_atual) / preco_atual < 0.01:
                print("[RESSONÂNCIA] O campo pulsa em sincronia com uma memória ancestral.")
                with open(caminho_memoria, "a") as f:
                    f.write(f"[{datetime.now(tz=zona)}] Ressonância detectada com ruptura de {mem_preco:.2f} em {mem_hora}\n")
                break

# ✅ Classifica a Intensidade das Rupturas
def classificar_memoria(preco_atual, timestamp_atual, densidade_atual=None):
    """
    Retorna True se a ruptura atual for significativamente mais intensa que a média das passadas.
    """
    memoria = []

    if not os.path.exists(caminho_log):
        return False

    with open(caminho_log, "r") as f:
        for linha in f:
            if "Ruptura detectada em" in linha:
                try:
                    preco = float(linha.split("em")[1].replace("USDT", "").strip())
                    memoria.append(preco)
                except Exception:
                    continue

    if not memoria:
        return False

    media = sum(memoria) / len(memoria)
    desvio = max(abs(p - media) for p in memoria)
    if abs(preco_atual - media) > desvio * 1.5:
        print("[NEURAL] Ruptura atual fora do padrão médio das anteriores.")
        return True

    return False

# ✅ *Nova Função: Captura da Memória Neural em Tempo Real*
def capturar_memoria_mercado(df):
    """
    Armazena os movimentos estratégicos em uma memória neural.
    Essa memória é usada para análises futuras e previsões.
    """
    global memoria_mercado

    for index, row in df.iterrows():
        movimento = {
            "timestamp": index,
            "preco": row["close"],
            "volume": row["volume"],
            "ressonancia": mente_fluidica_verificar_resonancia(row["close"], index),
            "classificacao": classificar_memoria(row["close"], index)
        }
        memoria_mercado.append(movimento)

    # ✅ Atualiza o arquivo de memória neural
    with open(caminho_memoria, "a") as f:
        for movimento in memoria_mercado:
            f.write(f"[{movimento['timestamp']}] Preço: {movimento['preco']} | Volume: {movimento['volume']} | Ressonância: {movimento['ressonancia']}\n")

    print(f"🔄 Memória Neural Atualizada. Total de Registros: {len(memoria_mercado)}")
    return memoria_mercado

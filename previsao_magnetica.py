import pandas as pd

# ✅ Função para detectar reversão de campo magnético
def detectar_zona_de_reversao(df):
    alerta = ""
    curvatura_ema8 = (
        df["EMA8"].diff().iloc[-1] - df["EMA8"].diff().iloc[-2]
    )
    curvatura_ema21 = (
        df["EMA21"].diff().iloc[-1] - df["EMA21"].diff().iloc[-2]
    )
    curvatura_sma200 = (
        df["SMA200"].diff().iloc[-1] - df["SMA200"].diff().iloc[-2]
    )

    if (curvatura_ema8 * curvatura_ema21 < 0) or (curvatura_ema8 * curvatura_sma200 < 0):
        alerta = "[PREVISÃO] 🔄 Possível reversão de campo magnético em formação."
    return alerta

# ✅ Função para mapear ponto de explosão
def mapear_ponto_de_explosao(df):
    alerta = ""
    candle_estreito = (df["high"].iloc[-1] - df["low"].iloc[-1]) < df["close"].rolling(10).std().iloc[-1] * 0.5
    densidade_alta = df["densidade"].iloc[-1] > df["densidade"].quantile(0.9)
    volume_baixo = df["volume"].iloc[-1] < df["volume"].rolling(10).mean().iloc[-1] * 0.7

    if candle_estreito and densidade_alta and volume_baixo:
        alerta = "[PREVISÃO] 🚀 Propulsão iminente. Energia sendo acumulada."
    return alerta

# ✅ Função para verificar distorção temporal
def verificar_distorcao_temporal(df):
    alerta = ""
    r1 = df["close"].pct_change(periods=5).iloc[-1]
    r2 = df["close"].pct_change(periods=10).iloc[-1]
    ritmo = abs(r1 - r2)

    if ritmo > 0.02 and df["volume"].iloc[-1] < df["volume"].rolling(10).mean().iloc[-1]:
        alerta = "[ANOMALIA TEMPORAL] ⚠️ Ritmo quebrado. Cuidado com falsa direção."
    return alerta

# ✅ Função principal para prever movimentos
def prever_movimentos(df):
    """
    Executa a previsão de movimentos com base em análise magnética.
    Retorna uma lista de alertas identificados.
    """
    alertas = []

    for func in [detectar_zona_de_reversao, mapear_ponto_de_explosao, verificar_distorcao_temporal]:
        msg = func(df)
        if msg:
            alertas.append(msg)

    # Log no terminal para controle
    for alerta in alertas:
        print(alerta)
    
    return alertas

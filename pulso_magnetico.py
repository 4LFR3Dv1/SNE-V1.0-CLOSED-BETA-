import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from mente_fluida_ciclica import avaliar_ciclo_ruptura
from memoria_neural import classificar_memoria

# === Função para classificar a ruptura por intensidade
def classificar_ruptura(preco_atual, media, desvio):
    delta = abs(preco_atual - media)
    if delta > desvio * 2:
        return "Classe Ômega"
    elif delta > desvio * 1.5:
        return "Classe Delta"
    elif delta < desvio * 0.75:
        return "Classe Ecos"
    else:
        return "Classe Sigma"

# ✅ Função para gerar o pulso de massa
def gerar_pulso_massa(df, tempo_ruptura, preco_ruptura, energia_ruptura):
    """
    Gera um gráfico visual do pulso de massa em um recorte de 5 minutos.
    Envia a imagem para o HALO caso seja iminente.
    """
    try:
        # 🔄 Import dentro da função para evitar loop circular
        from xenos_bot import enviar_imagem

        inicio = tempo_ruptura
        fim = tempo_ruptura + timedelta(minutes=5)
        df_recorte = df[(df.index >= inicio) & (df.index <= fim)].copy()
        if df_recorte.empty:
            print("[PULSO] Recorte de dados vazio.")
            return

        df_recorte["forca"] = abs(df_recorte["densidade"] - energia_ruptura)
        df_recorte["timestamp"] = mdates.date2num(df_recorte.index.to_pydatetime())

        # Cálculo da classe
        memoria_densidade = df[df["ruptura"]]["densidade"]
        media = memoria_densidade.mean() if not memoria_densidade.empty else 0
        desvio = memoria_densidade.std() if not memoria_densidade.empty else 0
        classe = classificar_ruptura(energia_ruptura, media, desvio)

        # Verifica se deve enviar ao HALO
        ruptura_imminente = avaliar_ciclo_ruptura(df, tempo_ruptura) or classificar_memoria(preco_ruptura, tempo_ruptura, energia_ruptura)

        # Geração do gráfico
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(df_recorte["timestamp"], df_recorte["forca"], color="yellow", linewidth=2, label="Pulso de Massa")
        ax.axvline(mdates.date2num(inicio), color="red", linestyle="--", label="Ruptura")
        ax.set_title(f"{classe} | Pulso: {energia_ruptura:.4f}", color="white")
        ax.set_facecolor("black")
        ax.tick_params(colors='white')
        ax.set_ylabel("Variação de Força", color='white')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        fig.tight_layout()
        fig.patch.set_facecolor('black')

        nome_img = f"pulso_{inicio.strftime('%H%M%S')}.png"
        caminho = f"relatorios/{nome_img}"
        os.makedirs("relatorios", exist_ok=True)
        fig.savefig(caminho, facecolor='black')
        plt.close(fig)

        print(f"\n[PULSO] {classe} registrada às {inicio.strftime('%H:%M:%S')}")
        print(f"[PULSO] Pulso de Massa salvo em {caminho}")

        if ruptura_imminente:
            enviar_imagem(fig, nome_img)

    except Exception as e:
        print(f"[ERRO PULSO MASSA] {e}")

# ✅ Função para detectar todos os pulsos no DataFrame
def detectar_pulsos_massa(df):
    """
    Detecta todos os pulsos de massa gravitacional no DataFrame e dispara o
    método de geração visual para cada ruptura encontrada.
    """
    print("[SNE] 🌌 Detectando Pulsos de Massa...")

    rupturas = df[df["ruptura"]]
    for index, row in rupturas.iterrows():
        gerar_pulso_massa(df, index, row["close"], row["densidade"])

    print(f"[SNE] ✅ Pulsos de Massa mapeados com sucesso: {len(rupturas)} encontrados.")
    return rupturas

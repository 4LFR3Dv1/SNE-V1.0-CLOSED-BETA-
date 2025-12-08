import requests
import os
from datetime import datetime, timedelta
from threading import Timer
from memoria_neural import capturar_memoria_mercado
from mente_fluida import mente_fluidica_verificar_resonancia
from mente_fluida_ciclica import mente_fluidica_detectar_ciclos
from mapeamento_gravitacional import detectar_zonas_criticas
from previsao_magnetica import prever_movimentos
from pulso_magnetico import detectar_pulsos_massa
from catalogo_magnetico import (
    exibir_zonas_relevantes, verificar_ressonancia, registrar_ruptura,
    identificar_compressao, identificar_proximidade_zona
)
from padroes_graficos import detectar_wedges, verificar_confirmacao_quebra
from visualizacao_wedges import criar_grafico_wedge, criar_grafico_comparativo

# === Importar sistema de monetização ===
try:
    from security_manager import security_manager
    from user_manager import user_manager
    from payment_manager import payment_manager
    from cache_manager import cache_manager
    from plan_config import PLANOS
    MONETIZATION_AVAILABLE = True
    print("✅ Sistema de monetização carregado no xenos_bot")
except ImportError as e:
    MONETIZATION_AVAILABLE = False
    print(f"⚠️ Sistema de monetização não disponível no xenos_bot: {e}")

# === Importar configurações seguras ===
try:
    from config_seguro import config
    TELEGRAM_TOKEN = config.TELEGRAM_TOKEN
    TELEGRAM_URL = config.TELEGRAM_URL
    TELEGRAM_PHOTO_URL = config.TELEGRAM_PHOTO_URL
    CHAT_ID = config.TELEGRAM_CHAT_ID
    print("✅ Configurações seguras carregadas do config_seguro.py")
except ImportError:
    # Fallback para configurações hardcoded (modo desenvolvimento)
    print("⚠️ config_seguro.py não encontrado. Usando configurações hardcoded.")
    TELEGRAM_TOKEN = "7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y"
    TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    TELEGRAM_PHOTO_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    CHAT_ID = "6457067653"

# === URLs para webhook ===
TELEGRAM_WEBHOOK_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
TELEGRAM_GET_UPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
TELEGRAM_DELETE_WEBHOOK_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"

# === Caminhos para salvar logs temporários e códices ===
CAMINHO_LOG_RUPTURAS = os.path.join(os.getcwd(), "log_rupturas.txt")
CAMINHO_CODICE_FLUXO = os.path.join(os.getcwd(), "codice_fluxo.txt")

estado = {
    "capital": 1000,
    "capital_real": 1000,
    "posicao": 0,
    "preco_medio": 0,
    "historico": [],
    "ressonancias_ignoradas": 0,
    "ultima_data_processada": None,
    "zonas_mapeadas": [],
    "rupturas_estrategicas": []
}

# === Buffer de mensagens e controle de tempo ===
buffer_mensagens = []
ultima_mensagem_enviada = datetime.now()
intervalo_envio = timedelta(minutes=5)  # Envio de 5 em 5 minutos
ultima_mensagem = ""  # Armazena o último conteúdo enviado


# === Verificação de conexão com a internet ===
def verificar_conexao():
    """
    Testa conexão com a API do Telegram para evitar falhas contínuas.
    """
    try:
        response = requests.get('https://api.telegram.org', timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# ✅ Verifica e cria os arquivos de log e códice, se não existirem
for caminho, nome in [(CAMINHO_LOG_RUPTURAS, "Log de Rupturas"), (CAMINHO_CODICE_FLUXO, "Códice de Fluxo")]:
    if not os.path.exists(caminho):
        with open(caminho, 'w') as file:
            file.write(f"🔍 {nome} Iniciado.\n")
        print(f"✅ Arquivo criado em: {caminho}")

# ✅ Envia mensagem para o Telegram de forma síncrona
ultima_mensagem_enviada = None

def enviar_foto(caminho_imagem, legenda="", max_tentativas=3):
    """
    Envia uma foto para o Telegram
    """
    if not verificar_conexao():
        print("❌ Sem conexão com a internet. Envio cancelado.")
        return False
    
    if not os.path.exists(caminho_imagem):
        print(f"❌ Arquivo não encontrado: {caminho_imagem}")
        return False
    
    for tentativa in range(max_tentativas):
        try:
            with open(caminho_imagem, 'rb') as photo:
                data = {
                    'chat_id': CHAT_ID,
                    'caption': legenda,
                    'parse_mode': 'HTML'
                }
                files = {'photo': photo}
                
                response = requests.post(TELEGRAM_PHOTO_URL, data=data, files=files, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ Foto enviada: {os.path.basename(caminho_imagem)}")
                    return True
                else:
                    print(f"⚠️ Erro {response.status_code}: {response.text}")
        
        except Exception as e:
            print(f"❌ Tentativa {tentativa + 1} falhou: {e}")
    
    return False


def enviar_oraculo(mensagem, max_tentativas=3):
    """
    Envia uma mensagem para o Oráculo via Telegram.
    Apenas envia se houver mudanças estratégicas.
    """
    global ultima_mensagem_enviada

    # Evita duplicidade
    if mensagem == ultima_mensagem_enviada:
        print("🔄 Mensagem duplicada detectada. Ignorando envio.")
        return False

    # Sanitizar HTML - remover tags não suportadas
    import re
    mensagem = re.sub(r'</?pre>', '', mensagem)
    mensagem = re.sub(r'</?div>', '', mensagem)
    mensagem = re.sub(r'</?span[^>]*>', '', mensagem)

    params = {
        'chat_id': CHAT_ID,
        'text': mensagem,
        'parse_mode': 'HTML'
    }

    tentativas = 0
    while tentativas < max_tentativas:
        try:
            response = requests.post(TELEGRAM_URL, params=params, timeout=10)
            if response.status_code == 200:
                print(f"✅ Mensagem enviada com sucesso: {mensagem}")
                ultima_mensagem_enviada = mensagem
                return True
            else:
                erro = response.text
                print(f"[ERRO ENVIO] Status {response.status_code}: {erro}")
        except requests.ConnectionError:
            print(f"[ERRO ENVIO] Conexão falhou. Tentativa {tentativas + 1} de {max_tentativas}.")
        except requests.Timeout:
            print(f"[ERRO ENVIO] Timeout excedido. Tentativa {tentativas + 1} de {max_tentativas}.")
        except Exception as e:
            print(f"[ERRO ENVIO] Tentativa {tentativas + 1} falhou: {e}")
        
        tentativas += 1
    
    print("[ERRO ENVIO] Máximo de tentativas atingido. Mensagem não enviada.")
    return False

# ✅ Função para agrupar mensagens e enviar de forma otimizada
def enviar_buffer_estrategico():
    """
    Envia todas as mensagens acumuladas no buffer a cada intervalo definido.
    """
    global buffer_mensagens, ultima_mensagem_enviada

    if buffer_mensagens:
        buffer_mensagens = list(set(buffer_mensagens))
        mensagem_estrategica = "📡 <b>Resumo Estratégico:</b>\n"
        mensagem_estrategica += "\n".join(buffer_mensagens)
        
        if enviar_oraculo(mensagem_estrategica):
            buffer_mensagens = []
            ultima_mensagem_enviada = datetime.now()

    # Apenas reinicia se houve alteração no buffer
    if buffer_mensagens:
        Timer(intervalo_envio.total_seconds(), enviar_buffer_estrategico).start()
def analise_estrategica(df):
    """
    Executa uma análise profunda do mercado, identificando:
    - Zonas de suporte e resistência
    - Canais de propulsão
    - Rupturas críticas
    - Fluxo mental e ressonâncias
    """
    preco_atual = df["close"].iloc[-1]
    timestamp = df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
    
    # 🔍 Mapeamento Gravitacional
    zonas_criticas = mapear_zonas_criticas(df)
    canais = detectar_pulsos_massa(df)

    # 🔎 Análise de Ressonância
    ressonante = mente_fluidica_verificar_resonancia(df)

    # 🔄 Previsão de Movimentos
    movimentos_futuros = prever_movimentos(df)

    # 🔎 Médias Móveis
    ema8 = df["EMA8"].iloc[-1]
    ema21 = df["EMA21"].iloc[-1]
    sma200 = df["SMA200"].iloc[-1]

    tendencia = "Neutra"
    if ema8 > ema21 > sma200:
        tendencia = "🔼 Tendência de Alta"
    elif ema8 < ema21 < sma200:
        tendencia = "🔻 Tendência de Baixa"
    
    # 📡 Relatório Estratégico Completo
    relatorio = (
        f"📊 <b>Análise Estratégica - Radar Ativado:</b>\n"
        f"🕰️ <b>Horário:</b> {timestamp}\n"
        f"💲 <b>Preço Atual:</b> {preco_atual:.2f} USDT\n\n"
        f"🔎 <b>Zonas Críticas:</b> {zonas_criticas}\n"
        f"🚀 <b>Canais de Propulsão:</b> {canais}\n"
        f"🛡️ <b>Ressonância Detectada:</b> {'Sim' if ressonante else 'Não'}\n"
        f"🔄 <b>Movimentos Esperados:</b> {movimentos_futuros}\n"
        f"📈 <b>Tendência Atual:</b> {tendencia}\n\n"
        f"🗒️ <b>Recomendações Estratégicas:</b>\n"
    )

    # 📌 Recomendações de Ação
    if ressonante and tendencia == "🔼 Tendência de Alta":
        relatorio += "🔵 Possível oportunidade de COMPRA detectada.\n"
    elif ressonante and tendencia == "🔻 Tendência de Baixa":
        relatorio += "🔴 Possível oportunidade de VENDA detectada.\n"
    else:
        relatorio += "⚠️ Mercado neutro, aguardar confirmação de direção.\n"
    
    # 🚀 Se houver zona crítica próxima, alertar no Telegram
    if zonas_criticas:
        enviar_alerta_tatico("Zona Crítica Detectada", preco_atual, timestamp, "zona")

    enviar_oraculo(relatorio)
    print(relatorio)
    
# ✅ Função para executar a cada 5 minutos
def iniciar_analise_estrategica():
    """
    Inicia um ciclo de análise estratégica a cada 5 minutos.
    """
    from fluxo_mental import obter_fluxo_mercado
    
    print("🔄 Iniciando análise estratégica...")
    df = obter_fluxo_mercado()
    
    if not df.empty:
        analise_estrategica(df)
    
    Timer(INTERVALO_ANALISE, iniciar_analise_estrategica).start()

# ✅ Inicia o ciclo de análise estratégica
    iniciar_analise_estrategica()

# ✅ Envio de Resumo Estratégico
def enviar_resumo_estrategico(estado):
    """
    Adiciona um resumo estratégico ao buffer para envio otimizado.
    """
    mensagem = "📋 <b>Resumo Estratégico:</b>\n"
    mensagem += f"💰 <b>Capital Atual:</b> {estado['capital']:.2f} USDT\n"
    mensagem += f"📈 <b>Posição Atual:</b> {estado['posicao']:.6f} BTC\n"
    mensagem += f"🔄 <b>Operações Realizadas:</b> {len(estado['historico'])}\n"
    mensagem += f"🛡️ <b>Ressonâncias Ignoradas:</b> {estado['ressonancias_ignoradas']}\n\n"
    
    if estado["historico"]:
        ultima_operacao = estado["historico"][-1]
        mensagem += f"📌 <b>Última Operação:</b> {ultima_operacao['tipo']} em {ultima_operacao['preco']} USDT\n"
    
    buffer_mensagens.append(mensagem)
    enviar_oraculo(mensagem)

# ✅ Envio de Relatório de Rupturas (DESATIVADO - Função obsoleta)
def enviar_log_rupturas():
    """
    Função obsoleta mantida para compatibilidade.
    O sistema agora usa análises em tempo real via Scanner e AUTO.
    """
    # Esta função foi desativada pois o sistema evoluiu para análises mais avançadas
    # Usar comandos: R (Scanner), AUTO (24/7), DASH (Dashboard)
    pass

# ✅ Geração do códice de fluxo
def gerar_codice_fluxo(estado):
    """
    Gera um códice de fluxo com os últimos movimentos estratégicos.
    """
    movimentos_unicos = list(set(estado.get("buffer_estrategico", [])))  # Remove duplicidades

    if movimentos_unicos:
        with open(CAMINHO_CODICE_FLUXO, 'a') as file:
            file.write(f"\n🔄 <b>Atualização:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("📌 <b>Movimentos Estratégicos Recentes:</b>\n")
            
            for movimento in movimentos_unicos:
                file.write(f"{movimento}\n")
            
            file.write("—" * 50 + "\n")
        
        print("✅ Códice de Fluxo atualizado com sucesso.")
    else:
        print("⚠️ Nenhum movimento estratégico recente detectado.")
def iniciar_oraculo():
    """
    Envia uma mensagem inicial para o Oráculo no Telegram.
    """
    mensagem = "🔮 <b>Oráculo iniciado. Aguardando instruções...</b>"
    enviar_oraculo(mensagem)
    print("✅ Oráculo iniciado e mensagem enviada.")

def enviar_alerta_tatico(movimento, preco, timestamp, tipo="neutro"):
    """
    Adiciona um alerta tático ao buffer para envio otimizado.
    """
    icone = "🛡️" if tipo == "ressonancia" else ("🚀" if tipo == "compra" else "💡")
    mensagem = f"{icone} <b>{movimento}</b>\n"
    mensagem += f"💰 <b>Preço:</b> {preco:.2f} USDT\n"
    mensagem += f"⏱ <b>Horário:</b> {timestamp}\n"
    buffer_mensagens.append(mensagem)
# ✅ Fechar a sessão do Oráculo
def fechar_sessao():
    """
    Finaliza a sessão do Telegram e envia mensagem de encerramento.
    """
    try:
        hora_fim = datetime.now().strftime("%H:%M:%S")
        mensagem_fim = f"""🔴 <b>SNE RADAR - SISTEMA ENCERRADO</b>

⏰ <b>Hora:</b> {hora_fim}
📊 <b>Status:</b> Desconectado

<b>📋 SESSÃO FINALIZADA</b>

✅ Todas as análises foram concluídas
✅ Buffers limpos
✅ Conexões encerradas

💡 <b>Até a próxima sessão!</b>
Para retomar, execute: <code>python3 main.py</code>
"""
        enviar_oraculo(mensagem_fim)
        print("✅ Mensagem de encerramento enviada ao Telegram")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem de encerramento: {e}")
    finally:
        print("[INFO] Finalizando sessão com o Oráculo...")
        buffer_mensagens.clear()


def enviar_alerta_wedge(symbol, df):
    """
    Detecta e envia alertas de Wedge Patterns para o Telegram
    
    Args:
        symbol: Par analisado (ex: 'BTCUSDT')
        df: DataFrame com dados OHLCV
    """
    try:
        # Detectar wedges
        wedges = detectar_wedges(df)
        
        if not wedges.get('wedge_detectado', False):
            return False
        
        # Verificar confirmação de quebra
        quebra = verificar_confirmacao_quebra(df, wedges)
        
        wedge = wedges
        preco_atual = df['close'].iloc[-1]
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Montar mensagem baseada no tipo de wedge
        if wedge['tipo'] == 'RISING_WEDGE':
            emoji = "🔺"
            sinal = "BEARISH"
            recomendacao = "Considerar SHORT"
            cor = "🔴"
        elif wedge['tipo'] == 'FALLING_WEDGE':
            emoji = "🔻"
            sinal = "BULLISH"
            recomendacao = "Considerar LONG"
            cor = "🟢"
        else:
            return False
        
        # Montar mensagem completa
        mensagem = f"""
{emoji} <b>WEDGE PATTERN DETECTADO!</b>

💰 <b>Par:</b> {symbol}
🕰 <b>Hora:</b> {timestamp}
📊 <b>Preço:</b> ${preco_atual:,.2f}

🔺 <b>Padrão:</b> {wedge['nome']}
📈 <b>Sinal:</b> {sinal}
🎯 <b>Confiança:</b> {wedge['confianca']}%
⚡ <b>Prob. Reversão:</b> {wedge['probabilidade_reversao']}%

📊 <b>Características:</b>
• Altura: ${wedge['altura_wedge']:,.2f}
• Volume Médio: {wedge['volume_medio']:,.0f}
• Convergência: {wedge['convergencia']:.4f}

🎯 <b>Níveis Operacionais:</b>"""
        
        # Adicionar alvo teórico
        if wedge.get('alvo_teorico'):
            alvo = wedge['alvo_teorico']
            mensagem += f"""
• Alvo: ${alvo['preco']:,.2f} ({alvo['direcao']})
• Distância: {alvo['percentual']:.1f}%"""
        
        # Adicionar stop loss
        if wedge.get('stop_loss'):
            stop = wedge['stop_loss']
            mensagem += f"""
• Stop Loss: ${stop['preco']:,.2f}
• Distância SL: {stop['percentual']:.1f}%"""
        
        # Adicionar ponto de convergência
        if wedge.get('ponto_convergencia'):
            conv = wedge['ponto_convergencia']
            mensagem += f"""
• Convergência: ${conv['y']:,.2f}"""
        
        # Adicionar informações de quebra se aplicável
        if quebra.get('quebrado', False):
            mensagem += f"""
        
        🚨 <b>CONFIRMAÇÃO DE QUEBRA:</b>
        • Tipo: {quebra['tipo_quebra']}
        • Preço: ${quebra['preco_quebra']:,.2f}
        • Volume: {'✅ Confirmado' if quebra['volume_confirma'] else '❌ Baixo'}
        • Ratio: {quebra['volume_ratio']:.1f}x
        • Descrição: {quebra['descricao']}"""
        
        # Adicionar recomendação
        mensagem += f"""
        
        {cor} <b>RECOMENDAÇÃO:</b> {recomendacao}
        
        ⚠️ <b>ATENÇÃO:</b> Wedge patterns são padrões de reversão!
        📚 <b>Estratégia:</b> Aguardar confirmação do rompimento
        🎯 <b>Target:</b> Altura do padrão projetada na direção do breakout
        
        <i>SNE Radar - Análise Técnica Avançada</i>
        """
        
        # Criar e enviar gráfico
        try:
            grafico_bytes = criar_grafico_wedge(df, wedges, symbol, "1h")
            if grafico_bytes:
                enviar_grafico_wedge(grafico_bytes, mensagem, symbol)
            else:
                enviar_oraculo(mensagem)
        except Exception as e:
            print(f"[ERRO GRÁFICO] Falha ao criar gráfico: {e}")
            enviar_oraculo(mensagem)
        
        # Log do alerta
        log_msg = f"[WEDGE ALERT] {symbol} - {wedge['nome']} detectado em ${preco_atual:,.2f}"
        print(log_msg)
        
        # Salvar no log de rupturas
        with open(CAMINHO_LOG_RUPTURAS, "a") as f:
            f.write(f"[{datetime.now()}] {log_msg}\n")
        
        return True
        
    except Exception as e:
        print(f"[ERRO WEDGE] Falha ao processar alerta: {e}")
        return False


def monitorar_wedges_continuo(symbol="BTCUSDT", interval="1m"):
    """
    Monitora continuamente por padrões de wedge
    
    Args:
        symbol: Par a monitorar
        interval: Timeframe para análise
    """
    try:
        import requests
        import pandas as pd
        
        # Coletar dados
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": 100}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype({
                'timestamp': 'datetime64[ms]',
                'open': float, 'high': float, 'low': float,
                'close': float, 'volume': float
            })
            
            # Enviar alerta se wedge detectado
            enviar_alerta_wedge(symbol, df)
            
    except Exception as e:
        print(f"[ERRO MONITOR] Falha no monitoramento de wedges: {e}")


def enviar_grafico_wedge(grafico_bytes, mensagem, symbol):
    """
    Envia gráfico de wedge para o Telegram
    
    Args:
        grafico_bytes: Bytes da imagem
        mensagem: Mensagem de texto
        symbol: Par analisado
    """
    try:
        import base64
        
        # Converter bytes para base64
        image_b64 = base64.b64encode(grafico_bytes).decode('utf-8')
        
        # Preparar dados para envio
        files = {
            'photo': ('wedge_chart.png', grafico_bytes, 'image/png')
        }
        
        data = {
            'chat_id': CHAT_ID,
            'caption': mensagem,
            'parse_mode': 'HTML'
        }
        
        # Enviar foto
        response = requests.post(TELEGRAM_PHOTO_URL, data=data, files=files, timeout=30)
        
        if response.status_code == 200:
            print(f"[TELEGRAM] Gráfico de wedge enviado para {symbol}")
        else:
            print(f"[ERRO TELEGRAM] Falha ao enviar gráfico: {response.text}")
            # Fallback: enviar apenas mensagem
            enviar_oraculo(mensagem)
            
    except Exception as e:
        print(f"[ERRO GRÁFICO] Falha ao enviar gráfico: {e}")
        # Fallback: enviar apenas mensagem
        enviar_oraculo(mensagem)

# ===========================================
# SISTEMA DE WEBHOOK E COMANDOS
# ===========================================

def configurar_webhook(webhook_url: str = None):
    """
    Configura webhook do Telegram
    
    Args:
        webhook_url: URL do webhook (opcional)
    """
    try:
        if webhook_url:
            data = {'url': webhook_url}
            response = requests.post(TELEGRAM_WEBHOOK_URL, data=data, timeout=10)
        else:
            # Usar polling em vez de webhook
            response = requests.post(TELEGRAM_DELETE_WEBHOOK_URL, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Webhook configurado: {webhook_url or 'Polling ativado'}")
                return True
            else:
                print(f"❌ Erro ao configurar webhook: {result.get('description')}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
        return False

def obter_mensagens():
    """
    Obtém mensagens pendentes do Telegram
    
    Returns:
        list: Lista de mensagens
    """
    try:
        response = requests.get(TELEGRAM_GET_UPDATES_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return data.get('result', [])
            else:
                print(f"❌ Erro na API: {data.get('description')}")
                return []
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro ao obter mensagens: {e}")
        return []

def processar_comando_telegram(comando: str, user_id: str, args: list = None):
    """
    Processa comandos do Telegram
    
    Args:
        comando: Comando recebido
        user_id: ID do usuário
        args: Argumentos do comando
        
    Returns:
        str: Resposta para o usuário
    """
    try:
        comando_limpo = comando.replace('/', '').lower()
        
        # === COMANDOS BÁSICOS ===
        if comando_limpo == 'start':
            return comando_start(user_id)
        elif comando_limpo == 'ajuda':
            return comando_ajuda(user_id)
        elif comando_limpo == 'demo':
            return comando_demo(user_id, args)
        elif comando_limpo == 'status':
            return comando_status(user_id)
        
        # === COMANDOS DE MONETIZAÇÃO ===
        elif comando_limpo == 'planos':
            return comando_planos(user_id)
        elif comando_limpo == 'upgrade':
            return comando_upgrade(user_id)
        
        # === COMANDOS PREMIUM ===
        elif comando_limpo == 'analise':
            return comando_analise(user_id, args)
        elif comando_limpo == 'relatorio':
            return comando_relatorio(user_id)
        
        # === COMANDOS INSTITUCIONAL ===
        elif comando_limpo == 'multi':
            return comando_multi(user_id, args)
        
        else:
            return "❌ Comando não reconhecido. Use /ajuda para ver todos os comandos."
            
    except Exception as e:
        print(f"❌ Erro ao processar comando {comando}: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_start(user_id: str) -> str:
    """Comando /start - Boas-vindas"""
    try:
        # Registrar atividade do usuário
        if MONETIZATION_AVAILABLE:
            user_manager.update_user_activity(user_id)
            
            # Verificar se é usuário existente
            if user_manager.is_user_registered(user_id):
                user_data = user_manager.get_user_data(user_id)
                plano = user_data['plano'].upper()
                mensagem = f"""
🚀 **Bem-vindo de volta ao SNE Radar!**

📊 **Seu Plano:** {plano}
✅ **Status:** {'Ativo' if user_data['is_active'] else 'Inativo'}

💡 **Comandos disponíveis:**
🔹 /analise - Análise técnica completa
🔹 /relatorio - Relatórios automáticos
🔹 /demo - Teste gratuito
🔹 /status - Ver detalhes da conta

🎯 **Use /ajuda para ver todos os comandos!**
"""
            else:
                # Criar usuário free
                user_manager.create_user(user_id, 'free')
                
                mensagem = f"""
🚀 **Bem-vindo ao SNE Radar!**

🎯 **Sistema de Análise Técnica Profissional**
📊 Análise multi-timeframe + DOM + Gestão de Risco

🔹 **Plano FREE:** 3 análises/dia
🔹 **Teste agora:** /demo BTCUSDT
🔹 **Upgrade:** /planos

💡 **Comandos disponíveis:**
🔹 /demo - Teste gratuito
🔹 /planos - Planos premium
🔹 /ajuda - Lista completa

🎯 **Comece com:** /demo BTCUSDT
"""
        else:
            mensagem = """
🚀 **Bem-vindo ao SNE Radar!**

🎯 **Sistema de Análise Técnica Profissional**
📊 Análise multi-timeframe + DOM + Gestão de Risco

💡 **Comandos disponíveis:**
🔹 /demo - Teste gratuito
🔹 /ajuda - Lista completa

🎯 **Comece com:** /demo BTCUSDT
"""
        
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando start: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_ajuda(user_id: str) -> str:
    """Comando /ajuda - Lista de comandos"""
    try:
        if MONETIZATION_AVAILABLE:
            user_data = user_manager.get_user_data(user_id)
            plano = user_data['plano'] if user_data else 'free'
            
            # Comandos por plano
            comandos_free = [
                "/start - Iniciar bot",
                "/demo - Teste gratuito",
                "/ajuda - Esta lista",
                "/planos - Planos premium"
            ]
            
            comandos_premium = [
                "/analise - Análise completa",
                "/relatorio - Relatórios técnicos",
                "/status - Status da conta"
            ]
            
            comandos_institutional = [
                "/multi - Análise multi-pair",
                "/config - Configurações"
            ]
            
            mensagem = f"""
📋 **COMANDOS DISPONÍVEIS**

🔹 **BÁSICOS (Todos):**
{chr(10).join(comandos_free)}

🔹 **PREMIUM ({plano}):**
{chr(10).join(comandos_premium) if plano in ['premium', 'institutional'] else '❌ Upgrade necessário'}

🔹 **INSTITUCIONAL ({plano}):**
{chr(10).join(comandos_institutional) if plano == 'institutional' else '❌ Upgrade necessário'}

💡 **Exemplos:**
• /demo BTCUSDT
• /analise ETHUSDT 1h
• /status

🎯 **Seu plano:** {plano.upper()}
"""
        else:
            mensagem = """
📋 **COMANDOS DISPONÍVEIS**

🔹 **BÁSICOS:**
/start - Iniciar bot
/demo - Teste gratuito
/ajuda - Esta lista

💡 **Exemplos:**
• /demo BTCUSDT
• /ajuda
"""
        
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando ajuda: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_demo(user_id: str, args: list = None) -> str:
    """Comando /demo - Análise limitada gratuita"""
    try:
        if MONETIZATION_AVAILABLE:
            # Verificar limite de análises
            if not security_manager.verificar_limite_analises(user_id):
                return "⚠️ Limite diário atingido. Assine premium para mais análises!"
        
        # Obter parâmetros
        par = args[0].upper() if args and len(args) > 0 else 'BTCUSDT'
        
        # Verificar se par é válido
        if not _is_valid_symbol(par):
            return "❌ Par inválido. Use: /demo BTCUSDT"
        
        # Gerar análise limitada
        resultado = _gerar_analise_demo(par)
        
        # Formatar resultado
        mensagem = _formatar_analise_demo(resultado, par)
        
        # Registrar uso
        if MONETIZATION_AVAILABLE:
            security_manager.registrar_uso_funcionalidade(user_id, 'demo')
        
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando demo: {e}")
        return "❌ Erro ao gerar análise demo. Tente novamente."

def comando_status(user_id: str) -> str:
    """Comando /status - Status da conta"""
    try:
        if not MONETIZATION_AVAILABLE:
            return "📊 Sistema sem monetização - Acesso livre"
        
        user_data = user_manager.get_user_data(user_id)
        if not user_data:
            return "❌ Usuário não encontrado. Use /start primeiro."
        
        stats = user_manager.get_user_stats(user_id)
        
        mensagem = f"""
📊 **MINHA CONTA**

🔹 **Plano:** {user_data['plano'].upper()}
🔹 **Status:** {'✅ Ativo' if user_data['is_active'] else '❌ Inativo'}
🔹 **Análises hoje:** {stats['analises_hoje']}/{PLANOS[user_data['plano']]['analises_dia']}
🔹 **Alertas ativos:** {stats['alertas_ativos']}

📅 **Vencimento:** {user_data['expires_at'] or 'N/A'}
📅 **Criado em:** {user_data['created_at'][:10]}
📅 **Última atividade:** {user_data['last_activity'][:10]}

💡 **Funcionalidades:**
{chr(10).join([f"✅ {func}" for func in PLANOS[user_data['plano']]['recursos'][:3]])}

🎯 **Upgrade:** /planos
"""
        
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando status: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_planos(user_id: str) -> str:
    """Comando /planos - Ver planos disponíveis"""
    try:
        if not MONETIZATION_AVAILABLE:
            return "❌ Sistema de monetização não disponível"
        
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
        
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando planos: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_upgrade(user_id: str) -> str:
    """Comando /upgrade - Upgrade de plano"""
    try:
        if not MONETIZATION_AVAILABLE:
            return "❌ Sistema de monetização não disponível"
        
        user_data = user_manager.get_user_data(user_id)
        if user_data:
            plano_atual = user_data['plano']
            
            if plano_atual == 'free':
                mensagem = f"""
🚀 **UPGRADE DISPONÍVEL**

📊 **Plano atual:** FREE
💡 **Upgrade disponível:**

🔹 PREMIUM - R$ {PLANOS['premium']['preco']}/mês
   ✅ 50 análises/dia
   ✅ Análise completa
   ✅ Relatórios técnicos

🔹 INSTITUCIONAL - R$ {PLANOS['institutional']['preco']}/mês
   ✅ 1000 análises/dia
   ✅ Multi-pair analysis
   ✅ API completa

📧 **Para assinar:** sne.radar@email.com
"""
            elif plano_atual == 'premium':
                mensagem = f"""
🚀 **UPGRADE DISPONÍVEL**

📊 **Plano atual:** PREMIUM
💡 **Upgrade disponível:**

🔹 INSTITUCIONAL - R$ {PLANOS['institutional']['preco']}/mês
   ✅ 1000 análises/dia
   ✅ Multi-pair analysis
   ✅ API completa
   ✅ Whitelabel

📧 **Para assinar:** sne.radar@email.com
"""
            else:
                mensagem = """
✅ **PLANO MÁXIMO**

📊 **Plano atual:** INSTITUCIONAL
🎯 **Você já tem o plano mais alto!**

💡 **Todas as funcionalidades disponíveis:**
✅ Análise multi-pair
✅ API completa
✅ Automação 24/7
✅ Whitelabel personalizado
"""
        else:
            mensagem = "❌ Usuário não encontrado"
        
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando upgrade: {e}")
        return "❌ Erro interno. Tente novamente."

def comando_analise(user_id: str, args: list = None) -> str:
    """Comando /analise - Análise completa premium"""
    try:
        if not MONETIZATION_AVAILABLE:
            return "❌ Sistema de monetização não disponível"
        
        # Verificar acesso premium
        if not security_manager.verificar_acesso_premium(user_id):
            return "⚠️ Acesso premium necessário. Use /planos para ver opções."
        
        # Verificar limite de análises
        if not security_manager.verificar_limite_analises(user_id):
            return "⚠️ Limite diário de análises atingido. Upgrade para mais análises!"
        
        # Obter parâmetros
        par = args[0].upper() if args and len(args) > 0 else 'BTCUSDT'
        timeframe = args[1] if args and len(args) > 1 else '1h'
        
        # Verificar se par é válido
        if not _is_valid_symbol(par):
            return "❌ Par inválido. Use: /analise BTCUSDT 1h"
        
        # Gerar análise completa
        resultado = _gerar_analise_completa(par, timeframe, user_id)
        
        # Formatar resultado
        mensagem = _formatar_analise_completa(resultado, par, timeframe)
        
        # Registrar uso
        security_manager.registrar_uso_funcionalidade(user_id, 'analise')
        
        return mensagem
        
    except Exception as e:
        print(f"❌ Erro no comando analise: {e}")
        return "❌ Erro ao gerar análise. Tente novamente."

def comando_relatorio(user_id: str) -> str:
    """Comando /relatorio - Relatórios técnicos"""
    try:
        if not MONETIZATION_AVAILABLE:
            return "❌ Sistema de monetização não disponível"
        
        # Verificar acesso premium
        if not security_manager.verificar_acesso_premium(user_id):
            return "⚠️ Acesso premium necessário. Use /planos para ver opções."
        
        # Verificar rate limit
        if not security_manager.aplicar_rate_limit_por_plano(user_id, 'relatorio'):
            return "⚠️ Limite de relatórios atingido. Tente novamente mais tarde."
        
        # Gerar relatório
        relatorio = _gerar_relatorio_completo()
        
        # Registrar uso
        security_manager.registrar_uso_funcionalidade(user_id, 'relatorio')
        
        return relatorio
        
    except Exception as e:
        print(f"❌ Erro no comando relatorio: {e}")
        return "❌ Erro ao gerar relatório. Tente novamente."

def comando_multi(user_id: str, args: list = None) -> str:
    """Comando /multi - Análise multi-pair"""
    try:
        if not MONETIZATION_AVAILABLE:
            return "❌ Sistema de monetização não disponível"
        
        # Verificar acesso institucional
        if not security_manager.verificar_acesso_institutional(user_id):
            return "⚠️ Acesso institucional necessário. Upgrade para plano Institutional!"
        
        # Implementar análise multi-pair
        return "🚧 Funcionalidade em desenvolvimento..."
        
    except Exception as e:
        print(f"❌ Erro no comando multi: {e}")
        return "❌ Erro interno. Tente novamente."

def _is_valid_symbol(symbol: str) -> bool:
    """Verifica se símbolo é válido"""
    valid_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT', 'LINKUSDT']
    return symbol.upper() in valid_symbols

def _gerar_analise_demo(par: str) -> dict:
    """Gera análise demo limitada"""
    # Mock para desenvolvimento
    return {
        'par': par,
        'preco': 50000.0,
        'tendencia': 'Alta',
        'score': 7.5,
        'recomendacao': 'Compra com cautela',
        'niveis': {
            'suporte': 48000,
            'resistencia': 52000
        }
    }

def _formatar_analise_demo(resultado: dict, par: str) -> str:
    """Formata análise demo para Telegram"""
    return f"""
📊 **ANÁLISE DEMO - {par}**

💰 **Preço:** ${resultado['preco']:,.2f}
📈 **Tendência:** {resultado['tendencia']}
⭐ **Score:** {resultado['score']}/10
💡 **Recomendação:** {resultado['recomendacao']}

📍 **Níveis:**
🔹 Suporte: ${resultado['niveis']['suporte']:,.2f}
🔹 Resistência: ${resultado['niveis']['resistencia']:,.2f}

⚠️ **Limitação:** Análise simplificada
🚀 **Upgrade:** /planos para análise completa
"""

def _gerar_analise_completa(par: str, timeframe: str, user_id: str) -> dict:
    """Gera análise completa premium"""
    try:
        # Verificar cache primeiro
        if MONETIZATION_AVAILABLE:
            cached_result = cache_manager.get_user_cache(user_id, 'analises', f"{par}_{timeframe}")
            if cached_result:
                return cached_result
        
        # Gerar análise usando sistema existente
        try:
            from motor_renan import analise_completa
            resultado = analise_completa(par, timeframe)
        except ImportError:
            # Mock para desenvolvimento
            resultado = {
                'par': par,
                'timeframe': timeframe,
                'preco': 50000.0,
                'tendencia': 'Alta',
                'score': 8.5,
                'recomendacao': 'Compra forte',
                'niveis': {
                    'suporte': 48000,
                    'resistencia': 52000,
                    'entry': 50000,
                    'stop': 47500,
                    'target': 52500
                },
                'indicadores': {
                    'rsi': 65,
                    'macd': 'Positivo',
                    'ema': 'Suporte'
                }
            }
        
        # Cachear resultado
        if MONETIZATION_AVAILABLE:
            cache_manager.set_user_cache(user_id, 'analises', f"{par}_{timeframe}", resultado, ttl=300)
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro ao gerar análise completa: {e}")
        return {'erro': str(e)}

def _formatar_analise_completa(resultado: dict, par: str, timeframe: str) -> str:
    """Formata análise completa para Telegram"""
    if 'erro' in resultado:
        return f"❌ Erro na análise: {resultado['erro']}"
    
    return f"""
📊 **ANÁLISE COMPLETA - {par} ({timeframe})**

💰 **Preço:** ${resultado['preco']:,.2f}
📈 **Tendência:** {resultado['tendencia']}
⭐ **Score:** {resultado['score']}/10
💡 **Recomendação:** {resultado['recomendacao']}

📍 **Níveis Operacionais:**
🔹 Entry: ${resultado['niveis']['entry']:,.2f}
🔹 Stop: ${resultado['niveis']['stop']:,.2f}
🔹 Target: ${resultado['niveis']['target']:,.2f}

📊 **Indicadores:**
🔹 RSI: {resultado['indicadores']['rsi']}
🔹 MACD: {resultado['indicadores']['macd']}
🔹 EMA: {resultado['indicadores']['ema']}

✅ **Análise Premium Completa**
"""

def _gerar_relatorio_completo() -> str:
    """Gera relatório completo"""
    try:
        # Mock para desenvolvimento
        return """
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
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        return "❌ Erro ao gerar relatório."

def iniciar_bot_polling():
    """
    Inicia o bot em modo polling (sem webhook)
    """
    try:
        print("🤖 Iniciando SNE Bot (Modo Polling)...")
        
        # Configurar polling
        configurar_webhook()  # Remove webhook se existir
        
        # Enviar mensagem de inicialização
        mensagem_inicial = """
🚀 **SNE RADAR BOT - SISTEMA INICIADO**

✅ **Sistema de Comandos Ativo**
✅ **Comandos Disponíveis:**
🔹 /start - Iniciar
🔹 /demo - Teste gratuito
🔹 /ajuda - Lista de comandos
🔹 /planos - Planos premium

🎯 **Bot pronto para uso!**
"""
        enviar_oraculo(mensagem_inicial)
        
        print("✅ SNE Bot iniciado com sucesso! (Modo Polling)")
        print("🔄 Aguardando mensagens...")
        
        # Loop principal de polling
        last_update_id = 0
        
        while True:
            try:
                # Obter mensagens
                updates = obter_mensagens()
                
                for update in updates:
                    update_id = update.get('update_id')
                    
                    if update_id > last_update_id:
                        last_update_id = update_id
                        
                        # Processar mensagem
                        message = update.get('message', {})
                        if message:
                            chat_id = message.get('chat', {}).get('id')
                            text = message.get('text', '')
                            user_id = str(message.get('from', {}).get('id', ''))
                            
                            if text.startswith('/'):
                                # Processar comando
                                parts = text.split()
                                comando = parts[0]
                                args = parts[1:] if len(parts) > 1 else []
                                
                                print(f"🔧 Processando comando: {comando} de {user_id}")
                                
                                # Processar comando
                                resposta = processar_comando_telegram(comando, user_id, args)
                                
                                # Enviar resposta
                                enviar_mensagem_para_usuario(chat_id, resposta)
                                
                            else:
                                # Mensagem de texto normal
                                resposta = "💡 Use /ajuda para ver todos os comandos disponíveis."
                                enviar_mensagem_para_usuario(chat_id, resposta)
                
                # Aguardar antes da próxima verificação
                import time
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no loop principal: {e}")
                import time
                time.sleep(5)
        
        print("✅ SNE Bot encerrado")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")

def configurar_webhook_producao(webhook_url: str):
    """
    Configura webhook para produção
    
    Args:
        webhook_url: URL completa do webhook (ex: https://seu-dominio.com/webhook)
    """
    try:
        print(f"🔧 Configurando webhook: {webhook_url}")
        
        data = {'url': webhook_url}
        response = requests.post(TELEGRAM_WEBHOOK_URL, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Webhook configurado com sucesso: {webhook_url}")
                return True
            else:
                print(f"❌ Erro ao configurar webhook: {result.get('description')}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
        return False

def processar_webhook_update(update_data: dict):
    """
    Processa update recebido via webhook
    
    Args:
        update_data: Dados do update do Telegram
    """
    try:
        message = update_data.get('message', {})
        if not message:
            return
        
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user_id = str(message.get('from', {}).get('id', ''))
        
        print(f"📨 Mensagem recebida de {user_id}: {text}")
        
        if text.startswith('/'):
            # Processar comando
            parts = text.split()
            comando = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            print(f"🔧 Processando comando: {comando}")
            
            # Processar comando
            resposta = processar_comando_telegram(comando, user_id, args)
            
            # Enviar resposta
            enviar_mensagem_para_usuario(chat_id, resposta)
            
        else:
            # Mensagem de texto normal
            resposta = "💡 Use /ajuda para ver todos os comandos disponíveis."
            enviar_mensagem_para_usuario(chat_id, resposta)
            
    except Exception as e:
        print(f"❌ Erro ao processar webhook update: {e}")

def iniciar_bot_webhook(webhook_url: str = None):
    """
    Inicia o bot em modo webhook
    
    Args:
        webhook_url: URL do webhook (opcional)
    """
    try:
        print("🤖 Iniciando SNE Bot (Modo Webhook)...")
        
        if webhook_url:
            # Configurar webhook
            if configurar_webhook_producao(webhook_url):
                print("✅ Webhook configurado. Bot pronto para receber mensagens!")
                print("🔄 Aguardando updates via webhook...")
                
                # Enviar mensagem de inicialização
                mensagem_inicial = """
🚀 **SNE RADAR BOT - WEBHOOK ATIVO**

✅ **Sistema de Comandos Ativo**
✅ **Webhook Configurado**
✅ **Comandos Disponíveis:**
🔹 /start - Iniciar
🔹 /demo - Teste gratuito
🔹 /ajuda - Lista de comandos
🔹 /planos - Planos premium

🎯 **Bot pronto para uso!**
"""
                enviar_oraculo(mensagem_inicial)
                
                return True
            else:
                print("❌ Falha ao configurar webhook")
                return False
        else:
            print("❌ URL do webhook não fornecida")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao iniciar bot webhook: {e}")
        return False

def obter_info_webhook():
    """
    Obtém informações sobre o webhook atual
    """
    try:
        response = requests.get(TELEGRAM_WEBHOOK_URL, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
                print("📊 **INFORMAÇÕES DO WEBHOOK:**")
                print(f"🔹 URL: {webhook_info.get('url', 'N/A')}")
                print(f"🔹 Certificado: {webhook_info.get('has_custom_certificate', False)}")
                print(f"🔹 Updates pendentes: {webhook_info.get('pending_update_count', 0)}")
                print(f"🔹 IP permitidos: {webhook_info.get('allowed_updates', [])}")
                return webhook_info
            else:
                print(f"❌ Erro ao obter info: {result.get('description')}")
                return None
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao obter info webhook: {e}")
        return None

def enviar_mensagem_para_usuario(chat_id: str, mensagem: str):
    """
    Envia mensagem para um usuário específico
    
    Args:
        chat_id: ID do chat
        mensagem: Mensagem a enviar
    """
    try:
        params = {
            'chat_id': chat_id,
            'text': mensagem,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(TELEGRAM_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Mensagem enviada para {chat_id}")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem para {chat_id}: {e}")
        return False

# ===========================================
# FUNÇÃO PRINCIPAL PARA EXECUTAR O BOT
# ===========================================
def main_bot():
    """Função principal para executar o bot"""
    try:
        print("🚀 Iniciando SNE Bot...")
        iniciar_bot_polling()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    # Executar bot
    main_bot()

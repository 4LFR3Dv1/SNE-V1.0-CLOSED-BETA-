#!/usr/bin/env python3
"""
Bot Telegram SNE Radar - Versão Simplificada para Teste
"""

import requests
import time
import sys
import os

# Adicionar path
sys.path.append(os.getcwd())

# Configurações do Telegram
TELEGRAM_TOKEN = "7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
TELEGRAM_GET_UPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

def enviar_mensagem(chat_id, mensagem):
    """Envia mensagem para o Telegram"""
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
            print(f"❌ Erro ao enviar: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def obter_mensagens():
    """Obtém mensagens do Telegram"""
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

def processar_comando(comando, user_id, chat_id):
    """Processa comandos simples"""
    comando_limpo = comando.replace('/', '').lower()
    
    if comando_limpo == 'start':
        mensagem = """
🚀 **Bem-vindo ao SNE Radar!**

🎯 **Sistema de Análise Técnica Profissional**
📊 Análise multi-timeframe + DOM + Gestão de Risco

💡 **Comandos disponíveis:**
🔹 /demo - Teste gratuito
🔹 /ajuda - Lista completa
🔹 /status - Status da conta

🎯 **Comece com:** /demo BTCUSDT
"""
    elif comando_limpo == 'demo':
        mensagem = """
📊 **ANÁLISE DEMO - BTCUSDT**

💰 **Preço:** $106,837.87
📈 **Tendência:** Lateral
⭐ **Score:** 7.5/10
💡 **Recomendação:** Aguardar confirmação

📍 **Níveis:**
🔹 Suporte: $105,000
🔹 Resistência: $108,000

⚠️ **Limitação:** Análise simplificada
🚀 **Upgrade:** /planos para análise completa
"""
    elif comando_limpo == 'ajuda':
        mensagem = """
📋 **COMANDOS DISPONÍVEIS**

🔹 **BÁSICOS:**
/start - Iniciar bot
/demo - Teste gratuito
/ajuda - Esta lista
/status - Status da conta

💡 **Exemplos:**
• /demo BTCUSDT
• /ajuda
"""
    elif comando_limpo == 'status':
        mensagem = """
📊 **MINHA CONTA**

🔹 **Plano:** FREE
🔹 **Status:** ✅ Ativo
🔹 **Análises hoje:** 1/3
🔹 **Alertas ativos:** 0

📅 **Criado em:** Hoje
📅 **Última atividade:** Agora

💡 **Funcionalidades:**
✅ Análise básica
✅ Demo gratuito
✅ Comandos básicos

🎯 **Upgrade:** /planos
"""
    else:
        mensagem = "❌ Comando não reconhecido. Use /ajuda para ver todos os comandos."
    
    # Enviar resposta
    enviar_mensagem(chat_id, mensagem)

def main():
    """Função principal"""
    try:
        print("🤖 INICIANDO BOT TELEGRAM SNE RADAR")
        print("=" * 50)
        
        # Enviar mensagem de inicialização
        chat_id_admin = "6457067653"
        mensagem_inicial = """
🚀 **SNE RADAR BOT - SISTEMA INICIADO**

✅ **Sistema de Comandos Ativo**
✅ **Comandos Disponíveis:**
🔹 /start - Iniciar
🔹 /demo - Teste gratuito
🔹 /ajuda - Lista de comandos

🎯 **Bot pronto para uso!**
"""
        enviar_mensagem(chat_id_admin, mensagem_inicial)
        
        print("✅ Bot iniciado!")
        print("🔄 Aguardando mensagens...")
        print("⚠️  Pressione Ctrl+C para parar")
        
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
                            
                            print(f"📨 Mensagem recebida: {text} de {user_id}")
                            
                            if text.startswith('/'):
                                # Processar comando
                                processar_comando(text, user_id, chat_id)
                            else:
                                # Mensagem de texto normal
                                resposta = "💡 Use /ajuda para ver todos os comandos disponíveis."
                                enviar_mensagem(chat_id, resposta)
                
                # Aguardar antes da próxima verificação
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no loop: {e}")
                time.sleep(5)
        
        print("✅ Bot encerrado")
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

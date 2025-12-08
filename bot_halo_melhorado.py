#!/usr/bin/env python3
"""
Bot HALO - Modo Polling Ativo (Versão Corrigida)
"""

import requests
import time
import json

def main():
    # Configurações do bot
    TELEGRAM_TOKEN = '7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y'
    TELEGRAM_GET_UPDATES_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates'
    TELEGRAM_SEND_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    
    print('🤖 BOT HALO - MODO POLLING ATIVO')
    print('=' * 40)
    print('🔄 Aguardando mensagens...')
    print('⚠️  Pressione Ctrl+C para parar')
    
    last_update_id = 0
    processed_updates = set()
    
    while True:
        try:
            # Obter mensagens
            response = requests.get(TELEGRAM_GET_UPDATES_URL, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])
                    
                    for update in updates:
                        update_id = update.get('update_id')
                        
                        if update_id > last_update_id:
                            last_update_id = update_id
                            
                            # Processar mensagem apenas uma vez
                            if update_id not in processed_updates:
                                processed_updates.add(update_id)
                                
                                message = update.get('message', {})
                                if message:
                                    chat_id = message.get('chat', {}).get('id')
                                    text = message.get('text', '')
                                    user_id = str(message.get('from', {}).get('id', ''))
                                    
                                    print(f'📨 Mensagem de {user_id}: {text}')
                                    
                                    if text.startswith('/'):
                                        # Processar comando
                                        if text == '/start':
                                            resposta = '''🚀 **Bem-vindo ao SNE Radar!**

🎯 **Sistema de Análise Técnica Profissional**
📊 Análise multi-timeframe + DOM + Gestão de Risco

💡 **Comandos disponíveis:**
🔹 /demo - Análise demo gratuita
🔹 /ajuda - Lista completa de comandos
🔹 /planos - Planos premium disponíveis
🔹 /status - Status da sua conta

🎯 **Comece com:** /demo para testar
📈 **Upgrade:** /planos para análise completa

💳 **Sistema de pagamento ativo!**'''
                                        
                                        elif text == '/demo':
                                            resposta = '''📊 **ANÁLISE DEMO - BTCUSDT**

💰 **Preço Atual:** $106,837.87
📈 **Tendência:** Lateral com viés de alta
⭐ **Score:** 7.5/10
💡 **Recomendação:** Aguardar confirmação

📍 **Níveis Operacionais:**
🔹 Suporte: $106,800 (EMA 21)
🔹 Resistência: $107,500 (Máxima recente)
🔹 Entry: $107,200 (Quebra de resistência)

📊 **Indicadores:**
🔹 RSI: 52 (Neutro)
🔹 MACD: Convergência positiva
🔹 Volume: Baixo (aguardar confirmação)

🎯 **Setup Operacional:**
• **LONG:** Acima de $107,200
• **SL:** $106,500 (-0.7%)
• **TP1:** $108,000 (+0.7%)
• **TP2:** $108,500 (+1.6%)

⚠️ **Limitação:** Análise simplificada
🚀 **Upgrade:** /planos para análise completa'''
                                        
                                        elif text == '/ajuda':
                                            resposta = '''📋 **COMANDOS DISPONÍVEIS**

🔹 **BÁSICOS:**
/start - Iniciar bot
/demo - Análise demo gratuita
/ajuda - Esta lista
/planos - Planos premium
/status - Status da conta

💡 **Exemplos:**
• /demo - Teste gratuito
• /planos - Ver opções premium
• /status - Minha conta'''
                                        
                                        elif text == '/planos':
                                            resposta = '''💳 **PLANOS SNE RADAR**

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
📧 sne.radar@email.com'''
                                        
                                        elif text == '/status':
                                            resposta = '''📊 **MINHA CONTA**

🔹 **Plano:** FREE
🔹 **Status:** ✅ Ativo
🔹 **Análises hoje:** 1/3
🔹 **Alertas ativos:** 0

📅 **Criado em:** 18/10/2025
📅 **Última atividade:** Agora

💡 **Funcionalidades:**
✅ 3 análises/dia
✅ Comandos básicos
✅ Demo gratuito

🎯 **Upgrade:** /planos'''
                                        
                                        else:
                                            resposta = '❌ Comando não reconhecido. Use /ajuda para ver todos os comandos.'
                                        
                                        # Enviar resposta
                                        params = {
                                            'chat_id': chat_id,
                                            'text': resposta,
                                            'parse_mode': 'HTML'
                                        }
                                        
                                        response_send = requests.post(TELEGRAM_SEND_URL, params=params, timeout=10)
                                        
                                        if response_send.status_code == 200:
                                            print(f'✅ Resposta enviada para {user_id}')
                                        else:
                                            print(f'❌ Erro ao enviar resposta: {response_send.status_code}')
                                        
                                    else:
                                        # Mensagem de texto normal
                                        resposta = '💡 Use /ajuda para ver todos os comandos disponíveis.'
                                        
                                        params = {
                                            'chat_id': chat_id,
                                            'text': resposta,
                                            'parse_mode': 'HTML'
                                        }
                                        
                                        requests.post(TELEGRAM_SEND_URL, params=params, timeout=10)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print('\n🛑 Bot interrompido pelo usuário')
            break
        except Exception as e:
            print(f'❌ Erro: {e}')
            time.sleep(5)

    print('✅ Bot encerrado')

if __name__ == "__main__":
    main()

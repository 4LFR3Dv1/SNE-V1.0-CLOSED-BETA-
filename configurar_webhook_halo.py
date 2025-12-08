#!/usr/bin/env python3
"""
Configurador de Webhook para Bot HALO
"""

import requests
import json

def configurar_webhook_halo():
    print("🔧 CONFIGURADOR DE WEBHOOK - BOT HALO")
    print("=" * 45)
    
    # Configurações do bot
    TELEGRAM_TOKEN = "7970664442:AAHTBoX69oRH-r_FxMXWDw8EZjnxxeBd69Y"
    TELEGRAM_WEBHOOK_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    TELEGRAM_GET_WEBHOOK_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    
    print(f"✅ Bot: @xenosv0_bot")
    print(f"✅ Token: {TELEGRAM_TOKEN[:10]}...")
    
    # Verificar webhook atual
    print("\n🔍 Verificando webhook atual...")
    
    try:
        response = requests.get(TELEGRAM_GET_WEBHOOK_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                webhook_info = data.get('result', {})
                print("📊 **WEBHOOK ATUAL:**")
                print(f"🔹 URL: {webhook_info.get('url', 'N/A')}")
                print(f"🔹 Certificado: {webhook_info.get('has_custom_certificate', False)}")
                print(f"🔹 Updates pendentes: {webhook_info.get('pending_update_count', 0)}")
                print(f"🔹 IP permitidos: {webhook_info.get('allowed_updates', [])}")
            else:
                print(f"❌ Erro na API: {data.get('description')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Opções de configuração
    print("\n📋 OPÇÕES DISPONÍVEIS:")
    print("1) Configurar webhook")
    print("2) Remover webhook (usar polling)")
    print("3) Ver informações do webhook")
    print("4) Sair")
    
    opcao = input("\nEscolha uma opção (1-4): ").strip()
    
    if opcao == "1":
        webhook_url = input("Digite a URL do webhook: ").strip()
        if webhook_url:
            print(f"\n🔧 Configurando webhook: {webhook_url}")
            
            data = {'url': webhook_url}
            response = requests.post(TELEGRAM_WEBHOOK_URL, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print("✅ Webhook configurado com sucesso!")
                    print(f"📡 URL: {webhook_url}")
                else:
                    print(f"❌ Erro ao configurar webhook: {result.get('description')}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
        else:
            print("❌ URL não fornecida")
            
    elif opcao == "2":
        print("\n🔧 Removendo webhook...")
        
        data = {'url': ''}
        response = requests.post(TELEGRAM_WEBHOOK_URL, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook removido. Bot em modo polling.")
            else:
                print(f"❌ Erro ao remover webhook: {result.get('description')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    elif opcao == "3":
        print("\n🔍 Informações do webhook:")
        # Já mostrado acima
        
    elif opcao == "4":
        print("👋 Saindo...")
        
    else:
        print("❌ Opção inválida")

if __name__ == "__main__":
    configurar_webhook_halo()

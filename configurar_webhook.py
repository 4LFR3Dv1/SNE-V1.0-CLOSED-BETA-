#!/usr/bin/env python3
"""
Script para configurar webhook do Telegram
"""

import sys
import os

# Adicionar o diretório atual ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🔧 CONFIGURADOR DE WEBHOOK TELEGRAM")
    print("=" * 40)
    
    try:
        from xenos_bot import (
            configurar_webhook_producao, 
            obter_info_webhook,
            configurar_webhook
        )
        
        print("✅ Módulo xenos_bot importado com sucesso")
        
        # Mostrar opções
        print("\n📋 OPÇÕES DISPONÍVEIS:")
        print("1) Configurar webhook")
        print("2) Ver informações do webhook")
        print("3) Remover webhook (usar polling)")
        print("4) Sair")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            webhook_url = input("Digite a URL do webhook: ").strip()
            if webhook_url:
                if configurar_webhook_producao(webhook_url):
                    print("✅ Webhook configurado com sucesso!")
                else:
                    print("❌ Falha ao configurar webhook")
            else:
                print("❌ URL não fornecida")
                
        elif opcao == "2":
            info = obter_info_webhook()
            if info:
                print("✅ Informações obtidas com sucesso!")
            else:
                print("❌ Falha ao obter informações")
                
        elif opcao == "3":
            if configurar_webhook():
                print("✅ Webhook removido. Bot em modo polling.")
            else:
                print("❌ Falha ao remover webhook")
                
        elif opcao == "4":
            print("👋 Saindo...")
            
        else:
            print("❌ Opção inválida")
            
    except ImportError as e:
        print(f"❌ Erro ao importar xenos_bot: {e}")
        print("💡 Verifique se o arquivo xenos_bot.py existe")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

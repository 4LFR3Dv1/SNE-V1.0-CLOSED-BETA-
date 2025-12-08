#!/usr/bin/env python3
"""
Script para executar o Bot Telegram SNE Radar
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

def main():
    """
    Função principal para executar o bot
    """
    try:
        print("🚀 INICIANDO BOT TELEGRAM SNE RADAR")
        print("=" * 50)
        
        # Importar e executar o bot
        from xenos_bot import iniciar_bot_polling
        
        print("✅ Módulos carregados com sucesso")
        print("🤖 Iniciando bot em modo polling...")
        print("📱 Aguardando mensagens do Telegram...")
        print("⚠️  Pressione Ctrl+C para parar")
        print("=" * 50)
        
        # Executar bot
        iniciar_bot_polling()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot interrompido pelo usuário")
        print("✅ Bot encerrado com sucesso")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

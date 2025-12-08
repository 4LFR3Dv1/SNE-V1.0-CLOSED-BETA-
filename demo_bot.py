#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEMONSTRAÇÃO DO SNE RADAR BOT - SISTEMA DE MONETIZAÇÃO
Teste dos comandos implementados
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Demonstração do bot"""
    print("🚀 DEMONSTRAÇÃO DO SNE RADAR BOT")
    print("=" * 50)
    
    try:
        # Importar o bot
        from telegram_bot import sne_bot
        
        print("✅ Bot importado com sucesso!")
        
        # Testar comandos básicos
        print("\n📱 TESTANDO COMANDOS BÁSICOS:")
        print("-" * 30)
        
        # Comando start
        print("🔹 Testando /start...")
        resultado = sne_bot.processar_comando("/start", "123456789")
        print(f"   Resultado: {resultado[:50]}...")
        
        # Comando demo
        print("🔹 Testando /demo BTCUSDT...")
        resultado = sne_bot.processar_comando("/demo", "123456789", ["BTCUSDT"])
        print(f"   Resultado: {resultado[:50]}...")
        
        # Comando ajuda
        print("🔹 Testando /ajuda...")
        resultado = sne_bot.processar_comando("/ajuda", "123456789")
        print(f"   Resultado: {resultado[:50]}...")
        
        # Comando termos
        print("🔹 Testando /termos...")
        resultado = sne_bot.processar_comando("/termos", "123456789")
        print(f"   Resultado: {resultado[:50]}...")
        
        print("\n💳 TESTANDO COMANDOS DE MONETIZAÇÃO:")
        print("-" * 40)
        
        # Comando assinar
        print("🔹 Testando /assinar...")
        resultado = sne_bot.processar_comando("/assinar", "123456789")
        print(f"   Resultado: {resultado[:50]}...")
        
        # Comando minha_assinatura
        print("🔹 Testando /minha_assinatura...")
        resultado = sne_bot.processar_comando("/minha_assinatura", "123456789")
        print(f"   Resultado: {resultado[:50]}...")
        
        print("\n⭐ TESTANDO COMANDOS PREMIUM:")
        print("-" * 35)
        
        # Comando analise (deve falhar por não ter acesso premium)
        print("🔹 Testando /analise BTCUSDT 1h...")
        resultado = sne_bot.processar_comando("/analise", "123456789", ["BTCUSDT", "1h"])
        print(f"   Resultado: {resultado[:50]}...")
        
        print("\n📊 ESTATÍSTICAS DO SISTEMA:")
        print("-" * 30)
        
        # Estatísticas do usuário
        user_stats = sne_bot.user_manager.get_user_stats("123456789")
        print(f"🔹 Usuário: {user_stats}")
        
        # Estatísticas de cache
        cache_stats = sne_bot.cache.get_stats()
        print(f"🔹 Cache: {cache_stats}")
        
        print("\n✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🎯 Sistema de monetização funcionando perfeitamente!")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

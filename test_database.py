#!/usr/bin/env python3
"""
Script para testar a configuração do banco de dados
"""

import os
import sys
from database_config import get_database_url, test_connection, print_config_status

def main():
    print("🔍 TESTE DE CONFIGURAÇÃO DO BANCO DE DADOS")
    print("=" * 50)
    
    # Mostrar status atual
    print_config_status()
    
    print("\n" + "=" * 50)
    print("🧪 TESTANDO CONFIGURAÇÕES:")
    
    # Testar configuração local
    print("\n📊 Testando configuração LOCAL:")
    local_url = get_database_url('local')
    print(f"   URL: {local_url}")
    local_ok = test_connection('local')
    print(f"   Conexão: {'✅ OK' if local_ok else '❌ Falha'}")
    
    # Testar configuração de produção
    print("\n📊 Testando configuração PRODUCTION:")
    prod_url = get_database_url('production')
    print(f"   URL: {'Configurada' if prod_url else 'Não configurada'}")
    if prod_url:
        # Não mostrar a URL completa por segurança
        print(f"   URL: {prod_url[:20]}...")
    prod_ok = test_connection('production')
    print(f"   Conexão: {'✅ OK' if prod_ok else '❌ Falha'}")
    
    # Testar detecção automática
    print("\n📊 Testando detecção automática:")
    auto_url = get_database_url()
    print(f"   Ambiente detectado: {'production' if os.environ.get('FLASK_ENV') == 'production' else 'local'}")
    print(f"   URL: {auto_url}")
    
    print("\n" + "=" * 50)
    print("📋 RESUMO:")
    print(f"   Local: {'✅' if local_ok else '❌'}")
    print(f"   Production: {'✅' if prod_ok else '❌'}")
    print(f"   Auto-detecção: {'✅' if auto_url else '❌'}")
    
    if local_ok and auto_url:
        print("\n🎉 Configuração funcionando corretamente!")
        return 0
    else:
        print("\n⚠️  Alguns problemas encontrados. Verifique as configurações.")
        return 1

if __name__ == "__main__":
    sys.exit(main())




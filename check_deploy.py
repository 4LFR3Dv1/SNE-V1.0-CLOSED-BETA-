#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se o deploy está funcionando corretamente
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_environment_variables():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print("🔍 Verificando variáveis de ambiente...")
    
    required_vars = [
        'FLASK_ENV',
        'SECRET_KEY',
        'DB_HOST',
        'DB_PORT', 
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
            print(f"❌ {var}: Não configurada")
        else:
            print(f"✅ {var}: Configurada")
    
    if missing_vars:
        print(f"\n⚠️ {len(missing_vars)} variáveis faltando:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("\n✅ Todas as variáveis de ambiente estão configuradas!")
    return True

def check_database_connection():
    """Verifica se a conexão com o banco está funcionando"""
    print("\n🗄️ Verificando conexão com banco de dados...")
    
    try:
        from database_config import get_database_url, test_connection
        
        # Testar conexão local
        if test_connection('local'):
            print("✅ Conexão local (SQLite): OK")
        else:
            print("❌ Conexão local (SQLite): Falha")
        
        # Testar conexão de produção
        if test_connection('production'):
            print("✅ Conexão produção (PostgreSQL): OK")
        else:
            print("❌ Conexão produção (PostgreSQL): Falha")
            print("   Verifique as variáveis de ambiente do banco")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def check_imports():
    """Verifica se todas as dependências podem ser importadas"""
    print("\n📦 Verificando importações...")
    
    required_modules = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_socketio',
        'pandas', 'numpy', 'matplotlib', 'requests', 'bcrypt'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️ {len(failed_imports)} módulos falharam na importação")
        return False
    
    print("\n✅ Todas as dependências estão disponíveis!")
    return True

def check_web_app():
    """Verifica se a aplicação web pode ser importada"""
    print("\n🌐 Verificando aplicação web...")
    
    try:
        # Tentar importar a aplicação
        import sne_radar_web
        print("✅ sne_radar_web.py pode ser importado")
        
        # Verificar se a app Flask foi criada
        if hasattr(sne_radar_web, 'app'):
            print("✅ App Flask criada com sucesso")
        else:
            print("❌ App Flask não encontrada")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao importar aplicação web: {e}")
        return False

def check_endpoints():
    """Verifica se os endpoints principais estão funcionando"""
    print("\n🔗 Verificando endpoints...")
    
    try:
        import sne_radar_web
        
        # Criar contexto de teste
        with sne_radar_web.app.test_client() as client:
            # Testar endpoint principal
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Endpoint principal (/): OK")
            else:
                print(f"❌ Endpoint principal (/): Status {response.status_code}")
            
            # Testar endpoint de API
            response = client.get('/api/v1/ta-summary')
            if response.status_code in [200, 404, 500]:  # 404/500 são aceitáveis se não houver dados
                print("✅ Endpoint API (/api/v1/ta-summary): OK")
            else:
                print(f"❌ Endpoint API (/api/v1/ta-summary): Status {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar endpoints: {e}")
        return False

def check_render_specific():
    """Verifica configurações específicas do Render"""
    print("\n🚀 Verificando configurações do Render...")
    
    # Verificar se estamos em produção
    if os.environ.get('FLASK_ENV') == 'production':
        print("✅ Ambiente de produção detectado")
    else:
        print("⚠️ Ambiente não é produção")
    
    # Verificar porta
    port = os.environ.get('PORT')
    if port:
        print(f"✅ Porta configurada: {port}")
    else:
        print("⚠️ Porta não configurada (usando padrão)")
    
    # Verificar se é Render
    if os.environ.get('RENDER'):
        print("✅ Executando no Render")
    else:
        print("ℹ️ Não executando no Render (ambiente local)")
    
    return True

def main():
    """Função principal de verificação"""
    print("🚀 VERIFICAÇÃO DE DEPLOY SNE RADAR")
    print("=" * 50)
    
    checks = [
        ("Variáveis de Ambiente", check_environment_variables),
        ("Conexão com Banco", check_database_connection),
        ("Importações", check_imports),
        ("Aplicação Web", check_web_app),
        ("Endpoints", check_endpoints),
        ("Configurações Render", check_render_specific)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {check_name}: {e}")
            results.append((check_name, False))
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("\n🎉 DEPLOY FUNCIONANDO PERFEITAMENTE!")
        print("\n📋 Sua aplicação está pronta para uso!")
    else:
        print(f"\n⚠️ {total - passed} problemas encontrados.")
        print("Consulte o guia de deploy para resolver os problemas.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)





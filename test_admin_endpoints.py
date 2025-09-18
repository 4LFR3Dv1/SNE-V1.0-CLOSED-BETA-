#!/usr/bin/env python3
# -*- coding: utf-8
"""
Script para testar os endpoints administrativos do SNE Radar
"""

import requests
import json
from datetime import datetime

def test_admin_endpoints():
    """Testa os endpoints administrativos"""
    
    base_url = "http://localhost:9999"
    
    print("🔍 TESTANDO ENDPOINTS ADMINISTRATIVOS")
    print("=" * 50)
    print(f"🌐 URL Base: {base_url}")
    print(f"⏰ Teste: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista de endpoints para testar
    endpoints = [
        "/admin",
        "/api/admin/users/stats",
        "/api/admin/users/list",
        "/api/admin/users/1",
        "/api/admin/system/stats"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"🔍 Testando: {endpoint}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ OK - Status: {response.status_code}")
                try:
                    data = response.json()
                    print(f"   📄 JSON válido: {json.dumps(data, indent=2)[:100]}...")
                except:
                    print(f"   📄 HTML/Texto: {response.text[:100]}...")
            elif response.status_code == 401:
                print(f"   🔒 Não autorizado - Status: {response.status_code}")
                print(f"   💡 Endpoint protegido (requer login)")
            elif response.status_code == 403:
                print(f"   🚫 Acesso negado - Status: {response.status_code}")
                print(f"   💡 Endpoint protegido (requer admin)")
            elif response.status_code == 404:
                print(f"   ❌ Não encontrado - Status: {response.status_code}")
            else:
                print(f"   ⚠️ Status inesperado: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro de conexão - Sistema offline")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout - Sistema lento")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print()
    
    print("🏁 TESTE CONCLUÍDO")
    print("=" * 50)

def test_with_auth():
    """Testa endpoints com autenticação"""
    
    base_url = "http://localhost:9999"
    
    print("\n🔐 TESTANDO COM AUTENTICAÇÃO")
    print("=" * 40)
    
    # Dados de login
    login_data = {
        'username': 'admin',
        'password': 'Admin123!'
    }
    
    try:
        # Fazer login
        print("🔑 Fazendo login...")
        session = requests.Session()
        
        login_response = session.post(f"{base_url}/login", data=login_data, timeout=5)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso!")
            
            # Testar endpoints protegidos
            admin_endpoints = [
                "/admin",
                "/api/admin/users/stats"
            ]
            
            for endpoint in admin_endpoints:
                try:
                    url = f"{base_url}{endpoint}"
                    print(f"\n🔍 Testando protegido: {endpoint}")
                    
                    response = session.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        print(f"   ✅ Acesso permitido!")
                        try:
                            data = response.json()
                            print(f"   📊 Dados: {json.dumps(data, indent=2)}")
                        except:
                            print(f"   📄 Conteúdo: {response.text[:200]}...")
                    else:
                        print(f"   ❌ Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
        else:
            print(f"❌ Falha no login: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste de autenticação: {e}")

def main():
    """Função principal"""
    print("🚀 SNE RADAR - TESTE DE ENDPOINTS ADMIN")
    print("=" * 60)
    
    # Testar endpoints sem autenticação
    test_admin_endpoints()
    
    # Testar endpoints com autenticação
    test_with_auth()
    
    print("\n💡 INSTRUÇÕES:")
    print("1. Certifique-se de que o sistema está rodando (python3 sne_radar_web.py)")
    print("2. Verifique se as rotas administrativas foram importadas")
    print("3. Teste o acesso via navegador: http://localhost:9999/admin")

if __name__ == "__main__":
    main()


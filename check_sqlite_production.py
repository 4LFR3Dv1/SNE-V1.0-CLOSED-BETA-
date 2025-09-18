#!/usr/bin/env python3
# -*- coding: utf-8
"""
Script para verificar se o sistema em produção usa SQLite
e tentar acessar os dados dos usuários
"""

import requests
import json
from datetime import datetime

def verificar_configuracao_producao():
    """Verifica como o sistema em produção está configurado"""
    
    base_url = "https://sne-radar-jwr2.onrender.com"
    
    print("🔍 VERIFICANDO CONFIGURAÇÃO DO SISTEMA EM PRODUÇÃO")
    print("=" * 60)
    print(f"🌐 URL: {base_url}")
    print(f"⏰ Verificação: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Verificar se o sistema está online
        print("📡 Testando conectividade...")
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Sistema online e respondendo")
        else:
            print(f"⚠️ Sistema respondeu com status: {response.status_code}")
            return
        
        # Verificar se há algum endpoint que possa revelar informações
        print("\n🔍 Verificando endpoints para informações do sistema...")
        
        # Tentar acessar endpoints que podem dar informações sobre o sistema
        endpoints_info = [
            "/api/system/info",
            "/api/status",
            "/health",
            "/info",
            "/debug"
        ]
        
        for endpoint in endpoints_info:
            try:
                endpoint_url = f"{base_url}{endpoint}"
                resp = requests.get(endpoint_url, timeout=5)
                
                if resp.status_code == 200:
                    print(f"✅ {endpoint} - Retornou dados")
                    try:
                        data = resp.json()
                        print(f"   📄 Conteúdo: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"   📄 Conteúdo: {resp.text[:200]}...")
                elif resp.status_code == 404:
                    print(f"❌ {endpoint} - Não encontrado")
                else:
                    print(f"⚠️ {endpoint} - Status: {resp.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - Erro: {e}")
        
        # Verificar se há variáveis de ambiente expostas
        print("\n🔍 Verificando se há variáveis de ambiente expostas...")
        
        # Tentar acessar arquivos que podem conter configurações
        config_files = [
            "/.env",
            "/config.json",
            "/env",
            "/environment"
        ]
        
        for config_file in config_files:
            try:
                config_url = f"{base_url}{config_file}"
                resp = requests.get(config_url, timeout=5)
                
                if resp.status_code == 200:
                    print(f"⚠️ {config_file} - ACESSÍVEL (possível problema de segurança)")
                    print(f"   📄 Conteúdo: {resp.text[:200]}...")
                elif resp.status_code == 404:
                    print(f"✅ {config_file} - Não encontrado (seguro)")
                else:
                    print(f"⚠️ {config_file} - Status: {resp.status_code}")
                    
            except Exception as e:
                print(f"❌ {config_file} - Erro: {e}")
        
        # Verificar se há logs ou informações de debug
        print("\n🔍 Verificando se há informações de debug...")
        
        # Tentar acessar com headers que podem revelar informações
        headers_debug = {
            'User-Agent': 'Mozilla/5.0 (compatible; SNE-Radar-Debug/1.0)',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        try:
            debug_resp = requests.get(base_url, headers=headers_debug, timeout=5)
            print(f"📡 Headers da resposta:")
            for key, value in debug_resp.headers.items():
                if key.lower() in ['server', 'x-powered-by', 'x-runtime', 'x-version']:
                    print(f"   {key}: {value}")
        except Exception as e:
            print(f"❌ Erro ao verificar headers: {e}")
        
        print("\n🎯 ANÁLISE DA SITUAÇÃO:")
        print("=" * 40)
        
        if response.status_code == 200:
            print("✅ Sistema funcionando corretamente")
            print("\n💡 POSSÍVEIS CONFIGURAÇÕES:")
            print("   1. Sistema usa SQLite local em produção")
            print("   2. Sistema usa banco interno do Render")
            print("   3. Sistema usa variáveis de ambiente não expostas")
            print("\n🔧 PRÓXIMOS PASSOS:")
            print("   1. Verificar logs no dashboard do Render")
            print("   2. Verificar configurações do serviço web")
            print("   3. Verificar se há banco de dados separado")
        else:
            print("❌ Sistema com problemas")
            print("💡 Verifique logs no Render")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - Sistema pode estar lento ou offline")
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Sistema offline ou URL incorreta")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def tentar_acessar_dados_via_api():
    """Tenta acessar dados via APIs do sistema"""
    
    base_url = "https://sne-radar-jwr2.onrender.com"
    
    print("\n" + "=" * 60)
    print("🔍 TENTANDO ACESSAR DADOS VIA API")
    print("=" * 60)
    
    # Tentar acessar APIs que podem retornar dados de usuários
    apis_usuarios = [
        "/api/users",
        "/api/admin/users",
        "/api/users/list",
        "/api/users/stats",
        "/api/admin/stats"
    ]
    
    for api in apis_usuarios:
        try:
            api_url = f"{base_url}{api}"
            resp = requests.get(api_url, timeout=5)
            
            if resp.status_code == 200:
                print(f"✅ {api} - Dados disponíveis!")
                try:
                    data = resp.json()
                    print(f"   📊 Conteúdo: {json.dumps(data, indent=2)}")
                except:
                    print(f"   📄 Conteúdo: {resp.text}")
            elif resp.status_code == 401:
                print(f"🔒 {api} - Protegido (requer autenticação)")
            elif resp.status_code == 404:
                print(f"❌ {api} - Não encontrado")
            else:
                print(f"⚠️ {api} - Status: {resp.status_code}")
                
        except Exception as e:
            print(f"❌ {api} - Erro: {e}")

def main():
    """Função principal"""
    print("🚀 SNE RADAR - INVESTIGADOR DE CONFIGURAÇÃO")
    print("=" * 60)
    
    # Verificar configuração geral
    verificar_configuracao_producao()
    
    # Tentar acessar dados via API
    tentar_acessar_dados_via_api()
    
    print("\n" + "=" * 60)
    print("🏁 INVESTIGAÇÃO CONCLUÍDA")
    print("=" * 60)
    
    print("\n💡 RECOMENDAÇÕES:")
    print("1. Verifique o dashboard do Render para logs")
    print("2. Verifique as configurações do serviço web")
    print("3. Verifique se há banco de dados separado")
    print("4. Considere usar o sistema web diretamente")

if __name__ == "__main__":
    main()


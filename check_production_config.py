#!/usr/bin/env python3
# -*- coding: utf-8
"""
Script para verificar a configuração do sistema SNE Radar em produção
"""

import requests
import json
from datetime import datetime

def verificar_sistema_producao():
    """Verifica a configuração do sistema em produção"""
    
    base_url = "https://sne-radar-jwr2.onrender.com"
    
    print("🔍 VERIFICANDO SISTEMA EM PRODUÇÃO")
    print("=" * 50)
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
        
        # Verificar se há endpoint de API
        print("\n🔍 Verificando endpoints disponíveis...")
        
        endpoints = [
            "/login",
            "/register", 
            "/dashboard",
            "/api/market-data"
        ]
        
        for endpoint in endpoints:
            try:
                endpoint_url = f"{base_url}{endpoint}"
                resp = requests.get(endpoint_url, timeout=5)
                
                if resp.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                elif resp.status_code == 302:  # Redirect (normal para login)
                    print(f"✅ {endpoint} - Redirect (OK)")
                elif resp.status_code == 401:  # Unauthorized (normal para APIs protegidas)
                    print(f"✅ {endpoint} - Protegido (OK)")
                else:
                    print(f"⚠️ {endpoint} - Status: {resp.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - Erro: {e}")
        
        # Verificar se há usuários cadastrados (tentando acessar dashboard)
        print("\n👥 Verificando sistema de usuários...")
        try:
            # Tentar acessar dashboard (deve redirecionar para login se não autenticado)
            dashboard_resp = requests.get(f"{base_url}/dashboard", timeout=5, allow_redirects=False)
            
            if dashboard_resp.status_code == 302:
                print("✅ Sistema de autenticação ativo")
                print("✅ Redirecionamento para login funcionando")
            else:
                print(f"⚠️ Dashboard respondeu com: {dashboard_resp.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar dashboard: {e}")
        
        # Verificar se há dados de mercado
        print("\n📊 Verificando dados de mercado...")
        try:
            # Tentar acessar API de dados de mercado
            market_resp = requests.get(f"{base_url}/api/market-data", timeout=5)
            
            if market_resp.status_code == 401:
                print("✅ API de dados protegida (requer autenticação)")
            elif market_resp.status_code == 200:
                print("✅ API de dados acessível")
                try:
                    data = market_resp.json()
                    print(f"   📈 Dados disponíveis: {len(data) if isinstance(data, dict) else 'N/A'}")
                except:
                    print("   📄 Resposta não é JSON válido")
            else:
                print(f"⚠️ API respondeu com: {market_resp.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao verificar API de dados: {e}")
        
        print("\n🎯 RECOMENDAÇÕES:")
        print("=" * 30)
        
        if response.status_code == 200:
            print("✅ Sistema funcionando corretamente")
            print("💡 Para conectar ao banco de produção:")
            print("   1. Acesse o dashboard do Render")
            print("   2. Vá para 'Databases'")
            print("   3. Copie a DATABASE_URL")
            print("   4. Configure no script: export DATABASE_URL=sua_url")
        else:
            print("❌ Sistema com problemas")
            print("💡 Verifique logs no Render")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - Sistema pode estar lento ou offline")
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Sistema offline ou URL incorreta")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def verificar_banco_local():
    """Verifica a configuração do banco local"""
    print("\n" + "=" * 50)
    print("💻 VERIFICANDO BANCO LOCAL")
    print("=" * 50)
    
    try:
        import sqlite3
        import os
        
        db_path = 'instance/sne_radar.db'
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar estrutura
            cursor.execute("PRAGMA table_info(user)")
            colunas = cursor.fetchall()
            
            print(f"✅ Banco local encontrado: {db_path}")
            print(f"📊 Colunas na tabela user: {len(colunas)}")
            
            for col in colunas:
                print(f"   • {col[1]} ({col[2]})")
            
            # Verificar usuários
            cursor.execute("SELECT COUNT(*) FROM user")
            total_users = cursor.fetchone()[0]
            print(f"👥 Total de usuários: {total_users}")
            
            conn.close()
            
        else:
            print("❌ Banco local não encontrado")
            print("💡 Execute o sistema web local para criar o banco")
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco local: {e}")

def main():
    """Função principal"""
    print("🚀 SNE RADAR - VERIFICADOR DE CONFIGURAÇÃO")
    print("=" * 60)
    
    # Verificar sistema em produção
    verificar_sistema_producao()
    
    # Verificar banco local
    verificar_banco_local()
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICAÇÃO CONCLUÍDA")
    print("=" * 60)

if __name__ == "__main__":
    main()


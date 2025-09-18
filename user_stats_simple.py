#!/usr/bin/env python3
# -*- coding: utf-8
"""
Script simples para consultar usuários de produção do SNE Radar
Usa a variável DATABASE_URL (mesma do sistema em produção)
"""

import os
import sys
from datetime import datetime

def conectar_banco_producao():
    """Conecta ao banco de produção usando DATABASE_URL"""
    
    # Verificar se DATABASE_URL está configurada
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não configurada")
        print("\n💡 Para configurar:")
        print("   1. Acesse o dashboard do Render")
        print("   2. Vá para 'Databases'")
        print("   3. Copie a DATABASE_URL")
        print("   4. Configure: export DATABASE_URL=sua_url")
        print("\n   Exemplo:")
        print("   export DATABASE_URL=postgresql://user:pass@host:port/database")
        return None
    
    try:
        # Tentar conectar com psycopg2 (PostgreSQL)
        import psycopg2
        
        # Extrair informações da URL
        if database_url.startswith('postgresql://'):
            # Formato: postgresql://user:pass@host:port/database
            url_parts = database_url.replace('postgresql://', '').split('@')
            if len(url_parts) == 2:
                user_pass = url_parts[0].split(':')
                host_port_db = url_parts[1].split('/')
                
                if len(user_pass) == 2 and len(host_port_db) == 2:
                    username = user_pass[0]
                    password = user_pass[1]
                    host_port = host_port_db[0].split(':')
                    host = host_port[0]
                    port = host_port[1] if len(host_port) > 1 else '5432'
                    database = host_port_db[1]
                    
                    print(f"🔗 Conectando ao banco de produção...")
                    print(f"   Host: {host}")
                    print(f"   Port: {port}")
                    print(f"   Database: {database}")
                    print(f"   User: {username}")
                    
                    conn = psycopg2.connect(
                        host=host,
                        port=port,
                        database=database,
                        user=username,
                        password=password
                    )
                    
                    print("✅ Conectado ao banco de produção!")
                    return conn
                    
        print("❌ Formato de DATABASE_URL inválido")
        return None
        
    except ImportError:
        print("❌ psycopg2 não instalado")
        print("💡 Instale com: pip install psycopg2-binary")
        return None
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def verificar_estrutura_banco(conn):
    """Verifica a estrutura do banco de produção"""
    try:
        cursor = conn.cursor()
        
        # Verificar se a tabela user existe
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'user'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabela 'user' não encontrada")
            return []
        
        # Verificar colunas
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            ORDER BY ordinal_position
        """)
        
        colunas = cursor.fetchall()
        colunas_nomes = [col[0] for col in colunas]
        
        print(f"\n🔍 ESTRUTURA DO BANCO DE PRODUÇÃO:")
        print("=" * 50)
        for col in colunas:
            print(f"  • {col[0]} ({col[1]})")
        
        return colunas_nomes
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return []

def estatisticas_usuarios(conn, colunas_disponiveis):
    """Estatísticas dos usuários de produção"""
    try:
        cursor = conn.cursor()
        
        # Total de usuários
        cursor.execute('SELECT COUNT(*) FROM "user"')
        total_usuarios = cursor.fetchone()[0]
        
        print(f"\n📊 ESTATÍSTICAS DOS USUÁRIOS DE PRODUÇÃO")
        print("=" * 60)
        print(f"👥 Total de usuários: {total_usuarios}")
        
        if total_usuarios == 0:
            print("❌ Nenhum usuário encontrado")
            return
        
        # Lista de usuários
        print(f"\n👤 LISTA DE USUÁRIOS:")
        print("-" * 40)
        
        # Construir query baseada nas colunas disponíveis
        colunas_select = ['username']
        if 'tier' in colunas_disponiveis:
            colunas_select.append('tier')
        if 'last_api_reset' in colunas_disponiveis:
            colunas_select.append('last_api_reset')
        if 'subscription_expires' in colunas_disponiveis:
            colunas_select.append('subscription_expires')
        
        query = f'SELECT {", ".join(colunas_select)} FROM "user" ORDER BY username'
        cursor.execute(query)
        
        usuarios = cursor.fetchall()
        
        for i, user in enumerate(usuarios, 1):
            username = user[0]
            print(f"  {i:2d}. {username}")
            
            # Informações adicionais se disponíveis
            if 'tier' in colunas_disponiveis and len(user) > 1:
                tier = user[1] or 'N/A'
                print(f"      Tier: {tier}")
            
            if 'last_api_reset' in colunas_disponiveis and len(user) > 2:
                ultimo_acesso = user[2] or 'Nunca'
                print(f"      Último acesso: {ultimo_acesso}")
            
            if 'subscription_expires' in colunas_disponiveis and len(user) > 3:
                expira = user[3] or 'N/A'
                print(f"      Expira: {expira}")
        
        # Estatísticas por tier (se disponível)
        if 'tier' in colunas_disponiveis:
            print(f"\n🏷️ USUÁRIOS POR TIER:")
            cursor.execute('SELECT tier, COUNT(*) FROM "user" GROUP BY tier')
            usuarios_por_tier = cursor.fetchall()
            
            for tier, quantidade in usuarios_por_tier:
                porcentagem = (quantidade / total_usuarios * 100) if total_usuarios > 0 else 0
                print(f"  • {tier or 'N/A'}: {quantidade} ({porcentagem:.1f}%)")
        
        # Usuários ativos (se disponível)
        if 'last_api_reset' in colunas_disponiveis:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM "user" 
                WHERE last_api_reset >= CURRENT_DATE - INTERVAL '30 days'
            """)
            usuarios_ativos = cursor.fetchone()[0]
            usuarios_inativos = total_usuarios - usuarios_ativos
            taxa_atividade = (usuarios_ativos / total_usuarios * 100) if total_usuarios > 0 else 0
            
            print(f"\n📈 ATIVIDADE:")
            print(f"  • Ativos (30 dias): {usuarios_ativos}")
            print(f"  • Inativos: {usuarios_inativos}")
            print(f"  • Taxa de atividade: {taxa_atividade:.1f}%")
        
        return {
            'total': total_usuarios,
            'usuarios': usuarios,
            'colunas': colunas_disponiveis
        }
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return None

def exportar_csv(conn, colunas_disponiveis, filename=None):
    """Exporta dados para CSV"""
    try:
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'usuarios_producao_{timestamp}.csv'
        
        cursor = conn.cursor()
        
        # Construir query
        colunas_select = ['username']
        if 'tier' in colunas_disponiveis:
            colunas_select.append('tier')
        if 'last_api_reset' in colunas_disponiveis:
            colunas_select.append('last_api_reset')
        if 'subscription_expires' in colunas_disponiveis:
            colunas_select.append('subscription_expires')
        if 'api_calls_today' in colunas_disponiveis:
            colunas_select.append('api_calls_today')
        
        query = f'SELECT {", ".join(colunas_select)} FROM "user" ORDER BY username'
        cursor.execute(query)
        
        usuarios = cursor.fetchall()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Cabeçalho
            writer.writerow(colunas_select)
            
            # Dados
            for user in usuarios:
                writer.writerow(user)
        
        print(f"\n💾 Dados exportados para: {filename}")
        print(f"   Total de usuários: {len(usuarios)}")
        print(f"   Colunas: {', '.join(colunas_select)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 SNE RADAR - CONSULTA DE USUÁRIOS DE PRODUÇÃO")
    print("=" * 60)
    
    # Conectar ao banco de produção
    conn = conectar_banco_producao()
    if not conn:
        return
    
    try:
        # Verificar estrutura
        colunas_disponiveis = verificar_estrutura_banco(conn)
        
        if not colunas_disponiveis:
            print("❌ Não foi possível verificar a estrutura do banco")
            return
        
        # Estatísticas
        stats = estatisticas_usuarios(conn, colunas_disponiveis)
        
        if stats and stats['total'] > 0:
            # Exportar dados (opcional)
            print(f"\n💾 Deseja exportar os dados para CSV? (s/n): ", end="")
            resposta = input().lower().strip()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                exportar_csv(conn, colunas_disponiveis)
        
    except KeyboardInterrupt:
        print("\n\n👋 Consulta interrompida")
    except Exception as e:
        print(f"\n❌ Erro durante a consulta: {e}")
    finally:
        conn.close()
        print("\n✅ Conexão fechada")

if __name__ == "__main__":
    main()


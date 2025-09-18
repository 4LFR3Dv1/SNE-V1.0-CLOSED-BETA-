#!/usr/bin/env python3
# -*- coding: utf-8
"""
Script para consultar estatísticas de usuários do SNE Radar
Conecta tanto ao banco local quanto ao de produção
"""

import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório atual ao path para importar database_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database_config import (
        get_database_url, 
        get_connection_info, 
        test_connection, 
        list_available_configs,
        print_config_status
    )
except ImportError:
    print("❌ Erro: arquivo database_config.py não encontrado")
    sys.exit(1)

def conectar_banco(config_name='local'):
    """
    Conecta ao banco especificado (local ou produção)
    """
    try:
        if config_name == 'local':
            import sqlite3
            config = get_connection_info('local')
            db_path = config.get('path', 'instance/sne_radar.db')
            
            if not os.path.exists(db_path):
                print(f"❌ Banco local não encontrado em: {db_path}")
                return None
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            print(f"✅ Conectado ao banco local: {db_path}")
            return conn
        
        elif config_name == 'production':
            import psycopg2
            config = get_connection_info('production')
            
            # Verificar se temos credenciais
            if not all([
                config.get('host'), 
                config.get('username'), 
                config.get('password'), 
                config.get('database')
            ]):
                print("❌ Credenciais de produção não configuradas")
                print("💡 Configure as variáveis de ambiente:")
                print("   export DB_HOST=seu_host")
                print("   export DB_PORT=5432")
                print("   export DB_NAME=seu_database")
                print("   export DB_USER=seu_usuario")
                print("   export DB_PASSWORD=sua_senha")
                return None
            
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['username'],
                password=config['password']
            )
            print(f"✅ Conectado ao banco de produção: {config['host']}:{config['port']}/{config['database']}")
            return conn
        
        else:
            print(f"❌ Configuração '{config_name}' não suportada")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco '{config_name}': {e}")
        return None

def verificar_estrutura_banco(conn, config_name='local'):
    """Verifica a estrutura atual do banco"""
    try:
        cursor = conn.cursor()
        
        if config_name == 'local':
            # SQLite
            cursor.execute("PRAGMA table_info(user)")
            colunas = cursor.fetchall()
            colunas_nomes = [col[1] for col in colunas]
        else:
            # PostgreSQL
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                ORDER BY ordinal_position
            """)
            colunas = cursor.fetchall()
            colunas_nomes = [col[0] for col in colunas]
        
        print(f"🔍 ESTRUTURA DO BANCO ({config_name.upper()}):")
        print("=" * 50)
        for col in colunas:
            if config_name == 'local':
                print(f"  • {col[1]} ({col[2]})")
            else:
                print(f"  • {col[0]} ({col[1]})")
        
        # Verificar se tem colunas de monetização
        colunas_monetizacao = ['tier', 'api_calls_today', 'last_api_reset', 'subscription_expires', 'api_key']
        colunas_faltando = [col for col in colunas_monetizacao if col not in colunas_nomes]
        
        if colunas_faltando:
            print(f"\n⚠️ COLUNAS FALTANDO PARA MONETIZAÇÃO:")
            for col in colunas_faltando:
                print(f"  • {col}")
        
        return colunas_nomes
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return []

def estatisticas_gerais(conn, colunas_disponiveis, config_name='local'):
    """Estatísticas gerais dos usuários"""
    try:
        cursor = conn.cursor()
        
        # Total de usuários
        cursor.execute("SELECT COUNT(*) as total FROM \"user\"")
        result = cursor.fetchone()
        total_usuarios = result[0] if config_name == 'production' else result['total']
        
        print(f"\n📊 ESTATÍSTICAS GERAIS DE USUÁRIOS")
        print("=" * 50)
        print(f"👥 Total de usuários: {total_usuarios}")
        
        # Estatísticas básicas (sempre disponíveis)
        if 'username' in colunas_disponiveis:
            cursor.execute('SELECT username FROM "user" ORDER BY username')
            usuarios = cursor.fetchall()
            
            print(f"\n👤 LISTA DE USUÁRIOS ({len(usuarios)}):")
            print("-" * 40)
            for i, user in enumerate(usuarios, 1):
                username = user[0] if config_name == 'production' else user['username']
                print(f"  {i:2d}. {username}")
        
        # Estatísticas avançadas (se disponíveis)
        if 'tier' in colunas_disponiveis:
            cursor.execute('SELECT tier, COUNT(*) as quantidade FROM "user" GROUP BY tier')
            usuarios_por_tier = cursor.fetchall()
            
            print(f"\n🏷️ USUÁRIOS POR TIER:")
            for row in usuarios_por_tier:
                if config_name == 'production':
                    tier, quantidade = row[0], row[1]
                else:
                    tier, quantidade = row['tier'], row['quantidade']
                
                porcentagem = (quantidade/total_usuarios*100) if total_usuarios > 0 else 0
                print(f"  • {tier.upper()}: {quantidade} ({porcentagem:.1f}%)")
        
        if 'last_api_reset' in colunas_disponiveis:
            if config_name == 'production':
                cursor.execute("""
                    SELECT COUNT(*) as ativos 
                    FROM "user" 
                    WHERE last_api_reset >= CURRENT_DATE - INTERVAL '30 days'
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) as ativos 
                    FROM "user" 
                    WHERE last_api_reset >= date('now', '-30 days')
                """)
            
            result = cursor.fetchone()
            usuarios_ativos = result[0] if config_name == 'production' else result['ativos']
            usuarios_inativos = total_usuarios - usuarios_ativos
            taxa_atividade = (usuarios_ativos / total_usuarios * 100) if total_usuarios > 0 else 0
            
            print(f"🟢 Usuários ativos (30 dias): {usuarios_ativos}")
            print(f"🔴 Usuários inativos: {usuarios_inativos}")
            print(f"📈 Taxa de atividade: {taxa_atividade:.1f}%")
        
        return {
            'total': total_usuarios,
            'colunas_disponiveis': colunas_disponiveis,
            'config_name': config_name
        }
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas gerais: {e}")
        return None

def detalhes_usuarios(conn, colunas_disponiveis, config_name='local', limit=20):
    """Lista detalhes dos usuários"""
    try:
        cursor = conn.cursor()
        
        # Construir query baseada nas colunas disponíveis
        colunas_select = ['username']
        if 'tier' in colunas_disponiveis:
            colunas_select.append('tier')
        if 'api_calls_today' in colunas_disponiveis:
            colunas_select.append('api_calls_today')
        if 'last_api_reset' in colunas_disponiveis:
            colunas_select.append('last_api_reset')
        if 'subscription_expires' in colunas_disponiveis:
            colunas_select.append('subscription_expires')
        if 'api_key' in colunas_disponiveis:
            colunas_select.append('api_key')
        
        query = f'SELECT {", ".join(colunas_select)} FROM "user" ORDER BY username LIMIT %s'
        if config_name == 'local':
            query = query.replace('%s', '?')
        
        cursor.execute(query, (limit,))
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("❌ Nenhum usuário encontrado")
            return None
        
        print(f"\n👤 DETALHES DOS USUÁRIOS:")
        print("=" * 80)
        
        # Cabeçalho da tabela
        headers = ['Username']
        if 'tier' in colunas_disponiveis:
            headers.append('Tier')
        if 'api_calls_today' in colunas_disponiveis:
            headers.append('API Calls')
        if 'last_api_reset' in colunas_disponiveis:
            headers.append('Último Acesso')
        if 'subscription_expires' in colunas_disponiveis:
            headers.append('Expira')
        if 'api_key' in colunas_disponiveis:
            headers.append('API Key')
        
        # Imprimir cabeçalho
        header_line = " | ".join(f"{h:<15}" for h in headers)
        print(header_line)
        print("-" * len(header_line))
        
        # Imprimir dados
        for user in usuarios:
            row_data = []
            
            # Username (sempre disponível)
            if config_name == 'production':
                row_data.append(user[0])
            else:
                row_data.append(user['username'])
            
            # Outras colunas
            col_index = 1
            if 'tier' in colunas_disponiveis:
                value = user[col_index] if config_name == 'production' else user['tier']
                row_data.append(str(value or 'N/A'))
                col_index += 1
            
            if 'api_calls_today' in colunas_disponiveis:
                value = user[col_index] if config_name == 'production' else user['api_calls_today']
                row_data.append(str(value or 0))
                col_index += 1
            
            if 'last_api_reset' in colunas_disponiveis:
                value = user[col_index] if config_name == 'production' else user['last_api_reset']
                row_data.append(str(value or 'Nunca'))
                col_index += 1
            
            if 'subscription_expires' in colunas_disponiveis:
                value = user[col_index] if config_name == 'production' else user['subscription_expires']
                row_data.append(str(value or 'N/A'))
                col_index += 1
            
            if 'api_key' in colunas_disponiveis:
                value = user[col_index] if config_name == 'production' else user['api_key']
                row_data.append('Sim' if value else 'Não')
            
            row_line = " | ".join(f"{d:<15}" for d in row_data)
            print(row_line)
        
        return usuarios
        
    except Exception as e:
        print(f"❌ Erro ao obter detalhes dos usuários: {e}")
        return None

def exportar_dados(conn, colunas_disponiveis, config_name='local', filename=None):
    """Exporta dados dos usuários para CSV"""
    try:
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'usuarios_{config_name}_{timestamp}.csv'
        
        cursor = conn.cursor()
        
        # Construir query baseada nas colunas disponíveis
        colunas_select = ['username']
        if 'tier' in colunas_disponiveis:
            colunas_select.append('tier')
        if 'api_calls_today' in colunas_disponiveis:
            colunas_select.append('api_calls_today')
        if 'last_api_reset' in colunas_disponiveis:
            colunas_select.append('last_api_reset')
        if 'subscription_expires' in colunas_disponiveis:
            colunas_select.append('subscription_expires')
        if 'api_key' in colunas_disponiveis:
            colunas_select.append('api_key')
        
        query = f'SELECT {", ".join(colunas_select)} FROM "user" ORDER BY username'
        cursor.execute(query)
        
        usuarios = cursor.fetchall()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Cabeçalho
            writer.writerow(colunas_select)
            
            # Dados
            for user in usuarios:
                if config_name == 'production':
                    row = [user[i] for i in range(len(colunas_select))]
                else:
                    row = [user[col] for col in colunas_select]
                writer.writerow(row)
        
        print(f"\n💾 Dados exportados para: {filename}")
        print(f"   Total de usuários exportados: {len(usuarios)}")
        print(f"   Colunas exportadas: {', '.join(colunas_select)}")
        print(f"   Banco: {config_name.upper()}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")
        return None

def main():
    """Função principal"""
    print("🔍 SNE RADAR - CONSULTA DE ESTATÍSTICAS DE USUÁRIOS")
    print("=" * 60)
    
    # Mostrar configurações disponíveis
    print_config_status()
    
    # Escolher banco
    print(f"\n🎯 ESCOLHA O BANCO DE DADOS:")
    print("1. Local (desenvolvimento)")
    print("2. Produção (Render)")
    print("3. Sair")
    
    while True:
        try:
            escolha = input("\nDigite sua escolha (1-3): ").strip()
            
            if escolha == '1':
                config_name = 'local'
                break
            elif escolha == '2':
                config_name = 'production'
                break
            elif escolha == '3':
                print("👋 Saindo...")
                return
            else:
                print("❌ Escolha inválida. Digite 1, 2 ou 3.")
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            return
    
    # Conectar ao banco escolhido
    conn = conectar_banco(config_name)
    if not conn:
        return
    
    try:
        # Verificar estrutura do banco
        colunas_disponiveis = verificar_estrutura_banco(conn, config_name)
        
        if not colunas_disponiveis:
            print("❌ Não foi possível verificar a estrutura do banco")
            return
        
        # Estatísticas gerais
        stats = estatisticas_gerais(conn, colunas_disponiveis, config_name)
        
        if stats and stats['total'] > 0:
            # Detalhes dos usuários
            detalhes_usuarios(conn, colunas_disponiveis, config_name)
            
            # Exportar dados (opcional)
            print(f"\n💾 Deseja exportar os dados para CSV? (s/n): ", end="")
            resposta = input().lower().strip()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                exportar_dados(conn, colunas_disponiveis, config_name)
        else:
            print("❌ Nenhum usuário encontrado no banco de dados")
    
    except KeyboardInterrupt:
        print("\n\n👋 Consulta interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a consulta: {e}")
    finally:
        conn.close()
        print(f"\n✅ Conexão com banco {config_name} fechada")

if __name__ == "__main__":
    main()


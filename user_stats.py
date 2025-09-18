#!/usr/bin/env python3
# -*- coding: utf-8
"""
Script para consultar estatísticas de usuários do SNE Radar
"""

import sqlite3
import os
from datetime import datetime, timedelta

def conectar_banco():
    """Conecta ao banco de dados SQLite"""
    db_path = 'instance/sne_radar.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def verificar_estrutura_banco(conn):
    """Verifica a estrutura atual do banco e sugere atualizações"""
    try:
        cursor = conn.cursor()
        
        # Verificar colunas existentes na tabela user
        cursor.execute("PRAGMA table_info(user)")
        colunas = cursor.fetchall()
        colunas_nomes = [col[1] for col in colunas]
        
        print("🔍 ESTRUTURA ATUAL DO BANCO:")
        print("=" * 40)
        for col in colunas:
            print(f"  • {col[1]} ({col[2]})")
        
        # Verificar se tem colunas de monetização
        colunas_monetizacao = ['tier', 'api_calls_today', 'last_api_reset', 'subscription_expires', 'api_key']
        colunas_faltando = [col for col in colunas_monetizacao if col not in colunas_nomes]
        
        if colunas_faltando:
            print(f"\n⚠️ COLUNAS FALTANDO PARA MONETIZAÇÃO:")
            for col in colunas_faltando:
                print(f"  • {col}")
            print(f"\n💡 Para ativar funcionalidades completas, execute o sistema web:")
            print(f"   python sne_radar_web.py")
            print(f"   (Isso atualizará automaticamente o banco)")
        
        return colunas_nomes
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return []

def estatisticas_gerais(conn, colunas_disponiveis):
    """Estatísticas gerais dos usuários baseadas nas colunas disponíveis"""
    try:
        cursor = conn.cursor()
        
        # Total de usuários
        cursor.execute("SELECT COUNT(*) as total FROM user")
        total_usuarios = cursor.fetchone()['total']
        
        print(f"\n📊 ESTATÍSTICAS GERAIS DE USUÁRIOS")
        print("=" * 50)
        print(f"👥 Total de usuários: {total_usuarios}")
        
        # Estatísticas básicas (sempre disponíveis)
        if 'username' in colunas_disponiveis:
            cursor.execute("SELECT username FROM user ORDER BY username")
            usuarios = cursor.fetchall()
            
            print(f"\n👤 LISTA DE USUÁRIOS ({len(usuarios)}):")
            print("-" * 40)
            for i, user in enumerate(usuarios, 1):
                print(f"  {i:2d}. {user['username']}")
        
        # Estatísticas avançadas (se disponíveis)
        if 'tier' in colunas_disponiveis:
            cursor.execute("""
                SELECT tier, COUNT(*) as quantidade 
                FROM user 
                GROUP BY tier
            """)
            usuarios_por_tier = cursor.fetchall()
            
            print(f"\n🏷️ USUÁRIOS POR TIER:")
            for row in usuarios_por_tier:
                tier = row['tier']
                quantidade = row['quantidade']
                porcentagem = (quantidade/total_usuarios*100) if total_usuarios > 0 else 0
                print(f"  • {tier.upper()}: {quantidade} ({porcentagem:.1f}%)")
        
        if 'last_api_reset' in colunas_disponiveis:
            cursor.execute("""
                SELECT COUNT(*) as ativos 
                FROM user 
                WHERE last_api_reset >= date('now', '-30 days')
            """)
            usuarios_ativos = cursor.fetchone()['ativos']
            usuarios_inativos = total_usuarios - usuarios_ativos
            taxa_atividade = (usuarios_ativos / total_usuarios * 100) if total_usuarios > 0 else 0
            
            print(f"🟢 Usuários ativos (30 dias): {usuarios_ativos}")
            print(f"🔴 Usuários inativos: {usuarios_inativos}")
            print(f"📈 Taxa de atividade: {taxa_atividade:.1f}%")
        
        if 'api_calls_today' in colunas_disponiveis:
            cursor.execute("""
                SELECT username, api_calls_today, last_api_reset
                FROM user 
                WHERE api_calls_today > 0
                ORDER BY api_calls_today DESC 
                LIMIT 5
            """)
            top_usuarios = cursor.fetchall()
            
            if top_usuarios:
                print(f"\n🔥 TOP 5 USUÁRIOS POR USO DE API:")
                print("-" * 50)
                for user in top_usuarios:
                    print(f"  • {user['username']}: {user['api_calls_today']} calls")
        
        return {
            'total': total_usuarios,
            'colunas_disponiveis': colunas_disponiveis
        }
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas gerais: {e}")
        return None

def detalhes_usuarios(conn, colunas_disponiveis, limit=20):
    """Lista detalhes dos usuários baseado nas colunas disponíveis"""
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
        
        query = f"SELECT {', '.join(colunas_select)} FROM user ORDER BY username LIMIT ?"
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
            row_data = [user['username']]
            if 'tier' in colunas_disponiveis:
                row_data.append(user['tier'] or 'N/A')
            if 'api_calls_today' in colunas_disponiveis:
                row_data.append(str(user['api_calls_today'] or 0))
            if 'last_api_reset' in colunas_disponiveis:
                ultimo = user['last_api_reset'] or 'Nunca'
                row_data.append(str(ultimo))
            if 'subscription_expires' in colunas_disponiveis:
                expira = user['subscription_expires'] or 'N/A'
                row_data.append(str(expira))
            if 'api_key' in colunas_disponiveis:
                tem_key = 'Sim' if user['api_key'] else 'Não'
                row_data.append(tem_key)
            
            row_line = " | ".join(f"{d:<15}" for d in row_data)
            print(row_line)
        
        return usuarios
        
    except Exception as e:
        print(f"❌ Erro ao obter detalhes dos usuários: {e}")
        return None

def analise_uso_api(conn, colunas_disponiveis):
    """Análise do uso da API por usuários (se disponível)"""
    if 'api_calls_today' not in colunas_disponiveis:
        print(f"\n⚠️ Análise de uso da API não disponível (coluna 'api_calls_today' não existe)")
        return None
    
    try:
        cursor = conn.cursor()
        
        # Top usuários por uso de API
        cursor.execute("""
            SELECT username, api_calls_today, last_api_reset
            FROM user 
            WHERE api_calls_today > 0
            ORDER BY api_calls_today DESC 
            LIMIT 10
        """)
        
        top_usuarios = cursor.fetchall()
        
        if top_usuarios:
            print(f"\n🔥 TOP 10 USUÁRIOS POR USO DE API:")
            print("=" * 60)
            print(f"{'Username':<15} {'API Calls':<10} {'Último Acesso':<15}")
            print("-" * 60)
            
            for user in top_usuarios:
                username = user['username']
                api_calls = user['api_calls_today']
                ultimo_acesso = user['last_api_reset'] or 'Nunca'
                
                print(f"{username:<15} {api_calls:<10} {str(ultimo_acesso):<15}")
        
        # Estatísticas gerais de uso
        cursor.execute("""
            SELECT 
                COUNT(*) as total_usuarios,
                AVG(api_calls_today) as media_calls,
                MAX(api_calls_today) as max_calls,
                SUM(api_calls_today) as total_calls
            FROM user
        """)
        
        stats = cursor.fetchone()
        
        print(f"\n📊 ESTATÍSTICAS DE USO DA API:")
        print("=" * 40)
        print(f"  • Total de usuários: {stats['total_usuarios']}")
        print(f"  • Média de calls: {stats['media_calls']:.1f}")
        print(f"  • Máximo de calls: {stats['max_calls']}")
        print(f"  • Total de calls: {stats['total_calls']}")
        
        return {
            'top_usuarios': top_usuarios,
            'stats': stats
        }
        
    except Exception as e:
        print(f"❌ Erro ao analisar uso da API: {e}")
        return None

def exportar_dados(conn, colunas_disponiveis, filename='usuarios_export.csv'):
    """Exporta dados dos usuários para CSV baseado nas colunas disponíveis"""
    try:
        import csv
        
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
        
        query = f"SELECT {', '.join(colunas_select)} FROM user ORDER BY username"
        cursor.execute(query)
        
        usuarios = cursor.fetchall()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=colunas_select)
            
            writer.writeheader()
            for user in usuarios:
                writer.writerow(dict(user))
        
        print(f"\n💾 Dados exportados para: {filename}")
        print(f"   Total de usuários exportados: {len(usuarios)}")
        print(f"   Colunas exportadas: {', '.join(colunas_select)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")
        return None

def main():
    """Função principal"""
    print("🔍 SNE RADAR - CONSULTA DE ESTATÍSTICAS DE USUÁRIOS")
    print("=" * 60)
    
    # Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        # Verificar estrutura do banco
        colunas_disponiveis = verificar_estrutura_banco(conn)
        
        if not colunas_disponiveis:
            print("❌ Não foi possível verificar a estrutura do banco")
            return
        
        # Estatísticas gerais
        stats = estatisticas_gerais(conn, colunas_disponiveis)
        
        if stats and stats['total'] > 0:
            # Detalhes dos usuários
            detalhes_usuarios(conn, colunas_disponiveis)
            
            # Análise de uso da API (se disponível)
            analise_uso_api(conn, colunas_disponiveis)
            
            # Exportar dados (opcional)
            print(f"\n💾 Deseja exportar os dados para CSV? (s/n): ", end="")
            resposta = input().lower().strip()
            
            if resposta in ['s', 'sim', 'y', 'yes']:
                exportar_dados(conn, colunas_disponiveis)
        else:
            print("❌ Nenhum usuário encontrado no banco de dados")
    
    except KeyboardInterrupt:
        print("\n\n👋 Consulta interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a consulta: {e}")
    finally:
        conn.close()
        print("\n✅ Conexão com banco fechada")

if __name__ == "__main__":
    main()

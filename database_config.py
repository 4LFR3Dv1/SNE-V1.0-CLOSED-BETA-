#!/usr/bin/env python3
# -*- coding: utf-8
"""
Configuração de conexões de banco de dados para SNE Radar
"""

import os
from typing import Optional, Dict, Any

# Configurações de banco de dados
DATABASE_CONFIGS = {
    'local': {
        'type': 'sqlite',
        'path': 'instance/sne_radar.db',
        'description': 'Banco local de desenvolvimento'
    },
    'production': {
        'type': 'postgresql',
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432'),
        'database': os.environ.get('DB_NAME', 'sne_radar'),
        'username': os.environ.get('DB_USER', 'sne_radar_user'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'description': 'Banco de produção no Render'
    }
}

def get_database_url(config_name: str = None) -> Optional[str]:
    """
    Retorna a URL de conexão para o banco especificado
    Se config_name for None, detecta automaticamente o ambiente
    """
    # Detectar ambiente automaticamente se não especificado
    if config_name is None:
        config_name = 'production' if os.environ.get('FLASK_ENV') == 'production' else 'local'
    
    if config_name not in DATABASE_CONFIGS:
        print(f"❌ Configuração '{config_name}' não encontrada")
        return None
    
    config = DATABASE_CONFIGS[config_name]
    
    if config['type'] == 'sqlite':
        return f"sqlite:///{config['path']}"
    
    elif config['type'] == 'postgresql':
        # Verificar se temos todas as credenciais
        required_fields = ['host', 'port', 'database', 'username', 'password']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            print(f"⚠️ Configurações faltando para banco de produção: {missing_fields}")
            print("💡 Configure as variáveis de ambiente:")
            for field in missing_fields:
                print(f"   export {field.upper()}=valor")
            return None
        
        return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    return None

def get_connection_info(config_name: str = 'local') -> Dict[str, Any]:
    """
    Retorna informações de conexão para o banco especificado
    """
    if config_name not in DATABASE_CONFIGS:
        return {}
    
    config = DATABASE_CONFIGS[config_name].copy()
    
    if config['type'] == 'postgresql':
        # Ocultar senha nas informações
        config['password'] = '***' if config.get('password') else 'Não configurada'
    
    return config

def test_connection(config_name: str = 'local') -> bool:
    """
    Testa a conexão com o banco especificado
    """
    try:
        if config_name == 'local':
            import sqlite3
            config = DATABASE_CONFIGS[config_name]
            conn = sqlite3.connect(config['path'])
            conn.close()
            return True
        
        elif config_name == 'production':
            import psycopg2
            config = DATABASE_CONFIGS[config_name]
            
            # Verificar se temos credenciais
            if not all([config.get('host'), config.get('username'), config.get('password'), config.get('database')]):
                print("❌ Credenciais de produção não configuradas")
                return False
            
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['username'],
                password=config['password']
            )
            conn.close()
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao testar conexão com '{config_name}': {e}")
        return False

def list_available_configs() -> list:
    """
    Lista todas as configurações disponíveis
    """
    return list(DATABASE_CONFIGS.keys())

def print_config_status():
    """
    Imprime o status de todas as configurações
    """
    print("🔍 STATUS DAS CONFIGURAÇÕES DE BANCO:")
    print("=" * 50)
    
    for config_name in DATABASE_CONFIGS:
        config = DATABASE_CONFIGS[config_name]
        print(f"\n📊 {config_name.upper()}:")
        print(f"   Tipo: {config['type']}")
        print(f"   Descrição: {config['description']}")
        
        if config['type'] == 'sqlite':
            import os
            exists = os.path.exists(config['path'])
            print(f"   Arquivo: {config['path']}")
            print(f"   Existe: {'✅ Sim' if exists else '❌ Não'}")
        
        elif config['type'] == 'postgresql':
            has_creds = all([
                config.get('host'), 
                config.get('username'), 
                config.get('password'), 
                config.get('database')
            ])
            print(f"   Host: {config.get('host', 'Não configurado')}")
            print(f"   Database: {config.get('database', 'Não configurado')}")
            print(f"   Username: {config.get('username', 'Não configurado')}")
            print(f"   Password: {'✅ Configurada' if config.get('password') else '❌ Não configurada'}")
            print(f"   Credenciais completas: {'✅ Sim' if has_creds else '❌ Não'}")
        
        # Testar conexão
        print(f"   Conexão: {'✅ OK' if test_connection(config_name) else '❌ Falha'}")

if __name__ == "__main__":
    print_config_status()


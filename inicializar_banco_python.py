#!/usr/bin/env python3
"""
Script para inicializar banco de dados Cloud SQL usando Python
Funciona mesmo com IP privado!
"""

import os
import sys
import subprocess
import tempfile

def get_db_password(project_id):
    """Obtém senha do Secret Manager"""
    try:
        result = subprocess.run(
            ['gcloud', 'secrets', 'versions', 'access', 'latest', 
             '--secret=sne-db-password', f'--project={project_id}'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao obter senha: {e}")
        sys.exit(1)

def create_tables_via_psql(connection_name, db_user, db_password, db_name, project_id):
    """Cria tabelas usando psql via Cloud SQL Proxy"""
    
    # SQL para criar tabelas
    sql = """
-- Tabela users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela signals
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    pair VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    price DECIMAL(18, 8),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela trades
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    pair VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    price DECIMAL(18, 8) NOT NULL,
    quantity DECIMAL(18, 8) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_signals_pair ON signals(pair);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
"""
    
    # Criar arquivo SQL temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql)
        sql_file = f.name
    
    try:
        # Tentar usar psql diretamente (se Cloud SQL Proxy estiver rodando)
        # Ou usar gcloud sql import sql via Cloud Storage
        
        print("📦 Usando gcloud sql import sql via Cloud Storage...")
        
        # Criar bucket temporário se não existir
        bucket_name = f"{project_id}-temp-sql"
        
        # Verificar se bucket existe
        check_bucket = subprocess.run(
            ['gsutil', 'ls', f'gs://{bucket_name}'],
            capture_output=True
        )
        
        if check_bucket.returncode != 0:
            print(f"📦 Criando bucket temporário: {bucket_name}")
            subprocess.run(
                ['gsutil', 'mb', f'gs://{bucket_name}'],
                check=True
            )
        
        # Upload do arquivo SQL
        sql_gcs_path = f'gs://{bucket_name}/init_tables.sql'
        print(f"📤 Fazendo upload do SQL para {sql_gcs_path}...")
        subprocess.run(
            ['gsutil', 'cp', sql_file, sql_gcs_path],
            check=True
        )
        
        # Importar SQL
        print("📝 Executando SQL no banco de dados...")
        subprocess.run(
            ['gcloud', 'sql', 'import', 'sql', connection_name.split(':')[-1],
             sql_gcs_path,
             f'--database={db_name}',
             f'--project={project_id}'],
            check=True
        )
        
        # Limpar
        subprocess.run(['gsutil', 'rm', sql_gcs_path], capture_output=True)
        
        print("✅ Tabelas criadas com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Alternativa: Use Cloud Shell para executar o SQL")
        sys.exit(1)
    finally:
        # Limpar arquivo temporário
        if os.path.exists(sql_file):
            os.unlink(sql_file)

def main():
    project_id = sys.argv[1] if len(sys.argv) > 1 else "sne-v1"
    instance_name = sys.argv[2] if len(sys.argv) > 2 else "sne-db-prod"
    db_name = sys.argv[3] if len(sys.argv) > 3 else "sne"
    db_user = "sne_admin"
    
    connection_name = f"{project_id}:us-central1:{instance_name}"
    
    print(f"🗄️ Inicializando banco de dados: {instance_name}")
    print(f"Projeto: {project_id}")
    print("")
    
    # Obter senha
    print("🔐 Obtendo senha do Secret Manager...")
    db_password = get_db_password(project_id)
    print("✅ Senha obtida")
    print("")
    
    # Criar tabelas
    create_tables_via_psql(connection_name, db_user, db_password, db_name, project_id)
    
    print("")
    print("🎉 Banco de dados inicializado!")

if __name__ == "__main__":
    main()




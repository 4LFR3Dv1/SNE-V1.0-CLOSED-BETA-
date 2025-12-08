#!/bin/bash
# Script para inicializar banco via Cloud Shell
# Execute este script no Cloud Shell do GCP

set -e

PROJECT_ID=${1:-"sne-v1"}
INSTANCE_NAME=${2:-"sne-db-prod"}
DB_NAME=${3:-"sne"}
DB_USER=${4:-"sne_admin"}

echo "🗄️ Inicializando banco de dados via Cloud Shell"
echo "Projeto: $PROJECT_ID"
echo "Instância: $INSTANCE_NAME"
echo ""

# Obter senha
echo "🔐 Obtendo senha do Secret Manager..."
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password --project=$PROJECT_ID)

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ Erro: Não foi possível obter a senha do banco"
    exit 1
fi

echo "✅ Senha obtida"
echo ""

# Conectar e executar SQL
echo "📝 Criando tabelas..."
echo ""

# Criar arquivo SQL temporário
cat > /tmp/create_tables.sql << 'EOF'
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
EOF

# Executar SQL via gcloud
echo "Executando SQL..."
PGPASSWORD="$DB_PASSWORD" psql \
    -h /cloudsql/${PROJECT_ID}:us-central1:${INSTANCE_NAME} \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -f /tmp/create_tables.sql

echo ""
echo "✅ Tabelas criadas com sucesso!"
echo ""
echo "📋 Verificando tabelas..."
PGPASSWORD="$DB_PASSWORD" psql \
    -h /cloudsql/${PROJECT_ID}:us-central1:${INSTANCE_NAME} \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -c "\dt"

echo ""
echo "🎉 Banco de dados inicializado!"




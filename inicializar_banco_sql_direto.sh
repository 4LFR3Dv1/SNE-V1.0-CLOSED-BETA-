#!/bin/bash
# Script para inicializar banco usando gcloud sql execute-sql
# Funciona mesmo com IP privado!

set -e

PROJECT_ID=${1:-"sne-v1"}
INSTANCE_NAME=${2:-"sne-db-prod"}
DB_NAME=${3:-"sne"}

echo "🗄️ Inicializando banco de dados: $INSTANCE_NAME"
echo "Projeto: $PROJECT_ID"
echo ""

# Criar arquivo SQL temporário
SQL_FILE=$(mktemp)
cat > "$SQL_FILE" << 'EOF'
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

echo "📝 Executando SQL para criar tabelas..."
echo ""

# Executar SQL via gcloud
gcloud sql execute-sql $INSTANCE_NAME \
    --database=$DB_NAME \
    --file="$SQL_FILE" \
    --project=$PROJECT_ID

echo ""
echo "✅ Tabelas criadas com sucesso!"
echo ""

# Verificar tabelas
echo "📋 Verificando tabelas criadas..."
gcloud sql execute-sql $INSTANCE_NAME \
    --database=$DB_NAME \
    --sql="SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" \
    --project=$PROJECT_ID

# Limpar arquivo temporário
rm -f "$SQL_FILE"

echo ""
echo "🎉 Banco de dados inicializado!"




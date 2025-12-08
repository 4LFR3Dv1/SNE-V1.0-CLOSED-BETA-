#!/bin/bash
# Script para inicializar banco usando gcloud sql import sql via Cloud Storage
# Funciona mesmo com IP privado!

set -e

PROJECT_ID=${1:-"sne-v1"}
INSTANCE_NAME=${2:-"sne-db-prod"}
DB_NAME=${3:-"sne"}

echo "🗄️ Inicializando banco de dados: $INSTANCE_NAME"
echo "Projeto: $PROJECT_ID"
echo ""

# Nome do bucket temporário
BUCKET_NAME="${PROJECT_ID}-temp-sql"
SQL_FILE="init_tables.sql"
GCS_PATH="gs://${BUCKET_NAME}/${SQL_FILE}"
LOCAL_SQL_FILE="criar_tabelas.sql"

# Criar bucket se não existir
echo "📦 Verificando bucket Cloud Storage..."
if ! gsutil ls "gs://${BUCKET_NAME}" &>/dev/null; then
    echo "📦 Criando bucket: ${BUCKET_NAME}"
    gsutil mb "gs://${BUCKET_NAME}" || true
fi

# Obter service account do Cloud SQL
echo "🔐 Obtendo service account do Cloud SQL..."
SQL_SA=$(gcloud sql instances describe ${INSTANCE_NAME} \
    --project=${PROJECT_ID} \
    --format="value(serviceAccountEmailAddress)")

if [ -z "$SQL_SA" ]; then
    echo "❌ Erro: Não foi possível obter service account do Cloud SQL"
    exit 1
fi

echo "✅ Service account: $SQL_SA"

# Dar permissão de leitura ao bucket
echo "🔐 Concedendo permissões ao bucket..."
gsutil iam ch serviceAccount:${SQL_SA}:objectViewer "gs://${BUCKET_NAME}"

# Upload do arquivo SQL
echo "📤 Fazendo upload do SQL para Cloud Storage..."
if [ -f "${LOCAL_SQL_FILE}" ]; then
    # Copiar arquivo local para o nome esperado no GCS
    cp "${LOCAL_SQL_FILE}" /tmp/${SQL_FILE}
    gsutil cp /tmp/${SQL_FILE} "${GCS_PATH}"
    rm -f /tmp/${SQL_FILE}
else
    echo "❌ Arquivo criar_tabelas.sql não encontrado!"
    echo "📝 Criando arquivo SQL..."
    
    cat > /tmp/${SQL_FILE} << 'EOF'
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
    
    gsutil cp /tmp/${SQL_FILE} "${GCS_PATH}"
    rm -f /tmp/${SQL_FILE}
fi

# Importar SQL
echo ""
echo "📝 Executando SQL no banco de dados..."
gcloud sql import sql ${INSTANCE_NAME} \
    "${GCS_PATH}" \
    --database=${DB_NAME} \
    --project=${PROJECT_ID}

# Limpar arquivo do bucket
echo ""
echo "🧹 Limpando arquivo temporário..."
gsutil rm "${GCS_PATH}" || true

echo ""
echo "✅ Tabelas criadas com sucesso!"
echo ""
echo "📋 Verificando tabelas..."
echo "Execute no Cloud Shell:"
echo "  gcloud sql connect ${INSTANCE_NAME} --user=sne_admin --database=${DB_NAME}"
echo "  \\dt"

echo ""
echo "🎉 Banco de dados inicializado!"


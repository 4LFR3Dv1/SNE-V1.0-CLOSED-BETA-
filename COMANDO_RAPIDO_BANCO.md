# 🚀 COMANDO RÁPIDO: Inicializar Banco

## ✅ MÉTODO MAIS RÁPIDO (Cloud Shell)

### 1. Abrir Cloud Shell

Acesse: https://console.cloud.google.com/sql/instances/sne-db-prod/overview?project=sne-v1

Clique no botão **"Cloud Shell"** (terminal no topo).

### 2. Executar SQL

Cole e execute este comando no Cloud Shell:

```bash
# Obter senha
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password --project=sne-v1)

# Conectar e criar tabelas
gcloud sql connect sne-db-prod --user=sne_admin --database=sne << EOF
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

-- Índices
CREATE INDEX IF NOT EXISTS idx_signals_pair ON signals(pair);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);

-- Verificar
\dt
EOF
```

**Quando pedir a senha**, cole: `$DB_PASSWORD`

---

## ✅ MÉTODO ALTERNATIVO (Upload SQL)

### 1. Fazer Upload do Arquivo SQL

No Cloud Shell, faça upload do arquivo `criar_tabelas.sql`:

```bash
# No Cloud Shell, clique em "Upload" e selecione criar_tabelas.sql
# Ou copie o conteúdo do arquivo
```

### 2. Executar

```bash
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password --project=sne-v1)
gcloud sql connect sne-db-prod --user=sne_admin --database=sne
# Cole a senha: $DB_PASSWORD
# Execute: \i criar_tabelas.sql
```

---

## ✅ MÉTODO LOCAL (Instalar Ferramentas)

Se preferir fazer localmente:

```bash
# 1. Instalar Cloud SQL Proxy
brew install cloud-sql-proxy

# 2. Instalar Alembic
pip install alembic psycopg2-binary

# 3. Executar
./deploy/init_db.sh sne-v1 us-central1 sne-v1:us-central1:sne-db-prod
```

---

**💡 Recomendação**: Use o Cloud Shell (Método 1) - é mais rápido e não precisa instalar nada!




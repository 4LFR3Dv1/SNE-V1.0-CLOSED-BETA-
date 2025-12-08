# 🗄️ INICIALIZAR BANCO DE DADOS

## ⚠️ PROBLEMA

Faltam ferramentas locais (Cloud SQL Proxy e Alembic). Vamos usar uma solução mais simples!

---

## ✅ OPÇÃO 1: Usar Cloud Shell (RECOMENDADO - Mais Fácil)

### Passo 1: Abrir Cloud Shell

1. Acesse: https://console.cloud.google.com/sql/instances/sne-db-prod/overview?project=sne-v1
2. Clique no botão **"Cloud Shell"** (ícone de terminal no topo)
3. Aguarde o Cloud Shell abrir

### Passo 2: Clonar Repositório (se necessário)

```bash
# Se o código não estiver no Cloud Shell, clone ou faça upload
# Por enquanto, vamos criar as tabelas diretamente via SQL
```

### Passo 3: Conectar ao Banco

```bash
# Obter senha
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password --project=sne-v1)

# Conectar ao Cloud SQL
gcloud sql connect sne-db-prod --user=sne_admin --database=sne
# Quando pedir senha, cole: $DB_PASSWORD
```

### Passo 4: Criar Tabelas Manualmente

Execute este SQL no prompt do PostgreSQL:

```sql
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

-- Verificar tabelas
\dt
```

---

## ✅ OPÇÃO 2: Instalar Ferramentas Localmente

### Instalar Cloud SQL Proxy

```bash
# macOS
brew install cloud-sql-proxy

# Ou baixar manualmente
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
chmod +x cloud-sql-proxy
sudo mv cloud-sql-proxy /usr/local/bin/
```

### Instalar Alembic

```bash
# Criar ambiente virtual (se não tiver)
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install alembic psycopg2-binary

# Executar migrações
./deploy/init_db.sh sne-v1 us-central1 sne-v1:us-central1:sne-db-prod
```

---

## ✅ OPÇÃO 3: Usar Cloud Build (Automático)

Criar um build específico para migrações:

```bash
# Criar arquivo cloudbuild-migrations.yaml
# E executar via Cloud Build
```

---

## 🎯 RECOMENDAÇÃO

**Use a Opção 1 (Cloud Shell)** - É mais rápida e não precisa instalar nada!

---

## 📋 DEPOIS DE CRIAR AS TABELAS

Teste a conexão:

```bash
# Via Cloud Shell
gcloud sql connect sne-db-prod --user=sne_admin --database=sne

# Verificar tabelas
\dt

# Testar inserção
INSERT INTO signals (pair, signal_type, price) VALUES ('BTCUSDT', 'BUY', 50000.00);
SELECT * FROM signals;
```

---

**💡 Dica**: A Opção 1 é a mais rápida e não requer instalações locais!




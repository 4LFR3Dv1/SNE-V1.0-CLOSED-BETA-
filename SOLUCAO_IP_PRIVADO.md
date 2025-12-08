# 🔧 SOLUÇÃO: Banco com IP Privado

## ⚠️ PROBLEMA

A instância Cloud SQL está configurada com apenas **IP privado** (sem IPv4 público), então `gcloud sql connect` não funciona diretamente.

---

## ✅ SOLUÇÃO: Usar `gcloud sql execute-sql`

Este método funciona mesmo com IP privado!

---

## 🚀 COMANDO RÁPIDO

```bash
./inicializar_banco_sql_direto.sh sne-v1 sne-db-prod sne
```

Ou manualmente:

```bash
# Executar SQL diretamente
gcloud sql execute-sql sne-db-prod \
    --database=sne \
    --sql="
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS signals (
        id SERIAL PRIMARY KEY,
        pair VARCHAR(20) NOT NULL,
        signal_type VARCHAR(50) NOT NULL,
        price DECIMAL(18, 8),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
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
    
    CREATE INDEX IF NOT EXISTS idx_signals_pair ON signals(pair);
    CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
    CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair);
    CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
    " \
    --project=sne-v1
```

---

## ✅ USAR ARQUIVO SQL

```bash
# Executar usando arquivo
gcloud sql execute-sql sne-db-prod \
    --database=sne \
    --file=criar_tabelas.sql \
    --project=sne-v1
```

---

## 🔍 VERIFICAR TABELAS

```bash
gcloud sql execute-sql sne-db-prod \
    --database=sne \
    --sql="SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" \
    --project=sne-v1
```

---

## 📋 ALTERNATIVAS

### Opção 1: Habilitar IP Público (Temporário)

```bash
# Adicionar IP público temporariamente
gcloud sql instances patch sne-db-prod \
    --assign-ip \
    --project=sne-v1

# Depois, remover:
gcloud sql instances patch sne-db-prod \
    --no-assign-ip \
    --project=sne-v1
```

**⚠️ Não recomendado para produção!**

### Opção 2: Usar Cloud SQL Proxy via Cloud Run

Criar um serviço Cloud Run temporário que execute o SQL.

---

## 🎯 RECOMENDAÇÃO

**Use `gcloud sql execute-sql`** - É a forma mais simples e segura!

Execute:

```bash
./inicializar_banco_sql_direto.sh sne-v1 sne-db-prod sne
```

---

**💡 Dica**: O IP privado é mais seguro! Use `gcloud sql execute-sql` para executar comandos SQL.




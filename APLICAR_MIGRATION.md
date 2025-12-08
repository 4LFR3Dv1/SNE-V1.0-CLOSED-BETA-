# 🔧 COMO APLICAR A MIGRATION ALEMBIC

## ⚠️ PROBLEMA

O comando `alembic` não está disponível no PATH. Vamos resolver isso!

---

## ✅ SOLUÇÕES

### **Opção 1: Usar Python -m (Recomendado)**

```bash
python3 -m alembic upgrade head
```

Se não funcionar, instale o Alembic primeiro:

```bash
python3 -m pip install alembic==1.13.2
python3 -m alembic upgrade head
```

---

### **Opção 2: Instalar Alembic Globalmente**

```bash
pip3 install alembic==1.13.2
alembic upgrade head
```

---

### **Opção 3: Usar Ambiente Virtual (Melhor Prática)**

Se você tem um ambiente virtual:

```bash
# Ativar ambiente virtual
source venv/bin/activate  # ou .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar migration
alembic upgrade head
```

---

### **Opção 4: Aplicar SQL Direto (Alternativa)**

Se o Alembic não funcionar, você pode aplicar os índices diretamente no banco:

```sql
-- Conectar ao banco de dados e executar:

-- Índices para market_data
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
ON market_data(symbol, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_timestamp 
ON market_data(timestamp DESC);

-- Índices para alert
CREATE INDEX IF NOT EXISTS idx_alerts_symbol_tipo 
ON alert(symbol, tipo);

CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
ON alert(timestamp DESC);

-- Índice para user
CREATE INDEX IF NOT EXISTS idx_users_is_admin 
ON "user"(is_admin);
```

---

## 🔍 VERIFICAR

Depois de aplicar, verifique se os índices foram criados:

```sql
-- PostgreSQL
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%';

-- SQLite
SELECT name FROM sqlite_master 
WHERE type = 'index' 
AND name LIKE 'idx_%';
```

---

## 📝 PRÓXIMOS PASSOS

1. Aplicar migration ou SQL direto
2. Reiniciar Flask
3. Testar performance

---

**Escolha a opção que funciona melhor para você!** ✅


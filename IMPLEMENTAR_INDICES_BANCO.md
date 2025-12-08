# 📊 IMPLEMENTAÇÃO: ÍNDICES NO BANCO DE DADOS

## 🎯 OBJETIVO

Criar índices apropriados para otimizar queries frequentes no banco de dados.

---

## 📋 ÍNDICES A IMPLEMENTAR

### **1. Tabela `market_data`**

```sql
-- Índice composto para queries por símbolo e timestamp (mais comum)
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
ON market_data(symbol, timestamp DESC);

-- Índice para queries por usuário
CREATE INDEX IF NOT EXISTS idx_market_data_user_id 
ON market_data(user_id);

-- Índice para queries por timestamp apenas
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp 
ON market_data(timestamp DESC);
```

**Benefício:** Queries como "últimos dados de BTCUSDT" serão muito mais rápidas.

---

### **2. Tabela `alerts`**

```sql
-- Índice composto para buscar alertas ativos por símbolo
CREATE INDEX IF NOT EXISTS idx_alerts_symbol_status 
ON alerts(symbol, status);

-- Índice para buscar alertas de um usuário com status
CREATE INDEX IF NOT EXISTS idx_alerts_user_id_status 
ON alerts(user_id, status);

-- Índice para ordenar por data de criação (mais recentes primeiro)
CREATE INDEX IF NOT EXISTS idx_alerts_created_at 
ON alerts(created_at DESC);
```

**Benefício:** Listagem de alertas será muito mais rápida.

---

### **3. Tabela `users`**

```sql
-- Índice único já existe no campo username (chave única)
-- Índice único já existe no campo email (chave única)

-- Índice para busca por admin
CREATE INDEX IF NOT EXISTS idx_users_is_admin 
ON users(is_admin) WHERE is_admin = TRUE;
```

**Benefício:** Queries de usuários admin serão otimizadas.

---

## 🔧 COMO APLICAR

### **Opção 1: Via Alembic (Recomendado)**

Criar migration:
```bash
alembic revision -m "add_performance_indexes"
```

### **Opção 2: Via SQL Direto**

Conectar ao banco e executar os comandos SQL acima.

---

## 📊 IMPACTO ESPERADO

- ⚡ **Queries 10-100x mais rápidas** dependendo do tamanho da tabela
- ⚡ **Menos carga** no banco de dados
- ⚡ **Melhor experiência** do usuário

---

**Próximo passo:** Implementar paginação nos endpoints que retornam listas grandes.


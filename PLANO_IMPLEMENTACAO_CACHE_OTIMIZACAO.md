# 🚀 PLANO DE IMPLEMENTAÇÃO: CACHE E OTIMIZAÇÃO

## 📋 OBJETIVO

Implementar cache de resultados e otimização de queries para melhorar performance do sistema, especialmente no endpoint `/api/signal` que é crítico para o dashboard.

---

## ✅ 1. STATUS ATUAL

### **Cache Manager Existente**
- ✅ `cache_manager.py` já existe e está completo
- ✅ Suporta TTL, invalidação, estatísticas
- ✅ Cache por usuário
- ❌ **NÃO está sendo usado no endpoint `/api/signal`**

### **Endpoint `/api/signal`**
- ❌ Executa análise completa a cada requisição
- ❌ Sem cache de resultados
- ❌ Performance degradada com múltiplas requisições simultâneas

---

## 🎯 2. IMPLEMENTAÇÃO: CACHE NO `/api/signal`

### **2.1. Estratégia de Cache**

**TTLs por Timeframe:**
- `1m`, `3m`, `5m`: **60 segundos** (dados muito voláteis)
- `15m`, `30m`: **180 segundos** (3 minutos)
- `1h`: **300 segundos** (5 minutos)
- `4h`, `1d`: **1800 segundos** (30 minutos)

**Chave de Cache:**
```
{symbol}_{timeframe}
Exemplo: "BTCUSDT_1h"
```

### **2.2. Implementação**

**Passo 1:** Integrar cache no endpoint
**Passo 2:** Adicionar invalidação quando necessário
**Passo 3:** Adicionar métricas de cache hit/miss

---

## 🔧 3. OTIMIZAÇÃO DE QUERIES

### **3.1. Banco de Dados**

**Tabelas Principais:**
- `users`
- `market_data`
- `alerts`

**Índices Recomendados:**
```sql
-- market_data
CREATE INDEX idx_market_data_symbol_timestamp ON market_data(symbol, timestamp DESC);
CREATE INDEX idx_market_data_user_id ON market_data(user_id);

-- alerts
CREATE INDEX idx_alerts_symbol_status ON alerts(symbol, status);
CREATE INDEX idx_alerts_user_id_status ON alerts(user_id, status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);

-- users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### **3.2. Paginação**

**Endpoints que precisam paginação:**
- `/api/market-data` (histórico)
- `/api/alerts` (lista de alertas)

**Implementar:**
```python
limit = request.args.get('limit', 50, type=int)
offset = request.args.get('offset', 0, type=int)
```

---

## 📊 4. BENEFÍCIOS ESPERADOS

### **Performance**
- ⚡ **Redução de 70-90%** no tempo de resposta do `/api/signal`
- ⚡ **Redução de carga** no motor de análise
- ⚡ **Menos chamadas** à Binance API

### **Experiência do Usuário**
- ✅ Respostas mais rápidas no dashboard
- ✅ Menos rate limiting
- ✅ Sistema mais responsivo

---

## 🔄 5. PRÓXIMOS PASSOS

1. ✅ Integrar cache no `/api/signal`
2. ✅ Adicionar índices no banco de dados
3. ✅ Implementar paginação
4. ✅ Adicionar métricas de performance
5. ✅ Monitorar hit rate do cache

---

## 📝 6. CONFIGURAÇÃO

### **6.1. Cache Config**

```python
CACHE_CONFIG = {
    'analises': {
        'maxsize': 500,  # Aumentar para dashboard
        'ttl': 300  # 5 minutos padrão
    },
    'sinais': {
        'maxsize': 1000,  # Muitos pares/timeframes
        'ttl': 180  # 3 minutos padrão
    }
}
```

### **6.2. TTL por Timeframe**

```python
TTL_BY_TIMEFRAME = {
    '1m': 60,
    '3m': 60,
    '5m': 60,
    '15m': 180,
    '30m': 180,
    '1h': 300,
    '4h': 1800,
    '1d': 1800,
    '1w': 3600
}
```

---

**Implementação começará agora!** 🚀


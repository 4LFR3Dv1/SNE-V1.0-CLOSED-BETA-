# 🔧 CORREÇÃO: Erro 429 (Rate Limit)

## 🐛 PROBLEMA

O Flask está retornando erro **429 (TOO MANY REQUESTS)** porque:
- Dashboard está fazendo muitas requisições simultâneas (8 símbolos ao mesmo tempo)
- Flask tem rate limiting configurado (Flask-Limiter)
- Requisições estão sendo bloqueadas por exceder o limite

---

## ✅ SOLUÇÕES APLICADAS

### **1. Requisições Sequenciais com Delay**
- ✅ Adicionado delay de **500ms** entre cada requisição
- ✅ Requisições agora são feitas **uma por vez**, não simultaneamente
- ✅ Reduzido número de símbolos de **8 para 5** (BTC, ETH, BNB, SOL, ADA)

### **2. Tratamento de Rate Limit**
- ✅ Se receber erro 429, aguarda **2 segundos** antes de continuar
- ✅ Tenta novamente apenas uma vez após o delay
- ✅ Logs informativos sobre rate limit

### **3. Intervalo de Atualização**
- ✅ Aumentado de **30 para 60 segundos** o auto-refresh
- ✅ Reduz carga no servidor

### **4. Código Ajustado:**

```javascript
// Antes: Todas as requisições ao mesmo tempo
await Promise.all(symbols.map(s => api.getSignal(s, '1h')))

// Depois: Sequencial com delay
for (const symbol of symbols) {
  if (results.length > 0) {
    await delay(500) // 500ms entre requisições
  }
  await api.getSignal(symbol, '1h')
}
```

---

## 📊 COMPARAÇÃO

| Antes | Depois |
|-------|--------|
| 8 requisições simultâneas | 5 requisições sequenciais |
| Delay: 0ms | Delay: 500ms entre cada |
| Auto-refresh: 30s | Auto-refresh: 60s |
| Sem tratamento de 429 | Tratamento com retry |

---

## 🧪 TESTE

Após as mudanças:

1. **Recarregar página** no navegador
2. **Verificar console** - deve ver delays entre requisições
3. **Aguardar** - requisições devem ser bem-sucedidas agora
4. **Verificar dashboard** - oportunidades devem aparecer

---

## 📋 SE AINDA HOUVER PROBLEMAS

### **Opção 1: Aumentar Delay**
```javascript
await delay(1000) // Aumentar para 1 segundo
```

### **Opção 2: Reduzir Símbolos**
```javascript
const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'] // Apenas 3
```

### **Opção 3: Desabilitar Rate Limit no Flask (Desenvolvimento)**
Verificar configuração do Flask-Limiter e aumentar limite temporariamente.

---

**Status:** ✅ Correções aplicadas - Aguardando teste


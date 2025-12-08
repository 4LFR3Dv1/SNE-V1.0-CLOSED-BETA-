# 🔧 DEBUG: API RETORNANDO HTML

## 🐛 PROBLEMA

A API está retornando HTML (`<!DOCTYPE html>`) em vez de JSON. Isso significa que:

1. **O Flask não está rodando** na porta 9999, OU
2. **O proxy do Vite não está funcionando**, OU
3. **A requisição está sendo interceptada** pelo servidor de desenvolvimento

---

## ✅ SOLUÇÕES

### **1. Verificar se o Flask está rodando**

```bash
# Verificar se há processo na porta 9999
lsof -i :9999

# Ou verificar no terminal onde você rodou:
python3 sne_radar_web.py
```

**Deve mostrar:**
```
 * Running on http://127.0.0.1:9999
```

---

### **2. Verificar o proxy do Vite**

O `vite.config.js` está configurado para:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:9999',
    changeOrigin: true
  }
}
```

**Isso significa:**
- Requisições para `/api/*` → `http://localhost:9999/api/*`
- Se o Flask não estiver rodando, o Vite retorna HTML (fallback)

---

### **3. Verificar o endpoint no Flask**

O endpoint existe em `sne_radar_web.py`:
```python
@app.route('/api/v1/candles')
@login_required
def api_v1_candles():
```

**Problema:** Requer autenticação (`@login_required`)

**Solução:** Verificar se você está logado ou remover temporariamente o `@login_required` para testar.

---

## 🔧 CORREÇÕES APLICADAS

### **1. Validação de resposta HTML**

Adicionado no `TradingChart.vue`:
```javascript
// Verificar se a resposta é HTML (erro de proxy)
if (typeof candlesResponse === 'string' && candlesResponse.includes('<!DOCTYPE')) {
  console.error('❌ Erro: API retornou HTML em vez de JSON')
  error.value = 'Erro de conexão com o servidor. Verifique se o Flask está rodando.'
  return
}
```

---

## 🧪 COMO TESTAR

### **1. Verificar Flask**
```bash
# Terminal 1: Iniciar Flask
python3 sne_radar_web.py

# Deve mostrar:
# * Running on http://127.0.0.1:9999
```

### **2. Verificar Vite**
```bash
# Terminal 2: Iniciar Vite
cd frontend
npm run dev

# Deve mostrar:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

### **3. Testar endpoint diretamente**
```bash
# No navegador ou curl:
curl http://localhost:9999/api/v1/candles?symbol=BTCUSDT&interval=1h&limit=100

# Se retornar HTML, o Flask não está rodando ou o endpoint não existe
# Se retornar JSON, está funcionando
```

---

## 🔍 DEBUG NO NAVEGADOR

### **1. Abrir DevTools (F12)**
- **Console:** Ver logs de erro
- **Network:** Ver requisições

### **2. Verificar requisição**
- **URL:** `http://localhost:5173/api/v1/candles?...`
- **Status:** Deve ser `200` ou `401` (não `404`)
- **Response:** Deve ser JSON, não HTML

### **3. Se retornar HTML:**
- Verificar se Flask está rodando
- Verificar se a porta está correta (9999)
- Verificar se há erro de CORS

---

## 📝 PRÓXIMOS PASSOS

1. **Iniciar Flask** na porta 9999
2. **Iniciar Vite** na porta 5173
3. **Fazer login** no sistema (se necessário)
4. **Testar novamente** o gráfico

---

**Status:** ✅ Validação adicionada - Verifique se o Flask está rodando!


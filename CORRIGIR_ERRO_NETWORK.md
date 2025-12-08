# 🔧 CORREÇÃO: Erro de Network Error no Dashboard

## 🐛 PROBLEMA IDENTIFICADO

As requisições da API estão falhando com "Network Error" porque:
1. Flask pode não estar rodando na porta 9999
2. Proxy do Vite pode não estar funcionando corretamente
3. As requisições podem estar tentando ir diretamente ao Vite em vez do Flask

---

## ✅ SOLUÇÃO

### **1. Verificar se Flask está rodando:**

```bash
# Verificar se Flask está na porta 9999
lsof -i :9999

# Se não estiver, iniciar Flask:
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
source venv/bin/activate
python3 sne_radar_web.py
```

### **2. Verificar Proxy do Vite:**

O proxy está configurado em `frontend/vite.config.js`. Se o Flask estiver rodando, o proxy deve funcionar.

### **3. Reiniciar Vite Dev Server:**

Se fez alterações no `vite.config.js`, precisa reiniciar:

```bash
cd frontend
npm run dev
```

---

## 🔍 DEBUG

### **Verificar no Console do Navegador:**

1. Abrir DevTools (F12)
2. Ir para Network tab
3. Tentar carregar o dashboard
4. Verificar as requisições:
   - Se estão indo para `localhost:5173/api/...` → Proxy deve redirecionar
   - Se estão indo para `localhost:9999/api/...` → Direto (pode ter CORS)

### **Testar Flask diretamente:**

```bash
# Health check
curl http://localhost:9999/health

# Testar endpoint de signal
curl "http://localhost:9999/api/signal?symbol=BTCUSDT&timeframe=1h"
```

---

## 📋 CHECKLIST

- [ ] Flask está rodando na porta 9999
- [ ] Vite está rodando na porta 5173
- [ ] Proxy está configurado corretamente
- [ ] Requisições estão usando `/api` (não URL absoluta)
- [ ] CORS está habilitado no Flask

---

## 🚀 PRÓXIMOS PASSOS

1. Iniciar Flask se não estiver rodando
2. Reiniciar Vite dev server
3. Verificar se as requisições passam pelo proxy
4. Testar endpoints diretamente


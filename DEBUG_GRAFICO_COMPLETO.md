# 🐛 DEBUG COMPLETO: Problema do Gráfico

## 📊 STATUS ATUAL

### ✅ **O que está funcionando:**
- Flask está rodando (porta 9999 ativa)
- Endpoint `/api/v1/chart-image` responde com `image/png` quando acessado via curl
- CORS headers estão configurados
- Componente Vue está tentando carregar

### ❌ **O que NÃO está funcionando:**
- Navegador recebe HTML (`<!DOCTYPE html>...`) em vez de imagem PNG
- Content-Type retornado é `text/html` em vez de `image/png`

---

## 🔍 ANÁLISE DO PROBLEMA

### **Teste Direto (Funciona):**
```bash
curl -I "http://localhost:9999/api/v1/chart-image?symbol=BTCUSDT&interval=1h"
# Retorna: Content-Type: image/png ✅
```

### **No Navegador (Não funciona):**
- URL: `http://localhost:9999/api/v1/chart-image?...`
- Retorna: HTML do Vue.js (`<!DOCTYPE html>...`)
- Content-Type: `text/html`

---

## 🎯 CAUSA PROVÁVEL

O **Vite dev server** está interceptando a requisição **ANTES** dela chegar ao Flask, mesmo com URL absoluta.

**Possíveis causas:**
1. Vite está fazendo proxy e retornando HTML
2. Navegador está bloqueando por CORS e caindo no fallback
3. Requisição está sendo interceptada por algum middleware

---

## ✅ SOLUÇÕES

### **SOLUÇÃO 1: Usar URL Relativa com Proxy Funcional**

Ajustar o proxy do Vite para funcionar corretamente:

```javascript
// frontend/vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:9999',
    changeOrigin: true,
    secure: false,
    rewrite: (path) => path,
    configure: (proxy) => {
      proxy.on('proxyReq', (proxyReq, req) => {
        console.log('Proxying:', req.url)
      })
    }
  }
}
```

E usar URL relativa no componente:
```javascript
const url = `/api/v1/chart-image?symbol=${props.symbol}&interval=${props.timeframe}&t=${timestamp}`
```

---

### **SOLUÇÃO 2: Build Frontend e Servir pelo Flask (Mais Simples)**

```bash
# Build frontend
cd frontend
npm run build
cd ..

# Rodar Flask (serve tudo)
python3 sne_radar_web.py

# Acessar: http://localhost:9999
```

**Vantagens:**
- ✅ Sem problemas de proxy
- ✅ Sem problemas de CORS
- ✅ Tudo no mesmo servidor
- ✅ Funciona igual em dev e produção

---

### **SOLUÇÃO 3: Desabilitar Vite e Usar Flask Direto**

Parar Vite e acessar Flask diretamente:
- Frontend: `http://localhost:9999` (Flask serve frontend buildado)
- Backend: `http://localhost:9999/api/*` (mesmo servidor)

---

## 🚀 RECOMENDAÇÃO: SOLUÇÃO 2

Buildar o frontend e servir tudo pelo Flask é a solução mais simples e funciona sempre:

```bash
# 1. Build frontend
cd frontend
npm run build
cd ..

# 2. Rodar Flask
python3 sne_radar_web.py

# 3. Acessar
# http://localhost:9999
```

**Funciona porque:**
- Frontend buildado está em `frontend/dist/`
- Flask detecta e serve automaticamente
- Não precisa de Vite dev server
- Não precisa de proxy
- Não tem problemas de CORS

---

## 📋 CHECKLIST

- [ ] Build do frontend feito (`npm run build`)
- [ ] Flask servindo frontend buildado
- [ ] Acessar Flask diretamente (sem Vite)
- [ ] Gráfico deve carregar

---

**Documento criado:** Janeiro 2025


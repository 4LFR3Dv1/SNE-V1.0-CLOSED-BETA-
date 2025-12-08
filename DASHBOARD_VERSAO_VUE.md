# 🔍 DASHBOARD: Versão Vue.js vs Template HTML

## ⚠️ IMPORTANTE: Você tem 2 dashboards diferentes!

### **1. Dashboard Vue.js (Frontend Moderno)**
- **Arquivo:** `frontend/src/views/Dashboard.vue`
- **Rota:** `/` (raiz)
- **Acesso:** `http://localhost:5173/` (com Vite) ou `http://localhost:9999/` (Flask serve frontend buildado)
- **Tecnologia:** Vue.js 3 + Vite
- **Status:** ✅ Componente Vue.js criado

### **2. Dashboard HTML Antigo (Template Flask)**
- **Arquivo:** `templates/dashboard.html`
- **Rota:** `/dashboard`
- **Acesso:** `http://localhost:9999/dashboard`
- **Tecnologia:** HTML + JavaScript vanilla
- **Status:** ⚠️ Template HTML antigo

---

## 🎯 QUAL VOCÊ ESTÁ ACESSANDO?

### **Se está acessando `http://localhost:9999/dashboard`:**
- ❌ Está vendo o template HTML antigo
- ❌ Não vai ver as mudanças do Vue.js

### **Se está acessando `http://localhost:5173/` ou `http://localhost:9999/`:**
- ✅ Deve ver o componente Vue.js
- ✅ Mudanças devem aparecer

---

## ✅ COMO ACESSAR A VERSÃO VUE.JS

### **Opção 1: Com Vite Dev Server (Recomendado para desenvolvimento)**

```bash
# Terminal 1: Flask
python3 sne_radar_web.py

# Terminal 2: Vite
cd frontend
npm run dev
```

**Acessar:** `http://localhost:5173/`

---

### **Opção 2: Build Frontend e Servir pelo Flask**

```bash
# 1. Buildar frontend
cd frontend
npm run build

# 2. Rodar Flask (serve frontend buildado automaticamente)
cd ..
python3 sne_radar_web.py
```

**Acessar:** `http://localhost:9999/`

---

## 🔧 VERIFICAR QUAL ESTÁ RODANDO

1. **Abrir DevTools** (F12)
2. **Verificar o HTML:**
   - Se tem `<div id="app">` → Vue.js ✅
   - Se tem `<div class="terminal-container">` → HTML antigo ❌

3. **Verificar console:**
   - Se tem logs do Vite → Vue.js ✅
   - Se não tem → HTML antigo ❌

---

## 📝 RESUMO

- **`/dashboard`** → Template HTML antigo (`templates/dashboard.html`)
- **`/`** → Componente Vue.js (`frontend/src/views/Dashboard.vue`)

**Para ver as mudanças do Vue.js, acesse `/` (raiz), não `/dashboard`!**


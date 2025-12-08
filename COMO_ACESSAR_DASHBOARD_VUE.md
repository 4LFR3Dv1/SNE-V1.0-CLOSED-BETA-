# 🎯 COMO ACESSAR O DASHBOARD VUE.JS

## ⚠️ PROBLEMA IDENTIFICADO

Você tem **2 dashboards diferentes**:

1. **Template HTML Antigo** (`templates/dashboard.html`) → Rota `/dashboard`
2. **Componente Vue.js** (`frontend/src/views/Dashboard.vue`) → Rota `/`

Se você está vendo a "mesma tela", provavelmente está acessando o template HTML antigo!

---

## ✅ SOLUÇÃO: Acessar a Versão Vue.js

### **Opção 1: Com Vite Dev Server (Recomendado)**

```bash
# Terminal 1: Flask
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
source venv/bin/activate
python3 sne_radar_web.py

# Terminal 2: Vite
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm run dev
```

**Acessar:** `http://localhost:5173/`

**Você deve ver:**
- Título "Dashboard [Vue.js v2.0]" (marcador de versão)
- Interface moderna Vue.js
- Filtros funcionais

---

### **Opção 2: Build e Servir pelo Flask**

```bash
# Buildar frontend
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm run build

# Rodar Flask (serve frontend buildado)
cd ..
source venv/bin/activate
python3 sne_radar_web.py
```

**Acessar:** `http://localhost:9999/` (raiz, não `/dashboard`)

---

## 🔍 VERIFICAR QUAL ESTÁ RODANDO

### **Dashboard Vue.js:**
- ✅ URL: `http://localhost:5173/` ou `http://localhost:9999/`
- ✅ Título mostra: "Dashboard [Vue.js v2.0]"
- ✅ Console mostra: "✅ Dashboard Vue.js v2.0 montado!"
- ✅ HTML contém: `<div id="app">`

### **Dashboard HTML Antigo:**
- ❌ URL: `http://localhost:9999/dashboard`
- ❌ Título mostra: "SNE RADAR" (sem versão)
- ❌ HTML contém: `<div class="terminal-container">`

---

## 📝 DIFERENÇA

| Característica | Vue.js (`/`) | HTML Antigo (`/dashboard`) |
|----------------|--------------|----------------------------|
| **Arquivo** | `frontend/src/views/Dashboard.vue` | `templates/dashboard.html` |
| **URL** | `/` | `/dashboard` |
| **Tecnologia** | Vue.js 3 | HTML + JS vanilla |
| **Marcador** | "[Vue.js v2.0]" | Sem marcador |

---

## 🚀 TESTE AGORA

1. **Parar tudo** (Ctrl+C nos terminais)
2. **Iniciar Vite dev server:**
   ```bash
   cd frontend
   npm run dev
   ```
3. **Acessar:** `http://localhost:5173/`
4. **Verificar console:** Deve mostrar "✅ Dashboard Vue.js v2.0 montado!"
5. **Verificar título:** Deve mostrar "[Vue.js v2.0]"

---

**Se ainda não funcionar, me diga qual URL está acessando!**


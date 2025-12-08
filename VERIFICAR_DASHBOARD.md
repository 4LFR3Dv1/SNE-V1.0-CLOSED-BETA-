# 🔍 COMO VERIFICAR QUAL DASHBOARD ESTÁ RODANDO

## ✅ PASSO A PASSO

### **1. Verificar se Vite está rodando:**
```bash
# Você deve ver processos:
ps aux | grep vite
# Resultado esperado: processo node com vite
```

✅ **Status:** Vite está rodando (confirmado)

---

### **2. Acessar a URL correta:**

**Vite Dev Server:**
```
http://localhost:5173/
```

**OU se o Flask está servindo o frontend buildado:**
```
http://localhost:9999/
```

⚠️ **NÃO acesse:** `http://localhost:9999/dashboard` (esse é o template HTML antigo)

---

### **3. Verificar no navegador:**

#### **A. Abrir DevTools (F12)**

#### **B. Verificar Console:**
Procure por esta mensagem:
```
✅ Dashboard Vue.js v2.0 montado!
```

**Se aparecer:** ✅ Dashboard Vue.js está funcionando!

**Se não aparecer:** ❌ Está vendo template HTML antigo ou erro

---

#### **C. Verificar Título da Página:**

**Dashboard Vue.js:**
```
Dashboard [Vue.js v2.0]
```

**Dashboard HTML Antigo:**
```
SNE RADAR
```

---

#### **D. Verificar HTML (Elements tab):**

**Dashboard Vue.js:**
```html
<div id="app">
  <div class="dashboard">
    <h1>Dashboard [Vue.js v2.0]</h1>
```

**Dashboard HTML Antigo:**
```html
<div class="terminal-container">
  <div class="terminal-header">
    <div class="terminal-title">SNE RADAR</div>
```

---

## 🎯 O QUE VOCÊ DEVE VER

### **Se está funcionando (Vue.js):**
- ✅ Título: "Dashboard [Vue.js v2.0]"
- ✅ Console: "✅ Dashboard Vue.js v2.0 montado!"
- ✅ Botão "Atualizar" no canto superior direito
- ✅ 3 cards: BTC/USDT, Sinais Ativos, Score Médio
- ✅ Seção "Oportunidades" com filtros
- ✅ Filtros: Busca, Sinal, Score Mínimo

### **Se está vendo template antigo:**
- ❌ Título: "SNE RADAR"
- ❌ Console: Nenhuma mensagem do Vue.js
- ❌ Interface terminal (estilo preto/verde)
- ❌ WebSocket tentando conectar

---

## 🔧 SE NÃO ESTÁ FUNCIONANDO

### **1. Limpar cache do navegador:**
- Ctrl+Shift+R (Windows/Linux)
- Cmd+Shift+R (Mac)

### **2. Recarregar página:**
- F5 ou Ctrl+R

### **3. Verificar URL:**
- Deve ser: `http://localhost:5173/` (com barra no final)
- NÃO: `http://localhost:9999/dashboard`

### **4. Reiniciar Vite:**
```bash
# Parar Vite (Ctrl+C)
# Reiniciar:
cd frontend
npm run dev
```

---

## 📝 INFORME

Me diga:
1. Qual URL está acessando?
2. O que aparece no título?
3. O que aparece no console (F12)?
4. Qual interface você vê (Vue.js moderna ou terminal antigo)?


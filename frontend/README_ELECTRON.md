# 🚀 Guia Rápido: Electron

## ⚠️ IMPORTANTE: Execute TODOS os comandos dentro do diretório `frontend/`

---

## 📋 Passo a Passo

### **1. Entrar no diretório frontend**

```bash
cd frontend
```

### **2. Instalar dependências**

```bash
npm install
```

### **3. Executar em desenvolvimento**

**Opção A: Modo simples (recomendado para começar)**

```bash
# Terminal 1: Iniciar Vite dev server
npm run dev

# Terminal 2: Depois que Vite estiver rodando, executar Electron
npm run electron:serve
```

**Opção B: Build e executar**

```bash
# Build do frontend
npm run build

# Executar Electron
npm run electron:serve
```

### **4. Build para produção**

```bash
# Build para macOS
npm run electron:build:mac

# Build para Windows
npm run electron:build:win

# Build para Linux
npm run electron:build:linux
```

---

## 🔧 Comandos Úteis

### **Verificar se está no diretório correto:**

```bash
pwd
# Deve mostrar: .../SNE_BACKUP_CLEAN/frontend

ls package.json
# Deve mostrar: package.json
```

### **Limpar e reinstalar:**

```bash
rm -rf node_modules package-lock.json
npm install
```

### **Verificar dependências instaladas:**

```bash
npm list electron
npm list electron-builder
```

---

## 🐛 Problemas Comuns

### **Erro: "Could not read package.json"**

**Causa:** Você não está no diretório `frontend/`

**Solução:**
```bash
cd frontend
pwd  # Verificar que está em .../frontend
```

### **Erro: "command not found: concurrently"**

**Causa:** Dependência não instalada

**Solução:**
```bash
cd frontend
npm install
```

### **Erro: "electron: command not found"**

**Causa:** Electron não instalado

**Solução:**
```bash
cd frontend
npm install electron --save-dev
```

---

## 📝 Checklist Antes de Executar

- [ ] Estou no diretório `frontend/` (`cd frontend`)
- [ ] Dependências instaladas (`npm install`)
- [ ] Node.js instalado (`node --version`)
- [ ] npm instalado (`npm --version`)

---

## 🎯 Comandos Rápidos (Copy & Paste)

```bash
# 1. Entrar no diretório
cd frontend

# 2. Instalar dependências
npm install

# 3. Executar (em 2 terminais)
# Terminal 1:
npm run dev

# Terminal 2 (depois que Vite estiver rodando):
npm run electron:serve
```

---

**Lembre-se:** Sempre `cd frontend` primeiro! 🎯



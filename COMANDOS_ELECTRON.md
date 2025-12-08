# 🚀 Comandos Electron - Guia Rápido

## ⚠️ IMPORTANTE: Sempre execute os comandos dentro do diretório `frontend/`

---

## 📋 Comandos Principais

### **1. Configurar Electron (primeira vez)**

```bash
# Na raiz do projeto
./setup_electron.sh
```

### **2. Desenvolvimento (testar app Electron)**

```bash
# IMPORTANTE: Entre no diretório frontend primeiro!
cd frontend

# Instalar dependências (se ainda não instalou)
npm install

# Executar em modo desenvolvimento
# Isso vai iniciar o Vite dev server E o Electron
npm run electron:dev

# OU executar separadamente:
# Terminal 1: Vite dev server
npm run dev

# Terminal 2: Electron (depois que Vite estiver rodando)
npm run electron:serve
```

### **3. Build para Produção**

```bash
# IMPORTANTE: Entre no diretório frontend primeiro!
cd frontend

# Build para todas as plataformas
npm run electron:build

# Ou para plataforma específica:
npm run electron:build:win   # Windows
npm run electron:build:mac   # macOS
npm run electron:build:linux # Linux
```

---

## 🔧 Comandos Úteis

### **Instalar dependências (se necessário)**

```bash
cd frontend
npm install
```

### **Verificar se Electron está configurado**

```bash
cd frontend
cat package.json | grep electron
```

### **Limpar build anterior**

```bash
cd frontend
rm -rf dist_electron
rm -rf node_modules/.cache
```

---

## 📁 Estrutura de Diretórios

```
SNE_BACKUP_CLEAN/
├── frontend/              ← COMANDOS AQUI!
│   ├── package.json       ← Este é o package.json do Electron
│   ├── src/
│   │   ├── background.js
│   │   └── preload.js
│   └── dist_electron/     ← Executáveis gerados aqui
│
└── (raiz)                 ← setup_electron.sh aqui
```

---

## ⚡ Comandos Rápidos (Copy & Paste)

### **Desenvolvimento:**
```bash
cd frontend && npm run electron:serve
```

### **Build macOS:**
```bash
cd frontend && npm run electron:build:mac
```

### **Build Windows:**
```bash
cd frontend && npm run electron:build:win
```

### **Build Linux:**
```bash
cd frontend && npm run electron:build:linux
```

---

## 🐛 Problemas Comuns

### **Erro: "Could not read package.json"**

**Causa:** Você está no diretório errado.

**Solução:**
```bash
cd frontend
npm run electron:serve
```

### **Erro: "electron:serve command not found"**

**Causa:** Electron não foi configurado ainda.

**Solução:**
```bash
# Na raiz do projeto
./setup_electron.sh
```

### **Erro: "Module not found"**

**Causa:** Dependências não instaladas.

**Solução:**
```bash
cd frontend
npm install
```

---

## 📝 Checklist

Antes de executar `npm run electron:serve`:

- [ ] Node.js instalado (`node --version`)
- [ ] npm instalado (`npm --version`)
- [ ] Executou `./setup_electron.sh` (na raiz)
- [ ] Está no diretório `frontend/`
- [ ] Dependências instaladas (`npm install`)

---

**Lembre-se:** Sempre `cd frontend` antes de executar comandos npm! 🎯


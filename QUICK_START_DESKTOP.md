# 🚀 Quick Start - SNE RADAR Desktop

## ⚡ Início Rápido (3 passos)

### 1. Instalar pywebview

```bash
pip install pywebview
```

### 2. Buildar Frontend (OBRIGATÓRIO)

```bash
cd frontend
npm install
npm run build
cd ..
```

**⚠️ IMPORTANTE:** O frontend PRECISA estar buildado para funcionar!

### 3. Executar

```bash
python3 sne_desktop.py
```

---

## 🔧 Se npm não estiver instalado

### macOS (com Homebrew)

```bash
# Instalar Node.js e npm
brew install node

# Verificar instalação
node --version
npm --version
```

### macOS (sem Homebrew)

1. Baixe Node.js de: https://nodejs.org/
2. Instale o pacote `.pkg`
3. Reinicie o terminal
4. Execute: `npm --version`

---

## 🎯 Modo Desenvolvimento (Alternativa)

Se você quiser testar sem buildar o frontend:

### Terminal 1: Iniciar Vite Dev Server

```bash
cd frontend
npm run dev
```

### Terminal 2: Iniciar Desktop App

```bash
python3 sne_desktop.py
```

O `sne_desktop.py` vai detectar automaticamente o Vite dev server e usar ele.

---

## ✅ Verificação Rápida

```bash
# 1. Verificar se frontend está buildado
ls frontend/dist/index.html

# 2. Se não existir, buildar
cd frontend && npm run build && cd ..

# 3. Executar
python3 sne_desktop.py
```

---

## 🐛 Problemas Comuns

### "npm: command not found"
→ Instale Node.js (veja acima)

### "Frontend não encontrado"
→ Execute: `cd frontend && npm run build`

### "Servidor não responde"
→ Verifique se a porta 9999 está livre: `lsof -i :9999`

### Janela abre mas está em branco
→ Verifique os logs do Flask no terminal
→ Verifique se o frontend foi buildado corretamente

---

**Status:** ✅ Pronto para uso após build do frontend!



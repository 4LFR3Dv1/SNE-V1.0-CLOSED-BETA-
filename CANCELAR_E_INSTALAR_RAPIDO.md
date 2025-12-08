# ⚡ CANCELAR INSTALAÇÃO E USAR MÉTODO RÁPIDO

A instalação do Homebrew pode travar ao compilar Python. Vamos usar o método mais rápido.

## 🛑 Passo 1: Cancelar Instalação Atual

No terminal onde está rodando o `brew install node`:

1. Pressione `Ctrl + C` para cancelar
2. Se não responder, pressione `Ctrl + Z` para pausar
3. Depois execute: `killall brew` (se necessário)

## 📥 Passo 2: Baixar Instalador Oficial (2 minutos)

### Opção A: Via Navegador

1. Acesse: **https://nodejs.org/**
2. Clique em **"Download Node.js (LTS)"** - versão v20.x ou v22.x
3. Baixe o arquivo `.pkg` para macOS

### Opção B: Via Terminal (depois de cancelar)

```bash
# Baixar Node.js LTS diretamente
cd ~/Downloads
curl -O https://nodejs.org/dist/v20.18.0/node-v20.18.0.pkg
```

## 🔧 Passo 3: Instalar (2 minutos)

1. Abra o arquivo `.pkg` baixado
2. Clique em **"Continuar"** → **"Continuar"** → **"Concordar"**
3. Clique em **"Instalar"**
4. Digite sua senha se solicitado
5. Aguarde ~2 minutos

## ✅ Passo 4: Verificar Instalação

**IMPORTANTE:** Feche o terminal atual e abra um NOVO terminal, depois execute:

```bash
node --version
npm --version
```

Deve mostrar algo como:
```
v20.18.0
10.8.0
```

## 📦 Passo 5: Instalar Dependências do Frontend

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm install
```

Isso vai demorar ~2-3 minutos para baixar todas as dependências.

## 🚀 Passo 6: Testar

```bash
cd frontend
npm run dev
```

Se abrir em `http://localhost:5173`, está funcionando! ✅

---

## ⚠️ Se Ainda Não Funcionar

Se após instalar pelo `.pkg` ainda não funcionar:

1. Feche TODOS os terminais
2. Abra um NOVO terminal
3. Execute: `source ~/.zshrc` ou `source ~/.bash_profile`
4. Teste novamente: `node --version`

---

**Tempo Total:** ~5 minutos (vs 30+ minutos do Homebrew)


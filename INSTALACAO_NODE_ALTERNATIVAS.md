# 🔧 INSTALAÇÃO DO NODE.JS - ALTERNATIVAS

## ⚠️ PROBLEMA IDENTIFICADO

O Homebrew está apresentando erros no macOS 12 (versão antiga). Vamos usar alternativas mais confiáveis.

---

## ✅ OPÇÃO 1: NVM (Node Version Manager) - RECOMENDADO

O NVM é mais flexível e funciona melhor em versões antigas do macOS.

### **Instalação:**

```bash
# 1. Instalar NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 2. Recarregar o terminal (ou fechar e abrir novamente)
source ~/.zshrc

# 3. Instalar Node.js LTS (versão estável)
nvm install --lts

# 4. Usar a versão instalada
nvm use --lts

# 5. Definir como padrão
nvm alias default node

# 6. Verificar instalação
node --version
npm --version
```

### **Vantagens:**
- ✅ Funciona em versões antigas do macOS
- ✅ Permite múltiplas versões do Node.js
- ✅ Fácil de atualizar
- ✅ Não depende do Homebrew

---

## ✅ OPÇÃO 2: Download Direto do Node.js

### **Instalação:**

1. **Acesse:** https://nodejs.org/
2. **Baixe a versão LTS** (Long Term Support) para macOS
3. **Instale o arquivo `.pkg`** baixado
4. **Siga o assistente de instalação**
5. **Verifique:**
   ```bash
   node --version
   npm --version
   ```

### **Vantagens:**
- ✅ Instalação simples (clique e instale)
- ✅ Funciona em qualquer versão do macOS
- ✅ Não requer ferramentas adicionais

---

## ✅ OPÇÃO 3: Corrigir Homebrew (Se Preferir)

Se quiser tentar corrigir o Homebrew:

```bash
# 1. Atualizar Homebrew
brew update

# 2. Limpar cache
brew cleanup

# 3. Tentar instalar novamente
brew install node
```

**Nota:** Pode não funcionar devido ao macOS 12 ser uma versão antiga (Tier 3).

---

## 🎯 RECOMENDAÇÃO FINAL

**Use o NVM (Opção 1)** - É a solução mais confiável para macOS 12 e permite gerenciar versões do Node.js facilmente.

---

## 📋 APÓS INSTALAR NODE.JS

Depois de instalar o Node.js (por qualquer método), execute:

```bash
# 1. Navegar para a pasta do frontend
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend

# 2. Instalar dependências
npm install

# 3. Verificar se lucide-vue-next foi instalado
npm list lucide-vue-next

# 4. Iniciar o projeto
npm run dev
```

---

## 🔍 VERIFICAÇÃO

Após instalar, verifique se tudo está funcionando:

```bash
# Verificar versão do Node.js
node --version
# Deve mostrar algo como: v20.x.x ou v18.x.x

# Verificar versão do npm
npm --version
# Deve mostrar algo como: 10.x.x ou 9.x.x

# Verificar se está no diretório correto
pwd
# Deve mostrar: /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
```

---

## ⚠️ NOTA IMPORTANTE

Se você escolher o **NVM**, lembre-se de:
- Recarregar o terminal após instalar (`source ~/.zshrc`)
- Ou fechar e abrir um novo terminal
- O NVM precisa ser "ativado" em cada novo terminal

---

**Status:** Aguardando instalação do Node.js via uma das opções acima.



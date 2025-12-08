# 📦 Como Instalar Node.js e npm

O Electron requer Node.js e npm. Siga as instruções abaixo para instalar.

---

## 🍎 macOS

### **Opção 1: Homebrew (Recomendado)**

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Node.js (inclui npm)
brew install node

# Verificar instalação
node --version
npm --version
```

### **Opção 2: Download Direto**

1. Acesse: https://nodejs.org/
2. Baixe a versão LTS (Long Term Support)
3. Execute o instalador `.pkg`
4. Siga as instruções

### **Opção 3: NVM (Node Version Manager)**

```bash
# Instalar NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Recarregar terminal ou executar:
source ~/.zshrc  # ou ~/.bash_profile

# Instalar Node.js LTS
nvm install --lts
nvm use --lts

# Verificar
node --version
npm --version
```

---

## 🪟 Windows

### **Opção 1: Download Direto**

1. Acesse: https://nodejs.org/
2. Baixe a versão LTS
3. Execute o instalador `.msi`
4. Siga as instruções (marque "Add to PATH")

### **Opção 2: Chocolatey**

```powershell
# Instalar Chocolatey (se não tiver)
# https://chocolatey.org/install

# Instalar Node.js
choco install nodejs-lts

# Verificar
node --version
npm --version
```

---

## 🐧 Linux

### **Ubuntu/Debian:**

```bash
# Via apt
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar
node --version
npm --version
```

### **Fedora/RHEL:**

```bash
# Via dnf
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
sudo dnf install -y nodejs

# Verificar
node --version
npm --version
```

---

## ✅ Verificar Instalação

Após instalar, verifique se está funcionando:

```bash
node --version   # Deve mostrar: v20.x.x ou similar
npm --version    # Deve mostrar: 10.x.x ou similar
```

---

## 🔧 Problemas Comuns

### **"command not found" após instalação**

**macOS/Linux:**
```bash
# Recarregar terminal
source ~/.zshrc  # ou ~/.bash_profile

# Ou adicionar ao PATH manualmente
export PATH="/usr/local/bin:$PATH"
```

**Windows:**
- Reinicie o terminal/PowerShell
- Verifique se Node.js foi adicionado ao PATH nas variáveis de ambiente

### **Versão antiga do Node.js**

```bash
# Atualizar via npm
npm install -g n
n lts

# Ou via Homebrew (macOS)
brew upgrade node
```

---

## 📋 Versões Recomendadas

- **Node.js:** v18.x ou v20.x (LTS)
- **npm:** v9.x ou v10.x (vem com Node.js)

---

## 🚀 Após Instalar

Depois de instalar Node.js, execute novamente:

```bash
./setup_electron.sh
```

---

**Precisa de ajuda?** Verifique a documentação oficial: https://nodejs.org/

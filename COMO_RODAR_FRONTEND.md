# 🚀 COMO RODAR O FRONTEND

## ✅ Status Atual

- ✅ Node.js v24.11.1 instalado via NVM
- ✅ npm v11.6.2 instalado
- ✅ Dependências do frontend instaladas (145 packages)

## 🛠️ Desenvolvimento Local

### Opção 1: Desenvolvimento com Vite (Recomendado)

```bash
# Terminal 1: Frontend (Vite dev server)
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm run dev

# Acessar: http://localhost:5173
# Vite faz proxy automático para Flask em /api e /socket.io
```

### Opção 2: Build e Servir via Flask

```bash
# 1. Build do frontend
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
npm run build

# 2. Rodar Flask (já serve o frontend automaticamente)
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_radar_web.py

# Acessar: http://localhost:9999
```

## 📋 Comandos Úteis

### Desenvolvimento
```bash
cd frontend
npm run dev          # Servidor de desenvolvimento Vite
npm run build        # Build para produção
npm run preview      # Preview do build localmente
```

### Verificar
```bash
node --version       # Verificar versão Node.js
npm --version        # Verificar versão npm
npm list             # Listar pacotes instalados
```

### Atualizar Dependências
```bash
cd frontend
npm update           # Atualizar dependências
npm audit fix        # Corrigir vulnerabilidades (se necessário)
```

## ⚠️ Notas

### Vulnerabilidades
Há 2 vulnerabilidades moderadas reportadas. Para corrigir (opcional):

```bash
cd frontend
npm audit fix
```

**Nota:** Se `npm audit fix` não resolver, você pode ignorar por enquanto (são vulnerabilidades em dependências de desenvolvimento).

### Atualizar npm
```bash
npm install -g npm@latest
```

## 🎯 Próximos Passos

1. **Testar desenvolvimento:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Testar build:**
   ```bash
   cd frontend
   npm run build
   ```

3. **Testar com Flask:**
   ```bash
   # Build primeiro
   cd frontend && npm run build && cd ..
   
   # Rodar Flask
   python3 sne_radar_web.py
   ```

## 🔧 Troubleshooting

### Problema: "command not found: node"

**Solução:** Carregue o NVM primeiro:
```bash
source "$HOME/.nvm/nvm.sh"
```

Ou adicione ao seu `~/.zshrc`:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

### Problema: Build falha

**Solução:** Limpe e reinstale:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

**Status:** ✅ **Tudo instalado e pronto para desenvolvimento!**


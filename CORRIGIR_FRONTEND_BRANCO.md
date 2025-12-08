# 🔧 CORRIGIR FRONTEND EM BRANCO

## ❌ Problema

- http://localhost:5173 está em branco
- http://localhost:9999 mostra dashboard antigo

## ✅ Solução

### 1. Estrutura Correta do Vite

No Vite, o `index.html` deve estar na **raiz** do projeto, não em `public/`.

**Estrutura correta:**
```
frontend/
├── index.html          ← AQUI (raiz)
├── src/
│   ├── main.js
│   ├── App.vue
│   └── ...
├── public/             ← Arquivos estáticos (imagens, etc)
└── package.json
```

### 2. Verificar Console do Navegador

Abra o console do navegador (F12) e verifique erros:
- Erros de importação
- Erros de módulos não encontrados
- Erros de sintaxe

### 3. Verificar se Vite Está Rodando

No terminal onde rodou `npm run dev`, verifique:
- Se há erros
- Se está escutando na porta 5173
- Se há mensagens de compilação

### 4. Recarregar Página

Depois de corrigir, recarregue a página com **Ctrl+Shift+R** (hard refresh)

---

## 🔍 Debug

### Verificar Erros no Terminal

```bash
cd frontend
source "$HOME/.nvm/nvm.sh"
npm run dev
```

Procure por:
- ✅ "ready in XXX ms"
- ❌ Erros de compilação
- ❌ Erros de módulos não encontrados

### Verificar Console do Navegador

1. Abra http://localhost:5173
2. Pressione F12
3. Vá para aba "Console"
4. Procure por erros em vermelho

---

## ✅ Checklist

- [ ] `index.html` está na raiz do frontend (não em public/)
- [ ] Vite está rodando sem erros
- [ ] Console do navegador não mostra erros
- [ ] Página recarregada (Ctrl+Shift+R)

---

**Status:** Corrigindo estrutura do Vite...


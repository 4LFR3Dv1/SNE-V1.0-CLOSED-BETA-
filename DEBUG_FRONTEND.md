# 🐛 DEBUG: Frontend em Branco

## ✅ Correção Aplicada

- ✅ `index.html` movido para raiz do frontend

## 🔍 Próximos Passos

### 1. Parar e Reiniciar Vite

No terminal onde está rodando `npm run dev`:
1. Pressione `Ctrl+C` para parar
2. Execute novamente:
   ```bash
   cd frontend
   source "$HOME/.nvm/nvm.sh"
   npm run dev
   ```

### 2. Verificar Erros no Terminal

Procure por mensagens como:
- ✅ `ready in XXX ms` - OK
- ❌ `Failed to resolve` - Erro de importação
- ❌ `Cannot find module` - Módulo não encontrado
- ❌ `SyntaxError` - Erro de sintaxe

### 3. Verificar Console do Navegador

1. Abra http://localhost:5173
2. Pressione **F12** (abrir DevTools)
3. Vá para aba **Console**
4. Procure por erros em **vermelho**

### 4. Verificar Network

1. Na aba **Network** do DevTools
2. Recarregue a página (F5)
3. Verifique se arquivos estão carregando:
   - `index.html` - deve retornar 200
   - `main.js` - deve retornar 200
   - `App.vue` - deve retornar 200

---

## 🔧 Erros Comuns

### Erro: "Cannot find module './App.vue'"

**Solução:** Verificar se `src/App.vue` existe

### Erro: "Failed to resolve import"

**Solução:** Verificar caminhos de importação

### Erro: "router is not defined"

**Solução:** Verificar se `src/router/index.js` existe e exporta router

---

## 📋 Checklist

- [ ] Vite reiniciado após mover index.html
- [ ] Console do navegador verificado
- [ ] Terminal do Vite verificado (sem erros)
- [ ] Página recarregada (Ctrl+Shift+R)

---

**Ação:** Reinicie o Vite e verifique o console do navegador!


# 🔧 RESOLVER ERRO 405

## ❌ Problema

Erro 405 (Method Not Allowed) ao acessar http://localhost:5173

## 🔍 Diagnóstico

O erro 405 geralmente acontece quando:
1. **Vue Router** tenta acessar rotas que não existem no servidor
2. **Vite** não está configurado para SPA (Single Page Application)
3. **Requisições** estão sendo bloqueadas

## ✅ Solução Aplicada

Atualizei `vite.config.js` para:
- ✅ Adicionar `host: true` (permite acesso externo)
- ✅ Melhorar configuração de proxy
- ✅ Adicionar `strictPort: false`

## 🔄 Próximos Passos

### 1. Reiniciar Vite

No terminal onde está rodando `npm run dev`:
1. Pressione `Ctrl+C` para parar
2. Execute novamente:
   ```bash
   cd frontend
   source "$HOME/.nvm/nvm.sh"
   npm run dev
   ```

### 2. Verificar no Navegador

1. Abra http://localhost:5173
2. Pressione **F12** (DevTools)
3. Vá para aba **Console**
4. Verifique se há erros

### 3. Verificar Network

1. Na aba **Network** do DevTools
2. Recarregue a página (F5)
3. Verifique requisições:
   - `index.html` - deve ser 200
   - `main.js` - deve ser 200
   - Outros arquivos - devem ser 200

## 🐛 Se Ainda Der Erro 405

### Verificar Rotas

O erro pode ser em rotas específicas. Verifique:
- `/` - deve funcionar
- `/analysis` - pode dar 405 se não configurado
- Outras rotas do Vue Router

### Solução Alternativa

Se persistir, pode ser problema com Vue Router. Verifique se:
- `src/router/index.js` está correto
- Componentes Vue existem
- Não há erros de importação

## 📋 Checklist

- [ ] Vite reiniciado após mudanças
- [ ] Console do navegador verificado
- [ ] Network tab verificado
- [ ] Rotas testadas

---

**Ação:** Reinicie o Vite e teste novamente!


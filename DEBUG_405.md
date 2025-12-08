# 🐛 DEBUG: Erro 405

## 🔍 Informações

O `curl` mostra que o servidor responde **200 OK**, então o erro 405 pode ser:

1. **Requisição específica** que está dando 405
2. **Vue Router** tentando acessar rotas
3. **Navegador** fazendo requisição diferente

## ✅ Solução Aplicada

Atualizei `vite.config.js` com:
- `host: true` - Permite acesso externo
- `strictPort: false` - Mais flexível
- Melhor configuração de proxy

## 🔄 Ação Necessária

### 1. Reiniciar Vite

**IMPORTANTE:** O Vite precisa ser reiniciado para aplicar as mudanças!

No terminal onde está rodando `npm run dev`:
1. Pressione `Ctrl+C`
2. Execute:
   ```bash
   cd frontend
   source "$HOME/.nvm/nvm.sh"
   npm run dev
   ```

### 2. Verificar no Navegador

1. Abra http://localhost:5173
2. Pressione **F12** (DevTools)
3. Vá para aba **Console**
4. **Copie e me envie** os erros que aparecem

### 3. Verificar Network Tab

1. Na aba **Network** do DevTools
2. Recarregue a página (F5)
3. Procure por requisições com status **405**
4. **Me diga qual URL** está dando 405

## 🎯 Possíveis Causas

### Causa 1: Vue Router
Se o erro for em rotas como `/analysis`, `/backtesting`, etc:
- **Normal** - Vue Router gerencia essas rotas no cliente
- **Solução:** Não é problema, é comportamento esperado

### Causa 2: Requisição API
Se o erro for em `/api/*`:
- **Problema:** Proxy não está funcionando
- **Solução:** Verificar se Flask está rodando na porta 9999

### Causa 3: Arquivo Específico
Se o erro for em arquivo `.js` ou `.vue`:
- **Problema:** Arquivo não encontrado ou erro de importação
- **Solução:** Verificar console para erros de compilação

---

## 📋 Informações Necessárias

Para resolver completamente, preciso saber:

1. **Qual URL** está dando 405?
   - `/` (página inicial)?
   - `/analysis`?
   - `/api/*`?
   - Outra?

2. **O que aparece no Console** do navegador?
   - Erros em vermelho?
   - Avisos em amarelo?

3. **O que aparece no Network tab**?
   - Qual requisição tem status 405?
   - Qual é a URL completa?

---

**Próximo passo:** Reinicie o Vite e me diga qual URL específica está dando 405!


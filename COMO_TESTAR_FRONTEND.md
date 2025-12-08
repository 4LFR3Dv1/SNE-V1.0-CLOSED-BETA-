# 🧪 COMO TESTAR O FRONTEND

## ✅ Status Atual

- ✅ **Vite rodando** em http://localhost:5173
- ⚠️ **Flask precisa rodar** para APIs funcionarem

---

## 🚀 Setup Completo (2 Terminais)

### Terminal 1: Frontend (Vite) - JÁ RODANDO ✅

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/frontend
source "$HOME/.nvm/nvm.sh"
npm run dev
```

**Status:** ✅ Rodando em http://localhost:5173

### Terminal 2: Backend (Flask) - PRECISA RODAR

Abra um **NOVO TERMINAL** e execute:

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_radar_web.py
```

**Acessar:** http://localhost:9999

---

## 🧪 Testar

### 1. Acessar Frontend

Abra no navegador: **http://localhost:5173**

Você deve ver:
- ✅ Header com logo "🚀 SNE RADAR"
- ✅ Dashboard com cards
- ✅ Navegação funcionando

### 2. Testar APIs

O Vite está configurado para fazer proxy automático:
- `/api/*` → `http://localhost:9999/api/*`
- `/socket.io/*` → `http://localhost:9999/socket.io/*`

### 3. Testar Análise

1. Vá para página "Análise"
2. Selecione um par (ex: BTCUSDT)
3. Selecione timeframe (ex: 1h)
4. Clique em "Analisar"

**Nota:** Precisa do Flask rodando para funcionar!

---

## 🔍 Verificar se Está Funcionando

### Frontend (Vite)
- ✅ Acesse: http://localhost:5173
- ✅ Deve carregar a página
- ✅ Navegação deve funcionar

### Backend (Flask)
- ✅ Acesse: http://localhost:9999
- ✅ Deve carregar (pode mostrar template antigo se frontend não estiver buildado)
- ✅ API: http://localhost:9999/api/health deve retornar JSON

### Integração
- ✅ Frontend em http://localhost:5173
- ✅ Flask em http://localhost:9999
- ✅ Vite faz proxy automático para Flask

---

## 🐛 Troubleshooting

### Problema: "Cannot GET /api/..."

**Solução:** Flask não está rodando. Inicie o Flask no Terminal 2.

### Problema: Página em branco

**Solução:** 
1. Verifique o console do navegador (F12)
2. Verifique se há erros no terminal do Vite
3. Verifique se todas as dependências estão instaladas

### Problema: Erro de conexão

**Solução:** 
1. Verifique se Flask está rodando na porta 9999
2. Verifique se Vite está rodando na porta 5173
3. Verifique firewall

---

## 📋 Checklist

- [x] Vite rodando (http://localhost:5173)
- [ ] Flask rodando (http://localhost:9999)
- [ ] Frontend carregando no navegador
- [ ] Navegação funcionando
- [ ] APIs respondendo (precisa Flask)

---

**Próximo passo:** Abra um novo terminal e rode o Flask!


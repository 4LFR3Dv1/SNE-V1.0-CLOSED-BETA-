# 🔐 CORREÇÃO: AUTENTICAÇÃO DA API

## 🐛 PROBLEMA

A API está retornando HTML em vez de JSON porque:
1. **O endpoint requer autenticação** (`@login_required`)
2. **O Flask-Login usa cookies de sessão**, não Bearer tokens
3. **O Axios não estava enviando cookies** por padrão

---

## ✅ CORREÇÕES APLICADAS

### **1. Configurar Axios para enviar cookies**

**Arquivo:** `frontend/src/services/api.js`

**Mudanças:**
```javascript
const api = axios.create({
  baseURL: '/api',
  withCredentials: true // ✅ Envia cookies de sessão
})

// No interceptor também:
config.withCredentials = true
```

---

## 🔍 COMO FUNCIONA

### **Flask-Login:**
- Usa **cookies de sessão** HTTP-only
- Não usa Bearer tokens
- Requer `withCredentials: true` no Axios

### **Fluxo:**
1. Usuário faz login → Flask cria sessão → Cookie é salvo
2. Requisições subsequentes → Axios envia cookie automaticamente
3. Flask valida cookie → Retorna dados JSON

---

## 🧪 COMO TESTAR

### **1. Verificar se está logado**

No navegador (DevTools → Application → Cookies):
- Deve haver cookie `session` do domínio `localhost`

### **2. Fazer login primeiro**

Se não estiver logado:
1. Acesse a página de login
2. Faça login
3. Depois tente usar o gráfico

### **3. Verificar requisições**

No DevTools → Network:
- Requisição `/api/v1/candles` deve ter:
  - **Cookie:** `session=...`
  - **Response:** JSON (não HTML)

---

## 🔧 ALTERNATIVA: Endpoint sem autenticação (temporário)

Se quiser testar sem login, pode remover temporariamente `@login_required`:

```python
# sne_radar_web.py
@app.route('/api/v1/candles')
# @login_required  # Comentar temporariamente
def api_v1_candles():
    # ...
```

**⚠️ ATENÇÃO:** Apenas para desenvolvimento! Remover em produção.

---

## 📝 PRÓXIMOS PASSOS

1. ✅ **Configurar Axios** para enviar cookies (`withCredentials: true`)
2. ⏳ **Fazer login** no sistema
3. ⏳ **Testar gráfico** novamente

---

**Status:** ✅ Correção aplicada - Faça login e teste novamente!


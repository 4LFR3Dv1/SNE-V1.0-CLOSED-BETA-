# 🚀 COMO FAZER DEPLOY NO RENDER - GUIA SIMPLIFICADO

**Sistema:** SNE Radar Web  
**Plataforma:** Render.com  
**Status:** ✅ Configurado e pronto

---

## 📋 O QUE VOCÊ JÁ TEM

✅ **render.yaml** - Configuração automática  
✅ **requirements_render.txt** - Dependências otimizadas  
✅ **database_config.py** - Banco de dados configurado  
✅ **sne_radar_web.py** - App Flask completo  

---

## 🎯 PASSO A PASSO RÁPIDO

### **OPÇÃO 1: Deploy Automático (RECOMENDADO)**

#### **1. Push para GitHub:**
```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Verificar status
git status

# Adicionar arquivos
git add .
git commit -m "Deploy: Configuração Render"
git push origin main
```

#### **2. No Render Dashboard:**

1. **Acesse:** https://dashboard.render.com
2. **Clique:** "New +" → "Blueprint"
3. **Conecte** seu repositório GitHub
4. **Render detectará automaticamente** o `render.yaml`
5. **Clique:** "Apply" para confirmar
6. **Render criará:**
   - ✅ Web Service (porta automática)
   - ✅ PostgreSQL Database
   - ✅ Todas as variáveis de ambiente
   - ✅ Health checks

#### **3. Aguardar Deploy:**
- ⏱️ **Build:** 2-5 minutos
- ✅ **Status:** Live após sucesso
- 🔗 **URL:** `https://sne-radar-web.onrender.com` (exemplo)

---

## ⚙️ OPÇÃO 2: Deploy Manual

### **1. Criar Web Service:**

No Dashboard Render:
- **Nome:** `sne-radar-web`
- **Environment:** `Python 3`
- **Build Command:**
```bash
pip install -r requirements_render.txt
pip install psycopg2-binary
```
- **Start Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT sne_radar_web:app
```

### **2. Criar PostgreSQL Database:**

- **Nome:** `sne-radar-db`
- **Plan:** Free
- **Database Name:** `sne_radar`
- **User:** `sne_radar_user`

### **3. Configurar Variáveis de Ambiente:**

No Web Service, adicione:

```bash
# Ambiente
FLASK_ENV=production
SECRET_KEY=(Render gera automaticamente)

# Banco de Dados (conecta automaticamente)
DB_HOST=(automático)
DB_PORT=(automático)
DB_NAME=sne_radar
DB_USER=sne_radar_user
DB_PASSWORD=(automático)

# Feature Flags
ENABLE_COINGLASS=false
ENABLE_CMC=false
ENABLE_TA_SUMMARY=false

# Configurações
UPDATE_INTERVAL=30
REQUEST_TIMEOUT=12
BINANCE_CALLS_PER_WINDOW=10
BINANCE_WINDOW_SECONDS=60
```

---

## ✅ VERIFICAR SE FUNCIONOU

### **1. Logs de Deploy:**

Na página do Web Service:
- **Vá em "Logs"**
- Procure por: `✅ Dependências instaladas`
- Procure por: `🚀 Iniciando SNE Radar...`
- ❌ Se houver erros, verifique mensagens

### **2. Teste a URL:**

Acesse: `https://seu-app.onrender.com`

**Deve mostrar:**
- ✅ Login page
- ✅ Criar conta
- ✅ Dashboard funcional

### **3. Teste Endpoints:**

```bash
# Health check (deve retornar 200 OK)
curl https://seu-app.onrender.com/health

# API de mercado
curl https://seu-app.onrender.com/api/v1/ta-summary

# Dashboard
curl https://seu-app.onrender.com/dashboard
```

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### **Problema 1: "Module not found"**

**Solução:**
- Verifique se `requirements_render.txt` tem todas as dependências
- Verifique se `gunicorn` está instalado

### **Problema 2: "psycopg2 not found"**

**Solução:**
Adicione ao Build Command:
```bash
pip install psycopg2-binary
```

### **Problema 3: "Database connection failed"**

**Solução:**
1. Verifique se o banco PostgreSQL foi criado
2. Verifique se as variáveis de ambiente do banco estão configuradas
3. Verifique se o banco está no mesmo projeto que o web service

### **Problema 4: "Port binding failed"**

**Solução:**
Certifique-se de usar `$PORT` no start command:
```bash
gunicorn --bind 0.0.0.0:$PORT sne_radar_web:app
```

### **Problema 5: "Request timeout"**

**Solução:**
Aumente o timeout no start command:
```bash
gunicorn --bind 0.0.0.0:$PORT --timeout 120 sne_radar_web:app
```

---

## 📊 RECURSOS DISPONÍVEIS (Plano Free)

| Recurso | Limite Free |
|---------|------------|
| **CPU** | 0.5 cores |
| **RAM** | 512 MB |
| **Storage** | 1 GB |
| **Bandwidth** | 100 GB/mês |
| **Sleep** | Dorme após 15min inatividade |
| **PostgreSQL** | 1 GB storage |

⚠️ **Importante:** No plano free, o app dorme após 15 minutos de inatividade. Primeira requisição após dormir leva ~30s para acordar.

---

## 🔄 ATUALIZAÇÕES AUTOMÁTICAS

### **Deploy Automático (push → deploy)**

Simplesmente faça push para `main`:
```bash
git add .
git commit -m "Update: Nova funcionalidade"
git push origin main
```

Render automaticamente:
1. Detecta mudanças
2. Faz novo build
3. Deploy automático

**Status no Dashboard:**
- 🔵 Building
- 🟢 Live

---

## 🎯 OTIMIZAÇÕES PARA PRODUÇÃO

### **1. Gunicorn Workers:**

Aumentar workers para performance:
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 sne_radar_web:app
```

### **2. Cache de APIs Externas:**

Evitar rate limits:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_market_data(symbol):
    # Cache de requisições
    pass
```

### **3. Rate Limiting:**

Proteger contra abuso:
```python
@limiter.limit("10 per minute")
@app.route('/api/v1/ta-summary')
def ta_summary():
    pass
```

---

## 📱 ACESSO VIA MOBILE

### **URL Pública:**

Após deploy, você terá uma URL pública:
```
https://sne-radar-web.onrender.com
```

**Acessível de qualquer lugar:**
- ✅ Desktop
- ✅ Mobile (iOS/Android)
- ✅ Tablets
- ✅ Qualquer navegador

### **Adicionar à Tela Inicial:**

**iOS:**
1. Safari → Abrir URL
2. Compartilhar → "Adicionar à Tela Inicial"

**Android:**
1. Chrome → Abrir URL
2. Menu → "Adicionar à tela inicial"

---

## 🔐 SEGURANÇA

### **HTTPS Automático:**

Render fornece HTTPS automaticamente:
- ✅ Certificado SSL válido
- ✅ Sem configuração adicional
- ✅ Renovação automática

### **Variáveis Sensíveis:**

Use o painel do Render para variáveis de ambiente:
- ✅ Não commite `.env` no git
- ✅ Use secrets do Render
- ✅ SENHAS nunca vão pro código

---

## 💰 CUSTOS

### **Plano Free:**
- ✅ **$0** - Grátis
- ✅ Apto para demonstrações
- ✅ Adequado para testes
- ⚠️ Limitações: 512MB RAM, 15min sleep

### **Plano Starter ($7/mês):**
- ✅ **Sem sleep**
- ✅ 512MB RAM
- ✅ 10 GB bandwidth
- ✅ Recomendado para produção

### **Plano Professional ($25/mês):**
- ✅ 1 GB RAM
- ✅ 50 GB bandwidth
- ✅ Sem limites
- ✅ Monitoramento avançado

---

## 🎉 EXEMPLO DE DEPLOY BEM-SUCEDIDO

```bash
# 1. Push para GitHub
git add .
git commit -m "Deploy: Configuração Render"
git push origin main

# 2. No Render Dashboard:
# - Criar novo Blueprint
# - Conectar repositório
# - Render detecta render.yaml automaticamente

# 3. Aguardar build:
# Build Command: pip install -r requirements_render.txt
# ✅ Installing dependencies...
# ✅ Building app...
# ✅ Deployed successfully!

# 4. Acessar:
# https://sne-radar-web-xxxx.onrender.com
```

---

## 📞 CHECKLIST DE DEPLOY

Antes de fazer deploy, verifique:

- [ ] Código está no GitHub
- [ ] `render.yaml` existe no repositório
- [ ] `requirements_render.txt` tem todas dependências
- [ ] `database_config.py` está configurado
- [ ] `sne_radar_web.py` tem todos os imports
- [ ] Testou localmente (`python3 sne_radar_web.py`)
- [ ] Variáveis de ambiente configuradas no Render
- [ ] PostgreSQL database criado
- [ ] Health check endpoint funciona

**Se tudo ✅, pode fazer deploy!**

---

## 🚀 COMANDO RÁPIDO

```bash
# Preparar
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
git status

# Deploy
git add .
git commit -m "Deploy para Render"
git push origin main

# Ir para render.com e criar Blueprint
# URL será: https://sne-radar-web.onrender.com
```

---

## ✅ CONCLUSÃO

**O sistema está pronto para deploy no Render!**

**Arquivos já prontos:**
- ✅ `render.yaml` - Configuração automática
- ✅ `requirements_render.txt` - Dependências
- ✅ `database_config.py` - Banco configurado
- ✅ `sne_radar_web.py` - App funcionando

**Próximos passos:**
1. Push para GitHub
2. Criar Blueprint no Render
3. Deploy automático

**Tempo estimado:** 10 minutos ⏱️

---

**🎉 Sucesso no deploy!**




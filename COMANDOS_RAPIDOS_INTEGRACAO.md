# ⚡ COMANDOS RÁPIDOS - INTEGRAÇÃO

## 🔐 1. ATUALIZAR SECRETS

### Interativo
```bash
./atualizar_secrets.sh sne-v1
```

### Rápido (com valores)
```bash
./atualizar_secrets_rapido.sh sne-v1 \
  "TELEGRAM_TOKEN" \
  "TELEGRAM_CHAT_ID" \
  "BINANCE_API_KEY" \
  "BINANCE_SECRET_KEY"
```

### Manual (um por um)
```bash
# Telegram
echo -n "TOKEN" | gcloud secrets versions add sne-telegram-bot-token --data-file=-
echo -n "CHAT_ID" | gcloud secrets versions add sne-telegram-chat-id --data-file=-

# Binance
echo -n "API_KEY" | gcloud secrets versions add sne-binance-api-key --data-file=-
echo -n "SECRET_KEY" | gcloud secrets versions add sne-binance-secret-key --data-file=-
```

---

## 🔍 2. VERIFICAR SECRETS

```bash
# Listar todos
gcloud secrets list --project=sne-v1

# Ver versões
gcloud secrets versions list sne-telegram-bot-token --project=sne-v1
gcloud secrets versions list sne-binance-api-key --project=sne-v1
```

---

## 🧪 3. TESTAR SERVIÇOS

```bash
# Health check
curl https://sne-web-pqhownilea-uc.a.run.app/health

# API Analyze
curl -X POST https://sne-web-pqhownilea-uc.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"pair": "BTCUSDT"}'

# API Signal
curl https://sne-web-pqhownilea-uc.a.run.app/api/signal
```

---

## 🚀 4. DEPLOY

```bash
# Deploy completo
./deploy_cloud_build.sh sne-v1 us-central1

# Ver logs
gcloud run services logs read sne-web --region=us-central1 --limit=50
```

---

## 📋 5. VERIFICAR STATUS

```bash
# Listar serviços
gcloud run services list --region=us-central1

# Ver detalhes
gcloud run services describe sne-web --region=us-central1

# Ver logs
gcloud run services logs read sne-web --region=us-central1 --limit=20
```

---

**💡 Execute `./atualizar_secrets.sh sne-v1` para começar!**




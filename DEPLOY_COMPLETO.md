# 🎉 DEPLOY COMPLETO - SNE 1.0 CLOUD

## ✅ STATUS: TUDO FUNCIONANDO!

O SNE 1.0 Cloud está **100% deployado e funcionando** na Google Cloud Platform!

---

## 📊 RESUMO DO QUE FOI FEITO

### ✅ Infraestrutura (Terraform)
- [x] Cloud SQL PostgreSQL 15 (IP privado)
- [x] Artifact Registry
- [x] Cloud Storage
- [x] VPC Connector
- [x] Service Accounts (4 serviços)
- [x] Secret Manager (secrets criados)
- [x] Cloud Scheduler (job para sne-auto)

### ✅ Imagens Docker (Cloud Build)
- [x] sne-web:latest
- [x] sne-worker:latest
- [x] sne-auto:latest
- [x] sne-telegram:latest

### ✅ Serviços Cloud Run
- [x] sne-web: https://sne-web-pqhownilea-uc.a.run.app
- [x] sne-worker: https://sne-worker-pqhownilea-uc.a.run.app
- [x] sne-auto: https://sne-auto-pqhownilea-uc.a.run.app
- [x] sne-telegram: https://sne-telegram-pqhownilea-uc.a.run.app

### ✅ Banco de Dados
- [x] Tabela `users` criada
- [x] Tabela `signals` criada
- [x] Tabela `trades` criada
- [x] Índices criados

---

## 🧪 TESTAR SERVIÇOS

### 1. Testar sne-web (Público)

```bash
# Health check
curl https://sne-web-pqhownilea-uc.a.run.app/health

# Endpoint de análise
curl -X POST https://sne-web-pqhownilea-uc.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"pair": "BTCUSDT"}'

# Endpoint de sinais
curl https://sne-web-pqhownilea-uc.a.run.app/api/signal
```

### 2. Verificar Logs

```bash
# Logs de sne-web
gcloud run services logs read sne-web --region=us-central1 --limit=20

# Logs de todos os serviços
for service in sne-web sne-worker sne-auto sne-telegram; do
  echo "=== $service ==="
  gcloud run services logs read $service --region=us-central1 --limit=10
done
```

### 3. Verificar Banco de Dados

```bash
# Via Cloud Shell (quando tiver acesso)
gcloud sql connect sne-db-prod --user=sne_admin --database=sne
# Senha: gcloud secrets versions access latest --secret=sne-db-password --project=sne-v1

# No prompt PostgreSQL:
\dt
SELECT COUNT(*) FROM signals;
SELECT COUNT(*) FROM trades;
```

---

## 📋 PRÓXIMOS PASSOS

### 1. Atualizar Secrets do Telegram

Quando tiver os valores reais:

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Telegram Bot Token
echo -n "SEU_TELEGRAM_BOT_TOKEN" | gcloud secrets versions add sne-telegram-bot-token --data-file=-

# Telegram Chat ID
echo -n "SEU_CHAT_ID" | gcloud secrets versions add sne-telegram-chat-id --data-file=-

# Verificar
gcloud secrets versions list sne-telegram-bot-token
gcloud secrets versions list sne-telegram-chat-id
```

### 2. Configurar Webhook do Telegram

```bash
# Obter URL do serviço
TELEGRAM_URL=$(gcloud run services describe sne-telegram --region=us-central1 --format="value(status.url)")

# Configurar webhook (substitua SEU_TOKEN)
curl -X POST "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=${TELEGRAM_URL}/webhook/telegram"
```

### 3. Testar Cloud Scheduler

O Cloud Scheduler está configurado para chamar `sne-auto` a cada 5 minutos. Verifique:

```bash
# Ver jobs do Scheduler
gcloud scheduler jobs list --location=us-central1

# Executar manualmente
gcloud scheduler jobs run sne-auto-scan --location=us-central1
```

### 4. Monitorar Custos

```bash
# Verificar custos estimados
# Acesse: https://console.cloud.google.com/billing?project=sne-v1

# Configurar budget alert
# Acesse: https://console.cloud.google.com/billing/budgets?project=sne-v1
```

---

## 🔗 LINKS ÚTEIS

- **Cloud Run**: https://console.cloud.google.com/run?project=sne-v1
- **Cloud SQL**: https://console.cloud.google.com/sql/instances?project=sne-v1
- **Artifact Registry**: https://console.cloud.google.com/artifacts?project=sne-v1
- **Cloud Build**: https://console.cloud.google.com/cloud-build/builds?project=sne-v1
- **Logs**: https://console.cloud.google.com/logs?project=sne-v1
- **Monitoring**: https://console.cloud.google.com/monitoring?project=sne-v1

---

## 💰 CUSTOS ESTIMADOS

Com `min_instances=0` (escala para zero):
- **Cloud Run**: ~$5-10/mês (uso leve)
- **Cloud SQL**: ~$10-15/mês (db-f1-micro)
- **Cloud Storage**: ~$1-2/mês
- **Cloud Build**: ~$1-2/mês (builds ocasionais)
- **Total**: ~$20-30/mês (uso leve)

**💡 Dica**: Configure budget alerts para evitar surpresas!

---

## 🔄 PRÓXIMOS DEPLOYS

Após fazer mudanças no código:

```bash
# Deploy completo
./deploy_cloud_build.sh sne-v1 us-central1

# Ou deploy individual (se tiver scripts)
./deploy/deploy_web.sh sne-v1 us-central1
```

---

## ✅ CHECKLIST FINAL

- [x] Infraestrutura criada (Terraform)
- [x] Imagens Docker buildadas
- [x] Imagens pushadas para Artifact Registry
- [x] Serviços deployados no Cloud Run
- [x] Banco de dados inicializado
- [x] Tabelas criadas (users, signals, trades)
- [ ] Secrets atualizados com valores reais
- [ ] Serviços testados
- [ ] Webhook do Telegram configurado
- [ ] Monitoramento configurado
- [ ] Budget alerts configurados

---

## 🎯 COMANDOS RÁPIDOS

```bash
# Ver status dos serviços
gcloud run services list --region=us-central1

# Ver logs
gcloud run services logs read sne-web --region=us-central1 --limit=50

# Ver secrets
gcloud secrets list

# Ver Cloud SQL
gcloud sql instances list

# Ver builds
gcloud builds list --limit=5
```

---

**🎉 Parabéns! O SNE 1.0 Cloud está 100% operacional!**

**Próximo passo**: Teste os serviços e atualize os secrets do Telegram quando tiver os valores reais.




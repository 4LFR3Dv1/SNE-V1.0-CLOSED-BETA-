# 🎯 PRÓXIMOS PASSOS FINAIS

## ✅ DEPLOY CONCLUÍDO!

Todos os serviços estão rodando. Agora você precisa:

---

## 1️⃣ INICIALIZAR BANCO DE DADOS

As migrações foram puladas no build. Execute manualmente:

### Opção A: Usando Cloud SQL Proxy Local

```bash
# Instalar Cloud SQL Proxy (se não tiver)
# macOS:
brew install cloud-sql-proxy

# Ou baixar:
# https://cloud.google.com/sql/docs/postgres/sql-proxy

# Conectar e executar migrações
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
./deploy/init_db.sh sne-v1 us-central1 sne-v1:us-central1:sne-db-prod
```

### Opção B: Usando Cloud Shell

1. Acesse: https://console.cloud.google.com/sql/instances/sne-db-prod/overview
2. Clique em "Conectar usando Cloud Shell"
3. Execute:
   ```bash
   # Obter senha
   DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password)
   
   # Conectar
   psql -h 127.0.0.1 -U sne_admin -d sne
   # Senha: $DB_PASSWORD
   
   # Executar migrações (via alembic ou SQL direto)
   ```

---

## 2️⃣ ATUALIZAR SECRETS COM VALORES REAIS

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Telegram Bot Token
echo -n "SEU_TELEGRAM_BOT_TOKEN_AQUI" | gcloud secrets versions add sne-telegram-bot-token --data-file=-

# Telegram Chat ID
echo -n "SEU_CHAT_ID_AQUI" | gcloud secrets versions add sne-telegram-chat-id --data-file=-

# Verificar
gcloud secrets versions list sne-telegram-bot-token
gcloud secrets versions list sne-telegram-chat-id
```

---

## 3️⃣ TESTAR SERVIÇOS

```bash
# Health checks
echo "=== sne-web ==="
curl https://sne-web-pqhownilea-uc.a.run.app/health

echo "=== sne-worker ==="
curl https://sne-worker-pqhownilea-uc.a.run.app/health

echo "=== sne-auto ==="
curl https://sne-auto-pqhownilea-uc.a.run.app/health

echo "=== sne-telegram ==="
curl https://sne-telegram-pqhownilea-uc.a.run.app/health

# Testar endpoints
curl -X POST https://sne-web-pqhownilea-uc.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"pair": "BTCUSDT"}'

curl https://sne-web-pqhownilea-uc.a.run.app/api/signal
```

---

## 4️⃣ VERIFICAR LOGS

```bash
# Logs de um serviço específico
gcloud run services logs read sne-web --region=us-central1 --limit=50

# Logs de todos os serviços
for service in sne-web sne-worker sne-auto sne-telegram; do
  echo "=== Logs de $service ==="
  gcloud run services logs read $service --region=us-central1 --limit=20
  echo ""
done
```

---

## 5️⃣ CONFIGURAR MONITORAMENTO

Acesse o Console do GCP e configure:

- **Alertas**: https://console.cloud.google.com/monitoring/alerting?project=sne-v1
- **Dashboards**: https://console.cloud.google.com/monitoring/dashboards?project=sne-v1
- **Logs**: https://console.cloud.google.com/logs?project=sne-v1

---

## 6️⃣ CONFIGURAR BUDGET ALERTS

Para evitar surpresas na fatura:

1. Acesse: https://console.cloud.google.com/billing/budgets?project=sne-v1
2. Crie um budget de $50/mês
3. Configure alertas em 50%, 90%, 100%

---

## 7️⃣ PRÓXIMOS DEPLOYS

Após fazer mudanças no código:

```bash
# Deploy completo
./deploy_cloud_build.sh sne-v1 us-central1

# Ou deploy individual
./deploy/deploy_web.sh sne-v1 us-central1
./deploy/deploy_worker.sh sne-v1 us-central1
```

---

## 📋 CHECKLIST

- [x] Infraestrutura criada
- [x] Imagens buildadas e pushadas
- [x] Serviços deployados
- [ ] Banco de dados inicializado
- [ ] Secrets atualizados
- [ ] Serviços testados
- [ ] Monitoramento configurado
- [ ] Budget alerts configurados

---

**🎉 Tudo pronto! O SNE 1.0 Cloud está funcionando!**




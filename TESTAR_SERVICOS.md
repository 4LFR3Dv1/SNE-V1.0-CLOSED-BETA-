# ✅ Testar Serviços Após Migração

## 🌍 URLs dos Serviços (europe-west1)

### Serviços Cloud Run

- **sne-web**: https://sne-web-pqhownilea-ew.a.run.app
- **sne-worker**: https://sne-worker-pqhownilea-ew.a.run.app
- **sne-auto**: https://sne-auto-pqhownilea-ew.a.run.app
- **sne-telegram**: https://sne-telegram-pqhownilea-ew.a.run.app

## 🧪 Testes

### 1. Health Checks

```bash
# sne-web
curl https://sne-web-pqhownilea-ew.a.run.app/health

# sne-worker
curl https://sne-worker-pqhownilea-ew.a.run.app/health

# sne-auto
curl https://sne-auto-pqhownilea-ew.a.run.app/health

# sne-telegram
curl https://sne-telegram-pqhownilea-ew.a.run.app/health
```

### 2. Testar API de Análise

```bash
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'
```

### 3. Testar com outros pares

```bash
# ETHUSDT
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "ETHUSDT", "timeframe": "15m"}'

# SOLUSDT
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "SOLUSDT", "timeframe": "1h"}'
```

### 4. Verificar Logs

```bash
# Logs do sne-web
gcloud run services logs read sne-web \
    --region=europe-west1 \
    --project=sne-v1 \
    --limit=20

# Logs do sne-worker
gcloud run services logs read sne-worker \
    --region=europe-west1 \
    --project=sne-v1 \
    --limit=20

# Logs em tempo real
gcloud run services logs tail sne-web \
    --region=europe-west1 \
    --project=sne-v1
```

### 5. Verificar Status dos Serviços

```bash
gcloud run services list \
    --region=europe-west1 \
    --project=sne-v1
```

### 6. Testar Cloud Scheduler

```bash
# Verificar job do scheduler
gcloud scheduler jobs describe sne-auto-scan \
    --location=us-central1 \
    --project=sne-v1

# Executar manualmente
gcloud scheduler jobs run sne-auto-scan \
    --location=us-central1 \
    --project=sne-v1
```

## 🔍 Verificar Conexão com Cloud SQL

```bash
# Verificar conexão do Cloud SQL
gcloud sql instances describe sne-db-prod \
    --project=sne-v1 \
    --format="value(connectionName)"

# Deve retornar: sne-v1:europe-west1:sne-db-prod
```

## ✅ Checklist de Validação

- [ ] Todos os serviços estão com status "Ready"
- [ ] Health checks retornam 200 OK
- [ ] API de análise funciona corretamente
- [ ] Logs não mostram erros de conexão
- [ ] Cloud SQL está acessível
- [ ] Cloud Scheduler está configurado corretamente

## 🐛 Troubleshooting

### Se health check falhar:

```bash
# Ver logs detalhados
gcloud run services logs read sne-web \
    --region=europe-west1 \
    --project=sne-v1 \
    --limit=50
```

### Se API retornar erro:

```bash
# Verificar variáveis de ambiente
gcloud run services describe sne-web \
    --region=europe-west1 \
    --project=sne-v1 \
    --format="value(spec.template.spec.containers[0].env)"
```

### Se conexão com Cloud SQL falhar:

```bash
# Verificar VPC Connector
gcloud compute networks vpc-access connectors describe sne-vpc-connector \
    --region=europe-west1 \
    --project=sne-v1
```

---

**🎉 Migração concluída!** Todos os serviços estão rodando em `europe-west1`.


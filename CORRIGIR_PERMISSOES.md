# 🔐 CORRIGIR PERMISSÕES DOS SERVIÇOS

## ⚠️ PROBLEMA

Erro "Forbidden" ao acessar os serviços. Isso acontece porque os serviços não têm permissão pública configurada.

---

## ✅ SOLUÇÃO: Configurar Permissões IAM

### 1. Tornar sne-web Público

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Permitir acesso público ao sne-web
gcloud run services add-iam-policy-binding sne-web \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

### 2. Manter Outros Serviços Privados (Recomendado)

Os outros serviços (sne-worker, sne-auto, sne-telegram) devem permanecer privados por segurança:

- **sne-worker**: Acessado apenas internamente
- **sne-auto**: Chamado pelo Cloud Scheduler
- **sne-telegram**: Recebe webhooks do Telegram

---

## 🧪 TESTAR APÓS CORRIGIR

```bash
# Health check (deve funcionar agora)
curl https://sne-web-pqhownilea-uc.a.run.app/health

# Endpoint de análise
curl -X POST https://sne-web-pqhownilea-uc.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"pair": "BTCUSDT"}'
```

---

## 🔍 VERIFICAR PERMISSÕES

```bash
# Ver permissões do sne-web
gcloud run services get-iam-policy sne-web --region=us-central1

# Ver permissões dos outros serviços
gcloud run services get-iam-policy sne-worker --region=us-central1
gcloud run services get-iam-policy sne-auto --region=us-central1
gcloud run services get-iam-policy sne-telegram --region=us-central1
```

---

## 🔒 SEGURANÇA

**sne-web** pode ser público porque:
- É o frontend/API pública
- Não expõe dados sensíveis
- Pode ter autenticação JWT no futuro

**Outros serviços** devem permanecer privados:
- Acessados apenas por serviços autorizados
- Cloud Scheduler (sne-auto)
- Webhooks autenticados (sne-telegram)
- Chamadas internas (sne-worker)

---

## 📋 COMANDO COMPLETO

```bash
# Tornar sne-web público
gcloud run services add-iam-policy-binding sne-web \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# Testar
curl https://sne-web-pqhownilea-uc.a.run.app/health
```

---

**💡 Execute o comando acima para tornar o sne-web público e testar!**




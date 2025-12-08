# 🔓 Corrigir Erro 403 Forbidden

## ❌ Problema

Os serviços Cloud Run estão retornando `403 Forbidden` porque o acesso público não está habilitado.

## ✅ Solução

### Opção 1: Usar Script (Recomendado)

```bash
./habilitar_acesso_publico.sh sne-v1 europe-west1
```

### Opção 2: Comandos Manuais

Execute os seguintes comandos para habilitar acesso público:

```bash
# sne-web
gcloud run services add-iam-policy-binding sne-web \
    --region=europe-west1 \
    --project=sne-v1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# sne-worker
gcloud run services add-iam-policy-binding sne-worker \
    --region=europe-west1 \
    --project=sne-v1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# sne-auto
gcloud run services add-iam-policy-binding sne-auto \
    --region=europe-west1 \
    --project=sne-v1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# sne-telegram
gcloud run services add-iam-policy-binding sne-telegram \
    --region=europe-west1 \
    --project=sne-v1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

### Opção 3: Atualizar Terraform

Se preferir fazer via Terraform, edite `infra/terraform/variables.tf`:

```hcl
variable "public_web" {
  description = "Allow unauthenticated access to sne-web service"
  type        = bool
  default     = true  # Mudar para true
}
```

E depois aplique:

```bash
cd infra/terraform
terraform apply -var="project_id=sne-v1" -var="region=europe-west1" -var="public_web=true"
```

## 🧪 Testar Após Habilitar

```bash
# Health check
curl https://sne-web-pqhownilea-ew.a.run.app/health

# API de análise
curl -X POST https://sne-web-pqhownilea-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'
```

## 🔒 Segurança

**⚠️ Atenção**: Habilitar acesso público significa que qualquer pessoa pode acessar os endpoints. 

Para produção, considere:
- Implementar autenticação (API keys, OAuth, etc.)
- Usar Cloud Armor para rate limiting
- Restringir acesso apenas a IPs específicos
- Manter apenas `sne-web` público e os outros privados

## 📋 URLs dos Serviços

- **sne-web**: https://sne-web-pqhownilea-ew.a.run.app
- **sne-worker**: https://sne-worker-pqhownilea-ew.a.run.app
- **sne-auto**: https://sne-auto-pqhownilea-ew.a.run.app
- **sne-telegram**: https://sne-telegram-pqhownilea-ew.a.run.app

---

**Execute o script `habilitar_acesso_publico.sh` para resolver rapidamente!** 🚀


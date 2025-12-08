# 🌍 MUDAR REGIÃO PARA EVITAR BLOQUEIO DA BINANCE

## ⚠️ PROBLEMA IDENTIFICADO

A Binance está bloqueando requisições da região `us-central1` (Iowa, EUA) com erro **451**:
```
"Service unavailable from a restricted location according to 'b. Eligibility'"
```

## ✅ SOLUÇÃO: MUDAR PARA REGIÃO NÃO BLOQUEADA

### Regiões Recomendadas (não bloqueadas pela Binance):

1. **🇪🇺 Europa** (Recomendado):
   - `europe-west1` (Bélgica) - **RECOMENDADO**
   - `europe-west4` (Holanda)
   - `europe-north1` (Finlândia)

2. **🇸🇬 Ásia**:
   - `asia-southeast1` (Singapura) - **RECOMENDADO**
   - `asia-east1` (Taiwan)
   - `asia-northeast1` (Tóquio)

3. **🇧🇷 América do Sul**:
   - `southamerica-east1` (São Paulo, Brasil)

---

## 🚀 COMO MUDAR A REGIÃO

### Opção 1: Mudar via Terraform (Recomendado)

1. **Editar `infra/terraform/variables.tf`**:
   ```hcl
   variable "region" {
     description = "GCP Region"
     type        = string
     default     = "europe-west1"  # Mudado de us-central1
   }
   ```

2. **Aplicar mudanças**:
   ```bash
   cd infra/terraform
   terraform plan -var="project_id=sne-v1" -var="region=europe-west1"
   terraform apply -var="project_id=sne-v1" -var="region=europe-west1"
   ```

### Opção 2: Mudar via Deploy Script

Edite `deploy_cloud_build.sh` e mude a região padrão:

```bash
REGION=${2:-"europe-west1"}  # Mudado de us-central1
```

---

## ⚠️ ATENÇÃO: RECURSOS QUE PRECISAM SER RECRIADOS

Ao mudar a região, alguns recursos precisam ser recriados:

1. **Cloud Run Services** - Serão recriados na nova região
2. **Cloud SQL** - Pode precisar ser recriado (ou usar Cloud SQL Proxy)
3. **VPC Connector** - Precisa ser recriado na nova região
4. **Artifact Registry** - Precisa ser recriado na nova região

**⚠️ IMPORTANTE**: Faça backup dos dados antes de mudar!

---

## 📋 CHECKLIST DE MIGRAÇÃO

- [ ] Fazer backup do banco de dados Cloud SQL
- [ ] Exportar secrets do Secret Manager (se necessário)
- [ ] Mudar variável `region` no Terraform
- [ ] Executar `terraform plan` para ver mudanças
- [ ] Executar `terraform apply` para aplicar mudanças
- [ ] Atualizar Artifact Registry para nova região
- [ ] Rebuild e redeploy das imagens Docker
- [ ] Testar endpoints após migração
- [ ] Verificar logs para confirmar acesso à Binance

---

## 🧪 TESTE APÓS MUDANÇA

Após mudar a região, teste:

```bash
curl -X POST https://sne-web-<hash>-<region>.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'
```

Verifique os logs:
```bash
gcloud run services logs read sne-web --region=europe-west1 --limit=20
```

Se não houver mais erro 451, a migração foi bem-sucedida! ✅

---

## 💡 RECOMENDAÇÃO FINAL

**Recomendo usar `europe-west1` (Bélgica)** porque:
- ✅ Não é bloqueada pela Binance
- ✅ Boa latência para Europa e Ásia
- ✅ Preços competitivos
- ✅ Alta disponibilidade




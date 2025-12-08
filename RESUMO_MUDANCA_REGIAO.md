# ✅ MUDANÇA DE REGIÃO CONFIGURADA

## 🎯 O QUE FOI FEITO

Atualizei a configuração padrão para usar **`europe-west1` (Bélgica)** ao invés de `us-central1` (Iowa, EUA) para evitar o bloqueio geográfico da Binance (erro 451).

---

## 📝 ARQUIVOS ATUALIZADOS

1. ✅ **`infra/terraform/variables.tf`**:
   - `region`: `us-central1` → `europe-west1`
   - `artifact_registry_location`: `us-central1` → `europe-west1`
   - `zone`: `us-central1-a` → `europe-west1-b`

2. ✅ **`deploy_cloud_build.sh`**:
   - Região padrão: `us-central1` → `europe-west1`

---

## 🚀 PRÓXIMOS PASSOS

### Opção 1: Migração Completa (Recomendado)

Execute o script de migração:

```bash
./migrar_regiao.sh sne-v1 us-central1 europe-west1
```

Este script irá:
- Fazer backup do banco de dados
- Aplicar mudanças no Terraform
- Recriar recursos na nova região

### Opção 2: Aplicar Terraform Manualmente

```bash
cd infra/terraform
terraform init -upgrade
terraform plan -var="project_id=sne-v1" -var="region=europe-west1"
terraform apply -var="project_id=sne-v1" -var="region=europe-west1"
```

### Opção 3: Deploy Direto (Mais Rápido)

Se você já tem os recursos criados, pode simplesmente fazer um novo deploy:

```bash
./deploy_cloud_build.sh sne-v1 europe-west1
```

---

## ⚠️ IMPORTANTE

**Recursos que serão recriados na nova região:**
- ✅ Cloud Run Services (sne-web, sne-worker, sne-auto, sne-telegram)
- ✅ Artifact Registry
- ✅ VPC Connector
- ⚠️ Cloud SQL (pode precisar ser recriado ou usar Cloud SQL Proxy)

**⚠️ ATENÇÃO**: Faça backup dos dados antes de migrar!

---

## 🧪 TESTE APÓS MIGRAÇÃO

Após a migração, teste:

```bash
# Health check
curl https://sne-web-<hash>-ew.a.run.app/health

# Análise completa
curl -X POST https://sne-web-<hash>-ew.a.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1h"}'
```

Verifique os logs:
```bash
gcloud run services logs read sne-web --region=europe-west1 --limit=20
```

**✅ Se não houver mais erro 451, a migração foi bem-sucedida!**

---

## 📋 CHECKLIST

- [x] Atualizar `variables.tf` com nova região
- [x] Atualizar `deploy_cloud_build.sh` com nova região
- [x] Criar script de migração `migrar_regiao.sh`
- [x] Criar documentação `MUDAR_REGIAO_BINANCE.md`
- [ ] Executar migração (você precisa fazer isso)
- [ ] Testar endpoints após migração
- [ ] Verificar logs para confirmar acesso à Binance

---

## 💡 POR QUE EUROPE-WEST1?

- ✅ **Não bloqueada pela Binance** (resolverá o erro 451)
- ✅ **Boa latência** para Europa e Ásia
- ✅ **Preços competitivos** no GCP
- ✅ **Alta disponibilidade** e confiabilidade
- ✅ **Suporte completo** a todos os serviços GCP necessários

---

**🚀 Pronto para migrar! Execute o script ou aplique o Terraform manualmente.**




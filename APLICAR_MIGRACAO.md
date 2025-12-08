# ✅ Aplicar Migração - Próximos Passos

## 📋 Status Atual

✅ Novo plano Terraform gerado com sucesso!
✅ Plano salvo em `infra/terraform/tfplan`

## ⚠️ IMPORTANTE: Verificar Deletion Protection

Antes de aplicar, certifique-se de que o deletion_protection foi desabilitado:

```bash
# Verificar status atual
gcloud sql instances describe sne-db-prod \
    --project=sne-v1 \
    --format="value(settings.deletionProtectionEnabled)"
```

Se retornar `True`, execute:

```bash
# Desabilitar proteção
gcloud sql instances patch sne-db-prod \
    --project=sne-v1 \
    --no-deletion-protection
```

## 🚀 Aplicar Migração

Depois de verificar/desabilitar a proteção:

```bash
cd infra/terraform
terraform apply tfplan
```

## 📊 O Que Será Feito

1. **Criar serviços Cloud Run** em `europe-west1`:
   - sne-auto
   - sne-web  
   - sne-worker

2. **Recriar Cloud SQL** em `europe-west1`:
   - ⚠️ **Dados serão perdidos** se não houver backup!
   - Certifique-se de ter backup antes de continuar

3. **Atualizar Cloud Scheduler** com nova URL

## 💾 Backup do Banco (RECOMENDADO)

Antes de aplicar, faça backup do banco:

```bash
# Criar backup manual
gcloud sql backups create \
    --instance=sne-db-prod \
    --project=sne-v1 \
    --description="Backup antes de migração para europe-west1"

# Listar backups
gcloud sql backups list \
    --instance=sne-db-prod \
    --project=sne-v1
```

## ⏱️ Tempo Estimado

- Cloud Run services: ~2-3 minutos cada
- Cloud SQL: ~5-10 minutos (criação)
- **Total**: ~15-20 minutos

## ✅ Após Aplicar

1. **Rebuild imagens Docker** na nova região:
   ```bash
   ./deploy_cloud_build.sh sne-v1 europe-west1
   ```

2. **Verificar serviços**:
   ```bash
   gcloud run services list --region=europe-west1 --project=sne-v1
   ```

3. **Testar endpoints**:
   ```bash
   # Obter URL
   gcloud run services describe sne-web \
       --region=europe-west1 \
       --format="value(status.url)"
   
   # Testar
   curl https://sne-web-<hash>-ew.a.run.app/health
   ```

---

**⚠️ Lembre-se**: O Cloud SQL será recriado e os dados serão perdidos se não houver backup!


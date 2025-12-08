# 🔧 Resolver Migração de Região - Cloud SQL

## ❌ Problema Encontrado

A migração falhou porque o Cloud SQL tem `deletion_protection` habilitado, impedindo a exclusão da instância.

## ✅ Solução

### Opção 1: Desabilitar Proteção e Continuar (Recomendado)

Execute os seguintes comandos:

```bash
# 1. Desabilitar deletion_protection
gcloud sql instances patch sne-db-prod \
    --project=sne-v1 \
    --no-deletion-protection

# 2. Continuar com o Terraform apply
cd infra/terraform
terraform apply tfplan
```

### Opção 2: Usar Script Automatizado

```bash
# Desabilitar proteção
./fix_deletion_protection.sh sne-v1 sne-db-prod

# Continuar migração
cd infra/terraform
terraform apply tfplan
```

### Opção 3: Remover do Estado e Recriar (Se a instância já foi destruída)

Se a instância já foi destruída mas o Terraform ainda a referencia:

```bash
cd infra/terraform

# Remover do estado
terraform state rm google_sql_database_instance.sne_db
terraform state rm google_sql_database.sne_database
terraform state rm google_sql_user.sne_admin

# Recriar plano
terraform plan -var="project_id=sne-v1" -var="region=europe-west1" -out=tfplan

# Aplicar
terraform apply tfplan
```

## 📋 O Que Aconteceu

1. ✅ Artifact Registry foi recriado em `europe-west1`
2. ✅ VPC Connector foi recriado em `europe-west1`
3. ✅ Storage Bucket foi recriado em `europe-west1`
4. ✅ Cloud Run services foram destruídos (serão recriados)
5. ❌ Cloud SQL não pôde ser destruído (deletion_protection)

## 🎯 Próximos Passos Após Resolver

1. **Rebuild das imagens Docker** na nova região:
   ```bash
   ./deploy_cloud_build.sh sne-v1 europe-west1
   ```

2. **Verificar serviços Cloud Run**:
   ```bash
   gcloud run services list --region=europe-west1 --project=sne-v1
   ```

3. **Testar endpoints**:
   ```bash
   # Obter URL do serviço
   gcloud run services describe sne-web --region=europe-west1 --format="value(status.url)"
   
   # Testar health
   curl https://sne-web-<hash>-ew.a.run.app/health
   ```

## ⚠️ Importante

- **Backup**: Certifique-se de que há backup do banco antes de migrar
- **Downtime**: Haverá downtime durante a migração
- **Dados**: Se o Cloud SQL for recriado, você precisará restaurar os dados do backup

## 🔄 Alternativa: Manter Cloud SQL na Região Original

Se preferir manter o Cloud SQL em `us-central1` e apenas migrar os serviços Cloud Run:

1. Remova o Cloud SQL do plano Terraform temporariamente
2. Migre apenas os serviços Cloud Run
3. Configure os serviços para acessar o Cloud SQL via VPC Peering entre regiões

---

**Execute a Opção 1 para resolver rapidamente!** 🚀


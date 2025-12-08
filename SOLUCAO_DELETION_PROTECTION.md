# 🔧 Solução: Deletion Protection ainda ativo

## ❌ Problema

Mesmo após desabilitar o `deletion_protection` via `gcloud`, o Terraform ainda está tentando usar o estado antigo que mostra `deletion_protection = true`.

## ✅ Soluções

### Opção 1: Aguardar Propagação (Recomendado)

A mudança pode levar alguns minutos para se propagar na API do GCP. Aguarde 1-2 minutos e tente novamente:

```bash
cd infra/terraform

# Aguardar 60 segundos
sleep 60

# Aplicar novamente
terraform apply -var="project_id=sne-v1" -var="region=europe-west1" -auto-approve
```

### Opção 2: Usar Script com Retry

Use o script que cria retries automáticos:

```bash
cd infra/terraform
./apply_migration.sh sne-v1 europe-west1
```

### Opção 3: Forçar Atualização do Estado

Remover e reimportar o recurso do estado:

```bash
cd infra/terraform

# Remover do estado
terraform state rm google_sql_database_instance.sne_db
terraform state rm google_sql_database.sne_database
terraform state rm google_sql_user.sne_admin

# Reimportar (isso vai detectar que deletion_protection está desabilitado)
terraform import google_sql_database_instance.sne_db sne-db-prod
terraform import google_sql_database.sne_database projects/sne-v1/instances/sne-db-prod/databases/sne
terraform import google_sql_user.sne_admin sne_admin//sne-db-prod

# Aplicar
terraform apply -var="project_id=sne-v1" -var="region=europe-west1" -auto-approve
```

### Opção 4: Verificar e Desabilitar Novamente

```bash
# Verificar status atual
gcloud sql instances describe sne-db-prod \
    --project=sne-v1 \
    --format="value(settings.deletionProtectionEnabled)"

# Se ainda estiver True, desabilitar novamente
gcloud sql instances patch sne-db-prod \
    --project=sne-v1 \
    --no-deletion-protection

# Aguardar 30 segundos
sleep 30

# Aplicar
cd infra/terraform
terraform apply -var="project_id=sne-v1" -var="region=europe-west1" -auto-approve
```

## 🔍 Verificar Status

```bash
# Verificar via gcloud
gcloud sql instances describe sne-db-prod \
    --project=sne-v1 \
    --format="value(settings.deletionProtectionEnabled)"

# Verificar no Terraform
cd infra/terraform
terraform state show google_sql_database_instance.sne_db | grep deletion
```

## 💡 Por que isso acontece?

O Terraform mantém um estado local que pode estar desatualizado. Quando você muda algo diretamente via `gcloud`, o Terraform não sabe até que você execute `terraform refresh` ou `terraform apply`.

Além disso, a API do GCP pode levar alguns segundos para propagar a mudança completamente.

## 🎯 Recomendação

**Use a Opção 1** (aguardar e tentar novamente) - é a mais simples e geralmente resolve o problema.

Se não funcionar após 2-3 minutos, use a **Opção 3** (reimportar o estado).


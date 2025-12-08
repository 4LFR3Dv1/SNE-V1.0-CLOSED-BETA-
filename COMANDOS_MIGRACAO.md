# 🚀 Comandos para Migração de Região

## 📍 Localização dos Arquivos Terraform

Os arquivos Terraform estão em:
```
/Users/renan/Desktop/SNE_BACKUP_CLEAN/infra/terraform/
```

## ✅ Comandos Corretos

### 1. Navegar para o diretório Terraform

```bash
# Opção 1: Caminho completo
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/infra/terraform

# Opção 2: Se já estiver na raiz do projeto
cd infra/terraform

# Opção 3: Verificar onde você está
pwd
# Se não estiver em /Users/renan/Desktop/SNE_BACKUP_CLEAN, navegue primeiro:
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
cd infra/terraform
```

### 2. Verificar Deletion Protection

```bash
gcloud sql instances describe sne-db-prod \
    --project=sne-v1 \
    --format="value(settings.deletionProtectionEnabled)"
```

### 3. Desabilitar Deletion Protection (se necessário)

```bash
gcloud sql instances patch sne-db-prod \
    --project=sne-v1 \
    --no-deletion-protection
```

### 4. Fazer Backup do Banco

```bash
gcloud sql backups create \
    --instance=sne-db-prod \
    --project=sne-v1 \
    --description="Backup antes de migração para europe-west1"
```

### 5. Aplicar Migração

```bash
# Navegar para o diretório Terraform
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN/infra/terraform

# Aguardar propagação (recomendado)
sleep 60

# Aplicar
terraform apply -var="project_id=sne-v1" -var="region=europe-west1" -auto-approve
```

### 6. Ou usar o script de migração

```bash
# Da raiz do projeto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Executar script
./migrar_regiao.sh sne-v1 us-central1 europe-west1
```

## 🔍 Verificar Estrutura

```bash
# Verificar se o diretório existe
ls -la /Users/renan/Desktop/SNE_BACKUP_CLEAN/infra/terraform/

# Ver arquivos Terraform
ls /Users/renan/Desktop/SNE_BACKUP_CLEAN/infra/terraform/*.tf
```

## ⚠️ Problema Comum

Se você receber `cd: no such file or directory`, significa que você não está no diretório correto.

**Solução:**
```bash
# Sempre comece da raiz do projeto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
cd infra/terraform
```

---

**💡 Dica**: Use `pwd` para verificar onde você está antes de navegar!


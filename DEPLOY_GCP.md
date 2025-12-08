# ☁️ DEPLOY NA GOOGLE CLOUD - GUIA COMPLETO

Guia passo a passo para fazer deploy do SNE 1.0 Cloud na Google Cloud Platform.

---

## 📋 PRÉ-REQUISITOS

Antes de começar, você precisa:

- [ ] Conta Google Cloud (com $300 de crédito gratuito)
- [ ] Billing habilitado na conta
- [ ] gcloud CLI instalado
- [ ] Terraform 1.0+ instalado
- [ ] Docker instalado (para build de imagens)

---

## 🚀 PASSO A PASSO COMPLETO

### PASSO 1: Instalar e Configurar gcloud CLI

```bash
# Verificar se já está instalado
gcloud --version

# Se não estiver, instalar (Mac):
# brew install google-cloud-sdk

# OU baixar de: https://cloud.google.com/sdk/docs/install
```

### PASSO 2: Autenticar no Google Cloud

```bash
# Login interativo
gcloud auth login

# Configurar credenciais para aplicações
gcloud auth application-default login

# Verificar autenticação
gcloud auth list
```

### PASSO 3: Criar ou Selecionar Projeto GCP

```bash
# Opção A: Criar novo projeto
export PROJECT_ID="sne-cloud-$(date +%s)"
gcloud projects create $PROJECT_ID --name="SNE Cloud"

# Opção B: Usar projeto existente
export PROJECT_ID="seu-projeto-existente"

# Definir projeto atual
gcloud config set project $PROJECT_ID

# Verificar
gcloud config get-value project
```

### PASSO 4: Habilitar Billing

```bash
# Listar billing accounts disponíveis
gcloud billing accounts list

# Linkar projeto ao billing account (SUBSTITUIR com seu ID)
gcloud billing projects link $PROJECT_ID \
  --billing-account=0X0X0X-0X0X0X-0X0X0X

# Verificar
gcloud billing projects describe $PROJECT_ID
```

### PASSO 5: Habilitar APIs Necessárias

```bash
# Habilitar todas as APIs necessárias
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage-api.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  vpcaccess.googleapis.com \
  servicenetworking.googleapis.com \
  compute.googleapis.com

# Verificar APIs habilitadas
gcloud services list --enabled | grep -E "(run|sql|secret|scheduler|artifact|build|vpc)"
```

### PASSO 6: Configurar Terraform Backend (Opcional mas Recomendado)

```bash
# Criar bucket para estado do Terraform
gsutil mb -p $PROJECT_ID -l us-central1 gs://sne-terraform-state-${PROJECT_ID}

# Habilitar versionamento
gsutil versioning set on gs://sne-terraform-state-${PROJECT_ID}

# Editar infra/terraform/main.tf e descomentar backend:
# backend "gcs" {
#   bucket = "sne-terraform-state-${PROJECT_ID}"
#   prefix = "terraform/state"
# }
```

### PASSO 7: Configurar Variáveis Terraform

```bash
cd infra/terraform

# Criar arquivo terraform.tfvars
cat > terraform.tfvars <<EOF
project_id = "$PROJECT_ID"
region     = "us-central1"
zone       = "us-central1-a"
environment = "prod"
public_web = false
enable_redis = false
min_instances = 0
max_instances = 10
EOF
```

### PASSO 8: Aplicar Infraestrutura com Terraform

```bash
# Inicializar Terraform
terraform init

# Verificar o que será criado (revisar cuidadosamente)
terraform plan

# Aplicar (vai criar todos os recursos - leva ~10-15 minutos)
terraform apply

# Digite "yes" quando solicitado
```

**⏱️ Tempo estimado:** 10-15 minutos

**O que será criado:**
- ✅ Cloud SQL (PostgreSQL)
- ✅ VPC Connector
- ✅ Artifact Registry
- ✅ Cloud Storage bucket
- ✅ Secret Manager secrets
- ✅ Service Accounts
- ✅ Cloud Run services (4)
- ✅ Cloud Scheduler job

### PASSO 9: Configurar Secrets

```bash
# Gerar senha segura para o banco
DB_PASSWORD=$(openssl rand -base64 32)
echo "Senha gerada: $DB_PASSWORD"  # Salve esta senha!

# Criar secret da senha do banco
echo -n "$DB_PASSWORD" | gcloud secrets create sne-db-password --data-file=-

# Criar secret do Telegram Bot Token
echo -n "SEU_TELEGRAM_BOT_TOKEN_AQUI" | gcloud secrets create sne-telegram-bot-token --data-file=-

# Criar secret do Telegram Chat ID
echo -n "SEU_CHAT_ID_AQUI" | gcloud secrets create sne-telegram-chat-id --data-file=-

# Criar secret key para Flask
echo -n "$(openssl rand -base64 32)" | gcloud secrets create sne-secret-key --data-file=-

# Verificar secrets criados
gcloud secrets list
```

### PASSO 10: Atualizar Senha do Banco no Cloud SQL

```bash
# Obter senha do secret
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password)

# Obter nome da instância
INSTANCE_NAME=$(terraform output -raw cloud_sql_instance_connection_name | cut -d: -f3)

# Atualizar senha do usuário
gcloud sql users set-password sne_admin \
  --instance=$INSTANCE_NAME \
  --password="$DB_PASSWORD"
```

### PASSO 11: Inicializar Banco de Dados

```bash
# Instalar Cloud SQL Proxy (se não tiver)
# Mac:
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
chmod +x cloud-sql-proxy

# Obter connection name
CONNECTION_NAME=$(terraform output -raw cloud_sql_instance_connection_name)
echo "Connection: $CONNECTION_NAME"

# Executar migrações
cd ../..
./deploy/init_db.sh $PROJECT_ID us-central1 $CONNECTION_NAME
```

### PASSO 12: Build e Push de Imagens Docker

```bash
# Autenticar Docker no Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Configurar variáveis
export REGION=us-central1
export REPO=us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts

# Build e push de cada serviço
echo "📦 Building sne-web..."
docker build -t $REPO/sne-web:latest ./services/sne-web
docker push $REPO/sne-web:latest

echo "📦 Building sne-worker..."
docker build -t $REPO/sne-worker:latest ./services/sne-worker
docker push $REPO/sne-worker:latest

echo "📦 Building sne-auto..."
docker build -t $REPO/sne-auto:latest ./services/sne-auto
docker push $REPO/sne-auto:latest

echo "📦 Building sne-telegram..."
docker build -t $REPO/sne-telegram:latest ./services/sne-telegram
docker push $REPO/sne-telegram:latest

# Verificar imagens
gcloud artifacts docker images list --repository=sne-artifacts --location=us-central1
```

### PASSO 13: Deploy dos Serviços Cloud Run

```bash
# Deploy todos os serviços de uma vez
./deploy/deploy_all.sh $PROJECT_ID us-central1

# OU deploy individual:
# ./deploy/deploy_web.sh $PROJECT_ID us-central1
# ./deploy/deploy_worker.sh $PROJECT_ID us-central1
# ./deploy/deploy_auto.sh $PROJECT_ID us-central1
# ./deploy/deploy_telegram.sh $PROJECT_ID us-central1
```

### PASSO 14: Verificar Deploy

```bash
# Listar todos os serviços
gcloud run services list --region=us-central1

# Obter URL do sne-web
WEB_URL=$(gcloud run services describe sne-web --region=us-central1 --format="value(status.url)")
echo "URL do sne-web: $WEB_URL"

# Testar health check
curl $WEB_URL/health

# Testar API
curl -X POST $WEB_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","timeframe":"15m"}'
```

### PASSO 15: Configurar Cloud Scheduler (Opcional)

```bash
# Verificar se job foi criado
gcloud scheduler jobs list --location=us-central1

# Testar job manualmente
gcloud scheduler jobs run sne-auto-scan --location=us-central1

# Ver logs da execução
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sne-auto" --limit=10
```

### PASSO 16: Configurar Budget Alert

```bash
# Obter billing account ID
BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(name)" --limit=1)

# Criar budget de $50/mês
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="SNE Cloud Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=90,basis=CURRENT_SPEND \
  --threshold-rule=percent=100,basis=CURRENT_SPEND

# Verificar
gcloud billing budgets list --billing-account=$BILLING_ACCOUNT
```

---

## ✅ VERIFICAÇÃO FINAL

Execute estes comandos para verificar se tudo está funcionando:

```bash
# 1. Verificar serviços Cloud Run
gcloud run services list --region=us-central1

# 2. Verificar Cloud SQL
gcloud sql instances list

# 3. Verificar secrets
gcloud secrets list

# 4. Verificar Artifact Registry
gcloud artifacts repositories list

# 5. Testar endpoints
WEB_URL=$(gcloud run services describe sne-web --region=us-central1 --format="value(status.url)")
curl $WEB_URL/health

# 6. Ver logs
gcloud logging read "resource.type=cloud_run_revision" --limit=10
```

---

## 🎯 COMANDOS RÁPIDOS DE REFERÊNCIA

### Ver Logs

```bash
# Logs de um serviço específico
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sne-web" --limit=50

# Logs em tempo real
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=sne-web"
```

### Atualizar um Serviço

```bash
# Rebuild e redeploy
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-web:latest ./services/sne-web
docker push us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-web:latest
./deploy/deploy_web.sh $PROJECT_ID us-central1
```

### Ver Custos

```bash
# Ver custos do projeto
gcloud billing projects describe $PROJECT_ID

# Ver uso de recursos
gcloud compute instances list
gcloud run services list --region=us-central1
```

---

## 🆘 TROUBLESHOOTING

### Erro: "API not enabled"

```bash
# Habilitar API específica
gcloud services enable NOME_DA_API
```

### Erro: "Permission denied"

```bash
# Verificar permissões
gcloud projects get-iam-policy $PROJECT_ID

# Adicionar permissões necessárias
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:seu-email@gmail.com" \
  --role="roles/owner"
```

### Erro: "Cloud SQL connection failed"

```bash
# Verificar VPC Connector
gcloud compute networks vpc-access connectors describe sne-vpc-connector --region=us-central1

# Verificar Cloud SQL
gcloud sql instances describe sne-db-prod
```

### Erro: "Image not found"

```bash
# Verificar se imagem foi pushada
gcloud artifacts docker images list --repository=sne-artifacts --location=us-central1

# Rebuild e push
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-web:latest ./services/sne-web
docker push us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-web:latest
```

---

## 💰 ESTIMATIVA DE CUSTOS

### Uso Leve (min_instances=0)
- **Cloud Run**: ~$5-20/mês (pay-per-use)
- **Cloud SQL (db-f1-micro)**: ~$7-10/mês
- **VPC Connector**: ~$5/mês
- **Cloud Storage**: ~$0.10/mês
- **Total**: ~$20-40/mês

### Para Reduzir Custos

```bash
# Ajustar min_instances para 0 (já está configurado)
# Reduzir max_instances se necessário
# Usar Cloud SQL menor (db-f1-micro já é o menor)
```

---

## 🗑️ LIMPEZA (Se Precisar Remover Tudo)

```bash
# ⚠️ CUIDADO: Isso remove TODOS os recursos!

# Destruir infraestrutura Terraform
cd infra/terraform
terraform destroy

# Deletar imagens Docker
gcloud artifacts docker images delete us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-web:latest --quiet
gcloud artifacts docker images delete us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-worker:latest --quiet
gcloud artifacts docker images delete us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-auto:latest --quiet
gcloud artifacts docker images delete us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-telegram:latest --quiet

# Deletar projeto (CUIDADO - irreversível!)
# gcloud projects delete $PROJECT_ID
```

---

## 📚 PRÓXIMOS PASSOS APÓS DEPLOY

1. ✅ **Integrar código do SNE RADAR** nos serviços
2. ✅ **Configurar domínio customizado** (opcional)
3. ✅ **Adicionar monitoramento avançado**
4. ✅ **Configurar CI/CD** com Cloud Build
5. ✅ **Otimizar custos** conforme uso

---

**🚀 Pronto para fazer deploy! Siga os passos acima na ordem.**

**💡 Dica:** Execute um passo por vez e verifique se funcionou antes de continuar.




# ✅ CHECKLIST DE DEPLOY - SNE 1.0 CLOUD

Checklist completo de 15 passos para deploy do zero ao ar.

## 📋 Pré-requisitos

- [ ] Conta Google Cloud com billing habilitado
- [ ] gcloud CLI instalado e configurado
- [ ] Terraform 1.0+ instalado
- [ ] Docker instalado
- [ ] Acesso ao GitHub (para CI/CD)

---

## 🚀 Passo a Passo

### 1. Criar e Configurar Projeto GCP

```bash
# Autenticar
gcloud auth login
gcloud auth application-default login

# Criar projeto
export PROJECT_ID="sne-cloud-$(date +%s)"
gcloud projects create $PROJECT_ID --name="SNE Cloud"

# Definir projeto
gcloud config set project $PROJECT_ID

# Habilitar billing (SUBSTITUIR com seu billing account ID)
gcloud billing projects link $PROJECT_ID --billing-account=0X0X0X-0X0X0X-0X0X0X
```

**✅ Verificação:** `gcloud config get-value project` deve retornar seu projeto.

---

### 2. Habilitar APIs Necessárias

```bash
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
```

**✅ Verificação:** `gcloud services list --enabled` deve listar todas as APIs.

---

### 3. Configurar Terraform Backend (Opcional mas Recomendado)

```bash
# Criar bucket para estado
gsutil mb -p $PROJECT_ID -l us-central1 gs://sne-terraform-state-${PROJECT_ID}
gsutil versioning set on gs://sne-terraform-state-${PROJECT_ID}

# Editar infra/terraform/main.tf e descomentar backend
# backend "gcs" {
#   bucket = "sne-terraform-state-${PROJECT_ID}"
#   prefix = "terraform/state"
# }
```

**✅ Verificação:** `gsutil ls gs://sne-terraform-state-${PROJECT_ID}` deve funcionar.

---

### 4. Configurar Variáveis Terraform

```bash
cd infra/terraform

# Criar terraform.tfvars
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

**✅ Verificação:** Arquivo `terraform.tfvars` criado.

---

### 5. Aplicar Infraestrutura Terraform

```bash
# Inicializar
terraform init

# Planejar (revisar mudanças)
terraform plan

# Aplicar (criar recursos)
terraform apply
```

**✅ Verificação:** `terraform output` deve mostrar URLs dos serviços.

**⏱️ Tempo estimado:** 10-15 minutos

---

### 6. Configurar Secrets no Secret Manager

```bash
# Gerar senha do banco
DB_PASSWORD=$(openssl rand -base64 32)
echo -n "$DB_PASSWORD" | gcloud secrets create sne-db-password --data-file=-

# Telegram (substituir com valores reais)
echo -n "SEU_TELEGRAM_BOT_TOKEN" | gcloud secrets create sne-telegram-bot-token --data-file=-
echo -n "SEU_CHAT_ID" | gcloud secrets create sne-telegram-chat-id --data-file=-

# Secret key
echo -n "$(openssl rand -base64 32)" | gcloud secrets create sne-secret-key --data-file=-

# Binance (opcional)
# echo -n "SUA_API_KEY" | gcloud secrets create sne-binance-api-key --data-file=-
# echo -n "SEU_SECRET_KEY" | gcloud secrets create sne-binance-secret-key --data-file=-
```

**✅ Verificação:** `gcloud secrets list` deve listar todos os secrets.

---

### 7. Atualizar Senha do Banco no Cloud SQL

```bash
# Obter senha do secret
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password)

# Atualizar usuário
gcloud sql users set-password sne_admin \
  --instance=sne-db-prod \
  --password="$DB_PASSWORD"
```

**✅ Verificação:** Senha atualizada no Cloud SQL.

---

### 8. Configurar Cloud SQL Proxy Localmente

```bash
# Instalar Cloud SQL Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
chmod +x cloud-sql-proxy

# Obter connection name
CONNECTION_NAME=$(terraform -chdir=infra/terraform output -raw cloud_sql_instance_connection_name)
echo "Connection: $CONNECTION_NAME"
```

**✅ Verificação:** Cloud SQL Proxy instalado.

---

### 9. Inicializar Banco de Dados

```bash
# Executar migrações
./deploy/init_db.sh $PROJECT_ID us-central1 $CONNECTION_NAME
```

**✅ Verificação:** Tabelas `users`, `signals`, `trades` criadas.

---

### 10. Build e Push de Imagens Docker

```bash
# Autenticar Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build e push
export REGION=us-central1
export REPO=us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts

# sne-web
docker build -t $REPO/sne-web:latest ./services/sne-web
docker push $REPO/sne-web:latest

# sne-worker
docker build -t $REPO/sne-worker:latest ./services/sne-worker
docker push $REPO/sne-worker:latest

# sne-auto
docker build -t $REPO/sne-auto:latest ./services/sne-auto
docker push $REPO/sne-auto:latest

# sne-telegram
docker build -t $REPO/sne-telegram:latest ./services/sne-telegram
docker push $REPO/sne-telegram:latest
```

**✅ Verificação:** `gcloud artifacts docker images list --repository=sne-artifacts` mostra as imagens.

---

### 11. Deploy dos Serviços Cloud Run

```bash
# Deploy todos
./deploy/deploy_all.sh $PROJECT_ID us-central1

# Ou individual
./deploy/deploy_web.sh $PROJECT_ID us-central1
./deploy/deploy_worker.sh $PROJECT_ID us-central1
./deploy/deploy_auto.sh $PROJECT_ID us-central1
./deploy/deploy_telegram.sh $PROJECT_ID us-central1
```

**✅ Verificação:** 
- `gcloud run services list` mostra todos os serviços
- URLs dos serviços respondem `/health` com 200 OK

---

### 12. Configurar Cloud Scheduler

```bash
# Verificar job criado
gcloud scheduler jobs list

# Testar manualmente
gcloud scheduler jobs run sne-auto-scan --location=us-central1
```

**✅ Verificação:** Job executado com sucesso.

---

### 13. Configurar Cloud Build Trigger (Opcional)

```bash
# Se usar GitHub, configurar trigger
# Editar infra/terraform/cloudbuild_trigger.tf com:
# - github_owner = "seu-usuario"
# - github_repo = "seu-repo"

# Aplicar
terraform -chdir=infra/terraform apply

# Ou criar manualmente
gcloud builds triggers create github \
  --name=sne-github-trigger \
  --repo-name=seu-repo \
  --repo-owner=seu-usuario \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

**✅ Verificação:** Trigger criado e funcionando.

---

### 14. Configurar Budget Alert

```bash
# Obter billing account ID
BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(name)" --limit=1)

# Criar budget
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="SNE Cloud Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=90,basis=CURRENT_SPEND \
  --threshold-rule=percent=100,basis=CURRENT_SPEND
```

**✅ Verificação:** Budget criado no console.

---

### 15. Testar Sistema Completo

```bash
# Obter URL do sne-web
WEB_URL=$(gcloud run services describe sne-web --region=us-central1 --format="value(status.url)")

# Testar health
curl $WEB_URL/health

# Testar API
curl -X POST $WEB_URL/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","timeframe":"15m"}'

# Verificar logs
gcloud logging read "resource.type=cloud_run_revision" --limit=10
```

**✅ Verificação:** 
- Todos os endpoints respondem
- Logs aparecem no Cloud Logging
- Cloud Scheduler executa jobs

---

## 🎉 Deploy Completo!

Se todos os passos foram concluídos com sucesso, o SNE 1.0 Cloud está no ar!

### Próximos Passos

1. **Integrar código do SNE RADAR** nos serviços
2. **Configurar domínio customizado** (opcional)
3. **Adicionar monitoramento** e alertas
4. **Otimizar custos** conforme uso
5. **Documentar** processos específicos

---

## 🔍 Verificações Finais

- [ ] Todos os serviços Cloud Run estão rodando
- [ ] Cloud SQL está acessível via VPC Connector
- [ ] Secrets estão configurados corretamente
- [ ] Cloud Scheduler está executando jobs
- [ ] Logs estão sendo gerados
- [ ] Budget alert está configurado
- [ ] Imagens Docker estão no Artifact Registry
- [ ] Migrações do banco foram aplicadas

---

## 🆘 Troubleshooting Rápido

### Serviço não inicia
```bash
gcloud run services describe sne-web --region=us-central1
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sne-web" --limit=50
```

### Erro de conexão com banco
```bash
# Verificar VPC Connector
gcloud compute networks vpc-access connectors describe sne-vpc-connector --region=us-central1

# Testar conexão
cloud-sql-proxy $CONNECTION_NAME
```

### Erro de permissões
```bash
# Verificar service account
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:serviceAccount:sa-sne-web@$PROJECT_ID.iam.gserviceaccount.com"
```

---

**✅ Checklist completo! Sistema pronto para produção!**




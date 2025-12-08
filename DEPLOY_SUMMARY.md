# 🚀 RESUMO DE DEPLOY - SNE 1.0 CLOUD

## 📦 Arquivos Gerados

### Microserviços (4 serviços)
- ✅ `services/sne-web/` - API Flask com WebSocket
- ✅ `services/sne-worker/` - Processador de jobs CPU-intensivos
- ✅ `services/sne-auto/` - Automação acionada por Cloud Scheduler
- ✅ `services/sne-telegram/` - Webhook handler Telegram

### Infraestrutura Terraform
- ✅ `infra/terraform/main.tf` - Providers e APIs
- ✅ `infra/terraform/variables.tf` - Variáveis
- ✅ `infra/terraform/outputs.tf` - Outputs
- ✅ `infra/terraform/cloudrun.tf` - Cloud Run services
- ✅ `infra/terraform/cloudsql.tf` - Cloud SQL PostgreSQL
- ✅ `infra/terraform/vpc.tf` - VPC Connector
- ✅ `infra/terraform/redis.tf` - Memorystore Redis (opcional)
- ✅ `infra/terraform/storage.tf` - Cloud Storage
- ✅ `infra/terraform/secrets.tf` - Secret Manager
- ✅ `infra/terraform/iam.tf` - Service Accounts e IAM
- ✅ `infra/terraform/scheduler.tf` - Cloud Scheduler
- ✅ `infra/terraform/artifactregistry.tf` - Artifact Registry
- ✅ `infra/terraform/cloudbuild_trigger.tf` - Cloud Build triggers

### Scripts de Deploy
- ✅ `deploy/deploy_all.sh` - Deploy todos os serviços
- ✅ `deploy/deploy_web.sh` - Deploy sne-web
- ✅ `deploy/deploy_worker.sh` - Deploy sne-worker
- ✅ `deploy/deploy_auto.sh` - Deploy sne-auto
- ✅ `deploy/deploy_telegram.sh` - Deploy sne-telegram
- ✅ `deploy/init_db.sh` - Inicializar banco de dados

### CI/CD
- ✅ `cloudbuild.yaml` - Pipeline completo Cloud Build
- ✅ `docker-compose.dev.yml` - Ambiente de desenvolvimento local

### Migrações
- ✅ `alembic.ini` - Configuração Alembic
- ✅ `alembic/env.py` - Ambiente Alembic
- ✅ `alembic/script.py.mako` - Template de migração
- ✅ `alembic/versions/0001_initial.py` - Migração inicial

### Documentação
- ✅ `README.md` - Documentação principal
- ✅ `CHECKLIST.md` - Checklist de 15 passos
- ✅ `DEPLOY_SUMMARY.md` - Este arquivo
- ✅ `services/*/README.md` - Documentação de cada serviço

---

## 🎯 Comandos de Inicialização Rápida

### 1. Configurar Projeto GCP

```bash
# Criar projeto
export PROJECT_ID="sne-cloud-$(date +%s)"
gcloud projects create $PROJECT_ID --name="SNE Cloud"
gcloud config set project $PROJECT_ID

# Habilitar billing (SUBSTITUIR com seu billing account)
gcloud billing projects link $PROJECT_ID --billing-account=SEU-BILLING-ACCOUNT-ID

# Habilitar APIs
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  vpcaccess.googleapis.com \
  servicenetworking.googleapis.com \
  compute.googleapis.com
```

### 2. Configurar Terraform Backend

```bash
# Criar bucket para estado
gsutil mb -p $PROJECT_ID -l us-central1 gs://sne-terraform-state-${PROJECT_ID}
gsutil versioning set on gs://sne-terraform-state-${PROJECT_ID}

# Editar infra/terraform/main.tf e descomentar backend
```

### 3. Aplicar Infraestrutura

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

# Inicializar e aplicar
terraform init
terraform plan
terraform apply
```

### 4. Configurar Secrets

```bash
# Gerar senha do banco
DB_PASSWORD=$(openssl rand -base64 32)
echo -n "$DB_PASSWORD" | gcloud secrets create sne-db-password --data-file=-

# Telegram
echo -n "SEU_TELEGRAM_BOT_TOKEN" | gcloud secrets create sne-telegram-bot-token --data-file=-
echo -n "SEU_CHAT_ID" | gcloud secrets create sne-telegram-chat-id --data-file=-

# Secret key
echo -n "$(openssl rand -base64 32)" | gcloud secrets create sne-secret-key --data-file=-

# Atualizar senha no Cloud SQL
gcloud sql users set-password sne_admin \
  --instance=sne-db-prod \
  --password="$DB_PASSWORD"
```

### 5. Inicializar Banco de Dados

```bash
# Obter connection name
CONNECTION_NAME=$(terraform -chdir=infra/terraform output -raw cloud_sql_instance_connection_name)

# Executar migrações
./deploy/init_db.sh $PROJECT_ID us-central1 $CONNECTION_NAME
```

### 6. Build e Push de Imagens

```bash
# Autenticar Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build e push
export REGION=us-central1
export REPO=us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts

for service in sne-web sne-worker sne-auto sne-telegram; do
  docker build -t $REPO/$service:latest ./services/$service
  docker push $REPO/$service:latest
done
```

### 7. Deploy dos Serviços

```bash
# Deploy todos
./deploy/deploy_all.sh $PROJECT_ID us-central1
```

### 8. Verificar Deploy

```bash
# Listar serviços
gcloud run services list

# Testar health
WEB_URL=$(gcloud run services describe sne-web --region=us-central1 --format="value(status.url)")
curl $WEB_URL/health
```

---

## 📊 Estrutura de Custos Estimada

### Uso Leve (min_instances=0)
- **Cloud Run**: ~$5-20/mês (pay-per-use)
- **Cloud SQL (db-f1-micro)**: ~$7-10/mês
- **Cloud Storage**: ~$0.10/mês
- **Secret Manager**: Gratuito
- **Cloud Scheduler**: Gratuito (até 3 jobs)
- **VPC Connector**: ~$5/mês
- **Total**: ~$20-40/mês

### Configurar Budget Alert

```bash
BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(name)" --limit=1)
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="SNE Cloud Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=90,basis=CURRENT_SPEND
```

---

## 🔐 Segurança

### Implementado
- ✅ Secrets no Secret Manager
- ✅ Service Accounts com permissões mínimas
- ✅ Cloud SQL com IP privado
- ✅ VPC Connector para acesso privado
- ✅ HTTPS obrigatório (Cloud Run)

### Rotação de Secrets

```bash
# Atualizar senha do banco
NEW_PASSWORD=$(openssl rand -base64 32)
echo -n "$NEW_PASSWORD" | gcloud secrets versions add sne-db-password --data-file=-
gcloud sql users set-password sne_admin --instance=sne-db-prod --password="$NEW_PASSWORD"
```

---

## 📈 Monitoramento

### Ver Logs

```bash
# Logs de um serviço
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sne-web" --limit=50

# Logs em tempo real
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=sne-web"
```

### Métricas

Acesse Cloud Monitoring para:
- Taxa de requisições
- Latência
- Taxa de erros
- Uso de CPU/Memória

---

## 🗑️ Limpeza de Recursos

```bash
# Destruir infraestrutura Terraform
cd infra/terraform
terraform destroy

# Deletar imagens
gcloud artifacts docker images delete us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts/sne-web:latest
# (repita para outros serviços)

# Deletar projeto (cuidado!)
gcloud projects delete $PROJECT_ID
```

---

## ✅ Checklist Rápido

- [ ] Projeto GCP criado e billing habilitado
- [ ] APIs habilitadas
- [ ] Terraform backend configurado
- [ ] Infraestrutura aplicada (terraform apply)
- [ ] Secrets configurados
- [ ] Banco de dados inicializado
- [ ] Imagens Docker buildadas e pushadas
- [ ] Serviços deployados
- [ ] Cloud Scheduler configurado
- [ ] Budget alert configurado
- [ ] Testes de endpoints funcionando
- [ ] Logs sendo gerados

---

## 🆘 Troubleshooting

### Erro de conexão com Cloud SQL
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

### Serviço não inicia
```bash
# Ver logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sne-web" --limit=50

# Ver detalhes do serviço
gcloud run services describe sne-web --region=us-central1
```

---

## 📚 Próximos Passos

1. **Integrar código do SNE RADAR** nos serviços
   - Migrar `motor_renan.py` para `sne-web`
   - Migrar `backtest.py` para `sne-worker`
   - Migrar `auto_analise.py` para `sne-auto`
   - Migrar `xenos_bot.py` para `sne-telegram`

2. **Configurar domínio customizado** (opcional)
   ```bash
   gcloud run domain-mappings create --service=sne-web --domain=api.sne.com
   ```

3. **Adicionar monitoramento avançado**
   - Dashboards no Cloud Monitoring
   - Alertas customizados
   - Métricas de negócio

4. **Otimizar custos**
   - Ajustar min_instances conforme uso
   - Usar Cloud SQL read replicas se necessário
   - Implementar cache (Redis)

5. **CI/CD completo**
   - Configurar GitHub Actions
   - Adicionar testes automatizados
   - Deploy automático em staging/prod

---

**🎉 SNE 1.0 Cloud está pronto para deploy!**

Siga o [CHECKLIST.md](CHECKLIST.md) para o passo-a-passo detalhado.




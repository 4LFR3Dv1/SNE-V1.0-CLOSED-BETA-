# 🚀 INÍCIO RÁPIDO - DEPLOY NO GOOGLE CLOUD

Guia rápido e direto para fazer deploy do SNE 1.0 Cloud.

---

## ⚡ RESUMO: 3 ETAPAS PRINCIPAIS

### 1️⃣ **INSTALAR FERRAMENTAS** (5 minutos)
### 2️⃣ **CONFIGURAR GCP** (10 minutos)
### 3️⃣ **FAZER DEPLOY** (20 minutos)

---

## 📦 ETAPA 1: INSTALAR FERRAMENTAS

### Opção A: Script Automático (Recomendado)

```bash
# Executar script de instalação
./instalar_ferramentas.sh
```

### Opção B: Manual

```bash
# Instalar gcloud
brew install --cask google-cloud-sdk

# Instalar Terraform
brew install terraform

# Verificar
gcloud --version
terraform --version
```

**✅ Quando terminar, continue para Etapa 2**

---

## ☁️ ETAPA 2: CONFIGURAR GOOGLE CLOUD

### Passo 1: Autenticar

```bash
# Login
gcloud auth login
gcloud auth application-default login
```

### Passo 2: Criar Projeto

```bash
# Criar projeto
export PROJECT_ID="sne-cloud-$(date +%s)"
gcloud projects create $PROJECT_ID --name="SNE Cloud"
gcloud config set project $PROJECT_ID

# Habilitar billing (SUBSTITUIR com seu billing account ID)
gcloud billing projects link $PROJECT_ID --billing-account=SEU-BILLING-ACCOUNT-ID
```

**💡 Como obter billing account ID:**
```bash
gcloud billing accounts list
```

### Passo 3: Habilitar APIs

```bash
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

**✅ Quando terminar, continue para Etapa 3**

---

## 🚀 ETAPA 3: FAZER DEPLOY

### Passo 1: Configurar Terraform

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

### Passo 2: Aplicar Infraestrutura

```bash
# Inicializar
terraform init

# Aplicar (vai criar tudo - leva ~10-15 minutos)
terraform apply
# Digite "yes" quando solicitado
```

### Passo 3: Configurar Secrets

```bash
# Gerar senha do banco
DB_PASSWORD=$(openssl rand -base64 32)

# Criar secrets
echo -n "$DB_PASSWORD" | gcloud secrets create sne-db-password --data-file=-
echo -n "SEU_TELEGRAM_TOKEN" | gcloud secrets create sne-telegram-bot-token --data-file=-
echo -n "SEU_CHAT_ID" | gcloud secrets create sne-telegram-chat-id --data-file=-
echo -n "$(openssl rand -base64 32)" | gcloud secrets create sne-secret-key --data-file=-
```

### Passo 4: Atualizar Senha do Banco

```bash
# Obter nome da instância
INSTANCE_NAME=$(terraform output -raw cloud_sql_instance_connection_name | cut -d: -f3)

# Atualizar senha
gcloud sql users set-password sne_admin \
  --instance=$INSTANCE_NAME \
  --password="$DB_PASSWORD"
```

### Passo 5: Build e Push de Imagens

```bash
# Voltar para raiz
cd ../..

# Autenticar Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build e push
export REGION=us-central1
export REPO=us-central1-docker.pkg.dev/$PROJECT_ID/sne-artifacts

for service in sne-web sne-worker sne-auto sne-telegram; do
  echo "📦 Building $service..."
  docker build -t $REPO/$service:latest ./services/$service
  docker push $REPO/$service:latest
done
```

### Passo 6: Deploy dos Serviços

```bash
# Deploy todos
./deploy/deploy_all.sh $PROJECT_ID us-central1
```

### Passo 7: Verificar

```bash
# Obter URL
WEB_URL=$(gcloud run services describe sne-web --region=us-central1 --format="value(status.url)")
echo "URL: $WEB_URL"

# Testar
curl $WEB_URL/health
```

---

## ✅ CHECKLIST RÁPIDO

- [ ] Ferramentas instaladas (gcloud, terraform)
- [ ] Autenticado no GCP
- [ ] Projeto criado e billing habilitado
- [ ] APIs habilitadas
- [ ] Terraform aplicado
- [ ] Secrets configurados
- [ ] Imagens Docker buildadas e pushadas
- [ ] Serviços deployados
- [ ] Health checks funcionando

---

## 🆘 PRECISA DE AJUDA?

### Guias Detalhados Disponíveis:

- **`INSTALAR_FERRAMENTAS.md`** - Instalação detalhada
- **`DEPLOY_GCP.md`** - Guia completo de deploy (16 passos)
- **`CHECKLIST.md`** - Checklist completo de 15 passos

### Comandos Úteis:

```bash
# Ver status dos serviços
gcloud run services list --region=us-central1

# Ver logs
gcloud logging read "resource.type=cloud_run_revision" --limit=10

# Ver custos
gcloud billing projects describe $PROJECT_ID
```

---

## 💰 CUSTOS ESTIMADOS

- **Uso leve**: ~$20-40/mês
- **Configurado com min_instances=0** para economizar

---

**🚀 Pronto para começar? Execute a Etapa 1 primeiro!**

```bash
./instalar_ferramentas.sh
```




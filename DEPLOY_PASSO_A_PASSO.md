# 🚀 DEPLOY PASSO A PASSO - SNE 1.0 CLOUD

Status atual: ✅ Configurado e pronto para deploy!

---

## ✅ O QUE JÁ ESTÁ PRONTO

- ✅ gcloud instalado e funcionando
- ✅ Projeto `sne-v1` configurado
- ✅ Billing linkado
- ✅ APIs habilitadas
- ✅ Terraform configurado

---

## 📋 PRÓXIMOS PASSOS

### PASSO 1: Verificar Terraform

```bash
# Verificar se está instalado
terraform --version

# Se não estiver, instalar:
brew install terraform
```

### PASSO 2: Configurar Terraform Backend (Opcional)

```bash
# Criar bucket para estado (opcional mas recomendado)
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gsutil mb -p sne-v1 -l us-central1 gs://sne-terraform-state-sne-v1 2>/dev/null || echo "Bucket já existe"
gsutil versioning set on gs://sne-terraform-state-sne-v1

# Editar infra/terraform/main.tf e descomentar backend:
# backend "gcs" {
#   bucket = "sne-terraform-state-sne-v1"
#   prefix = "terraform/state"
# }
```

### PASSO 3: Aplicar Infraestrutura Terraform

```bash
cd infra/terraform

# Inicializar
terraform init

# Ver o que será criado
terraform plan

# Aplicar (vai criar todos os recursos - leva ~10-15 minutos)
terraform apply
# Digite "yes" quando solicitado
```

**⏱️ Tempo estimado:** 10-15 minutos

### PASSO 4: Configurar Secrets

```bash
# Voltar para raiz
cd ../..

# Gerar senha do banco
DB_PASSWORD=$(openssl rand -base64 32)
echo "Senha gerada (salve esta!): $DB_PASSWORD"

# Criar secrets
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
echo -n "$DB_PASSWORD" | gcloud secrets create sne-db-password --data-file=-
echo -n "SEU_TELEGRAM_BOT_TOKEN" | gcloud secrets create sne-telegram-bot-token --data-file=-
echo -n "SEU_CHAT_ID" | gcloud secrets create sne-telegram-chat-id --data-file=-
echo -n "$(openssl rand -base64 32)" | gcloud secrets create sne-secret-key --data-file=-
```

### PASSO 5: Atualizar Senha do Banco

```bash
# Obter connection name do Terraform
cd infra/terraform
CONNECTION_NAME=$(terraform output -raw cloud_sql_instance_connection_name)
INSTANCE_NAME=$(echo $CONNECTION_NAME | cut -d: -f3)

# Obter senha
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password)

# Atualizar
gcloud sql users set-password sne_admin \
  --instance=$INSTANCE_NAME \
  --password="$DB_PASSWORD"
```

### PASSO 6: Build e Push de Imagens

```bash
# Voltar para raiz
cd ../..

# Autenticar Docker
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build e push
export REGION=us-central1
export REPO=us-central1-docker.pkg.dev/sne-v1/sne-artifacts

for service in sne-web sne-worker sne-auto sne-telegram; do
  echo "📦 Building $service..."
  docker build -t $REPO/$service:latest ./services/$service
  docker push $REPO/$service:latest
done
```

### PASSO 7: Deploy dos Serviços

```bash
# Deploy todos
./deploy/deploy_all.sh sne-v1 us-central1
```

### PASSO 8: Verificar

```bash
# Listar serviços
gcloud run services list --region=us-central1

# Testar
WEB_URL=$(gcloud run services describe sne-web --region=us-central1 --format="value(status.url)")
curl $WEB_URL/health
```

---

## 🎯 COMANDO RÁPIDO PARA COMEÇAR

```bash
# 1. Verificar Terraform
terraform --version || brew install terraform

# 2. Ir para Terraform
cd infra/terraform

# 3. Inicializar e aplicar
terraform init
terraform plan
terraform apply
```

---

## 📊 STATUS ATUAL

- ✅ Projeto: `sne-v1`
- ✅ Billing: Linkado
- ✅ APIs: Habilitadas
- ⏳ Terraform: Pronto para aplicar
- ⏳ Secrets: A configurar
- ⏳ Imagens: A buildar
- ⏳ Deploy: A fazer

---

**🚀 Pronto para continuar! Execute o PASSO 3 acima para criar a infraestrutura.**




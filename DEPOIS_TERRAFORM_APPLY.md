# 🚀 PRÓXIMOS PASSOS APÓS TERRAFORM APPLY

## ✅ O QUE FOI CORRIGIDO

- ✅ VPC Connector: Formato corrigido para `projects/{project}/locations/{location}/connectors/{connector}`
- ✅ Cloud Build Trigger: Tornado opcional (só cria se GitHub configurado)
- ✅ Imagens Docker: Usando placeholder temporário (`gcr.io/cloudrun/hello`)

---

## 📋 APÓS TERRAFORM APPLY

Os serviços Cloud Run serão criados com imagens placeholder. Você precisará:

### 1. Build e Push das Imagens Docker

```bash
# Autenticar Docker
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build e push de cada serviço
export REPO=us-central1-docker.pkg.dev/sne-v1/sne-artifacts

for service in sne-web sne-worker sne-auto sne-telegram; do
  echo "📦 Building $service..."
  docker build -t $REPO/$service:latest ./services/$service
  docker push $REPO/$service:latest
done
```

### 2. Atualizar Serviços Cloud Run com Imagens Corretas

```bash
# Atualizar cada serviço
gcloud run services update sne-web \
  --image us-central1-docker.pkg.dev/sne-v1/sne-artifacts/sne-web:latest \
  --region us-central1

gcloud run services update sne-worker \
  --image us-central1-docker.pkg.dev/sne-v1/sne-artifacts/sne-worker:latest \
  --region us-central1

gcloud run services update sne-auto \
  --image us-central1-docker.pkg.dev/sne-v1/sne-artifacts/sne-auto:latest \
  --region us-central1

gcloud run services update sne-telegram \
  --image us-central1-docker.pkg.dev/sne-v1/sne-artifacts/sne-telegram:latest \
  --region us-central1
```

**OU usar os scripts de deploy:**

```bash
./deploy/deploy_all.sh sne-v1 us-central1
```

---

## 🎯 AGORA: EXECUTAR TERRAFORM APPLY

```bash
cd infra/terraform
terraform apply
```

**Digite `yes` quando solicitado.**

**⏱️ Tempo estimado:** 10-15 minutos

---

## 📝 NOTAS IMPORTANTES

1. **Imagens Placeholder**: Os serviços serão criados com `gcr.io/cloudrun/hello` (imagem de teste do Google)
2. **Atualizar Depois**: Após buildar as imagens, atualize os serviços
3. **Cloud Build Trigger**: Não será criado se `github_owner` e `github_repo` estiverem vazios (isso é normal)

---

**🚀 Execute `terraform apply` agora!**




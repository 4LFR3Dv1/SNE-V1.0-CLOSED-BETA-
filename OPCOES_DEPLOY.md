# 🚀 OPÇÕES DE DEPLOY - SEM DOCKER DESKTOP

Você tem **2 opções** para fazer deploy sem instalar Docker Desktop:

---

## ✅ OPÇÃO 1: Cloud Build (RECOMENDADO - Mais Fácil)

**Não precisa de Docker local!** O Cloud Build faz tudo na nuvem.

```bash
# Deploy completo via Cloud Build
./deploy_cloud_build.sh sne-v1 us-central1
```

Ou manualmente:

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Submeter build (vai buildar na nuvem)
gcloud builds submit \
    --project=sne-v1 \
    --config=cloudbuild.yaml \
    --substitutions=_PROJECT_ID=sne-v1,_REGION=us-central1,_DB_CONNECTION_NAME=sne-v1:us-central1:sne-db-prod,_DB_USER=sne_admin,_DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password),_DB_NAME=sne
```

**Vantagens:**
- ✅ Não precisa instalar nada
- ✅ Build mais rápido (na nuvem)
- ✅ Já faz deploy automático
- ✅ Executa migrações do banco

---

## ✅ OPÇÃO 2: Instalar Docker Desktop

Se quiser buildar localmente:

```bash
# Instalar via Homebrew
brew install --cask docker

# Iniciar
open -a Docker

# Aguardar 30 segundos
sleep 30

# Verificar
docker ps

# Build e deploy
./build_imagens.sh sne-v1 us-central1
./deploy/deploy_all.sh sne-v1 us-central1
```

---

## 🎯 RECOMENDAÇÃO

**Use Cloud Build (Opção 1)** - É mais rápido e não precisa instalar nada!

---

## 📋 PRÓXIMOS PASSOS

1. **Escolha uma opção acima**
2. **Execute o comando**
3. **Aguarde o build terminar**
4. **Teste os serviços**

---

## ⚠️ NOTA SOBRE CLOUDBUILD.YAML

O `cloudbuild.yaml` precisa de algumas correções para funcionar. Vou criar uma versão corrigida.




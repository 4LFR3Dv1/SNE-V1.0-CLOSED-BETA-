# 🔧 RESOLVER PROBLEMAS COM DOCKER

## ⚠️ PROBLEMAS IDENTIFICADOS

1. **Docker daemon não está rodando**
2. **Caminhos dos serviços podem estar incorretos**

---

## ✅ SOLUÇÃO

### 1. Iniciar Docker Desktop

```bash
# Abrir Docker Desktop
open -a Docker

# Aguardar 30 segundos para iniciar
sleep 30

# Verificar se está rodando
docker ps
```

Se retornar uma lista (mesmo que vazia), está funcionando! ✅

### 2. Verificar Diretório

```bash
# Verificar onde você está
pwd

# Deve estar em: /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Se não estiver, navegar para lá
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Verificar se os serviços existem
ls -la services/
```

### 3. Build e Push (Após Docker Iniciar)

```bash
# Garantir que está no diretório correto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Autenticar Docker
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build e push
export REPO=us-central1-docker.pkg.dev/sne-v1/sne-artifacts

for service in sne-web sne-worker sne-auto sne-telegram; do
  echo "📦 Building $service..."
  docker build -t $REPO/$service:latest ./services/$service
  docker push $REPO/$service:latest
done
```

---

## 🚀 OU USAR O SCRIPT AUTOMÁTICO

```bash
# Garantir que está no diretório correto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Executar script
./build_e_deploy_tudo.sh sne-v1 us-central1
```

---

## 🔍 VERIFICAÇÕES

```bash
# 1. Docker está rodando?
docker ps

# 2. Está no diretório correto?
pwd
# Deve ser: /Users/renan/Desktop/SNE_BACKUP_CLEAN

# 3. Serviços existem?
ls services/sne-web
ls services/sne-worker
ls services/sne-auto
ls services/sne-telegram
```

---

**💡 Dica:** Inicie o Docker Desktop primeiro, aguarde 30 segundos, depois execute os comandos novamente.




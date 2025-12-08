# 🐳 INICIAR DOCKER E BUILDAR IMAGENS

## ⚠️ PROBLEMA

Docker daemon não está rodando. Você precisa iniciar o Docker Desktop primeiro.

---

## ✅ SOLUÇÃO PASSO A PASSO

### PASSO 1: Iniciar Docker Desktop

**Opção A - Via Terminal:**
```bash
open -a Docker
```

**Opção B - Manual:**
1. Abra o **Docker Desktop** no seu Mac
2. Aguarde até aparecer "Docker Desktop is running" na barra de menu

### PASSO 2: Aguardar Docker Iniciar

```bash
# Aguardar 30 segundos
sleep 30

# Verificar se está rodando
docker ps
```

Se retornar uma lista (mesmo que vazia), está funcionando! ✅

### PASSO 3: Navegar para o Diretório Correto

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
```

### PASSO 4: Buildar e Pushar Imagens

**Opção A - Script Automático (Recomendado):**
```bash
./build_imagens.sh sne-v1 us-central1
```

**Opção B - Manual:**
```bash
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

## 🔍 VERIFICAÇÕES RÁPIDAS

```bash
# 1. Docker está rodando?
docker ps
# ✅ Se funcionar, está OK

# 2. Está no diretório correto?
pwd
# ✅ Deve ser: /Users/renan/Desktop/SNE_BACKUP_CLEAN

# 3. Serviços existem?
ls services/sne-web
# ✅ Deve listar arquivos
```

---

## 🚀 COMANDO COMPLETO (Copie e Cole)

```bash
# 1. Iniciar Docker
open -a Docker
sleep 30

# 2. Navegar para diretório correto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# 3. Verificar Docker
docker ps

# 4. Build e push
./build_imagens.sh sne-v1 us-central1
```

---

**💡 Dica:** Se o Docker Desktop não estiver instalado, instale em: https://www.docker.com/products/docker-desktop/




# 🐳 INSTALAR DOCKER DESKTOP

## ⚠️ Docker Desktop não está instalado

Você precisa instalar o Docker Desktop para buildar as imagens.

---

## ✅ OPÇÃO 1: Instalar via Homebrew (Recomendado)

```bash
# Instalar Docker Desktop
brew install --cask docker

# Iniciar Docker Desktop
open -a Docker

# Aguardar 30 segundos
sleep 30

# Verificar
docker ps
```

---

## ✅ OPÇÃO 2: Download Manual

1. Acesse: https://www.docker.com/products/docker-desktop/
2. Baixe o Docker Desktop para Mac
3. Instale o arquivo `.dmg`
4. Abra o Docker Desktop
5. Aguarde iniciar (ícone na barra de menu)

---

## ✅ OPÇÃO 3: Usar Cloud Build (Sem Docker Local)

Se não quiser instalar Docker localmente, você pode usar **Cloud Build** diretamente:

```bash
# Build e deploy usando Cloud Build (sem Docker local)
gcloud builds submit --config cloudbuild.yaml
```

Isso vai:
- Buildar as imagens na nuvem
- Pushar para Artifact Registry
- Fazer deploy dos serviços

---

## 🚀 DEPOIS DE INSTALAR

```bash
# 1. Verificar Docker
docker ps

# 2. Navegar para diretório
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# 3. Build e deploy
./build_imagens.sh sne-v1 us-central1
./deploy/deploy_all.sh sne-v1 us-central1
```

---

## 💡 RECOMENDAÇÃO

**Para desenvolvimento local:** Instale Docker Desktop (Opção 1 ou 2)

**Para deploy rápido:** Use Cloud Build (Opção 3) - não precisa de Docker local!




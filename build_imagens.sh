#!/bin/bash
# Script para buildar e pushar imagens Docker

set -e

# Verificar se está no diretório correto
if [ ! -d "services/sne-web" ]; then
    echo "❌ Erro: Execute este script do diretório raiz do projeto"
    echo "   cd /Users/renan/Desktop/SNE_BACKUP_CLEAN"
    exit 1
fi

# Verificar Docker
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    echo "   Inicie o Docker Desktop e aguarde 30 segundos"
    exit 1
fi

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID=${1:-"sne-v1"}
REGION=${2:-"us-central1"}
REPO=us-central1-docker.pkg.dev/${PROJECT_ID}/sne-artifacts

echo "🚀 Build e Push de Imagens Docker"
echo "Projeto: $PROJECT_ID"
echo "Repositório: $REPO"
echo ""

# Autenticar Docker
echo "🔐 Autenticando Docker..."
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Build e push
echo ""
echo "📦 Building e pushando imagens..."
for service in sne-web sne-worker sne-auto sne-telegram; do
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📦 $service"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [ ! -d "services/$service" ]; then
    echo "❌ Diretório services/$service não encontrado!"
    continue
  fi
  
  # Build
  echo "Building..."
  docker build -t $REPO/$service:latest ./services/$service || {
    echo "❌ Erro ao buildar $service"
    exit 1
  }
  
  # Push
  echo "Pushing..."
  docker push $REPO/$service:latest || {
    echo "❌ Erro ao pushar $service"
    exit 1
  }
  
  echo "✅ $service concluído!"
done

echo ""
echo "✅ Todas as imagens foram buildadas e pushadas!"
echo ""
echo "📋 Próximo passo: Atualizar serviços Cloud Run"
echo "   ./deploy/deploy_all.sh $PROJECT_ID $REGION"




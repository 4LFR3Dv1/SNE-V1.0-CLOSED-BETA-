#!/bin/bash
# Script completo: Build e Deploy de todas as imagens

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID=${1:-"sne-v1"}
REGION=${2:-"us-central1"}
REPO=us-central1-docker.pkg.dev/${PROJECT_ID}/sne-artifacts

echo "🚀 Build e Deploy Completo - SNE 1.0 Cloud"
echo "Projeto: $PROJECT_ID"
echo "Região: $REGION"
echo ""

# 1. Autenticar Docker
echo "🔐 Autenticando Docker..."
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# 2. Build e push de cada serviço
echo ""
echo "📦 Building e pushando imagens..."
for service in sne-web sne-worker sne-auto sne-telegram; do
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📦 $service"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Build
  echo "Building..."
  docker build -t $REPO/$service:latest ./services/$service
  
  # Push
  echo "Pushing..."
  docker push $REPO/$service:latest
  
  echo "✅ $service concluído!"
done

# 3. Atualizar serviços Cloud Run
echo ""
echo "🚀 Atualizando serviços Cloud Run..."
for service in sne-web sne-worker sne-auto sne-telegram; do
  echo "Atualizando $service..."
  gcloud run services update $service \
    --image $REPO/$service:latest \
    --region $REGION \
    --quiet
  
  echo "✅ $service atualizado!"
done

# 4. Verificar
echo ""
echo "✅ Deploy completo!"
echo ""
echo "📋 URLs dos serviços:"
gcloud run services list --region=$REGION --format="table(SERVICE,URL)"

echo ""
echo "🧪 Testando health checks..."
for service in sne-web sne-worker sne-auto sne-telegram; do
  URL=$(gcloud run services describe $service --region=$REGION --format="value(status.url)")
  echo -n "  $service: "
  curl -s $URL/health | head -1 || echo "Erro"
done

echo ""
echo "🎉 Tudo pronto!"




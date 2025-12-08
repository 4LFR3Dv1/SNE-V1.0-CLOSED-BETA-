#!/bin/bash
# Deploy usando Cloud Build (sem Docker local)

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID=${1:-"sne-v1"}
REGION=${2:-"europe-west1"}  # Changed to avoid Binance geo-blocking

echo "🚀 Deploy via Cloud Build (sem Docker local)"
echo "Projeto: $PROJECT_ID"
echo "Região: $REGION"
echo ""

# Verificar se cloudbuild.yaml existe
if [ ! -f "cloudbuild.yaml" ]; then
    echo "❌ cloudbuild.yaml não encontrado!"
    exit 1
fi

# Connection name
DB_CONNECTION_NAME="${PROJECT_ID}:${REGION}:sne-db-prod"

echo "📦 Submetendo build para Cloud Build..."
echo "   Connection: $DB_CONNECTION_NAME"
echo "   (A senha será obtida do Secret Manager durante o build)"
echo ""

# Submeter build com substituições
gcloud builds submit \
    --project=$PROJECT_ID \
    --config=cloudbuild.yaml \
    --substitutions=_PROJECT_ID=$PROJECT_ID,_REGION=$REGION,_DB_CONNECTION_NAME=$DB_CONNECTION_NAME

echo ""
echo "✅ Build concluído!"
echo ""
echo "📋 Verificando serviços..."
gcloud run services list --region=$REGION --format="table(SERVICE,URL,STATUS)"

echo ""
echo "🎉 Deploy completo!"


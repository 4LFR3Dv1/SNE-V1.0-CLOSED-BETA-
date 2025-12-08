#!/bin/bash
# Script para habilitar acesso público aos serviços Cloud Run

set -e

PROJECT_ID=${1:-"sne-v1"}
REGION=${2:-"europe-west1"}

echo "🔓 Habilitando acesso público aos serviços Cloud Run..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Projeto: $PROJECT_ID"
echo "Região: $REGION"
echo ""

SERVICES=("sne-web" "sne-worker" "sne-auto" "sne-telegram")

for SERVICE in "${SERVICES[@]}"; do
    echo "🔓 Habilitando acesso público para $SERVICE..."
    
    gcloud run services add-iam-policy-binding $SERVICE \
        --region=$REGION \
        --project=$PROJECT_ID \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --quiet
    
    echo "✅ $SERVICE configurado!"
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Acesso público habilitado para todos os serviços!"
echo ""
echo "📋 URLs dos serviços:"
echo ""
for SERVICE in "${SERVICES[@]}"; do
    URL=$(gcloud run services describe $SERVICE \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)" 2>/dev/null || echo "N/A")
    echo "  $SERVICE: $URL"
done
echo ""
echo "🧪 Teste agora:"
echo "  curl https://sne-web-pqhownilea-ew.a.run.app/health"
echo ""


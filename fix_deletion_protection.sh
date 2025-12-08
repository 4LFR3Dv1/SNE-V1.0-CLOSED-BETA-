#!/bin/bash
# Script para desabilitar deletion_protection do Cloud SQL antes da migração

set -e

PROJECT_ID=${1:-"sne-v1"}
INSTANCE_NAME=${2:-"sne-db-prod"}

echo "🔓 Desabilitando deletion_protection do Cloud SQL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Projeto: $PROJECT_ID"
echo "Instância: $INSTANCE_NAME"
echo ""

# Verificar se a instância existe
if ! gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID &>/dev/null; then
    echo "❌ Instância $INSTANCE_NAME não encontrada no projeto $PROJECT_ID"
    exit 1
fi

# Verificar status atual
CURRENT_PROTECTION=$(gcloud sql instances describe $INSTANCE_NAME --project=$PROJECT_ID --format="value(settings.deletionProtectionEnabled)" 2>/dev/null || echo "false")

if [ "$CURRENT_PROTECTION" == "True" ] || [ "$CURRENT_PROTECTION" == "true" ]; then
    echo "⚠️  deletion_protection está HABILITADO"
    echo "🔓 Desabilitando..."
    
    gcloud sql instances patch $INSTANCE_NAME \
        --project=$PROJECT_ID \
        --no-deletion-protection
    
    echo "✅ deletion_protection desabilitado!"
else
    echo "✅ deletion_protection já está desabilitado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Pronto para migração!"
echo ""
echo "Agora você pode continuar com:"
echo "  terraform apply tfplan"
echo ""


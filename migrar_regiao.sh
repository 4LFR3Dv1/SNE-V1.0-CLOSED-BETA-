#!/bin/bash
# Script para migrar região do Cloud Run para evitar bloqueio da Binance

set -e

PROJECT_ID=${1:-"sne-v1"}
OLD_REGION=${2:-"us-central1"}
NEW_REGION=${3:-"europe-west1"}

echo "🌍 Migração de Região - SNE 1.0 Cloud"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Projeto: $PROJECT_ID"
echo "Região Atual: $OLD_REGION"
echo "Nova Região: $NEW_REGION"
echo ""

# Verificar se a nova região é diferente
if [ "$OLD_REGION" == "$NEW_REGION" ]; then
    echo "⚠️  A nova região é igual à atual. Nada a fazer."
    exit 0
fi

echo "⚠️  ATENÇÃO: Esta migração irá:"
echo "   1. Recriar todos os serviços Cloud Run na nova região"
echo "   2. Recriar o Artifact Registry na nova região"
echo "   3. Recriar o VPC Connector na nova região"
echo "   4. O Cloud SQL pode precisar ser recriado (ou usar proxy)"
echo ""
read -p "Deseja continuar? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migração cancelada."
    exit 1
fi

echo ""
echo "📋 Passos da migração:"
echo ""

# 1. Backup do banco de dados (se necessário)
echo "1️⃣  Fazendo backup do banco de dados..."
gcloud sql backups create --instance=sne-db-prod --project=$PROJECT_ID 2>/dev/null || echo "   ⚠️  Backup automático já existe ou falhou (continuando...)"

# 2. Atualizar Terraform
echo ""
echo "2️⃣  Atualizando configuração Terraform..."
cd infra/terraform

# Verificar se já está na nova região
CURRENT_REGION=$(grep 'default.*=.*"europe-west1"' variables.tf | head -1 | grep -o 'europe-west1' || echo "")
if [ "$CURRENT_REGION" != "europe-west1" ]; then
    echo "   📝 Atualizando variables.tf..."
    sed -i.bak 's/default.*=.*"us-central1"/default     = "europe-west1"/' variables.tf
    echo "   ✅ variables.tf atualizado"
else
    echo "   ✅ variables.tf já está configurado para $NEW_REGION"
fi

# 3. Desabilitar deletion_protection do Cloud SQL
echo ""
echo "3️⃣  Preparando Cloud SQL para migração..."
if gcloud sql instances describe sne-db-prod --project=$PROJECT_ID &>/dev/null; then
    CURRENT_PROTECTION=$(gcloud sql instances describe sne-db-prod --project=$PROJECT_ID --format="value(settings.deletionProtectionEnabled)" 2>/dev/null || echo "false")
    if [ "$CURRENT_PROTECTION" == "True" ] || [ "$CURRENT_PROTECTION" == "true" ]; then
        echo "   🔓 Desabilitando deletion_protection do Cloud SQL..."
        gcloud sql instances patch sne-db-prod \
            --project=$PROJECT_ID \
            --no-deletion-protection
        echo "   ✅ deletion_protection desabilitado!"
    else
        echo "   ✅ deletion_protection já está desabilitado"
    fi
else
    echo "   ⚠️  Instância Cloud SQL não encontrada (será criada na nova região)"
fi

# 4. Aplicar Terraform
echo ""
echo "4️⃣  Aplicando mudanças no Terraform..."
echo "   ⚠️  Isso pode levar alguns minutos..."
terraform init -upgrade
terraform plan -var="project_id=$PROJECT_ID" -var="region=$NEW_REGION" -out=tfplan
read -p "   Aplicar mudanças? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply tfplan
    echo "   ✅ Terraform aplicado!"
else
    echo "   ⚠️  Terraform não aplicado. Execute manualmente:"
    echo "   terraform apply -var=\"project_id=$PROJECT_ID\" -var=\"region=$NEW_REGION\""
fi

# 5. Atualizar Artifact Registry
echo ""
echo "5️⃣  Atualizando Artifact Registry..."
echo "   ℹ️  O Artifact Registry será recriado na nova região"
echo "   ℹ️  Você precisará fazer rebuild das imagens Docker"

# 6. Atualizar deploy script
echo ""
echo "6️⃣  Atualizando script de deploy..."
cd ../..
if grep -q "us-central1" deploy_cloud_build.sh; then
    sed -i.bak "s/us-central1/europe-west1/g" deploy_cloud_build.sh
    echo "   ✅ deploy_cloud_build.sh atualizado"
else
    echo "   ✅ deploy_cloud_build.sh já está atualizado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Migração configurada!"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Rebuild e redeploy das imagens Docker:"
echo "   ./deploy_cloud_build.sh $PROJECT_ID $NEW_REGION"
echo ""
echo "2. Testar endpoints:"
echo "   curl https://sne-web-<hash>-$NEW_REGION.a.run.app/health"
echo ""
echo "3. Verificar logs:"
echo "   gcloud run services logs read sne-web --region=$NEW_REGION --limit=20"
echo ""
echo "4. Testar acesso à Binance:"
echo "   curl -X POST https://sne-web-<hash>-$NEW_REGION.a.run.app/api/analyze \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"symbol\": \"BTCUSDT\", \"timeframe\": \"1h\"}'"
echo ""
echo "💡 Se não houver mais erro 451, a migração foi bem-sucedida! ✅"


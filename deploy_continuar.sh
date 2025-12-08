#!/bin/bash
# Script para continuar o deploy do SNE 1.0 Cloud

set -e

# Adicionar gcloud ao PATH
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

echo "🚀 Continuando deploy do SNE 1.0 Cloud..."
echo ""

# Verificar se gcloud está funcionando
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud não encontrado. Execute: source ~/.zshrc"
    exit 1
fi

# Verificar projeto atual
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    echo "⚠️  Nenhum projeto configurado"
    echo ""
    echo "📋 Criando novo projeto..."
    
    # Criar projeto
    export PROJECT_ID="sne-cloud-$(date +%s)"
    echo "Criando projeto: $PROJECT_ID"
    gcloud projects create $PROJECT_ID --name="SNE Cloud" || {
        echo "❌ Erro ao criar projeto. Verifique se já existe ou use um ID diferente."
        exit 1
    }
    
    # Definir projeto
    gcloud config set project $PROJECT_ID
    echo "✅ Projeto $PROJECT_ID criado e configurado"
else
    echo "✅ Projeto atual: $CURRENT_PROJECT"
    export PROJECT_ID=$CURRENT_PROJECT
fi

echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Habilitar billing (necessário):"
echo "   gcloud billing projects link $PROJECT_ID --billing-account=SEU-BILLING-ACCOUNT-ID"
echo ""
echo "2. Habilitar APIs necessárias:"
echo "   ./habilitar_apis.sh $PROJECT_ID"
echo ""
echo "3. Aplicar infraestrutura Terraform:"
echo "   cd infra/terraform"
echo "   terraform init"
echo "   terraform apply"
echo ""




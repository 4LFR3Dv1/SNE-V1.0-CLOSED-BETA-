#!/bin/bash
# Script para instalar ferramentas necessárias para deploy GCP

set -e

echo "🛠️  Instalando ferramentas para deploy GCP..."
echo ""

# Verificar Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew não encontrado. Instalando..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew já instalado"
fi

# Instalar gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo "📦 Instalando Google Cloud SDK..."
    brew install --cask google-cloud-sdk
    echo "✅ Google Cloud SDK instalado"
else
    echo "✅ gcloud já instalado: $(gcloud --version | head -1)"
fi

# Instalar Terraform
if ! command -v terraform &> /dev/null; then
    echo "📦 Instalando Terraform..."
    brew install terraform
    echo "✅ Terraform instalado"
else
    echo "✅ Terraform já instalado: $(terraform --version | head -1)"
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker não encontrado. Instale o Docker Desktop: https://www.docker.com/products/docker-desktop"
else
    echo "✅ Docker já instalado: $(docker --version)"
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Execute: gcloud auth login"
echo "2. Siga o guia: DEPLOY_GCP.md"
echo ""




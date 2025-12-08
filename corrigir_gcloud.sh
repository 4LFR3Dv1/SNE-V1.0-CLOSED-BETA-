#!/bin/bash
# Script para corrigir instalação do gcloud

set -e

echo "🔧 Corrigindo instalação do Google Cloud SDK..."
echo ""

# Configurar Python do sistema
export CLOUDSDK_PYTHON=/usr/bin/python3
echo "✅ Python configurado: $CLOUDSDK_PYTHON"
/usr/bin/python3 --version

# Limpar instalação anterior (se houver)
echo ""
echo "🧹 Limpando instalação anterior..."
brew uninstall --cask google-cloud-sdk 2>/dev/null || echo "Nenhuma instalação anterior encontrada"
rm -rf /usr/local/share/google-cloud-sdk 2>/dev/null || true

# Instalar novamente
echo ""
echo "📦 Instalando Google Cloud SDK..."
brew install --cask google-cloud-sdk

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
if command -v gcloud &> /dev/null; then
    gcloud --version
    echo ""
    echo "🎉 Google Cloud SDK instalado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Execute: gcloud auth login"
    echo "2. Execute: gcloud init"
    echo "3. Siga o guia: DEPLOY_GCP.md"
else
    echo "❌ Instalação falhou. Tente instalar manualmente:"
    echo "   curl https://sdk.cloud.google.com | bash"
fi




#!/bin/bash
# Corrigir PATH e virtualenv do gcloud

set -e

echo "🔧 Corrigindo gcloud PATH e virtualenv..."
echo ""

# Adicionar ao PATH
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Configurar Python
export CLOUDSDK_PYTHON=$(which python3)
echo "✅ Python configurado: $CLOUDSDK_PYTHON"
$CLOUDSDK_PYTHON --version

# Verificar se gcloud está acessível
if [ ! -f "$HOME/google-cloud-sdk/bin/gcloud" ]; then
    echo "❌ gcloud não encontrado em ~/google-cloud-sdk/bin/"
    echo "Execute: ./instalar_gcloud_manual.sh"
    exit 1
fi

echo ""
echo "🔧 Recriando virtualenv do gcloud..."
# Remover virtualenv corrompido
rm -rf ~/.config/gcloud/virtenv 2>/dev/null || true

# Recriar virtualenv
$HOME/google-cloud-sdk/bin/gcloud config virtualenv create --python-to-use $CLOUDSDK_PYTHON 2>&1 || {
    echo "⚠️  Tentando método alternativo..."
    # Método alternativo: usar gcloud components reinstall
    $HOME/google-cloud-sdk/bin/gcloud components reinstall --quiet 2>&1 || true
}

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
if $HOME/google-cloud-sdk/bin/gcloud --version > /dev/null 2>&1; then
    $HOME/google-cloud-sdk/bin/gcloud --version
    echo ""
    echo "🎉 gcloud corrigido com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Execute: source ~/.zshrc  (ou abra um novo terminal)"
    echo "2. Execute: gcloud auth login"
    echo "3. Execute: gcloud init"
else
    echo "❌ Ainda há problemas. Tente:"
    echo "   rm -rf ~/.config/gcloud"
    echo "   ~/google-cloud-sdk/install.sh --quiet"
fi




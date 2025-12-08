#!/bin/bash
# Instalação manual do Google Cloud SDK (sem Homebrew)

set -e

echo "🔧 Instalando Google Cloud SDK manualmente..."
echo ""

# Diretório de instalação
INSTALL_DIR="$HOME/google-cloud-sdk"

# Remover instalação anterior (se houver)
if [ -d "$INSTALL_DIR" ]; then
    echo "🧹 Removendo instalação anterior..."
    rm -rf "$INSTALL_DIR"
fi

# Baixar e instalar
echo "📦 Baixando Google Cloud SDK..."
curl https://sdk.cloud.google.com | bash

# Adicionar ao PATH
echo ""
echo "📝 Adicionando ao PATH..."
if ! grep -q "google-cloud-sdk/bin" ~/.zshrc 2>/dev/null; then
    echo 'export PATH="$HOME/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc
    echo "✅ Adicionado ao ~/.zshrc"
else
    echo "✅ Já está no PATH"
fi

# Carregar no shell atual
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Verificar instalação
echo ""
echo "✅ Verificando instalação..."
if command -v gcloud &> /dev/null; then
    gcloud --version
    echo ""
    echo "🎉 Google Cloud SDK instalado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Execute: source ~/.zshrc  (ou abra um novo terminal)"
    echo "2. Execute: gcloud auth login"
    echo "3. Execute: gcloud init"
    echo "4. Siga o guia: DEPLOY_GCP.md"
else
    echo "⚠️  gcloud não encontrado no PATH"
    echo "Execute: source ~/.zshrc"
fi




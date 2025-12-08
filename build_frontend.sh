#!/bin/bash

# Script para build do frontend SNE

# Carregar NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Carregando NVM..."
    source "$HOME/.nvm/nvm.sh"
fi

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo ""

# Ir para diretório frontend
cd "$(dirname "$0")/frontend"

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

echo ""
echo "🔨 Fazendo build do frontend..."
echo ""

# Build
npm run build

# Verificar se build foi bem-sucedido
if [ -f "dist/index.html" ]; then
    echo ""
    echo "✅ Build concluído com sucesso!"
    echo "📁 Arquivos em: frontend/dist/"
    echo ""
    echo "💡 Agora você pode rodar o Flask:"
    echo "   python3 sne_radar_web.py"
    echo "   Acesse: http://localhost:9999"
else
    echo ""
    echo "❌ Erro no build! Verifique os erros acima."
    exit 1
fi


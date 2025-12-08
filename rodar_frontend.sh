#!/bin/bash

# Script para rodar o frontend SNE

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
echo "🚀 Iniciando servidor de desenvolvimento..."
echo "🌐 Acesse: http://localhost:5173"
echo ""
echo "💡 Para parar, pressione Ctrl+C"
echo ""

# Rodar Vite
npm run dev


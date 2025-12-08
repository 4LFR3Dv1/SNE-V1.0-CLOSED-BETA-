#!/bin/bash

# Script para rodar frontend + backend completo

echo "🚀 Iniciando SNE Frontend + Backend"
echo ""

# Carregar NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Carregando NVM..."
    source "$HOME/.nvm/nvm.sh"
fi

echo "✅ Node.js: $(node --version)"
echo ""

# Verificar se estamos no diretório correto
if [ ! -d "frontend" ]; then
    echo "❌ Diretório frontend não encontrado!"
    echo "   Execute este script do diretório raiz do projeto"
    exit 1
fi

echo "📋 Instruções:"
echo ""
echo "1. Este script vai iniciar o Flask (backend)"
echo "2. Em OUTRO TERMINAL, execute:"
echo "   cd frontend"
echo "   source \"\$HOME/.nvm/nvm.sh\""
echo "   npm run dev"
echo ""
echo "3. Acesse:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:9999"
echo ""
echo "Pressione Enter para iniciar o Flask..."
read

echo ""
echo "🔧 Iniciando Flask..."
echo ""

# Rodar Flask
python3 sne_radar_web.py


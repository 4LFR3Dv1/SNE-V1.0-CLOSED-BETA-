#!/bin/bash

echo "🔍 Verificando instalação do Node.js..."
echo ""

# Verificar Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js instalado:"
    node --version
else
    echo "❌ Node.js NÃO encontrado"
fi

echo ""

# Verificar npm
if command -v npm &> /dev/null; then
    echo "✅ npm instalado:"
    npm --version
else
    echo "❌ npm NÃO encontrado"
fi

echo ""
echo "📋 Próximos passos:"
echo ""

if command -v node &> /dev/null && command -v npm &> /dev/null; then
    echo "✅ Tudo instalado! Execute:"
    echo "   cd frontend"
    echo "   npm install"
else
    echo "⚠️  Instale Node.js primeiro:"
    echo "   1. Baixe de: https://nodejs.org/"
    echo "   2. Instale o arquivo .pkg"
    echo "   3. Abra um NOVO terminal"
    echo "   4. Execute este script novamente"
fi


#!/bin/bash
# Script para criar instalador Windows a partir do Mac
# Opções: Wine, Docker, ou preparar para build em Windows

echo "========================================"
echo "📦 Criar Instalador Windows (do Mac)"
echo "========================================"
echo ""

# Verificar se o executável Windows foi buildado
if [ ! -f "dist/SNE_RADAR.exe" ]; then
    echo "❌ Executável Windows não encontrado!"
    echo ""
    echo "💡 Você precisa buildar o executável Windows primeiro."
    echo "   Mas PyInstaller no Mac não cria .exe para Windows."
    echo ""
    echo "📋 OPÇÕES:"
    echo ""
    echo "1️⃣  Usar GitHub Actions (Recomendado - Mais Fácil)"
    echo "    - Crie um workflow que builda no Windows automaticamente"
    echo "    - Execute: ./setup_github_actions_windows.sh"
    echo ""
    echo "2️⃣  Usar Docker com Windows (Avançado)"
    echo "    - Requer Docker Desktop"
    echo "    - Execute: ./build_windows_docker.sh"
    echo ""
    echo "3️⃣  Usar Wine (Emulação Windows)"
    echo "    - Instale Wine: brew install --cask wine-stable"
    echo "    - Execute: ./build_windows_wine.sh"
    echo ""
    echo "4️⃣  Preparar arquivos e buildar em Windows depois"
    echo "    - Execute: ./preparar_build_windows.sh"
    echo "    - Copie para Windows e execute build_windows.bat"
    echo ""
    exit 1
fi

echo "✅ Executável encontrado: dist/SNE_RADAR.exe"
echo ""

# Verificar opções disponíveis
echo "🔍 Verificando opções disponíveis..."
echo ""

# Verificar Wine
if command -v wine &> /dev/null; then
    echo "✅ Wine encontrado"
    WINE_AVAILABLE=1
else
    echo "❌ Wine não encontrado"
    WINE_AVAILABLE=0
fi

# Verificar Docker
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "✅ Docker encontrado e rodando"
    DOCKER_AVAILABLE=1
else
    echo "❌ Docker não encontrado ou não está rodando"
    DOCKER_AVAILABLE=0
fi

echo ""
echo "📋 OPÇÕES DISPONÍVEIS:"
echo ""

if [ $WINE_AVAILABLE -eq 1 ]; then
    echo "1️⃣  Usar Wine (já instalado)"
    echo "    Execute: ./build_windows_wine.sh"
    echo ""
fi

if [ $DOCKER_AVAILABLE -eq 1 ]; then
    echo "2️⃣  Usar Docker com Windows"
    echo "    Execute: ./build_windows_docker.sh"
    echo ""
fi

echo "3️⃣  GitHub Actions (Recomendado)"
echo "    Execute: ./setup_github_actions_windows.sh"
echo ""

echo "4️⃣  Preparar e buildar em Windows depois"
echo "    Execute: ./preparar_build_windows.sh"
echo ""

echo "💡 RECOMENDAÇÃO: Use GitHub Actions (opção 3)"
echo "   É mais confiável e não precisa instalar nada extra!"
echo ""



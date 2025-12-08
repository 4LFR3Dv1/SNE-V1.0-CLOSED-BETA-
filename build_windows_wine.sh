#!/bin/bash
# Build instalador Windows usando Wine (emulação Windows no Mac)
# Requer: Wine instalado

echo "========================================"
echo "🍷 Criando Instalador Windows via Wine"
echo "========================================"
echo ""

# Verificar Wine
if ! command -v wine &> /dev/null; then
    echo "❌ Wine não encontrado!"
    echo ""
    echo "💡 Instale Wine:"
    echo "   brew install --cask wine-stable"
    echo ""
    echo "   Ou:"
    echo "   brew install --cask gcenx/wine/wine-crossover"
    echo ""
    exit 1
fi

echo "✅ Wine encontrado"
echo ""

# Verificar se o executável foi buildado
if [ ! -f "dist/SNE_RADAR.exe" ]; then
    echo "❌ Executável não encontrado!"
    echo "💡 Primeiro você precisa buildar o executável Windows."
    echo "   Mas PyInstaller no Mac não cria .exe para Windows."
    echo ""
    echo "💡 SOLUÇÃO: Use GitHub Actions ou Docker para buildar o .exe primeiro."
    exit 1
fi

# Verificar se Inno Setup está instalado no Wine
WINE_PREFIX="${HOME}/.wine"
INNO_PATH="${WINE_PREFIX}/drive_c/Program Files (x86)/Inno Setup 6/ISCC.exe"

if [ ! -f "$INNO_PATH" ]; then
    echo "⚠️  Inno Setup não encontrado no Wine"
    echo ""
    echo "💡 Você precisa instalar Inno Setup no Wine primeiro:"
    echo ""
    echo "1. Baixe Inno Setup: https://jrsoftware.org/isinfo.php"
    echo "2. Execute: wine innosetup-6.x.x.exe"
    echo "3. Instale normalmente no Wine"
    echo ""
    echo "Ou use outra opção (GitHub Actions é mais fácil!)"
    exit 1
fi

echo "✅ Inno Setup encontrado no Wine"
echo ""

# Criar diretório para o instalador
mkdir -p installer

# Compilar o instalador usando Wine
echo "🔨 Compilando instalador via Wine..."
echo ""

wine "$INNO_PATH" setup_sne_radar.iss

if [ $? -eq 0 ] && [ -f "installer/SNE_RADAR_Setup.exe" ]; then
    echo ""
    echo "✅ Instalador criado com sucesso!"
    echo ""
    echo "📦 Arquivo: installer/SNE_RADAR_Setup.exe"
    echo ""
else
    echo ""
    echo "❌ Erro ao criar instalador"
    echo ""
    echo "💡 Tente usar GitHub Actions (mais confiável):"
    echo "   ./setup_github_actions_windows.sh"
    echo ""
    exit 1
fi



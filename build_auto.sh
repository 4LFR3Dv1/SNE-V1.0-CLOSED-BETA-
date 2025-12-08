#!/bin/bash
# build_auto.sh
# Script automático que verifica TUDO e builda o executável standalone

set -e

echo "🔍 Verificando pré-requisitos..."
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ERRORS=0

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Python 3 encontrado${NC}"
fi

# 2. Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 não encontrado${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ pip3 encontrado${NC}"
fi

# 3. Verificar Node.js (necessário APENAS para buildar, não para usar o executável)
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js/npm não encontrado${NC}"
    echo "   Node.js é necessário APENAS para buildar o frontend"
    echo "   O executável FINAL não precisará do Node.js!"
    echo ""
    echo "   Instale Node.js:"
    echo "     macOS: brew install node"
    echo "     OU: https://nodejs.org/"
    echo ""
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Node.js encontrado${NC}"
fi

# 4. Verificar pywebview
if ! python3 -c "import webview" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  pywebview não instalado${NC}"
    echo "   Instalando automaticamente..."
    pip3 install pywebview
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ pywebview instalado${NC}"
    else
        echo -e "${RED}❌ Erro ao instalar pywebview${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${GREEN}✅ pywebview instalado${NC}"
fi

# 5. Verificar PyInstaller
if ! command -v pyinstaller &> /dev/null && ! python3 -m PyInstaller --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  PyInstaller não instalado${NC}"
    echo "   Instalando automaticamente..."
    pip3 install pyinstaller
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PyInstaller instalado${NC}"
    else
        echo -e "${RED}❌ Erro ao instalar PyInstaller${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${GREEN}✅ PyInstaller instalado${NC}"
fi

echo ""
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Encontrados $ERRORS erro(s). Corrija antes de continuar.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Todos os pré-requisitos atendidos!${NC}"
echo ""
echo "🚀 Iniciando build do executável standalone..."
echo ""

# Executar build
./build_standalone.sh


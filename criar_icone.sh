#!/bin/bash
# Script para converter PNG em ICNS e configurar nos arquivos de build
# Uso: ./criar_icone.sh caminho/para/imagem.png

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Erro: Especifique o caminho da imagem PNG${NC}"
    echo ""
    echo "Uso: $0 caminho/para/imagem.png"
    echo ""
    echo "Exemplo:"
    echo "  $0 assets/logo_sne.png"
    exit 1
fi

PNG_FILE="$1"
ICON_NAME="logo_sne"

# Verificar se arquivo existe
if [ ! -f "$PNG_FILE" ]; then
    echo -e "${RED}❌ Erro: Arquivo não encontrado: $PNG_FILE${NC}"
    exit 1
fi

# Verificar se é PNG
if ! file "$PNG_FILE" | grep -q "PNG"; then
    echo -e "${YELLOW}⚠️  Aviso: Arquivo pode não ser PNG válido${NC}"
fi

echo -e "${BLUE}🎨 Criando ícone para SNE_RADAR${NC}"
echo ""

# Criar diretório assets se não existir
mkdir -p assets

# Determinar nome base do ícone
if [[ "$PNG_FILE" == *"/"* ]]; then
    # Se tem caminho, usar nome do arquivo sem extensão
    ICON_BASE=$(basename "$PNG_FILE" .png)
else
    ICON_BASE=$(echo "$PNG_FILE" | sed 's/\.png$//')
fi

ICON_DIR="assets/${ICON_BASE}.iconset"
ICNS_FILE="assets/${ICON_BASE}.icns"

echo -e "${YELLOW}📁 Criando estrutura de ícones...${NC}"

# Remover diretório antigo se existir
rm -rf "$ICON_DIR"
mkdir -p "$ICON_DIR"

# Verificar se sips está disponível (macOS)
if ! command -v sips &> /dev/null; then
    echo -e "${RED}❌ Erro: 'sips' não encontrado. Este script requer macOS.${NC}"
    exit 1
fi

# Verificar se iconutil está disponível
if ! command -v iconutil &> /dev/null; then
    echo -e "${RED}❌ Erro: 'iconutil' não encontrado. Este script requer macOS.${NC}"
    exit 1
fi

echo -e "${YELLOW}🖼️  Gerando tamanhos de ícone...${NC}"

# Gerar todos os tamanhos necessários
# macOS requer múltiplos tamanhos para diferentes contextos

# 16x16
sips -z 16 16 "$PNG_FILE" --out "${ICON_DIR}/icon_16x16.png" > /dev/null
sips -z 32 32 "$PNG_FILE" --out "${ICON_DIR}/icon_16x16@2x.png" > /dev/null

# 32x32
sips -z 32 32 "$PNG_FILE" --out "${ICON_DIR}/icon_32x32.png" > /dev/null
sips -z 64 64 "$PNG_FILE" --out "${ICON_DIR}/icon_32x32@2x.png" > /dev/null

# 128x128
sips -z 128 128 "$PNG_FILE" --out "${ICON_DIR}/icon_128x128.png" > /dev/null
sips -z 256 256 "$PNG_FILE" --out "${ICON_DIR}/icon_128x128@2x.png" > /dev/null

# 256x256
sips -z 256 256 "$PNG_FILE" --out "${ICON_DIR}/icon_256x256.png" > /dev/null
sips -z 512 512 "$PNG_FILE" --out "${ICON_DIR}/icon_256x256@2x.png" > /dev/null

# 512x512
sips -z 512 512 "$PNG_FILE" --out "${ICON_DIR}/icon_512x512.png" > /dev/null
sips -z 1024 1024 "$PNG_FILE" --out "${ICON_DIR}/icon_512x512@2x.png" > /dev/null

echo -e "${GREEN}✅ Tamanhos gerados${NC}"

# Converter para ICNS
echo -e "${YELLOW}🔄 Convertendo para ICNS...${NC}"
iconutil -c icns "$ICON_DIR" -o "$ICNS_FILE"

if [ ! -f "$ICNS_FILE" ]; then
    echo -e "${RED}❌ Erro ao criar arquivo ICNS${NC}"
    exit 1
fi

ICNS_SIZE=$(du -h "$ICNS_FILE" | cut -f1)
echo -e "${GREEN}✅ Arquivo ICNS criado: $ICNS_FILE ($ICNS_SIZE)${NC}"

# Atualizar build_mac.spec
echo ""
echo -e "${YELLOW}📝 Atualizando build_mac.spec...${NC}"

if [ -f "build_mac.spec" ]; then
    # Verificar se já tem icon configurado
    if grep -q "icon=" build_mac.spec; then
        # Substituir linha existente
        sed -i.bak "s|icon=.*|icon='$ICNS_FILE',|" build_mac.spec
        echo -e "${GREEN}✅ build_mac.spec atualizado${NC}"
    else
        # Adicionar após name='SNE_RADAR.app',
        sed -i.bak "/name='SNE_RADAR.app',/a\\
    icon='$ICNS_FILE',
" build_mac.spec
        echo -e "${GREEN}✅ build_mac.spec atualizado (adicionado)${NC}"
    fi
    rm -f build_mac.spec.bak
else
    echo -e "${YELLOW}⚠️  build_mac.spec não encontrado${NC}"
fi

# Atualizar build_mac_with_launcher.spec
if [ -f "build_mac_with_launcher.spec" ]; then
    if grep -q "icon=" build_mac_with_launcher.spec; then
        sed -i.bak "s|icon=.*|icon='$ICNS_FILE',|" build_mac_with_launcher.spec
        echo -e "${GREEN}✅ build_mac_with_launcher.spec atualizado${NC}"
    else
        sed -i.bak "/name='SNE_RADAR.app',/a\\
    icon='$ICNS_FILE',
" build_mac_with_launcher.spec
        echo -e "${GREEN}✅ build_mac_with_launcher.spec atualizado (adicionado)${NC}"
    fi
    rm -f build_mac_with_launcher.spec.bak
fi

# Atualizar build_nuitka.sh
echo -e "${YELLOW}📝 Atualizando build_nuitka.sh...${NC}"

if [ -f "build_nuitka.sh" ]; then
    # Verificar se já tem --macos-app-icon
    if grep -q "--macos-app-icon" build_nuitka.sh; then
        # Substituir linha existente
        sed -i.bak "s|--macos-app-icon=.*|--macos-app-icon=$ICNS_FILE \\\\|" build_nuitka.sh
        echo -e "${GREEN}✅ build_nuitka.sh atualizado${NC}"
    else
        # Adicionar após --macos-create-app-bundle
        sed -i.bak "/--macos-create-app-bundle/a\\
        --macos-app-icon=$ICNS_FILE \\\\
" build_nuitka.sh
        echo -e "${GREEN}✅ build_nuitka.sh atualizado (adicionado)${NC}"
    fi
    rm -f build_nuitka.sh.bak
else
    echo -e "${YELLOW}⚠️  build_nuitka.sh não encontrado${NC}"
fi

# Limpar diretório temporário (opcional - manter para debug)
# rm -rf "$ICON_DIR"

echo ""
echo -e "${GREEN}✅ Ícone criado e configurado com sucesso!${NC}"
echo ""
echo -e "${BLUE}📋 Próximos passos:${NC}"
echo "   1. Verifique o arquivo: $ICNS_FILE"
echo "   2. Rebuild o app:"
echo "      ./build_with_launcher.sh"
echo "      OU"
echo "      ./build_nuitka.sh"
echo "   3. Verifique o ícone no Finder/Dock"
echo ""
echo -e "${YELLOW}💡 Dica:${NC} Para ver o ícone antes de rebuildar:"
echo "   open $ICNS_FILE"
echo ""


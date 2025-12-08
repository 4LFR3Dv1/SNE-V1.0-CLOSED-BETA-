#!/bin/bash
# Build completo do SNE_RADAR.app com todas as novas funcionalidades

set -e

echo "🔨 =========================================="
echo "   BUILD COMPLETO - SNE RADAR.app"
echo "   Com Scanner de Oportunidades e Wick Radar"
echo "🔨 =========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo "🔍 Verificando dependências..."

if ! command_exists python3; then
    echo -e "${RED}❌ Python3 não encontrado!${NC}"
    exit 1
fi

# Carregar NVM se disponível
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "   📦 Carregando NVM..."
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
fi

# Verificar npm após carregar NVM
if ! command_exists npm; then
    echo -e "${YELLOW}⚠️ npm não encontrado no PATH${NC}"
    echo "   Tentando carregar NVM..."
    
    # Tentar carregar NVM de diferentes locais
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    elif [ -s "/usr/local/opt/nvm/nvm.sh" ]; then
        export NVM_DIR="/usr/local/opt/nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi
    
    # Verificar novamente
    if ! command_exists npm; then
        echo -e "${RED}❌ npm ainda não encontrado!${NC}"
        echo ""
        echo "💡 Soluções:"
        echo "   1. Instalar Node.js: brew install node"
        echo "   2. Ou instalar NVM: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
        echo "   3. Ou usar Node.js direto se já estiver instalado"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"
echo -e "${GREEN}✅ npm: $(npm --version)${NC}"

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}⚠️ PyInstaller não encontrado. Instalando...${NC}"
    pip3 install pyinstaller
fi

echo -e "${GREEN}✅ Dependências OK${NC}"
echo ""

# Passo 1: Buildar Frontend
echo "📦 [1/4] Buildando frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "   📥 Instalando dependências npm..."
    npm install
fi

echo "   🔨 Executando build..."
npm run build

if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ Erro: frontend/dist/index.html não foi criado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend buildado com sucesso${NC}"
cd ..
echo ""

# Passo 2: Verificar módulos novos
echo "🔍 [2/4] Verificando módulos novos..."

MISSING_MODULES=0

if [ ! -d "scanners" ]; then
    echo -e "${RED}❌ Diretório scanners/ não encontrado!${NC}"
    MISSING_MODULES=1
fi

if [ ! -d "notifications" ]; then
    echo -e "${RED}❌ Diretório notifications/ não encontrado!${NC}"
    MISSING_MODULES=1
fi

if [ ! -d "monitors" ]; then
    echo -e "${RED}❌ Diretório monitors/ não encontrado!${NC}"
    MISSING_MODULES=1
fi

if [ $MISSING_MODULES -eq 1 ]; then
    echo -e "${RED}❌ Módulos faltando! Verifique a estrutura do projeto.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Todos os módulos encontrados${NC}"
echo ""

# Passo 3: Limpar builds anteriores
echo "🧹 [3/4] Limpando builds anteriores..."
rm -rf build dist *.spec.bak
echo -e "${GREEN}✅ Limpeza concluída${NC}"
echo ""

# Passo 4: Buildar .app
echo "🔨 [4/4] Buildando SNE_RADAR.app..."
echo ""

# Verificar se launcher.sh existe
if [ ! -f "launcher.sh" ]; then
    echo -e "${YELLOW}⚠️ launcher.sh não encontrado. Criando...${NC}"
    cat > launcher.sh << 'EOF'
#!/bin/bash
# Launcher para SNE_RADAR.app
cd "$(dirname "$0")"
exec ./SNE_RADAR_bin
EOF
    chmod +x launcher.sh
fi

# Executar PyInstaller
python3 -m PyInstaller build_mac_with_launcher.spec --clean --noconfirm

# Pós-processamento: CONFIGURAR LAUNCHER WRAPPER
echo ""
echo "🔧 Configurando launcher wrapper (garante duplo clique)..."

APP_MACOS="dist/SNE_RADAR.app/Contents/MacOS"
APP_BUNDLE="dist/SNE_RADAR.app"

if [ -d "$APP_MACOS" ]; then
    # 1. Verificar se o executável Python existe
    if [ -f "$APP_MACOS/SNE_RADAR" ]; then
        # Verificar se é um binário Mach-O (não script)
        if file "$APP_MACOS/SNE_RADAR" | grep -q "Mach-O"; then
            echo "   ✅ Executável Python verificado (binário Mach-O)"
            
            # 2. RENOMEAR executável Python para SNE_RADAR_bin
            mv "$APP_MACOS/SNE_RADAR" "$APP_MACOS/SNE_RADAR_bin"
            echo "   ✅ Executável Python renomeado para SNE_RADAR_bin"
        else
            echo -e "   ${YELLOW}⚠️ Executável não é binário válido${NC}"
        fi
    else
        echo -e "   ${RED}❌ Executável SNE_RADAR não encontrado!${NC}"
    fi
    
    # 3. CONFIGURAR LAUNCHER como executável principal
    if [ -f "launcher.sh" ]; then
        # Copiar launcher.sh para o bundle
        cp launcher.sh "$APP_MACOS/launcher.sh"
        chmod +x "$APP_MACOS/launcher.sh"
        
        # Renomear launcher.sh para SNE_RADAR (nome do executável principal)
        mv "$APP_MACOS/launcher.sh" "$APP_MACOS/SNE_RADAR"
        chmod +x "$APP_MACOS/SNE_RADAR"
        echo "   ✅ Launcher wrapper configurado como executável principal"
    else
        echo -e "   ${RED}❌ launcher.sh não encontrado!${NC}"
        echo "   💡 Criando launcher.sh básico..."
        cat > launcher.sh << 'EOF'
#!/bin/bash
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
EXECUTABLE="$APP_DIR/SNE_RADAR_bin"
if [ -f "$EXECUTABLE" ]; then
    chmod +x "$EXECUTABLE"
    exec "$EXECUTABLE"
else
    osascript -e 'display dialog "Erro: Executável não encontrado." buttons {"OK"} default button 1 with icon stop'
    exit 1
fi
EOF
        chmod +x launcher.sh
        cp launcher.sh "$APP_MACOS/SNE_RADAR"
        chmod +x "$APP_MACOS/SNE_RADAR"
        echo "   ✅ Launcher básico criado e configurado"
    fi
    
    # 4. Garantir permissões de execução
    chmod +x "$APP_MACOS/SNE_RADAR" 2>/dev/null || true
    chmod +x "$APP_MACOS/SNE_RADAR_bin" 2>/dev/null || true
    
    # Verificar módulos incluídos
    echo ""
    echo "📋 Verificando módulos incluídos:"
    
    if [ -d "$APP_BUNDLE/Contents/Resources/scanners" ]; then
        echo -e "   ${GREEN}✅ scanners/ incluído${NC}"
    else
        echo -e "   ${RED}❌ scanners/ NÃO incluído${NC}"
    fi
    
    if [ -d "$APP_BUNDLE/Contents/Resources/notifications" ]; then
        echo -e "   ${GREEN}✅ notifications/ incluído${NC}"
    else
        echo -e "   ${RED}❌ notifications/ NÃO incluído${NC}"
    fi
    
    if [ -d "$APP_BUNDLE/Contents/Resources/monitors" ]; then
        echo -e "   ${GREEN}✅ monitors/ incluído${NC}"
    else
        echo -e "   ${RED}❌ monitors/ NÃO incluído${NC}"
    fi
    
    if [ -d "$APP_BUNDLE/Contents/Resources/frontend/dist" ]; then
        echo -e "   ${GREEN}✅ frontend/dist/ incluído${NC}"
    else
        echo -e "   ${RED}❌ frontend/dist/ NÃO incluído${NC}"
    fi
fi

# Remover quarentena do macOS
echo ""
echo "🔓 Removendo quarentena do macOS..."
xattr -dr com.apple.quarantine "$APP_BUNDLE" 2>/dev/null || true

# Resultado final
echo ""
echo "=========================================="
echo -e "${GREEN}✅ BUILD COMPLETO COM SUCESSO!${NC}"
echo "=========================================="
echo ""
echo "📦 App criado em:"
echo "   $(pwd)/dist/SNE_RADAR.app"
echo ""
echo "🧪 Para testar:"
echo "   open dist/SNE_RADAR.app"
echo ""
echo "📊 Verificar logs:"
echo "   tail -f ~/Library/Application\\ Support/SNE_RADAR/logs/scanner.log"
echo ""
echo "🌐 Acessar Wick Radar:"
echo "   http://127.0.0.1:9999/wick-radar"
echo ""


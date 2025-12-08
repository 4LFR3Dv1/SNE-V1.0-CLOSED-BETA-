#!/bin/bash
# build_standalone.sh
# Script para buildar o SNE RADAR como aplicação desktop nativa

set -e  # Parar em caso de erro

echo "🔨 Construindo SNE RADAR Desktop..."
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar se estamos no diretório correto
if [ ! -f "sne_desktop.py" ]; then
    echo -e "${RED}❌ Erro: sne_desktop.py não encontrado${NC}"
    echo "💡 Execute este script na raiz do projeto SNE_BACKUP_CLEAN"
    exit 1
fi

# 2. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado${NC}"
    exit 1
fi

# 3. Instalar/Verificar pywebview
echo -e "${YELLOW}📦 Verificando pywebview...${NC}"
if ! python3 -c "import webview" 2>/dev/null; then
    echo "📥 Instalando pywebview..."
    pip3 install pywebview
else
    echo -e "${GREEN}✅ pywebview já instalado${NC}"
fi

# 4. Build do frontend (OBRIGATÓRIO para o executável)
echo ""
echo -e "${YELLOW}📦 Buildando frontend Vue.js...${NC}"
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Diretório frontend não encontrado${NC}"
    exit 1
fi

cd frontend

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js/npm não encontrado!${NC}"
    echo ""
    echo "Para criar o executável, você precisa do Node.js instalado."
    echo "Mas o executável FINAL não precisará do Node.js!"
    echo ""
    echo "Instale Node.js:"
    echo "  macOS: brew install node"
    echo "  OU baixe de: https://nodejs.org/"
    echo ""
    exit 1
fi

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependências do frontend..."
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao instalar dependências do frontend${NC}"
        exit 1
    fi
fi

# Build do frontend
echo "🔨 Compilando frontend para produção..."
npm run build

if [ ! -d "dist" ] || [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ Erro: Frontend não foi buildado corretamente${NC}"
    echo "Verifique os erros acima"
    exit 1
fi

echo -e "${GREEN}✅ Frontend buildado com sucesso${NC}"
echo "📦 Frontend será incluído no executável"
cd ..

# 5. Criar diretórios necessários
echo ""
echo -e "${YELLOW}📁 Criando diretórios...${NC}"
mkdir -p data
mkdir -p logs
mkdir -p instance

# 6. Inicializar banco de dados SQLite (opcional)
echo ""
echo -e "${YELLOW}💾 Inicializando banco de dados SQLite local...${NC}"
if [ -f "inicializar_banco_python.py" ]; then
    # Forçar modo standalone para usar SQLite local
    export STANDALONE_MODE=true
    export FLASK_ENV=standalone
    export DATABASE_URL="sqlite:///$(pwd)/data/sne_radar.db"
    
    # Tentar inicializar, mas não falhar se der erro
    python3 -c "
import os
os.environ['STANDALONE_MODE'] = 'true'
os.environ['FLASK_ENV'] = 'standalone'
os.environ['DATABASE_URL'] = 'sqlite:///$(pwd)/data/sne_radar.db'

try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
        print('✅ Banco SQLite inicializado')
except Exception as e:
    print(f'⚠️ Banco já existe ou erro: {e}')
" || echo "⚠️ Banco será criado na primeira execução"
else
    echo "⚠️ Script de inicialização não encontrado, pulando..."
fi

# 7. Verificar/Instalar PyInstaller
echo ""
echo -e "${YELLOW}📦 Verificando PyInstaller...${NC}"
if ! command -v pyinstaller &> /dev/null && ! python3 -m PyInstaller --version &> /dev/null; then
    echo "📥 Instalando PyInstaller..."
    pip3 install pyinstaller
else
    echo -e "${GREEN}✅ PyInstaller já instalado${NC}"
fi

# Determinar como executar PyInstaller
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER_CMD="pyinstaller"
elif python3 -m PyInstaller --version &> /dev/null; then
    PYINSTALLER_CMD="python3 -m PyInstaller"
else
    echo -e "${RED}❌ PyInstaller não encontrado${NC}"
    echo "Tente: pip3 install pyinstaller"
    exit 1
fi

echo "🔧 Usando: $PYINSTALLER_CMD"

# 8. Detectar plataforma
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo ""
echo -e "${YELLOW}🖥️  Plataforma detectada: ${PLATFORM} ${ARCH}${NC}"

# 9. Build executável
echo ""
echo -e "${YELLOW}🔨 Criando executável...${NC}"

if [ "$PLATFORM" = "Darwin" ]; then
    # macOS
    SPEC_FILE="build_mac.spec"
    if [ ! -f "$SPEC_FILE" ]; then
        echo -e "${RED}❌ $SPEC_FILE não encontrado${NC}"
        exit 1
    fi
    
    echo "📦 Usando $SPEC_FILE para macOS..."
    $PYINSTALLER_CMD "$SPEC_FILE" --clean --noconfirm
    
    if [ -d "dist/SNE_RADAR.app" ]; then
        echo ""
        echo -e "${GREEN}✅ Build completo!${NC}"
        echo ""
        echo "📦 Aplicação criada em: dist/SNE_RADAR.app"
        echo ""
        echo "✅ O executável inclui:"
        echo "   - Backend Python completo"
        echo "   - Frontend Vue.js buildado"
        echo "   - Todas as dependências"
        echo "   - Banco SQLite (será criado na primeira execução)"
        echo ""
        echo "🚀 Para testar:"
        echo "   open dist/SNE_RADAR.app"
        echo ""
        echo "📋 Para distribuir:"
        echo "   cd dist"
        echo "   zip -r SNE_RADAR_macOS_v1.0.0.zip SNE_RADAR.app"
        echo ""
        echo "💡 O executável é STANDALONE - não precisa de:"
        echo "   ❌ Python instalado"
        echo "   ❌ Node.js instalado"
        echo "   ❌ Dependências instaladas"
        echo "   ✅ Tudo está incluído!"
    else
        echo -e "${RED}❌ Erro: SNE_RADAR.app não foi criado${NC}"
        exit 1
    fi
    
elif [ "$PLATFORM" = "Linux" ]; then
    # Linux
    echo "📦 Build para Linux..."
    $PYINSTALLER_CMD --name=SNE_RADAR \
        --onefile \
        --windowed \
        --add-data "frontend/dist:frontend/dist" \
        --add-data "data:data" \
        --hidden-import=webview \
        --hidden-import=flask \
        --hidden-import=flask_socketio \
        sne_desktop.py
    
    if [ -f "dist/SNE_RADAR" ]; then
        echo -e "${GREEN}✅ Build completo!${NC}"
        echo "📦 Executável criado em: dist/SNE_RADAR"
    else
        echo -e "${RED}❌ Erro: Executável não foi criado${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ Plataforma não suportada: $PLATFORM${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Processo concluído!${NC}"


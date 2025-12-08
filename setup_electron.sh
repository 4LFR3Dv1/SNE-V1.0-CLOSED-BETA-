#!/bin/bash
# setup_electron.sh - Configurar Electron no projeto Vue

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Configurando Electron para SNE Radar${NC}"
echo ""

# Verificar se Node.js/npm está instalado
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado!${NC}"
    echo ""
    echo "📦 Instale o Node.js primeiro:"
    echo ""
    echo "Opção 1: Via Homebrew (recomendado no macOS):"
    echo "   brew install node"
    echo ""
    echo "Opção 2: Download direto:"
    echo "   https://nodejs.org/"
    echo ""
    echo "Opção 3: Via nvm (Node Version Manager):"
    echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "   nvm install --lts"
    echo ""
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm não encontrado!${NC}"
    echo "Node.js geralmente vem com npm. Verifique sua instalação."
    exit 1
fi

echo -e "${GREEN}✅ Node.js encontrado: $(node --version)${NC}"
echo -e "${GREEN}✅ npm encontrado: $(npm --version)${NC}"
echo ""

cd frontend

# 1. Instalar dependências do Electron
echo -e "${YELLOW}📦 Instalando dependências do Electron...${NC}"
npm install --save-dev electron electron-builder
npm install --save-dev vue-cli-plugin-electron-builder
npm install --save-dev electron-devtools-installer

# 2. Verificar se arquivos necessários existem
echo -e "${YELLOW}📋 Verificando arquivos...${NC}"

if [ ! -f "src/background.js" ]; then
    echo -e "${RED}❌ src/background.js não encontrado${NC}"
    exit 1
fi

if [ ! -f "src/preload.js" ]; then
    echo -e "${RED}❌ src/preload.js não encontrado${NC}"
    exit 1
fi

# 3. Criar .env.production se não existir
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}📝 Criando .env.production...${NC}"
    cat > .env.production << EOF
# API URL para produção (Cloud Run)
VUE_APP_API_URL=https://api.sne-radar.com
EOF
    echo -e "${GREEN}✅ .env.production criado${NC}"
fi

# 4. Criar .env.development se não existir
if [ ! -f ".env.development" ]; then
    echo -e "${YELLOW}📝 Criando .env.development...${NC}"
    cat > .env.development << EOF
# API URL para desenvolvimento (local)
VUE_APP_API_URL=http://localhost:5000
EOF
    echo -e "${GREEN}✅ .env.development criado${NC}"
fi

# 5. Atualizar package.json com scripts do Electron
echo -e "${YELLOW}📝 Atualizando package.json...${NC}"

# Adicionar scripts se não existirem
if ! grep -q "electron:serve" package.json; then
    # Usar node para adicionar scripts
    node << EOF
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));

pkg.scripts = pkg.scripts || {};
pkg.scripts['electron:serve'] = 'vue-cli-service electron:serve';
pkg.scripts['electron:build'] = 'vue-cli-service electron:build';
pkg.scripts['electron:build:win'] = 'vue-cli-service electron:build --win';
pkg.scripts['electron:build:mac'] = 'vue-cli-service electron:build --mac';
pkg.scripts['electron:build:linux'] = 'vue-cli-service electron:build --linux';

fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
EOF
    echo -e "${GREEN}✅ Scripts adicionados ao package.json${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}✅ Electron configurado com sucesso!${NC}"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Desenvolvimento:"
echo "   cd frontend"
echo "   npm run electron:serve"
echo ""
echo "2. Build para produção:"
echo "   cd frontend"
echo "   npm run electron:build"
echo ""
echo "3. Build para plataforma específica:"
echo "   npm run electron:build:win   # Windows"
echo "   npm run electron:build:mac   # macOS"
echo "   npm run electron:build:linux # Linux"
echo ""


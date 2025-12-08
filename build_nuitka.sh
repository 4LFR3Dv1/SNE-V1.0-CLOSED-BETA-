#!/bin/bash
# build_nuitka.sh - Build com Nuitka para proteção de IP
# Compila Python para C++ e depois para binário nativo

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔨 Building SNE RADAR com Nuitka (Proteção de IP)${NC}"
echo ""

# 1. Verificar se Nuitka está instalado
if ! python3 -m nuitka --version &> /dev/null; then
    echo -e "${RED}❌ Nuitka não encontrado${NC}"
    echo "Instalando Nuitka..."
    pip3 install nuitka
fi

echo -e "${GREEN}✅ Nuitka encontrado${NC}"

# 2. Verificar se frontend está buildado
if [ ! -d "frontend/dist" ]; then
    echo -e "${YELLOW}⚠️  Frontend não buildado. Buildando agora...${NC}"
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Instalando dependências do frontend..."
        npm install
    fi
    npm run build
    cd ..
fi

echo -e "${GREEN}✅ Frontend buildado${NC}"

# 3. Detectar plataforma
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo ""
echo -e "${YELLOW}🖥️  Plataforma: ${PLATFORM} ${ARCH}${NC}"
echo ""

# 4. Build com Nuitka
echo -e "${YELLOW}🔨 Compilando com Nuitka...${NC}"
echo "   (Isso pode levar alguns minutos...)"

if [ "$PLATFORM" = "Darwin" ]; then
    # macOS
    # Verificar se ícone existe
    if [ -f "assets/logo_sne.icns" ]; then
        echo -e "${GREEN}✅ Ícone encontrado: assets/logo_sne.icns${NC}"
        # Build com Nuitka (com ícone)
        python3 -m nuitka \
            --standalone \
            --enable-plugin=anti-bloat \
            --enable-plugin=pywebview \
            --include-data-dir=frontend/dist=frontend/dist \
            --include-module=flask \
            --include-module=flask_socketio \
            --include-module=flask_sqlalchemy \
            --include-module=flask_login \
            --include-module=flask_limiter \
            --include-module=motor_renan \
            --include-module=contexto_global \
            --include-module=estrutura_mercado \
            --include-module=multi_timeframe \
            --include-module=confluencia \
            --include-module=fluxo_ativo \
            --include-module=catalogo_magnetico \
            --include-module=padroes_graficos \
            --include-module=indicadores \
            --include-module=indicadores_avancados \
            --include-module=analise_candles_detalhada \
            --include-module=gestao_risco_profissional \
            --include-module=relatorio_profissional \
            --include-module=calcular_suportes_resistencias \
            --include-module=niveis_operacionais \
            --include-module=database_config \
            --include-module=config \
            --include-package-data=pandas \
            --include-package-data=numpy \
            --include-package-data=matplotlib \
            --output-dir=dist \
            --output-filename=SNE_RADAR \
            --macos-create-app-bundle \
            --macos-app-name="SNE RADAR" \
            --macos-app-version="1.0.0" \
            --macos-app-icon=assets/logo_sne.icns \
            --remove-output \
            sne_desktop.py
    else
        echo -e "${YELLOW}⚠️  Ícone não encontrado (assets/logo_sne.icns) - usando padrão${NC}"
        # Build com Nuitka (sem ícone)
        python3 -m nuitka \
            --standalone \
            --enable-plugin=anti-bloat \
            --enable-plugin=pywebview \
            --include-data-dir=frontend/dist=frontend/dist \
            --include-module=flask \
            --include-module=flask_socketio \
            --include-module=flask_sqlalchemy \
            --include-module=flask_login \
            --include-module=flask_limiter \
            --include-module=motor_renan \
            --include-module=contexto_global \
            --include-module=estrutura_mercado \
            --include-module=multi_timeframe \
            --include-module=confluencia \
            --include-module=fluxo_ativo \
            --include-module=catalogo_magnetico \
            --include-module=padroes_graficos \
            --include-module=indicadores \
            --include-module=indicadores_avancados \
            --include-module=analise_candles_detalhada \
            --include-module=gestao_risco_profissional \
            --include-module=relatorio_profissional \
            --include-module=calcular_suportes_resistencias \
            --include-module=niveis_operacionais \
            --include-module=database_config \
            --include-module=config \
            --include-package-data=pandas \
            --include-package-data=numpy \
            --include-package-data=matplotlib \
            --output-dir=dist \
            --output-filename=SNE_RADAR \
            --macos-create-app-bundle \
            --macos-app-name="SNE RADAR" \
            --macos-app-version="1.0.0" \
            --remove-output \
            sne_desktop.py
    fi

    # Nuitka cria o app com o nome do arquivo Python (sne_desktop.app)
    # Precisamos renomear para SNE_RADAR.app
    if [ -d "dist/sne_desktop.app" ]; then
        echo ""
        echo -e "${GREEN}✅ Build completo!${NC}"
        
        # Remover app antigo se existir
        if [ -d "dist/SNE_RADAR.app" ]; then
            echo -e "${YELLOW}🗑️  Removendo app antigo...${NC}"
            rm -rf "dist/SNE_RADAR.app"
        fi
        
        # Renomear app
        echo -e "${YELLOW}📝 Renomeando app para SNE_RADAR.app...${NC}"
        mv "dist/sne_desktop.app" "dist/SNE_RADAR.app"
        
        # Configurar bundle identifier no Info.plist
        INFO_PLIST="dist/SNE_RADAR.app/Contents/Info.plist"
        if [ -f "$INFO_PLIST" ]; then
            echo -e "${YELLOW}🔧 Configurando Info.plist...${NC}"
            # Adicionar bundle identifier se não existir
            if ! grep -q "CFBundleIdentifier" "$INFO_PLIST"; then
                # Usar plutil para adicionar (macOS nativo)
                if command -v plutil &> /dev/null; then
                    plutil -insert CFBundleIdentifier -string "com.sne.radar" "$INFO_PLIST" 2>/dev/null || true
                    echo -e "${GREEN}✅ Bundle identifier configurado${NC}"
                fi
            fi
        fi
        
        # Verificar se executável existe e dar permissão
        EXECUTABLE="dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR"
        if [ -f "$EXECUTABLE" ]; then
            chmod +x "$EXECUTABLE"
            echo -e "${GREEN}✅ Permissões de execução configuradas${NC}"
        fi
        
        echo ""
        echo "📦 Aplicação criada em: dist/SNE_RADAR.app"
        echo ""
        echo "🔐 Proteção de IP:"
        echo "   ✅ Código compilado para C++"
        echo "   ✅ Muito mais difícil de engenharia reversa"
        echo "   ✅ Binário nativo (não Python bytecode)"
        echo ""
        echo "🚀 Para testar:"
        echo "   open dist/SNE_RADAR.app"
    elif [ -d "dist/SNE_RADAR.app" ]; then
        # Se já existe com o nome correto
        echo ""
        echo -e "${GREEN}✅ Build completo!${NC}"
        echo "📦 Aplicação encontrada em: dist/SNE_RADAR.app"
    else
        echo -e "${RED}❌ Erro: App não foi criado${NC}"
        echo "Procurando em dist/:"
        ls -la dist/ | grep -E "\.app|\.dist"
        exit 1
    fi

elif [ "$PLATFORM" = "Linux" ]; then
    # Linux
    python3 -m nuitka \
        --standalone \
        --enable-plugin=anti-bloat \
        --enable-plugin=pywebview \
        --include-data-dir=frontend/dist=frontend/dist \
        --include-module=flask \
        --include-module=flask_socketio \
        --include-module=flask_sqlalchemy \
        --include-module=motor_renan \
        --output-dir=dist \
        --output-filename=SNE_RADAR \
        --remove-output \
        sne_desktop.py

    if [ -f "dist/SNE_RADAR.bin" ]; then
        echo ""
        echo -e "${GREEN}✅ Build completo!${NC}"
        echo "📦 Executável em: dist/SNE_RADAR.bin"
    else
        echo -e "${RED}❌ Erro: Executável não foi criado${NC}"
        exit 1
    fi

else
    echo -e "${RED}❌ Plataforma não suportada: ${PLATFORM}${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Build com Nuitka concluído!${NC}"



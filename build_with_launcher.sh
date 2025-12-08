#!/bin/bash
# Build com launcher wrapper para garantir duplo clique

set -e

echo "🔨 Construindo SNE RADAR com launcher wrapper..."
echo ""

# Verificar se launcher.sh existe
if [ ! -f "launcher.sh" ]; then
    echo "❌ launcher.sh não encontrado!"
    exit 1
fi

# Dar permissão de execução ao launcher
chmod +x launcher.sh

# Usar spec com launcher
SPEC_FILE="build_mac_with_launcher.spec"

if [ ! -f "$SPEC_FILE" ]; then
    echo "❌ $SPEC_FILE não encontrado!"
    exit 1
fi

# Build normal primeiro (frontend, etc)
echo "📦 Buildando frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..

# Build do executável com launcher
echo "🔨 Criando executável com launcher..."
python3 -m PyInstaller "$SPEC_FILE" --clean --noconfirm

# Pós-processamento: configurar launcher como executável principal
echo "🔧 Configurando launcher como executável principal..."
APP_MACOS="dist/SNE_RADAR.app/Contents/MacOS"
APP_BUNDLE="dist/SNE_RADAR.app"

if [ -d "$APP_MACOS" ]; then
    # 1. Renomear o executável Python para SNE_RADAR_bin
    if [ -f "$APP_MACOS/SNE_RADAR" ]; then
        mv "$APP_MACOS/SNE_RADAR" "$APP_MACOS/SNE_RADAR_bin"
        echo "✅ Executável Python renomeado para SNE_RADAR_bin"
    fi
    
    # 2. Copiar launcher.sh como executável principal
    cp launcher.sh "$APP_MACOS/launcher.sh"
    chmod +x "$APP_MACOS/launcher.sh"
    
    # 3. Criar link simbólico ou renomear (macOS prefere sem extensão)
    # Na verdade, vamos renomear o launcher para o nome do executável
    mv "$APP_MACOS/launcher.sh" "$APP_MACOS/SNE_RADAR"
    chmod +x "$APP_MACOS/SNE_RADAR"
    echo "✅ Launcher configurado como executável principal"
    
    # 4. Atualizar Info.plist para apontar para SNE_RADAR (que agora é o launcher)
    INFO_PLIST="$APP_BUNDLE/Contents/Info.plist"
    if [ -f "$INFO_PLIST" ]; then
        # O Info.plist já deve estar correto (CFBundleExecutable = SNE_RADAR)
        # Mas vamos garantir
        if ! grep -q "<string>SNE_RADAR</string>" "$INFO_PLIST"; then
            echo "⚠️ Ajustando Info.plist..."
            # Substituir o valor de CFBundleExecutable
            /usr/bin/sed -i '' 's/<key>CFBundleExecutable<\/key>.*/<key>CFBundleExecutable<\/key>\n\t<string>SNE_RADAR<\/string>/' "$INFO_PLIST" 2>/dev/null || {
                # Fallback: usar Python
                /usr/bin/plutil -replace CFBundleExecutable -string "SNE_RADAR" "$INFO_PLIST" 2>/dev/null || echo "⚠️ Não foi possível ajustar Info.plist automaticamente"
            }
        fi
        echo "✅ Info.plist verificado"
    fi
    
    # 5. Verificar estrutura final
    echo ""
    echo "📋 Estrutura final:"
    echo "   $APP_MACOS/SNE_RADAR (launcher wrapper)"
    echo "   $APP_MACOS/SNE_RADAR_bin (executável Python)"
    ls -lh "$APP_MACOS" | grep -E "(SNE_RADAR|launcher)" || true
fi

# Remover quarentena
echo "🔓 Removendo quarentena do macOS..."
xattr -dr com.apple.quarantine dist/SNE_RADAR.app 2>/dev/null || true

echo ""
echo "✅ Build completo com launcher!"
echo ""
echo "📦 App criado em: dist/SNE_RADAR.app"
echo ""
echo "🚀 Agora você pode:"
echo "   1. Clicar duas vezes no app (deve funcionar!)"
echo "   2. Ou executar: open dist/SNE_RADAR.app"
echo ""
echo "💡 O launcher garante execução correta mesmo com duplo clique"


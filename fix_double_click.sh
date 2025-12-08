#!/bin/bash
# Script para fazer o app abrir com duplo clique

APP_PATH="dist/SNE_RADAR.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App não encontrado em: $APP_PATH"
    echo "💡 Execute primeiro: ./build_standalone.sh"
    exit 1
fi

echo "🔧 Configurando app para abrir com duplo clique..."
echo ""

# 1. Remover quarentena do macOS
echo "1️⃣ Removendo quarentena do macOS..."
xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Quarentena removida"
else
    echo "   ⚠️ Não havia quarentena (ou não foi possível remover)"
fi

# 2. Dar permissões de execução
echo "2️⃣ Configurando permissões..."
chmod +x "$APP_PATH/Contents/MacOS/SNE_RADAR"
chmod -R u+r "$APP_PATH"
echo "   ✅ Permissões configuradas"

# 3. Verificar Info.plist
echo "3️⃣ Verificando configurações do app..."
if [ -f "$APP_PATH/Contents/Info.plist" ]; then
    echo "   ✅ Info.plist encontrado"
    
    # Verificar se tem LSUIElement
    if grep -q "LSUIElement" "$APP_PATH/Contents/Info.plist"; then
        echo "   ✅ LSUIElement configurado"
    fi
else
    echo "   ⚠️ Info.plist não encontrado"
fi

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Tente abrir com duplo clique agora"
echo ""
echo "2. Se ainda não abrir, clique com BOTÃO DIREITO > Abrir"
echo "   (primeira vez que o macOS bloqueia apps não assinados)"
echo ""
echo "3. Ou execute via terminal:"
echo "   open '$APP_PATH'"
echo ""
echo "4. Ou arraste para a pasta Applications e abra de lá"
echo ""
echo "💡 O app funciona perfeitamente via terminal:"
echo "   ./dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR"



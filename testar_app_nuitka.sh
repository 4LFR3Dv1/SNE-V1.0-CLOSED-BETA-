#!/bin/bash
# Script para testar o app buildado com Nuitka

set -e

APP_PATH="dist/SNE_RADAR.app"

if [ ! -d "$APP_PATH" ]; then
    # Tentar com o nome que o Nuitka cria
    if [ -d "dist/sne_desktop.app" ]; then
        APP_PATH="dist/sne_desktop.app"
        echo "⚠️  Usando: $APP_PATH"
    else
        echo "❌ App não encontrado!"
        exit 1
    fi
fi

echo "🔍 Verificando app: $APP_PATH"
echo ""

# Verificar estrutura
echo "📁 Estrutura do app:"
ls -la "$APP_PATH/Contents/" 2>/dev/null || echo "❌ Estrutura inválida"
echo ""

# Verificar executável
EXECUTABLE="$APP_PATH/Contents/MacOS/SNE_RADAR"
if [ -f "$EXECUTABLE" ]; then
    echo "✅ Executável encontrado: $EXECUTABLE"
    echo "   Tamanho: $(du -h "$EXECUTABLE" | cut -f1)"
    echo "   Tipo: $(file "$EXECUTABLE" | cut -d: -f2)"
    echo ""
    
    # Verificar permissões
    if [ -x "$EXECUTABLE" ]; then
        echo "✅ Permissões de execução OK"
    else
        echo "⚠️  Adicionando permissões de execução..."
        chmod +x "$EXECUTABLE"
    fi
else
    echo "❌ Executável não encontrado!"
    echo "Arquivos em MacOS/:"
    ls -la "$APP_PATH/Contents/MacOS/" 2>/dev/null || echo "Diretório não existe"
    exit 1
fi

# Verificar Info.plist
INFO_PLIST="$APP_PATH/Contents/Info.plist"
if [ -f "$INFO_PLIST" ]; then
    echo "✅ Info.plist encontrado"
    echo ""
    echo "📋 Informações do app:"
    if command -v plutil &> /dev/null; then
        plutil -p "$INFO_PLIST" | grep -E "CFBundleName|CFBundleExecutable|CFBundleIdentifier" || true
    fi
else
    echo "⚠️  Info.plist não encontrado"
fi

echo ""
echo "🚀 Tentando abrir o app..."
echo ""

# Tentar abrir
open "$APP_PATH" 2>&1 || {
    echo "❌ Erro ao abrir com 'open'"
    echo ""
    echo "💡 Tentando executar diretamente:"
    "$EXECUTABLE" 2>&1 | head -20 || echo "Erro ao executar"
}

echo ""
echo "✅ Teste concluído!"


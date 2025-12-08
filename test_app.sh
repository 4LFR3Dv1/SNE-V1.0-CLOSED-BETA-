#!/bin/bash
# Script para testar o app e ver os logs

echo "🧪 Testando SNE_RADAR.app..."
echo ""

APP_PATH="dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR"

if [ ! -f "$APP_PATH" ]; then
    echo "❌ App não encontrado em: $APP_PATH"
    echo "💡 Execute primeiro: ./build_standalone.sh"
    exit 1
fi

echo "🚀 Executando app e mostrando logs..."
echo "💡 Pressione Ctrl+C para parar"
echo ""

# Executar e mostrar output
"$APP_PATH" 2>&1



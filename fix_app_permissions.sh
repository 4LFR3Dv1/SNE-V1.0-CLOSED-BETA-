#!/bin/bash
# Script para corrigir permissões do app macOS

APP_PATH="dist/SNE_RADAR.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App não encontrado em: $APP_PATH"
    exit 1
fi

echo "🔧 Corrigindo permissões do app..."

# Remover quarentena do macOS (Gatekeeper)
xattr -dr com.apple.quarantine "$APP_PATH" 2>/dev/null || echo "⚠️ Não foi possível remover quarentena (pode não estar em quarentena)"

# Dar permissões de execução
chmod +x "$APP_PATH/Contents/MacOS/SNE_RADAR"

# Dar permissões de leitura para todos os arquivos
chmod -R u+r "$APP_PATH"

echo "✅ Permissões corrigidas!"
echo ""
echo "💡 Se ainda não abrir, tente:"
echo "   1. Clicar com botão direito > Abrir (primeira vez)"
echo "   2. Ou executar: open -a '$APP_PATH'"
echo "   3. Ou verificar logs: ~/Library/Application Support/SNE_RADAR/logs/"



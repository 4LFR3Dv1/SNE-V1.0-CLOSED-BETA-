#!/bin/bash
# Script para testar app quando aberto diretamente

echo "🧪 Testando app quando executado diretamente..."
echo ""

APP_PATH="/Users/renan/Desktop/SNE_BACKUP_CLEAN/dist/SNE_RADAR.app"
EXECUTABLE="$APP_PATH/Contents/MacOS/SNE_RADAR"

if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ Executável não encontrado: $EXECUTABLE"
    exit 1
fi

echo "✅ Executável encontrado"
echo ""

# Criar diretório de logs se não existir
LOG_DIR="$HOME/Library/Application Support/SNE_RADAR/logs"
mkdir -p "$LOG_DIR"

# Executar app e capturar output
echo "🚀 Executando app..."
echo "📝 Output será salvo em: $LOG_DIR/test_output.log"
echo ""

# Executar em background e capturar output
"$EXECUTABLE" > "$LOG_DIR/test_output.log" 2>&1 &
APP_PID=$!

echo "📌 PID do app: $APP_PID"
echo "⏳ Aguardando 5 segundos..."
sleep 5

# Verificar se ainda está rodando
if ps -p $APP_PID > /dev/null 2>&1; then
    echo "✅ App ainda está rodando (PID: $APP_PID)"
    echo "💡 Para parar: kill $APP_PID"
else
    echo "❌ App parou/fechou"
    echo ""
    echo "📋 Últimas linhas do log:"
    tail -30 "$LOG_DIR/test_output.log"
fi

echo ""
echo "📝 Log completo em: $LOG_DIR/test_output.log"




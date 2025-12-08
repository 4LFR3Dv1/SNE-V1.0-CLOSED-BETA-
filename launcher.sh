#!/bin/bash
# Launcher wrapper para SNE_RADAR.app
# Este script garante que o app funcione corretamente quando aberto com duplo clique

# Obter diretório do app
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_BUNDLE="$(cd "$APP_DIR/../.." && pwd)"

# O executável Python foi renomeado para SNE_RADAR_bin
EXECUTABLE="$APP_DIR/SNE_RADAR_bin"

# Se não encontrar, tentar o nome original
if [ ! -f "$EXECUTABLE" ]; then
    EXECUTABLE="$APP_DIR/SNE_RADAR"
fi

# Log para debug (opcional - remover em produção)
LOG_FILE="$HOME/Library/Application Support/SNE_RADAR/logs/launcher.log"
mkdir -p "$(dirname "$LOG_FILE")"
echo "$(date): Launcher iniciado" >> "$LOG_FILE"
echo "APP_DIR: $APP_DIR" >> "$LOG_FILE"
echo "APP_BUNDLE: $APP_BUNDLE" >> "$LOG_FILE"
echo "EXECUTABLE: $EXECUTABLE" >> "$LOG_FILE"

# Verificar se o executável existe
if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ Executável não encontrado: $EXECUTABLE" >> "$LOG_FILE"
    
    # Mostrar diálogo de erro (macOS)
    osascript -e 'display dialog "Erro: Executável não encontrado.\n\nVerifique se o app está completo." buttons {"OK"} default button 1 with icon stop' 2>/dev/null
    
    exit 1
fi

# Dar permissão de execução (garantir)
chmod +x "$EXECUTABLE" 2>/dev/null

# Configurar variáveis de ambiente
export PYTHONUNBUFFERED=1
export SNE_RADAR_APP_BUNDLE="$APP_BUNDLE"

# Mudar para o diretório do executável
cd "$APP_DIR"

# Executar o app
echo "$(date): Executando: $EXECUTABLE" >> "$LOG_FILE"

# Executar e capturar código de saída
"$EXECUTABLE" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

echo "$(date): App encerrado com código: $EXIT_CODE" >> "$LOG_FILE"

# Se houver erro, mostrar diálogo
if [ $EXIT_CODE -ne 0 ] && [ $EXIT_CODE -ne 130 ]; then  # 130 = Ctrl+C
    osascript -e "display dialog \"O app encerrou com erro (código: $EXIT_CODE).\n\nVerifique os logs em:\n$LOG_FILE\" buttons {\"OK\"} default button 1 with icon caution" 2>/dev/null
fi

exit $EXIT_CODE


#!/bin/bash
# Script para extrair secrets dos arquivos do sistema e atualizar no GCP

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID=${1:-"sne-v1"}

echo "🔍 Extraindo secrets dos arquivos do sistema..."
echo "Projeto: $PROJECT_ID"
echo ""

# Extrair Telegram Token do xenos_bot.py
echo "📝 Extraindo Telegram Bot Token..."
TELEGRAM_TOKEN=$(grep -oP 'TELEGRAM_TOKEN\s*=\s*"[^"]+"' xenos_bot.py 2>/dev/null | head -1 | sed 's/.*"\(.*\)"/\1/' || \
                 grep -oP 'TELEGRAM_TOKEN\s*=\s*[^"]+' config_seguro.py 2>/dev/null | head -1 | sed 's/.*=\s*//' || \
                 echo "")

if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "⚠️  Telegram Token não encontrado nos arquivos"
    echo -n "Digite o Telegram Bot Token: "
    read TELEGRAM_TOKEN
fi

# Extrair Chat ID
echo "📝 Extraindo Telegram Chat ID..."
CHAT_ID=$(grep -oP 'CHAT_ID\s*=\s*"[^"]+"' xenos_bot.py 2>/dev/null | head -1 | sed 's/.*"\(.*\)"/\1/' || \
          grep -oP 'TELEGRAM_CHAT_ID\s*=\s*[^"]+' config_seguro.py 2>/dev/null | head -1 | sed 's/.*=\s*//' || \
          echo "")

if [ -z "$CHAT_ID" ]; then
    echo "⚠️  Chat ID não encontrado nos arquivos"
    echo -n "Digite o Telegram Chat ID: "
    read CHAT_ID
fi

# Extrair Binance API Key
echo "📝 Extraindo Binance API Key..."
BINANCE_API_KEY=$(grep -i "BINANCE.*API.*KEY\|API.*KEY.*BINANCE" config*.py 2>/dev/null | head -1 | sed 's/.*=\s*["'\'']\(.*\)["'\'']/\1/' | sed 's/.*=\s*//' | tr -d ' ' || \
                  grep -i "binance.*api.*key" *.py 2>/dev/null | head -1 | sed 's/.*=\s*["'\'']\(.*\)["'\'']/\1/' || \
                  echo "")

if [ -z "$BINANCE_API_KEY" ]; then
    echo "⚠️  Binance API Key não encontrada nos arquivos"
    echo -n "Digite o Binance API Key (ou Enter para pular): "
    read BINANCE_API_KEY
fi

# Extrair Binance Secret Key
echo "📝 Extraindo Binance Secret Key..."
BINANCE_SECRET_KEY=$(grep -i "BINANCE.*SECRET\|SECRET.*BINANCE" config*.py 2>/dev/null | head -1 | sed 's/.*=\s*["'\'']\(.*\)["'\'']/\1/' | sed 's/.*=\s*//' | tr -d ' ' || \
                     grep -i "binance.*secret" *.py 2>/dev/null | head -1 | sed 's/.*=\s*["'\'']\(.*\)["'\'']/\1/' || \
                     echo "")

if [ -z "$BINANCE_SECRET_KEY" ]; then
    echo "⚠️  Binance Secret Key não encontrada nos arquivos"
    echo -n "Digite o Binance Secret Key (ou Enter para pular): "
    read -s BINANCE_SECRET_KEY
    echo ""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Secrets encontrados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Telegram Token: ${TELEGRAM_TOKEN:0:20}..."
echo "Chat ID: $CHAT_ID"
if [ -n "$BINANCE_API_KEY" ]; then
    echo "Binance API Key: ${BINANCE_API_KEY:0:20}..."
fi
if [ -n "$BINANCE_SECRET_KEY" ]; then
    echo "Binance Secret Key: ${BINANCE_SECRET_KEY:0:20}..."
fi
echo ""

read -p "Deseja atualizar esses secrets no GCP? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Cancelado."
    exit 0
fi

# Atualizar Telegram Token
if [ -n "$TELEGRAM_TOKEN" ]; then
    echo ""
    echo "📤 Atualizando Telegram Bot Token..."
    echo -n "$TELEGRAM_TOKEN" | gcloud secrets versions add sne-telegram-bot-token \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro, tentando novamente..."
        echo -n "$TELEGRAM_TOKEN" | gcloud secrets versions add sne-telegram-bot-token \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Telegram Bot Token atualizado"
fi

# Atualizar Chat ID
if [ -n "$CHAT_ID" ]; then
    echo "📤 Atualizando Telegram Chat ID..."
    echo -n "$CHAT_ID" | gcloud secrets versions add sne-telegram-chat-id \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro, tentando novamente..."
        echo -n "$CHAT_ID" | gcloud secrets versions add sne-telegram-chat-id \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Telegram Chat ID atualizado"
fi

# Atualizar Binance API Key
if [ -n "$BINANCE_API_KEY" ]; then
    echo "📤 Atualizando Binance API Key..."
    echo -n "$BINANCE_API_KEY" | gcloud secrets versions add sne-binance-api-key \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro, tentando novamente..."
        echo -n "$BINANCE_API_KEY" | gcloud secrets versions add sne-binance-api-key \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Binance API Key atualizada"
fi

# Atualizar Binance Secret Key
if [ -n "$BINANCE_SECRET_KEY" ]; then
    echo "📤 Atualizando Binance Secret Key..."
    echo -n "$BINANCE_SECRET_KEY" | gcloud secrets versions add sne-binance-secret-key \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro, tentando novamente..."
        echo -n "$BINANCE_SECRET_KEY" | gcloud secrets versions add sne-binance-secret-key \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Binance Secret Key atualizada"
fi

echo ""
echo "✅ Todos os secrets foram atualizados!"
echo ""
echo "📋 Verificar:"
echo "  gcloud secrets list --project=$PROJECT_ID"




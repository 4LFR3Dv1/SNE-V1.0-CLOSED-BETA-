#!/bin/bash
# Script rápido para atualizar secrets (valores via argumentos)

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID=${1:-"sne-v1"}
TELEGRAM_TOKEN=${2:-""}
TELEGRAM_CHAT_ID=${3:-""}
BINANCE_API_KEY=${4:-""}
BINANCE_SECRET_KEY=${5:-""}

echo "🔐 Atualizando Secrets - SNE 1.0 Cloud"
echo "Projeto: $PROJECT_ID"
echo ""

# Telegram Bot Token
if [ -n "$TELEGRAM_TOKEN" ]; then
    echo "📝 Atualizando Telegram Bot Token..."
    echo -n "$TELEGRAM_TOKEN" | gcloud secrets versions add sne-telegram-bot-token \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro ao atualizar, tentando novamente..."
        echo -n "$TELEGRAM_TOKEN" | gcloud secrets versions add sne-telegram-bot-token \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Telegram Bot Token atualizado"
fi

# Telegram Chat ID
if [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "📝 Atualizando Telegram Chat ID..."
    echo -n "$TELEGRAM_CHAT_ID" | gcloud secrets versions add sne-telegram-chat-id \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro ao atualizar, tentando novamente..."
        echo -n "$TELEGRAM_CHAT_ID" | gcloud secrets versions add sne-telegram-chat-id \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Telegram Chat ID atualizado"
fi

# Binance API Key
if [ -n "$BINANCE_API_KEY" ]; then
    echo "📝 Atualizando Binance API Key..."
    echo -n "$BINANCE_API_KEY" | gcloud secrets versions add sne-binance-api-key \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro ao atualizar, tentando novamente..."
        echo -n "$BINANCE_API_KEY" | gcloud secrets versions add sne-binance-api-key \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Binance API Key atualizado"
fi

# Binance Secret Key
if [ -n "$BINANCE_SECRET_KEY" ]; then
    echo "📝 Atualizando Binance Secret Key..."
    echo -n "$BINANCE_SECRET_KEY" | gcloud secrets versions add sne-binance-secret-key \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro ao atualizar, tentando novamente..."
        echo -n "$BINANCE_SECRET_KEY" | gcloud secrets versions add sne-binance-secret-key \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    echo "✅ Binance Secret Key atualizado"
fi

echo ""
echo "✅ Atualização concluída!"
echo ""
echo "📋 Uso:"
echo "  ./atualizar_secrets_rapido.sh sne-v1 TELEGRAM_TOKEN TELEGRAM_CHAT_ID BINANCE_API_KEY BINANCE_SECRET_KEY"
echo ""
echo "📋 Verificar:"
echo "  gcloud secrets list --project=$PROJECT_ID"




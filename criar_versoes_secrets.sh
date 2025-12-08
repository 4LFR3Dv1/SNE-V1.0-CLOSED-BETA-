#!/bin/bash
# Script para criar versões dos secrets após terraform apply

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

echo "🔧 Criando versões dos secrets..."
echo ""

# Gerar secret key
SECRET_KEY=$(openssl rand -base64 32)
echo "✅ Secret key gerado"

# Criar versões dos secrets
echo "📝 Criando versões..."

# Secret key
echo -n "$SECRET_KEY" | gcloud secrets versions add sne-secret-key --data-file=- 2>/dev/null || {
    echo "⚠️  Versão já existe, adicionando nova..."
    echo -n "$SECRET_KEY" | gcloud secrets versions add sne-secret-key --data-file=-
}

# Telegram (placeholders temporários)
echo -n "TEMPORARY_PLACEHOLDER_UPDATE_AFTER_DEPLOY" | gcloud secrets versions add sne-telegram-bot-token --data-file=- 2>/dev/null || {
    echo "⚠️  Versão já existe, adicionando nova..."
    echo -n "TEMPORARY_PLACEHOLDER_UPDATE_AFTER_DEPLOY" | gcloud secrets versions add sne-telegram-bot-token --data-file=-
}

echo -n "TEMPORARY_PLACEHOLDER_UPDATE_AFTER_DEPLOY" | gcloud secrets versions add sne-telegram-chat-id --data-file=- 2>/dev/null || {
    echo "⚠️  Versão já existe, adicionando nova..."
    echo -n "TEMPORARY_PLACEHOLDER_UPDATE_AFTER_DEPLOY" | gcloud secrets versions add sne-telegram-chat-id --data-file=-
}

echo ""
echo "✅ Versões dos secrets criadas!"
echo ""
echo "📋 Próximos passos:"
echo "1. Execute: cd infra/terraform && terraform apply"
echo "2. Depois atualize os secrets com valores reais:"
echo "   echo -n 'SEU_TOKEN' | gcloud secrets versions add sne-telegram-bot-token --data-file=-"
echo "   echo -n 'SEU_CHAT_ID' | gcloud secrets versions add sne-telegram-chat-id --data-file=-"




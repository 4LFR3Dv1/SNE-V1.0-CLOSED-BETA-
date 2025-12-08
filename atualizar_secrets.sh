#!/bin/bash
# Script para atualizar secrets do SNE 1.0 Cloud

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID=${1:-"sne-v1"}

echo "🔐 Atualizando Secrets - SNE 1.0 Cloud"
echo "Projeto: $PROJECT_ID"
echo ""

# Verificar se gcloud está configurado
if ! gcloud config get-value project &>/dev/null; then
    echo "❌ gcloud não está configurado. Execute: gcloud init"
    exit 1
fi

# Função para atualizar secret
update_secret() {
    local secret_name=$1
    local description=$2
    local is_sensitive=${3:-true}
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📝 $description"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ "$is_sensitive" = "true" ]; then
        echo -n "Digite o valor (não será exibido): "
        read -s value
        echo ""
    else
        echo -n "Digite o valor: "
        read value
    fi
    
    if [ -z "$value" ]; then
        echo "⚠️  Valor vazio, pulando..."
        return
    fi
    
    echo -n "$value" | gcloud secrets versions add "$secret_name" \
        --data-file=- \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Erro ao atualizar secret. Tentando criar nova versão..."
        echo -n "$value" | gcloud secrets versions add "$secret_name" \
            --data-file=- \
            --project="$PROJECT_ID"
    }
    
    echo "✅ Secret atualizado com sucesso!"
}

# Menu interativo
echo "Selecione quais secrets atualizar:"
echo ""
echo "1) Telegram Bot Token"
echo "2) Telegram Chat ID"
echo "3) Binance API Key"
echo "4) Binance Secret Key"
echo "5) Todos os acima"
echo "6) Sair"
echo ""
read -p "Escolha uma opção (1-6): " choice

case $choice in
    1)
        update_secret "sne-telegram-bot-token" "Telegram Bot Token"
        ;;
    2)
        update_secret "sne-telegram-chat-id" "Telegram Chat ID" false
        ;;
    3)
        update_secret "sne-binance-api-key" "Binance API Key"
        ;;
    4)
        update_secret "sne-binance-secret-key" "Binance Secret Key"
        ;;
    5)
        update_secret "sne-telegram-bot-token" "Telegram Bot Token"
        update_secret "sne-telegram-chat-id" "Telegram Chat ID" false
        update_secret "sne-binance-api-key" "Binance API Key"
        update_secret "sne-binance-secret-key" "Binance Secret Key"
        ;;
    6)
        echo "Saindo..."
        exit 0
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "✅ Atualização de secrets concluída!"
echo ""
echo "📋 Verificar secrets:"
echo "  gcloud secrets list --project=$PROJECT_ID"
echo ""
echo "📋 Ver versões de um secret:"
echo "  gcloud secrets versions list sne-telegram-bot-token --project=$PROJECT_ID"




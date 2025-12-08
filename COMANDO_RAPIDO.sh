#!/bin/bash
# Comando rápido: Iniciar Docker + Build + Deploy

echo "🚀 SNE 1.0 Cloud - Build e Deploy Completo"
echo ""

# 1. Iniciar Docker
echo "🐳 Iniciando Docker Desktop..."
open -a Docker
echo "⏳ Aguardando Docker iniciar (30 segundos)..."
sleep 30

# 2. Verificar Docker
echo "🔍 Verificando Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker ainda não está rodando!"
    echo "   Por favor, inicie o Docker Desktop manualmente e aguarde"
    exit 1
fi
echo "✅ Docker está rodando!"

# 3. Navegar para diretório correto
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
echo "📁 Diretório: $(pwd)"

# 4. Build e push
echo ""
echo "📦 Buildando e pushando imagens..."
./build_imagens.sh sne-v1 us-central1

# 5. Deploy
echo ""
echo "🚀 Fazendo deploy dos serviços..."
./deploy/deploy_all.sh sne-v1 us-central1

echo ""
echo "🎉 Tudo pronto!"




#!/bin/bash
# Habilitar APIs necessárias para o SNE Cloud

set -e

export PATH="$HOME/google-cloud-sdk/bin:$PATH"

PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Erro: Projeto não especificado"
    echo "Uso: ./habilitar_apis.sh [PROJECT_ID]"
    exit 1
fi

echo "🔧 Habilitando APIs no projeto: $PROJECT_ID"
echo ""

gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage-api.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  vpcaccess.googleapis.com \
  servicenetworking.googleapis.com \
  compute.googleapis.com \
  --project=$PROJECT_ID

echo ""
echo "✅ APIs habilitadas com sucesso!"
echo ""
echo "⏳ Aguardando propagação (10 segundos)..."
sleep 10

echo ""
echo "📋 Verificando APIs habilitadas..."
gcloud services list --enabled --project=$PROJECT_ID | grep -E "(run|sql|secret|scheduler|artifact|build|vpc)" || echo "Algumas APIs podem ainda estar sendo habilitadas"




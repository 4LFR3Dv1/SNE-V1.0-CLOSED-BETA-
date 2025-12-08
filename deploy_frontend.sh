#!/bin/bash

set -e

PROJECT_ID="sne-v1"
REGION="europe-west1"
SERVICE_NAME="sne-web"

echo "🔨 Building frontend..."
cd frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Build
echo "🏗️ Building..."
npm run build

# Verificar build
if [ ! -f "dist/index.html" ]; then
  echo "❌ Build failed! dist/index.html not found"
  exit 1
fi

echo "✅ Frontend built successfully"
cd ..

echo "📦 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --port 9999

echo "✅ Deploy complete!"


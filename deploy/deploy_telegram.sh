#!/bin/bash
set -e

# Deploy sne-telegram service
# Usage: ./deploy_telegram.sh [project-id] [region]

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT:-"your-project-id"}}
REGION=${2:-"us-central1"}
IMAGE_TAG=${3:-"latest"}

echo "🚀 Deploying sne-telegram to $PROJECT_ID/$REGION"

gcloud run deploy sne-telegram \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/sne-artifacts/sne-telegram:${IMAGE_TAG} \
  --region $REGION \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account sa-sne-telegram@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-secrets TELEGRAM_BOT_TOKEN=sne-telegram-bot-token:latest,TELEGRAM_CHAT_ID=sne-telegram-chat-id:latest,SECRET_KEY=sne-secret-key:latest \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80

echo "✅ sne-telegram deployed successfully!"




#!/bin/bash
set -e

# Deploy sne-worker service
# Usage: ./deploy_worker.sh [project-id] [region]

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT:-"your-project-id"}}
REGION=${2:-"us-central1"}
IMAGE_TAG=${3:-"latest"}

echo "🚀 Deploying sne-worker to $PROJECT_ID/$REGION"

gcloud run deploy sne-worker \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/sne-artifacts/sne-worker:${IMAGE_TAG} \
  --region $REGION \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account sa-sne-worker@${PROJECT_ID}.iam.gserviceaccount.com \
  --vpc-connector sne-vpc-connector \
  --set-env-vars DATABASE_URL="postgresql://sne_admin:$(gcloud secrets versions access latest --secret=sne-db-password)@/sne?host=/cloudsql/${PROJECT_ID}:${REGION}:sne-db-prod" \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 1

echo "✅ sne-worker deployed successfully!"




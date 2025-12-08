#!/bin/bash
set -e

# Deploy sne-web service
# Usage: ./deploy_web.sh [project-id] [region]

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT:-"your-project-id"}}
REGION=${2:-"us-central1"}
IMAGE_TAG=${3:-"latest"}

echo "🚀 Deploying sne-web to $PROJECT_ID/$REGION"

gcloud run deploy sne-web \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/sne-artifacts/sne-web:${IMAGE_TAG} \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --service-account sa-sne-web@${PROJECT_ID}.iam.gserviceaccount.com \
  --vpc-connector sne-vpc-connector \
  --set-env-vars DATABASE_URL="postgresql://sne_admin:$(gcloud secrets versions access latest --secret=sne-db-password)@/sne?host=/cloudsql/${PROJECT_ID}:${REGION}:sne-db-prod" \
  --set-secrets SECRET_KEY=sne-secret-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80

echo "✅ sne-web deployed successfully!"




#!/bin/bash
set -e

# Deploy all SNE services
# Usage: ./deploy_all.sh [project-id] [region]

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT:-"your-project-id"}}
REGION=${2:-"us-central1"}

echo "🚀 Deploying all SNE services to project: $PROJECT_ID, region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Deploy each service
./deploy_web.sh $PROJECT_ID $REGION
./deploy_worker.sh $PROJECT_ID $REGION
./deploy_auto.sh $PROJECT_ID $REGION
./deploy_telegram.sh $PROJECT_ID $REGION

echo "✅ All services deployed successfully!"




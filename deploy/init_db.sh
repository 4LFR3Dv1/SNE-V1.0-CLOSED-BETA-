#!/bin/bash
set -e

# Initialize database and run migrations
# Usage: ./init_db.sh [project-id] [region] [connection-name]

PROJECT_ID=${1:-${GOOGLE_CLOUD_PROJECT:-"your-project-id"}}
REGION=${2:-"us-central1"}
CONNECTION_NAME=${3:-"${PROJECT_ID}:${REGION}:sne-db-prod"}

echo "🗄️ Initializing database: $CONNECTION_NAME"

# Start Cloud SQL Proxy in background
cloud-sql-proxy ${CONNECTION_NAME} --port 5432 &
PROXY_PID=$!

# Wait for proxy to be ready
sleep 5

# Get database password from Secret Manager
DB_PASSWORD=$(gcloud secrets versions access latest --secret=sne-db-password --project=$PROJECT_ID)

# Set DATABASE_URL
export DATABASE_URL="postgresql://sne_admin:${DB_PASSWORD}@127.0.0.1:5432/sne"

# Run Alembic migrations
echo "📦 Running database migrations..."
cd "$(dirname "$0")/.."
alembic upgrade head

# Stop Cloud SQL Proxy
kill $PROXY_PID

echo "✅ Database initialized successfully!"




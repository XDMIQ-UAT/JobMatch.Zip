#!/bin/bash
# Deploy Agents to Cloud Run (Linux/Mac)

set -e

PROJECT_ID="${PROJECT_ID:-futurelink-private-112912460}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-agent-service}"

echo "================================================"
echo "  Deploy Agents to Cloud Run"
echo "================================================"
echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Set project
echo "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com --quiet

# Build and push
echo "Building and pushing container image..."
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME"
gcloud builds submit --tag $IMAGE_TAG

# Deploy
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_TAG:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --port 8080

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test endpoints:"
echo "  Health: $SERVICE_URL/health"
echo "  Workflows: $SERVICE_URL/workflows"
echo ""


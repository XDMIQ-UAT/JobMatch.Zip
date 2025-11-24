#!/bin/bash
set -e

echo "=== Google Secret Manager Setup for JobMatch AI ==="
echo "Project: futurelink-private-112912460"
echo ""

# Enable Secret Manager API
echo "Step 1: Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=futurelink-private-112912460

# Create secrets
echo ""
echo "Step 2: Creating secrets in Google Secret Manager..."

# JWT_SECRET
echo "Creating JWT_SECRET..."
JWT_SECRET=$(openssl rand -base64 32)
echo -n "$JWT_SECRET" | gcloud secrets create jobmatch-jwt-secret \
  --project=futurelink-private-112912460 \
  --replication-policy="automatic" \
  --data-file=- \
  2>/dev/null || echo "Secret already exists, updating version..."

if [ $? -ne 0 ]; then
  echo -n "$JWT_SECRET" | gcloud secrets versions add jobmatch-jwt-secret \
    --project=futurelink-private-112912460 \
    --data-file=-
fi

# DATABASE_URL
echo "Creating DATABASE_URL..."
DATABASE_URL="postgresql://dash@localhost:5432/jobmatch_ai"
echo -n "$DATABASE_URL" | gcloud secrets create jobmatch-database-url \
  --project=futurelink-private-112912460 \
  --replication-policy="automatic" \
  --data-file=- \
  2>/dev/null || echo "Secret already exists, updating version..."

if [ $? -ne 0 ]; then
  echo -n "$DATABASE_URL" | gcloud secrets versions add jobmatch-database-url \
    --project=futurelink-private-112912460 \
    --data-file=-
fi

# OPENAI_API_KEY (placeholder - you'll need to update this)
echo "Creating OPENAI_API_KEY placeholder..."
echo "⚠️  You need to manually add your OpenAI API key!"
echo ""
echo "Run this command with your actual OpenAI API key:"
echo "echo -n 'sk-proj-YOUR_KEY_HERE' | gcloud secrets create jobmatch-openai-key \\"
echo "  --project=futurelink-private-112912460 \\"
echo "  --replication-policy='automatic' \\"
echo "  --data-file=-"
echo ""

# Grant VM service account access to secrets
echo "Step 3: Granting VM service account access to secrets..."

# Get the default compute service account
PROJECT_NUMBER=$(gcloud projects describe futurelink-private-112912460 --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Service account: $SERVICE_ACCOUNT"

# Grant access to each secret
for SECRET_NAME in jobmatch-jwt-secret jobmatch-database-url jobmatch-openai-key; do
  echo "Granting access to $SECRET_NAME..."
  gcloud secrets add-iam-policy-binding $SECRET_NAME \
    --project=futurelink-private-112912460 \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" 2>/dev/null || true
done

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Secrets created:"
echo "  - jobmatch-jwt-secret"
echo "  - jobmatch-database-url"
echo "  - jobmatch-openai-key (needs your API key)"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key using the command shown above"
echo "2. Deploy the secret-loading script to the VM"
echo "3. Update backend to load secrets from Secret Manager"
echo ""

#!/bin/bash
# Setup Billing Budget for GCP Project
# Sets $100/month limit and stops all services when limit is reached

set -e

PROJECT_ID="${GCP_PROJECT_ID:-futurelink}"
BILLING_ACCOUNT_ID="${BILLING_ACCOUNT_ID}"
BUDGET_AMOUNT="${BUDGET_AMOUNT:-100}"
BUDGET_CURRENCY="${BUDGET_CURRENCY:-USD}"

echo "🔧 Setting up billing budget for project: $PROJECT_ID"
echo "Budget limit: $BUDGET_AMOUNT $BUDGET_CURRENCY/month"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Get billing account ID if not provided
if [ -z "$BILLING_ACCOUNT_ID" ]; then
    echo "📋 Getting billing account ID..."
    BILLING_ACCOUNT_ID=$(gcloud billing projects describe $PROJECT_ID --format="value(billingAccountName)" 2>/dev/null | sed 's/.*\///' || echo "")
    
    if [ -z "$BILLING_ACCOUNT_ID" ]; then
        echo "❌ No billing account found for project $PROJECT_ID"
        echo "Please link a billing account first:"
        echo "  gcloud billing projects link $PROJECT_ID --billing-account=BILLING_ACCOUNT_ID"
        exit 1
    fi
fi

echo "✅ Using billing account: $BILLING_ACCOUNT_ID"

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable \
    cloudbilling.googleapis.com \
    billingbudgets.googleapis.com \
    cloudfunctions.googleapis.com \
    pubsub.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    compute.googleapis.com \
    --project=$PROJECT_ID

# Create Pub/Sub topic for budget alerts
TOPIC_NAME="billing-budget-alerts"
echo "📨 Creating Pub/Sub topic: $TOPIC_NAME"
gcloud pubsub topics create $TOPIC_NAME --project=$PROJECT_ID 2>/dev/null || echo "Topic already exists"

# Create Pub/Sub subscription
SUBSCRIPTION_NAME="billing-budget-subscription"
echo "📬 Creating Pub/Sub subscription: $SUBSCRIPTION_NAME"
gcloud pubsub subscriptions create $SUBSCRIPTION_NAME \
    --topic=$TOPIC_NAME \
    --project=$PROJECT_ID \
    2>/dev/null || echo "Subscription already exists"

# Create Cloud Function to stop services when budget is exceeded
echo "⚙️  Creating Cloud Function to stop services..."
FUNCTION_NAME="stop-services-on-budget-exceeded"
FUNCTION_REGION="${FUNCTION_REGION:-us-central1}"

# Use the function code from scripts/billing-budget-function
FUNCTION_SOURCE_DIR="scripts/billing-budget-function"

if [ ! -d "$FUNCTION_SOURCE_DIR" ]; then
    echo "❌ Function source directory not found: $FUNCTION_SOURCE_DIR"
    exit 1
fi

# Use the function source directory directly (or copy to temp if needed)
# For Cloud Functions deployment, we'll use the source directory directly
FUNCTION_DEPLOY_SOURCE="$FUNCTION_SOURCE_DIR"

# Deploy Cloud Function
echo "🚀 Deploying Cloud Function..."
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python311 \
    --region=$FUNCTION_REGION \
    --source=$FUNCTION_DEPLOY_SOURCE \
    --entry-point=stop_services_pubsub \
    --trigger-topic=$TOPIC_NAME \
    --set-env-vars="GCP_PROJECT=$PROJECT_ID" \
    --service-account=$(gcloud iam service-accounts list --filter="displayName:Compute Engine default service account" --format="value(email)" --project=$PROJECT_ID) \
    --project=$PROJECT_ID \
    --allow-unauthenticated=false \
    --timeout=540s \
    --memory=512MB

# Grant necessary permissions to Cloud Function service account
SERVICE_ACCOUNT=$(gcloud functions describe $FUNCTION_NAME --region=$FUNCTION_REGION --gen2 --format="value(serviceAccountEmail)" --project=$PROJECT_ID)
echo "🔐 Granting permissions to service account: $SERVICE_ACCOUNT"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/compute.instanceAdmin.v1" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.admin" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/cloudfunctions.admin" \
    --condition=None

# Create billing budget
echo "💰 Creating billing budget..."
BUDGET_DISPLAY_NAME="Monthly Budget Limit - $BUDGET_AMOUNT $BUDGET_CURRENCY"

# Create budget JSON
BUDGET_JSON=$(cat <<EOF
{
  "displayName": "$BUDGET_DISPLAY_NAME",
  "budgetFilter": {
    "projects": ["projects/$PROJECT_ID"],
    "creditTypesTreatment": "INCLUDE_ALL_CREDITS"
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "$BUDGET_CURRENCY",
      "units": "$BUDGET_AMOUNT"
    }
  },
  "thresholdRules": [
    {
      "thresholdPercent": 0.5,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.75,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.9,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 1.0,
      "spendBasis": "CURRENT_SPEND"
    }
  ],
  "notificationsRule": {
    "pubsubTopic": "projects/$PROJECT_ID/topics/$TOPIC_NAME",
    "schemaVersion": "1.0"
  },
  "allUpdatesRule": {
    "pubsubTopic": "projects/$PROJECT_ID/topics/$TOPIC_NAME"
  }
}
EOF
)

# Create budget using gcloud
echo "$BUDGET_JSON" > $TEMP_DIR/budget.json

gcloud billing budgets create \
    --billing-account=$BILLING_ACCOUNT_ID \
    --display-name="$BUDGET_DISPLAY_NAME" \
    --budget-amount=$BUDGET_AMOUNT \
    --budget-amount-currency=$BUDGET_CURRENCY \
    --projects=$PROJECT_ID \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=75 \
    --threshold-rule=percent=90 \
    --threshold-rule=percent=100 \
    --pubsub-topic=projects/$PROJECT_ID/topics/$TOPIC_NAME

echo ""
echo "✅ Billing budget setup complete!"
echo ""
echo "📊 Budget Details:"
echo "  - Project: $PROJECT_ID"
echo "  - Budget: $BUDGET_AMOUNT $BUDGET_CURRENCY/month"
echo "  - Alerts at: 50%, 75%, 90%, 100%"
echo "  - Services will stop automatically at 100%"
echo ""
echo "🔍 To check budget status:"
echo "  gcloud billing budgets list --billing-account=$BILLING_ACCOUNT_ID"
echo ""
echo "📝 To view Cloud Function logs:"
echo "  gcloud functions logs read $FUNCTION_NAME --region=$FUNCTION_REGION --gen2"
echo ""


# Setup Billing Budget for GCP Project (PowerShell)
# Sets $100/month limit and stops all services when limit is reached

$ErrorActionPreference = "Stop"

$PROJECT_ID = if ($env:GCP_PROJECT_ID) { $env:GCP_PROJECT_ID } else { "futurelink" }
$BILLING_ACCOUNT_ID = $env:BILLING_ACCOUNT_ID
$BUDGET_AMOUNT = if ($env:BUDGET_AMOUNT) { $env:BUDGET_AMOUNT } else { "100" }
$BUDGET_CURRENCY = if ($env:BUDGET_CURRENCY) { $env:BUDGET_CURRENCY } else { "USD" }
$FUNCTION_REGION = if ($env:FUNCTION_REGION) { $env:FUNCTION_REGION } else { "us-central1" }

Write-Host "🔧 Setting up billing budget for project: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "Budget limit: $BUDGET_AMOUNT $BUDGET_CURRENCY/month" -ForegroundColor Cyan

# Check if gcloud is installed
try {
    $null = gcloud --version 2>$null
} catch {
    Write-Host "❌ gcloud CLI not found. Please install Google Cloud SDK." -ForegroundColor Red
    exit 1
}

# Set project
gcloud config set project $PROJECT_ID

# Get billing account ID if not provided
if (-not $BILLING_ACCOUNT_ID) {
    Write-Host "📋 Getting billing account ID..." -ForegroundColor Yellow
    $billingInfo = gcloud billing projects describe $PROJECT_ID --format="json" 2>$null | ConvertFrom-Json
    if ($billingInfo.billingAccountName) {
        $BILLING_ACCOUNT_ID = $billingInfo.billingAccountName -replace '.*/', ''
    }
    
    if (-not $BILLING_ACCOUNT_ID) {
        Write-Host "❌ No billing account found for project $PROJECT_ID" -ForegroundColor Red
        Write-Host "Please link a billing account first:" -ForegroundColor Yellow
        Write-Host "  gcloud billing projects link $PROJECT_ID --billing-account=BILLING_ACCOUNT_ID" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "✅ Using billing account: $BILLING_ACCOUNT_ID" -ForegroundColor Green

# Enable required APIs
Write-Host "🔌 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable `
    cloudbilling.googleapis.com `
    billingbudgets.googleapis.com `
    cloudfunctions.googleapis.com `
    pubsub.googleapis.com `
    cloudbuild.googleapis.com `
    run.googleapis.com `
    compute.googleapis.com `
    --project=$PROJECT_ID

# Create Pub/Sub topic for budget alerts
$TOPIC_NAME = "billing-budget-alerts"
Write-Host "📨 Creating Pub/Sub topic: $TOPIC_NAME" -ForegroundColor Yellow
try {
    gcloud pubsub topics create $TOPIC_NAME --project=$PROJECT_ID 2>$null
} catch {
    Write-Host "Topic already exists" -ForegroundColor Gray
}

# Create Pub/Sub subscription
$SUBSCRIPTION_NAME = "billing-budget-subscription"
Write-Host "📬 Creating Pub/Sub subscription: $SUBSCRIPTION_NAME" -ForegroundColor Yellow
try {
    gcloud pubsub subscriptions create $SUBSCRIPTION_NAME `
        --topic=$TOPIC_NAME `
        --project=$PROJECT_ID 2>$null
} catch {
    Write-Host "Subscription already exists" -ForegroundColor Gray
}

# Create Cloud Function to stop services when budget is exceeded
Write-Host "⚙️  Creating Cloud Function to stop services..." -ForegroundColor Yellow
$FUNCTION_NAME = "stop-services-on-budget-exceeded"

# Use the function code from scripts/billing-budget-function
$FUNCTION_SOURCE_DIR = "scripts\billing-budget-function"

if (-not (Test-Path $FUNCTION_SOURCE_DIR)) {
    Write-Host "❌ Function source directory not found: $FUNCTION_SOURCE_DIR" -ForegroundColor Red
    exit 1
}

# Use the function source directory directly for deployment
$FUNCTION_DEPLOY_SOURCE = $FUNCTION_SOURCE_DIR

# Deploy Cloud Function
Write-Host "🚀 Deploying Cloud Function..." -ForegroundColor Yellow
$serviceAccount = gcloud iam service-accounts list --filter="displayName:Compute Engine default service account" --format="value(email)" --project=$PROJECT_ID

gcloud functions deploy $FUNCTION_NAME `
    --gen2 `
    --runtime=python311 `
    --region=$FUNCTION_REGION `
    --source=$FUNCTION_DEPLOY_SOURCE `
    --entry-point=stop_services_pubsub `
    --trigger-topic=$TOPIC_NAME `
    --set-env-vars="GCP_PROJECT=$PROJECT_ID" `
    --service-account=$serviceAccount `
    --project=$PROJECT_ID `
    --allow-unauthenticated=false `
    --timeout=540s `
    --memory=512MB

# Grant necessary permissions to Cloud Function service account
Write-Host "🔐 Granting permissions to service account..." -ForegroundColor Yellow
$functionInfo = gcloud functions describe $FUNCTION_NAME --region=$FUNCTION_REGION --gen2 --format="json" --project=$PROJECT_ID | ConvertFrom-Json
$SERVICE_ACCOUNT = $functionInfo.serviceAccountEmail

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/compute.instanceAdmin.v1" `
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/run.admin" `
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:$SERVICE_ACCOUNT" `
    --role="roles/cloudfunctions.admin" `
    --condition=None

# Create billing budget
Write-Host "💰 Creating billing budget..." -ForegroundColor Yellow
$BUDGET_DISPLAY_NAME = "Monthly Budget Limit - $BUDGET_AMOUNT $BUDGET_CURRENCY"

gcloud billing budgets create `
    --billing-account=$BILLING_ACCOUNT_ID `
    --display-name="$BUDGET_DISPLAY_NAME" `
    --budget-amount=$BUDGET_AMOUNT `
    --budget-amount-currency=$BUDGET_CURRENCY `
    --projects=$PROJECT_ID `
    --threshold-rule=percent=50 `
    --threshold-rule=percent=75 `
    --threshold-rule=percent=90 `
    --threshold-rule=percent=100 `
    --pubsub-topic=projects/$PROJECT_ID/topics/$TOPIC_NAME

Write-Host ""
Write-Host "✅ Billing budget setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Budget Details:" -ForegroundColor Cyan
Write-Host "  - Project: $PROJECT_ID"
Write-Host "  - Budget: $BUDGET_AMOUNT $BUDGET_CURRENCY/month"
Write-Host "  - Alerts at: 50%, 75%, 90%, 100%"
Write-Host "  - Services will stop automatically at 100%"
Write-Host ""
Write-Host "🔍 To check budget status:" -ForegroundColor Yellow
Write-Host "  gcloud billing budgets list --billing-account=$BILLING_ACCOUNT_ID"
Write-Host ""
Write-Host "📝 To view Cloud Function logs:" -ForegroundColor Yellow
Write-Host "  gcloud functions logs read $FUNCTION_NAME --region=$FUNCTION_REGION --gen2"
Write-Host ""


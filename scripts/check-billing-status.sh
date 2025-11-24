#!/bin/bash
# Check billing budget status for GCP project

set -e

PROJECT_ID="${GCP_PROJECT_ID:-futurelink}"
BILLING_ACCOUNT_ID="${BILLING_ACCOUNT_ID}"

echo "📊 Checking billing status for project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Get billing account ID if not provided
if [ -z "$BILLING_ACCOUNT_ID" ]; then
    BILLING_ACCOUNT_ID=$(gcloud billing projects describe $PROJECT_ID --format="value(billingAccountName)" 2>/dev/null | sed 's/.*\///' || echo "")
    
    if [ -z "$BILLING_ACCOUNT_ID" ]; then
        echo "❌ No billing account found for project $PROJECT_ID"
        exit 1
    fi
fi

echo "Billing Account: $BILLING_ACCOUNT_ID"
echo ""

# List budgets
echo "💰 Budgets:"
gcloud billing budgets list --billing-account=$BILLING_ACCOUNT_ID --format="table(displayName,budgetFilter.projects,budgetFilter.projects[0]:label=PROJECT,amount.specifiedAmount.currencyCode,amount.specifiedAmount.units,thresholdRules)"

echo ""
echo "📈 Current spending:"
gcloud billing projects describe $PROJECT_ID --format="table(projectId,billingAccountName,billingEnabled)"

echo ""
echo "🔍 To view detailed budget information:"
echo "  gcloud billing budgets describe BUDGET_ID --billing-account=$BILLING_ACCOUNT_ID"


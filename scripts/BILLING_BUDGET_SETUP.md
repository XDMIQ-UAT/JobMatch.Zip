# GCP Billing Budget Setup Guide

This guide explains how to set up a $100/month billing limit for the `futurelink` GCP project with automatic service shutdown when the limit is reached.

## Overview

The setup includes:
1. **Billing Budget**: $100/month limit with alerts at 50%, 75%, 90%, and 100%
2. **Cloud Function**: Automatically stops all services when budget reaches 100%
3. **Pub/Sub Integration**: Connects budget alerts to the shutdown function

## Prerequisites

1. **Google Cloud CLI installed**: [Install gcloud](https://cloud.google.com/sdk/docs/install)
2. **Authenticated**: `gcloud auth login`
3. **Project access**: Access to the `futurelink` project
4. **Billing account**: Project must be linked to a billing account

## Quick Setup

### Linux/Mac

```bash
export GCP_PROJECT_ID="futurelink"
export BILLING_ACCOUNT_ID="your-billing-account-id"  # Optional, will auto-detect
./scripts/setup-billing-budget.sh
```

### Windows (PowerShell)

```powershell
$env:GCP_PROJECT_ID = "futurelink"
$env:BILLING_ACCOUNT_ID = "your-billing-account-id"  # Optional, will auto-detect
.\scripts\setup-billing-budget.ps1
```

## What Gets Stopped

When the budget limit (100%) is reached, the following services are automatically stopped:

1. **Compute Engine VMs**: All running VM instances are stopped
2. **Cloud Run Services**: All services are scaled down to 0 instances
3. **Cloud Functions**: Noted but not automatically stopped (requires manual intervention)

**Note**: Cloud SQL instances are **NOT** automatically stopped to prevent data loss. You can manually stop them if needed.

## Manual Operations

### Check Budget Status

```bash
./scripts/check-billing-status.sh
```

Or manually:
```bash
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID
```

### Manually Stop All Services

```bash
export GCP_PROJECT_ID="futurelink"
./scripts/stop-all-services.sh
```

### View Cloud Function Logs

```bash
gcloud functions logs read stop-services-on-budget-exceeded \
    --region=us-central1 \
    --gen2 \
    --project=futurelink
```

## Budget Alerts

The budget is configured with alerts at:
- **50%**: Early warning ($50 spent)
- **75%**: Approaching limit ($75 spent)
- **90%**: Critical warning ($90 spent)
- **100%**: **Services automatically stop** ($100 spent)

## How It Works

1. **Billing Budget** monitors spending for the `futurelink` project
2. When spending reaches a threshold, a **Pub/Sub message** is sent
3. **Cloud Function** (`stop-services-on-budget-exceeded`) receives the message
4. Function checks if threshold is 100%
5. If yes, it stops all Compute Engine VMs and scales Cloud Run services to 0
6. Logs are written to Cloud Function logs

## Customization

### Change Budget Amount

Edit the script or set environment variable:
```bash
export BUDGET_AMOUNT="200"  # $200/month instead of $100
./scripts/setup-billing-budget.sh
```

### Change Alert Thresholds

Edit the `--threshold-rule` parameters in the script:
```bash
--threshold-rule=percent=25 \
--threshold-rule=percent=50 \
--threshold-rule=percent=75 \
--threshold-rule=percent=100
```

### Change Function Region

```bash
export FUNCTION_REGION="us-east1"
./scripts/setup-billing-budget.sh
```

## Troubleshooting

### "No billing account found"

Link a billing account first:
```bash
gcloud billing projects link futurelink --billing-account=BILLING_ACCOUNT_ID
```

### "Permission denied"

Ensure you have the following roles:
- `roles/billing.admin` (to create budgets)
- `roles/owner` or `roles/editor` (to deploy functions)
- `roles/pubsub.admin` (to create topics/subscriptions)

### Function not triggering

1. Check Pub/Sub topic exists: `gcloud pubsub topics list`
2. Check subscription exists: `gcloud pubsub subscriptions list`
3. Check function logs: `gcloud functions logs read stop-services-on-budget-exceeded --gen2`
4. Verify budget is sending to Pub/Sub topic

### Services not stopping

1. Check function logs for errors
2. Verify service account has required permissions:
   - `roles/compute.instanceAdmin.v1`
   - `roles/run.admin`
3. Manually test the function:
   ```bash
   gcloud functions call stop-services-on-budget-exceeded \
       --gen2 \
       --region=us-central1 \
       --data='{"data":"eyJhbGVydFRocmVzaG9sZEV4Y2VlZGVkIjoxfQ=="}'
   ```

## Security Considerations

1. **Service Account**: The Cloud Function uses the Compute Engine default service account with minimal required permissions
2. **Authentication**: Function is not publicly accessible (requires Pub/Sub trigger)
3. **Audit Logging**: All actions are logged in Cloud Function logs
4. **Manual Override**: Services can be manually restarted if needed

## Cost of Budget Monitoring

- **Billing Budget API**: Free
- **Pub/Sub**: Free tier includes 10GB/month (more than enough for budget alerts)
- **Cloud Function**: Free tier includes 2 million invocations/month
- **Total Cost**: **$0** (within free tier limits)

## Restarting Services After Budget Reset

When the new billing month starts, you'll need to manually restart services:

1. **Restart VMs**:
   ```bash
   gcloud compute instances start INSTANCE_NAME --zone=ZONE --project=futurelink
   ```

2. **Scale up Cloud Run**:
   ```bash
   gcloud run services update SERVICE_NAME \
       --region=REGION \
       --min-instances=1 \
       --project=futurelink
   ```

Or use the reverse of `stop-all-services.sh` to create a startup script.

## Additional Resources

- [GCP Billing Budgets Documentation](https://cloud.google.com/billing/docs/how-to/budgets)
- [Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)


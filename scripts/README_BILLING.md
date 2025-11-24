# Billing Budget Setup - Quick Reference

## Setup $100/month Budget for futurelink Project

### Quick Start

**Linux/Mac:**
```bash
export GCP_PROJECT_ID="futurelink"
./scripts/setup-billing-budget.sh
```

**Windows:**
```powershell
$env:GCP_PROJECT_ID = "futurelink"
.\scripts\setup-billing-budget.ps1
```

## What It Does

1. ✅ Creates a **$100/month billing budget** for the `futurelink` project
2. ✅ Sets up **alerts at 50%, 75%, 90%, and 100%** spending
3. ✅ Creates a **Cloud Function** that automatically stops all services at 100%
4. ✅ Stops **Compute Engine VMs** and scales **Cloud Run services to 0** when limit reached

## Files Created

- `scripts/setup-billing-budget.sh` - Linux/Mac setup script
- `scripts/setup-billing-budget.ps1` - Windows PowerShell setup script
- `scripts/billing-budget-function/main.py` - Cloud Function code
- `scripts/billing-budget-function/requirements.txt` - Python dependencies
- `scripts/stop-all-services.sh` - Manual service shutdown script
- `scripts/check-billing-status.sh` - Check budget status script
- `scripts/BILLING_BUDGET_SETUP.md` - Full documentation

## Manual Commands

**Check budget:**
```bash
./scripts/check-billing-status.sh
```

**Stop all services manually:**
```bash
export GCP_PROJECT_ID="futurelink"
./scripts/stop-all-services.sh
```

**View function logs:**
```bash
gcloud functions logs read stop-services-on-budget-exceeded \
    --region=us-central1 \
    --gen2 \
    --project=futurelink
```

## Important Notes

- ⚠️ **Cloud SQL instances are NOT stopped** automatically (to prevent data loss)
- ⚠️ Services must be **manually restarted** after budget resets
- ✅ Budget monitoring is **free** (within GCP free tier)
- ✅ All actions are **logged** for audit purposes

For detailed documentation, see `scripts/BILLING_BUDGET_SETUP.md`.


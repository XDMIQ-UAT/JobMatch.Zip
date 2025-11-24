# Check SES configuration on VM
# Diagnose why SES email sending is failing

param(
    [string]$VmName = "jobmatch-vm",
    [string]$Zone = "us-central1-a"
)

Write-Host "🔍 Checking SES Configuration on VM..." -ForegroundColor Cyan
Write-Host ""

# Check .env file
Write-Host "📋 Step 1: Checking .env file..." -ForegroundColor Yellow
gcloud compute ssh $VmName --zone=$Zone --command="cd /opt/jobmatch && cat .env | grep -E 'EMAIL_PROVIDER_MODE|SES_FROM_EMAIL|AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|SES_REGION' | sed 's/=.*/=***HIDDEN***/'" 2>&1

Write-Host ""
Write-Host "📋 Step 2: Testing SES connection from container..." -ForegroundColor Yellow
$testScript = @"
import sys
sys.path.insert(0, '/app')
from backend.config import settings
from backend.auth.email_provider import create_email_manager
import asyncio

print(f'EMAIL_PROVIDER_MODE: {settings.EMAIL_PROVIDER_MODE}')
print(f'SES_FROM_EMAIL: {settings.SES_FROM_EMAIL}')
print(f'AWS_ACCESS_KEY_ID: {\"SET\" if settings.AWS_ACCESS_KEY_ID else \"NOT SET\"}')
print(f'AWS_SECRET_ACCESS_KEY: {\"SET\" if settings.AWS_SECRET_ACCESS_KEY else \"NOT SET\"}')
print(f'SES_REGION: {settings.SES_REGION}')

# Test email manager initialization
try:
    manager = create_email_manager()
    print(f'Email Manager Provider Mode: {manager.provider_mode}')
    print(f'From Email: {manager.from_email}')
    print(f'SES Client: {\"INITIALIZED\" if manager.ses_client else \"NOT INITIALIZED\"}')
    
    if manager.ses_client:
        # Test SES connection
        try:
            quota = manager.ses_client.get_send_quota()
            print(f'SES Send Quota: {quota}')
        except Exception as e:
            print(f'SES Connection Error: {e}')
except Exception as e:
    print(f'Error creating email manager: {e}')
"@

$testScript | gcloud compute ssh $VmName --zone=$Zone --command="cd /opt/jobmatch && docker compose exec -T app python3" 2>&1

Write-Host ""
Write-Host "📋 Step 3: Checking backend logs for email errors..." -ForegroundColor Yellow
gcloud compute ssh $VmName --zone=$Zone --command="cd /opt/jobmatch && docker compose logs app --tail=100 | grep -i 'email\|ses\|verification' | tail -20" 2>&1

Write-Host ""
Write-Host "✅ Diagnostic complete!" -ForegroundColor Green


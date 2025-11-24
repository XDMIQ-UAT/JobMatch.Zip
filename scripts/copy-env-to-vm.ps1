# Copy .env file to Production VM
# This script securely copies your local .env file to the VM
# Note: .env is excluded from git, so it must be manually deployed

param(
    [string]$VmName,
    [string]$Zone,
    [string]$EnvFile = ".env"
)

# Set defaults if not provided
if (-not $VmName) {
    $VmName = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
}
if (-not $Zone) {
    $Zone = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
}

Write-Host "📋 Copying .env file to VM" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Error: .env file not found at: $EnvFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure you're running this from the project root directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found .env file" -ForegroundColor Green
Write-Host "   VM: $VmName" -ForegroundColor White
Write-Host "   Zone: $Zone" -ForegroundColor White
Write-Host ""

# Backup existing .env on VM before overwriting
Write-Host "💾 Backing up existing .env on VM..." -ForegroundColor Yellow
$backupCmd = "cd /opt/jobmatch && if [ -f .env ]; then cp .env .env.backup.`$(date +%Y%m%d_%H%M%S) && echo '✅ Backed up existing .env'; else echo 'ℹ️  No existing .env to backup'; fi"

gcloud compute ssh $VmName --zone=$Zone --command=$backupCmd

# Copy .env file
Write-Host ""
Write-Host "📤 Copying .env to VM..." -ForegroundColor Cyan
gcloud compute scp $EnvFile "${VmName}:/opt/jobmatch/.env" --zone=$Zone

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ .env file copied successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Verify the file was copied
    Write-Host "🔍 Verifying .env on VM..." -ForegroundColor Yellow
    $verifyCmd = "cd /opt/jobmatch && if [ -f .env ]; then echo '✅ .env file exists' && echo '' && echo '📋 Checking key settings:' && grep -E '^(EMAIL_PROVIDER_MODE|SES_FROM_EMAIL|AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|SES_REGION)=' .env | sed 's/=.*/=***/' || echo '   (Some settings not found)'; else echo '❌ .env file not found!' && exit 1; fi"
    
    gcloud compute ssh $VmName --zone=$Zone --command=$verifyCmd
    
    Write-Host ""
    Write-Host "🔄 Restarting backend to load new environment variables..." -ForegroundColor Cyan
    Write-Host ""
    
    # Restart backend service
    Write-Host "   Restarting backend..." -ForegroundColor Gray
    $restartCmd = "cd /opt/jobmatch && (if command -v supervisorctl &> /dev/null; then sudo supervisorctl restart backend; elif systemctl list-units 2>/dev/null | grep -q backend; then sudo systemctl restart backend; else sudo docker compose restart backend; fi) && sleep 3 && echo '✅ Backend restart command executed'"
    
    gcloud compute ssh $VmName --zone=$Zone --command=$restartCmd
    
    Write-Host ""
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Test email sending on https://jobmatch.zip/auth" -ForegroundColor White
    Write-Host "   2. Check backend logs if issues persist:" -ForegroundColor White
    Write-Host "      gcloud compute ssh $VmName --zone=$Zone --command='tail -f /tmp/backend.log'" -ForegroundColor Gray
} else {
    Write-Host "❌ Failed to copy .env file" -ForegroundColor Red
    exit 1
}


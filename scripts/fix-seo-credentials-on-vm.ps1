# Fix Google Search Console credentials format on VM
# This properly formats the credentials for docker-compose .env file

$ErrorActionPreference = "Stop"

$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
$CREDS_FILE = "secrets/search-console-credentials.json"

if (-not (Test-Path $CREDS_FILE)) {
    Write-Host "❌ Credentials file not found: $CREDS_FILE" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Fixing credentials format on VM..." -ForegroundColor Cyan

# Read credentials
$credsJson = Get-Content $CREDS_FILE -Raw
$credsBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($credsJson))

# Create fix script
$tempScript = Join-Path $env:TEMP "fix-seo-creds.sh"
$scriptContent = @"
#!/bin/bash
cd /opt/jobmatch || exit 1

# Decode credentials
CREDS_JSON=`$(echo '$credsBase64' | base64 -d)

# Remove existing credentials
sed -i '/GOOGLE_SEARCH_CONSOLE_CREDENTIALS/d' .env
sed -i '/GOOGLE_SEARCH_CONSOLE_SITE_URL/d' .env

# Add credentials in proper format for .env file
# Use printf to avoid shell interpretation issues
printf 'GOOGLE_SEARCH_CONSOLE_CREDENTIALS=' >> .env
printf '%s' "'" >> .env
printf '%s' "`$CREDS_JSON" >> .env
printf '%s\n' "'" >> .env
echo "GOOGLE_SEARCH_CONSOLE_SITE_URL='https://jobmatch.zip'" >> .env

echo '✅ Credentials fixed successfully'
"@

$scriptContent | Set-Content -Path $tempScript -Encoding UTF8 -NoNewline

# Upload and execute
gcloud compute scp $tempScript "${VM_NAME}:/tmp/fix-seo-creds.sh" --zone=$ZONE
gcloud compute ssh $VM_NAME --zone=$ZONE --command="sed -i 's/\r$//' /tmp/fix-seo-creds.sh && chmod +x /tmp/fix-seo-creds.sh && /tmp/fix-seo-creds.sh && rm /tmp/fix-seo-creds.sh"

Remove-Item $tempScript -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Credentials fixed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔄 Now restart the backend:" -ForegroundColor Yellow
    Write-Host "   gcloud compute ssh $VM_NAME --zone=$ZONE" -ForegroundColor White
    Write-Host "   Then run: cd /opt/jobmatch && docker restart `$(docker ps -q -f name=app)" -ForegroundColor White
} else {
    Write-Host "❌ Failed to fix credentials" -ForegroundColor Red
    exit 1
}


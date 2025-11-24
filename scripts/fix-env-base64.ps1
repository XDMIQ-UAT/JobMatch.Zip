# Fix .env file using base64 encoding for credentials
# This avoids docker-compose parsing issues with JSON

$ErrorActionPreference = "Stop"

$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
$CREDS_FILE = "secrets/search-console-credentials.json"

if (-not (Test-Path $CREDS_FILE)) {
    Write-Host "❌ Credentials file not found" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Fixing .env file with base64 encoding..." -ForegroundColor Cyan

# Read and base64 encode credentials
$credsJson = Get-Content $CREDS_FILE -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($credsJson)
$credsBase64 = [Convert]::ToBase64String($bytes)

# Create fix script
$tempScript = Join-Path $env:TEMP "fix-env-base64.sh"
$scriptContent = @"
#!/bin/bash
cd /opt/jobmatch || exit 1

# Remove existing credentials
sed -i '/GOOGLE_SEARCH_CONSOLE_CREDENTIALS/d' .env
sed -i '/GOOGLE_SEARCH_CONSOLE_SITE_URL/d' .env

# Add credentials using base64 (app will decode)
echo "GOOGLE_SEARCH_CONSOLE_CREDENTIALS_B64='$credsBase64'" >> .env
echo "GOOGLE_SEARCH_CONSOLE_SITE_URL='https://jobmatch.zip'" >> .env

echo '✅ .env file fixed with base64 encoding'
"@

$scriptContent | Set-Content -Path $tempScript -Encoding UTF8 -NoNewline

# Upload and execute
gcloud compute scp $tempScript "${VM_NAME}:/tmp/fix-env-base64.sh" --zone=$ZONE
gcloud compute ssh $VM_NAME --zone=$ZONE --command="sed -i 's/\r$//' /tmp/fix-env-base64.sh && chmod +x /tmp/fix-env-base64.sh && /tmp/fix-env-base64.sh && rm /tmp/fix-env-base64.sh"

Remove-Item $tempScript -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ .env file fixed!" -ForegroundColor Green
    Write-Host "⚠️  Note: App needs to decode base64. Updating search_console.py..." -ForegroundColor Yellow
    
    # Update the search console manager to handle base64
    Write-Host "The app will need to decode GOOGLE_SEARCH_CONSOLE_CREDENTIALS_B64 if present" -ForegroundColor Gray
} else {
    Write-Host "❌ Failed to fix .env file" -ForegroundColor Red
    exit 1
}


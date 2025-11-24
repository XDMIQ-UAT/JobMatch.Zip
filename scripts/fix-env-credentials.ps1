# Fix .env file credentials format for docker-compose
# This properly escapes the JSON for .env file format

$ErrorActionPreference = "Stop"

$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
$CREDS_FILE = "secrets/search-console-credentials.json"

if (-not (Test-Path $CREDS_FILE)) {
    Write-Host "❌ Credentials file not found" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Fixing .env file format..." -ForegroundColor Cyan

# Read and properly format credentials
$credsJson = Get-Content $CREDS_FILE -Raw
# Convert to single-line and escape for shell
$credsEscaped = $credsJson -replace "`r`n", "" -replace "`n", "" -replace '"', '\"'

# Create fix script
$tempScript = Join-Path $env:TEMP "fix-env.sh"
$scriptContent = @"
#!/bin/bash
cd /opt/jobmatch || exit 1

# Remove existing credentials
sed -i '/GOOGLE_SEARCH_CONSOLE_CREDENTIALS/d' .env
sed -i '/GOOGLE_SEARCH_CONSOLE_SITE_URL/d' .env

# Add credentials using printf to avoid shell interpretation
# The JSON needs to be in single quotes with escaped single quotes
CREDS_JSON='$credsEscaped'
# Escape single quotes in JSON for .env file
CREDS_FOR_ENV=`$(echo "`$CREDS_JSON" | sed "s/'/'\''/g")

# Write to .env using a here-doc to avoid quote issues
cat >> .env <<'ENVEOF'
GOOGLE_SEARCH_CONSOLE_CREDENTIALS='$credsEscaped'
GOOGLE_SEARCH_CONSOLE_SITE_URL='https://jobmatch.zip'
ENVEOF

echo '✅ .env file fixed'
"@

$scriptContent | Set-Content -Path $tempScript -Encoding UTF8 -NoNewline

# Upload and execute
gcloud compute scp $tempScript "${VM_NAME}:/tmp/fix-env.sh" --zone=$ZONE
gcloud compute ssh $VM_NAME --zone=$ZONE --command="sed -i 's/\r$//' /tmp/fix-env.sh && chmod +x /tmp/fix-env.sh && /tmp/fix-env.sh && rm /tmp/fix-env.sh"

Remove-Item $tempScript -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ .env file fixed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔄 Now start the backend:" -ForegroundColor Yellow
    Write-Host "   gcloud compute ssh $VM_NAME --zone=$ZONE" -ForegroundColor White
    Write-Host "   cd /opt/jobmatch" -ForegroundColor White
    Write-Host "   docker compose up -d app" -ForegroundColor White
} else {
    Write-Host "❌ Failed to fix .env file" -ForegroundColor Red
    exit 1
}


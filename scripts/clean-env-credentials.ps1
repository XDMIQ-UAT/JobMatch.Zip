# Clean and properly set credentials in .env file
# Removes ALL credential lines and adds only base64 version

$ErrorActionPreference = "Stop"

$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
$CREDS_FILE = "secrets/search-console-credentials.json"

if (-not (Test-Path $CREDS_FILE)) {
    Write-Host "❌ Credentials file not found" -ForegroundColor Red
    exit 1
}

Write-Host "🧹 Cleaning and fixing .env file..." -ForegroundColor Cyan

# Read and base64 encode credentials
$credsJson = Get-Content $CREDS_FILE -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($credsJson)
$credsBase64 = [Convert]::ToBase64String($bytes)

# Create cleanup script
$tempScript = Join-Path $env:TEMP "clean-env.sh"
$scriptContent = @"
#!/bin/bash
cd /opt/jobmatch || exit 1

# Remove ALL credential-related lines (including any with quotes or base64)
sed -i '/GOOGLE_SEARCH_CONSOLE/d' .env

# Add clean base64 version
echo "GOOGLE_SEARCH_CONSOLE_CREDENTIALS_B64=$credsBase64" >> .env
echo "GOOGLE_SEARCH_CONSOLE_SITE_URL=https://jobmatch.zip" >> .env

echo '✅ .env file cleaned and fixed'
"@

$scriptContent | Set-Content -Path $tempScript -Encoding UTF8 -NoNewline

# Upload and execute
gcloud compute scp $tempScript "${VM_NAME}:/tmp/clean-env.sh" --zone=$ZONE
gcloud compute ssh $VM_NAME --zone=$ZONE --command="sed -i 's/\r$//' /tmp/clean-env.sh && chmod +x /tmp/clean-env.sh && /tmp/clean-env.sh && rm /tmp/clean-env.sh"

Remove-Item $tempScript -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ .env file cleaned and fixed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔄 Now start the backend:" -ForegroundColor Yellow
    Write-Host "   gcloud compute ssh $VM_NAME --zone=$ZONE" -ForegroundColor White
    Write-Host "   cd /opt/jobmatch" -ForegroundColor White
    Write-Host "   docker compose up -d app" -ForegroundColor White
} else {
    Write-Host "❌ Failed to clean .env file" -ForegroundColor Red
    exit 1
}


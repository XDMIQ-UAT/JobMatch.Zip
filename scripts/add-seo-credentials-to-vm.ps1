# Add Google Search Console credentials to production VM
# Usage: .\scripts\add-seo-credentials-to-vm.ps1

$ErrorActionPreference = "Stop"

$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }
$CREDS_FILE = "secrets/search-console-credentials.json"

if (-not (Test-Path $CREDS_FILE)) {
    Write-Host "❌ Credentials file not found: $CREDS_FILE" -ForegroundColor Red
    Write-Host "Run the setup script first to generate credentials." -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Adding Google Search Console credentials to VM..." -ForegroundColor Cyan

# Read credentials and encode to base64 to avoid quote issues
$credsJson = Get-Content $CREDS_FILE -Raw
$credsBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($credsJson))

# Create a temporary script file
$tempScript = Join-Path $env:TEMP "add-seo-creds.sh"
$scriptContent = @"
#!/bin/bash
cd /opt/jobmatch || exit 1

# Decode credentials from base64
CREDS_JSON=`$(echo '$credsBase64' | base64 -d)

# Remove existing credentials if present
if grep -q 'GOOGLE_SEARCH_CONSOLE_CREDENTIALS' .env; then
    echo 'Updating existing credentials...'
    sed -i '/GOOGLE_SEARCH_CONSOLE_CREDENTIALS/d' .env
    sed -i '/GOOGLE_SEARCH_CONSOLE_SITE_URL/d' .env
fi

# Add new credentials (properly escape for .env file)
# Use single quotes and escape any single quotes in the JSON
CREDS_ESCAPED=`$(echo "`$CREDS_JSON" | sed "s/'/'\''/g" | sed 's/"/\\"/g')
echo "GOOGLE_SEARCH_CONSOLE_CREDENTIALS='`$CREDS_ESCAPED'" >> .env
echo "GOOGLE_SEARCH_CONSOLE_SITE_URL='https://jobmatch.zip'" >> .env

echo 'Credentials added successfully'
"@

# Write script to temp file
$scriptContent | Set-Content -Path $tempScript -Encoding UTF8 -NoNewline

# Upload and execute script
Write-Host "Uploading script to VM..." -ForegroundColor Gray
gcloud compute scp $tempScript "${VM_NAME}:/tmp/add-seo-creds.sh" --zone=$ZONE

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upload script" -ForegroundColor Red
    Remove-Item $tempScript -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Executing script on VM..." -ForegroundColor Gray
# Convert line endings and execute
gcloud compute ssh $VM_NAME --zone=$ZONE --command="sed -i 's/\r$//' /tmp/add-seo-creds.sh && chmod +x /tmp/add-seo-creds.sh && /tmp/add-seo-creds.sh && rm /tmp/add-seo-creds.sh"

# Clean up local temp file
Remove-Item $tempScript -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Credentials added successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔄 Restart backend to apply changes:" -ForegroundColor Yellow
    Write-Host "   gcloud compute ssh $VM_NAME --zone=$ZONE --command='cd /opt/jobmatch && docker-compose restart app'" -ForegroundColor White
} else {
    Write-Host "❌ Failed to add credentials" -ForegroundColor Red
    exit 1
}

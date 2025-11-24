# Setup Search Console Credentials for .env
# Converts JSON credentials file to single-line format for .env

$ErrorActionPreference = "Stop"

$credentialsFile = "secrets/search-console-credentials.json"
$envFile = ".env"

if (-not (Test-Path $credentialsFile)) {
    Write-Host "Error: Credentials file not found: $credentialsFile" -ForegroundColor Red
    Write-Host "Run: gcloud iam service-accounts keys create $credentialsFile --iam-account=jobmatch-seo-service@futurelink-private-112912460.iam.gserviceaccount.com" -ForegroundColor Yellow
    exit 1
}

# Read credentials JSON
$credentials = Get-Content $credentialsFile | ConvertFrom-Json

# Convert to single-line JSON with escaped quotes
$credentialsJson = $credentials | ConvertTo-Json -Compress -Depth 10
$credentialsEscaped = $credentialsJson -replace '"', '\"'

# Read existing .env or create new
$envContent = @()
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile
    # Remove existing GOOGLE_SEARCH_CONSOLE_CREDENTIALS if present
    $envContent = $envContent | Where-Object { $_ -notmatch "^GOOGLE_SEARCH_CONSOLE_CREDENTIALS=" }
}

# Add new credentials
$envContent += "GOOGLE_SEARCH_CONSOLE_CREDENTIALS='$credentialsEscaped'"
$envContent += "GOOGLE_SEARCH_CONSOLE_SITE_URL='https://jobmatch.zip'"

# Write back to .env
$envContent | Set-Content $envFile

Write-Host "✅ Search Console credentials added to .env" -ForegroundColor Green
Write-Host ""
Write-Host "Service Account Email: $($credentials.client_email)" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANT: Grant Search Console access manually:" -ForegroundColor Yellow
Write-Host "   1. Go to https://search.google.com/search-console" -ForegroundColor Yellow
Write-Host "   2. Select property: https://jobmatch.zip" -ForegroundColor Yellow
Write-Host "   3. Go to Settings > Users and permissions" -ForegroundColor Yellow
Write-Host "   4. Click 'Add User'" -ForegroundColor Yellow
Write-Host "   5. Enter: $($credentials.client_email)" -ForegroundColor Yellow
Write-Host "   6. Select 'Full' permission" -ForegroundColor Yellow
Write-Host "   7. Click 'Add'" -ForegroundColor Yellow
Write-Host ""


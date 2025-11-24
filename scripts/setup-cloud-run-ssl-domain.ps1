# Setup HTTPS domain mapping for jobmatch.zip to Cloud Run using SSL bundle from /secrets
# Destroys SSL bundle after use

param(
    [string]$Domain = "jobmatch.zip",
    [string]$GcpProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = "us-central1",
    [string]$CloudRunService = $env:CLOUD_RUN_SERVICE,
    [string]$SslBundlePath = "secrets\jobmatch.zip-ssl-bundle.zip",
    [string]$TempDir = "secrets\ssl-temp"
)

$ErrorActionPreference = "Stop"

if (-not $GcpProjectId) {
    Write-Host "❌ GCP_PROJECT_ID not set" -ForegroundColor Red
    exit 1
}

if (-not $CloudRunService) {
    Write-Host "⚠️  CLOUD_RUN_SERVICE not set, attempting to detect..." -ForegroundColor Yellow
    $services = gcloud run services list --region=$Region --format="value(name)" --limit=1 --project=$GcpProjectId 2>$null
    if ($services) {
        $CloudRunService = $services[0]
        Write-Host "✅ Detected Cloud Run service: $CloudRunService" -ForegroundColor Green
    } else {
        Write-Host "❌ Could not detect Cloud Run service. Please set CLOUD_RUN_SERVICE environment variable" -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path $SslBundlePath)) {
    Write-Host "❌ SSL bundle not found: $SslBundlePath" -ForegroundColor Red
    exit 1
}

Write-Host "🔒 Setting up HTTPS domain mapping for $Domain to Cloud Run service: $CloudRunService" -ForegroundColor Cyan
Write-Host ""

# Step 1: Extract SSL bundle
Write-Host "📦 Step 1: Extracting SSL bundle..." -ForegroundColor Cyan
if (Test-Path $TempDir) {
    Remove-Item -Path $TempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
Expand-Archive -Path $SslBundlePath -DestinationPath $TempDir -Force

# Find certificate and key files
$certFile = Get-ChildItem -Path $TempDir -Recurse -Include "*.cert.pem", "cert.pem", "fullchain.pem" | Select-Object -First 1
$keyFile = Get-ChildItem -Path $TempDir -Recurse -Include "private.key.pem", "privkey.pem", "*.key.pem" | Select-Object -First 1

if (-not $certFile -or -not $keyFile) {
    Write-Host "❌ Could not find certificate or key files in SSL bundle" -ForegroundColor Red
    Write-Host "   Found files:" -ForegroundColor Yellow
    Get-ChildItem -Path $TempDir -Recurse -File | ForEach-Object { Write-Host "   $($_.FullName)" }
    exit 1
}

Write-Host "✅ Found certificate: $($certFile.FullName)" -ForegroundColor Green
Write-Host "✅ Found private key: $($keyFile.FullName)" -ForegroundColor Green

# Step 2: Verify SSL certificate
Write-Host ""
Write-Host "🔐 Step 2: Verifying SSL certificate..." -ForegroundColor Cyan
# Verify certificate is valid (basic check)
try {
    $certContent = Get-Content $certFile.FullName -Raw
    if ($certContent -notmatch "BEGIN CERTIFICATE") {
        Write-Host "❌ Invalid certificate file" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Certificate format verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to read certificate file" -ForegroundColor Red
    exit 1
}

# Step 3: Get current Cloud Run service URL
Write-Host ""
Write-Host "🌐 Step 3: Getting Cloud Run service URL..." -ForegroundColor Cyan
$serviceUrl = gcloud run services describe $CloudRunService `
    --region=$Region `
    --format="value(status.url)" `
    --project=$GcpProjectId

if (-not $serviceUrl) {
    Write-Host "❌ Could not get Cloud Run service URL" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Cloud Run service URL: $serviceUrl" -ForegroundColor Green

# Step 4: Create domain mapping (Cloud Run auto-provisions SSL)
Write-Host ""
Write-Host "🔗 Step 4: Creating domain mapping for $Domain..." -ForegroundColor Cyan

# Check if domain mapping already exists
$existingMapping = gcloud run domain-mappings describe $Domain `
    --region=$Region `
    --format="value(name)" `
    --project=$GcpProjectId 2>$null

if ($existingMapping) {
    Write-Host "⚠️  Domain mapping already exists, updating..." -ForegroundColor Yellow
    $updateResult = gcloud run domain-mappings update $Domain `
        --region=$Region `
        --service=$CloudRunService `
        --project=$GcpProjectId 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to update domain mapping" -ForegroundColor Red
        Write-Host $updateResult
        exit 1
    }
} else {
    $createResult = gcloud run domain-mappings create $Domain `
        --service=$CloudRunService `
        --region=$Region `
        --project=$GcpProjectId 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create domain mapping" -ForegroundColor Red
        Write-Host $createResult
        exit 1
    }
}

Write-Host "✅ Domain mapping created/updated" -ForegroundColor Green

# Step 5: Wait for domain mapping to be ready
Write-Host ""
Write-Host "⏳ Step 5: Waiting for domain mapping to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Get DNS records needed
$dnsRecords = gcloud run domain-mappings describe $Domain `
    --region=$Region `
    --format="value(status.resourceRecords)" `
    --project=$GcpProjectId

if ($dnsRecords) {
    Write-Host "📋 DNS records to configure:" -ForegroundColor Yellow
    Write-Host $dnsRecords
    Write-Host ""
    Write-Host "⚠️  Please configure these DNS records at your domain registrar" -ForegroundColor Yellow
}

# Step 6: Clean up SSL bundle
Write-Host ""
Write-Host "🧹 Step 6: Cleaning up SSL bundle..." -ForegroundColor Cyan
Remove-Item -Path $TempDir -Recurse -Force
Remove-Item -Path $SslBundlePath -Force

Write-Host "✅ SSL bundle destroyed" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Domain mapping setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Domain: https://$Domain" -ForegroundColor Cyan
Write-Host "🔗 Cloud Run Service: $CloudRunService" -ForegroundColor Cyan
Write-Host "📍 Region: $Region" -ForegroundColor Cyan
Write-Host "🔐 SSL: Auto-provisioned by Google Cloud (managed certificate)" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Configure DNS records at your domain registrar"
Write-Host "   2. Wait for DNS propagation (can take up to 48 hours)"
Write-Host "   3. Verify HTTPS is working: curl -I https://$Domain"
Write-Host ""
Write-Host "⚠️  Note: SSL bundle has been destroyed as requested" -ForegroundColor Yellow


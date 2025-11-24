# Deploy Backend Only to Production VM
# Usage: .\scripts\deploy-backend-only.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Backend to jobmatch.zip..." -ForegroundColor Cyan
Write-Host ""

# Configuration
$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }

# Step 1: Create backend package
Write-Host "📦 Step 1: Creating backend package..." -ForegroundColor Cyan
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
$backendDir = Join-Path $tempDir "backend"

# Copy backend files (exclude cache and compiled files)
Get-ChildItem -Path "backend" -Recurse | Where-Object {
    $_.FullName -notmatch '__pycache__' -and
    $_.FullName -notmatch '\.pyc$' -and
    $_.FullName -notmatch '\.pyo$'
} | ForEach-Object {
    $relativePath = $_.FullName.Substring((Resolve-Path "backend").Path.Length + 1)
    $destPath = Join-Path $backendDir $relativePath
    $destDir = Split-Path $destPath -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item $_.FullName -Destination $destPath -Force
}

# Create zip
$zipFile = Join-Path $tempDir "backend.zip"
Compress-Archive -Path $backendDir -DestinationPath $zipFile -Force

Write-Host "✅ Package created: backend.zip" -ForegroundColor Green
Write-Host ""

# Step 2: Upload and deploy
Write-Host "📤 Step 2: Uploading to VM..." -ForegroundColor Cyan
gcloud compute scp $zipFile "${VM_NAME}:/tmp/backend.zip" --zone=$ZONE

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    Remove-Item $tempDir -Recurse -Force
    exit 1
}

Write-Host "✅ Upload complete" -ForegroundColor Green
Write-Host ""

# Step 3: Deploy on VM
Write-Host "🔧 Step 3: Deploying on VM..." -ForegroundColor Cyan
$deployCmd = @"
cd /opt/jobmatch
echo "Backing up existing backend..."
mv backend backend.backup.`$(date +%Y%m%d_%H%M%S) || true

echo "Extracting new backend..."
unzip -q /tmp/backend.zip -d /opt/jobmatch
rm /tmp/backend.zip

echo "Restarting backend service..."
sudo systemctl restart jobmatch-backend
sleep 3

echo ""
echo "Checking backend status..."
sudo systemctl status jobmatch-backend --no-pager | head -15
"@

gcloud compute ssh $VM_NAME --zone=$ZONE --command=$deployCmd

Write-Host ""
Write-Host "✅ Backend deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🧪 Test magic link:" -ForegroundColor Cyan
Write-Host "   .\scripts\test-magic-link-send.ps1 -Email me@myl.zip" -ForegroundColor White

# Cleanup
Remove-Item $tempDir -Recurse -Force


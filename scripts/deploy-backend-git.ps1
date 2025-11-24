# Deploy Backend Using Git (respects .gitignore)
# This ensures only tracked files are deployed, matching what's in git

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Backend via Git..." -ForegroundColor Cyan
Write-Host ""

# Configuration
$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }

# Step 1: Create archive of tracked files only
Write-Host "📦 Step 1: Creating backend archive from git..." -ForegroundColor Cyan

# Use git archive to get only tracked files (respects .gitignore)
$archiveFile = "backend-git.tar.gz"
git archive --format=tar.gz --prefix=backend/ HEAD backend/ > $archiveFile

if (-not (Test-Path $archiveFile)) {
    Write-Host "❌ Failed to create git archive" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $archiveFile).Length / 1MB
Write-Host "✅ Archive created: $archiveFile ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
Write-Host ""

# Step 2: Upload to VM
Write-Host "📤 Step 2: Uploading to VM..." -ForegroundColor Cyan
gcloud compute scp $archiveFile "${VM_NAME}:/tmp/backend-git.tar.gz" --zone=$ZONE

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    Remove-Item $archiveFile -Force
    exit 1
}

Write-Host "✅ Upload complete" -ForegroundColor Green
Write-Host ""

# Step 3: Deploy on VM
Write-Host "🔧 Step 3: Deploying on VM..." -ForegroundColor Cyan
$deployCmd = @"
cd /opt/jobmatch
echo "Backing up existing backend..."
if [ -d backend ]; then
    mv backend backend.backup.`$(date +%Y%m%d_%H%M%S)
fi

echo "Extracting new backend from git archive..."
tar -xzf /tmp/backend-git.tar.gz -C /opt/jobmatch
rm /tmp/backend-git.tar.gz

echo "Ensuring __init__.py files exist..."
touch backend/__init__.py
touch backend/api/__init__.py 2>/dev/null || true

echo "Restarting backend service..."
sudo systemctl restart jobmatch-backend
sleep 5

echo ""
echo "Backend status:"
sudo systemctl status jobmatch-backend --no-pager | head -12
"@

gcloud compute ssh $VM_NAME --zone=$ZONE --command=$deployCmd

Write-Host ""
Write-Host "✅ Backend deployment complete!" -ForegroundColor Green

# Cleanup
Remove-Item $archiveFile -Force

Write-Host ""
Write-Host "🧪 Test magic link:" -ForegroundColor Cyan
Write-Host "   .\scripts\test-magic-link-send.ps1 -Email me@myl.zip" -ForegroundColor White


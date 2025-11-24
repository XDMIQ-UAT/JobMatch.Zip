# Deploy Frontend Only to Production (jobmatch.zip)
# Usage: .\scripts\deploy-frontend-only.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Frontend to jobmatch.zip..." -ForegroundColor Cyan
Write-Host ""

# Configuration
$VM_NAME = if ($env:VM_NAME) { $env:VM_NAME } else { "jobmatch-vm" }
$ZONE = if ($env:GCP_ZONE) { $env:GCP_ZONE } else { "us-central1-a" }

# Step 1: Verify frontend build exists
Write-Host "📦 Step 1: Verifying frontend build..." -ForegroundColor Cyan
Set-Location frontend

if (-not (Test-Path ".next")) {
    Write-Host "❌ Build not found. Building frontend..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
} else {
    Write-Host "✅ Build found" -ForegroundColor Green
}

Set-Location ..

# Step 2: Get VM IP
Write-Host "`n🌐 Step 2: Getting VM information..." -ForegroundColor Cyan
try {
    $VM_IP = gcloud compute instances describe $VM_NAME --zone=$ZONE --format="value(networkInterfaces[0].accessConfigs[0].natIP)" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to get VM IP"
    }
    Write-Host "   VM: $VM_NAME" -ForegroundColor White
    Write-Host "   IP: $VM_IP" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to get VM IP. Make sure gcloud is configured and VM exists." -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Create deployment package (frontend only)
Write-Host "`n📦 Step 3: Creating deployment package..." -ForegroundColor Cyan
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
$deployDir = Join-Path $tempDir "frontend-deploy"

New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

# Copy frontend files
Write-Host "   Copying frontend files..." -ForegroundColor Gray
Copy-Item -Path "frontend\.next\standalone\*" -Destination "$deployDir" -Recurse -Force
Copy-Item -Path "frontend\.next\static" -Destination "$deployDir\.next\static" -Recurse -Force
Copy-Item -Path "frontend\public" -Destination "$deployDir\public" -Recurse -Force

# Create zip
$zipFile = "frontend-deploy.zip"
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

Write-Host "   Creating zip archive..." -ForegroundColor Gray
Compress-Archive -Path "$deployDir\*" -DestinationPath $zipFile -Force

$zipSize = [math]::Round((Get-Item $zipFile).Length / 1MB, 2)
Write-Host "✅ Package created: $zipFile ($zipSize MB)" -ForegroundColor Green

# Cleanup temp directory
Remove-Item -Path $tempDir -Recurse -Force

# Step 4: Upload to VM
Write-Host "`n📤 Step 4: Uploading to VM..." -ForegroundColor Cyan
gcloud compute scp $zipFile "${VM_NAME}:/tmp/" --zone=$ZONE
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
    exit 1
}
Write-Host "✅ Upload complete" -ForegroundColor Green

# Step 5: Deploy on VM
Write-Host "`n🔧 Step 5: Deploying on VM..." -ForegroundColor Cyan
$deployCmd = @"
cd /opt/jobmatch/frontend
echo 'Stopping frontend service...'
sudo supervisorctl stop frontend 2>/dev/null || systemctl stop frontend 2>/dev/null || pkill -f 'next start' || true
echo 'Extracting new frontend files...'
sudo unzip -o /tmp/frontend-deploy.zip -d /opt/jobmatch/frontend
sudo rm -f /tmp/frontend-deploy.zip
echo 'Setting correct permissions...'
sudo chown -R $(whoami):$(whoami) /opt/jobmatch/frontend 2>/dev/null || true
echo 'Restarting frontend service...'
sudo supervisorctl restart frontend 2>/dev/null || systemctl restart frontend 2>/dev/null || (cd /opt/jobmatch/frontend && NODE_ENV=production PORT=3000 nohup npm run start > /tmp/frontend.log 2>&1 &)
echo 'Waiting for service to start...'
sleep 5
sudo supervisorctl status frontend 2>/dev/null || systemctl status frontend 2>/dev/null || echo 'Service started in background'
echo '✅ Frontend deployment complete!'
"@

# Save deploy command to temp file with Unix line endings
$tempScript = New-TemporaryFile
# Convert Windows CRLF to Unix LF
$unixContent = $deployCmd -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($tempScript, $unixContent + "`n", [System.Text.Encoding]::ASCII)

# Upload and execute
gcloud compute scp $tempScript "${VM_NAME}:/tmp/deploy-frontend.sh" --zone=$ZONE
gcloud compute ssh $VM_NAME --zone=$ZONE --command="chmod +x /tmp/deploy-frontend.sh && sudo /tmp/deploy-frontend.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
}

# Cleanup
Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
Remove-Item $tempScript -Force -ErrorAction SilentlyContinue

Write-Host "`n🌐 Frontend deployed to: https://jobmatch.zip" -ForegroundColor Cyan
Write-Host "`n📋 Test the site:" -ForegroundColor Yellow
Write-Host "   " -NoNewline
Write-Host "https://jobmatch.zip" -ForegroundColor Blue
Write-Host "`n📋 Other test URLs:" -ForegroundColor Yellow
Write-Host "   https://jobmatch.zip/manifest.json" -ForegroundColor White
Write-Host "   https://jobmatch.zip/sw.js" -ForegroundColor White


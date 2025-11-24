# Final fix for manifest.json and sw.js on production VM
# Uses a bash script file to avoid line ending issues

param(
    [string]$VmName = "jobmatch-vm",
    [string]$Zone = "us-central1-a"
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Fixing manifest.json and sw.js on production VM..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload static files
Write-Host "📤 Step 1: Uploading static files..." -ForegroundColor Cyan
gcloud compute scp "frontend\public\manifest.json" "frontend\public\sw.js" "${VmName}:/tmp/" --zone=$Zone

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Files uploaded" -ForegroundColor Green
Write-Host ""

# Step 2: Upload bash script
Write-Host "📤 Step 2: Uploading configuration script..." -ForegroundColor Cyan
gcloud compute scp "scripts\fix-manifest-sw.sh" "${VmName}:/tmp/fix-manifest-sw.sh" --zone=$Zone

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Script upload failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Script uploaded" -ForegroundColor Green
Write-Host ""

# Step 3: Execute script
Write-Host "🌐 Step 3: Executing configuration script..." -ForegroundColor Cyan
gcloud compute ssh $VmName --zone=$Zone --command="chmod +x /tmp/fix-manifest-sw.sh && sudo /tmp/fix-manifest-sw.sh"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Configuration failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Fix applied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Testing endpoints..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Test the endpoints
try {
    $manifestResponse = Invoke-WebRequest -Uri "https://jobmatch.zip/manifest.json" -UseBasicParsing -TimeoutSec 10
    $swResponse = Invoke-WebRequest -Uri "https://jobmatch.zip/sw.js" -UseBasicParsing -TimeoutSec 10
    
    if ($manifestResponse.StatusCode -eq 200 -and $swResponse.StatusCode -eq 200) {
        Write-Host "✅ manifest.json: HTTP $($manifestResponse.StatusCode)" -ForegroundColor Green
        Write-Host "✅ sw.js: HTTP $($swResponse.StatusCode)" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 All fixed! The files are now accessible." -ForegroundColor Green
    } else {
        Write-Host "⚠️  manifest.json: HTTP $($manifestResponse.StatusCode)" -ForegroundColor Yellow
        Write-Host "⚠️  sw.js: HTTP $($swResponse.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not verify endpoints: $_" -ForegroundColor Yellow
    Write-Host "Please check manually: https://jobmatch.zip/manifest.json and https://jobmatch.zip/sw.js" -ForegroundColor Yellow
}


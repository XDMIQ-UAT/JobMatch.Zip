# Quick fix script to upload manifest.json and sw.js to VM and configure Nginx
# This bypasses the deployment issue and serves files directly

param(
    [string]$VmName = "jobmatch-vm",
    [string]$Zone = "us-central1-a"
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Fixing manifest.json and sw.js on production VM..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload static files
Write-Host "📤 Step 1: Uploading static files..." -ForegroundColor Cyan

# Create temp directory
$tempDir = Join-Path $env:TEMP "jobmatch-static-fix"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Copy manifest.json
Copy-Item -Path "frontend\public\manifest.json" -Destination "$tempDir\manifest.json" -Force
Write-Host "✓ Copied manifest.json" -ForegroundColor Green

# Copy sw.js
Copy-Item -Path "frontend\public\sw.js" -Destination "$tempDir\sw.js" -Force
Write-Host "✓ Copied sw.js" -ForegroundColor Green

# Upload to VM
Write-Host "📤 Uploading to VM..." -ForegroundColor Cyan
gcloud compute scp "$tempDir\manifest.json" "$tempDir\sw.js" "${VmName}:/tmp/" --zone=$Zone

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Files uploaded" -ForegroundColor Green
Write-Host ""

# Step 2: Create Nginx config update script
Write-Host "🌐 Step 2: Configuring Nginx to serve static files..." -ForegroundColor Cyan

$nginxUpdateScript = @'
#!/bin/bash
set -e

# Create static files directory
sudo mkdir -p /var/www/jobmatch/static

# Copy files to static directory
sudo cp /tmp/manifest.json /var/www/jobmatch/static/
sudo cp /tmp/sw.js /var/www/jobmatch/static/
sudo chown -R www-data:www-data /var/www/jobmatch/static
sudo chmod 644 /var/www/jobmatch/static/*

# Backup current nginx config
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)

# Check if nginx config exists
if [ -f /etc/nginx/sites-available/jobmatch ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/jobmatch"
else
    NGINX_CONFIG="/etc/nginx/sites-available/default"
fi

# Add static file locations before the main location block
sudo sed -i '/location \/ {/i\
    # Static files - manifest.json and sw.js\
    location = /manifest.json {\
        root /var/www/jobmatch/static;\
        add_header Content-Type "application/manifest+json";\
        add_header Cache-Control "public, max-age=3600, must-revalidate";\
        access_log off;\
    }\
\
    location = /sw.js {\
        root /var/www/jobmatch/static;\
        add_header Content-Type "application/javascript";\
        add_header Service-Worker-Allowed "/";\
        add_header Cache-Control "public, max-age=3600, must-revalidate";\
        access_log off;\
    }\
' "$NGINX_CONFIG"

# Test nginx config
sudo nginx -t

if [ $? -eq 0 ]; then
    # Reload nginx
    sudo systemctl reload nginx
    echo "✅ Nginx configured and reloaded"
else
    echo "❌ Nginx config test failed, restoring backup"
    sudo cp "$NGINX_CONFIG.backup."* "$NGINX_CONFIG" 2>/dev/null || true
    exit 1
fi
'@

# Write script to temp file
$scriptFile = Join-Path $tempDir "update-nginx.sh"
$nginxUpdateScript | Set-Content -Path $scriptFile -Encoding UTF8

# Upload and execute script
Write-Host "📤 Uploading Nginx update script..." -ForegroundColor Cyan
gcloud compute scp "$scriptFile" "${VmName}:/tmp/update-nginx.sh" --zone=$Zone

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Script upload failed" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Executing Nginx configuration..." -ForegroundColor Cyan
# Execute commands directly instead of using a script file
gcloud compute ssh $VmName --zone=$Zone --command="
set -e
sudo mkdir -p /var/www/jobmatch/static
sudo cp /tmp/manifest.json /var/www/jobmatch/static/
sudo cp /tmp/sw.js /var/www/jobmatch/static/
sudo chown -R www-data:www-data /var/www/jobmatch/static
sudo chmod 644 /var/www/jobmatch/static/*
echo 'Files copied to static directory'
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Nginx configuration failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Fix applied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Testing endpoints..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# Test the endpoints
$manifestTest = curl -s -o $null -w "%{http_code}" https://jobmatch.zip/manifest.json
$swTest = curl -s -o $null -w "%{http_code}" https://jobmatch.zip/sw.js

if ($manifestTest -eq "200" -and $swTest -eq "200") {
    Write-Host "✅ manifest.json: HTTP $manifestTest" -ForegroundColor Green
    Write-Host "✅ sw.js: HTTP $swTest" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 All fixed! The files should now be accessible." -ForegroundColor Green
} else {
    Write-Host "⚠️  manifest.json: HTTP $manifestTest" -ForegroundColor Yellow
    Write-Host "⚠️  sw.js: HTTP $swTest" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Files uploaded but may need Nginx reload. Check manually." -ForegroundColor Yellow
}

# Cleanup
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue


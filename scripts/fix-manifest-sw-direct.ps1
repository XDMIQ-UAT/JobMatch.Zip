# Direct fix for manifest.json and sw.js on production VM
# Updates Nginx config to serve static files directly

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

# Step 2: Execute commands on VM to set up static files and update Nginx
Write-Host "🌐 Step 2: Configuring static files and Nginx..." -ForegroundColor Cyan

$commands = @"
set -e
# Create static directory
sudo mkdir -p /var/www/jobmatch/static
sudo cp /tmp/manifest.json /var/www/jobmatch/static/
sudo cp /tmp/sw.js /var/www/jobmatch/static/
sudo chown -R www-data:www-data /var/www/jobmatch/static
sudo chmod 644 /var/www/jobmatch/static/*

# Find nginx config
if [ -f /etc/nginx/sites-available/jobmatch ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/jobmatch"
elif [ -f /etc/nginx/sites-available/default ]; then
    NGINX_CONFIG="/etc/nginx/sites-available/default"
else
    echo "❌ Could not find nginx config"
    exit 1
fi

# Backup config
sudo cp "`$NGINX_CONFIG" "`$NGINX_CONFIG.backup.`$(date +%Y%m%d_%H%M%S)"

# Check if static file locations already exist
if grep -q "location = /manifest.json" "`$NGINX_CONFIG"; then
    echo "⚠️  Static file locations already exist, updating..."
    # Remove old entries
    sudo sed -i '/location = \/manifest.json/,/^    }$/d' "`$NGINX_CONFIG"
    sudo sed -i '/location = \/sw.js/,/^    }$/d' "`$NGINX_CONFIG"
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
' "`$NGINX_CONFIG"

# Test nginx config
if sudo nginx -t; then
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded successfully"
else
    echo "❌ Nginx config test failed"
    exit 1
fi
"@

# Execute commands - escape $ signs for PowerShell
$commandsEscaped = $commands -replace '\$', '`$'
gcloud compute ssh $VmName --zone=$Zone --command=$commandsEscaped

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


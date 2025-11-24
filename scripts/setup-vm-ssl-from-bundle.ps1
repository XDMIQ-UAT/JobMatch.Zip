# Setup HTTPS for jobmatch.zip domain on GCP VM using SSL bundle from /secrets
# Destroys SSL bundle after use
# DNS should already point to VM IP address

param(
    [string]$VmName = "jobmatch-vm",
    [string]$Zone = "us-central1-a",
    [string]$Domain = "jobmatch.zip",
    [string]$SslBundlePath = "secrets\jobmatch.zip-ssl-bundle.zip",
    [string]$TempDir = "secrets\ssl-temp",
    [string]$GcpProjectId = $env:GCP_PROJECT_ID
)

$ErrorActionPreference = "Stop"

# Auto-detect GCP project ID if not set
if (-not $GcpProjectId) {
    $GcpProjectId = gcloud config get-value project 2>$null
    if ($GcpProjectId) {
        Write-Host "✅ Auto-detected GCP Project ID: $GcpProjectId" -ForegroundColor Green
    }
}

Write-Host "🔒 Setting up HTTPS for $Domain on VM using SSL bundle..." -ForegroundColor Cyan
Write-Host ""

# Check if SSL bundle exists
if (-not (Test-Path $SslBundlePath)) {
    Write-Host "❌ SSL bundle not found: $SslBundlePath" -ForegroundColor Red
    exit 1
}

# Get VM IP
try {
    if ($GcpProjectId) {
        $vmIp = gcloud compute instances describe $VmName --zone=$Zone --project=$GcpProjectId --format="value(networkInterfaces[0].accessConfigs[0].natIP)" 2>$null
    } else {
        $vmIp = gcloud compute instances describe $VmName --zone=$Zone --format="value(networkInterfaces[0].accessConfigs[0].natIP)" 2>$null
    }
    if ($vmIp) {
        Write-Host "✅ VM IP: $vmIp" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Could not get VM IP automatically" -ForegroundColor Yellow
        Write-Host "   Please ensure VM exists and gcloud is configured" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not get VM IP automatically" -ForegroundColor Yellow
}
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
$chainFile = Get-ChildItem -Path $TempDir -Recurse -Include "chain.pem", "*.chain.pem" | Select-Object -First 1

if (-not $certFile -or -not $keyFile) {
    Write-Host "❌ Could not find certificate or key files in SSL bundle" -ForegroundColor Red
    Write-Host "   Found files:" -ForegroundColor Yellow
    Get-ChildItem -Path $TempDir -Recurse -File | ForEach-Object { Write-Host "   $($_.FullName)" }
    exit 1
}

Write-Host "✅ Found certificate: $($certFile.FullName)" -ForegroundColor Green
Write-Host "✅ Found private key: $($keyFile.FullName)" -ForegroundColor Green
if ($chainFile) {
    Write-Host "✅ Found chain: $($chainFile.FullName)" -ForegroundColor Green
}

# Step 2: Verify certificate
Write-Host ""
Write-Host "🔐 Step 2: Verifying SSL certificate..." -ForegroundColor Cyan
try {
    $certContent = Get-Content $certFile.FullName -Raw
    if ($certContent -notmatch "BEGIN CERTIFICATE") {
        Write-Host "⚠️  Warning: Certificate format may be invalid, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Certificate format verified" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Warning: Could not verify certificate format" -ForegroundColor Yellow
}

# Step 3: Create fullchain if chain exists
if ($chainFile) {
    Write-Host ""
    Write-Host "🔗 Step 3: Creating fullchain certificate..." -ForegroundColor Cyan
    $fullchainContent = (Get-Content $certFile.FullName -Raw) + (Get-Content $chainFile.FullName -Raw)
    $fullchainFile = Join-Path $TempDir "fullchain.pem"
    Set-Content -Path $fullchainFile -Value $fullchainContent
} else {
    $fullchainFile = $certFile.FullName
}

# Step 4: Upload certificates to VM
Write-Host ""
Write-Host "📤 Step 4: Uploading certificates to VM..." -ForegroundColor Cyan

# Create SSL directory on VM
$createDirResult = gcloud compute ssh $VmName --zone=$Zone --command="sudo mkdir -p /etc/nginx/ssl/$Domain && sudo chmod 700 /etc/nginx/ssl/$Domain" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to connect to VM. Please check:" -ForegroundColor Red
    Write-Host "   1. VM name: $VmName" -ForegroundColor Yellow
    Write-Host "   2. Zone: $Zone" -ForegroundColor Yellow
    Write-Host "   3. gcloud authentication" -ForegroundColor Yellow
    exit 1
}

# Upload certificate files
gcloud compute scp "$fullchainFile" "${VmName}:/tmp/fullchain.pem" --zone=$Zone
gcloud compute scp "$($keyFile.FullName)" "${VmName}:/tmp/privkey.pem" --zone=$Zone
if ($chainFile) {
    gcloud compute scp "$($chainFile.FullName)" "${VmName}:/tmp/chain.pem" --zone=$Zone
}

# Move certificates to proper location and set permissions
$moveCmd = @"
sudo mv /tmp/fullchain.pem /etc/nginx/ssl/$Domain/fullchain.pem
sudo mv /tmp/privkey.pem /etc/nginx/ssl/$Domain/privkey.pem
if [ -f /tmp/chain.pem ]; then
    sudo mv /tmp/chain.pem /etc/nginx/ssl/$Domain/chain.pem
fi
sudo chmod 600 /etc/nginx/ssl/$Domain/privkey.pem
sudo chmod 644 /etc/nginx/ssl/$Domain/fullchain.pem
if [ -f /etc/nginx/ssl/$Domain/chain.pem ]; then
    sudo chmod 644 /etc/nginx/ssl/$Domain/chain.pem
fi
sudo chown root:root /etc/nginx/ssl/$Domain/*
"@

gcloud compute ssh $VmName --zone=$Zone --command=$moveCmd

Write-Host "✅ Certificates uploaded to VM" -ForegroundColor Green

# Step 5: Configure Nginx
Write-Host ""
Write-Host "🌐 Step 5: Configuring Nginx with SSL certificates..." -ForegroundColor Cyan

$nginxConfig = @'
server {
    listen 80;
    server_name JOBMATCH_DOMAIN www.JOBMATCH_DOMAIN;

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name JOBMATCH_DOMAIN www.JOBMATCH_DOMAIN;

    # SSL certificates from bundle
    ssl_certificate /etc/nginx/ssl/JOBMATCH_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/JOBMATCH_DOMAIN/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
'@

# Replace domain placeholder
$nginxConfig = $nginxConfig -replace 'JOBMATCH_DOMAIN', $Domain

# Create nginx config file locally first, then upload
$nginxConfigFile = Join-Path $env:TEMP "nginx-jobmatch.conf"
$nginxConfig | Set-Content -Path $nginxConfigFile -Encoding UTF8

# Upload config file
gcloud compute scp "$nginxConfigFile" "${VmName}:/tmp/nginx-jobmatch.conf" --zone=$Zone

$nginxSetupCmd = @"
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
sudo mv /tmp/nginx-jobmatch.conf /etc/nginx/sites-available/jobmatch
sudo ln -sf /etc/nginx/sites-available/jobmatch /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
"@

# Clean up local temp file
Remove-Item -Path $nginxConfigFile -Force -ErrorAction SilentlyContinue

$nginxResult = gcloud compute ssh $VmName --zone=$Zone --command=$nginxSetupCmd 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Nginx configured and reloaded" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to configure Nginx" -ForegroundColor Red
    Write-Host $nginxResult
    exit 1
}

# Step 6: Optional - Verify DNS with Cloud DNS
Write-Host ""
Write-Host "🔍 Step 6: Verifying DNS configuration..." -ForegroundColor Cyan

if ($GcpProjectId) {
    $zoneName = gcloud dns managed-zones list --filter="dnsName:$Domain" --format="value(name)" --project=$GcpProjectId 2>$null | Select-Object -First 1
    if ($zoneName) {
        Write-Host "✅ Found Cloud DNS zone: $zoneName" -ForegroundColor Green
        $dnsRecords = gcloud dns record-sets list --zone=$zoneName --filter="name:$Domain." --format="value(rrdatas)" --project=$GcpProjectId 2>$null
        if ($dnsRecords) {
            Write-Host "   DNS A record: $dnsRecords" -ForegroundColor Cyan
            if ($vmIp -and $dnsRecords -match [regex]::Escape($vmIp)) {
                Write-Host "   ✅ DNS points to VM IP" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  DNS may not point to VM IP ($vmIp)" -ForegroundColor Yellow
            }
        }
    }
}

# Step 7: Clean up SSL bundle
Write-Host ""
Write-Host "🧹 Step 7: Cleaning up SSL bundle..." -ForegroundColor Cyan
Remove-Item -Path $TempDir -Recurse -Force
Remove-Item -Path $SslBundlePath -Force

Write-Host "✅ SSL bundle destroyed" -ForegroundColor Green

Write-Host ""
Write-Host "✅ SSL setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Your application should now be available at:" -ForegroundColor Cyan
Write-Host "   https://$Domain" -ForegroundColor White
Write-Host "   https://www.$Domain" -ForegroundColor White
Write-Host ""
Write-Host "📋 Certificate Details:" -ForegroundColor Cyan
Write-Host "   Certificate: /etc/nginx/ssl/$Domain/fullchain.pem" -ForegroundColor White
Write-Host "   Private Key: /etc/nginx/ssl/$Domain/privkey.pem" -ForegroundColor White
Write-Host ""
if ($vmIp) {
    Write-Host "🔍 Test HTTPS:" -ForegroundColor Cyan
    Write-Host "   curl -I https://$Domain" -ForegroundColor White
    Write-Host "   curl -I https://$Domain/health" -ForegroundColor White
}
Write-Host ""
Write-Host "⚠️  Note: SSL bundle has been destroyed as requested" -ForegroundColor Yellow


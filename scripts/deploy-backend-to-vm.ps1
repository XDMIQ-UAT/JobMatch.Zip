# Deploy Backend to VM - Full Redeployment
# Phases 2-6: Complete backend deployment with backup and validation
# VM: jobmatch.zip (146.190.208.67)

param(
    [string]$VMUser = "root",
    [string]$VMHost = "146.190.208.67",
    [string]$BackendPackage = "E:\JobFinder\backend-deployment.zip",
    [switch]$SkipBackup = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Backend to VM: $VMHost" -ForegroundColor Cyan
Write-Host ""

# Verify package exists
if (-not (Test-Path $BackendPackage)) {
    Write-Host "❌ Package not found: $BackendPackage" -ForegroundColor Red
    Write-Host "Run: .\scripts\create-backend-deployment-package.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Package: $BackendPackage" -ForegroundColor White
Write-Host ""

# Phase 2: Backup VM and stop services
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 2: Backup VM Backend & Stop Services" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipBackup) {
    Write-Host "🔄 Creating backup of existing backend..." -ForegroundColor Yellow
    
    $backupCmd = @"
cd /opt/jobmatch
if [ -d backend ]; then
    BACKUP_NAME=backend.backup.`$(date +%Y%m%d_%H%M%S)
    echo "Backing up to: `$BACKUP_NAME"
    mv backend `$BACKUP_NAME
    echo "✅ Backup created: `$BACKUP_NAME"
else
    echo "⚠️  No existing backend directory found - fresh installation"
fi
"@
    
    ssh "${VMUser}@${VMHost}" $backupCmd
    
    Write-Host ""
}

Write-Host "🛑 Stopping backend service..." -ForegroundColor Yellow

$stopCmd = @"
if systemctl list-units --type=service | grep -q jobmatch-backend; then
    sudo systemctl stop jobmatch-backend
    echo "✅ Backend service stopped"
else
    echo "⚠️  No jobmatch-backend service found - will configure later"
fi
"@

ssh "${VMUser}@${VMHost}" $stopCmd
Write-Host ""

# Phase 3: Deploy backend package
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 3: Deploy Backend Package" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📤 Uploading package to VM..." -ForegroundColor Yellow
scp $BackendPackage "${VMUser}@${VMHost}:/tmp/backend-deployment.zip"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Upload failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Upload complete" -ForegroundColor Green
Write-Host ""

Write-Host "📦 Extracting package on VM..." -ForegroundColor Yellow

$extractCmd = @"
cd /opt/jobmatch
echo "Extracting backend package..."
unzip -q /tmp/backend-deployment.zip -d /opt/jobmatch
rm /tmp/backend-deployment.zip

echo ""
echo "Verifying structure..."
if [ -d backend ]; then
    echo "✅ backend/ directory exists"
    if [ -f backend/main.py ]; then
        echo "✅ backend/main.py exists"
    else
        echo "❌ backend/main.py MISSING"
        exit 1
    fi
    if [ -d backend/database ]; then
        echo "✅ backend/database/ module exists"
    else
        echo "❌ backend/database/ MISSING"
        exit 1
    fi
    if [ -d backend/auth ]; then
        echo "✅ backend/auth/ module exists"
    else
        echo "❌ backend/auth/ MISSING"
        exit 1
    fi
else
    echo "❌ backend/ directory not found after extraction"
    exit 1
fi

echo ""
echo "Installing dependencies..."
cd backend
pip3 install -r requirements.txt --quiet

echo ""
echo "✅ Package deployed and dependencies installed"
"@

ssh "${VMUser}@${VMHost}" $extractCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Phase 4: Configuration check
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 4: Configuration & Environment" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔍 Checking environment configuration..." -ForegroundColor Yellow

$configCheckCmd = @"
cd /opt/jobmatch

echo "Checking .env file..."
if [ -f .env ]; then
    echo "✅ .env file exists"
    
    # Check critical variables
    if grep -q "DATABASE_URL" .env; then
        echo "✅ DATABASE_URL configured"
    else
        echo "⚠️  DATABASE_URL not set"
    fi
    
    if grep -q "AWS_ACCESS_KEY_ID" .env && grep -q "AWS_SECRET_ACCESS_KEY" .env; then
        echo "✅ AWS credentials configured"
    else
        echo "⚠️  AWS credentials not set (magic link email won't work)"
    fi
    
    if grep -q "SES_FROM_EMAIL" .env; then
        echo "✅ SES_FROM_EMAIL configured"
    else
        echo "⚠️  SES_FROM_EMAIL not set"
    fi
else
    echo "⚠️  No .env file found - using defaults"
    echo "   Create .env file with required variables:"
    echo "   - DATABASE_URL"
    echo "   - AWS_ACCESS_KEY_ID"
    echo "   - AWS_SECRET_ACCESS_KEY"
    echo "   - SES_FROM_EMAIL"
fi

echo ""
echo "Testing imports..."
cd /opt/jobmatch
python3 -c "from backend.database.connection import get_db; print('✅ database.connection import OK')" 2>&1
python3 -c "from backend.auth.social_auth import SocialAuthManager; print('✅ auth.social_auth import OK')" 2>&1
python3 -c "from backend.auth.email_provider import EmailProviderManager; print('✅ auth.email_provider import OK')" 2>&1
"@

ssh "${VMUser}@${VMHost}" $configCheckCmd
Write-Host ""

# Phase 5: Service restart and health checks
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 5: Service Restart & Health Checks" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔄 Starting backend service..." -ForegroundColor Yellow

$startCmd = @"
if systemctl list-units --type=service | grep -q jobmatch-backend; then
    sudo systemctl start jobmatch-backend
    sleep 3
    sudo systemctl status jobmatch-backend --no-pager | head -20
else
    echo "⚠️  No systemd service configured"
    echo "   Starting backend manually for testing..."
    cd /opt/jobmatch
    nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /var/log/jobmatch-backend.log 2>&1 &
    sleep 3
    echo "Backend started in background (PID: \$!)"
fi
"@

ssh "${VMUser}@${VMHost}" $startCmd
Write-Host ""

Write-Host "🏥 Running health checks..." -ForegroundColor Yellow

$healthCheckCmd = @"
echo "Testing health endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool 2>&1
echo ""

echo "Testing auth endpoint..."
curl -s http://localhost:8000/api/auth/user?anonymous_id=test 2>&1 | head -10
"@

ssh "${VMUser}@${VMHost}" $healthCheckCmd
Write-Host ""

# Phase 6: Validation summary
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PHASE 6: Deployment Validation" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Backend Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Test magic link endpoint:" -ForegroundColor White
Write-Host "     curl -X POST http://$VMHost/api/social-auth/magic-link/send -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\"}'" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Check backend logs:" -ForegroundColor White
Write-Host "     ssh ${VMUser}@${VMHost} 'journalctl -u jobmatch-backend -f'" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Verify database connection on VM" -ForegroundColor White
Write-Host ""
Write-Host "  4. Configure environment variables if needed (.env on VM)" -ForegroundColor White
Write-Host ""

Write-Host "🔗 Endpoints:" -ForegroundColor Cyan
Write-Host "  Health: http://$VMHost/health" -ForegroundColor White
Write-Host "  API Docs: http://$VMHost/docs" -ForegroundColor White
Write-Host "  Magic Link Send: http://$VMHost/api/social-auth/magic-link/send" -ForegroundColor White
Write-Host ""

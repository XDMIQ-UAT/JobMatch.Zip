# Restart Frontend Production Server
# Usage: .\scripts\restart-frontend.ps1

Write-Host "Restarting Frontend Production Server..." -ForegroundColor Green

# Check if running in production environment
if ($env:NODE_ENV -ne "production") {
    Write-Host "⚠️  Warning: NODE_ENV is not set to 'production'" -ForegroundColor Yellow
    Write-Host "   Setting NODE_ENV=production for this session" -ForegroundColor Yellow
    $env:NODE_ENV = "production"
}

# Check if supervisord is available (Linux/WSL)
if (Get-Command supervisorctl -ErrorAction SilentlyContinue) {
    Write-Host "`nRestarting via supervisord..." -ForegroundColor Cyan
    supervisorctl restart frontend
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend restarted successfully" -ForegroundColor Green
        Write-Host "`nChecking status..." -ForegroundColor Cyan
        supervisorctl status frontend
    } else {
        Write-Host "❌ Failed to restart frontend via supervisord" -ForegroundColor Red
        Write-Host "   Trying manual restart..." -ForegroundColor Yellow
    }
}

# Manual restart - find and kill existing process, then start new one
Write-Host "`nChecking for running Next.js processes..." -ForegroundColor Cyan
$processes = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*next*" -or $_.Path -like "*frontend*"
}

if ($processes) {
    Write-Host "Found $($processes.Count) Node.js process(es)" -ForegroundColor Yellow
    foreach ($proc in $processes) {
        Write-Host "  Stopping process $($proc.Id)..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

# Start frontend in production mode
Write-Host "`nStarting Frontend Production Server..." -ForegroundColor Cyan
Set-Location frontend

# Verify build exists
if (-not (Test-Path ".next")) {
    Write-Host "❌ Error: Build not found. Run 'npm run build' first." -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "✅ Build found, starting server..." -ForegroundColor Green
Write-Host "   Port: 3000" -ForegroundColor Gray
Write-Host "   Mode: Production" -ForegroundColor Gray

# Start in background
$env:NODE_ENV = "production"
$env:PORT = "3000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:NODE_ENV='production'; `$env:PORT='3000'; Write-Host 'Starting Frontend Production Server...' -ForegroundColor Green; npm run start"

Set-Location ..

Write-Host "`n✅ Frontend production server starting..." -ForegroundColor Green
Write-Host "   URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nNote: Check the new PowerShell window for server logs." -ForegroundColor Yellow


# Start Frontend with HTTPS on port 8443
# Usage: .\scripts\start-frontend-https.ps1

Write-Host "Starting Frontend with HTTPS on port 8443..." -ForegroundColor Green

# Check if Node is available
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host "Node.js: $nodeVersion" -ForegroundColor Cyan

# Change to frontend directory
Set-Location frontend

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Set port to 8443
$env:PORT = "8443"

# Start Next.js with HTTPS
# Note: Next.js doesn't natively support HTTPS in dev mode
# We'll use a simple HTTPS proxy or configure Next.js to use HTTPS
Write-Host "`nStarting Next.js dev server..." -ForegroundColor Yellow
Write-Host "Note: Next.js dev mode uses HTTP by default." -ForegroundColor Yellow
Write-Host "For HTTPS, you may need to use a reverse proxy or configure Next.js differently." -ForegroundColor Yellow
Write-Host "`nStarting on port 8443 (HTTP)..." -ForegroundColor Cyan

# Start Next.js dev server on port 8443
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:PORT='8443'; Write-Host 'Starting Next.js on port 8443...' -ForegroundColor Green; npm run dev"

Set-Location ..

Write-Host "`n✅ Frontend starting on http://localhost:8443" -ForegroundColor Green
Write-Host "`nNote: This is HTTP, not HTTPS. For true HTTPS, you'll need:" -ForegroundColor Yellow
Write-Host "  1. SSL certificates" -ForegroundColor Gray
Write-Host "  2. A reverse proxy (like nginx)" -ForegroundColor Gray
Write-Host "  3. Or use a tool like 'local-ssl-proxy'" -ForegroundColor Gray


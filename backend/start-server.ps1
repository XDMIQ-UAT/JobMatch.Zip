# Quick start script for backend server
# Can be run from backend directory
# Usage: .\start-server.ps1

Write-Host "Starting Backend Server..." -ForegroundColor Green

# Get project root (parent of current directory)
$backendDir = Get-Location
$projectRoot = Split-Path -Parent $backendDir

# Set Python path to project root (required for imports)
$env:PYTHONPATH = $projectRoot

# Ensure we're in backend directory
Set-Location $backendDir

Write-Host "Project Root: $projectRoot" -ForegroundColor Gray
Write-Host "Backend Directory: $backendDir" -ForegroundColor Gray
Write-Host ""

# Verify main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "Error: main.py not found!" -ForegroundColor Red
    exit 1
}

# Start server
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "SEO Status: http://localhost:8000/api/seo/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload


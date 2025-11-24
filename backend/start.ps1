# Simple backend server start script
# Run from backend directory: .\start.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting Backend Server..." -ForegroundColor Green

# Get absolute paths
$backendDir = Get-Location
$projectRoot = Split-Path -Parent $backendDir

Write-Host "Project Root: $projectRoot" -ForegroundColor Gray
Write-Host "Backend Dir: $backendDir" -ForegroundColor Gray

# Set Python path - CRITICAL for imports
$env:PYTHONPATH = $projectRoot
Write-Host "PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray

# Verify main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "ERROR: main.py not found in current directory!" -ForegroundColor Red
    Write-Host "Current directory: $backendDir" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "SEO Status: http://localhost:8000/api/seo/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload


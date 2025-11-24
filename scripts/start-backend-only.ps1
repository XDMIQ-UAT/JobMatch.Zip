# Start Backend Server Only
# Usage: .\scripts\start-backend-only.ps1

Write-Host "Starting Backend Server..." -ForegroundColor Green

# Get project root (parent of scripts directory)
if ($PSScriptRoot) {
    $projectRoot = Split-Path -Parent $PSScriptRoot
} else {
    # Fallback if PSScriptRoot not available
    $projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}

$backendDir = Join-Path $projectRoot "backend"

# Verify backend directory exists
if (-not (Test-Path $backendDir)) {
    Write-Host "Error: Backend directory not found: $backendDir" -ForegroundColor Red
    exit 1
}

# Set Python path to project root
$env:PYTHONPATH = $projectRoot

# Change to backend directory
Set-Location $backendDir

Write-Host "Project Root: $projectRoot" -ForegroundColor Gray
Write-Host "Backend Directory: $backendDir" -ForegroundColor Gray
Write-Host ""

# Verify main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "Error: main.py not found in backend directory!" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Start server
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "SEO Status: http://localhost:8000/api/seo/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn with single worker to avoid multiprocessing issues on Windows/Python 3.13
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

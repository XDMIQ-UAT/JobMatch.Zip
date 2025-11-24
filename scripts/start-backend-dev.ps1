# Start Backend Server for Development
# This script starts the FastAPI backend on port 8001 (since Next.js uses 8000)

Write-Host "🚀 Starting FastAPI Backend Server..." -ForegroundColor Green
Write-Host ""

# Get project root
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"

# Set Python path
$env:PYTHONPATH = $projectRoot

# Change to backend directory
Set-Location $backendDir

# Verify .env exists in project root
$envFile = Join-Path $projectRoot ".env"
if (Test-Path $envFile) {
    Write-Host "✅ Found .env file at: $envFile" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: .env file not found at: $envFile" -ForegroundColor Yellow
    Write-Host "   Email functionality may not work correctly." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   Backend URL: http://localhost:8001" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "   Health Check: http://localhost:8001/health" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Note: Frontend should use port 8001 for API calls" -ForegroundColor Yellow
Write-Host "   Update NEXT_PUBLIC_API_URL=http://localhost:8001/api" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start server on port 8001 to avoid conflict with Next.js on 8000
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload


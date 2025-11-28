# Test Agent Service Locally

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Testing Agent Service Locally" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if service is running
$port = 8080
$url = "http://localhost:$port"

Write-Host "Testing service at: $url" -ForegroundColor Yellow
Write-Host ""

# Health check
Write-Host "1. Health Check:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$url/health" -Method GET -UseBasicParsing
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

# List workflows
Write-Host "2. List Workflows:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$url/workflows" -Method GET -UseBasicParsing
    Write-Host "   ✅ Status: $($response.StatusCode)" -ForegroundColor Green
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   Workflows found: $($data.count)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "To start the service locally:" -ForegroundColor Yellow
Write-Host "  cd agents-cloud-run" -ForegroundColor White
Write-Host "  python agent_service.py" -ForegroundColor White
Write-Host ""


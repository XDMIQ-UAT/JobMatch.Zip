# Test Email Authentication Endpoint
param(
    [string]$Email = "me@myl.zip",
    [string]$ApiUrl = "http://localhost:8001/api"
)

Write-Host "Testing Email Authentication Endpoint" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl" -ForegroundColor White
Write-Host "Email: $Email" -ForegroundColor White
Write-Host ""

try {
    $body = @{
        email = $Email
    } | ConvertTo-Json

    Write-Host "Sending request..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$ApiUrl/auth/social/email/send" -Method Post -ContentType "application/json" -Body $body
    
    Write-Host "[SUCCESS] Email verification code sent!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "[ERROR] Failed to send email:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "Error Details:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Cyan
    Write-Host "1. Check if backend is running: netstat -ano | Select-String ':8001'" -ForegroundColor White
    Write-Host "2. Check backend logs for errors" -ForegroundColor White
    Write-Host "3. Verify SES configuration in .env file" -ForegroundColor White
}


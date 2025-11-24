# Test Magic Link Email Sending
param(
    [string]$Email = "me@myl.zip",
    [string]$ApiUrl = "http://localhost:8001/api"
)

Write-Host "Testing Magic Link Email Sending" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl" -ForegroundColor White
Write-Host "Email: $Email" -ForegroundColor White
Write-Host ""

try {
    $baseUrl = "https://jobmatch.zip"
    $body = @{
        email = $Email
        base_url = $baseUrl
    } | ConvertTo-Json

    Write-Host "Sending magic link request..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$ApiUrl/auth/social/email/magic-link" -Method Post -ContentType "application/json" -Body $body
    
    Write-Host "[SUCCESS] Magic link sent!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
    
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Check backend console for magic link URL (dev mode)" -ForegroundColor White
    Write-Host "2. Check email inbox for: $Email" -ForegroundColor White
    Write-Host "3. Check spam folder if not in inbox" -ForegroundColor White
    Write-Host "4. Click the magic link to authenticate" -ForegroundColor White
    
} catch {
    Write-Host "[ERROR] Failed to send magic link:" -ForegroundColor Red
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
    Write-Host "4. Test SES directly: .\scripts\test-ses-email.ps1 -ToEmail '$Email'" -ForegroundColor White
}


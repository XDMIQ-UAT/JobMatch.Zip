# Get Magic Link (for testing when email not received)
param(
    [string]$Email = "me@myl.zip",
    [string]$ApiUrl = "http://localhost:8001/api"
)

Write-Host "Getting Magic Link..." -ForegroundColor Cyan
Write-Host ""

try {
    $body = @{
        email = $Email
        base_url = "https://jobmatch.zip"
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Uri "$ApiUrl/auth/social/email/magic-link" -Method Post -ContentType "application/json" -Body $body
    
    Write-Host "[SUCCESS] Magic link generated!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Magic Link:" -ForegroundColor Cyan
    Write-Host $result.magic_link -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Copy this link and open it in your browser to authenticate." -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Email may be in spam folder or delayed." -ForegroundColor Gray
    Write-Host "      You can use this link directly instead." -ForegroundColor Gray
    
} catch {
    Write-Host "[ERROR] Failed to get magic link:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}


# Simple Email Test - Works in Cursor IDE Console
# Usage: .\scripts\test-email-simple.ps1 -Email me@myl.zip

param(
    [Parameter(Mandatory=$false)]
    [string]$Email = "me@myl.zip"
)

$ErrorActionPreference = "Stop"

Write-Host "📧 Testing Email: $Email" -ForegroundColor Cyan
Write-Host ""

try {
    $body = @{
        email = $Email
        base_url = "https://jobmatch.zip"
    } | ConvertTo-Json

    $response = Invoke-RestMethod `
        -Uri "https://jobmatch.zip/api/auth/social/email/magic-link" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 30

    Write-Host "✅ Success!" -ForegroundColor Green
    Write-Host "   Message: $($response.message)" -ForegroundColor White
    Write-Host "   Email: $($response.email)" -ForegroundColor White
    Write-Host ""
    Write-Host "📬 Check your inbox at: $Email" -ForegroundColor Cyan
    
    if ($response.magic_link) {
        Write-Host ""
        Write-Host "🔗 Magic Link (dev mode):" -ForegroundColor Yellow
        Write-Host "   $($response.magic_link)" -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   Status: $statusCode" -ForegroundColor Yellow
        
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $errorBody = $reader.ReadToEnd() | ConvertFrom-Json
            Write-Host "   Detail: $($errorBody.detail)" -ForegroundColor Red
        } catch {
            Write-Host "   Response: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    exit 1
}


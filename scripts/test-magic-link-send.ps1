# Test Magic Link Email Sending
# Tests the backend's ability to send magic link emails via SES

param(
    [string]$Email = "me@myl.zip",
    [string]$ApiUrl = "https://jobmatch.zip/api"
)

Write-Host "🧪 Testing Magic Link Email Sending" -ForegroundColor Cyan
Write-Host ""
Write-Host "📧 Email: $Email" -ForegroundColor White
Write-Host "🌐 API URL: $ApiUrl" -ForegroundColor White
Write-Host ""

# Test backend health first
Write-Host "🔍 Step 1: Checking backend health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$ApiUrl/../health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Backend health check failed: $_" -ForegroundColor Yellow
    Write-Host "   Continuing anyway..." -ForegroundColor Gray
}

Write-Host ""
Write-Host "📨 Step 2: Sending magic link email..." -ForegroundColor Yellow

$body = @{
    email = $Email
    base_url = "https://jobmatch.zip"
} | ConvertTo-Json

try {
    # Try possible endpoint paths
    $endpoints = @(
        "$ApiUrl/auth/social/email/magic-link",
        "$ApiUrl/social/email/magic-link",
        "$ApiUrl/auth/email/magic-link"
    )
    
    $response = $null
    $lastError = $null
    
    foreach ($endpoint in $endpoints) {
        try {
            Write-Host "   Trying: $endpoint" -ForegroundColor Gray
            $response = Invoke-RestMethod -Uri $endpoint -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
            break
        } catch {
            $lastError = $_
            continue
        }
    }
    
    if (-not $response) {
        throw $lastError
    }
    
    Write-Host "   ✅ Magic link sent successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Response:" -ForegroundColor Cyan
    Write-Host "   Message: $($response.message)" -ForegroundColor White
    Write-Host "   Email: $($response.email)" -ForegroundColor White
    Write-Host "   Expires in: $($response.expires_in) seconds" -ForegroundColor White
    
    if ($response.magic_link) {
        Write-Host ""
        Write-Host "🔗 Dev Mode Magic Link:" -ForegroundColor Cyan
        Write-Host "   $($response.magic_link)" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 You can use this link directly to authenticate" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "📬 Check your inbox at: $Email" -ForegroundColor Cyan
        Write-Host "   - Look for email from: info@jobmatch.zip" -ForegroundColor White
        Write-Host "   - Check spam folder if not in inbox" -ForegroundColor White
        Write-Host "   - Link is valid for 24 hours" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "✅ Test completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Failed to send magic link" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error Details:" -ForegroundColor Yellow
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   Status Code: $statusCode" -ForegroundColor White
        
        try {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $reader.ReadToEnd()
            $errorJson = $errorBody | ConvertFrom-Json
            
            Write-Host "   Error: $($errorJson.detail)" -ForegroundColor Red
            
            if ($errorJson.detail -like "*SES*" -or $errorJson.detail -like "*AWS*") {
                Write-Host ""
                Write-Host "💡 SES Configuration Issue:" -ForegroundColor Yellow
                Write-Host "   1. Verify .env file is on VM: .\scripts\copy-env-to-vm.ps1" -ForegroundColor White
                Write-Host "   2. Check backend logs for details" -ForegroundColor White
                Write-Host "   3. Verify email addresses in SES console" -ForegroundColor White
            }
        } catch {
            Write-Host "   Response: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Message -like "*connect*" -or $_.Exception.Message -like "*timeout*") {
            Write-Host ""
            Write-Host "💡 Connection Issue:" -ForegroundColor Yellow
            Write-Host "   - Backend may not be running" -ForegroundColor White
            Write-Host "   - Check: gcloud compute ssh jobmatch-vm --zone=us-central1-a" -ForegroundColor White
        }
    }
    
    exit 1
}


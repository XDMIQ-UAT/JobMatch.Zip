# Simple SES Configuration Test
# Tests AWS SES credentials and email verification status

Write-Host "🔍 Testing AWS SES Configuration" -ForegroundColor Cyan
Write-Host ""

# Load .env file
$envFile = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -eq "AWS_ACCESS_KEY_ID") { $env:AWS_ACCESS_KEY_ID = $value }
            if ($key -eq "AWS_SECRET_ACCESS_KEY") { $env:AWS_SECRET_ACCESS_KEY = $value }
            if ($key -eq "AWS_REGION") { $env:AWS_DEFAULT_REGION = $value }
            if ($key -eq "SES_REGION") { $env:AWS_DEFAULT_REGION = $value }
            if ($key -eq "SES_FROM_EMAIL") { $script:fromEmail = $value }
            if ($key -eq "EMAIL_PROVIDER_MODE") { $script:providerMode = $value }
        }
    }
} else {
    Write-Host "[ERROR] .env file not found at: $envFile" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   EMAIL_PROVIDER_MODE: $providerMode" -ForegroundColor White
Write-Host "   SES_FROM_EMAIL: $fromEmail" -ForegroundColor White
Write-Host "   AWS_REGION: $env:AWS_DEFAULT_REGION" -ForegroundColor White
Write-Host ""

# Test AWS CLI connection
Write-Host "🔌 Testing AWS SES Connection..." -ForegroundColor Yellow
$quota = aws ses get-send-quota --region $env:AWS_DEFAULT_REGION 2>&1

if ($LASTEXITCODE -eq 0) {
    $quotaData = $quota | ConvertFrom-Json
    Write-Host "   ✅ Connection successful!" -ForegroundColor Green
    Write-Host "   Max 24h Send: $($quotaData.Max24HourSend)" -ForegroundColor White
    Write-Host "   Sent Last 24h: $($quotaData.SentLast24Hours)" -ForegroundColor White
    Write-Host "   Max Send Rate: $($quotaData.MaxSendRate)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "   ❌ Connection failed!" -ForegroundColor Red
    Write-Host $quota -ForegroundColor Red
    Write-Host ""
    Write-Host "   Possible issues:" -ForegroundColor Yellow
    Write-Host "   - AWS credentials incorrect" -ForegroundColor White
    Write-Host "   - IAM user doesn't have SES permissions" -ForegroundColor White
    Write-Host "   - Network connectivity issue" -ForegroundColor White
    exit 1
}

# Check verified identities
Write-Host "📧 Checking Verified Email Addresses..." -ForegroundColor Yellow
$identities = aws ses list-verified-email-addresses --region $env:AWS_DEFAULT_REGION 2>&1

if ($LASTEXITCODE -eq 0) {
    $identityData = $identities | ConvertFrom-Json
    $verifiedEmails = $identityData.VerifiedEmailAddresses
    
    Write-Host "   Found $($verifiedEmails.Count) verified email(s):" -ForegroundColor White
    foreach ($email in $verifiedEmails) {
        Write-Host "     - $email" -ForegroundColor Cyan
    }
    Write-Host ""
    
    # Check if sender email is verified
    if ($fromEmail -and $verifiedEmails -notcontains $fromEmail) {
        Write-Host "   ⚠️  WARNING: Sender email '$fromEmail' is NOT verified!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   To verify, run:" -ForegroundColor Cyan
        Write-Host "   .\scripts\verify-ses-email.ps1 -EmailAddress $fromEmail" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "   ✅ Sender email '$fromEmail' is verified" -ForegroundColor Green
        Write-Host ""
    }
} else {
    Write-Host "   ⚠️  Could not check verified identities:" -ForegroundColor Yellow
    Write-Host $identities -ForegroundColor Yellow
    Write-Host ""
}

# Check account status (sandbox vs production)
Write-Host "📊 Checking Account Status..." -ForegroundColor Yellow
$accountAttributes = aws ses get-account-sending-enabled --region $env:AWS_DEFAULT_REGION 2>&1

# Note: SES sandbox mode means you can only send to verified emails
Write-Host "   ℹ️  If SES is in sandbox mode:" -ForegroundColor Cyan
Write-Host "      - You can only send to verified email addresses" -ForegroundColor White
Write-Host "      - Request production access to send to any email" -ForegroundColor White
Write-Host ""

Write-Host "✅ Configuration check complete!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Verify sender email: .\scripts\verify-ses-email.ps1 -EmailAddress $fromEmail" -ForegroundColor White
Write-Host "   2. Verify recipient email (if in sandbox): .\scripts\verify-ses-email.ps1 -EmailAddress <recipient>" -ForegroundColor White
Write-Host "   3. Request production access if needed (AWS SES Console)" -ForegroundColor White


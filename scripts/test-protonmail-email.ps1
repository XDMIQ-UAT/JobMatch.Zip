# Test Email Sending to ProtonMail Addresses
# This script tests sending emails to ProtonMail addresses via SES

param(
    [Parameter(Mandatory=$true)]
    [string]$ToEmail,
    
    [string]$FromEmail = "info@jobmatch.zip",
    
    [switch]$VerifyFirst
)

Write-Host "Testing Email Sending to ProtonMail" -ForegroundColor Cyan
Write-Host ""

# Load credentials from .env
$envFile = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -eq "AWS_ACCESS_KEY_ID") { $env:AWS_ACCESS_KEY_ID = $value }
            if ($key -eq "AWS_SECRET_ACCESS_KEY") { $env:AWS_SECRET_ACCESS_KEY = $value }
            if ($key -eq "AWS_REGION") { $env:AWS_DEFAULT_REGION = $value }
        }
    }
} else {
    Write-Host "[WARNING] .env file not found, using environment variables" -ForegroundColor Yellow
}

$region = $env:AWS_DEFAULT_REGION
if (-not $region) { $region = "us-west-2" }

Write-Host "From: $FromEmail" -ForegroundColor White
Write-Host "To: $ToEmail" -ForegroundColor White
Write-Host "Region: $region" -ForegroundColor White
Write-Host ""

# Check if ProtonMail domain
$isProtonMail = $ToEmail -match '@(proton\.(me|mail|pm)|pm\.me)$'
if ($isProtonMail) {
    Write-Host "[INFO] Detected ProtonMail address" -ForegroundColor Cyan
    Write-Host ""
}

# Check verification status if requested
if ($VerifyFirst) {
    Write-Host "Checking verification status..." -ForegroundColor Yellow
    $verifyCheck = aws ses get-identity-verification-attributes --identities $ToEmail --region $region 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $verifyResponse = $verifyCheck | ConvertFrom-Json
        $verifyStatus = $verifyResponse.VerificationAttributes.PSObject.Properties.Value.VerificationStatus
        
        if ($verifyStatus -eq "Success") {
            Write-Host "[SUCCESS] Email address is verified" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Email address is NOT verified (Status: $verifyStatus)" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "In sandbox mode, recipient must be verified." -ForegroundColor Yellow
            Write-Host "To verify this email, run:" -ForegroundColor Cyan
            Write-Host "   .\scripts\verify-ses-email.ps1 -EmailAddress `"$ToEmail`"" -ForegroundColor White
            Write-Host ""
            $continue = Read-Host "Continue anyway? (y/n)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                exit 0
            }
        }
    }
    Write-Host ""
}

# Check SES account status (sandbox vs production)
Write-Host "Checking SES account status..." -ForegroundColor Yellow
$quota = aws ses get-send-quota --region $region 2>&1 | ConvertFrom-Json

if ($quota.Max24HourSend -eq 200) {
    Write-Host "[INFO] SES Account Status: SANDBOX MODE" -ForegroundColor Yellow
    Write-Host "   - Max send rate: 200 emails per 24 hours" -ForegroundColor Gray
    Write-Host "   - Can only send to verified email addresses" -ForegroundColor Gray
    Write-Host "   - To send to any email (including ProtonMail), request production access" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "[INFO] SES Account Status: PRODUCTION MODE" -ForegroundColor Green
    Write-Host "   - Max send rate: $($quota.Max24HourSend) emails per 24 hours" -ForegroundColor Gray
    Write-Host "   - Can send to any email address" -ForegroundColor Gray
    Write-Host ""
}

# Send test email
Write-Host "Sending test email..." -ForegroundColor Yellow

$subject = "Test Email from JobMatch Platform - ProtonMail Test"
$body = @"
This is a test email sent from the JobMatch platform to verify SES integration with ProtonMail.

Email Details:
- Sent via Amazon SES
- From: $FromEmail
- To: $ToEmail
- Timestamp: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")

If you received this email, SES integration is working correctly!

Best regards,
JobMatch Platform Team
"@

# Create JSON file
$tempFile = Join-Path $env:TEMP "ses-protonmail-test-$(Get-Random).json"
$emailJson = @{
    Source = $FromEmail
    Destination = @{
        ToAddresses = @($ToEmail)
    }
    Message = @{
        Subject = @{
            Data = $subject
            Charset = "UTF-8"
        }
        Body = @{
            Text = @{
                Data = $body
                Charset = "UTF-8"
            }
            Html = @{
                Data = $body -replace "`n", "<br>`n"
                Charset = "UTF-8"
            }
        }
    }
} | ConvertTo-Json -Depth 10

try {
    # Write JSON to file without BOM
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($tempFile, $emailJson.Trim(), $utf8NoBom)
    
    # Send email
    $normalizedPath = $tempFile -replace '\\', '/'
    $fileUri = "file://$normalizedPath"
    
    $result = aws ses send-email --cli-input-json $fileUri --region $region 2>&1
    
    # Clean up temp file
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    
    if ($LASTEXITCODE -eq 0) {
        $resultObj = $result | ConvertFrom-Json
        Write-Host "[SUCCESS] Email sent successfully!" -ForegroundColor Green
        Write-Host "   Message ID: $($resultObj.MessageId)" -ForegroundColor White
        Write-Host ""
        Write-Host "Check the ProtonMail inbox for: $ToEmail" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "   1. Check inbox (and spam folder)" -ForegroundColor White
        Write-Host "   2. Verify email was received" -ForegroundColor White
        Write-Host "   3. Check email headers for delivery details" -ForegroundColor White
        Write-Host ""
        
        if ($quota.Max24HourSend -eq 200) {
            Write-Host "[TIP] To send to ProtonMail addresses without verification:" -ForegroundColor Yellow
            Write-Host "   Request production access in AWS SES Console" -ForegroundColor White
            Write-Host "   Account Dashboard -> Request Production Access" -ForegroundColor White
        }
    } else {
        Write-Host "[ERROR] Failed to send email:" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        Write-Host ""
        
        if ($result -match "not verified|sandbox") {
            Write-Host "[SOLUTION] This email address needs to be verified in sandbox mode." -ForegroundColor Yellow
            Write-Host "   Run: .\scripts\verify-ses-email.ps1 -EmailAddress `"$ToEmail`"" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "[ERROR] Error: $_" -ForegroundColor Red
    Remove-Item $tempFile -ErrorAction SilentlyContinue
}


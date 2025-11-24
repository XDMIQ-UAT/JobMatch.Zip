# Verify Email Address in AWS SES (for Sandbox Mode)
# This script verifies an email address so it can receive emails in SES sandbox mode

param(
    [Parameter(Mandatory=$true)]
    [string]$EmailAddress,
    
    [string]$Region = "us-west-2"
)

Write-Host "Verifying Email Address in AWS SES" -ForegroundColor Cyan
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
            if ($key -eq "SES_REGION") { $Region = $value }
        }
    }
} else {
    Write-Host "[WARNING] .env file not found at: $envFile" -ForegroundColor Yellow
    Write-Host "   Using environment variables if set" -ForegroundColor Gray
}

$env:AWS_DEFAULT_REGION = $Region

Write-Host "Email: $EmailAddress" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host ""

# Check current verification status
Write-Host "Checking current verification status..." -ForegroundColor Yellow
$verifyCheck = aws ses get-identity-verification-attributes --identities $EmailAddress --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    $verifyResponse = $verifyCheck | ConvertFrom-Json
    $verifyStatus = $verifyResponse.VerificationAttributes.PSObject.Properties.Value.VerificationStatus
    
    if ($verifyStatus -eq "Success") {
        Write-Host "[SUCCESS] Email address is already verified!" -ForegroundColor Green
        Write-Host ""
        Write-Host "This email can now receive emails from SES in sandbox mode." -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "[WARNING] Email address is not verified (Status: $verifyStatus)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Email address not found in SES (not yet verified)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Requesting verification for $EmailAddress..." -ForegroundColor Yellow

# Request email verification
$verifyResult = aws ses verify-email-identity --email-address $EmailAddress --region $Region 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Verification request sent successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Check the inbox for: $EmailAddress" -ForegroundColor White
    Write-Host "   2. Look for an email from AWS SES (noreply-aws@amazon.com)" -ForegroundColor White
    Write-Host "   3. Click the verification link in the email" -ForegroundColor White
    Write-Host "   4. Once verified, this email can receive emails from SES" -ForegroundColor White
    Write-Host ""
    Write-Host "[TIP] Check spam folder if you don't see the email" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To check verification status, run:" -ForegroundColor Gray
    Write-Host "   aws ses get-identity-verification-attributes --identities $EmailAddress --region $Region" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Failed to request verification:" -ForegroundColor Red
    Write-Host $verifyResult -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "   - AWS credentials not configured correctly" -ForegroundColor White
    Write-Host "   - IAM user doesn't have ses:VerifyEmailIdentity permission" -ForegroundColor White
    Write-Host "   - Email address format is invalid" -ForegroundColor White
    exit 1
}


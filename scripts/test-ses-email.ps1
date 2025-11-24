# Test SES Email Sending
# This script tests sending an email via SES directly

param(
    [Parameter(Mandatory=$true)]
    [string]$ToEmail,
    
    [string]$FromEmail = "info@jobmatch.zip"
)

Write-Host "Testing SES Email Sending" -ForegroundColor Cyan
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
    Write-Host "[ERROR] .env file not found at: $envFile" -ForegroundColor Red
    exit 1
}

Write-Host "From: $FromEmail" -ForegroundColor White
Write-Host "To: $ToEmail" -ForegroundColor White
Write-Host "Region: $env:AWS_DEFAULT_REGION" -ForegroundColor White
Write-Host ""

# Check if recipient is verified (for sandbox mode)
Write-Host "Checking recipient verification status..." -ForegroundColor Yellow
$verifyCheck = aws ses get-identity-verification-attributes --identities $ToEmail --region $env:AWS_DEFAULT_REGION 2>&1
$verifyStatus = ($verifyCheck | ConvertFrom-Json).VerificationAttributes.PSObject.Properties.Value.VerificationStatus

if ($verifyStatus -eq "Success") {
    Write-Host "[SUCCESS] Recipient email is verified" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Recipient email is NOT verified" -ForegroundColor Yellow
    Write-Host "   If SES is in sandbox mode, you must verify this email first" -ForegroundColor Yellow
    Write-Host "   Run: aws ses verify-email-identity --email-address $ToEmail --region $env:AWS_DEFAULT_REGION" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Sending test email..." -ForegroundColor Yellow

# Send test email via AWS CLI
$subject = "Test Email from JobMatch Platform"
$body = "This is a test email sent from the JobMatch platform to verify SES integration."

# Create JSON file
$tempFile = Join-Path $env:TEMP "ses-email-$(Get-Random).json"
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
        }
    }
} | ConvertTo-Json -Depth 10

try {
    # Write JSON to file without BOM (UTF-8)
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($tempFile, $emailJson.Trim(), $utf8NoBom)
    
    # Use file:// with forward slashes (Windows format: file://C:/path)
    $normalizedPath = $tempFile -replace '\\', '/'
    $fileUri = "file://$normalizedPath"
    
    Write-Host "   Using JSON file: $tempFile" -ForegroundColor Gray
    
    $result = aws ses send-email --cli-input-json $fileUri --region $env:AWS_DEFAULT_REGION 2>&1
    
    # Clean up temp file
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    
    if ($LASTEXITCODE -eq 0) {
        $resultObj = $result | ConvertFrom-Json
        Write-Host "[SUCCESS] Email sent successfully!" -ForegroundColor Green
        Write-Host "   Message ID: $($resultObj.MessageId)" -ForegroundColor White
        Write-Host ""
        Write-Host "Check the inbox for: $ToEmail" -ForegroundColor Cyan
    } else {
        Write-Host "[ERROR] Failed to send email:" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Error: $_" -ForegroundColor Red
    Remove-Item $tempFile -ErrorAction SilentlyContinue
}


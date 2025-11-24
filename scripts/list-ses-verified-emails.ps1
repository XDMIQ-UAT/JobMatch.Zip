# List All Verified Email Addresses in AWS SES
# This script lists all verified email identities in your SES account

param(
    [string]$Region = "us-west-2"
)

Write-Host "Listing Verified Email Addresses in AWS SES" -ForegroundColor Cyan
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
}

$env:AWS_DEFAULT_REGION = $Region

Write-Host "Region: $Region" -ForegroundColor White
Write-Host ""

# List all identities (emails and domains)
Write-Host "Fetching verified identities..." -ForegroundColor Yellow
$listResult = aws ses list-identities --region $Region 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to list identities:" -ForegroundColor Red
    Write-Host $listResult -ForegroundColor Red
    exit 1
}

$identities = ($listResult | ConvertFrom-Json).Identities

if ($identities.Count -eq 0) {
    Write-Host "[INFO] No verified identities found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To verify an email address, run:" -ForegroundColor Gray
    Write-Host "   .\scripts\verify-ses-email.ps1 -EmailAddress 'email@example.com'" -ForegroundColor Gray
    exit 0
}

Write-Host "Found $($identities.Count) identity/identities" -ForegroundColor Green
Write-Host ""

# Get verification attributes for all identities
Write-Host "Checking verification status..." -ForegroundColor Yellow
$verifyResult = aws ses get-identity-verification-attributes --identities $identities --region $Region 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to get verification attributes:" -ForegroundColor Red
    Write-Host $verifyResult -ForegroundColor Red
    exit 1
}

$verifyAttributes = ($verifyResult | ConvertFrom-Json).VerificationAttributes

# Separate emails and domains
$verifiedEmails = @()
$pendingEmails = @()
$verifiedDomains = @()
$pendingDomains = @()

foreach ($identity in $identities) {
    if ($verifyAttributes.PSObject.Properties.Name -contains $identity) {
        $status = $verifyAttributes.$identity.VerificationStatus
        
        if ($identity -match '@') {
            # It's an email address
            if ($status -eq "Success") {
                $verifiedEmails += @{
                    Email = $identity
                    Status = $status
                }
            } else {
                $pendingEmails += @{
                    Email = $identity
                    Status = $status
                }
            }
        } else {
            # It's a domain
            if ($status -eq "Success") {
                $verifiedDomains += @{
                    Domain = $identity
                    Status = $status
                }
            } else {
                $pendingDomains += @{
                    Domain = $identity
                    Status = $status
                }
            }
        }
    }
}

# Display results
if ($verifiedEmails.Count -gt 0) {
    Write-Host "[SUCCESS] Verified Email Addresses ($($verifiedEmails.Count)):" -ForegroundColor Green
    foreach ($email in $verifiedEmails) {
        Write-Host "   - $($email.Email)" -ForegroundColor White
    }
    Write-Host ""
}

if ($pendingEmails.Count -gt 0) {
    Write-Host "[PENDING] Pending Email Verifications ($($pendingEmails.Count)):" -ForegroundColor Yellow
    foreach ($email in $pendingEmails) {
        Write-Host "   - $($email.Email) (Status: $($email.Status))" -ForegroundColor White
    }
    Write-Host ""
}

if ($verifiedDomains.Count -gt 0) {
    Write-Host "[SUCCESS] Verified Domains ($($verifiedDomains.Count)):" -ForegroundColor Green
    foreach ($domain in $verifiedDomains) {
        Write-Host "   - $($domain.Domain)" -ForegroundColor White
    }
    Write-Host ""
}

if ($pendingDomains.Count -gt 0) {
    Write-Host "[PENDING] Pending Domain Verifications ($($pendingDomains.Count)):" -ForegroundColor Yellow
    foreach ($domain in $pendingDomains) {
        Write-Host "   - $($domain.Domain) (Status: $($domain.Status))" -ForegroundColor White
    }
    Write-Host ""
}

# Summary
$totalVerified = $verifiedEmails.Count + $verifiedDomains.Count
$totalPending = $pendingEmails.Count + $pendingDomains.Count

Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "   Verified: $totalVerified" -ForegroundColor Green
Write-Host "   Pending: $totalPending" -ForegroundColor Yellow
Write-Host "   Total: $($identities.Count)" -ForegroundColor White
Write-Host ""

# Sandbox mode info
Write-Host "SES Sandbox Mode:" -ForegroundColor Cyan
Write-Host "   In sandbox mode, you can only send emails to verified addresses." -ForegroundColor Gray
Write-Host "   To send to any email, request production access in AWS SES Console." -ForegroundColor Gray
Write-Host ""


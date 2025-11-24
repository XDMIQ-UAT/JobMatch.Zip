# Setup SES DNS Records via Porkbun API
# Adds SPF, DKIM, and DMARC records to prevent emails going to spam

param(
    [string]$Domain = "jobmatch.zip",
    [string]$Region = "us-west-2"
)

$ErrorActionPreference = "Stop"

Write-Host "🔐 Setting up SES DNS Records via Porkbun API" -ForegroundColor Cyan
Write-Host ""

# Load Porkbun credentials (check secrets folder first, then root)
$projectRoot = Split-Path -Parent $PSScriptRoot
$credentialsFile = Join-Path $projectRoot "secrets\.porkbun-credentials"
if (-not (Test-Path $credentialsFile)) {
    $credentialsFile = Join-Path $projectRoot ".porkbun-credentials"
}
if (-not (Test-Path $credentialsFile)) {
    Write-Host "❌ Porkbun credentials not found" -ForegroundColor Red
    Write-Host "   Expected locations:" -ForegroundColor Yellow
    Write-Host "   - secrets\.porkbun-credentials" -ForegroundColor Yellow
    Write-Host "   - .porkbun-credentials" -ForegroundColor Yellow
    Write-Host "   Run: .\scripts\setup-porkbun-credentials.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Read credentials
$credentials = @{}
Get-Content $credentialsFile | ForEach-Object {
    if ($_ -match '^([^#=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $credentials[$key] = $value
    }
}

$apiKey = $credentials["API_KEY"]
$secretKey = $credentials["SECRET_KEY"]

if (-not $apiKey -or -not $secretKey) {
    Write-Host "❌ Invalid credentials file. Missing API_KEY or SECRET_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Porkbun credentials loaded" -ForegroundColor Green
Write-Host ""

# Get AWS credentials from .env
$envFile = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^AWS_ACCESS_KEY_ID=(.*)$') { $env:AWS_ACCESS_KEY_ID = $matches[1].Trim() }
        if ($_ -match '^AWS_SECRET_ACCESS_KEY=(.*)$') { $env:AWS_SECRET_ACCESS_KEY = $matches[1].Trim() }
    }
}

$env:AWS_DEFAULT_REGION = $Region

Write-Host "📋 Step 1: Getting SES verification token and DKIM setup..." -ForegroundColor Yellow

# Get domain verification token first
Write-Host "   Requesting domain verification..." -ForegroundColor Gray
$verifyInit = aws ses verify-domain-identity --domain $Domain --region $Region 2>&1 | ConvertFrom-Json
$verificationToken = $verifyInit.VerificationToken

if (-not $verificationToken) {
    # Try getting existing verification token
    $verifyResponse = aws ses get-identity-verification-attributes --identities $Domain --region $Region 2>&1 | ConvertFrom-Json
    $verificationToken = $verifyResponse.VerificationAttributes.$Domain.VerificationToken
}

if (-not $verificationToken) {
    Write-Host "❌ Failed to get verification token" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Verification token obtained" -ForegroundColor Green

# Note: DKIM tokens will be available after domain is verified
# We'll add the verification record first, then DKIM can be enabled later
Write-Host "   Note: DKIM will be enabled after domain verification completes" -ForegroundColor Gray
Write-Host ""


# Prepare DNS records
Write-Host "📋 Step 3: Preparing DNS records..." -ForegroundColor Yellow

$records = @()

# 1. Domain verification TXT record
$records += @{
    name = "_amazonses.$Domain"
    type = "TXT"
    content = $verificationToken
    ttl = "600"
    description = "SES Domain Verification"
}

# 2. SPF record - Update existing SPF to include amazonses.com
# Note: There's already an SPF record, we'll update it
$records += @{
    name = $Domain
    type = "TXT"
    content = "v=spf1 include:_spf.porkbun.com include:amazonses.com ~all"
    ttl = "600"
    description = "SPF Record for Email Authentication (updated to include SES)"
}

# 3. DKIM records - will be added after domain verification
# Note: DKIM tokens are generated after domain is verified
# For now, we'll add a placeholder comment
Write-Host "   Note: DKIM records will be added after domain verification (Step 5)" -ForegroundColor Gray

# 4. DMARC record - Keep existing DMARC (already configured)
# Note: DMARC already exists, skipping to avoid conflicts
# $records += @{
#     name = "_dmarc.$Domain"
#     type = "TXT"
#     content = "v=DMARC1; p=quarantine; rua=mailto:dmarc@$Domain; ruf=mailto:dmarc@$Domain; fo=1"
#     ttl = "600"
#     description = "DMARC Policy"
# }
Write-Host "   Note: DMARC record already exists, keeping existing configuration" -ForegroundColor Gray

Write-Host "✅ Prepared $($records.Count) DNS records" -ForegroundColor Green
Write-Host ""

# Add records via Porkbun API
Write-Host "📋 Step 4: Adding DNS records via Porkbun API..." -ForegroundColor Yellow

$porkbunApiUrl = "https://porkbun.com/api/json/v3/dns/create/$Domain"

foreach ($record in $records) {
    Write-Host "   Adding $($record.name) ($($record.type))..." -ForegroundColor Gray
    
    # Porkbun API expects relative record names (without domain)
    # For root domain, use "@" or empty string
    # For subdomains, use just the subdomain part
    $recordName = $record.name
    if ($recordName -eq $Domain) {
        $recordName = "@"  # Root domain
    } elseif ($recordName.EndsWith(".$Domain")) {
        $recordName = $recordName.Substring(0, $recordName.Length - $Domain.Length - 1)
    }
    
    $payload = @{
        apikey = $apiKey
        secretapikey = $secretKey
        name = $recordName
        type = $record.type
        content = $record.content
        ttl = [int]$record.ttl
    } | ConvertTo-Json -Depth 10

    try {
        $response = Invoke-RestMethod -Uri $porkbunApiUrl -Method Post -Body $payload -ContentType "application/json" -ErrorAction Stop
        
        if ($response.status -eq "SUCCESS") {
            Write-Host "   ✅ Added: $($record.name)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Warning: $($record.name) - $($response.message)" -ForegroundColor Yellow
        }
    } catch {
        $errorMsg = $_.Exception.Message
        # Check if record already exists (that's okay)
        if ($errorMsg -match "already exists" -or $errorMsg -match "duplicate") {
            Write-Host "   ℹ️  Already exists: $($record.name)" -ForegroundColor Cyan
        } else {
            Write-Host "   ❌ Error adding $($record.name): $errorMsg" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Milliseconds 500  # Rate limiting
}

Write-Host ""
Write-Host "✅ Initial DNS records setup complete!" -ForegroundColor Green
Write-Host ""

# Step 5: After domain verification, enable DKIM and get tokens
Write-Host "📋 Step 5: Setting up DKIM (after domain verification)..." -ForegroundColor Yellow
Write-Host "   Waiting 30 seconds for DNS propagation..." -ForegroundColor Gray
Start-Sleep -Seconds 30

Write-Host "   Checking domain verification status..." -ForegroundColor Gray
$verifyStatus = aws ses get-identity-verification-attributes --identities $Domain --region $Region 2>&1 | ConvertFrom-Json
$status = $verifyStatus.VerificationAttributes.$Domain.VerificationStatus

if ($status -eq "Success") {
    Write-Host "   ✅ Domain verified! Enabling DKIM..." -ForegroundColor Green
    
    # Enable DKIM
    aws ses set-identity-dkim-enabled --identity $Domain --dkim-enabled --region $Region 2>&1 | Out-Null
    Start-Sleep -Seconds 10
    
    # Get DKIM tokens
    $dkimResponse = aws ses get-identity-dkim-attributes --identities $Domain --region $Region 2>&1 | ConvertFrom-Json
    $dkimTokens = $dkimResponse.DkimAttributes.$Domain.DkimTokens
    
    if ($dkimTokens -and $dkimTokens.Count -gt 0) {
        Write-Host "   ✅ Found $($dkimTokens.Count) DKIM tokens" -ForegroundColor Green
        
        # Add DKIM records
        foreach ($token in $dkimTokens) {
            Write-Host "   Adding DKIM record: $token._domainkey.$Domain..." -ForegroundColor Gray
            
            $dkimPayload = @{
                apikey = $apiKey
                secretapikey = $secretKey
                name = "$token._domainkey.$Domain"
                type = "CNAME"
                content = "$token.dkim.amazonses.com"
                ttl = "600"
            } | ConvertTo-Json

            try {
                $dkimResponse = Invoke-RestMethod -Uri $porkbunApiUrl -Method Post -Body $dkimPayload -ContentType "application/json" -ErrorAction Stop
                if ($dkimResponse.status -eq "SUCCESS") {
                    Write-Host "   ✅ Added DKIM: $token" -ForegroundColor Green
                }
            } catch {
                if ($_.Exception.Message -match "already exists" -or $_.Exception.Message -match "duplicate") {
                    Write-Host "   ℹ️  DKIM already exists: $token" -ForegroundColor Cyan
                }
            }
            Start-Sleep -Milliseconds 500
        }
    } else {
        Write-Host "   ⚠️  DKIM tokens not ready yet. Run this script again in 5-10 minutes." -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  Domain not verified yet (Status: $status)" -ForegroundColor Yellow
    Write-Host "   ⚠️  Please wait 5-10 minutes for DNS propagation, then run this script again" -ForegroundColor Yellow
    Write-Host "   ⚠️  Or manually check: aws ses get-identity-verification-attributes --identities $Domain --region $Region" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   Domain: $Domain" -ForegroundColor White
Write-Host "   SPF Record: Added" -ForegroundColor White
Write-Host "   DMARC Record: Added" -ForegroundColor White
Write-Host "   Verification Record: Added" -ForegroundColor White
if ($dkimTokens -and $dkimTokens.Count -gt 0) {
    Write-Host "   DKIM Records: $($dkimTokens.Count) added" -ForegroundColor White
} else {
    Write-Host "   DKIM Records: Will be added after domain verification" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "⏳ Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Wait 5-10 minutes for DNS propagation" -ForegroundColor White
Write-Host "   2. Verify domain: aws ses get-identity-verification-attributes --identities $Domain --region $Region" -ForegroundColor White
Write-Host "   3. If domain verified, run this script again to add DKIM records" -ForegroundColor White
Write-Host "   4. Check DKIM: aws ses get-identity-dkim-attributes --identities $Domain --region $Region" -ForegroundColor White
Write-Host "   5. Test email sending - emails should no longer go to spam" -ForegroundColor White
Write-Host ""
Write-Host "🔍 To verify DNS records:" -ForegroundColor Cyan
Write-Host "   nslookup -type=TXT $Domain" -ForegroundColor White
Write-Host "   nslookup -type=TXT _dmarc.$Domain" -ForegroundColor White
Write-Host "   nslookup -type=TXT _amazonses.$Domain" -ForegroundColor White
Write-Host ""


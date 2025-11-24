# Setup Porkbun API credentials securely
# Prompts user for credentials and saves to gitignored file

$CREDENTIALS_FILE = ".porkbun-credentials"

Write-Host "🔐 Porkbun API Credentials Setup" -ForegroundColor Cyan
Write-Host ""

# Check if credentials already exist
if (Test-Path $CREDENTIALS_FILE) {
    Write-Host "⚠️  Credentials file already exists at $CREDENTIALS_FILE" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to update it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Keeping existing credentials."
        exit 0
    }
}

Write-Host "Enter your Porkbun API credentials:"
Write-Host ""

# Get credentials from user
$API_KEY = Read-Host "Porkbun API Key"
$SECRET_KEY = Read-Host "Porkbun Secret Key" -AsSecureString
$SECRET_KEY_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($SECRET_KEY))

if ([string]::IsNullOrWhiteSpace($API_KEY) -or [string]::IsNullOrWhiteSpace($SECRET_KEY_PLAIN)) {
    Write-Host "❌ API Key and Secret Key cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔍 Validating credentials..." -ForegroundColor Yellow

# Validate credentials by making test API call
$validationPayload = @{
    apikey = $API_KEY
    secretapikey = $SECRET_KEY_PLAIN
} | ConvertTo-Json

try {
    $validationResponse = Invoke-RestMethod -Uri "https://porkbun.com/api/json/v3/ping" -Method Post -Body $validationPayload -ContentType "application/json" -ErrorAction Stop
    
    if ($validationResponse.status -eq "SUCCESS") {
        Write-Host "✅ Credentials validated successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Credential validation failed: $($validationResponse.message)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Credential validation failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "💾 Saving credentials to $CREDENTIALS_FILE..." -ForegroundColor Green

# Save credentials securely
$credentialsContent = @"
# Porkbun API Credentials
# DO NOT COMMIT THIS FILE TO VERSION CONTROL
API_KEY=$API_KEY
SECRET_KEY=$SECRET_KEY_PLAIN
"@

$credentialsContent | Out-File -FilePath $CREDENTIALS_FILE -Encoding UTF8 -NoNewline

# Set restrictive permissions (Windows)
try {
    $acl = Get-Acl $CREDENTIALS_FILE
    $acl.SetAccessRuleProtection($true, $false)
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
    $acl.SetAccessRule($accessRule)
    Set-Acl $CREDENTIALS_FILE $acl
} catch {
    Write-Host "⚠️  Could not set file permissions (this is okay on Windows)" -ForegroundColor Yellow
}

Write-Host "✅ Credentials saved to $CREDENTIALS_FILE" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "   Run: .\scripts\setup-ses-dns-records.ps1 to set up email authentication DNS records" -ForegroundColor White
Write-Host ""


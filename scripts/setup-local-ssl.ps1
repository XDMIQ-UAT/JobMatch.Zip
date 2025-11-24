# Setup local SSL for localhost.jobmatch.zip
# Adds entry to hosts file and optionally generates self-signed certificate

param(
    [switch]$GenerateCert = $false,
    [string]$CertDir = "secrets\local-ssl"
)

$ErrorActionPreference = "Stop"

Write-Host "🔒 Setting up local SSL for localhost.jobmatch.zip..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Add to hosts file
Write-Host "📝 Step 1: Adding to hosts file..." -ForegroundColor Cyan
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$entry = "127.0.0.1`tlocalhost.jobmatch.zip"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  Administrator privileges required to modify hosts file" -ForegroundColor Yellow
    Write-Host "   Please run PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

if (Select-String -Path $hostsPath -Pattern "localhost.jobmatch.zip" -Quiet) {
    Write-Host "✅ Entry already exists in hosts file" -ForegroundColor Green
} else {
    try {
        Add-Content -Path $hostsPath -Value $entry
        Write-Host "✅ Added localhost.jobmatch.zip to hosts file" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to modify hosts file: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 2: Generate self-signed certificate (optional)
if ($GenerateCert) {
    Write-Host "🔐 Step 2: Generating self-signed certificate..." -ForegroundColor Cyan
    
    # Check if OpenSSL is available
    $openssl = Get-Command openssl -ErrorAction SilentlyContinue
    if (-not $openssl) {
        Write-Host "⚠️  OpenSSL not found. Skipping certificate generation." -ForegroundColor Yellow
        Write-Host "   Install OpenSSL or use existing certificate" -ForegroundColor Yellow
    } else {
        if (-not (Test-Path $CertDir)) {
            New-Item -ItemType Directory -Path $CertDir -Force | Out-Null
        }
        
        $keyPath = Join-Path $CertDir "localhost.jobmatch.zip.key"
        $certPath = Join-Path $CertDir "localhost.jobmatch.zip.crt"
        
        Write-Host "   Generating certificate..." -ForegroundColor White
        openssl req -x509 -newkey rsa:4096 -keyout $keyPath -out $certPath -days 365 -nodes `
            -subj "/CN=localhost.jobmatch.zip" `
            -addext "subjectAltName=DNS:localhost.jobmatch.zip,DNS:*.localhost.jobmatch.zip" 2>&1 | Out-Null
        
        if (Test-Path $certPath) {
            Write-Host "✅ Certificate generated:" -ForegroundColor Green
            Write-Host "   Key: $keyPath" -ForegroundColor White
            Write-Host "   Cert: $certPath" -ForegroundColor White
            Write-Host ""
            Write-Host "📋 Next steps:" -ForegroundColor Cyan
            Write-Host "   1. Configure your dev server to use these certificates" -ForegroundColor White
            Write-Host "   2. Trust the certificate in your browser (double-click .crt file)" -ForegroundColor White
        } else {
            Write-Host "❌ Failed to generate certificate" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "✅ Local SSL setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 You can now access:" -ForegroundColor Cyan
Write-Host "   https://localhost.jobmatch.zip" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Note: Your production SSL certificate must include" -ForegroundColor Yellow
Write-Host "   'localhost.jobmatch.zip' in Subject Alternative Names" -ForegroundColor Yellow
Write-Host "   to use the same certificate for both production and local dev." -ForegroundColor Yellow


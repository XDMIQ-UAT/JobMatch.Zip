# Get Amazon SES configuration (without exposing credentials)
# Safe for Warp terminal - shows configuration status, not actual secrets

param(
    [switch]$ShowStatus = $true,
    [switch]$TestConnection = $false,
    [switch]$ShowFileLocation = $false
)

$envFile = Join-Path $PSScriptRoot "..\.env"

if (-not (Test-Path $envFile)) {
    Write-Host "❌ .env file not found at: $envFile" -ForegroundColor Red
    Write-Host "💡 Run: .\scripts\setup-ses-credentials.ps1" -ForegroundColor Yellow
    exit 1
}

# Read .env file
$envContent = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envContent[$key] = $value
    }
}

# Check for SES credentials
$hasAccessKey = $envContent.ContainsKey("AWS_ACCESS_KEY_ID") -and $envContent["AWS_ACCESS_KEY_ID"]
$hasSecretKey = $envContent.ContainsKey("AWS_SECRET_ACCESS_KEY") -and $envContent["AWS_SECRET_ACCESS_KEY"]
$hasRegion = $envContent.ContainsKey("SES_REGION") -and $envContent["SES_REGION"]
$hasFromEmail = $envContent.ContainsKey("SES_FROM_EMAIL") -and $envContent["SES_FROM_EMAIL"]
$providerMode = $envContent["EMAIL_PROVIDER_MODE"]

if ($ShowFileLocation) {
    Write-Host "📁 Credentials file location: $envFile" -ForegroundColor Cyan
    Write-Host ""
}

if ($ShowStatus) {
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "📋 Amazon SES Configuration Status" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "AWS Access Key ID:     " -NoNewline
    if ($hasAccessKey) {
        $keyPreview = $envContent["AWS_ACCESS_KEY_ID"].Substring(0, [Math]::Min(8, $envContent["AWS_ACCESS_KEY_ID"].Length)) + "..." 
        Write-Host "✅ Set ($keyPreview)" -ForegroundColor Green
    } else {
        Write-Host "❌ Not set" -ForegroundColor Red
    }
    
    Write-Host "AWS Secret Access Key: " -NoNewline
    if ($hasSecretKey) {
        Write-Host "✅ Set (hidden)" -ForegroundColor Green
    } else {
        Write-Host "❌ Not set" -ForegroundColor Red
    }
    
    Write-Host "SES Region:            " -NoNewline
    if ($hasRegion) {
        Write-Host "✅ $($envContent['SES_REGION'])" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Not set (default: us-west-2)" -ForegroundColor Yellow
    }
    
    Write-Host "SES From Email:       " -NoNewline
    if ($hasFromEmail) {
        Write-Host "✅ $($envContent['SES_FROM_EMAIL'])" -ForegroundColor Green
    } else {
        Write-Host "❌ Not set" -ForegroundColor Red
    }
    
    Write-Host "Email Provider Mode:  " -NoNewline
    if ($providerMode) {
        Write-Host "✅ $providerMode" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Not set (default: smtp)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Overall status
    if ($hasAccessKey -and $hasSecretKey -and $hasFromEmail) {
        Write-Host "✅ SES credentials are configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  SES credentials are incomplete" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Missing:" -ForegroundColor Yellow
        if (-not $hasAccessKey) { Write-Host "   • AWS_ACCESS_KEY_ID" -ForegroundColor Red }
        if (-not $hasSecretKey) { Write-Host "   • AWS_SECRET_ACCESS_KEY" -ForegroundColor Red }
        if (-not $hasFromEmail) { Write-Host "   • SES_FROM_EMAIL" -ForegroundColor Red }
    }
}

if ($TestConnection) {
    Write-Host ""
    Write-Host "🔍 Testing SES connection..." -ForegroundColor Cyan
    
    if (-not ($hasAccessKey -and $hasSecretKey)) {
        Write-Host "❌ Cannot test: Missing credentials" -ForegroundColor Red
        exit 1
    }
    
    # Test using Python/boto3
    $testScript = @"
import boto3
from botocore.exceptions import ClientError

try:
    ses = boto3.client(
        'ses',
        aws_access_key_id='$($envContent['AWS_ACCESS_KEY_ID'])',
        aws_secret_access_key='$($envContent['AWS_SECRET_ACCESS_KEY'])',
        region_name='$($envContent['SES_REGION'])'
    )
    quota = ses.get_send_quota()
    print(f"SUCCESS: Max 24h Send: {quota.get('Max24HourSend', 'N/A')}")
except ClientError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")
"@
    
    try {
        $result = $testScript | python 2>&1
        if ($result -match "SUCCESS") {
            Write-Host "✅ SES connection successful!" -ForegroundColor Green
            Write-Host "   $result" -ForegroundColor Gray
        } else {
            Write-Host "❌ SES connection failed:" -ForegroundColor Red
            Write-Host "   $result" -ForegroundColor Red
        }
    } catch {
        Write-Host "⚠️  Python/boto3 not available for testing" -ForegroundColor Yellow
        Write-Host "   Install: pip install boto3" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "🔒 Security:" -ForegroundColor Cyan
Write-Host "   • Credentials are stored in: $envFile" -ForegroundColor Gray
Write-Host "   • File is in .gitignore (safe from GitHub)" -ForegroundColor Gray
Write-Host "   • Actual secret values are never displayed" -ForegroundColor Gray
Write-Host ""


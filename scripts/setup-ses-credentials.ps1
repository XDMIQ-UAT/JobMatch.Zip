# Setup Amazon SES credentials securely
# Prompts user for credentials and saves to .env file

$ENV_FILE = ".env"

Write-Host "🔐 Amazon SES Credentials Setup" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (Test-Path $ENV_FILE) {
    Write-Host "⚠️  .env file already exists at $ENV_FILE" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to add/update SES credentials? (y/n)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Keeping existing .env file."
        exit 0
    }
} else {
    Write-Host "📝 Creating new .env file..." -ForegroundColor Green
}

Write-Host ""
Write-Host "Enter your Amazon SES credentials:"
Write-Host ""

# Get credentials from user
$AWS_ACCESS_KEY_ID = Read-Host "AWS Access Key ID"
$AWS_SECRET_ACCESS_KEY = Read-Host "AWS Secret Access Key" -AsSecureString
$AWS_SECRET_ACCESS_KEY_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($AWS_SECRET_ACCESS_KEY))

$AWS_REGION = Read-Host "AWS Region (default: us-west-2)"
if ([string]::IsNullOrWhiteSpace($AWS_REGION)) {
    $AWS_REGION = "us-west-2"
}

$SES_REGION = Read-Host "SES Region (default: $AWS_REGION)"
if ([string]::IsNullOrWhiteSpace($SES_REGION)) {
    $SES_REGION = $AWS_REGION
}

$SES_FROM_EMAIL = Read-Host "SES From Email (e.g., admin@futurelink.zip)"
$EMAIL_PROVIDER_MODE = Read-Host "Email Provider Mode (ses/smtp, default: ses)"
if ([string]::IsNullOrWhiteSpace($EMAIL_PROVIDER_MODE)) {
    $EMAIL_PROVIDER_MODE = "ses"
}

Write-Host ""
Write-Host "🔍 Validating credentials..." -ForegroundColor Yellow

# Try to validate credentials by importing boto3 (if available)
try {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $validationScript = @"
import boto3
from botocore.exceptions import ClientError

try:
    ses = boto3.client(
        'ses',
        aws_access_key_id='$AWS_ACCESS_KEY_ID',
        aws_secret_access_key='$AWS_SECRET_ACCESS_KEY_PLAIN',
        region_name='$SES_REGION'
    )
    # Try to get send quota (doesn't send email, just validates credentials)
    response = ses.get_send_quota()
    print('SUCCESS')
except ClientError as e:
    print(f'ERROR: {e}')
except Exception as e:
    print(f'ERROR: {e}')
"@
        $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
        $validationScript | Out-File -FilePath $tempScript -Encoding UTF8
        $result = python $tempScript 2>&1
        Remove-Item $tempScript -ErrorAction SilentlyContinue
        
        if ($result -match "SUCCESS") {
            Write-Host "✅ Credentials validated successfully" -ForegroundColor Green
        } elseif ($result -match "ERROR") {
            Write-Host "⚠️  Credential validation failed: $result" -ForegroundColor Yellow
            Write-Host "Continuing anyway..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Python not found, skipping validation" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not validate credentials: $_" -ForegroundColor Yellow
    Write-Host "Continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💾 Saving credentials to $ENV_FILE..." -ForegroundColor Green

# Read existing .env file if it exists
$envContent = @{}
if (Test-Path $ENV_FILE) {
    Get-Content $ENV_FILE | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envContent[$key] = $value
        }
    }
}

# Update SES-related variables
$envContent["AWS_ACCESS_KEY_ID"] = $AWS_ACCESS_KEY_ID
$envContent["AWS_SECRET_ACCESS_KEY"] = $AWS_SECRET_ACCESS_KEY_PLAIN
$envContent["AWS_REGION"] = $AWS_REGION
$envContent["SES_REGION"] = $SES_REGION
$envContent["SES_FROM_EMAIL"] = $SES_FROM_EMAIL
$envContent["EMAIL_PROVIDER_MODE"] = $EMAIL_PROVIDER_MODE

# Write back to .env file
$output = @()
Get-Content $ENV_FILE -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=') {
        $key = $matches[1].Trim()
        if (-not $envContent.ContainsKey($key)) {
            $output += $_
        }
    } elseif ($_ -notmatch '^\s*#') {
        $output += $_
    }
}

# Add SES configuration section
$output += ""
$output += "# Amazon SES Configuration"
$output += "AWS_ACCESS_KEY_ID=$($envContent['AWS_ACCESS_KEY_ID'])"
$output += "AWS_SECRET_ACCESS_KEY=$($envContent['AWS_SECRET_ACCESS_KEY'])"
$output += "AWS_REGION=$($envContent['AWS_REGION'])"
$output += "SES_REGION=$($envContent['SES_REGION'])"
$output += "SES_FROM_EMAIL=$($envContent['SES_FROM_EMAIL'])"
$output += "EMAIL_PROVIDER_MODE=$($envContent['EMAIL_PROVIDER_MODE'])"

$output | Out-File -FilePath $ENV_FILE -Encoding UTF8

Write-Host "✅ Credentials saved to $ENV_FILE" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Configuration Summary:" -ForegroundColor Cyan
Write-Host "   AWS Region: $AWS_REGION"
Write-Host "   SES Region: $SES_REGION"
Write-Host "   From Email: $SES_FROM_EMAIL"
Write-Host "   Provider Mode: $EMAIL_PROVIDER_MODE"
Write-Host ""
Write-Host "⚠️  Remember to:" -ForegroundColor Yellow
Write-Host "   1. Verify your sender email in AWS SES console"
Write-Host "   2. Move out of SES sandbox if needed (for production)"
Write-Host "   3. Never commit .env file to git"
Write-Host ""


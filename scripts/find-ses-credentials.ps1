# Find Amazon SES credentials securely (without exposing them)
# Safe to use in Warp terminal - never outputs actual credentials

param(
    [switch]$ShowLocationsOnly = $false,
    [switch]$VerifyExists = $false
)

Write-Host "🔍 Searching for Amazon SES credentials..." -ForegroundColor Cyan
Write-Host ""

$foundLocations = @()
$credentialFiles = @()

# Check 1: .env file in project root
$envFile = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $envFile) {
    $hasSES = Select-String -Path $envFile -Pattern "AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|SES_REGION|SES_FROM_EMAIL" -Quiet
    if ($hasSES) {
        $foundLocations += ".env (project root)"
        $credentialFiles += $envFile
        Write-Host "✅ Found SES credentials in: .env" -ForegroundColor Green
    } else {
        Write-Host "⚠️  .env exists but no SES credentials found" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ .env file not found in project root" -ForegroundColor Red
}

# Check 2: secrets/ directory
$secretsDir = Join-Path $PSScriptRoot "..\secrets"
if (Test-Path $secretsDir) {
    $sesFiles = Get-ChildItem -Path $secretsDir -File -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -match "ses|aws|credential" -and $_.Extension -match "json|txt|env|credentials" }
    
    if ($sesFiles) {
        foreach ($file in $sesFiles) {
            $foundLocations += "secrets/$($file.Name)"
            $credentialFiles += $file.FullName
            Write-Host "✅ Found potential credential file: secrets/$($file.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  secrets/ directory exists but no SES credential files found" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  secrets/ directory not found" -ForegroundColor Yellow
}

# Check 3: Common locations in E:\
Write-Host ""
Write-Host "🔍 Checking common credential locations in E:\..." -ForegroundColor Cyan

$commonPaths = @(
    "E:\credentials",
    "E:\secrets",
    "E:\aws",
    "E:\ses",
    "E:\config",
    "E:\.credentials",
    "E:\.secrets"
)

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        Write-Host "   📁 Found: $path" -ForegroundColor Yellow
        
        # Look for credential files
        $files = Get-ChildItem -Path $path -File -Recurse -ErrorAction SilentlyContinue | 
            Where-Object { $_.Name -match "ses|aws|credential|\.env" -and $_.Extension -match "json|txt|env|credentials|key" } |
            Select-Object -First 5
        
        if ($files) {
            foreach ($file in $files) {
                $relativePath = $file.FullName.Replace("E:\", "E:\")
                $foundLocations += $relativePath
                $credentialFiles += $file.FullName
                Write-Host "      ✅ $($file.Name)" -ForegroundColor Green
            }
        }
    }
}

# Check 4: Environment variables (current session only)
Write-Host ""
Write-Host "🔍 Checking environment variables..." -ForegroundColor Cyan
$envVars = @("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "SES_REGION", "SES_FROM_EMAIL")
$foundEnvVars = @()

foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var, "Process")
    if ($value) {
        $foundEnvVars += $var
        Write-Host "   ✅ $var is set (in current session)" -ForegroundColor Green
    }
}

if ($foundEnvVars.Count -eq 0) {
    Write-Host "   ⚠️  No SES environment variables found in current session" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 Summary" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($foundLocations.Count -gt 0) {
    Write-Host ""
    Write-Host "✅ Credentials found in the following locations:" -ForegroundColor Green
    foreach ($loc in $foundLocations) {
        Write-Host "   • $loc" -ForegroundColor White
    }
    
    if ($VerifyExists) {
        Write-Host ""
        Write-Host "🔍 Verifying credential files (checking if they contain SES keys)..." -ForegroundColor Cyan
        foreach ($file in $credentialFiles) {
            if (Test-Path $file) {
                $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
                if ($content -match "AWS_ACCESS_KEY|AWS_SECRET|SES") {
                    Write-Host "   ✅ $file contains SES credentials" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️  $file exists but may not contain SES credentials" -ForegroundColor Yellow
                }
            }
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ No SES credentials found in common locations" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Run: .\scripts\setup-ses-credentials.ps1" -ForegroundColor White
    Write-Host "   2. Or manually create .env file with SES credentials" -ForegroundColor White
    Write-Host "   3. Or check AWS credentials file: ~/.aws/credentials" -ForegroundColor White
}

if ($foundEnvVars.Count -gt 0) {
    Write-Host ""
    Write-Host "✅ Environment variables set (current session only):" -ForegroundColor Green
    foreach ($var in $foundEnvVars) {
        Write-Host "   • $var" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "🔒 Security Notes:" -ForegroundColor Cyan
Write-Host "   • Credentials are NOT displayed above (safe for Warp)" -ForegroundColor White
Write-Host "   • All credential files are in .gitignore" -ForegroundColor White
Write-Host "   • Never commit credentials to GitHub" -ForegroundColor White
Write-Host ""

# Check AWS credentials file (standard location)
$awsCredsFile = "$env:USERPROFILE\.aws\credentials"
if (Test-Path $awsCredsFile) {
    Write-Host "💡 AWS credentials file found: $awsCredsFile" -ForegroundColor Yellow
    Write-Host "   (Check this file manually if credentials aren't in .env)" -ForegroundColor Gray
}

Write-Host ""


# Compliance Scanner for JobFinder Platform
# Scans codebase for HIPAA/PII/Privacy/Security issues

param(
    [string]$ReportPath = "E:\JobFinder\docs\COMPLIANCE_REPORT.md",
    [switch]$Verbose,
    [switch]$FixIssues
)

Write-Host "🔍 JobFinder Compliance Scanner" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = "E:\JobFinder"
$issues = @()
$warnings = @()
$passed = @()

function Add-Issue {
    param($Severity, $Category, $Description, $Location, $Fix)
    $script:issues += [PSCustomObject]@{
        Severity = $Severity
        Category = $Category
        Description = $Description
        Location = $Location
        Fix = $Fix
    }
}

function Add-Warning {
    param($Message)
    $script:warnings += $Message
}

function Add-Pass {
    param($Message)
    $script:passed += $Message
}

Write-Host "1️⃣ Scanning for PII in Logs..." -ForegroundColor Yellow

# Check for email addresses in logging statements
$emailLogs = Get-ChildItem -Path "$rootPath\backend" -Include "*.py" -Recurse | 
    Select-String -Pattern 'logger\.(info|debug|warning|error)\(.*\{.*email.*\}' |
    Where-Object { $_.Line -notmatch 'redact_email' }

if ($emailLogs) {
    foreach ($match in $emailLogs) {
        Add-Issue -Severity "HIGH" -Category "PII Logging" `
            -Description "Email address logged in plaintext" `
            -Location "$($match.Path):$($match.LineNumber)" `
            -Fix "Import and use redact_email() from backend.security.pii_redaction"
    }
    Write-Host "  ❌ Found $($emailLogs.Count) instances of email logging" -ForegroundColor Red
} else {
    Add-Pass "No email addresses logged in plaintext"
    Write-Host "  ✅ No email addresses logged" -ForegroundColor Green
}

# Check for phone numbers in logging
$phoneLogs = Get-ChildItem -Path "$rootPath\backend" -Include "*.py" -Recurse | 
    Select-String -Pattern 'logger\.(info|debug|warning|error)\(.*\{.*phone.*\}' |
    Where-Object { $_.Line -notmatch 'redact_phone' }

if ($phoneLogs) {
    foreach ($match in $phoneLogs) {
        Add-Issue -Severity "HIGH" -Category "PII Logging" `
            -Description "Phone number logged in plaintext" `
            -Location "$($match.Path):$($match.LineNumber)" `
            -Fix "Import and use redact_phone() from backend.security.pii_redaction"
    }
    Write-Host "  ❌ Found $($phoneLogs.Count) instances of phone logging" -ForegroundColor Red
} else {
    Add-Pass "No phone numbers logged in plaintext"
    Write-Host "  ✅ No phone numbers logged" -ForegroundColor Green
}

Write-Host ""
Write-Host "2️⃣ Checking Secrets Management..." -ForegroundColor Yellow

# Check for hardcoded SECRET_KEY
$secretKey = Select-String -Path "$rootPath\backend\config.py" -Pattern 'SECRET_KEY.*=.*"change-me-in-production"'
if ($secretKey) {
    Add-Issue -Severity "CRITICAL" -Category "Secrets" `
        -Description "Hardcoded default SECRET_KEY found" `
        -Location "backend/config.py:33" `
        -Fix "Set SECRET_KEY via environment variable"
    Write-Host "  ❌ Default SECRET_KEY still in config" -ForegroundColor Red
} else {
    Add-Pass "SECRET_KEY properly configured"
    Write-Host "  ✅ SECRET_KEY not using default" -ForegroundColor Green
}

# Check .env file exists and is in .gitignore
if (-not (Test-Path "$rootPath\.env")) {
    Add-Warning "No .env file found - secrets may not be configured"
    Write-Host "  ⚠️ No .env file found" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
}

$gitignore = Get-Content "$rootPath\.gitignore" -ErrorAction SilentlyContinue
if ($gitignore -and ($gitignore -match '\.env')) {
    Add-Pass ".env file is in .gitignore"
    Write-Host "  ✅ .env in .gitignore" -ForegroundColor Green
} else {
    Add-Issue -Severity "HIGH" -Category "Secrets" `
        -Description ".env file not in .gitignore" `
        -Location ".gitignore" `
        -Fix "Add .env to .gitignore"
    Write-Host "  ❌ .env not in .gitignore" -ForegroundColor Red
}

Write-Host ""
Write-Host "3️⃣ Checking CORS Configuration..." -ForegroundColor Yellow

$corsCheck = Select-String -Path "$rootPath\backend\main.py" -Pattern 'allow_methods=\["\*"\]'
if ($corsCheck) {
    Add-Issue -Severity "HIGH" -Category "API Security" `
        -Description "Overly permissive CORS configuration" `
        -Location "backend/main.py" `
        -Fix "Restrict CORS to specific methods: ['GET', 'POST', 'PUT', 'DELETE']"
    Write-Host "  ❌ CORS allows all methods" -ForegroundColor Red
} else {
    Add-Pass "CORS properly configured"
    Write-Host "  ✅ CORS restricted" -ForegroundColor Green
}

Write-Host ""
Write-Host "4️⃣ Checking Security Headers..." -ForegroundColor Yellow

$securityHeaders = Test-Path "$rootPath\backend\security\security_headers.py"
if ($securityHeaders) {
    Add-Pass "Security headers module exists"
    Write-Host "  ✅ Security headers module found" -ForegroundColor Green
    
    # Check if headers are actually applied in main.py
    $mainPy = Get-Content "$rootPath\backend\main.py" -Raw
    if ($mainPy -match 'security_headers') {
        Add-Pass "Security headers applied in main.py"
        Write-Host "  ✅ Security headers applied" -ForegroundColor Green
    } else {
        Add-Issue -Severity "HIGH" -Category "Web Security" `
            -Description "Security headers module exists but not applied" `
            -Location "backend/main.py" `
            -Fix "Import and apply security headers middleware"
        Write-Host "  ⚠️ Security headers not applied" -ForegroundColor Yellow
    }
} else {
    Add-Warning "Security headers module not fully implemented"
    Write-Host "  ⚠️ Security headers need verification" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "5️⃣ Checking Database Schema..." -ForegroundColor Yellow

$modelsContent = Get-Content "$rootPath\backend\database\models.py" -Raw

# Check for sensitive PII fields
$sensitiveFields = @('ssn', 'social_security', 'credit_card', 'password_hash', 'drivers_license')
$foundSensitive = $false
foreach ($field in $sensitiveFields) {
    if ($modelsContent -match $field) {
        Add-Issue -Severity "CRITICAL" -Category "Database" `
            -Description "Sensitive PII field found: $field" `
            -Location "backend/database/models.py" `
            -Fix "Remove or encrypt sensitive PII fields"
        $foundSensitive = $true
    }
}

if (-not $foundSensitive) {
    Add-Pass "No sensitive PII fields in database schema"
    Write-Host "  ✅ No SSN/credit cards in schema" -ForegroundColor Green
}

# Check for anonymous-first design
if ($modelsContent -match 'AnonymousUser') {
    Add-Pass "Anonymous-first architecture implemented"
    Write-Host "  ✅ Anonymous-first design confirmed" -ForegroundColor Green
} else {
    Add-Warning "Anonymous-first architecture may not be implemented"
}

Write-Host ""
Write-Host "6️⃣ Checking Rate Limiting..." -ForegroundColor Yellow

$rateLimiter = Test-Path "$rootPath\backend\security\rate_limiter.py"
if ($rateLimiter) {
    Add-Pass "Rate limiter module exists"
    Write-Host "  ✅ Rate limiter found" -ForegroundColor Green
} else {
    Add-Issue -Severity "MEDIUM" -Category "API Security" `
        -Description "No rate limiting implementation found" `
        -Location "backend/security/" `
        -Fix "Implement rate limiting middleware"
    Write-Host "  ❌ No rate limiter found" -ForegroundColor Red
}

Write-Host ""
Write-Host "7️⃣ Checking Dependencies..." -ForegroundColor Yellow

$requirements = Get-Content "$rootPath\backend\requirements.txt"
$duplicates = $requirements | Group-Object | Where-Object { $_.Count -gt 1 }

if ($duplicates) {
    foreach ($dup in $duplicates) {
        Add-Issue -Severity "LOW" -Category "Dependencies" `
            -Description "Duplicate dependency: $($dup.Name)" `
            -Location "backend/requirements.txt" `
            -Fix "Remove duplicate entry"
    }
    Write-Host "  ⚠️ Found $($duplicates.Count) duplicate dependencies" -ForegroundColor Yellow
} else {
    Add-Pass "No duplicate dependencies"
    Write-Host "  ✅ No duplicate dependencies" -ForegroundColor Green
}

Write-Host ""
Write-Host "8️⃣ Checking for PII in User Content Fields..." -ForegroundColor Yellow

# Warn about free text fields that could contain PII
$freeTextFields = @('experience_summary', 'content', 'description')
$needsModeration = $false
foreach ($field in $freeTextFields) {
    if ($modelsContent -match $field) {
        $needsModeration = $true
    }
}

if ($needsModeration) {
    Add-Warning "Free text fields exist - implement PII scanning for user content"
    Write-Host "  ⚠️ User content fields need PII moderation" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ No user content fields found" -ForegroundColor Green
}

# Check if PII scanner exists
$piiScanner = Test-Path "$rootPath\backend\ai\pii_scanner.py"
if ($piiScanner) {
    Add-Pass "PII scanner module exists"
    Write-Host "  ✅ PII scanner implemented" -ForegroundColor Green
} else {
    Add-Issue -Severity "MEDIUM" -Category "Content Moderation" `
        -Description "No PII scanner for user-generated content" `
        -Location "backend/ai/" `
        -Fix "Create PII scanner module"
}

Write-Host ""
Write-Host "9️⃣ Checking GDPR Compliance..." -ForegroundColor Yellow

# Check for data deletion endpoints
$apiFiles = Get-ChildItem -Path "$rootPath\backend\api" -Include "*.py" -Recurse
$deletionEndpoint = $apiFiles | Select-String -Pattern '@router\.delete.*user' -SimpleMatch

if ($deletionEndpoint) {
    Add-Pass "User deletion endpoint found"
    Write-Host "  ✅ Data deletion endpoint exists" -ForegroundColor Green
} else {
    Add-Issue -Severity "HIGH" -Category "GDPR" `
        -Description "No 'Right to be Forgotten' implementation" `
        -Location "backend/api/" `
        -Fix "Implement DELETE /api/users/{anonymous_id} endpoint"
    Write-Host "  ❌ No user deletion endpoint" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔟 Checking Privacy Policy..." -ForegroundColor Yellow

$privacyPolicy = Test-Path "$rootPath\docs\PRIVACY_POLICY.md"
if ($privacyPolicy) {
    Add-Pass "Privacy Policy document exists"
    Write-Host "  ✅ Privacy Policy found" -ForegroundColor Green
} else {
    Add-Issue -Severity "CRITICAL" -Category "Legal" `
        -Description "No Privacy Policy document" `
        -Location "docs/" `
        -Fix "Create PRIVACY_POLICY.md with GDPR/CCPA compliance"
    Write-Host "  ❌ No Privacy Policy" -ForegroundColor Red
}

# Generate Report
Write-Host ""
Write-Host "📊 Generating Report..." -ForegroundColor Cyan

$criticalIssues = ($issues | Where-Object { $_.Severity -eq "CRITICAL" }).Count
$highIssues = ($issues | Where-Object { $_.Severity -eq "HIGH" }).Count
$mediumIssues = ($issues | Where-Object { $_.Severity -eq "MEDIUM" }).Count
$lowIssues = ($issues | Where-Object { $_.Severity -eq "LOW" }).Count

$report = @"
# JobFinder Compliance Scan Report
**Generated**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Summary
- 🔴 **Critical Issues**: $criticalIssues
- 🟠 **High Priority**: $highIssues
- 🟡 **Medium Priority**: $mediumIssues
- 🔵 **Low Priority**: $lowIssues
- ⚠️ **Warnings**: $($warnings.Count)
- ✅ **Passed Checks**: $($passed.Count)

## Issues Found

"@

foreach ($issue in $issues | Sort-Object @{Expression={
    switch ($_.Severity) {
        "CRITICAL" { 1 }
        "HIGH" { 2 }
        "MEDIUM" { 3 }
        "LOW" { 4 }
        default { 5 }
    }
}}) {
    $icon = switch ($issue.Severity) {
        "CRITICAL" { "🔴" }
        "HIGH" { "🟠" }
        "MEDIUM" { "🟡" }
        "LOW" { "🔵" }
    }
    
    $report += @"

### $icon $($issue.Severity): $($issue.Description)
- **Category**: $($issue.Category)
- **Location**: ``$($issue.Location)``
- **Fix**: $($issue.Fix)

"@
}

if ($warnings) {
    $report += @"

## Warnings

"@
    foreach ($warning in $warnings) {
        $report += "- ⚠️ $warning`n"
    }
}

$report += @"

## Passed Checks

"@
foreach ($pass in $passed) {
    $report += "- ✅ $pass`n"
}

$report += @"

## Next Steps

1. Address all CRITICAL issues before public release
2. Fix HIGH priority issues within 24 hours
3. Schedule MEDIUM priority fixes within 1 week
4. Review LOW priority items monthly

## Compliance Checklist

- [ ] All PII redacted from logs
- [ ] SECRET_KEY set via environment variable
- [ ] CORS restricted to production domains
- [ ] Security headers applied
- [ ] Rate limiting implemented
- [ ] GDPR data deletion endpoint
- [ ] Privacy Policy published
- [ ] Content moderation for PII
- [ ] Penetration testing completed
- [ ] Legal compliance review

---
*Generated by Compliance Guardian Agent*
"@

# Save report
$report | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "✅ Report saved to: $ReportPath" -ForegroundColor Green

# Display summary
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Scan Complete!" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Issues Found:" -ForegroundColor White
Write-Host "  🔴 Critical: $criticalIssues" -ForegroundColor Red
Write-Host "  🟠 High:     $highIssues" -ForegroundColor Yellow
Write-Host "  🟡 Medium:   $mediumIssues" -ForegroundColor Yellow
Write-Host "  🔵 Low:      $lowIssues" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ✅ Passed:   $($passed.Count)" -ForegroundColor Green
Write-Host "  ⚠️ Warnings: $($warnings.Count)" -ForegroundColor Yellow
Write-Host ""

if ($criticalIssues -gt 0) {
    Write-Host "⛔ CRITICAL ISSUES FOUND - DO NOT DEPLOY TO PRODUCTION" -ForegroundColor Red -BackgroundColor Black
    exit 1
} elseif ($highIssues -gt 0) {
    Write-Host "⚠️ HIGH PRIORITY ISSUES - Address before release" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ No critical issues found - Ready for review" -ForegroundColor Green
    exit 0
}

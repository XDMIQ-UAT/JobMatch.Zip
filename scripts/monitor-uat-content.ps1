# UAT Content Monitor - Critical Event Detection
# Monitors UAT folders for unexpected user content during testing phase
# Author: Security Team
# Last Updated: 2025-11-25

param(
    [string]$UATPath = "E:\zip-jobmatch\frontend\app\uat",
    [string]$BackendUATPath = "E:\zip-jobmatch\backend\uat",
    [string]$LogPath = "E:\zip-jobmatch\logs\uat-monitor.log",
    [string]$AlertsPath = "E:\zip-jobmatch\logs\uat-alerts.json",
    [int]$IntervalSeconds = 30
)

# Ensure logs directory exists
$logsDir = Split-Path -Parent $LogPath
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

# Initialize alerts file if it doesn't exist
if (-not (Test-Path $AlertsPath)) {
    "[]" | Out-File -FilePath $AlertsPath -Encoding UTF8
}

# Sensitive content patterns to detect
$SensitivePatterns = @(
    # PII Patterns
    '\b\d{3}-\d{2}-\d{4}\b',                    # SSN
    '\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', # Email
    '\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',            # Phone
    '\b\d{16}\b',                                # Credit card
    '\b(?:\d[ -]*?){13,19}\b',                   # Credit card with spaces
    
    # Financial Keywords
    'credit card',
    'social security',
    'bank account',
    'routing number',
    'password',
    'secret key',
    'api key',
    'token',
    
    # Personal Data
    'date of birth',
    'driver.?license',
    'passport',
    'salary',
    'income',
    
    # Medical
    'diagnosis',
    'prescription',
    'medical record',
    'health insurance',
    
    # Suspicious Activity
    'exploit',
    'vulnerability',
    'backdoor',
    'inject',
    'xss',
    'sql injection'
)

function Write-MonitorLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogPath -Value $logEntry
    
    if ($Level -eq "CRITICAL" -or $Level -eq "WARNING") {
        Write-Host $logEntry -ForegroundColor $(if ($Level -eq "CRITICAL") { "Red" } else { "Yellow" })
    } else {
        Write-Host $logEntry -ForegroundColor Gray
    }
}

function Add-Alert {
    param(
        [string]$Type,
        [string]$FilePath,
        [string]$Content,
        [string]$Reason
    )
    
    $alert = @{
        timestamp = (Get-Date -Format "o")
        type = $Type
        file = $FilePath
        contentSnippet = $Content.Substring(0, [Math]::Min(200, $Content.Length))
        reason = $Reason
        severity = "CRITICAL"
    }
    
    $alerts = Get-Content $AlertsPath -Raw | ConvertFrom-Json
    $alerts += $alert
    $alerts | ConvertTo-Json -Depth 10 | Out-File -FilePath $AlertsPath -Encoding UTF8
    
    Write-MonitorLog "🚨 CRITICAL ALERT: $Reason in file: $FilePath" "CRITICAL"
}

function Scan-FileContent {
    param([string]$FilePath)
    
    try {
        $content = Get-Content $FilePath -Raw -ErrorAction Stop
        
        foreach ($pattern in $SensitivePatterns) {
            if ($content -match $pattern) {
                Add-Alert -Type "SENSITIVE_CONTENT" -FilePath $FilePath -Content $content -Reason "Detected pattern: $pattern"
                return $true
            }
        }
        
        # Check for unusual file sizes (potential data dump)
        $fileInfo = Get-Item $FilePath
        if ($fileInfo.Length -gt 1MB) {
            Add-Alert -Type "LARGE_FILE" -FilePath $FilePath -Content "" -Reason "Unusually large file: $($fileInfo.Length) bytes"
            return $true
        }
        
        return $false
    }
    catch {
        Write-MonitorLog "Error scanning file $FilePath : $_" "WARNING"
        return $false
    }
}

function Check-UnexpectedFiles {
    param([string]$Path)
    
    # Whitelist of expected file patterns
    $expectedPatterns = @(
        '.*\.tsx$',
        '.*\.ts$',
        '.*\.json$',
        '.*\.md$',
        'page\.tsx$',
        'layout\.tsx$',
        'loading\.tsx$',
        'error\.tsx$'
    )
    
    Get-ChildItem -Path $Path -Recurse -File | ForEach-Object {
        $file = $_
        $isExpected = $false
        
        foreach ($pattern in $expectedPatterns) {
            if ($file.Name -match $pattern) {
                $isExpected = $true
                break
            }
        }
        
        if (-not $isExpected) {
            Add-Alert -Type "UNEXPECTED_FILE" -FilePath $file.FullName -Content "" -Reason "Unexpected file type in UAT folder"
        }
    }
}

function Check-UserSubmissions {
    # Check for user-uploaded content directories
    $uploadPaths = @(
        "$UATPath\uploads",
        "$UATPath\submissions",
        "$UATPath\user-data",
        "$BackendUATPath\uploads",
        "$BackendUATPath\data"
    )
    
    foreach ($path in $uploadPaths) {
        if (Test-Path $path) {
            $fileCount = (Get-ChildItem $path -Recurse -File).Count
            if ($fileCount -gt 0) {
                Write-MonitorLog "⚠️  Found $fileCount files in submission directory: $path" "WARNING"
                
                # Scan each file
                Get-ChildItem $path -Recurse -File | ForEach-Object {
                    Scan-FileContent -FilePath $_.FullName
                }
            }
        }
    }
}

function Monitor-RecentChanges {
    $since = (Get-Date).AddMinutes(-5)
    
    $recentChanges = Get-ChildItem -Path $UATPath -Recurse -File | 
        Where-Object { $_.LastWriteTime -gt $since } |
        Select-Object FullName, LastWriteTime, Length
    
    if ($recentChanges) {
        Write-MonitorLog "Recent file modifications detected:" "INFO"
        foreach ($change in $recentChanges) {
            Write-MonitorLog "  - $($change.FullName) (Modified: $($change.LastWriteTime), Size: $($change.Length) bytes)" "INFO"
            Scan-FileContent -FilePath $change.FullName
        }
    }
}

# Main monitoring loop
Write-MonitorLog "=== UAT Content Monitor Started ===" "INFO"
Write-MonitorLog "Monitoring paths:" "INFO"
Write-MonitorLog "  - Frontend: $UATPath" "INFO"
Write-MonitorLog "  - Backend: $BackendUATPath" "INFO"
Write-MonitorLog "Alert threshold: Any unexpected content" "INFO"
Write-MonitorLog "Check interval: $IntervalSeconds seconds" "INFO"

$iteration = 0
while ($true) {
    $iteration++
    Write-MonitorLog "--- Scan #$iteration ---" "INFO"
    
    try {
        # Check for unexpected files
        if (Test-Path $UATPath) {
            Check-UnexpectedFiles -Path $UATPath
        }
        
        if (Test-Path $BackendUATPath) {
            Check-UnexpectedFiles -Path $BackendUATPath
        }
        
        # Check for user submissions
        Check-UserSubmissions
        
        # Monitor recent changes
        Monitor-RecentChanges
        
        # Count total alerts
        $alerts = Get-Content $AlertsPath -Raw | ConvertFrom-Json
        $criticalCount = ($alerts | Where-Object { $_.severity -eq "CRITICAL" }).Count
        
        if ($criticalCount -gt 0) {
            Write-MonitorLog "🔴 ACTIVE ALERTS: $criticalCount critical events detected!" "CRITICAL"
        } else {
            Write-MonitorLog "✅ No critical events detected" "INFO"
        }
        
    }
    catch {
        Write-MonitorLog "Error during monitoring cycle: $_" "WARNING"
    }
    
    Start-Sleep -Seconds $IntervalSeconds
}
